import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import os
import json
import urllib.request

# Set Streamlit page config
st.set_page_config(
    page_title="Rogee Financial Command Center",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown('''
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
    .notice-banner-green {
        background-color: #ECFDF5;
        border-left: 6px solid #10B981;
        padding: 1rem;
        border-radius: 6px;
        color: #065F46;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .notice-banner-red {
        background-color: #FEF2F2;
        border-left: 6px solid #EF4444;
        padding: 1rem;
        border-radius: 6px;
        color: #991B1B;
        font-weight: 600;
        margin-bottom: 1rem;
    }
</style>
''', unsafe_allow_html=True)

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
    clean_user = username.lower().replace(" ", "_") if username else "rogee"
    data_file = f"expenses_{clean_user}.csv"
    stocks_file = f"stocks_{clean_user}.csv"
    proj_file = f"projections_{clean_user}.csv"
    settings_file = f"settings_{clean_user}.json"

    # Migrate default expenses if profile file doesn't exist
    if not os.path.exists(data_file) and os.path.exists(DATA_FILE_DEFAULT):
        try:
            df = pd.read_csv(DATA_FILE_DEFAULT)
            df.to_csv(data_file, index=False)
        except Exception:
            pass
    return data_file, stocks_file, proj_file, settings_file

def load_data(data_file):
    if os.path.exists(data_file):
        try:
            df = pd.read_csv(data_file)
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date']).dt.date
            # Ensure missing columns exist
            for col in MASTER_COLS:
                if col not in df.columns:
                    df[col] = None
            df = df.reindex(columns=MASTER_COLS)
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=MASTER_COLS)

def save_data(df, data_file):
    df = df.reindex(columns=MASTER_COLS)
    df.to_csv(data_file, index=False)

def load_stocks(stocks_file):
    cols = ["Ticker", "Name", "Shares", "Avg Price (PHP/USD)", "Currency", "Market Price (PHP/USD)"]
    if os.path.exists(stocks_file):
        try:
            df = pd.read_csv(stocks_file)
            for c in cols:
                if c not in df.columns:
                    df[c] = None
            return df[cols]
        except Exception:
            pass
    demo_stocks = pd.DataFrame([
        {"Ticker": "SM", "Name": "SM Investments", "Shares": 500, "Avg Price (PHP/USD)": 850.0, "Currency": "PHP", "Market Price (PHP/USD)": 910.0},
        {"Ticker": "BDO", "Name": "BDO Unibank", "Shares": 1200, "Avg Price (PHP/USD)": 130.0, "Currency": "PHP", "Market Price (PHP/USD)": 145.0},
        {"Ticker": "XAUUSD", "Name": "Gold Trading Capital", "Shares": 1, "Avg Price (PHP/USD)": 2000.0, "Currency": "USD", "Market Price (PHP/USD)": 2720.0}
    ])
    return demo_stocks

def save_stocks(df, stocks_file):
    df.to_csv(stocks_file, index=False)

def load_user_settings(settings_file):
    defaults = {
        "salary_bhd": 500.0,
        "sideline_bhd": 0.0,
        "business_bhd": 0.0,
        "other_bhd": 0.0,
        "needs_pct": 50,
        "wants_pct": 30,
        "savings_pct": 20,
        "currency_symbol": "BD"
    }
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

def load_projections(proj_file, monthly_income, needs_target, wants_target, savings_target):
    proj_cols = [
        "Month",
        "Projected Income (BHD)",
        "Needs & Debts (BHD)",
        "Wants (BHD)",
        "Savings & Investments (BHD)",
        "Total Expenses (BHD)",
        "Net Surplus (BHD)",
        "Cumulative Savings (BHD)"
    ]
    if os.path.exists(proj_file):
        try:
            df = pd.read_csv(proj_file)
            rename_map = {
                "Income (BHD)": "Projected Income (BHD)",
                "Projected Income": "Projected Income (BHD)",
                "Income": "Projected Income (BHD)",
                "Expenses (BHD)": "Total Expenses (BHD)",
                "Total Expenses": "Total Expenses (BHD)",
                "Net Savings": "Net Surplus (BHD)",
                "Cumulative Balance": "Cumulative Savings (BHD)"
            }
            df = df.rename(columns=rename_map)
            for c in proj_cols:
                if c not in df.columns:
                    df[c] = 0.0
            return df[proj_cols]
        except Exception:
            pass
    
    months = [f"Month {i}" for i in range(1, 13)]
    rows = []
    cum_savings = 0.0
    for m in months:
        tot_exp = needs_target + wants_target
        surplus = monthly_income - tot_exp
        cum_savings += savings_target + max(0.0, surplus)
        rows.append({
            "Month": m,
            "Projected Income (BHD)": round(monthly_income, 2),
            "Needs & Debts (BHD)": round(needs_target, 2),
            "Wants (BHD)": round(wants_target, 2),
            "Savings & Investments (BHD)": round(savings_target, 2),
            "Total Expenses (BHD)": round(tot_exp, 2),
            "Net Surplus (BHD)": round(surplus, 2),
            "Cumulative Savings (BHD)": round(cum_savings, 2)
        })
    return pd.DataFrame(rows)

