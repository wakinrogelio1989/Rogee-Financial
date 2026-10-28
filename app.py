import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import os
import json

# Page Config
st.set_page_config(
    page_title="Rogee Financial Command Center",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with Dark Mode Contrast
st.markdown("""
<style>
    .main-header { font-size: 1.8rem; font-weight: 800; color: #1E3A8A; margin-bottom: 0.1rem; line-height: 1.2; }
    @media (prefers-color-scheme: dark) { .main-header { color: #60A5FA !important; } }
    .sub-header { font-size: 0.95rem; color: #4B5563; margin-bottom: 0.8rem; }
    @media (prefers-color-scheme: dark) { .sub-header { color: #9CA3AF !important; } }
    
    .time-badge { background-color: #F3F4F6; border: 1px solid #E5E7EB; color: #1F2937 !important; padding: 6px 12px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; margin-bottom: 12px; display: inline-block; width: 100%; text-align: center; }
    @media (prefers-color-scheme: dark) {
        .time-badge { background-color: #1F2937 !important; border-color: #374151 !important; color: #F3F4F6 !important; }
    }

    .overbudget-banner { background-color: #FEF2F2; border: 1px solid #FECACA; border-left: 5px solid #EF4444; padding: 12px 16px; border-radius: 6px; margin-bottom: 14px; color: #991B1B !important; font-weight: 600; }
    @media (prefers-color-scheme: dark) {
        .overbudget-banner { background-color: #450A0A !important; border-color: #7F1D1D !important; color: #FECACA !important; }
    }

    .surplus-banner { background-color: #F0FDF4; border: 1px solid #BBF7D0; border-left: 5px solid #22C55E; padding: 12px 16px; border-radius: 6px; margin-bottom: 14px; color: #166534 !important; font-weight: 600; }
    @media (prefers-color-scheme: dark) {
        .surplus-banner { background-color: #052E16 !important; border-color: #14532D !important; color: #BBF7D0 !important; }
    }

    .rate-card { background-color: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #3B82F6; padding: 8px 12px; border-radius: 6px; margin-bottom: 12px; font-size: 0.85rem; color: #1E40AF !important; }
    @media (prefers-color-scheme: dark) {
        .rate-card { background-color: #1E3A8A !important; border-color: #1D4ED8 !important; color: #BFDBFE !important; }
    }

    .stMetric { background-color: #F9FAFB !important; padding: 8px 12px; border-radius: 6px; border: 1px solid #E5E7EB !important; }
    div[data-testid="stMetricValue"] { font-size: 1.15rem !important; font-weight: 800 !important; color: #1E3A8A !important; }
    div[data-testid="stMetricLabel"] { color: #374151 !important; font-weight: 600 !important; }

    @media (prefers-color-scheme: dark) {
        .stMetric { background-color: #1F2937 !important; border: 1px solid #374151 !important; }
        div[data-testid="stMetricValue"] { color: #60A5FA !important; }
        div[data-testid="stMetricLabel"] { color: #D1D5DB !important; }
    }
</style>
""", unsafe_allow_html=True)

USER_PROFILES = {
    "Rogee": {
        "sec_key": "ROGEE_KEY",
        "def_key": "1989",
        "data_file": "expenses_rogee.csv",
        "config_file": "config_rogee.json",
        "invest_file": "investments_rogee.csv"
    },
    "Ferdie": {
        "sec_key": "USER2_KEY",
        "def_key": "Ce_0121119",
        "data_file": "expenses_user2.csv",
        "config_file": "config_user2.json",
        "invest_file": "investments_user2.csv"
    },
    "User 3": {
        "sec_key": "USER3_KEY",
        "def_key": "user3026",
        "data_file": "expenses_user3.csv",
        "config_file": "config_user3.json",
        "invest_file": "investments_user3.csv"
    },
    "User 4": {
        "sec_key": "USER4_KEY",
        "def_key": "user42026",
        "data_file": "expenses_user4.csv",
        "config_file": "config_user4.json",
        "invest_file": "investments_user4.csv"
    }
}

if "authenticated_user" not in st.session_state:
    st.session_state["authenticated_user"] = None

# Authentication Screen
if not st.session_state["authenticated_user"]:
    st.markdown('<div class="main-header">🔐 Rogee Financial Command Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Select your user profile and enter your secret passcode to access your personal ledger.</div>', unsafe_allow_html=True)
    
    col_l1, col_l2 = st.columns([1, 1])
    with col_l1:
        selected_user = st.selectbox("Select User Profile", list(USER_PROFILES.keys()))
        input_passkey = st.text_input("Enter Passcode", type="password")
        login_btn = st.button("Unlock Dashboard", type="primary", use_container_width=True)
        
        prof_info = USER_PROFILES[selected_user]
        correct_key = st.secrets.get(prof_info["sec_key"], prof_info["def_key"]) if hasattr(st, "secrets") else prof_info["def_key"]
        
        if login_btn:
            if input_passkey == correct_key:
                st.session_state["authenticated_user"] = selected_user
                st.success(f"Welcome, {selected_user}!")
                st.rerun()
            else:
                st.error("Incorrect passcode. Please try again.")
    with col_l2:
        st.info("💡 Default Passcodes:\n- Rogee: rogee2026\n- User 2: user2026\n- User 3: user3026\n- User 4: user42026\n\nConfigure custom keys in Streamlit Secrets!")
    st.stop()

current_user = st.session_state["authenticated_user"]
user_cfg = USER_PROFILES[current_user]

DATA_FILE = user_cfg["data_file"]
CONFIG_FILE = user_cfg["config_file"]
INVEST_FILE = user_cfg["invest_file"]

def load_user_config():
    defaults = {
        "currency_symbol": "BD",
        "salary_bhd": 1500.0,
        "business_bhd": 0.0,
        "sidelines_bhd": 0.0,
        "other_income_bhd": 0.0,
        "bhd_to_php": 158.50,
        "bhd_to_usd": 2.6525,
        "debts_pct": 15,
        "needs_pct": 45,
        "wants_pct": 20,
        "savings_pct": 20
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                defaults.update(data)
        except Exception:
            pass
    return defaults

def save_user_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=4)

cfg = load_user_config()

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            if "Amount" in df.columns and "Billed Amount" not in df.columns:
                df["Billed Amount"] = df["Amount"]
            if "Actual Paid" not in df.columns:
                df["Actual Paid"] = df["Billed Amount"] if "Billed Amount" in df.columns else 0.0
            if "Currency" not in df.columns:
                df["Currency"] = "BHD"
            if "Status" not in df.columns:
                df["Status"] = "Paid"
            if "Payment Method" not in df.columns:
                df["Payment Method"] = "Benefit Pay"
            
            df["Billed Amount"] = pd.to_numeric(df["Billed Amount"], errors="coerce").fillna(0.0)
            df["Actual Paid"] = pd.to_numeric(df["Actual Paid"], errors="coerce").fillna(0.0)
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=[
        "Date", "Main Category", "Sub Category", "Merchant/Description", 
        "Billed Amount", "Actual Paid", "Currency", "Status", "Payment Method"
    ])

