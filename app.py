import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import os
import requests

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Rogee Financial Command Center",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    .notice-banner-green {
        background-color: #ECFDF5;
        border-left: 5px solid #10B981;
        padding: 1rem;
        border-radius: 6px;
        color: #065F46;
        font-weight: 600;
        margin-bottom: 1.2rem;
    }
    .notice-banner-red {
        background-color: #FEF2F2;
        border-left: 5px solid #EF4444;
        padding: 1rem;
        border-radius: 6px;
        color: #991B1B;
        font-weight: 600;
        margin-bottom: 1.2rem;
    }
    .summary-card-blue {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 8px;
        padding: 1rem;
        color: #1E40AF;
    }
    .summary-card-green {
        background-color: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-radius: 8px;
        padding: 1rem;
        color: #166534;
    }
    .summary-card-red {
        background-color: #FEF2F2;
        border: 1px solid #FECACA;
        border-radius: 8px;
        padding: 1rem;
        color: #991B1B;
    }
    .summary-card-amber {
        background-color: #FFFBEB;
        border: 1px solid #FDE68A;
        border-radius: 8px;
        padding: 1rem;
        color: #92400E;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Master Constants & Default Files
# ---------------------------------------------------------
DATA_FILE_DEFAULT = "expenses.csv"
STOCKS_FILE_DEFAULT = "stocks_rogee.csv"
PROJECTIONS_FILE_DEFAULT = "projections_rogee.csv"

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

# ---------------------------------------------------------
# Live Exchange Rate Fetcher
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_live_exchange_rates():
    default_rates = {"PHP": 157.0, "USD": 2.65, "EUR": 2.45, "GBP": 2.10, "CAD": 3.65, "AED": 9.73, "SAR": 9.94}
    try:
        url = "https://open.er-api.com/v6/latest/BHD"
        res = requests.get(url, timeout=4)
        if res.status_code == 200:
            data = res.json()
            rates = data.get("rates", {})
            return {
                "PHP": float(rates.get("PHP", 157.0)),
                "USD": float(rates.get("USD", 2.65)),
                "EUR": float(rates.get("EUR", 2.45)),
                "GBP": float(rates.get("GBP", 2.10)),
                "CAD": float(rates.get("CAD", 3.65)),
                "AED": float(rates.get("AED", 9.73)),
                "SAR": float(rates.get("SAR", 9.94))
            }, True
    except Exception:
        pass
    return default_rates, False

rates_dict, is_live = fetch_live_exchange_rates()
bhd_to_php = rates_dict.get("PHP", 157.0)
bhd_to_usd = rates_dict.get("USD", 2.65)

# ---------------------------------------------------------
# User Profile & Data Handler Functions
# ---------------------------------------------------------
def get_user_data_files(username):
    clean_user = username.lower().replace(" ", "_")
    data_file = f"expenses_{clean_user}.csv"
    stocks_file = f"stocks_{clean_user}.csv"
    proj_file = f"projections_{clean_user}.csv"
    
    if not os.path.exists(data_file) and os.path.exists(DATA_FILE_DEFAULT):
        try:
            df = pd.read_csv(DATA_FILE_DEFAULT)
            df.to_csv(data_file, index=False)
        except Exception:
            pass
            
    return data_file, stocks_file, proj_file

def load_data(data_file):
    if os.path.exists(data_file):
        try:
            df = pd.read_csv(data_file)
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date']).dt.date
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
    if os.path.exists(stocks_file):
        try:
            df = pd.read_csv(stocks_file)
            return df
        except Exception:
            pass
    return pd.DataFrame([
        {"Ticker": "SM", "Name": "SM Investments Corp", "Shares": 500, "Avg Price (PHP/USD)": 850.0, "Currency": "PHP", "Market Price (PHP/USD)": 910.0},
        {"Ticker": "BDO", "Name": "BDO Unibank Inc", "Shares": 1200, "Avg Price (PHP/USD)": 130.0, "Currency": "PHP", "Market Price (PHP/USD)": 145.0},
        {"Ticker": "MT5_CAP", "Name": "MT5 Forex Trading Capital", "Shares": 1, "Avg Price (PHP/USD)": 2500.0, "Currency": "USD", "Market Price (PHP/USD)": 2850.0}
    ])

def save_stocks(df, stocks_file):
    df.to_csv(stocks_file, index=False)

def load_projections(proj_file, default_income=1200.0, needs_pct=50, wants_pct=30, savings_pct=20):
    if os.path.exists(proj_file):
        try:
            df = pd.read_csv(proj_file)
            if not df.empty and "Month" in df.columns:
                return df
        except Exception:
            pass
    
    # Generate 12-month projection defaults
    rows = []
    cum_savings = 0.0
    for m in range(1, 13):
        income = default_income
        needs = income * (needs_pct / 100.0)
        wants = income * (wants_pct / 100.0)
        savings = income * (savings_pct / 100.0)
        total_exp = needs + wants
        surplus = income - total_exp
        cum_savings += savings
        rows.append({
            "Month": f"Month {m}",
            "Projected Income (BD)": round(income, 2),
            "Needs & Debts (BD)": round(needs, 2),
            "Wants (BD)": round(wants, 2),
            "Savings Target (BD)": round(savings, 2),
            "Total Projected Expenses (BD)": round(total_exp, 2),
            "Net Surplus (BD)": round(surplus, 2),
            "Cumulative Savings (BD)": round(cum_savings, 2)
        })
    return pd.DataFrame(rows)

def save_projections(df, proj_file):
    df.to_csv(proj_file, index=False)

def recalculate_ledger(df, rate_php, rate_usd):
    if df.empty:
        return pd.DataFrame(columns=MASTER_COLS)
    
    df = df.copy()
    
    if "Billed Amount" not in df.columns and "Amount" in df.columns:
        df["Billed Amount"] = df["Amount"]
    if "Actual Paid" not in df.columns:
        df["Actual Paid"] = df["Billed Amount"]
    if "Currency" not in df.columns:
        df["Currency"] = "BHD"
        
    df["Billed Amount"] = pd.to_numeric(df["Billed Amount"], errors='coerce').fillna(0.0)
    df["Actual Paid"] = pd.to_numeric(df["Actual Paid"], errors='coerce').fillna(0.0)
    
    pending_list = []
    pct_paid_list = []
    pct_rem_list = []
    equiv_list = []
    status_list = []
    
    for idx, row in df.iterrows():
        billed = float(row["Billed Amount"])
        paid = float(row["Actual Paid"])
        curr = str(row["Currency"]).strip().upper() if pd.notnull(row["Currency"]) else "BHD"
        
        pending = max(0.0, billed - paid)
        pct_paid = (paid / billed * 100.0) if billed > 0 else (100.0 if paid >= billed else 0.0)
        pct_paid = min(100.0, max(0.0, pct_paid))
        pct_rem = 100.0 - pct_paid
        
        if pct_paid >= 99.9:
            st_val = "Paid"
        elif pct_paid > 0.1:
            st_val = "Partially Paid"
        else:
            st_val = "Not Paid"
            
        if curr == "BHD":
            php_val = billed * rate_php
            usd_val = billed * rate_usd
            equiv_str = f"₱ {php_val:,.2f} | $ {usd_val:,.2f}"
        elif curr == "PHP":
            bhd_val = billed / rate_php if rate_php > 0 else 0
            usd_val = bhd_val * rate_usd
            equiv_str = f"BD {bhd_val:,.2f} | $ {usd_val:,.2f}"
        elif curr == "USD":
            bhd_val = billed / rate_usd if rate_usd > 0 else 0
            php_val = bhd_val * rate_php
            equiv_str = f"BD {bhd_val:,.2f} | ₱ {php_val:,.2f}"
        else:
            equiv_str = "-"
            
        pending_list.append(round(pending, 2))
        pct_paid_list.append(round(pct_paid, 1))
        pct_rem_list.append(round(pct_rem, 1))
        equiv_list.append(equiv_str)
        status_list.append(st_val)
        
    df["Pending Due"] = pending_list
    df["% Paid"] = pct_paid_list
    df["% Remaining"] = pct_rem_list
    df["Equivalent"] = equiv_list
    df["Status"] = status_list
    df["Item #"] = range(1, len(df) + 1)
    
    df = df.reindex(columns=MASTER_COLS)
    return df

# ---------------------------------------------------------
# Security Passcode Login Portal
# ---------------------------------------------------------
USER_PASSCODES = {
    "Rogee": os.environ.get("ROGEE_KEY", "rogee2026"),
    "User 2": os.environ.get("USER2_KEY", "user2026"),
    "User 3": os.environ.get("USER3_KEY", "user2026"),
    "User 4": os.environ.get("USER4_KEY", "user2026")
}

if "authenticated_user" not in st.session_state:
    st.session_state["authenticated_user"] = None

if st.session_state["authenticated_user"] is None:
    st.markdown('<div style="text-align:center; padding: 2.5rem 1rem;"><h1 style="color:#1E3A8A;">🔒 Rogee Financial Portal</h1><p style="color:#4B5563; font-size:1.1rem;">Select your profile and enter your private passkey to access your financial command center.</p></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
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
            st.info("**Rogee**: `rogee2026` | **User 2/3/4**: `user2026`\n*Customizable via Streamlit Cloud Secrets.*")
    st.stop()

# Load Active User Data
active_user = st.session_state["authenticated_user"]
user_data_file, user_stocks_file, user_proj_file = get_user_data_files(active_user)

df_expenses = load_data(user_data_file)
df_expenses = recalculate_ledger(df_expenses, bhd_to_php, bhd_to_usd)
df_stocks = load_stocks(user_stocks_file)

# ---------------------------------------------------------
# Sidebar: Settings & Multi-Stream Income
# ---------------------------------------------------------
st.sidebar.title(f"⚙️ Settings ({active_user})")

if st.sidebar.button("🔒 Sign Out / Lock Portal", use_container_width=True):
    st.session_state["authenticated_user"] = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("💱 Live Rates")
live_badge = "🟢 Live API" if is_live else "🟠 Offline Default"
st.sidebar.caption(f"Status: {live_badge}")
st.sidebar.text(f"1 BHD = {bhd_to_php:.2f} PHP")
st.sidebar.text(f"1 BHD = $ {bhd_to_usd:.2f} USD")

st.sidebar.markdown("---")
st.sidebar.subheader("💵 Income Streams")
primary_salary = st.sidebar.number_input("Primary Salary (BD)", min_value=0.0, value=1200.0, step=50.0)
business_income = st.sidebar.number_input("Business / Freelance (BD)", min_value=0.0, value=0.0, step=50.0)
sideline_income = st.sidebar.number_input("Sidelines & Investments (BD)", min_value=0.0, value=0.0, step=50.0)

total_monthly_income_bhd = primary_salary + business_income + sideline_income
total_monthly_income_php = total_monthly_income_bhd * bhd_to_php
total_monthly_income_usd = total_monthly_income_bhd * bhd_to_usd

st.sidebar.markdown(f"""
<div style="background-color:#EFF6FF; border:1px solid #BFDBFE; border-radius:6px; padding:0.8rem; color:#1E40AF; font-weight:600; margin-top:0.5rem;">
    <div>Total Income: BD {total_monthly_income_bhd:,.2f}</div>
    <div style="font-size:0.85rem; color:#3B82F6;">₱ {total_monthly_income_php:,.2f} PHP | $ {total_monthly_income_usd:,.2f} USD</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Allocation Framework Targets (%)")
needs_pct = st.sidebar.slider("Needs & Debts Target %", 0, 100, 50)
wants_pct = st.sidebar.slider("Wants Target %", 0, 100, 30)
savings_pct = st.sidebar.slider("Savings Target %", 0, 100, 20)

total_pct = needs_pct + wants_pct + savings_pct
if total_pct != 100:
    st.sidebar.warning(f"Allocation total is {total_pct}%. It should equal 100%.")

# DYNAMIC FRAMEWORK NAME
framework_title = f"{needs_pct}/{wants_pct}/{savings_pct} Personal Finance Budgeting Framework"

# Target Calculations
needs_target_bhd = total_monthly_income_bhd * (needs_pct / 100.0)
wants_target_bhd = total_monthly_income_bhd * (wants_pct / 100.0)
savings_target_bhd = total_monthly_income_bhd * (savings_pct / 100.0)

# Load 12-Month Projections
df_projections = load_projections(user_proj_file, total_monthly_income_bhd, needs_pct, wants_pct, savings_pct)

# ---------------------------------------------------------
# Main App Header
# ---------------------------------------------------------
st.markdown('<div class="main-header">Rogee Financial Command Center</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">{framework_title}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Application Tabs
# ---------------------------------------------------------
tab_dash, tab_add, tab_history, tab_proj, tab_invest, tab_calc, tab_converter = st.tabs([
    "📊 Dashboard & Analytics",
    "➕ Record Expense / Payment",
    "📋 Transaction History",
    "🔮 12-Month Projections",
    "📈 MT5 & COL Investments",
    "📐 MT5 Pip Calculator",
    "💱 Live Currency Converter"
])

# CALCULATE ACTUAL SPENDING IN BHD FROM LEDGER
actual_needs_bhd = 0.0
actual_wants_bhd = 0.0
actual_savings_bhd = 0.0

if not df_expenses.empty:
    for _, r in df_expenses.iterrows():
        cat = str(r["Main Category"])
        curr = str(r["Currency"]).strip().upper() if pd.notnull(r["Currency"]) else "BHD"
        billed = float(r["Billed Amount"]) if pd.notnull(r["Billed Amount"]) else 0.0
        
        # Convert to BHD
        if curr == "PHP":
            amt_bhd = billed / bhd_to_php if bhd_to_php > 0 else 0
        elif curr == "USD":
            amt_bhd = billed / bhd_to_usd if bhd_to_usd > 0 else 0
        else:
            amt_bhd = billed
            
        if "Needs" in cat or "Debt" in cat or "Priority" in cat:
            actual_needs_bhd += amt_bhd
        elif "Want" in cat:
            actual_wants_bhd += amt_bhd
        elif "Save" in cat or "Invest" in cat:
            actual_savings_bhd += amt_bhd
        else:
            actual_needs_bhd += amt_bhd

total_spent_bhd = actual_needs_bhd + actual_wants_bhd + actual_savings_bhd
net_remaining_bhd = total_monthly_income_bhd - total_spent_bhd

# ---------------------------------------------------------
# TAB 1: DASHBOARD & ANALYTICS
# ---------------------------------------------------------
with tab_dash:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Monthly Income", f"BD {total_monthly_income_bhd:,.2f}")
    m2.metric("Total Billed Expenses", f"BD {total_spent_bhd:,.2f}", delta=f"-BD {total_spent_bhd:,.2f}", delta_color="inverse")
    
    if net_remaining_bhd >= 0:
        m3.metric("Net Surplus Balance", f"BD {net_remaining_bhd:,.2f}", delta=f"BD {net_remaining_bhd:,.2f}")
    else:
        m3.metric("Over Budget Deficit", f"BD {net_remaining_bhd:,.2f}", delta=f"BD {net_remaining_bhd:,.2f}", delta_color="inverse")
        
    savings_rate = (actual_savings_bhd / total_monthly_income_bhd * 100.0) if total_monthly_income_bhd > 0 else 0.0
    m4.metric("Savings & Debt Rate", f"{savings_rate:.1f}%", delta=f"{savings_rate - savings_pct:.1f}% vs Target")

    st.markdown("---")
    st.subheader(f"🎯 {framework_title} Benchmark Allocation Breakdown")

    cat_data = [
        {"Category": f"Needs & Debts ({needs_pct}%)", "Target Allocation": f"{needs_pct}%", "Target (BD)": needs_target_bhd, "Actual Spent (BD)": actual_needs_bhd, "Difference (BD)": needs_target_bhd - actual_needs_bhd, "Status": "On Track" if actual_needs_bhd <= needs_target_bhd else "Over Target"},
        {"Category": f"Wants ({wants_pct}%)", "Target Allocation": f"{wants_pct}%", "Target (BD)": wants_target_bhd, "Actual Spent (BD)": actual_wants_bhd, "Difference (BD)": wants_target_bhd - actual_wants_bhd, "Status": "On Track" if actual_wants_bhd <= wants_target_bhd else "Over Target"},
        {"Category": f"Savings ({savings_pct}%)", "Target Allocation": f"{savings_pct}%", "Target (BD)": savings_target_bhd, "Actual Spent (BD)": actual_savings_bhd, "Difference (BD)": actual_savings_bhd - savings_target_bhd, "Status": "Target Met" if actual_savings_bhd >= savings_target_bhd else "Under Goal"}
    ]
    df_cat_summary = pd.DataFrame(cat_data)
    st.dataframe(
        df_cat_summary.style.format({
            "Target (BD)": "BD {:,.2f}",
            "Actual Spent (BD)": "BD {:,.2f}",
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
            "Category": ["Needs & Debts", "Wants", "Savings"],
            "Target": [needs_target_bhd, wants_target_bhd, savings_target_bhd],
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
                names=["Needs & Debts", "Wants", "Savings"],
                color_discrete_sequence=['#2563EB', '#F59E0B', '#10B981'],
                hole=0.45
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expenses logged yet. Add your first expense in the 'Record Expense' tab!")

# ---------------------------------------------------------
# TAB 2: RECORD EXPENSE / PAYMENT
# ---------------------------------------------------------
with tab_add:
    st.subheader("➕ Record a New Expense or Payment")

    with st.form("add_expense_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)

        with col_a:
            exp_date = st.date_input("Date", value=datetime.today())
            main_cat = st.selectbox("Category", [
                f"Needs & Debts ({needs_pct}%)",
                f"Wants ({wants_pct}%)",
                f"Savings ({savings_pct}%)",
                "100% Priority / Direct Bills",
                "Debts & Credits Payoff"
            ])
            
            if "Needs" in main_cat or "Debt" in main_cat or "Priority" in main_cat:
                sub_cats = ["Housing / Rent / Mortgage", "Utilities & Bills", "Groceries", "Transportation / Fuel", "Healthcare / Insurance", "Personal Loan", "Settle Debt"]
            elif "Want" in main_cat:
                sub_cats = ["Dining Out & Coffee", "Entertainment & Streaming", "Shopping & Apparel", "Hobbies & Travel", "Subscriptions", "Miscellaneous"]
            else:
                sub_cats = ["Emergency Fund", "Retirement / 401(k) / IRA", "Stock Investments", "Extra Debt Payoff", "Major Goal Savings"]

            sub_cat = st.selectbox("Sub-Category", sub_cats)

        with col_b:
            merchant = st.text_input("Merchant / Description / Bill Name", placeholder="e.g., EWA, Coop Loan, Flat Rent")
            exp_curr = st.selectbox("Transaction Currency", ["BHD", "PHP", "USD"], index=0)
            billed_amt = st.number_input(f"Billed / Planned Amount ({exp_curr})", min_value=0.01, step=5.0, value=50.0)
            actual_paid = st.number_input(f"Actual Paid Amount ({exp_curr})", min_value=0.0, step=5.0, value=50.0)
            payment_method = st.selectbox("Payment Method", ["Bank Transfer", "Credit Card", "Debit Card", "Cash"])

        submit_btn = st.form_submit_button("💾 Save Transaction")

        if submit_btn:
            new_row = pd.DataFrame([{
                "Item #": len(df_expenses) + 1,
                "Date": exp_date,
                "Main Category": main_cat,
                "Sub Category": sub_cat,
                "Merchant/Description": merchant if merchant else "Unspecified",
                "Billed Amount": billed_amt,
                "Actual Paid": actual_paid,
                "Currency": exp_curr,
                "Pending Due": max(0.0, billed_amt - actual_paid),
                "% Paid": (actual_paid / billed_amt * 100.0) if billed_amt > 0 else 0.0,
                "% Remaining": 100.0 - ((actual_paid / billed_amt * 100.0) if billed_amt > 0 else 0.0),
                "Equivalent": "-",
                "Status": "Paid" if actual_paid >= billed_amt else ("Partially Paid" if actual_paid > 0 else "Not Paid"),
                "Payment Method": payment_method
            }])
            df_expenses = pd.concat([df_expenses, new_row], ignore_index=True)
            df_expenses = recalculate_ledger(df_expenses, bhd_to_php, bhd_to_usd)
            save_data(df_expenses, user_data_file)
            st.success(f"Successfully recorded '{merchant if merchant else sub_cat}' ({exp_curr} {billed_amt:,.2f})!")
            st.rerun()

# ---------------------------------------------------------
# TAB 3: TRANSACTION HISTORY & EDITABLE LEDGER
# ---------------------------------------------------------
with tab_history:
    st.subheader("📋 Recorded Expense History & Payment Ledger")

    if not df_expenses.empty:
        df_expenses = recalculate_ledger(df_expenses, bhd_to_php, bhd_to_usd)

        # ---------------------------------------------------------
        # BUDGET STATUS NOTICE BANNER (ABOVE TABLES)
        # ---------------------------------------------------------
        if net_remaining_bhd >= 0:
            rem_php = net_remaining_bhd * bhd_to_php
            rem_usd = net_remaining_bhd * bhd_to_usd
            st.markdown(f"""
            <div class="notice-banner-green">
                🟢 WITHIN BUDGET STATUS: You have available remaining income!<br>
                Net Unspent Cash Balance: BD {net_remaining_bhd:,.2f} | ₱ {rem_php:,.2f} PHP | $ {rem_usd:,.2f} USD
            </div>
            """, unsafe_allow_html=True)
        else:
            def_bhd = abs(net_remaining_bhd)
            def_php = def_bhd * bhd_to_php
            def_usd = def_bhd * bhd_to_usd
            st.markdown(f"""
            <div class="notice-banner-red">
                🚨 OVER BUDGET STATUS NOTICE: Total payments exceed your monthly income limit!<br>
                Current Overage / Limit Deficit: -BD {def_bhd:,.2f} | -₱ {def_php:,.2f} PHP | -$ {def_usd:,.2f} USD
            </div>
            """, unsafe_allow_html=True)

        st.subheader("✏️ Interactive Editable Ledger Grid")
        st.caption("You can directly double-click any cell below to edit amounts, categories, or payment statuses, then click Save Ledger Changes.")

        # Ensure MASTER_COLS order is strictly enforced
        df_expenses = df_expenses.reindex(columns=MASTER_COLS)

        edited_df = st.data_editor(
            df_expenses,
            use_container_width=True,
            hide_index=True,
            key="ledger_editor"
        )

        col_s1, col_s2 = st.columns([1, 4])
        with col_s1:
            if st.button("💾 Save Ledger Changes", type="primary"):
                recalculated = recalculate_ledger(edited_df, bhd_to_php, bhd_to_usd)
                save_data(recalculated, user_data_file)
                st.success("Ledger changes saved successfully!")
                st.rerun()

        st.markdown("---")
        st.subheader("🎨 Payment Status Color-Coded Ledger")

        def color_status_rows(row):
            st_val = str(row.get("Status", ""))
            if "Paid" == st_val:
                return ["background-color: #D1FAE5; color: #065F46;"] * len(row)
            elif "Partially" in st_val:
                return ["background-color: #FEF3C7; color: #92400E;"] * len(row)
            else:
                return ["background-color: #FEE2E2; color: #991B1B;"] * len(row)

        st.dataframe(
            df_expenses.style.apply(color_status_rows, axis=1),
            use_container_width=True,
            hide_index=True
        )

        # ---------------------------------------------------------
        # TOTAL OUTSTANDING & PAYMENT LEDGER SUMMARY (BELOW TABLES)
        # ---------------------------------------------------------
        st.markdown("---")
        st.subheader("💰 Total Outstanding & Payment Ledger Summary")

        bhd_rows = df_expenses[df_expenses["Currency"] == "BHD"]
        php_rows = df_expenses[df_expenses["Currency"] == "PHP"]
        usd_rows = df_expenses[df_expenses["Currency"] == "USD"]

        bhd_billed = bhd_rows["Billed Amount"].sum()
        bhd_paid = bhd_rows["Actual Paid"].sum()
        bhd_pending = bhd_rows["Pending Due"].sum()

        php_billed = php_rows["Billed Amount"].sum()
        php_paid = php_rows["Actual Paid"].sum()
        php_pending = php_rows["Pending Due"].sum()
        php_billed_in_bhd = php_billed / bhd_to_php if bhd_to_php > 0 else 0
        php_paid_in_bhd = php_paid / bhd_to_php if bhd_to_php > 0 else 0
        php_pending_in_bhd = php_pending / bhd_to_php if bhd_to_php > 0 else 0

        usd_billed = usd_rows["Billed Amount"].sum()
        usd_paid = usd_rows["Actual Paid"].sum()
        usd_pending = usd_rows["Pending Due"].sum()
        usd_billed_in_bhd = usd_billed / bhd_to_usd if bhd_to_usd > 0 else 0
        usd_paid_in_bhd = usd_paid / bhd_to_usd if bhd_to_usd > 0 else 0
        usd_pending_in_bhd = usd_pending / bhd_to_usd if bhd_to_usd > 0 else 0

        grand_billed_bhd = bhd_billed + php_billed_in_bhd + usd_billed_in_bhd
        grand_paid_bhd = bhd_paid + php_paid_in_bhd + usd_paid_in_bhd
        grand_pending_bhd = bhd_pending + php_pending_in_bhd + usd_pending_in_bhd

        c_sum1, c_sum2, c_sum3, c_sum4 = st.columns(4)

        with c_sum1:
            st.markdown(f"""
            <div class="summary-card-blue">
                <h4>🇧🇭 BHD Currency Bills</h4>
                <b>Total Billed:</b> BD {bhd_billed:,.2f}<br>
                <b>Total Paid:</b> BD {bhd_paid:,.2f}<br>
                <b>Pending Due:</b> BD {bhd_pending:,.2f}
            </div>
            """, unsafe_allow_html=True)

        with c_sum2:
            st.markdown(f"""
            <div class="summary-card-amber">
                <h4>🇵🇭 PHP Currency Bills</h4>
                <b>Total Billed:</b> ₱ {php_billed:,.2f} <small>(BD {php_billed_in_bhd:,.2f})</small><br>
                <b>Total Paid:</b> ₱ {php_paid:,.2f} <small>(BD {php_paid_in_bhd:,.2f})</small><br>
                <b>Pending Due:</b> ₱ {php_pending:,.2f} <small>(BD {php_pending_in_bhd:,.2f})</small>
            </div>
            """, unsafe_allow_html=True)

        with c_sum3:
            st.markdown(f"""
            <div class="summary-card-green">
                <h4>💵 USD Currency Bills</h4>
                <b>Total Billed:</b> $ {usd_billed:,.2f} <small>(BD {usd_billed_in_bhd:,.2f})</small><br>
                <b>Total Paid:</b> $ {usd_paid:,.2f} <small>(BD {usd_paid_in_bhd:,.2f})</small><br>
                <b>Pending Due:</b> $ {usd_pending:,.2f} <small>(BD {usd_pending_in_bhd:,.2f})</small>
            </div>
            """, unsafe_allow_html=True)

        with c_sum4:
            st.markdown(f"""
            <div class="summary-card-red">
                <h4>🌍 Combined Grand Total (In BD)</h4>
                <b>Total Billed:</b> BD {grand_billed_bhd:,.2f}<br>
                <b>Total Paid:</b> BD {grand_paid_bhd:,.2f}<br>
                <b>Pending Due:</b> BD {grand_pending_bhd:,.2f}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        col_d1, col_d2 = st.columns([2, 1])
        with col_d1:
            csv_data = df_expenses.reindex(columns=MASTER_COLS).to_csv(index=False)
            st.download_button(
                label="📥 Download Transaction Ledger (CSV)",
                data=csv_data,
                file_name=f"transaction_ledger_{active_user.lower()}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_d2:
            if st.button("🗑️ Clear All Transactions", type="primary", use_container_width=True):
                empty_df = pd.DataFrame(columns=MASTER_COLS)
                save_data(empty_df, user_data_file)
                st.success("Transactions cleared!")
                st.rerun()
    else:
        st.info("No transaction history found. Start adding expenses in the 'Record Expense' tab!")

# ---------------------------------------------------------
# TAB 4: 12-MONTH PROJECTIONS (EDITABLE & DOWNLOADABLE)
# ---------------------------------------------------------
with tab_proj:
    st.subheader("🔮 12-Month Projected Budgeting Engine & Forecast")
    st.info("💡 You can directly edit any row/cell in the table below to input your future budget forecasts and calculations, then click 'Save Projections' or download as CSV!")

    col_p1, col_p2 = st.columns([1, 3])
    with col_p1:
        if st.button("🔄 Auto-Recalculate Defaults (12 Months)", use_container_width=True):
            df_projections = load_projections(user_proj_file, total_monthly_income_bhd, needs_pct, wants_pct, savings_pct)
            save_projections(df_projections, user_proj_file)
            st.success("Reset 12-month projections to default targets!")
            st.rerun()

    edited_proj_df = st.data_editor(
        df_projections,
        use_container_width=True,
        hide_index=True,
        key="proj_editor_grid"
    )

    col_pr1, col_pr2 = st.columns([1, 2])
    with col_pr1:
        if st.button("💾 Save 12-Month Projections", type="primary", use_container_width=True):
            save_projections(edited_proj_df, user_proj_file)
            st.success("12-Month projections saved successfully!")
            st.rerun()
    with col_pr2:
        csv_proj = edited_proj_df.to_csv(index=False)
        st.download_button(
            label="📥 Download 12-Month Projection Forecast (CSV)",
            data=csv_proj,
            file_name=f"12_month_projection_{active_user.lower()}.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown("---")
    st.subheader("📈 Projection Forecast Visualizations")

    c_pj1, c_pj2 = st.columns(2)
    with c_pj1:
        fig_proj_bar = go.Figure(data=[
            go.Bar(name='Projected Income', x=edited_proj_df['Month'], y=edited_proj_df['Projected Income (BD)'], marker_color='#3B82F6'),
            go.Bar(name='Total Expenses', x=edited_proj_df['Month'], y=edited_proj_df['Total Projected Expenses (BD)'], marker_color='#EF4444')
        ])
        fig_proj_bar.update_layout(
            barmode='group',
            title="Monthly Projected Income vs. Expenses (BD)",
            yaxis_title="Amount (BD)",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_proj_bar, use_container_width=True)

    with c_pj2:
        fig_cum = px.line(
            edited_proj_df,
            x='Month',
            y='Cumulative Savings (BD)',
            title="1-Year Cumulative Savings & Wealth Accumulation (BD)",
            markers=True
        )
        fig_cum.update_traces(line_color='#10B981', line_width=3)
        fig_cum.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_cum, use_container_width=True)

# ---------------------------------------------------------
# TAB 5: MT5 & COL INVESTMENTS
# ---------------------------------------------------------
with tab_invest:
    st.subheader("📈 MT5 & COL Financial Investment Portfolio")
    st.caption("Manage your Philippine stocks (COL Financial) and Forex/Trading Capital (MT5).")

    edited_stocks_df = st.data_editor(
        df_stocks,
        use_container_width=True,
        hide_index=True,
        key="stocks_editor"
    )

    if st.button("💾 Save Portfolio Changes", type="primary"):
        save_stocks(edited_stocks_df, user_stocks_file)
        st.success("Portfolio changes saved successfully!")
        st.rerun()

    st.markdown("---")
    st.subheader("📊 Portfolio Valuation Summary")

    total_val_php = 0.0
    total_val_usd = 0.0

    if not edited_stocks_df.empty:
        for _, row in edited_stocks_df.iterrows():
            shares = float(row.get("Shares", 0))
            mkt_price = float(row.get("Market Price (PHP/USD)", 0))
            curr = str(row.get("Currency", "PHP")).upper()
            val = shares * mkt_price
            if curr == "PHP":
                total_val_php += val
            else:
                total_val_usd += val

    val_php_in_bhd = total_val_php / bhd_to_php if bhd_to_php > 0 else 0
    val_usd_in_bhd = total_val_usd / bhd_to_usd if bhd_to_usd > 0 else 0
    total_portfolio_bhd = val_php_in_bhd + val_usd_in_bhd
    total_portfolio_php = total_portfolio_bhd * bhd_to_php
    total_portfolio_usd = total_portfolio_bhd * bhd_to_usd

    ci1, ci2, ci3 = st.columns(3)
    ci1.metric("COL Financial (PH Stocks)", f"₱ {total_val_php:,.2f}", delta=f"BD {val_php_in_bhd:,.2f}")
    ci2.metric("MT5 Capital (Forex/USD)", f"$ {total_val_usd:,.2f}", delta=f"BD {val_usd_in_bhd:,.2f}")
    ci3.metric("Total Portfolio Valuation", f"BD {total_portfolio_bhd:,.2f}", delta=f"₱ {total_portfolio_php:,.2f} | $ {total_portfolio_usd:,.2f}")

# ---------------------------------------------------------
# TAB 6: MT5 PIP CALCULATOR
# ---------------------------------------------------------
with tab_calc:
    st.subheader("📐 MT5 Pip Value & Risk Calculator")

    col_k1, col_k2 = st.columns(2)
    with col_k1:
        pair = st.selectbox("Select Symbol / Currency Pair", [
            "USDPHP", "BHDPHP", "USDCAD", "EURUSD", "GBPUSD", "USDJPY", "XAUUSD (Gold)", "USDCHF", "AUDUSD", "NZDUSD"
        ])
        lot_size = st.number_input("Lot Size (Standard Lots)", min_value=0.01, step=0.01, value=0.10)
        leverage = st.selectbox("Account Leverage", [50, 100, 200, 400, 500, 1000], index=4)

    with col_k2:
        entry_price = st.number_input("Entry Price", min_value=0.0001, step=0.01, value=1.0850 if "EUR" in pair else 100.0)
        exit_price = st.number_input("Exit Price / Target Price", min_value=0.0001, step=0.01, value=1.0900 if "EUR" in pair else 100.5)

    pips = abs(exit_price - entry_price) * (100 if "JPY" in pair or "XAU" in pair else 10000)
    contract_size = 100 if "XAU" in pair else 100000
    pip_val_usd = lot_size * contract_size * (0.01 if "JPY" in pair or "XAU" in pair else 0.0001)
    pip_val_bhd = pip_val_usd / bhd_to_usd if bhd_to_usd > 0 else 0
    margin_req_usd = (lot_size * contract_size * entry_price) / leverage
    margin_req_bhd = margin_req_usd / bhd_to_usd if bhd_to_usd > 0 else 0
    pnl_usd = (exit_price - entry_price) * lot_size * contract_size if exit_price >= entry_price else -abs(entry_price - exit_price) * lot_size * contract_size
    pnl_bhd = pnl_usd / bhd_to_usd if bhd_to_usd > 0 else 0

    st.markdown("---")
    cp1, cp2, cp3, cp4 = st.columns(4)
    cp1.metric("Pip Value ($ / BD)", f"$ {pip_val_usd:.2f}", delta=f"BD {pip_val_bhd:.2f}")
    cp2.metric("Required Margin", f"$ {margin_req_usd:,.2f}", delta=f"BD {margin_req_bhd:,.2f}")
    cp3.metric("Total Pips", f"{pips:,.1f} pips")
    cp4.metric("Position Profit/Loss", f"$ {pnl_usd:,.2f}", delta=f"BD {pnl_bhd:,.2f}")

# ---------------------------------------------------------
# TAB 7: LIVE CURRENCY CONVERTER
# ---------------------------------------------------------
with tab_converter:
    st.subheader("💱 Live On-The-Spot Currency Converter")

    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1:
        from_curr = st.selectbox("From Currency", ["BHD", "PHP", "USD", "EUR", "GBP", "CAD", "AED", "SAR"], index=0)
    with col_v2:
        to_curr = st.selectbox("To Currency", ["PHP", "BHD", "USD", "EUR", "GBP", "CAD", "AED", "SAR"], index=0)
    with col_v3:
        input_amount = st.number_input("Amount to Convert", min_value=0.01, step=10.0, value=100.0)

    # Base conversions via BHD
    from_rate_bhd = 1.0 if from_curr == "BHD" else rates_dict.get(from_curr, 1.0)
    to_rate_bhd = 1.0 if to_curr == "BHD" else rates_dict.get(to_curr, 1.0)

    if from_curr == "BHD":
        converted_result = input_amount * to_rate_bhd
    else:
        in_bhd = input_amount / from_rate_bhd if from_rate_bhd > 0 else 0
        converted_result = in_bhd * to_rate_bhd

    st.markdown(f"""
    <div class="summary-card-blue" style="text-align:center; margin-top:1rem;">
        <h3>{input_amount:,.2f} {from_curr} = <span style="color:#10B981;">{converted_result:,.2f} {to_curr}</span></h3>
        <small>Rates status: {live_badge}</small>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📊 Common BHD Conversion Table")
    quick_tbl = pd.DataFrame([
        {"BHD Amount": f"BD {amt}", "PHP Equivalent": f"₱ {amt * bhd_to_php:,.2f}", "USD Equivalent": f"$ {amt * bhd_to_usd:,.2f}"}
        for amt in [10, 50, 100, 200, 500, 1000]
    ])
    st.dataframe(quick_tbl, use_container_width=True, hide_index=True)