def save_projections(df, proj_file):
    df.to_csv(proj_file, index=False)

# Live Exchange Rates with fallback
@st.cache_data(ttl=3600)
def fetch_exchange_rates():
    try:
        url = "https://open.er-api.com/v6/latest/BHD"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            rates = data.get("rates", {})
            php_rate = rates.get("PHP", 155.0)
            usd_rate = rates.get("USD", 2.6596)
            eur_rate = rates.get("EUR", 2.45)
            gbp_rate = rates.get("GBP", 2.10)
            sar_rate = rates.get("SAR", 9.97)
            aed_rate = rates.get("AED", 9.77)
            cad_rate = rates.get("CAD", 3.65)
            return {
                "PHP": php_rate, "USD": usd_rate, "EUR": eur_rate,
                "GBP": gbp_rate, "SAR": sar_rate, "AED": aed_rate,
                "CAD": cad_rate, "is_live": True
            }
    except Exception:
        return {
            "PHP": 155.0, "USD": 2.6596, "EUR": 2.45,
            "GBP": 2.10, "SAR": 9.97, "AED": 9.77,
            "CAD": 3.65, "is_live": False
        }

rates = fetch_exchange_rates()
bhd_to_php = rates["PHP"]
bhd_to_usd = rates["USD"]

USER_PASSCODES = {
    "Rogee": os.environ.get("ROGEE_KEY", "rogee2026"),
    "User 2": os.environ.get("USER2_KEY", "user2026"),
    "User 3": os.environ.get("USER3_KEY", "user2026"),
    "User 4": os.environ.get("USER4_KEY", "user2026")
}

if "authenticated_user" not in st.session_state:
    st.session_state["authenticated_user"] = None