def save_data(df, path):
    df.to_csv(path, index=False)

df_expenses = load_data()

# Sidebar Setup
st.sidebar.title(f"👤 {current_user}'s Settings")
if st.sidebar.button("🚪 Log Out", use_container_width=True):
    st.session_state["authenticated_user"] = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("💱 Currency & Live Exchange Rates")
curr_symbol = st.sidebar.selectbox("Base Currency Symbol", ["BD", "₱", "$", "€", "£"], index=0)
bhd_to_php = st.sidebar.number_input("Exchange Rate: 1 BHD to PHP (₱)", min_value=1.0, value=float(cfg.get("bhd_to_php", 158.50)), step=0.5)
bhd_to_usd = st.sidebar.number_input("Exchange Rate: 1 BHD to USD ($)", min_value=0.1, value=float(cfg.get("bhd_to_usd", 2.6525)), step=0.01)

st.sidebar.markdown("---")
st.sidebar.subheader("💵 Monthly Take-Home Income")
salary_bhd = st.sidebar.number_input(f"Primary Salary ({curr_symbol})", min_value=0.0, value=float(cfg.get("salary_bhd", 1500.0)), step=50.0)
business_bhd = st.sidebar.number_input(f"Business Income ({curr_symbol})", min_value=0.0, value=float(cfg.get("business_bhd", 0.0)), step=50.0)
sidelines_bhd = st.sidebar.number_input(f"Sidelines / Freelance ({curr_symbol})", min_value=0.0, value=float(cfg.get("sidelines_bhd", 0.0)), step=50.0)
other_income_bhd = st.sidebar.number_input(f"Other Income ({curr_symbol})", min_value=0.0, value=float(cfg.get("other_income_bhd", 0.0)), step=50.0)

total_income_bhd = salary_bhd + business_bhd + sidelines_bhd + other_income_bhd

st.sidebar.markdown("---")
st.sidebar.subheader("📊 4-Category Framework Allocation (%)")
debts_pct = st.sidebar.slider("Debts & Credits Target %", 0, 100, int(cfg.get("debts_pct", 15)))
needs_pct = st.sidebar.slider("Needs Target % (Essentials)", 0, 100, int(cfg.get("needs_pct", 45)))
wants_pct = st.sidebar.slider("Wants Target % (Lifestyle)", 0, 100, int(cfg.get("wants_pct", 20)))
savings_pct = st.sidebar.slider("Savings & Investments %", 0, 100, int(cfg.get("savings_pct", 20)))

tot_alloc = debts_pct + needs_pct + wants_pct + savings_pct
if tot_alloc != 100:
    st.sidebar.warning(f"⚠️ Allocation total is {tot_alloc}%. Adjust sliders to equal 100%.")

# Save config updates
new_cfg = {
    "currency_symbol": curr_symbol,
    "salary_bhd": salary_bhd,
    "business_bhd": business_bhd,
    "sidelines_bhd": sidelines_bhd,
    "other_income_bhd": other_income_bhd,
    "bhd_to_php": bhd_to_php,
    "bhd_to_usd": bhd_to_usd,
    "debts_pct": debts_pct,
    "needs_pct": needs_pct,
    "wants_pct": wants_pct,
    "savings_pct": savings_pct
}
save_user_config(new_cfg)

