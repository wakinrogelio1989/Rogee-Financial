import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import os
import json
import requests

# Set Streamlit page config
st.set_page_config(
    page_title="Rogee Financial Command Center",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #4B5563;
        margin-bottom: 1.2rem;
    }
    .card-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .notice-banner-green {
        background-color: #D1FAE5;
        border-left: 6px solid #059669;
        color: #065F46;
        padding: 1rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    .notice-banner-red {
        background-color: #FEE2E2;
        border-left: 6px solid #DC2626;
        color: #991B1B;
        padding: 1rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    .summary-card-bhd {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 8px;
        padding: 1rem;
    }
    .summary-card-php {
        background-color: #FEF3C7;
        border: 1px solid #FDE68A;
        border-radius: 8px;
        padding: 1rem;
    }
    .summary-card-usd {
        background-color: #F3E8FF;
        border: 1px solid #DDD6FE;
        border-radius: 8px;
        padding: 1rem;
    }
    .summary-card-total {
        background-color: #ECFDF5;
        border: 2px solid #10B981;
        border-radius: 8px;
        padding: 1rem;
    }
    .text-blue { color: #1E40AF; font-weight: 700; }
    .text-green { color: #166534; font-weight: 700; }
    .text-red { color: #991B1B; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

DATA_FILE_DEFAULT = "expenses.csv"
STOCKS_FILE_DEFAULT = "stocks_rogee.csv"

# MASTER COLUMN ORDER FOR TRANSACTION LEDGER
MASTER_COLS = [
    "Item #",
    "Date",
    "Main Category",
    "Sub Category",
    "Merchant/Description",
    "Billed Amount",
    "Actual Paid",
    "Currency",
    "Pending Due",
    "% Paid",
    "% Remaining",
    "Equivalent",
    "Status",
    "Payment Method"
]

def get_user_file_paths(username):
    clean_user = username.lower().replace(" ", "_")
    data_file = f"expenses_{clean_user}.csv"
    stocks_file = f"stocks_{clean_user}.csv"
    proj_file = f"projections_{clean_user}.csv"
    settings_file = f"settings_{clean_user}.json"
    
    if not os.path.exists(data_file) and os.path.exists(DATA_FILE_DEFAULT):
        try:
            df = pd.read_csv(DATA_FILE_DEFAULT)
            df.to_csv(data_file, index=False)
        except Exception:
            pass
            
    return data_file, stocks_file, proj_file, settings_file

def load_user_settings(settings_file):
    defaults = {"salary_bhd": 500.0, "sideline_bhd": 0.0, "business_bhd": 0.0, "other_bhd": 0.0, "needs_pct": 50, "wants_pct": 30, "savings_pct": 20}
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r") as f:
                saved = json.load(f)
                defaults.update(saved)
        except Exception:
            pass
    return defaults

def save_user_settings(settings_dict, settings_file):
    try:
        with open(settings_file, "w") as f:
            json.dump(settings_dict, f, indent=4)
    except Exception:
        pass

def load_data(data_file):
    if os.path.exists(data_file):
        try:
            df = pd.read_csv(data_file)
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date']).dt.date
            df = df.reindex(columns=MASTER_COLS)
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=MASTER_COLS)

def save_data(df, data_file):
    df = df.reindex(columns=MASTER_COLS)
    df.to_csv(data_file, index=False)

def load_stocks(stocks_file):
    if os.path.exists(stocks_file):
        try:
            df = pd.read_csv(stocks_file)
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=["Ticker", "Name", "Shares", "Avg Price", "Currency", "Market Price"])

def save_stocks(df, stocks_file):
    df.to_csv(stocks_file, index=False)

def load_projections(proj_file, default_income, default_needs, default_wants, default_savings):
    cols = ["Month", "Projected Income (BHD)", "Needs & Debts (BHD)", "Wants (BHD)", "Savings (BHD)", "Total Expenses (BHD)", "Net Surplus (BHD)", "Cumulative Savings (BHD)"]
    if os.path.exists(proj_file):
        try:
            df = pd.read_csv(proj_file)
            rename_map = {
                "Income (BHD)": "Projected Income (BHD)",
                "Projected Income": "Projected Income (BHD)",
                "Expenses (BHD)": "Total Expenses (BHD)"
            }
            df = df.rename(columns=rename_map)
            for c in cols:
                if c not in df.columns:
                    df[c] = 0.0
            return df[cols]
        except Exception:
            pass
            
    months = [f"Month {i}" for i in range(1, 13)]
    data = []
    cum = 0.0
    for m in months:
        tot_exp = default_needs + default_wants + default_savings
        surplus = default_income - tot_exp
        cum += default_savings + max(0.0, surplus)
        data.append({
            "Month": m,
            "Projected Income (BHD)": round(default_income, 2),
            "Needs & Debts (BHD)": round(default_needs, 2),
            "Wants (BHD)": round(default_wants, 2),
            "Savings (BHD)": round(default_savings, 2),
            "Total Expenses (BHD)": round(tot_exp, 2),
            "Net Surplus (BHD)": round(surplus, 2),
            "Cumulative Savings (BHD)": round(cum, 2)
        })
    return pd.DataFrame(data)

def save_projections(df, proj_file):
    df.to_csv(proj_file, index=False)

# Live Exchange Rate Fetcher
@st.cache_data(ttl=3600)
def get_live_exchange_rates():
    try:
        res = requests.get("https://open.er-api.com/v6/latest/BHD", timeout=5)
        if res.status_code == 200:
            rates = res.json().get("rates", {})
            bhd_to_php = rates.get("PHP", 155.0)
            bhd_to_usd = rates.get("USD", 2.6596)
            return bhd_to_php, bhd_to_usd, True
    except Exception:
        pass
    return 155.0, 2.6596, False

bhd_to_php_rate, bhd_to_usd_rate, is_live_rate = get_live_exchange_rates()

# USER PASSCODES FOR LOGIN
USER_PASSCODES = {
    "Rogee": os.environ.get("ROGEE_KEY", "rogee2026"),
    "User 2": os.environ.get("USER2_KEY", "user2026"),
    "User 3": os.environ.get("USER3_KEY", "user2026"),
    "User 4": os.environ.get("USER4_KEY", "user2026")
}

# LOGIN PORTAL
if "authenticated_user" not in st.session_state:
    st.session_state["authenticated_user"] = None

if st.session_state["authenticated_user"] is None:
    st.markdown('<div style="text-align:center; padding-top:2rem;"><h1 style="color:#1E3A8A;">🔒 Rogee Financial Command Center</h1><p style="color:#4B5563;">Select profile and enter passcode to unlock your portal.</p></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        with st.form("login_form"):
            selected_user = st.selectbox("Select User Profile", list(USER_PASSCODES.keys()))
            entered_passcode = st.text_input("Enter Passkey", type="password")
            login_btn = st.form_submit_button("🔓 Unlock Portal", use_container_width=True)
            if login_btn:
                if entered_passcode == USER_PASSCODES.get(selected_user):
                    st.session_state["authenticated_user"] = selected_user
                    st.success(f"Welcome, {selected_user}!")
                    st.rerun()
                else:
                    st.error("Invalid passkey. Please try again.")
        with st.expander("💡 Passkey Reference"):
            st.info("**Rogee**: `rogee2026` | **User 2/3/4**: `user2026`")
    st.stop()

active_user = st.session_state["authenticated_user"]
user_data_file, user_stocks_file, user_proj_file, user_settings_file = get_user_file_paths(active_user)
user_settings = load_user_settings(user_settings_file)

# SIDEBAR SETTINGS
st.sidebar.title(f"👤 {active_user}'s Portal")
if st.sidebar.button("🔒 Sign Out / Lock Portal"):
    st.session_state["authenticated_user"] = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("💵 Income Streams")
salary_bhd = st.sidebar.number_input("Primary Salary (BHD)", min_value=0.0, value=float(user_settings.get("salary_bhd", 500.0)), step=10.0)
sideline_bhd = st.sidebar.number_input("Sideline Income (BHD)", min_value=0.0, value=float(user_settings.get("sideline_bhd", 0.0)), step=10.0)
business_bhd = st.sidebar.number_input("Business Income (BHD)", min_value=0.0, value=float(user_settings.get("business_bhd", 0.0)), step=10.0)
other_bhd = st.sidebar.number_input("Other Income (BHD)", min_value=0.0, value=float(user_settings.get("other_bhd", 0.0)), step=10.0)

total_income_bhd = salary_bhd + sideline_bhd + business_bhd + other_bhd
total_income_php = total_income_bhd * bhd_to_php_rate
total_income_usd = total_income_bhd * bhd_to_usd_rate

st.sidebar.markdown(f"**Total Income:** BD {total_income_bhd:,.2f} | ₱ {total_income_php:,.2f} | $ {total_income_usd:,.2f}")

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Budget Targets (%)")
needs_pct = st.sidebar.slider("Needs & Debts Target %", 0, 100, int(user_settings.get("needs_pct", 50)))
wants_pct = st.sidebar.slider("Wants Target %", 0, 100, int(user_settings.get("wants_pct", 30)))
savings_pct = st.sidebar.slider("Savings Target %", 0, 100, int(user_settings.get("savings_pct", 20)))

tot_pct = needs_pct + wants_pct + savings_pct
if tot_pct != 100:
    st.sidebar.warning(f"Targets total {tot_pct}%. Adjust to equal 100%.")

# Save user settings
current_settings = {
    "salary_bhd": salary_bhd,
    "sideline_bhd": sideline_bhd,
    "business_bhd": business_bhd,
    "other_bhd": other_bhd,
    "needs_pct": needs_pct,
    "wants_pct": wants_pct,
    "savings_pct": savings_pct
}
if current_settings != user_settings:
    save_user_settings(current_settings, user_settings_file)

# Load user data
df_expenses = load_data(user_data_file)
df_stocks = load_stocks(user_stocks_file)

# Calculate targets
needs_target_bhd = total_income_bhd * (needs_pct / 100.0)
wants_target_bhd = total_income_bhd * (wants_pct / 100.0)
savings_target_bhd = total_income_bhd * (savings_pct / 100.0)

framework_title = f"{needs_pct}/{wants_pct}/{savings_pct} Budgeting Framework"

# Main App Header
st.markdown(f'<div class="main-header">Rogee Financial Command Center</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Personalized Multi-Currency Tracker & Analytics based on the {framework_title}</div>', unsafe_allow_html=True)

# Tabs
tab_dash, tab_add, tab_history, tab_proj, tab_stocks, tab_calc, tab_rates = st.tabs([
    "📊 Dashboard & Analytics",
    "➕ Record Expense",
    "📋 Transaction History",
    "🔮 12-Month Projections",
    "📈 MT5 & COL Investments",
    "📐 MT5 Pip Calculator",
    "💱 Live Currency Converter"
])

# Process Actuals from df_expenses
actual_needs_bhd = 0.0
actual_wants_bhd = 0.0
actual_savings_bhd = 0.0

if not df_expenses.empty:
    for idx, row in df_expenses.iterrows():
        cat = str(row.get("Main Category", ""))
        paid = float(row.get("Actual Paid", 0.0) if pd.notnull(row.get("Actual Paid")) else 0.0)
        curr = str(row.get("Currency", "BHD"))
        
        # Convert to BHD
        if curr == "PHP":
            amt_bhd = paid / bhd_to_php_rate
        elif curr == "USD":
            amt_bhd = paid / bhd_to_usd_rate
        else:
            amt_bhd = paid
            
        if "Needs" in cat or "Debt" in cat:
            actual_needs_bhd += amt_bhd
        elif "Want" in cat:
            actual_wants_bhd += amt_bhd
        elif "Saving" in cat:
            actual_savings_bhd += amt_bhd

total_spent_bhd = actual_needs_bhd + actual_wants_bhd + actual_savings_bhd
remaining_cash_bhd = total_income_bhd - total_spent_bhd
savings_rate = (actual_savings_bhd / total_income_bhd * 100) if total_income_bhd > 0 else 0.0

# TAB 1: DASHBOARD
with tab_dash:
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Monthly Income", f"BD {total_income_bhd:,.2f}")
    m2.metric("Total Spent", f"BD {total_spent_bhd:,.2f}", delta=f"-BD {total_spent_bhd:,.2f}", delta_color="inverse")
    m3.metric("Remaining Balance", f"BD {remaining_cash_bhd:,.2f}", delta=f"BD {remaining_cash_bhd:,.2f}")
    m4.metric("Savings Rate", f"{savings_rate:.1f}%", delta=f"{savings_rate - savings_pct:.1f}% vs Target")
    
    # Total billed to be paid
    total_billed_bhd = 0.0
    if not df_expenses.empty:
        for idx, row in df_expenses.iterrows():
            billed = float(row.get("Billed Amount", 0.0) if pd.notnull(row.get("Billed Amount")) else 0.0)
            curr = str(row.get("Currency", "BHD"))
            if curr == "PHP":
                total_billed_bhd += billed / bhd_to_php_rate
            elif curr == "USD":
                total_billed_bhd += billed / bhd_to_usd_rate
            else:
                total_billed_bhd += billed
    m5.metric("Total Expenses Needed", f"BD {total_billed_bhd:,.2f}")

    st.markdown("---")
    st.subheader(f"🎯 {framework_title} Benchmark Allocation Breakdown")

    cat_summary_data = [
        {"Category": f"Needs & Debts ({needs_pct}%)", "Target Allocation": f"{needs_pct}%", "Target (BHD)": needs_target_bhd, "Actual Spent (BHD)": actual_needs_bhd, "Difference (BHD)": needs_target_bhd - actual_needs_bhd, "Status": "On Track" if actual_needs_bhd <= needs_target_bhd else "Over Target"},
        {"Category": f"Wants ({wants_pct}%)", "Target Allocation": f"{wants_pct}%", "Target (BHD)": wants_target_bhd, "Actual Spent (BHD)": actual_wants_bhd, "Difference (BHD)": wants_target_bhd - actual_wants_bhd, "Status": "On Track" if actual_wants_bhd <= wants_target_bhd else "Over Target"},
        {"Category": f"Savings ({savings_pct}%)", "Target Allocation": f"{savings_pct}%", "Target (BHD)": savings_target_bhd, "Actual Spent (BHD)": actual_savings_bhd, "Difference (BHD)": actual_savings_bhd - savings_target_bhd, "Status": "Target Met" if actual_savings_bhd >= savings_target_bhd else "Under Goal"}
    ]
    st.dataframe(pd.DataFrame(cat_summary_data).style.format({"Target (BHD)": "BD {:,.2f}", "Actual Spent (BHD)": "BD {:,.2f}", "Difference (BHD)": "BD {:,.2f}"}), use_container_width=True, hide_index=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Target vs. Actual Spending (BHD)")
        bar_df = pd.DataFrame({
            "Category": ["Needs & Debts", "Wants", "Savings"],
            "Target": [needs_target_bhd, wants_target_bhd, savings_target_bhd],
            "Actual": [actual_needs_bhd, actual_wants_bhd, actual_savings_bhd]
        })
        fig_bar = go.Figure(data=[
            go.Bar(name='Target', x=bar_df['Category'], y=bar_df['Target'], marker_color='#93C5FD'),
            go.Bar(name='Actual', x=bar_df['Category'], y=bar_df['Actual'], marker_color='#1D4ED8')
        ])
        fig_bar.update_layout(barmode='group', yaxis_title="Amount (BHD)", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("Actual Expense Share")
        if total_spent_bhd > 0:
            fig_pie = px.pie(values=[actual_needs_bhd, actual_wants_bhd, actual_savings_bhd], names=["Needs & Debts", "Wants", "Savings"], color_discrete_sequence=['#2563EB', '#F59E0B', '#10B981'], hole=0.45)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expense transactions recorded yet.")

# TAB 2: RECORD EXPENSE
with tab_add:
    st.subheader("➕ Record New Expense or Payment")
    with st.form("add_exp_form", clear_on_submit=True):
        col_1, col_2 = st.columns(2)
        with col_1:
            exp_date = st.date_input("Date", value=datetime.today())
            main_cat = st.selectbox("Category", [f"Needs & Debts ({needs_pct}%)", f"Wants ({wants_pct}%)", f"Savings ({savings_pct}%)"])
            if "Needs" in main_cat or "Debt" in main_cat:
                sub_cats = ["Housing / Rent / Mortgage", "Utilities & Bills", "Groceries", "Transportation / Fuel", "Healthcare / Insurance", "Personal Loan / Debts"]
            elif "Want" in main_cat:
                sub_cats = ["Dining Out & Coffee", "Entertainment & Streaming", "Shopping & Apparel", "Subscriptions", "Miscellaneous"]
            else:
                sub_cats = ["Emergency Fund", "Stock Investments", "Retirement", "Major Goal Savings"]
            sub_cat = st.selectbox("Sub-Category", sub_cats)
            merchant = st.text_input("Merchant / Description", placeholder="e.g., EWA, Flat Rent, Supermarket")

        with col_2:
            currency_entry = st.selectbox("Currency", ["BHD", "PHP", "USD"])
            billed_amt = st.number_input(f"Billed / Planned Amount ({currency_entry})", min_value=0.0, step=5.0)
            paid_amt = st.number_input(f"Actual Paid Amount ({currency_entry})", min_value=0.0, step=5.0)
            payment_method = st.selectbox("Payment Method", ["Bank Transfer", "Credit Card", "Debit Card", "Cash"])

        submit_exp = st.form_submit_button("💾 Record Expense", use_container_width=True)
        if submit_exp:
            pending_due = max(0.0, billed_amt - paid_amt)
            pct_paid = (paid_amt / billed_amt * 100) if billed_amt > 0 else (100.0 if paid_amt > 0 else 0.0)
            pct_rem = max(0.0, 100.0 - pct_paid)
            status = "Paid" if pct_paid >= 100 else ("Partially Paid" if pct_paid > 0 else "Not Paid")
            
            # Equivalent string
            if currency_entry == "BHD":
                equiv_str = f"₱ {billed_amt * bhd_to_php_rate:,.2f} | $ {billed_amt * bhd_to_usd_rate:,.2f}"
            elif currency_entry == "PHP":
                equiv_str = f"BD {billed_amt / bhd_to_php_rate:,.2f} | $ {(billed_amt / bhd_to_php_rate) * bhd_to_usd_rate:,.2f}"
            else:
                equiv_str = f"BD {billed_amt / bhd_to_usd_rate:,.2f} | ₱ {(billed_amt / bhd_to_usd_rate) * bhd_to_php_rate:,.2f}"

            next_item = len(df_expenses) + 1
            new_row = pd.DataFrame([{
                "Item #": next_item,
                "Date": exp_date,
                "Main Category": main_cat,
                "Sub Category": sub_cat,
                "Merchant/Description": merchant if merchant else sub_cat,
                "Billed Amount": billed_amt,
                "Actual Paid": paid_amt,
                "Currency": currency_entry,
                "Pending Due": pending_due,
                "% Paid": round(pct_paid, 1),
                "% Remaining": round(pct_rem, 1),
                "Equivalent": equiv_str,
                "Status": status,
                "Payment Method": payment_method
            }])
            df_expenses = pd.concat([df_expenses, new_row], ignore_index=True)
            save_data(df_expenses, user_data_file)
            st.success(f"Recorded transaction '{merchant if merchant else sub_cat}' successfully!")
            st.rerun()

# TAB 3: TRANSACTION HISTORY
with tab_history:
    st.subheader("📋 Transaction History & Ledger")
    
    # BUDGET NOTICE BANNER
    if total_spent_bhd <= total_income_bhd:
        rem_php = remaining_cash_bhd * bhd_to_php_rate
        rem_usd = remaining_cash_bhd * bhd_to_usd_rate
        st.markdown(f'<div class="notice-banner-green">🟢 <b>WITHIN BUDGET NOTICE:</b> Remaining Net Available Cash Balance = <b>BD {remaining_cash_bhd:,.2f}</b> | <b>₱ {rem_php:,.2f} PHP</b> | <b>$ {rem_usd:,.2f} USD</b></div>', unsafe_allow_html=True)
    else:
        over_bhd = total_spent_bhd - total_income_bhd
        over_php = over_bhd * bhd_to_php_rate
        over_usd = over_bhd * bhd_to_usd_rate
        st.markdown(f'<div class="notice-banner-red">🚨 <b>OVER BUDGET NOTICE:</b> Exceeded Spending Limit Deficit = <b>-BD {over_bhd:,.2f}</b> | <b>-₱ {over_php:,.2f} PHP</b> | <b>-$ {over_usd:,.2f} USD</b></div>', unsafe_allow_html=True)

    if not df_expenses.empty:
        df_expenses = df_expenses.reindex(columns=MASTER_COLS)
        st.markdown("#### ✏️ Interactive Editable Ledger Grid")
        edited_df = st.data_editor(df_expenses, use_container_width=True, hide_index=True, key="ledger_editor")
        if st.button("💾 Save Ledger Changes", type="primary"):
            save_data(edited_df, user_data_file)
            st.success("Ledger saved successfully!")
            st.rerun()

        st.markdown("---")
        st.markdown("#### 🎨 Color-Coded Status Ledger View")
        def style_status(val):
            if val == "Paid": return "background-color: #D1FAE5; color: #065F46; font-weight: bold;"
            elif val == "Partially Paid": return "background-color: #FEF3C7; color: #92400E; font-weight: bold;"
            else: return "background-color: #FEE2E2; color: #991B1B; font-weight: bold;"
            
        st.dataframe(df_expenses.style.map(style_status, subset=["Status"]), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("💰 Total Outstanding & Payment Ledger Summary")

        # ABSOLUTELY INITIALIZE ALL SUMMARY VARIABLES TO PREVENT ANY NameError!
        bhd_billed = 0.0
        bhd_paid = 0.0
        bhd_pending = 0.0

        php_billed = 0.0
        php_paid = 0.0
        php_pending = 0.0

        usd_billed = 0.0
        usd_paid = 0.0
        usd_pending = 0.0

        for idx, row in df_expenses.iterrows():
            c_curr = str(row.get("Currency", "BHD"))
            c_billed = float(row.get("Billed Amount", 0.0) if pd.notnull(row.get("Billed Amount")) else 0.0)
            c_paid = float(row.get("Actual Paid", 0.0) if pd.notnull(row.get("Actual Paid")) else 0.0)
            c_pending = float(row.get("Pending Due", 0.0) if pd.notnull(row.get("Pending Due")) else 0.0)

            if c_curr == "BHD":
                bhd_billed += c_billed
                bhd_paid += c_paid
                bhd_pending += c_pending
            elif c_curr == "PHP":
                php_billed += c_billed
                php_paid += c_paid
                php_pending += c_pending
            elif c_curr == "USD":
                usd_billed += c_billed
                usd_paid += c_paid
                usd_pending += c_pending

        # Calculate BHD equivalents
        php_billed_bhd = php_billed / bhd_to_php_rate
        php_paid_bhd = php_paid / bhd_to_php_rate
        php_pending_bhd = php_pending / bhd_to_php_rate

        usd_billed_bhd = usd_billed / bhd_to_usd_rate
        usd_paid_bhd = usd_paid / bhd_to_usd_rate
        usd_pending_bhd = usd_pending / bhd_to_usd_rate

        grand_billed_bhd = bhd_billed + php_billed_bhd + usd_billed_bhd
        grand_paid_bhd = bhd_paid + php_paid_bhd + usd_paid_bhd
        grand_pending_bhd = bhd_pending + php_pending_bhd + usd_pending_bhd

        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.markdown(f'<div class="summary-card-bhd"><h4>🇧🇭 BHD Bills</h4><p class="text-blue">Billed: BD {bhd_billed:,.2f}</p><p class="text-green">Paid: BD {bhd_paid:,.2f}</p><p class="text-red">Pending: BD {bhd_pending:,.2f}</p></div>', unsafe_allow_html=True)
        with s2:
            st.markdown(f'<div class="summary-card-php"><h4>🇵🇭 PHP Bills</h4><p class="text-blue">Billed: ₱ {php_billed:,.2f}<br><small>(BD {php_billed_bhd:,.2f})</small></p><p class="text-green">Paid: ₱ {php_paid:,.2f}<br><small>(BD {php_paid_bhd:,.2f})</small></p><p class="text-red">Pending: ₱ {php_pending:,.2f}<br><small>(BD {php_pending_bhd:,.2f})</small></p></div>', unsafe_allow_html=True)
        with s3:
            st.markdown(f'<div class="summary-card-usd"><h4>💵 USD Bills</h4><p class="text-blue">Billed: $ {usd_billed:,.2f}<br><small>(BD {usd_billed_bhd:,.2f})</small></p><p class="text-green">Paid: $ {usd_paid:,.2f}<br><small>(BD {usd_paid_bhd:,.2f})</small></p><p class="text-red">Pending: $ {usd_pending:,.2f}<br><small>(BD {usd_pending_bhd:,.2f})</small></p></div>', unsafe_allow_html=True)
        with s4:
            st.markdown(f'<div class="summary-card-total"><h4>🌍 Combined Grand Total (In BD)</h4><p class="text-blue">Total Billed: BD {grand_billed_bhd:,.2f}</p><p class="text-green">Total Paid: BD {grand_paid_bhd:,.2f}</p><p class="text-red">Total Pending: BD {grand_pending_bhd:,.2f}</p></div>', unsafe_allow_html=True)

        st.markdown("---")
        csv_download = df_expenses.reindex(columns=MASTER_COLS).to_csv(index=False)
        st.download_button("📥 Download Transaction Ledger (CSV)", data=csv_download, file_name=f"ledger_{active_user.lower()}.csv", mime="text/csv")
    else:
        st.info("No expense transactions recorded yet.")

# TAB 4: 12-MONTH PROJECTIONS
with tab_proj:
    st.subheader("🔮 12-Month & Yearly Projected Budgeting Engine")
    df_projections = load_projections(user_proj_file, total_income_bhd, needs_target_bhd, wants_target_bhd, savings_target_bhd)
    
    st.markdown("#### ✏️ Interactive 12-Month Projection Forecast Matrix")
    edited_proj = st.data_editor(df_projections, use_container_width=True, hide_index=True, key="proj_editor")
    
    pcol1, pcol2 = st.columns(2)
    with pcol1:
        if st.button("💾 Save 12-Month Projections", type="primary"):
            save_projections(edited_proj, user_proj_file)
            st.success("Projections saved successfully!")
            st.rerun()
    with pcol2:
        proj_csv = edited_proj.to_csv(index=False)
        st.download_button("📥 Download 12-Month Forecast (CSV)", data=proj_csv, file_name=f"projections_{active_user.lower()}.csv", mime="text/csv")

    st.markdown("---")
    
    # Safe dynamic column retrieval
    inc_col = "Projected Income (BHD)" if "Projected Income (BHD)" in edited_proj.columns else edited_proj.columns[1]
    exp_col = "Total Expenses (BHD)" if "Total Expenses (BHD)" in edited_proj.columns else edited_proj.columns[5]
    cum_col = "Cumulative Savings (BHD)" if "Cumulative Savings (BHD)" in edited_proj.columns else edited_proj.columns[-1]

    fig_proj = go.Figure()
    fig_proj.add_trace(go.Bar(x=edited_proj["Month"], y=edited_proj[inc_col], name="Projected Income", marker_color="#3B82F6"))
    fig_proj.add_trace(go.Bar(x=edited_proj["Month"], y=edited_proj[exp_col], name="Total Expenses", marker_color="#EF4444"))
    fig_proj.update_layout(barmode="group", title="12-Month Income vs. Expense Forecast (BHD)", yaxis_title="BHD")
    st.plotly_chart(fig_proj, use_container_width=True)

    fig_cum = px.line(edited_proj, x="Month", y=cum_col, title="1-Year Cumulative Wealth & Savings Accumulation (BHD)", markers=True)
    st.plotly_chart(fig_cum, use_container_width=True)

# TAB 5: INVESTMENTS
with tab_stocks:
    st.subheader("📈 MT5 & COL Financial Investment Portfolio")
    edited_stocks = st.data_editor(df_stocks, use_container_width=True, hide_index=True, num_rows="dynamic", key="stocks_editor")
    if st.button("💾 Save Portfolio Changes", type="primary"):
        save_stocks(edited_stocks, user_stocks_file)
        st.success("Portfolio updated successfully!")
        st.rerun()

# TAB 6: MT5 PIP CALCULATOR
with tab_calc:
    st.subheader("📐 MT5 Pip Value & Margin Calculator")
    c1, c2 = st.columns(2)
    with c1:
        pair = st.selectbox("Currency Pair", ["USDPHP", "BHDPHP", "EURUSD", "GBPUSD", "USDJPY", "XAUUSD (Gold)"])
        lot_size = st.number_input("Lot Size", min_value=0.01, value=1.0, step=0.01)
        entry_price = st.number_input("Entry Price", min_value=0.0001, value=1.0, format="%.4f")
    with c2:
        exit_price = st.number_input("Exit Price", min_value=0.0001, value=1.05, format="%.4f")
        leverage = st.selectbox("Leverage", [100, 200, 400, 500], index=1)
        
    pips = abs(exit_price - entry_price) * (100 if "JPY" in pair else 10000)
    st.metric("Total Pips", f"{pips:,.1f} Pips")

# TAB 7: CURRENCY CONVERTER
with tab_rates:
    st.subheader("𒒱 Live Currency Converter")
    st.info(f"Live Exchange Rate Status: {'🟢 Active' if is_live_rate else '⚠️ Fallback Offline'} | 1 BD = ₱ {bhd_to_php_rate:.2f} PHP = $ {bhd_to_usd_rate:.2f} USD")
    amt_conv = st.number_input("Amount in BHD to Convert", min_value=0.0, value=100.0)
    st.write(f"**{amt_conv:,.2f} BHD** = **₱ {amt_conv * bhd_to_php_rate:,.2f} PHP** = **$ {amt_conv * bhd_to_usd_rate:,.2f} USD**")
