import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import requests

# ---------------------------------------------------------
# Streamlit Page Config
# ---------------------------------------------------------
st.set_page_config(
    page_title="Rogee Financial Command Center",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for high-contrast, clean UI & polished cards
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.1rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #4B5563;
        margin-bottom: 1.2rem;
    }
    .login-box {
        max-width: 450px;
        margin: 40px auto;
        padding: 30px;
        background-color: #FFFFFF;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        border: 1px solid #E5E7EB;
        text-align: center;
    }
    .notice-banner-green {
        background-color: #ECFDF5;
        border-left: 5px solid #10B981;
        padding: 12px 18px;
        border-radius: 8px;
        margin-bottom: 15px;
        color: #065F46;
        font-weight: 600;
    }
    .notice-banner-red {
        background-color: #FEF2F2;
        border-left: 5px solid #EF4444;
        padding: 12px 18px;
        border-radius: 8px;
        margin-bottom: 15px;
        color: #991B1B;
        font-weight: 600;
    }
    .summary-card {
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 12px;
        border: 1px solid #CBD5E1;
    }
    .card-blue { background-color: #EFF6FF; border-color: #BFDBFE; color: #1E40AF; }
    .card-green { background-color: #F0FDF4; border-color: #BBF7D0; color: #166534; }
    .card-red { background-color: #FEF2F2; border-color: #FECACA; color: #991B1B; }
    .card-amber { background-color: #FFFBEB; border-color: #FDE68A; color: #92400E; }
    
    .card-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 6px; }
    .card-value { font-size: 1.4rem; font-weight: 800; }
    .card-sub { font-size: 0.9rem; font-weight: 600; opacity: 0.9; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# Live Exchange Rates Fetcher
@st.cache_data(ttl=3600)
def get_live_exchange_rates():
    try:
        res = requests.get("https://open.er-api.com/v6/latest/BHD", timeout=5)
        if res.status_code == 200:
            data = res.json()
            rates = data.get("rates", {})
            php_rate = rates.get("PHP", 155.0)
            usd_rate = rates.get("USD", 2.65)
            eur_rate = rates.get("EUR", 2.45)
            gbp_rate = rates.get("GBP", 2.10)
            cad_rate = rates.get("CAD", 3.60)
            aed_rate = rates.get("AED", 9.73)
            sar_rate = rates.get("SAR", 9.94)
            return {
                "PHP": php_rate, "USD": usd_rate, "EUR": eur_rate,
                "GBP": gbp_rate, "CAD": cad_rate, "AED": aed_rate,
                "SAR": sar_rate, "BHD": 1.0
            }, "Live Market Rates"
    except Exception:
        pass
    # Fallback default static rates
    return {
        "PHP": 155.0, "USD": 2.65, "EUR": 2.45,
        "GBP": 2.10, "CAD": 3.60, "AED": 9.73,
        "SAR": 9.94, "BHD": 1.0
    }, "Standard Default Rates"

rates_dict, rate_status = get_live_exchange_rates()
bhd_to_php = rates_dict["PHP"]
bhd_to_usd = rates_dict["USD"]

# ---------------------------------------------------------
# Security & Authentication (Clean & Simple Login)
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = "Rogee"

USER_PASSKEYS = {
    "Rogee": os.getenv("ROGEE_KEY", "1989"),
    "Ferdie": os.getenv("USER2_KEY", "Ce_021119"),
    "User 3": os.getenv("USER3_KEY", "user32026"),
    "User 4": os.getenv("USER4_KEY", "user42026"),
}

if not st.session_state["authenticated"]:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("## 🔐 Rogee Financial Portal")
    st.markdown("Please select your profile and enter passcode to unlock.")
    
    selected_user = st.selectbox("👤 Select Profile", list(USER_PASSKEYS.keys()))
    entered_key = st.text_input("🔑 Passcode", type="password", placeholder="Enter passcode...")
    
    if st.button("Unlock Command Center", type="primary", use_container_width=True):
        if entered_key == USER_PASSKEYS[selected_user]:
            st.session_state["authenticated"] = True
            st.session_state["current_user"] = selected_user
            st.success(f"Welcome back, {selected_user}!")
            st.rerun()
        else:
            st.error("Incorrect passcode. Please try again.")
            
    with st.expander("ℹ️ Default Access Passkeys"):
        st.write("**Rogee:** `rogee2026` | **User 2:** `user2026` | **User 3:** `user32026` | **User 4:** `user42026`")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# User Data File Path
current_user = st.session_state["current_user"]
user_slug = current_user.lower().replace(" ", "_")
DATA_FILE = f"expenses_{user_slug}.csv"
STOCKS_FILE = f"stocks_{user_slug}.csv"

# Migrate old expenses.csv if user file doesn't exist yet
if not os.path.exists(DATA_FILE) and os.path.exists("expenses.csv"):
    try:
        import shutil
        shutil.copy("expenses.csv", DATA_FILE)
    except Exception:
        pass

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date']).dt.date
            # Ensure required schema columns exist
            for col in ["Item #", "Billed Amount", "Actual Paid", "Currency", "Status", "Payment Method"]:
                if col not in df.columns:
                    if col == "Item #": df[col] = range(1, len(df) + 1)
                    elif col == "Billed Amount": df[col] = df.get("Amount", 0.0)
                    elif col == "Actual Paid": df[col] = df.get("Amount", 0.0)
                    elif col == "Currency": df[col] = "BHD"
                    elif col == "Status": df[col] = "Paid"
                    elif col == "Payment Method": df[col] = "Bank Transfer"
            return df
        except Exception:
            pass
    Define your master column sequence MASTER\_COLS = [ "Item #", "Date", "Main Category", "Sub Category", "Merchant/Description", "Billed Amount", "Actual Paid", "Currency", "Pending Due", "% Paid", "% Remaining", "Equivalent", "Status", "Payment Method" ] # Initialize or load expenses dataframe with locked column order def load\_data(): if os.path.exists(DATA\_FILE): try: df = pd.read\_csv(DATA\_FILE) if 'Date' in df.columns: df['Date'] = pd.to\_datetime(df['Date']).dt.date # 🔒 Lock column order for existing loaded CSV data df = df.reindex(columns=MASTER\_COLS) return df except Exception: pass return pd.DataFrame(columns=MASTER\_COLS) def save\_data(df): # 🔒 Ensure saved CSV on disk strictly follows MASTER\_COLS df = df.reindex(columns=MASTER\_COLS) df.to\_csv(DATA\_FILE, index=False)

df_expenses = load_data()
df_stocks = load_stocks()
# ---------------------------------------------------------
# Sidebar Settings
# ---------------------------------------------------------
st.sidebar.title(f"👤 {current_user}'s Settings")

if st.sidebar.button("🔒 Sign Out / Lock Portal", type="secondary"):
    st.session_state["authenticated"] = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("💰 Monthly Take-Home Income")

salary_bhd = st.sidebar.number_input("Primary Monthly Salary (BHD)", min_value=0.0, value=1200.0, step=50.0)
business_income = st.sidebar.number_input("Business / Side Business (BHD)", min_value=0.0, value=0.0, step=25.0)
sideline_income = st.sidebar.number_input("Sidelines / Investments (BHD)", min_value=0.0, value=0.0, step=25.0)
bonus_income = st.sidebar.number_input("Other Allowances / Bonuses (BHD)", min_value=0.0, value=0.0, step=25.0)

total_income_bhd = salary_bhd + business_income + sideline_income + bonus_income
total_income_php = total_income_bhd * bhd_to_php
total_income_usd = total_income_bhd * bhd_to_usd

st.sidebar.markdown(f"""
<div style="background-color:#ECFDF5; border:1px solid #10B981; padding:10px; border-radius:8px; margin:10px 0;">
    <div style="font-size:0.85rem; color:#065F46; font-weight:700;">TOTAL COMBINED INCOME</div>
    <div style="font-size:1.2rem; color:#047857; font-weight:800;">BD {total_income_bhd:,.2f}</div>
    <div style="font-size:0.8rem; color:#065F46;">₱ {total_income_php:,.2f} PHP | $ {total_income_usd:,.2f} USD</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Budget Target Allocations (%)")

needs_pct = st.sidebar.slider("Needs Target % (Essentials)", 0, 100, 50)
wants_pct = st.sidebar.slider("Wants Target % (Lifestyle)", 0, 100, 30)
savings_pct = st.sidebar.slider("Savings Target % (Goals/Debt)", 0, 100, 20)

total_pct = needs_pct + wants_pct + savings_pct
if total_pct != 100:
    st.sidebar.warning(f"Allocation total is {total_pct}%. Adjust to equal 100%.")

# Framework Ratio Title
framework_title = f"{needs_pct}/{wants_pct}/{savings_pct}"

# Target Amounts in BHD
needs_target = total_income_bhd * (needs_pct / 100.0)
wants_target = total_income_bhd * (wants_pct / 100.0)
savings_target = total_income_bhd * (savings_pct / 100.0)

# Main Title Header
st.markdown('<div class="main-header">Rogee Financial Command Center</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Personal Finance & Investment Tracker based on the <b>{framework_title} Framework</b></div>', unsafe_allow_html=True)

# Navigation Tabs
tab_dash, tab_add, tab_history, tab_invest, tab_proj, tab_calc, tab_converter = st.tabs([
    "📊 Dashboard & Analytics",
    "➕ Record Expense / Payment",
    "📋 Transaction History",
    "📈 MT5 & COL Investments",
    "🔮 12-Month Projections",
    "📐 MT5 Pip Calculator",
    "💱 Live Currency Converter"
])

# Helper function to convert transaction amount to BHD
def to_bhd(amt, curr):
    if curr == "PHP": return amt / bhd_to_php
    elif curr == "USD": return amt / bhd_to_usd
    return amt

# Compute actuals converted to BHD
actual_needs_bhd = 0.0
actual_wants_bhd = 0.0
actual_savings_bhd = 0.0
total_billed_bhd = 0.0
total_paid_bhd = 0.0
total_pending_bhd = 0.0

# Calculate detailed bills by currency
bhd_bills_billed = 0.0
bhd_bills_paid = 0.0
bhd_bills_pending = 0.0

php_bills_billed = 0.0
php_bills_paid = 0.0
php_bills_pending = 0.0

usd_bills_billed = 0.0
usd_bills_paid = 0.0
usd_bills_pending = 0.0

if not df_expenses.empty:
    for idx, row in df_expenses.iterrows():
        cat = str(row.get("Main Category", ""))
        billed = float(row.get("Billed Amount", 0.0))
        paid = float(row.get("Actual Paid", 0.0))
        curr = str(row.get("Currency", "BHD")).upper()
        
        pending = max(0.0, billed - paid)
        
        billed_in_bhd = to_bhd(billed, curr)
        paid_in_bhd = to_bhd(paid, curr)
        pending_in_bhd = to_bhd(pending, curr)
        
        total_billed_bhd += billed_in_bhd
        total_paid_bhd += paid_in_bhd
        total_pending_bhd += pending_in_bhd
        
        if "Needs" in cat: actual_needs_bhd += paid_in_bhd
        elif "Wants" in cat: actual_wants_bhd += paid_in_bhd
        else: actual_savings_bhd += paid_in_bhd
        
        if curr == "PHP":
            php_bills_billed += billed
            php_bills_paid += paid
            php_bills_pending += pending
        elif curr == "USD":
            usd_bills_billed += billed
            usd_bills_paid += paid
            usd_bills_pending += pending
        else:
            bhd_bills_billed += billed
            bhd_bills_paid += paid
            bhd_bills_pending += pending

total_spent_bhd = actual_needs_bhd + actual_wants_bhd + actual_savings_bhd
remaining_cash_bhd = total_income_bhd - total_paid_bhd
savings_rate = (actual_savings_bhd / total_income_bhd * 100.0) if total_income_bhd > 0 else 0.0

# ---------------------------------------------------------
# TAB 1: DASHBOARD & ANALYTICS
# ---------------------------------------------------------
with tab_dash:
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Monthly Net Income", f"BD {total_income_bhd:,.2f}")
    m2.metric("Total Actual Paid", f"BD {total_paid_bhd:,.2f}", delta=f"-BD {total_paid_bhd:,.2f}", delta_color="inverse")
    
    if remaining_cash_bhd >= 0:
        m3.metric("Remaining Net Cash", f"BD {remaining_cash_bhd:,.2f}", delta=f"BD {remaining_cash_bhd:,.2f}")
    else:
        m3.metric("Over Budget Balance", f"BD {remaining_cash_bhd:,.2f}", delta=f"BD {remaining_cash_bhd:,.2f}", delta_color="inverse")
        
    m4.metric(f"Savings Rate ({savings_pct}%)", f"{savings_rate:.1f}%", delta=f"{savings_rate - savings_pct:.1f}% vs Target")
    m5.metric("Total Expenses to be Paid", f"BD {total_billed_bhd:,.2f}", delta=f"Pending BD {total_pending_bhd:,.2f}", delta_color="off")

    st.markdown("---")
    st.subheader(f"🎯 {framework_title} Target Benchmark Allocation Breakdown")

    cat_data = [
        {"Category": f"Needs ({needs_pct}%)", "Target (%)": f"{needs_pct}%", "Target (BD)": needs_target, "Actual Paid (BD)": actual_needs_bhd, "Difference (BD)": needs_target - actual_needs_bhd, "Status": "On Track" if actual_needs_bhd <= needs_target else "Over Target"},
        {"Category": f"Wants ({wants_pct}%)", "Target (%)": f"{wants_pct}%", "Target (BD)": wants_target, "Actual Paid (BD)": actual_wants_bhd, "Difference (BD)": wants_target - actual_wants_bhd, "Status": "On Track" if actual_wants_bhd <= wants_target else "Over Target"},
        {"Category": f"Savings & Debt ({savings_pct}%)", "Target (%)": f"{savings_pct}%", "Target (BD)": savings_target, "Actual Paid (BD)": actual_savings_bhd, "Difference (BD)": actual_savings_bhd - savings_target, "Status": "Target Met" if actual_savings_bhd >= savings_target else "Under Goal"}
    ]
    df_cat_summary = pd.DataFrame(cat_data)
    
    st.dataframe(
        df_cat_summary.style.format({
            "Target (BD)": "BD {:,.2f}",
            "Actual Paid (BD)": "BD {:,.2f}",
            "Difference (BD)": "BD {:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Target vs. Actual Spending (BD)")
        chart_df = pd.DataFrame({
            "Category": [f"Needs ({needs_pct}%)", f"Wants ({wants_pct}%)", f"Savings ({savings_pct}%)"],
            "Target": [needs_target, wants_target, savings_target],
            "Actual": [actual_needs_bhd, actual_wants_bhd, actual_savings_bhd]
        })
        fig_bar = go.Figure(data=[
            go.Bar(name='Target', x=chart_df['Category'], y=chart_df['Target'], marker_color='#93C5FD'),
            go.Bar(name='Actual', x=chart_df['Category'], y=chart_df['Actual'], marker_color='#1D4ED8')
        ])
        fig_bar.update_layout(
            barmode='group',
            yaxis_title="Amount (BD)",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("Actual Spending Share")
        if total_spent_bhd > 0:
            fig_pie = px.pie(
                values=[actual_needs_bhd, actual_wants_bhd, actual_savings_bhd],
                names=[f"Needs ({needs_pct}%)", f"Wants ({wants_pct}%)", f"Savings ({savings_pct}%)"],
                color_discrete_sequence=['#2563EB', '#F59E0B', '#10B981'],
                hole=0.45
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expenses logged yet. Add your first expense in 'Add Expense / Payment'!")

# ---------------------------------------------------------
# TAB 2: RECORD EXPENSE / PAYMENT
# ---------------------------------------------------------
with tab_add:
    st.subheader("➕ Record a New Expense or Payment")

    col_a, col_b = st.columns(2)

    with col_a:
        exp_date = st.date_input("Date", value=datetime.today())
        main_cat = st.selectbox("Category Group", [
            f"Needs & Debts ({needs_pct}%)",
            f"Wants ({wants_pct}%)",
            f"Savings ({savings_pct}%)",
            "100% Priority / Essential Commitments",
            "Debts & Credits Payoff"
        ])
        
        if "Needs" in main_cat or "100%" in main_cat:
            sub_cats = ["Housing / Rent / Mortgage", "Utilities & Bills", "Groceries", "Transportation / Fuel", "Healthcare / Insurance", "Tuition & Family"]
        elif "Wants" in main_cat:
            sub_cats = ["Dining Out & Coffee", "Entertainment & Streaming", "Shopping & Apparel", "Hobbies & Travel", "Subscriptions", "Miscellaneous"]
        elif "Debts" in main_cat:
            sub_cats = ["Credit Card Payoff", "Personal Loan", "Auto Loan", "Settle Debt", "Family Support / Remittance"]
        else:
            sub_cats = ["Emergency Fund", "COL Financial / Philippine Stocks", "MT5 Forex / Trading Capital", "Retirement / Savings", "Major Goal"]

        sub_cat = st.selectbox("Sub-Category", sub_cats)

    with col_b:
        merchant = st.text_input("Merchant / Description", placeholder="e.g., Rent, Grocery Store, Utility")
        exp_curr = st.selectbox("Transaction Currency", ["BHD", "PHP", "USD"], index=0)
        billed_amt = st.number_input(f"Planned / Billed Amount ({exp_curr})", min_value=0.01, step=10.0, value=100.0)
        actual_paid_amt = st.number_input(f"Actual Amount Paid ({exp_curr})", min_value=0.0, step=10.0, value=billed_amt)
        payment_method = st.selectbox("Payment Method", ["Bank Transfer", "Credit Card", "Debit Card", "Cash", "COL Financial Transfer", "MT5 Transfer"])

    if st.button("Save Expense / Payment Record", type="primary", use_container_width=True):
        new_item_num = len(df_expenses) + 1
        pending_val = max(0.0, billed_amt - actual_paid_amt)
        pct_paid_val = (actual_paid_amt / billed_amt * 100.0) if billed_amt > 0 else 100.0
        pct_rem_val = max(0.0, 100.0 - pct_paid_val)
        
        if pct_paid_val >= 99.9: status_str = "Paid"
        elif pct_paid_val <= 0.1: status_str = "Not Paid"
        else: status_str = "Partially Paid"
        
        if exp_curr == "PHP":
            eq_str = f"BD {billed_amt / bhd_to_php:,.2f} | $ {billed_amt / bhd_to_php * bhd_to_usd:,.2f}"
        elif exp_curr == "USD":
            eq_str = f"BD {billed_amt / bhd_to_usd:,.2f} | ₱ {billed_amt / bhd_to_usd * bhd_to_php:,.2f}"
        else:
            eq_str = f"₱ {billed_amt * bhd_to_php:,.2f} | $ {billed_amt * bhd_to_usd:,.2f}"

        new_row = pd.DataFrame([{
            "Item #": new_item_num,
            "Date": exp_date,
            "Main Category": main_cat,
            "Sub Category": sub_cat,
            "Merchant/Description": merchant if merchant else sub_cat,
            "Billed Amount": billed_amt,
            "Actual Paid": actual_paid_amt,
            "Currency": exp_curr,
            "Pending Due": pending_val,
            "% Paid": round(pct_paid_val, 1),
            "% Remaining": round(pct_rem_val, 1),
            "Equivalent": eq_str,
            "Status": status_str,
            "Payment Method": payment_method
        }])
        
        df_expenses = pd.concat([df_expenses, new_row], ignore_index=True)
        save_data(df_expenses)
        st.success(f"Successfully recorded {exp_curr} {billed_amt:,.2f} for '{merchant if merchant else sub_cat}'!")
        st.rerun()

# ---------------------------------------------------------
# TAB 3: TRANSACTION HISTORY & LEDGER
# ---------------------------------------------------------
with tab_history:
    st.subheader("📋 Transaction History & Payment Ledger")

    # NOTICE BANNER ABOVE TRANSACTIONS
    if remaining_cash_bhd >= 0:
        st.markdown(f"""
        <div class="notice-banner-green">
            🟢 <b>WITHIN BUDGET STATUS:</b> You have available remaining income balance!<br>
            <b>Net Unspent Cash Balance:</b> BD {remaining_cash_bhd:,.2f} &nbsp;|&nbsp; ₱ {remaining_cash_bhd * bhd_to_php:,.2f} PHP &nbsp;|&nbsp; $ {remaining_cash_bhd * bhd_to_usd:,.2f} USD
        </div>
        """, unsafe_allow_html=True)
    else:
        overage_bhd = abs(remaining_cash_bhd)
        st.markdown(f"""
        <div class="notice-banner-red">
            🚨 <b>OVER BUDGET STATUS NOTICE:</b> Total payments exceed your monthly income limit!<br>
            <b>Current Limit Deficit:</b> -BD {overage_bhd:,.2f} &nbsp;|&nbsp; -₱ {overage_bhd * bhd_to_php:,.2f} PHP &nbsp;|&nbsp; -$ {overage_bhd * bhd_to_usd:,.2f} USD
        </div>
        """, unsafe_allow_html=True)

    if not df_expenses.empty:
        st.markdown("#### ✏️ Interactive Editable Ledger Grid")
        st.caption("Double-click any cell below to modify dates, amounts, currencies, or statuses directly, then click 'Save Ledger Changes'.")
        
        edited_df = st.data_editor(
            df_expenses,
            use_container_width=True,
            num_rows="dynamic",
            hide_index=True,
            column_config={
                "Currency": st.column_config.SelectboxColumn("Currency", options=["BHD", "PHP", "USD"], required=True),
                "Status": st.column_config.SelectboxColumn("Status", options=["Paid", "Partially Paid", "Not Paid"], required=True),
                "Billed Amount": st.column_config.NumberColumn("Billed Amount", format="%.2f"),
                "Actual Paid": st.column_config.NumberColumn("Actual Paid", format="%.2f")
            }
        )

        if st.button("💾 Save Ledger Changes", type="primary"):
            # Recalculate computed fields
            for idx in edited_df.index:
                billed = float(edited_df.at[idx, "Billed Amount"]) if pd.notnull(edited_df.at[idx, "Billed Amount"]) else 0.0
                paid = float(edited_df.at[idx, "Actual Paid"]) if pd.notnull(edited_df.at[idx, "Actual Paid"]) else 0.0
                curr = str(edited_df.at[idx, "Currency"]).upper()
                
                pending = max(0.0, billed - paid)
                pct_p = (paid / billed * 100.0) if billed > 0 else 100.0
                pct_r = max(0.0, 100.0 - pct_p)
                
                if pct_p >= 99.9: stat = "Paid"
                elif pct_p <= 0.1: stat = "Not Paid"
                else: stat = "Partially Paid"
                
                if curr == "PHP": eq = f"BD {billed / bhd_to_php:,.2f} | $ {billed / bhd_to_php * bhd_to_usd:,.2f}"
                elif curr == "USD": eq = f"BD {billed / bhd_to_usd:,.2f} | ₱ {billed / bhd_to_usd * bhd_to_php:,.2f}"
                else: eq = f"₱ {billed * bhd_to_php:,.2f} | $ {billed * bhd_to_usd:,.2f}"
                
                edited_df.at[idx, "Pending Due"] = round(pending, 2)
                edited_df.at[idx, "% Paid"] = round(pct_p, 1)
                edited_df.at[idx, "% Remaining"] = round(pct_r, 1)
                edited_df.at[idx, "Status"] = stat
                edited_df.at[idx, "Equivalent"] = eq
                edited_df.at[idx, "Item #"] = idx + 1
                
            save_data(edited_df)
            st.success("Ledger changes saved successfully!")
            st.rerun()

        st.markdown("---")
        st.markdown("#### 🎨 Color-Highlighted Payment Status Ledger")

        def highlight_status_row(row):
            stat = str(row.get("Status", ""))
            pct_p = float(row.get("% Paid", 100.0))
            if stat == "Paid" or pct_p >= 99.9:
                return ['background-color: #D1FAE5; color: #065F46; font-weight: 500;'] * len(row)
            elif stat == "Partially Paid" or (0.1 < pct_p < 99.9):
                return ['background-color: #FEF3C7; color: #92400E; font-weight: 500;'] * len(row)
            else:
                return ['background-color: #FEE2E2; color: #991B1B; font-weight: 500;'] * len(row)

        st.dataframe(
            df_expenses.style.apply(highlight_status_row, axis=1),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        st.subheader("💰 Total Outstanding & Payment Ledger Summary")

        # 4 SUMMARY CARDS: BHD BILLS, PHP BILLS, USD BILLS, COMBINED GRAND TOTAL IN BHD
        sc1, sc2, sc3, sc4 = st.columns(4)

        with sc1:
            st.markdown(f"""
            <div class="summary-card card-blue">
                <div class="card-title">🇧🇭 BHD Currency Bills</div>
                <div class="card-value">BD {bhd_bills_billed:,.2f}</div>
                <div class="card-sub">🟢 Paid: BD {bhd_bills_paid:,.2f}</div>
                <div class="card-sub">🔴 Pending: BD {bhd_bills_pending:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        with sc2:
            php_in_bhd_billed = php_bills_billed / bhd_to_php
            php_in_bhd_paid = php_bills_paid / bhd_to_php
            php_in_bhd_pending = php_bills_pending / bhd_to_php
            st.markdown(f"""
            <div class="summary-card card-amber">
                <div class="card-title">🇵🇭 PHP Currency Bills</div>
                <div class="card-value">₱ {php_bills_billed:,.2f} PHP</div>
                <div class="card-sub"><b>(BD {php_in_bhd_billed:,.2f} Equiv)</b></div>
                <div class="card-sub">🟢 Paid: ₱ {php_bills_paid:,.2f} (BD {php_in_bhd_paid:,.2f})</div>
                <div class="card-sub">🔴 Pending: ₱ {php_bills_pending:,.2f} (BD {php_in_bhd_pending:,.2f})</div>
            </div>
            """, unsafe_allow_html=True)

        with sc3:
            usd_in_bhd_billed = usd_bills_billed / bhd_to_usd
            usd_in_bhd_paid = usd_bills_paid / bhd_to_usd
            usd_in_bhd_pending = usd_bills_pending / bhd_to_usd
            st.markdown(f"""
            <div class="summary-card card-green">
                <div class="card-title">💵 USD Currency Bills</div>
                <div class="card-value">$ {usd_bills_billed:,.2f} USD</div>
                <div class="card-sub"><b>(BD {usd_in_bhd_billed:,.2f} Equiv)</b></div>
                <div class="card-sub">🟢 Paid: $ {usd_bills_paid:,.2f} (BD {usd_in_bhd_paid:,.2f})</div>
                <div class="card-sub">🔴 Pending: $ {usd_bills_pending:,.2f} (BD {usd_in_bhd_pending:,.2f})</div>
            </div>
            """, unsafe_allow_html=True)

        with sc4:
            st.markdown(f"""
            <div class="summary-card card-red">
                <div class="card-title">🌍 Combined Grand Total (In BD)</div>
                <div class="card-value">BD {total_billed_bhd:,.2f}</div>
                <div class="card-sub">🟢 Total Paid: BD {total_paid_bhd:,.2f}</div>
                <div class="card-sub">🔴 Total Pending: BD {total_pending_bhd:,.2f}</div>
                <div class="card-sub" style="font-size:0.75rem; margin-top:6px; color:#4B5563;">*Includes BHD + PHP + USD converted to BD vs. Salary</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            csv_data = df_expenses.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Export Full Ledger to CSV", data=csv_data, file_name=f"ledger_{user_slug}.csv", mime="text/csv", use_container_width=True)
        with col_ex2:
            if st.button("🗑️ Clear All Transaction Data", type="primary", use_container_width=True):
                if os.path.exists(DATA_FILE):
                    os.remove(DATA_FILE)
                st.success("All transaction logs cleared!")
                st.rerun()
    else:
        st.info("No transaction history recorded yet. Start adding expenses in 'Add Expense / Payment'!")

# ---------------------------------------------------------
# TAB 4: MT5 & COL FINANCIAL INVESTMENTS PORTFOLIO
# ---------------------------------------------------------
with tab_invest:
    st.subheader("📈 MT5 & COL Financial Investment Portfolio")
    st.markdown("Track and manage your stock holdings (COL Financial Philippines) and trading equity (MetaTrader 5).")

    i_col1, i_col2 = st.columns([1, 2])

    with i_col1:
        st.markdown("#### ➕ Add New Holding / Asset")
        inv_platform = st.selectbox("Investment Platform", ["COL Financial (PH Stocks)", "MT5 Forex / Trading", "Crypto / Digital Assets", "Real Estate / Other"])
        inv_ticker = st.text_input("Ticker Symbol / Asset Name", placeholder="e.g., SM, BDO, TEL, ALI, XAUUSD, BTC")
        inv_category = st.selectbox("Asset Category", ["Philippine Stocks (PSE)", "Forex & Commodities", "Crypto", "Mutual Funds / ETFs", "Bonds"])
        inv_shares = st.number_input("Shares / Quantity", min_value=0.0001, step=100.0, value=1000.0)
        inv_buy_price = st.number_input("Avg Purchase Price", min_value=0.0001, step=1.0, value=50.0)
        inv_curr_price = st.number_input("Current Market Price", min_value=0.0001, step=1.0, value=55.0)
        inv_curr = st.selectbox("Asset Currency", ["PHP", "USD", "BHD"], index=0 if "COL" in inv_platform else 1)

        if st.button("Add Holding to Portfolio", type="primary", use_container_width=True):
            new_inv = pd.DataFrame([{
                "Platform": inv_platform,
                "Ticker / Asset": inv_ticker if inv_ticker else "Stock Asset",
                "Category": inv_category,
                "Shares / Quantity": inv_shares,
                "Avg Buy Price": inv_buy_price,
                "Current Price": inv_curr_price,
                "Currency": inv_curr
            }])
            df_stocks = pd.concat([df_stocks, new_inv], ignore_index=True)
            save_stocks(df_stocks)
            st.success(f"Added {inv_ticker} to {inv_platform} portfolio!")
            st.rerun()

    with i_col2:
        st.markdown("#### 📊 Current Investment Portfolio Summary")
        if not df_stocks.empty:
            # Calculate values
            df_stocks["Cost Basis"] = df_stocks["Shares / Quantity"] * df_stocks["Avg Buy Price"]
            df_stocks["Market Value"] = df_stocks["Shares / Quantity"] * df_stocks["Current Price"]
            df_stocks["Unrealized P&L"] = df_stocks["Market Value"] - df_stocks["Cost Basis"]
            df_stocks["Return %"] = (df_stocks["Unrealized P&L"] / df_stocks["Cost Basis"] * 100.0)

            # Convert values to BHD for unified portfolio valuation
            df_stocks["Market Value (BD)"] = df_stocks.apply(lambda r: to_bhd(r["Market Value"], r["Currency"]), axis=1)

            total_portfolio_bhd = df_stocks["Market Value (BD)"].sum()
            total_portfolio_php = total_portfolio_bhd * bhd_to_php
            total_portfolio_usd = total_portfolio_bhd * bhd_to_usd

            p1, p2, p3 = st.columns(3)
            p1.metric("Total Portfolio (BD)", f"BD {total_portfolio_bhd:,.2f}")
            p2.metric("Total Portfolio (PHP)", f"₱ {total_portfolio_php:,.2f}")
            p3.metric("Total Portfolio (USD)", f"$ {total_portfolio_usd:,.2f}")

            st.markdown("---")
            edited_stocks = st.data_editor(
                df_stocks,
                use_container_width=True,
                num_rows="dynamic",
                hide_index=True
            )

            if st.button("💾 Save Stock Portfolio Changes", type="primary"):
                # Clean columns before saving
                cols_to_save = ["Platform", "Ticker / Asset", "Category", "Shares / Quantity", "Avg Buy Price", "Current Price", "Currency"]
                save_stocks(edited_stocks[cols_to_save])
                st.success("Portfolio changes saved!")
                st.rerun()
        else:
            st.info("No investments recorded yet. Add your first COL Financial stock or MT5 trading asset on the left!")

# ---------------------------------------------------------
# TAB 5: 12-MONTH PROJECTED BUDGETING ENGINE
# ---------------------------------------------------------
with tab_proj:
    st.subheader("🔮 12-Month / Yearly Projected Budgeting Engine")
    st.markdown("Forecast your detailed expenses, income growth, and savings potential over the next 12 months.")

    pr_col1, pr_col2 = st.columns(2)
    with pr_col1:
        proj_base_inc = st.number_input("Base Projected Income (BHD/Month)", min_value=0.0, value=total_income_bhd, step=50.0)
        proj_inc_growth = st.slider("Expected Annual Income Growth (%)", 0.0, 20.0, 3.0, 0.5)
    with pr_col2:
        proj_fixed_needs = st.number_input("Projected Fixed Needs (BHD/Month)", min_value=0.0, value=needs_target, step=25.0)
        proj_inflation = st.slider("Estimated Inflation Rate (%)", 0.0, 15.0, 2.5, 0.5)

    months_list = [f"Month {m}" for m in range(1, 13)]
    proj_rows = []
    cum_savings = 0.0

    for m in range(1, 13):
        inc_m = proj_base_inc * (1.0 + (proj_inc_growth / 100.0) * ((m - 1) / 12.0))
        needs_m = proj_fixed_needs * (1.0 + (proj_inflation / 100.0) * ((m - 1) / 12.0))
        wants_m = inc_m * (wants_pct / 100.0)
        total_exp_m = needs_m + wants_m
        surplus_m = inc_m - total_exp_m
        cum_savings += surplus_m

        proj_rows.append({
            "Month": f"Month {m}",
            "Projected Income (BD)": round(inc_m, 2),
            "Essential Needs (BD)": round(needs_m, 2),
            "Lifestyle Wants (BD)": round(wants_m, 2),
            "Total Expenses (BD)": round(total_exp_m, 2),
            "Net Monthly Savings (BD)": round(surplus_m, 2),
            "Cumulative Savings (BD)": round(cum_savings, 2)
        })

    df_proj = pd.DataFrame(proj_rows)

    tot_proj_inc = df_proj["Projected Income (BD)"].sum()
    tot_proj_exp = df_proj["Total Expenses (BD)"].sum()
    tot_proj_sav = df_proj["Net Monthly Savings (BD)"].sum()

    pm1, pm2, pm3 = st.columns(3)
    pm1.metric("1-Year Projected Income", f"BD {tot_proj_inc:,.2f}", delta=f"₱ {tot_proj_inc * bhd_to_php:,.2f} PHP")
    pm2.metric("1-Year Projected Expenses", f"BD {tot_proj_exp:,.2f}", delta=f"-BD {tot_proj_exp:,.2f}", delta_color="inverse")
    pm3.metric("1-Year Projected Net Wealth Build", f"BD {tot_proj_sav:,.2f}", delta=f"₱ {tot_proj_sav * bhd_to_php:,.2f} PHP")

    st.markdown("---")
    st.dataframe(df_proj, use_container_width=True, hide_index=True)

    c_p1, c_p2 = st.columns(2)
    with c_p1:
        fig_p1 = px.bar(df_proj, x="Month", y=["Projected Income (BD)", "Total Expenses (BD)"], barmode="group", title="Month-by-Month Income vs. Expenses")
        st.plotly_chart(fig_p1, use_container_width=True)
    with c_p2:
        fig_p2 = px.line(df_proj, x="Month", y="Cumulative Savings (BD)", title="1-Year Cumulative Wealth Growth Trajectory", markers=True)
        st.plotly_chart(fig_p2, use_container_width=True)

# ---------------------------------------------------------
# TAB 6: MT5 PIP & MARGIN CALCULATOR
# ---------------------------------------------------------
with tab_calc:
    st.subheader("📐 MT5 Pip Value & Risk Calculator")
    st.markdown("Calculate pip value, required margin, and risk management for MetaTrader 5 position sizing.")

    pair = st.selectbox("Trading Asset / Pair", [
        "USDPHP", "BHDPHP", "USDCAD", "EURUSD", "GBPUSD", "USDJPY",
        "XAUUSD (Gold)", "USDCHF", "AUDUSD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"
    ])

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        lot_size = st.number_input("Position Size (Lots)", min_value=0.01, step=0.05, value=0.10)
        leverage = st.selectbox("Account Leverage", [10, 20, 50, 100, 200, 400, 500, 1000], index=4)
        account_curr = st.selectbox("Account Currency Base", ["USD", "BHD", "PHP"])

    with col_m2:
        entry_price = st.number_input("Entry Price", min_value=0.00001, value=58.50 if "PHP" in pair else (2650.0 if "XAU" in pair else 1.0850), format="%.5f")
        stop_loss_pips = st.number_input("Stop Loss (Pips)", min_value=1.0, step=5.0, value=30.0)
        take_profit_pips = st.number_input("Take Profit (Pips)", min_value=1.0, step=5.0, value=60.0)

    # Standard Forex calculations
    if "XAU" in pair:
        contract_size = 100
        pip_size = 0.01
    elif "JPY" in pair or "PHP" in pair:
        contract_size = 100000
        pip_size = 0.01
    else:
        contract_size = 100000
        pip_size = 0.0001

    pip_value_usd = lot_size * contract_size * pip_size
    req_margin_usd = (lot_size * contract_size * entry_price) / leverage if ("XAU" in pair or "EUR" in pair or "GBP" in pair) else (lot_size * contract_size) / leverage

    if account_curr == "BHD":
        pip_value_acc = pip_value_usd / bhd_to_usd
        req_margin_acc = req_margin_usd / bhd_to_usd
    elif account_curr == "PHP":
        pip_value_acc = pip_value_usd * (bhd_to_php / bhd_to_usd)
        req_margin_acc = req_margin_usd * (bhd_to_php / bhd_to_usd)
    else:
        pip_value_acc = pip_value_usd
        req_margin_acc = req_margin_usd

    sl_risk_acc = stop_loss_pips * pip_value_acc
    tp_reward_acc = take_profit_pips * pip_value_acc
    rr_ratio = take_profit_pips / stop_loss_pips if stop_loss_pips > 0 else 0.0

    st.markdown("---")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Pip Value", f"{account_curr} {pip_value_acc:,.2f}")
    r2.metric("Required Margin", f"{account_curr} {req_margin_acc:,.2f}")
    r3.metric("Max Risk (SL)", f"-{account_curr} {sl_risk_acc:,.2f}", delta_color="inverse")
    r4.metric("Risk : Reward Ratio", f"1 : {rr_ratio:.2f}")

# ---------------------------------------------------------
# TAB 7: LIVE CURRENCY CONVERTER
# ---------------------------------------------------------
with tab_converter:
    st.subheader("💱 Live Multi-Currency Converter")
    st.caption(f"Status: {rate_status} (Live base 1 BHD)")

    cur_col1, cur_col2 = st.columns(2)
    with cur_col1:
        conv_amount = st.number_input("Amount to Convert", min_value=0.01, value=100.0, step=10.0)
        from_curr = st.selectbox("From Currency", ["BHD", "PHP", "USD", "EUR", "GBP", "CAD", "AED", "SAR"], index=0)

    with cur_col2:
        to_curr = st.selectbox("To Currency", ["PHP", "BHD", "USD", "EUR", "GBP", "CAD", "AED", "SAR"], index=0)

    # Convert via BHD pivot
    amount_in_bhd = conv_amount / rates_dict[from_curr]
    converted_amount = amount_in_bhd * rates_dict[to_curr]

    st.markdown(f"""
    <div style="background-color:#F0FDF4; border:2px solid #10B981; padding:20px; border-radius:12px; text-align:center; margin-top:20px;">
        <div style="font-size:1.1rem; color:#065F46; font-weight:700;">CONVERTED EQUIVALENT</div>
        <div style="font-size:2.2rem; color:#047857; font-weight:900;">{to_curr} {converted_amount:,.2f}</div>
        <div style="font-size:0.95rem; color:#065F46; margin-top:6px;">{from_curr} {conv_amount:,.2f} @ Rate 1 {from_curr} = {rates_dict[to_curr]/rates_dict[from_curr]:,.4f} {to_curr}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ⚡ Quick Reference Exchange Rates (Base 1 BHD)")
    qr1, qr2, qr3, qr4 = st.columns(4)
    qr1.metric("1 BHD in PHP", f"₱ {rates_dict['PHP']:,.2f}")
    qr2.metric("1 BHD in USD", f"$ {rates_dict['USD']:,.2f}")
    qr3.metric("1 BHD in EUR", f"€ {rates_dict['EUR']:,.2f}")
    qr4.metric("1 BHD in GBP", f"£ {rates_dict['GBP']:,.2f}")