framework_title = f"{debts_pct}/{needs_pct}/{wants_pct}/{savings_pct} Framework"

# Currency Conversion Helper Functions
def to_bhd(amt, cur):
    amt = float(amt)
    if cur == "PHP":
        return amt / bhd_to_php if bhd_to_php > 0 else 0.0
    elif cur == "USD":
        return amt / bhd_to_usd if bhd_to_usd > 0 else 0.0
    return amt

def to_php(amt_bhd):
    return float(amt_bhd) * bhd_to_php

def to_usd(amt_bhd):
    return float(amt_bhd) * bhd_to_usd

# Calculate Paid BHD for each transaction
if not df_expenses.empty:
    df_expenses["Billed_BHD"] = df_expenses.apply(lambda r: to_bhd(r["Billed Amount"], r.get("Currency", "BHD")), axis=1)
    df_expenses["Paid_BHD"] = df_expenses.apply(lambda r: to_bhd(r["Actual Paid"], r.get("Currency", "BHD")), axis=1)
    df_expenses["Pending_BHD"] = (df_expenses["Billed_BHD"] - df_expenses["Paid_BHD"]).clip(lower=0.0)
else:
    df_expenses["Billed_BHD"] = 0.0
    df_expenses["Paid_BHD"] = 0.0
    df_expenses["Pending_BHD"] = 0.0

total_spent_bhd = float(df_expenses["Paid_BHD"].sum()) if not df_expenses.empty else 0.0
net_remaining_bhd = total_income_bhd - total_spent_bhd

# Header with Live Clocks
bh_time = datetime.now(timezone.utc) + timedelta(hours=3)
ph_time = datetime.now(timezone.utc) + timedelta(hours=8)

st.markdown('<div class="main-header">Rogee Financial Command Center</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Personal Budgeting & Wealth Tracking — <b>{framework_title}</b></div>', unsafe_allow_html=True)

st.markdown(
    f'<div class="time-badge">'
    f'🇧🇭 <b>Bahrain:</b> {bh_time.strftime("%d %b %Y, %I:%M %p")} AST &nbsp;|&nbsp; '
    f'🇵🇭 <b>Philippines:</b> {ph_time.strftime("%d %b %Y, %I:%M %p")} PST &nbsp;|&nbsp; '
    f'👤 <b>User Profile:</b> {current_user}'
    f'</div>',
    unsafe_allow_html=True
)

# Over Budget / Surplus Alert Banner
if net_remaining_bhd < 0:
    over_amt_bhd = abs(net_remaining_bhd)
    st.markdown(
        f'<div class="overbudget-banner">'
        f'🚨 <b>OVER BUDGET ALERT:</b> Total payments exceed income by '
        f'<b>BD {over_amt_bhd:,.2f}</b> (₱{to_php(over_amt_bhd):,.2f} | ${to_usd(over_amt_bhd):,.2f})!'
        f'</div>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f'<div class="surplus-banner">'
        f'✅ <b>NET CASH REMAINING:</b> You have '
        f'<b>BD {net_remaining_bhd:,.2f}</b> (₱{to_php(net_remaining_bhd):,.2f} | ${to_usd(net_remaining_bhd):,.2f}) available in unspent income.'
        f'</div>',
        unsafe_allow_html=True
    )

# Tabs
tab_dash, tab_add, tab_history, tab_invest, tab_reports, tab_guide = st.tabs([
    "📊 Dashboard & Analytics", 
    "➕ Record Expense", 
    "📜 Transaction History", 
    "📊 MT5 & COL Investments", 
    "📥 Download Reports", 
    "📘 User Guide"
])