if st.session_state["authenticated_user"] is None:
    st.markdown('<div style="text-align:center; padding: 2.5rem 1rem;"><h1 style="color:#1E3A8A; font-size: 2.5rem; margin-bottom: 0.5rem;">🔒 Rogee Financial Portal</h1><p style="color:#4B5563; font-size: 1.1rem;">Select your profile and enter your private passkey to access your financial command center.</p></div>', unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("login_form"):
            selected_user = st.selectbox("Select Profile", list(USER_PASSCODES.keys()))
            entered_passcode = st.text_input("Enter Passkey", type="password")
            login_submit = st.form_submit_button("🔓 Unlock Portal", use_container_width=True)
            if login_submit:
                if entered_passcode == USER_PASSCODES.get(selected_user):
                    st.session_state["authenticated_user"] = selected_user
                    st.success(f"Welcome back, {selected_user}!")
                    st.rerun()
                else:
                    st.error("Invalid passkey. Please try again.")
        with st.expander("💡 Default Passkeys Reference"):
            st.info("**Rogee**: `rogee2026` | **User 2/3/4**: `user2026`\n*You can customize passkeys via Streamlit Cloud Secrets.*")
    st.stop()

active_user = st.session_state["authenticated_user"]
user_data_file, user_stocks_file, user_proj_file, user_settings_file = get_user_file_paths(active_user)

saved_settings = load_user_settings(user_settings_file)

st.sidebar.title(f"👤 {active_user}'s Settings")

if st.sidebar.button("🔒 Sign Out / Lock Portal", use_container_width=True):
    st.session_state["authenticated_user"] = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("💵 Income Streams")

salary_bhd = st.sidebar.number_input("Primary Monthly Salary (BHD)", min_value=0.0, value=float(saved_settings.get("salary_bhd", 500.0)), step=10.0)
sideline_bhd = st.sidebar.number_input("Sideline / Freelance Income (BHD)", min_value=0.0, value=float(saved_settings.get("sideline_bhd", 0.0)), step=10.0)
business_bhd = st.sidebar.number_input("Business Income (BHD)", min_value=0.0, value=float(saved_settings.get("business_bhd", 0.0)), step=10.0)
other_bhd = st.sidebar.number_input("Other Income / Bonus (BHD)", min_value=0.0, value=float(saved_settings.get("other_bhd", 0.0)), step=10.0)

total_income_bhd = salary_bhd + sideline_bhd + business_bhd + other_bhd
total_income_php = total_income_bhd * bhd_to_php
total_income_usd = total_income_bhd * bhd_to_usd

new_settings = {
    "salary_bhd": salary_bhd,
    "sideline_bhd": sideline_bhd,
    "business_bhd": business_bhd,
    "other_bhd": other_bhd,
    "needs_pct": saved_settings.get("needs_pct", 50),
    "wants_pct": saved_settings.get("wants_pct", 30),
    "savings_pct": saved_settings.get("savings_pct", 20)
}

st.sidebar.markdown(f"**Total Income**: BD {total_income_bhd:,.2f} | ₱ {total_income_php:,.2f} | $ {total_income_usd:,.2f}")

st.sidebar.markdown("---")

needs_pct = st.sidebar.slider("Needs & Debts Target %", 0, 100, int(saved_settings.get("needs_pct", 50)))
wants_pct = st.sidebar.slider("Wants Target %", 0, 100, int(saved_settings.get("wants_pct", 30)))
savings_pct = st.sidebar.slider("Savings & Investments Target %", 0, 100, int(saved_settings.get("savings_pct", 20)))

new_settings["needs_pct"] = needs_pct
new_settings["wants_pct"] = wants_pct
new_settings["savings_pct"] = savings_pct

if new_settings != saved_settings:
    save_user_settings(new_settings, user_settings_file)

total_pct = needs_pct + wants_pct + savings_pct
if total_pct != 100:
    st.sidebar.warning(f"Allocation total is {total_pct}%. It should equal 100%.")

framework_title = f"{needs_pct}/{wants_pct}/{savings_pct} Budgeting Framework"

needs_target = total_income_bhd * (needs_pct / 100.0)
wants_target = total_income_bhd * (wants_pct / 100.0)
savings_target = total_income_bhd * (savings_pct / 100.0)

df_expenses = load_data(user_data_file)
df_stocks = load_stocks(user_stocks_file)

st.markdown('<div class="main-header">Rogee Financial Command Center</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Personal Multi-Currency Finance & Investment Manager ({framework_title})</div>', unsafe_allow_html=True)

tab_dash, tab_add, tab_history, tab_proj, tab_invest, tab_conv, tab_pip = st.tabs([
    "📊 Dashboard & Analytics",
    "➕ Record Expense / Payment",
    "📋 Transaction History",
    "🔮 12-Month Projections",
    "📈 MT5 & COL Investments",
    "💱 Live Currency Converter",
    "📐 MT5 Pip Calculator"
])

def process_ledger_totals(df):
    if df.empty:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    
    bhd_billed, bhd_paid, bhd_pending = 0.0, 0.0, 0.0
    php_billed, php_paid, php_pending = 0.0, 0.0, 0.0
    usd_billed, usd_paid, usd_pending = 0.0, 0.0, 0.0

    for _, row in df.iterrows():
        curr = str(row.get("Currency", "BHD")).upper()
        billed = float(row.get("Billed Amount", 0.0) or 0.0)
        paid = float(row.get("Actual Paid", 0.0) or 0.0)
        pending = billed - paid

        if curr == "PHP":
            php_billed += billed
            php_paid += paid
            php_pending += pending
        elif curr == "USD":
            usd_billed += billed
            usd_paid += paid
            usd_pending += pending
        else:
            bhd_billed += billed
            bhd_paid += paid
            bhd_pending += pending

    php_billed_in_bhd = php_billed / bhd_to_php if bhd_to_php > 0 else 0.0
    php_paid_in_bhd = php_paid / bhd_to_php if bhd_to_php > 0 else 0.0
    php_pending_in_bhd = php_pending / bhd_to_php if bhd_to_php > 0 else 0.0

    usd_billed_in_bhd = usd_billed / 2.6596
    usd_paid_in_bhd = usd_paid / 2.6596
    usd_pending_in_bhd = usd_pending / 2.6596

    grand_total_billed_bhd = bhd_billed + php_billed_in_bhd + usd_billed_in_bhd
    grand_total_paid_bhd = bhd_paid + php_paid_in_bhd + usd_paid_in_bhd
    grand_total_pending_bhd = bhd_pending + php_pending_in_bhd + usd_pending_in_bhd

    return (bhd_billed, bhd_paid, bhd_pending, 
            php_billed, php_paid, php_pending, php_billed_in_bhd, php_paid_in_bhd, php_pending_in_bhd,
            grand_total_billed_bhd, grand_total_paid_bhd, grand_total_pending_bhd)

(bhd_billed, bhd_paid, bhd_pending,
 php_billed, php_paid, php_pending, php_billed_in_bhd, php_paid_in_bhd, php_pending_in_bhd,
 grand_total_billed_bhd, grand_total_paid_bhd, grand_total_pending_bhd) = process_ledger_totals(df_expenses)

with tab_dash:
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Monthly Net Income", f"BD {total_income_bhd:,.2f}")
    m2.metric("Total Spent / Paid", f"BD {grand_total_paid_bhd:,.2f}", delta=f"-BD {grand_total_paid_bhd:,.2f}", delta_color="inverse")
    
    rem_balance = total_income_bhd - grand_total_paid_bhd
    if rem_balance >= 0:
        m3.metric("Remaining Cash Balance", f"BD {rem_balance:,.2f}", delta=f"BD {rem_balance:,.2f}")
    else:
        m3.metric("Over Budget Limit Deficit", f"-BD {abs(rem_balance):,.2f}", delta=f"-BD {abs(rem_balance):,.2f}", delta_color="inverse")

    savings_spent_bhd = 0.0
    if not df_expenses.empty:
        sav_rows = df_expenses[df_expenses["Main Category"].astype(str).str.contains("Savings|Investments", case=False, na=False)]
        for _, r in sav_rows.iterrows():
            c = str(r.get("Currency", "BHD")).upper()
            amt = float(r.get("Actual Paid", 0.0) or 0.0)
            if c == "PHP":
                savings_spent_bhd += amt / bhd_to_php
            elif c == "USD":
                savings_spent_bhd += amt / 2.6596
            else:
                savings_spent_bhd += amt

    current_sav_rate = (savings_spent_bhd / total_income_bhd * 100) if total_income_bhd > 0 else 0.0
    m4.metric("Savings & Investment Rate", f"{current_sav_rate:.1f}%", delta=f"{current_sav_rate - savings_pct:.1f}% vs Target")
    m5.metric("Total Expenses to be Paid", f"BD {grand_total_billed_bhd:,.2f}", delta=f"Pending: BD {grand_total_pending_bhd:,.2f}")

    st.markdown("---")

    st.subheader(f"📊 {framework_title} Breakdown")

    needs_spent_bhd = 0.0
    wants_spent_bhd = 0.0
    if not df_expenses.empty:
        for _, r in df_expenses.iterrows():
            cat = str(r.get("Main Category", ""))
            c = str(r.get("Currency", "BHD")).upper()
            amt = float(r.get("Actual Paid", 0.0) or 0.0)
            amt_bhd = (amt / bhd_to_php) if c == "PHP" else ((amt / 2.6596) if c == "USD" else amt)
            
            if "Needs" in cat or "Debts" in cat:
                needs_spent_bhd += amt_bhd
            elif "Wants" in cat:
                wants_spent_bhd += amt_bhd

    cat_summary = [
        {"Category": f"Needs & Debts ({needs_pct}%)", "Target (%)": f"{needs_pct}%", "Target (BD)": needs_target, "Actual Paid (BD)": needs_spent_bhd, "Difference (BD)": needs_target - needs_spent_bhd, "Status": "On Track" if needs_spent_bhd <= needs_target else "Over Target"},
        {"Category": f"Wants ({wants_pct}%)", "Target (%)": f"{wants_pct}%", "Target (BD)": wants_target, "Actual Paid (BD)": wants_spent_bhd, "Difference (BD)": wants_target - wants_spent_bhd, "Status": "On Track" if wants_spent_bhd <= wants_target else "Over Target"},
        {"Category": f"Savings & Investments ({savings_pct}%)", "Target (%)": f"{savings_pct}%", "Target (BD)": savings_target, "Actual Paid (BD)": savings_spent_bhd, "Difference (BD)": savings_spent_bhd - savings_target, "Status": "Goal Met" if savings_spent_bhd >= savings_target else "Under Target"}
    ]
    df_cat = pd.DataFrame(cat_summary)
    st.dataframe(
        df_cat.style.format({
            "Target (BD)": "BD {:,.2f}",
            "Actual Paid (BD)": "BD {:,.2f}",
            "Difference (BD)": "BD {:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    dc1, dc2 = st.columns(2)

    with dc1:
        st.subheader("Target vs. Actual Spending (BD)")
        fig_bar = go.Figure(data=[
            go.Bar(name='Target', x=["Needs & Debts", "Wants", "Savings"], y=[needs_target, wants_target, savings_target], marker_color='#93C5FD'),
            go.Bar(name='Actual Spent', x=["Needs & Debts", "Wants", "Savings"], y=[needs_spent_bhd, wants_spent_bhd, savings_spent_bhd], marker_color='#1D4ED8')
        ])
        fig_bar.update_layout(barmode='group', yaxis_title="Amount (BD)", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    with dc2:
        st.subheader("Actual Expense Distribution")
        tot_actual_spent = needs_spent_bhd + wants_spent_bhd + savings_spent_bhd
        if tot_actual_spent > 0:
            fig_pie = px.pie(
                values=[needs_spent_bhd, wants_spent_bhd, savings_spent_bhd],
                names=["Needs & Debts", "Wants", "Savings & Investments"],
                color_discrete_sequence=['#2563EB', '#F59E0B', '#10B981'],
                hole=0.45
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expenses recorded yet. Add your first transaction in the 'Record Expense' tab!")

with tab_add:
    st.subheader("Record a New Expense / Payment")

    with st.form("add_transaction_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            tx_date = st.date_input("Date", value=datetime.today())
            tx_main_cat = st.selectbox("Category", [
                f"Needs & Debts ({needs_pct}%)",
                f"Wants ({wants_pct}%)",
                f"Savings & Investments ({savings_pct}%)",
                "100% Priority",
                "Debts & Credits Payoff"
            ])

            if "Needs" in tx_main_cat or "Debts" in tx_main_cat:
                sub_options = ["Housing / Rent / Mortgage", "Utilities & Bills", "Groceries", "Transportation / Fuel", "Healthcare & Insurance", "Tuition & Family", "Personal Loan", "Credit Card Debt", "Settle Debt"]
            elif "Wants" in tx_main_cat:
                sub_options = ["Dining Out & Coffee", "Entertainment & Subscriptions", "Shopping & Apparel", "Hobbies & Travel", "Miscellaneous"]
            else:
                sub_options = ["Emergency Fund", "COL Financial Stock Investment", "MT5 Forex Capital", "Retirement Fund", "Major Goal Savings"]

            tx_sub_cat = st.selectbox("Sub Category", sub_options)
            tx_merchant = st.text_input("Merchant / Description", placeholder="e.g. Landlord, Utility, Grocery Store")

        with col2:
            tx_curr = st.selectbox("Transaction Currency", ["BHD", "PHP", "USD"])
            tx_billed = st.number_input(f"Planned / Billed Amount ({tx_curr})", min_value=0.0, step=5.0, value=50.0)
            tx_paid = st.number_input(f"Actual Amount Paid ({tx_curr})", min_value=0.0, step=5.0, value=50.0)
            tx_pay_method = st.selectbox("Payment Method", ["Bank Transfer", "Credit Card", "Debit Card", "Cash"])

        tx_submit = st.form_submit_button("💾 Save Transaction to Ledger", use_container_width=True)

        if tx_submit:
            status = "Paid" if tx_paid >= tx_billed else ("Partially Paid" if tx_paid > 0 else "Not Paid")
            pending = tx_billed - tx_paid
            pct_paid = (tx_paid / tx_billed * 100) if tx_billed > 0 else 100.0
            pct_rem = 100.0 - pct_paid

            if tx_curr == "PHP":
                equiv_str = f"BD {tx_billed/bhd_to_php:.2f} | $ {tx_billed/(bhd_to_php/bhd_to_usd):.2f}"
            elif tx_curr == "USD":
                equiv_str = f"BD {tx_billed/2.6596:.2f} | ₱ {tx_billed*58.28:,.2f}"
            else:
                equiv_str = f"₱ {tx_billed*bhd_to_php:,.2f} | $ {tx_billed*bhd_to_usd:,.2f}"

            item_num = len(df_expenses) + 1

            new_tx = {
                "Item #": item_num,
                "Date": tx_date,
                "Main Category": tx_main_cat,
                "Sub Category": tx_sub_cat,
                "Merchant/Description": tx_merchant if tx_merchant else "Unspecified",
                "Billed Amount": tx_billed,
                "Actual Paid": tx_paid,
                "Currency": tx_curr,
                "Pending Due": pending,
                "% Paid": round(pct_paid, 1),
                "% Remaining": round(pct_rem, 1),
                "Equivalent": equiv_str,
                "Status": status,
                "Payment Method": tx_pay_method
            }

            df_expenses = pd.concat([df_expenses, pd.DataFrame([new_tx])], ignore_index=True)
            save_data(df_expenses, user_data_file)
            st.success(f"Successfully recorded transaction: {tx_merchant} ({tx_curr} {tx_paid:,.2f})")
            st.rerun()

with tab_history:
    st.subheader("📋 Recorded Expense History & Ledger")

    rem_net_cash = total_income_bhd - grand_total_paid_bhd
    if rem_net_cash >= 0:
        st.markdown(f'''
        <div class="notice-banner-green">
            🟢 <b>WITHIN BUDGET STATUS NOTICE</b><br>
            Remaining Net Cash Balance: <b>BD {rem_net_cash:,.2f}</b> | <b>₱ {rem_net_cash * bhd_to_php:,.2f} PHP</b> | <b>$ {rem_net_cash * bhd_to_usd:,.2f} USD</b>
        </div>
        ''', unsafe_allow_html=True)
    else:
        deficit_bhd = abs(rem_net_cash)
        st.markdown(f'''
        <div class="notice-banner-red">
            🚨 <b>OVER BUDGET STATUS NOTICE</b><br>
            Total payments exceed income limit by: <b>-BD {deficit_bhd:,.2f}</b> | <b>-₱ {deficit_bhd * bhd_to_php:,.2f} PHP</b> | <b>-$ {deficit_bhd * bhd_to_usd:,.2f} USD</b>
        </div>
        ''', unsafe_allow_html=True)

    if not df_expenses.empty:
        df_expenses = df_expenses.reindex(columns=MASTER_COLS)

        st.markdown("##### ✏️ Interactive Editable Ledger Grid")
        edited_ledger = st.data_editor(
            df_expenses,
            use_container_width=True,
            hide_index=True,
            key="ledger_grid_editor"
        )

        if st.button("💾 Save Ledger Changes", type="primary"):
            for idx, r in edited_ledger.iterrows():
                b = float(r.get("Billed Amount", 0.0) or 0.0)
                p = float(r.get("Actual Paid", 0.0) or 0.0)
                edited_ledger.at[idx, "Pending Due"] = b - p
                edited_ledger.at[idx, "% Paid"] = round((p / b * 100) if b > 0 else 100.0, 1)
                edited_ledger.at[idx, "% Remaining"] = round(100.0 - edited_ledger.at[idx, "% Paid"], 1)
                edited_ledger.at[idx, "Status"] = "Paid" if p >= b else ("Partially Paid" if p > 0 else "Not Paid")
            
            save_data(edited_ledger, user_data_file)
            st.success("Ledger changes saved successfully!")
            st.rerun()

        st.markdown("---")

        st.markdown("##### 🎨 Status-Highlighted Color Ledger View")
        def style_status_row(row):
            st_val = str(row.get("Status", ""))
            if st_val == "Paid":
                return ['background-color: #D1FAE5; color: #065F46; font-weight: 500;'] * len(row)
            elif st_val == "Partially Paid":
                return ['background-color: #FEF3C7; color: #92400E; font-weight: 500;'] * len(row)
            else:
                return ['background-color: #FEE2E2; color: #991B1B; font-weight: 500;'] * len(row)

        st.dataframe(
            df_expenses.style.apply(style_status_row, axis=1),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        st.subheader("💰 Total Outstanding & Payment Ledger Summary")

        sc1, sc2, sc3, sc4 = st.columns(4)

        with sc1:
            st.markdown(f'''
            <div style="background-color:#EFF6FF; padding:1rem; border-radius:8px; border: 1px solid #BFDBFE;">
                <h4 style="color:#1E40AF; margin-top:0;">🇧🇭 BHD Currency Bills</h4>
                <p style="color:#1E3A8A; margin-bottom:4px;"><b>Total Billed:</b> BD {bhd_billed:,.2f}</p>
                <p style="color:#166534; margin-bottom:4px;"><b>Actual Paid:</b> BD {bhd_paid:,.2f}</p>
                <p style="color:#991B1B; margin-bottom:0;"><b>Pending Due:</b> BD {bhd_pending:,.2f}</p>
            </div>
            ''', unsafe_allow_html=True)

        with sc2:
            st.markdown(f'''
            <div style="background-color:#F0FDF4; padding:1rem; border-radius:8px; border: 1px solid #BBF7D0;">
                <h4 style="color:#166534; margin-top:0;">🇵🇭 PHP Currency Bills</h4>
                <p style="color:#1E3A8A; margin-bottom:4px;"><b>Total Billed:</b> ₱ {php_billed:,.2f} <br><small>(~BD {php_billed_in_bhd:,.2f})</small></p>
                <p style="color:#166534; margin-bottom:4px;"><b>Actual Paid:</b> ₱ {php_paid:,.2f} <br><small>(~BD {php_paid_in_bhd:,.2f})</small></p>
                <p style="color:#991B1B; margin-bottom:0;"><b>Pending Due:</b> ₱ {php_pending:,.2f} <br><small>(~BD {php_pending_in_bhd:,.2f})</small></p>
            </div>
            ''', unsafe_allow_html=True)

        with sc3:
            usd_billed_bhd = usd_billed / 2.6596
            usd_paid_bhd = usd_paid / 2.6596
            usd_pending_bhd = usd_pending / 2.6596
            st.markdown(f'''
            <div style="background-color:#FEFCE8; padding:1rem; border-radius:8px; border: 1px solid #FEF08A;">
                <h4 style="color:#854D0E; margin-top:0;">💵 USD Currency Bills</h4>
                <p style="color:#1E3A8A; margin-bottom:4px;"><b>Total Billed:</b> $ {usd_billed:,.2f} <br><small>(~BD {usd_billed_bhd:,.2f})</small></p>
                <p style="color:#166534; margin-bottom:4px;"><b>Actual Paid:</b> $ {usd_paid:,.2f} <br><small>(~BD {usd_paid_bhd:,.2f})</small></p>
                <p style="color:#991B1B; margin-bottom:0;"><b>Pending Due:</b> $ {usd_pending:,.2f} <br><small>(~BD {usd_pending_bhd:,.2f})</small></p>
            </div>
            ''', unsafe_allow_html=True)

        with sc4:
            st.markdown(f'''
            <div style="background-color:#F5F3FF; padding:1rem; border-radius:8px; border: 1px solid #DDD6FE;">
                <h4 style="color:#5B21B6; margin-top:0;">🌍 Combined Grand Total (In BD)</h4>
                <p style="color:#1E3A8A; margin-bottom:4px;"><b>Total Bills (BD):</b> BD {grand_total_billed_bhd:,.2f}</p>
                <p style="color:#166534; margin-bottom:4px;"><b>Total Paid (BD):</b> BD {grand_total_paid_bhd:,.2f}</p>
                <p style="color:#991B1B; margin-bottom:0;"><b>Total Pending (BD):</b> BD {grand_total_pending_bhd:,.2f}</p>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown("---")

        csv_download = df_expenses.reindex(columns=MASTER_COLS).to_csv(index=False)
        st.download_button(
            label="📥 Download Transaction Ledger (CSV)",
            data=csv_download,
            file_name=f"rogee_ledger_{active_user.lower()}.csv",
            mime="text/csv"
        )
    else:
        st.info("No transaction history recorded yet. Use the 'Record Expense' tab to log your first payment!")

with tab_proj:
    st.subheader("🔮 12-Month Projected Budgeting & Wealth Forecast")
    st.markdown("View and customize your 12-month projected financial forecast. Edit any cell in the table below to adjust future budget calculations.")

    df_proj = load_projections(user_proj_file, total_income_bhd, needs_target, wants_target, savings_target)

    edited_proj = st.data_editor(
        df_proj,
        use_container_width=True,
        hide_index=True,
        key="proj_table_editor"
    )

    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        if st.button("💾 Save 12-Month Projections", type="primary", use_container_width=True):
            for idx, r in edited_proj.iterrows():
                inc = float(r.get("Projected Income (BHD)", 0.0) or 0.0)
                n = float(r.get("Needs & Debts (BHD)", 0.0) or 0.0)
                w = float(r.get("Wants (BHD)", 0.0) or 0.0)
                s = float(r.get("Savings & Investments (BHD)", 0.0) or 0.0)
                tot_exp = n + w
                surplus = inc - tot_exp
                edited_proj.at[idx, "Total Expenses (BHD)"] = round(tot_exp, 2)
                edited_proj.at[idx, "Net Surplus (BHD)"] = round(surplus, 2)
            
            running_cum = 0.0
            for idx in edited_proj.index:
                s = float(edited_proj.at[idx, "Savings & Investments (BHD)"])
                surplus = float(edited_proj.at[idx, "Net Surplus (BHD)"])
                running_cum += s + max(0.0, surplus)
                edited_proj.at[idx, "Cumulative Savings (BHD)"] = round(running_cum, 2)

            save_projections(edited_proj, user_proj_file)
            st.success("12-Month Projections saved successfully!")
            st.rerun()

    with pc2:
        if st.button("🔄 Auto-Recalculate Defaults", use_container_width=True):
            if os.path.exists(user_proj_file):
                os.remove(user_proj_file)
            st.success("Reset projections to baseline settings!")
            st.rerun()

    with pc3:
        csv_proj = edited_proj.to_csv(index=False)
        st.download_button(
            label="📥 Download Projections (CSV)",
            data=csv_proj,
            file_name=f"rogee_12month_projection_{active_user.lower()}.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown("---")

    # Safe column lookup for charts to guarantee zero KeyErrors regardless of custom column edits
    inc_col = "Projected Income (BHD)" if "Projected Income (BHD)" in edited_proj.columns else edited_proj.columns[1]
    exp_col = "Total Expenses (BHD)" if "Total Expenses (BHD)" in edited_proj.columns else edited_proj.columns[5]
    cum_col = "Cumulative Savings (BHD)" if "Cumulative Savings (BHD)" in edited_proj.columns else edited_proj.columns[-1]

    pr_col1, pr_col2 = st.columns(2)

    with pr_col1:
        st.subheader("Monthly Projected Income vs. Expenses (BHD)")
        fig_proj = go.Figure()
        fig_proj.add_trace(go.Bar(x=edited_proj["Month"], y=edited_proj[inc_col], name="Projected Income", marker_color="#3B82F6"))
        fig_proj.add_trace(go.Bar(x=edited_proj["Month"], y=edited_proj[exp_col], name="Projected Expenses", marker_color="#EF4444"))
        fig_proj.update_layout(barmode="group", yaxis_title="Amount (BD)", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_proj, use_container_width=True)

    with pr_col2:
        st.subheader("1-Year Cumulative Wealth Build-Up (BHD)")
        fig_cum = go.Figure()
        fig_cum.add_trace(go.Scatter(x=edited_proj["Month"], y=edited_proj[cum_col], mode="lines+markers", name="Cumulative Savings", line=dict(color="#10B981", width=3)))
        fig_cum.update_layout(yaxis_title="Cumulative Wealth (BD)", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_cum, use_container_width=True)

with tab_invest:
    st.subheader("📈 MT5 Trading Capital & COL Financial Stock Portfolio")
    st.markdown("Manage your stock holdings and forex trading capital in one unified view.")

    edited_stocks = st.data_editor(
        df_stocks,
        use_container_width=True,
        hide_index=True,
        key="stocks_grid_editor"
    )

    if st.button("💾 Save Portfolio Changes", type="primary"):
        save_stocks(edited_stocks, user_stocks_file)
        st.success("Investment portfolio updated successfully!")
        st.rerun()

    st.markdown("---")

    tot_val_php = 0.0
    tot_val_usd = 0.0

    for _, r in edited_stocks.iterrows():
        sh = float(r.get("Shares", 0) or 0)
        mp = float(r.get("Market Price (PHP/USD)", 0) or 0)
        c = str(r.get("Currency", "PHP")).upper()
        if c == "USD":
            tot_val_usd += sh * mp
        else:
            tot_val_php += sh * mp

    tot_val_php_in_bhd = tot_val_php / bhd_to_php if bhd_to_php > 0 else 0.0
    tot_val_usd_in_bhd = tot_val_usd / 2.6596
    grand_portfolio_bhd = tot_val_php_in_bhd + tot_val_usd_in_bhd

    pv1, pv2, pv3 = st.columns(3)
    pv1.metric("COL Financial Portfolio (PHP)", f"₱ {tot_val_php:,.2f}", delta=f"~BD {tot_val_php_in_bhd:,.2f}")
    pv2.metric("MT5 Forex Capital (USD)", f"$ {tot_val_usd:,.2f}", delta=f"~BD {tot_val_usd_in_bhd:,.2f}")
    pv3.metric("Grand Total Investment Portfolio (BHD)", f"BD {grand_portfolio_bhd:,.2f}")

with tab_conv:
    st.subheader("💱 Live Multi-Currency Converter & Exchange Rates")
    
    status_msg = "🟢 Connected Live API" if rates["is_live"] else "🟡 Offline Fallback Rates"
    st.info(f"<b>Market Exchange Rates Status:</b> {status_msg} | Base Currency: 1 BD (Bahraini Dinar)", unsafe_allow_html=True)

    cr1, cr2, cr3, cr4 = st.columns(4)
    cr1.metric("1 BD → PHP", f"₱ {bhd_to_php:.2f} PHP")
    cr2.metric("1 BD → USD", f"$ {bhd_to_usd:.4f} USD")
    cr3.metric("1 BD → EUR", f"€ {rates['EUR']:.2f} EUR")
    cr4.metric("1 BD → SAR / AED", f"{rates['SAR']:.2f} SAR | {rates['AED']:.2f} AED")

    st.markdown("---")
    st.subheader("On-the-Spot Converter Tool")
    
    cv_col1, cv_col2, cv_col3 = st.columns(3)
    with cv_col1:
        conv_amount = st.number_input("Amount to Convert", min_value=0.01, value=100.0, step=10.0)
    with cv_col2:
        from_curr = st.selectbox("From Currency", ["BHD", "PHP", "USD", "EUR", "GBP", "SAR", "AED"])
    with cv_col3:
        to_curr = st.selectbox("To Currency", ["PHP", "BHD", "USD", "EUR", "GBP", "SAR", "AED"])

    curr_to_bhd_map = {
        "BHD": 1.0,
        "PHP": 1.0 / bhd_to_php,
        "USD": 1.0 / bhd_to_usd,
        "EUR": 1.0 / rates["EUR"],
        "GBP": 1.0 / rates["GBP"],
        "SAR": 1.0 / rates["SAR"],
        "AED": 1.0 / rates["AED"]
    }

    amount_in_bhd = conv_amount * curr_to_bhd_map.get(from_curr, 1.0)
    converted_result = amount_in_bhd / curr_to_bhd_map.get(to_curr, 1.0)

    st.success(f"**{conv_amount:,.2f} {from_curr}** = **{converted_result:,.2f} {to_curr}** (BD Equivalent: BD {amount_in_bhd:,.2f})")

with tab_pip:
    st.subheader("📐 MT5 Pip Value, Margin & Position Risk Calculator")

    pip_c1, pip_c2 = st.columns(2)

    with pip_c1:
        pair = st.selectbox("Select Currency Pair / Asset", ["USDPHP", "BHDPHP", "XAUUSD (Gold)", "EURUSD", "GBPUSD", "USDJPY", "USDCAD", "USDCHF"])
        lot_size = st.number_input("Lot Size (Standard Lots)", min_value=0.01, value=1.0, step=0.1)
        leverage = st.selectbox("Account Leverage", ["1:100", "1:200", "1:500", "1:1000"], index=2)
        entry_price = st.number_input("Entry Price", min_value=0.0001, value=2720.0 if "XAU" in pair else (58.25 if "PHP" in pair else 1.0850), step=0.01)
        exit_price = st.number_input("Target / Exit Price", min_value=0.0001, value=2735.0 if "XAU" in pair else (58.50 if "PHP" in pair else 1.0900), step=0.01)

    with pip_c2:
        st.markdown("#### 📊 Trade Calculation Breakdown")
        
        if "XAU" in pair:
            pip_size = 0.1
            pip_val_usd = lot_size * 10.0
            price_diff = exit_price - entry_price
            pnl_usd = price_diff * 100 * lot_size
        elif "JPY" in pair:
            pip_size = 0.01
            pip_val_usd = (0.01 / entry_price) * (lot_size * 100000)
            pnl_usd = (exit_price - entry_price) / pip_size * pip_val_usd
        else:
            pip_size = 0.0001
            pip_val_usd = lot_size * 10.0
            pnl_usd = (exit_price - entry_price) * 10000 * pip_val_usd

        lev_num = int(leverage.split(":")[1])
        contract_size = 100 if "XAU" in pair else 100000
        margin_usd = (lot_size * contract_size * entry_price) / lev_num

        pnl_bhd = pnl_usd / 2.6596
        pnl_php = pnl_usd * 58.28

        st.info(f"""
        * **Pip Value (USD)**: $ {pip_val_usd:.2f} per pip
        * **Required Margin**: $ {margin_usd:,.2f} USD (~BD {margin_usd/2.6596:,.2f})
        * **Projected Trade P&L**: **$ {pnl_usd:,.2f} USD**
        * **P&L in BD**: **BD {pnl_bhd:,.2f}**
        * **P&L in PHP**: **₱ {pnl_php:,.2f} PHP**
        """)