# ----------------------------------------------------
# TAB 1: DASHBOARD
# ----------------------------------------------------
with tab_dash:
    # Target calculations
    target_debts = total_income_bhd * (debts_pct / 100.0)
    target_needs = total_income_bhd * (needs_pct / 100.0)
    target_wants = total_income_bhd * (wants_pct / 100.0)
    target_savings = total_income_bhd * (savings_pct / 100.0)

    # Actual spending calculations by main category
    def cat_spent(cat_name):
        if df_expenses.empty: return 0.0
        subset = df_expenses[df_expenses["Main Category"].str.contains(cat_name, case=False, na=False)]
        return float(subset["Paid_BHD"].sum())

    actual_priority = cat_spent("100% Priority")
    actual_debts = cat_spent("Debts")
    actual_needs = cat_spent("Needs")
    actual_wants = cat_spent("Wants")
    actual_savings = cat_spent("Savings")

    rate_mult = 1.0
    if curr_symbol == "₱": rate_mult = bhd_to_php
    elif curr_symbol == "$": rate_mult = bhd_to_usd

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Monthly Income", f"{curr_symbol}{(total_income_bhd * rate_mult):,.2f}", help=f"BD {total_income_bhd:,.2f}")
    m2.metric("Total Expenses Paid", f"{curr_symbol}{(total_spent_bhd * rate_mult):,.2f}", delta=f"-{curr_symbol}{(total_spent_bhd * rate_mult):,.2f}", delta_color="inverse")
    
    if net_remaining_bhd >= 0:
        m3.metric("Remaining Net Cash", f"{curr_symbol}{(net_remaining_bhd * rate_mult):,.2f}", delta=f"{curr_symbol}{(net_remaining_bhd * rate_mult):,.2f}")
    else:
        m3.metric("Over Budget Overage", f"-{curr_symbol}{(abs(net_remaining_bhd) * rate_mult):,.2f}", delta=f"-{curr_symbol}{(abs(net_remaining_bhd) * rate_mult):,.2f}", delta_color="inverse")

    savings_rate = (actual_savings / total_income_bhd * 100.0) if total_income_bhd > 0 else 0.0
    m4.metric("Savings & Invest Rate", f"{savings_rate:.1f}%", delta=f"{savings_rate - savings_pct:.1f}% vs Target")

    st.markdown("---")
    st.subheader(f"📊 {framework_title} Benchmark Allocation")

    cat_table_data = [
        {"Category": "100% Priority & People to Pay", "Target %": "100%", "Target (BD)": total_income_bhd, "Actual Paid (BD)": actual_priority, "Status": "Mandatory First"},
        {"Category": f"Debts & Credits ({debts_pct}%)", "Target %": f"{debts_pct}%", "Target (BD)": target_debts, "Actual Paid (BD)": actual_debts, "Status": "On Track" if actual_debts <= target_debts else "Over Target"},
        {"Category": f"Needs ({needs_pct}%)", "Target %": f"{needs_pct}%", "Target (BD)": target_needs, "Actual Paid (BD)": actual_needs, "Status": "On Track" if actual_needs <= target_needs else "Over Target"},
        {"Category": f"Wants ({wants_pct}%)", "Target %": f"{wants_pct}%", "Target (BD)": target_wants, "Actual Paid (BD)": actual_wants, "Status": "On Track" if actual_wants <= target_wants else "Over Target"},
        {"Category": f"Savings & Investments ({savings_pct}%)", "Target %": f"{savings_pct}%", "Target (BD)": target_savings, "Actual Paid (BD)": actual_savings, "Status": "Target Met" if actual_savings >= target_savings else "Under Goal"}
    ]
    df_cat_summary = pd.DataFrame(cat_table_data)
    
    st.dataframe(
        df_cat_summary.style.format({
            "Target (BD)": lambda x: f"BD {x:,.2f} (₱{to_php(x):,.2f})",
            "Actual Paid (BD)": lambda x: f"BD {x:,.2f} (₱{to_php(x):,.2f})"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    c_ch1, c_ch2 = st.columns(2)
    with c_ch1:
        st.subheader("Target vs. Actual Spending (BD)")
        fig_bar = go.Figure(data=[
            go.Bar(name='Target', x=["Debts", "Needs", "Wants", "Savings"], y=[target_debts, target_needs, target_wants, target_savings], marker_color='#93C5FD'),
            go.Bar(name='Actual Paid', x=["Debts", "Needs", "Wants", "Savings"], y=[actual_debts, actual_needs, actual_wants, actual_savings], marker_color='#1D4ED8')
        ])
        fig_bar.update_layout(barmode='group', yaxis_title="Amount (BHD)", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    with c_ch2:
        st.subheader("Expense Distribution Share")
        if total_spent_bhd > 0:
            fig_pie = px.pie(
                values=[actual_priority, actual_debts, actual_needs, actual_wants, actual_savings],
                names=["100% Priority", "Debts & Credits", "Needs", "Wants", "Savings & Investments"],
                color_discrete_sequence=['#EF4444', '#F59E0B', '#2563EB', '#8B5CF6', '#10B981'],
                hole=0.4
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expenses recorded yet.")

# ----------------------------------------------------
# TAB 2: RECORD EXPENSE (Instant Dynamic Dropdowns)
# ----------------------------------------------------
with tab_add:
    st.subheader("➕ Record a New Payment or Expense")
    
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        exp_date = st.date_input("Date", value=datetime.today())
        main_cat_options = [
            "100% Priority & People to Pay",
            f"Debts & Credits ({debts_pct}%)",
            f"Needs ({needs_pct}%)",
            f"Wants ({wants_pct}%)",
            f"Savings & Investments ({savings_pct}%)"
        ]
        main_cat = st.selectbox("Category", main_cat_options, key="add_main_cat")
    
    with col_sel2:
        if "Priority" in main_cat:
            sub_cats = ["Family Remittance & People to Pay", "House Rental", "Electric / Water / Utility Bills", "Urgent Loans & Debt", "Emergency Support"]
        elif "Debts" in main_cat:
            sub_cats = ["Credit Card Payment", "Bank Loan Installment", "Car Loan", "Housing Loan", "Personal Debt Payoff"]
        elif "Needs" in main_cat:
            sub_cats = ["Groceries & Food Essentials", "Transportation / Fuel", "Healthcare & Insurance", "School / Education Fees", "Work Expenses"]
        elif "Wants" in main_cat:
            sub_cats = ["Dining Out & Coffee", "Shopping & Personal Care", "Entertainment & Subscriptions", "Travel & Leisure", "Gadgets & Hobbies"]
        else:
            sub_cats = ["Emergency Fund", "COL Stock Investments", "MT5 Trading Deposit", "Index Funds / Stocks", "Pension / Savings Account"]
        
        sub_cat = st.selectbox("Sub-Category", sub_cats, key="add_sub_cat")

    with st.form("add_expense_form", clear_on_submit=True):
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            merchant = st.text_input("Merchant / Description / Payee", placeholder="e.g., Landlord, Credit Card, Supermarket")
            billed_amt = st.number_input("Billed / Planned Amount", min_value=0.01, value=100.0, step=10.0)
            pay_currency = st.selectbox("Transaction Currency", ["BHD", "PHP", "USD"], index=0)

        with fcol2:
            status_choice = st.selectbox("Payment Status", ["Paid", "Partially Paid", "Pending Payment", "Not Paid"], index=0)
            
            default_actual = billed_amt if status_choice == "Paid" else (0.0 if "Pending" in status_choice or "Not" in status_choice else billed_amt / 2.0)
            actual_paid = st.number_input("Actual Amount Paid", min_value=0.0, value=float(default_actual), step=10.0)
            pay_method = st.selectbox("Payment Method", ["Benefit Pay", "Remittance", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])

        submit_btn = st.form_submit_button("💾 Save Payment Entry", type="primary", use_container_width=True)

        if submit_btn:
            calc_status = "Paid" if actual_paid >= billed_amt else ("Not Paid" if actual_paid == 0 else "Partially Paid")
            new_row = pd.DataFrame([{
                "Date": exp_date,
                "Main Category": main_cat,
                "Sub Category": sub_cat,
                "Merchant/Description": merchant if merchant else sub_cat,
                "Billed Amount": float(billed_amt),
                "Actual Paid": float(actual_paid),
                "Currency": pay_currency,
                "Status": calc_status,
                "Payment Method": pay_method
            }])
            df_expenses = pd.concat([df_expenses, new_row], ignore_index=True)
            save_data(df_expenses, DATA_FILE)
            st.success(f"Successfully recorded transaction for '{merchant if merchant else sub_cat}'!")
            st.rerun()

# ----------------------------------------------------
# TAB 3: TRANSACTION HISTORY (Interactive & Color Styler)
# ----------------------------------------------------
with tab_history:
    st.subheader(f"📜 Recorded Transaction History ({current_user})")

    if not df_expenses.empty:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            cat_filters = st.multiselect("Filter Main Category", options=list(df_expenses["Main Category"].unique()), default=list(df_expenses["Main Category"].unique()))
        with col_f2:
            status_filters = st.multiselect("Filter Status", options=["Paid", "Partially Paid", "Pending Payment", "Not Paid"], default=["Paid", "Partially Paid", "Pending Payment", "Not Paid"])

        # Filter
        df_filtered = df_expenses.copy()
        if cat_filters:
            df_filtered = df_filtered[df_filtered["Main Category"].isin(cat_filters)]
        if status_filters:
            df_filtered = df_filtered[df_filtered["Status"].isin(status_filters)]

        # Grouping & Chronological Sorting
        cat_order = {
            "100% Priority": 1,
            "Debts": 2,
            "Needs": 3,
            "Wants": 4,
            "Savings": 5
        }
        def get_cat_rank(cat_str):
            for k, v in cat_order.items():
                if k.lower() in str(cat_str).lower():
                    return v
            return 6

        df_filtered["cat_rank"] = df_filtered["Main Category"].apply(get_cat_rank)
        df_filtered["Date_DT"] = pd.to_datetime(df_filtered["Date"])
        df_filtered = df_filtered.sort_values(by=["cat_rank", "Date_DT"], ascending=[True, True]).reset_index(drop=True)

        # Recalculate Columns
        df_filtered["Billed Amount"] = pd.to_numeric(df_filtered["Billed Amount"], errors="coerce").fillna(0.0)
        df_filtered["Actual Paid"] = pd.to_numeric(df_filtered["Actual Paid"], errors="coerce").fillna(0.0)
        
        df_filtered["Pending Due"] = (df_filtered["Billed Amount"] - df_filtered["Actual Paid"]).clip(lower=0.0)
        
        df_filtered["% Paid"] = df_filtered.apply(
            lambda r: (r["Actual Paid"] / r["Billed Amount"] * 100.0) if r["Billed Amount"] > 0 else (100.0 if r["Actual Paid"] > 0 else 0.0),
            axis=1
        )
        df_filtered["% Remaining"] = (100.0 - df_filtered["% Paid"]).clip(lower=0.0)

        # Auto-update status based on % Paid
        def auto_status(row):
            pct = row["% Paid"]
            if pct >= 100.0:
                return "Paid"
            elif pct <= 0.0:
                return "Not Paid"
            else:
                return "Partially Paid"

        df_filtered["Status"] = df_filtered.apply(auto_status, axis=1)

        # Build Equivalent String
        def make_equiv_str(row):
            amt = row["Actual Paid"]
            cur = row.get("Currency", "BHD")
            bhd_val = to_bhd(amt, cur)
            php_val = to_php(bhd_val)
            usd_val = to_usd(bhd_val)
            return f"BD {bhd_val:,.2f} | ₱{php_val:,.2f} | ${usd_val:,.2f}"

        df_filtered["Equivalent (BHD / PHP / USD)"] = df_filtered.apply(make_equiv_str, axis=1)

        # Assign Item #
        df_filtered["Item #"] = range(1, len(df_filtered) + 1)

        display_cols = [
            "Item #", "Date", "Main Category", "Sub Category", "Merchant/Description",
            "Billed Amount", "Actual Paid", "Currency", "Pending Due",
            "% Paid", "% Remaining", "Equivalent (BHD / PHP / USD)", "Status", "Payment Method"
        ]
        
        df_display = df_filtered[display_cols].copy()

        st.caption("✏️ **Double-click any cell** below to edit dates, categories, descriptions, or amounts. Select rows to delete, then click **💾 Save Changes**!")

        edited_df = st.data_editor(
            df_display,
            num_rows="dynamic",
            use_container_width=True,
            key=f"editor_{current_user}",
            disabled=["Item #", "Pending Due", "% Paid", "% Remaining", "Equivalent (BHD / PHP / USD)"]
        )

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("💾 Save Ledger Changes", type="primary", use_container_width=True):
                save_cols = ["Date", "Main Category", "Sub Category", "Merchant/Description", "Billed Amount", "Actual Paid", "Currency", "Status", "Payment Method"]
                clean_save = edited_df[save_cols].copy()
                save_data(clean_save, DATA_FILE)
                st.success("Ledger saved successfully!")
                st.rerun()

        with col_s2:
            if st.button("🗑️ Clear Entire History", use_container_width=True):
                if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
                st.success("All records cleared!")
                st.rerun()

        st.markdown("---")
        st.subheader("🎨 Status-Highlighted Ledger View")

        # Color Styler for Table View
        def style_rows(df):
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            for idx, row in df.iterrows():
                pct = row["% Paid"]
                if pct >= 100.0:
                    bg = 'background-color: #D1FAE5; color: #065F46; font-weight: 600;'  # Green
                elif pct <= 0.0:
                    bg = 'background-color: #FEE2E2; color: #991B1B; font-weight: 600;'  # Red
                else:
                    bg = 'background-color: #FEF3C7; color: #92400E; font-weight: 600;'  # Yellow
                styles.loc[idx] = bg
            return styles

        st.dataframe(
            df_display.style.apply(style_rows, axis=None).format({
                "Billed Amount": "{:,.2f}",
                "Actual Paid": "{:,.2f}",
                "Pending Due": "{:,.2f}",
                "% Paid": "{:.1f}%",
                "% Remaining": "{:.1f}%"
            }),
            use_container_width=True,
            hide_index=True
        )

        # ----------------------------------------------------
        # 💰 TOTAL OUTSTANDING & PAYMENT LEDGER SUMMARY
        # ----------------------------------------------------
        st.markdown("---")
        st.subheader("💰 Total Outstanding & Payment Ledger Summary")

        # Aggregate Overall Totals in BHD
        total_billed_bhd = float(df_filtered.apply(lambda r: to_bhd(r["Billed Amount"], r["Currency"]), axis=1).sum())
        total_paid_bhd = float(df_filtered.apply(lambda r: to_bhd(r["Actual Paid"], r["Currency"]), axis=1).sum())
        total_pending_bhd = (total_billed_bhd - total_paid_bhd) if total_billed_bhd >= total_paid_bhd else 0.0

        # Aggregate PHP Denominated / PHP Specific Totals from Transactions
        php_records = df_filtered[df_filtered["Currency"] == "PHP"]
        
        if not php_records.empty:
            php_billed_raw = float(php_records["Billed Amount"].sum())
            php_paid_raw = float(php_records["Actual Paid"].sum())
            php_pending_raw = float(php_records["Pending Due"].sum())
            
            php_billed_equiv_bhd = to_bhd(php_billed_raw, "PHP")
            php_paid_equiv_bhd = to_bhd(php_paid_raw, "PHP")
            php_pending_equiv_bhd = to_bhd(php_pending_raw, "PHP")
        else:
            # If no transactions were directly entered in PHP currency, calculate the converted PHP equivalent of all records
            php_billed_raw = to_php(total_billed_bhd)
            php_paid_raw = to_php(total_paid_bhd)
            php_pending_raw = to_php(total_pending_bhd)
            
            php_billed_equiv_bhd = total_billed_bhd
            php_paid_equiv_bhd = total_paid_bhd
            php_pending_equiv_bhd = total_pending_bhd

        # Display Summary Cards
        sc1, sc2, sc3 = st.columns(3)

        with sc1:
            st.markdown("#### 📋 Total Billed / Needed to Pay")
            st.info(
                f"**🇵🇭 Philippine Peso (PHP):**\n"
                f"- **Needed to Pay:** ₱{php_billed_raw:,.2f}\n"
                f"- **Equivalent BHD:** BD {php_billed_equiv_bhd:,.2f}\n\n"
                f"---\n"
                f"**🌍 Grand Total All Currencies:**\n"
                f"- **BD:** BD {total_billed_bhd:,.2f}\n"
                f"- **PHP:** ₱{to_php(total_billed_bhd):,.2f}\n"
                f"- **USD:** ${to_usd(total_billed_bhd):,.2f}"
            )

        with sc2:
            st.markdown("#### 🟢 Total Actual Amount Paid")
            st.success(
                f"**🇵🇭 Philippine Peso (PHP):**\n"
                f"- **Paid Amount:** ₱{php_paid_raw:,.2f}\n"
                f"- **Equivalent BHD:** BD {php_paid_equiv_bhd:,.2f}\n\n"
                f"---\n"
                f"**🌍 Grand Total All Currencies:**\n"
                f"- **BD:** BD {total_paid_bhd:,.2f}\n"
                f"- **PHP:** ₱{to_php(total_paid_bhd):,.2f}\n"
                f"- **USD:** ${to_usd(total_paid_bhd):,.2f}"
            )

        with sc3:
            st.markdown("#### 🔴 Total Remaining Pending Due")
            st.error(
                f"**🇵🇭 Philippine Peso (PHP):**\n"
                f"- **Remaining Unpaid:** ₱{php_pending_raw:,.2f}\n"
                f"- **Equivalent BHD:** BD {php_pending_equiv_bhd:,.2f}\n\n"
                f"---\n"
                f"**🌍 Grand Total All Currencies:**\n"
                f"- **BD:** BD {total_pending_bhd:,.2f}\n"
                f"- **PHP:** ₱{to_php(total_pending_bhd):,.2f}\n"
                f"- **USD:** ${to_usd(total_pending_bhd):,.2f}"
            )

    else:
        st.info("No transaction history recorded yet. Add payments in the 'Record Expense' tab!")

# ----------------------------------------------------
# TAB 4: MT5 & COL INVESTMENTS
# ----------------------------------------------------
with tab_invest:
    st.subheader("📊 MT5 Trading & COL Stock Investments Tracker")
    t_inv1, t_inv2 = st.tabs(["🧮 Forex Trading Calculators", "📈 Investment Portfolio"])

    with t_inv1:
        st.markdown("### 📍 MT5 Pip Value & Margin Calculators")
        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown("#### Pip Value Calculator")
            symbol = st.selectbox("Trading Asset / Pair", ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD (Gold)", "USDCHF", "AUDUSD"])
            lots = st.number_input("Standard Lot Volume", min_value=0.01, value=1.0, step=0.1)
            acc_curr = st.selectbox("Account Base Currency", ["USD", "BHD", "PHP"])
            
            pip_size = 0.01 if "JPY" in symbol else (0.1 if "Gold" in symbol or "XAU" in symbol else 0.0001)
            lot_units = 100 if "Gold" in symbol or "XAU" in symbol else 100000
            
            pip_val_usd = (pip_size * lot_units) * lots
            if acc_curr == "BHD":
                pip_val_disp = pip_val_usd / bhd_to_usd if bhd_to_usd > 0 else 0.0
                curr_lbl = "BD"
            elif acc_curr == "PHP":
                pip_val_disp = (pip_val_usd / bhd_to_usd) * bhd_to_php if bhd_to_usd > 0 else 0.0
                curr_lbl = "₱"
            else:
                pip_val_disp = pip_val_usd
                curr_lbl = "$"

            st.metric(f"Pip Value per {pip_size} Movement", f"{curr_lbl} {pip_val_disp:,.2f}")

        with cc2:
            st.markdown("#### Required Margin Calculator")
            asset_price = st.number_input("Current Asset Market Price ($)", min_value=0.01, value=2700.0 if "Gold" in symbol else 1.0850)
            leverage = st.selectbox("Account Leverage Ratio", [100, 200, 500, 1000], index=2)
            
            notional_usd = (lot_units * lots) * asset_price
            req_margin_usd = notional_usd / leverage
            
            st.metric("Required Margin (USD)", f"${req_margin_usd:,.2f}")
            st.caption(f"Equivalent in BHD: BD {(req_margin_usd/bhd_to_usd):,.2f} | PHP: ₱{((req_margin_usd/bhd_to_usd)*bhd_to_php):,.2f}")

    with t_inv2:
        st.markdown("### 📈 COL Stocks & Investment Portfolio")
        def load_investments():
            if os.path.exists(INVEST_FILE):
                try: return pd.read_csv(INVEST_FILE)
                except Exception: pass
            return pd.DataFrame(columns=["Asset Name", "Platform", "Units / Shares", "Buy Price", "Current Price", "Total Invested", "Current Value", "Profit / Loss"])

        df_invest = load_investments()

        with st.form("add_invest_form", clear_on_submit=True):
            ic1, ic2 = st.columns(2)
            with ic1:
                asset_name = st.text_input("Asset Name", placeholder="e.g., COL Financial Stock, Gold, MT5 Balance")
                platform = st.selectbox("Platform", ["COL Financial", "MT5 Broker", "Binance / Crypto", "Local Bank Index", "Other"])
                units = st.number_input("Units / Shares Owned", min_value=0.01, value=100.0)
            with ic2:
                buy_price = st.number_input("Average Buy Price ($ / ₱)", min_value=0.01, value=10.0)
                curr_price = st.number_input("Current Market Price ($ / ₱)", min_value=0.01, value=12.0)
            
            sub_inv = st.form_submit_button("➕ Add Investment Asset")
            if sub_inv and asset_name:
                tot_inv = units * buy_price
                curr_val = units * curr_price
                pnl = curr_val - tot_inv
                
                new_inv = pd.DataFrame([{
                    "Asset Name": asset_name,
                    "Platform": platform,
                    "Units / Shares": units,
                    "Buy Price": buy_price,
                    "Current Price": curr_price,
                    "Total Invested": tot_inv,
                    "Current Value": curr_val,
                    "Profit / Loss": pnl
                }])
                df_invest = pd.concat([df_invest, new_inv], ignore_index=True)
                df_invest.to_csv(INVEST_FILE, index=False)
                st.success(f"Added '{asset_name}' to portfolio!")
                st.rerun()

        if not df_invest.empty:
            st.dataframe(df_invest.style.format({
                "Buy Price": "${:,.2f}",
                "Current Price": "${:,.2f}",
                "Total Invested": "${:,.2f}",
                "Current Value": "${:,.2f}",
                "Profit / Loss": "${:,.2f}"
            }), use_container_width=True, hide_index=True)

            tot_pnl = float(df_invest["Profit / Loss"].sum())
            st.metric("Total Portfolio Un-realized P&L", f"${tot_pnl:,.2f}", delta=f"${tot_pnl:,.2f}")

            if st.button("Clear Investment Ledger"):
                if os.path.exists(INVEST_FILE): os.remove(INVEST_FILE)
                st.rerun()

# ----------------------------------------------------
# TAB 5: DOWNLOAD REPORTS
# ----------------------------------------------------
with tab_reports:
    st.subheader("📥 Download Financial Reports & Data")
    col_r1, col_r2 = st.columns(2)
    
    with col_r1:
        st.markdown("#### 📊 CSV Transaction Ledger")
        if not df_expenses.empty:
            csv_data = df_expenses.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download CSV Ledger",
                data=csv_data,
                file_name=f"financial_ledger_{current_user.lower().replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No transaction records available to export.")

    with col_r2:
        st.markdown("#### 📜 Executive Financial Summary Report")
        rep_date = datetime.today().strftime("%Y-%m-%d")
        total_exp_bhd = float(df_expenses["Paid_BHD"].sum()) if not df_expenses.empty and "Paid_BHD" in df_expenses.columns else 0.0
        
        rep_text = f"""==================================================
ROGEE FINANCIAL COMMAND CENTER - EXECUTIVE REPORT
==================================================
User Profile   : {current_user}
Report Date    : {rep_date}
Bahrain Time   : {bh_time.strftime("%Y-%m-%d %I:%M %p")}
Philippine Time: {ph_time.strftime("%Y-%m-%d %I:%M %p")}
Exchange Rate  : 1 BHD = {bhd_to_php:,.2f} PHP = ${bhd_to_usd:,.2f} USD
Framework      : {framework_title}

--------------------------------------------------
1. INCOME & CASH BALANCE SUMMARY
--------------------------------------------------
- Primary Salary         : BD {salary_bhd:,.2f}
- Business Income        : BD {business_bhd:,.2f}
- Sidelines / Freelance  : BD {sidelines_bhd:,.2f}
- Other Income           : BD {other_income_bhd:,.2f}
--------------------------------------------------
TOTAL COMBINED INCOME    : BD {total_income_bhd:,.2f}
   - Equivalent in PHP   : PHP {(total_income_bhd * bhd_to_php):,.2f}
   - Equivalent in USD   : USD ${(total_income_bhd * bhd_to_usd):,.2f}

--------------------------------------------------
2. EXPENSES & OUTSTANDING PAYMENTS
--------------------------------------------------
- Total Expenses Paid    : BD {total_exp_bhd:,.2f}
- Net Cash Remaining     : BD {(total_income_bhd - total_exp_bhd):,.2f}
- PHP Billed Needed      : PHP {to_php(total_billed_bhd if 'total_billed_bhd' in locals() else 0.0):,.2f}
- PHP Actual Paid        : PHP {to_php(total_paid_bhd if 'total_paid_bhd' in locals() else 0.0):,.2f}
- PHP Remaining Unpaid   : PHP {to_php(total_pending_bhd if 'total_pending_bhd' in locals() else 0.0):,.2f}
==================================================
"""
        st.download_button(
            label="📥 Download Executive Summary (.TXT)",
            data=rep_text,
            file_name=f"financial_summary_{current_user.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# ----------------------------------------------------
# TAB 6: USER GUIDE
# ----------------------------------------------------
with tab_guide:
    st.subheader("📘 Security & Deployment Configuration Guide")
    st.markdown("""
    ### 🔐 Custom Access Keys Setup:
    To configure private passkeys for Rogee, User 2, User 3, or User 4 on Streamlit Cloud:
    1. Open your Streamlit Cloud dashboard.
    2. Go to **App Settings > Secrets**.
    3. Add your private keys:
       ```toml
       ROGEE_KEY = "YourPrivatePassphrase"
       USER2_KEY = "User2Passphrase"
       USER3_KEY = "User3Passphrase"
       USER4_KEY = "User4Passphrase"
       ```
    4. Click Save!
    """)
