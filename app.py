import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import os
import json
import shutil

st.set_page_config(
    page_title="Rogee Financial Command Center",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling with Dark/Light Mode Adaptive Contrast
st.markdown('''
<style>
    .main-header { font-size: 1.8rem; font-weight: 800; color: #1E3A8A; margin-bottom: 0.1rem; line-height: 1.2; }
    @media (prefers-color-scheme: dark) { .main-header { color: #60A5FA !important; } }
    .sub-header { font-size: 0.95rem; color: #4B5563; margin-bottom: 0.8rem; }
    @media (prefers-color-scheme: dark) { .sub-header { color: #9CA3AF !important; } }
    
    .time-badge { background-color: #F3F4F6; border: 1px solid #E5E7EB; color: #1F2937 !important; padding: 6px 12px; border-radius: 6px; font-size: 0.82rem; font-weight: 600; margin-bottom: 12px; display: inline-block; width: 100%; text-align: center; }
    @media (prefers-color-scheme: dark) {
        .time-badge { background-color: #1F2937 !important; border-color: #374151 !important; color: #F3F4F6 !important; }
    }

    .notice-banner-green { background-color: #ECFDF5; border: 1px solid #A7F3D0; border-left: 5px solid #10B981; padding: 12px 16px; border-radius: 6px; margin-bottom: 14px; color: #065F46 !important; font-weight: 700; }
    .notice-banner-green * { color: #065F46 !important; }
    @media (prefers-color-scheme: dark) {
        .notice-banner-green { background-color: #064E3B !important; border-color: #047857 !important; color: #A7F3D0 !important; }
        .notice-banner-green * { color: #A7F3D0 !important; }
    }

    .notice-banner-red { background-color: #FEF2F2; border: 1px solid #FECACA; border-left: 5px solid #EF4444; padding: 12px 16px; border-radius: 6px; margin-bottom: 14px; color: #991B1B !important; font-weight: 700; }
    .notice-banner-red * { color: #991B1B !important; }
    @media (prefers-color-scheme: dark) {
        .notice-banner-red { background-color: #450A0A !important; border-color: #7F1D1D !important; color: #FECACA !important; }
        .notice-banner-red * { color: #FECACA !important; }
    }

    .summary-card-blue { background-color: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #3B82F6; padding: 12px 16px; border-radius: 6px; margin-bottom: 10px; color: #1E40AF !important; font-weight: 700; }
    .summary-card-blue * { color: #1E40AF !important; }
    @media (prefers-color-scheme: dark) {
        .summary-card-blue { background-color: #1E3A8A !important; border-color: #1D4ED8 !important; color: #BFDBFE !important; }
        .summary-card-blue * { color: #BFDBFE !important; }
    }

    .summary-card-green { background-color: #F0FDF4; border: 1px solid #BBF7D0; border-left: 4px solid #22C55E; padding: 12px 16px; border-radius: 6px; margin-bottom: 10px; color: #166534 !important; font-weight: 700; }
    .summary-card-green * { color: #166534 !important; }
    @media (prefers-color-scheme: dark) {
        .summary-card-green { background-color: #052E16 !important; border-color: #14532D !important; color: #BBF7D0 !important; }
        .summary-card-green * { color: #BBF7D0 !important; }
    }

    .summary-card-red { background-color: #FEF2F2; border: 1px solid #FECACA; border-left: 4px solid #EF4444; padding: 12px 16px; border-radius: 6px; margin-bottom: 10px; color: #991B1B !important; font-weight: 700; }
    .summary-card-red * { color: #991B1B !important; }
    @media (prefers-color-scheme: dark) {
        .summary-card-red { background-color: #450A0A !important; border-color: #7F1D1D !important; color: #FECACA !important; }
        .summary-card-red * { color: #FECACA !important; }
    }

    .summary-card-amber { background-color: #FFFBEB; border: 1px solid #FDE68A; border-left: 4px solid #F59E0B; padding: 12px 16px; border-radius: 6px; margin-bottom: 10px; color: #78350F !important; font-weight: 700; }
    .summary-card-amber * { color: #78350F !important; }
    @media (prefers-color-scheme: dark) {
        .summary-card-amber { background-color: #451A03 !important; border-color: #78350F !important; color: #FDE68A !important; }
        .summary-card-amber * { color: #FDE68A !important; }
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
''', unsafe_allow_html=True)

USER_PROFILES = {
    "Rogee": {
        "sec_key": "ROGEE_KEY",
        "def_key": "rogee2026",
        "data_file": "expenses_rogee.csv",
        "config_file": "config_rogee.json"
    },
    "User 2": {
        "sec_key": "USER2_KEY",
        "def_key": "user2026",
        "data_file": "expenses_user2.csv",
        "config_file": "config_user2.json"
    },
    "User 3": {
        "sec_key": "USER3_KEY",
        "def_key": "user32026",
        "data_file": "expenses_user3.csv",
        "config_file": "config_user3.json"
    },
    "User 4": {
        "sec_key": "USER4_KEY",
        "def_key": "user42026",
        "data_file": "expenses_user4.csv",
        "config_file": "config_user4.json"
    }
}

bhd_to_php = 155.0
bhd_to_usd = 2.6525
usd_to_php = 58.435

def convert_to_bhd(val, curr):
    c = str(curr).upper().strip()
    if c == "PHP":
        return val / bhd_to_php
    elif c == "USD":
        return val / bhd_to_usd
    return float(val)

def convert_from_bhd(val_bhd, target_curr):
    c = str(target_curr).upper().strip()
    if c == "PHP":
        return val_bhd * bhd_to_php
    elif c == "USD":
        return val_bhd * bhd_to_usd
    return float(val_bhd)

# Load / Save Data & Automatic Schema Migration
def load_data(file_name):
    # Fallback migration check if profile file doesn't exist
    if not os.path.exists(file_name):
        if os.path.exists("expenses.csv"):
            try:
                shutil.copy("expenses.csv", file_name)
            except Exception:
                pass
        elif os.path.exists("/workspace/artifacts/expenses.csv"):
            try:
                shutil.copy("/workspace/artifacts/expenses.csv", file_name)
            except Exception:
                pass

    if os.path.exists(file_name):
        try:
            df = pd.read_csv(file_name)
        except Exception:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    req_cols = ["Item #", "Date", "Main Category", "Sub Category", "Merchant/Description", 
                "Billed Amount", "Actual Paid", "Currency", "Pending Due", "% Paid", "% Remaining", 
                "Equivalent", "Status", "Payment Method"]

    if df.empty:
        # Create standard sample dataset if empty
        sample_records = [
            {"Item #": 1, "Date": "2026-10-01", "Main Category": "Needs (50%)", "Sub Category": "Housing / Rent / Mortgage", "Merchant/Description": "Apartment Rent", "Billed Amount": 1800.0, "Actual Paid": 1800.0, "Currency": "BHD", "Payment Method": "Bank Transfer"},
            {"Item #": 2, "Date": "2026-10-02", "Main Category": "Needs (50%)", "Sub Category": "Groceries", "Merchant/Description": "Whole Foods Market", "Billed Amount": 220.5, "Actual Paid": 220.5, "Currency": "BHD", "Payment Method": "Credit Card"},
            {"Item #": 3, "Date": "2026-10-03", "Main Category": "Needs (50%)", "Sub Category": "Utilities & Bills", "Merchant/Description": "Electric & Water Utility", "Billed Amount": 145.0, "Actual Paid": 145.0, "Currency": "BHD", "Payment Method": "Debit Card"},
            {"Item #": 4, "Date": "2026-10-05", "Main Category": "Wants (30%)", "Sub Category": "Dining Out & Coffee", "Merchant/Description": "Corner Cafe & Bistro", "Billed Amount": 42.5, "Actual Paid": 42.5, "Currency": "BHD", "Payment Method": "Credit Card"},
            {"Item #": 5, "Date": "2026-10-08", "Main Category": "Wants (30%)", "Sub Category": "Subscriptions", "Merchant/Description": "Streaming Services", "Billed Amount": 29.99, "Actual Paid": 29.99, "Currency": "BHD", "Payment Method": "Credit Card"},
            {"Item #": 6, "Date": "2026-10-10", "Main Category": "Savings & Debt (20%)", "Sub Category": "Emergency Fund", "Merchant/Description": "High-Yield Savings Deposit", "Billed Amount": 500.0, "Actual Paid": 500.0, "Currency": "BHD", "Payment Method": "Bank Transfer"},
            {"Item #": 7, "Date": "2026-10-12", "Main Category": "Savings & Debt (20%)", "Sub Category": "Stock Investments", "Merchant/Description": "Index Fund Contribution", "Billed Amount": 500.0, "Actual Paid": 500.0, "Currency": "BHD", "Payment Method": "Bank Transfer"},
            {"Item #": 8, "Date": "2026-10-15", "Main Category": "Needs (50%)", "Sub Category": "Transportation / Fuel", "Merchant/Description": "Gas Station", "Billed Amount": 55.0, "Actual Paid": 55.0, "Currency": "BHD", "Payment Method": "Credit Card"},
            {"Item #": 9, "Date": "2026-10-18", "Main Category": "Wants (30%)", "Sub Category": "Entertainment & Streaming", "Merchant/Description": "Concert Tickets", "Billed Amount": 115.0, "Actual Paid": 115.0, "Currency": "BHD", "Payment Method": "Credit Card"}
        ]
        df = pd.DataFrame(sample_records)

    # Legacy Column Mapping & Migration
    if "Amount" in df.columns and "Billed Amount" not in df.columns:
        df["Billed Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
    if "Actual Paid" not in df.columns:
        df["Actual Paid"] = df["Billed Amount"]
    if "Currency" not in df.columns:
        df["Currency"] = "BHD"

    df["Billed Amount"] = pd.to_numeric(df["Billed Amount"], errors="coerce").fillna(0.0)
    df["Actual Paid"] = pd.to_numeric(df["Actual Paid"], errors="coerce").fillna(0.0)
    df["Currency"] = df["Currency"].astype(str).fillna("BHD").str.strip().str.upper()

    df["Pending Due"] = (df["Billed Amount"] - df["Actual Paid"]).clip(lower=0.0)
    
    def calc_pct(row):
        b = float(row["Billed Amount"])
        p = float(row["Actual Paid"])
        if b <= 0:
            return 100.0 if p >= 0 else 0.0
        return round(min((p / b) * 100.0, 100.0), 1)

    df["% Paid"] = df.apply(calc_pct, axis=1)
    df["% Remaining"] = (100.0 - df["% Paid"]).clip(lower=0.0)

    def calc_status(row):
        pct = float(row["% Paid"])
        if pct >= 100.0:
            return "Paid"
        elif pct <= 0.0:
            return "Not Paid"
        return "Partially Paid"

    df["Status"] = df.apply(calc_status, axis=1)

    def calc_eq(row):
        curr = str(row["Currency"]).upper()
        billed = float(row["Billed Amount"])
        paid = float(row["Actual Paid"])
        if curr == "PHP":
            bhd_val = billed / bhd_to_php
            usd_val = billed / usd_to_php
            return f"BD {bhd_val:,.2f} | $ {usd_val:,.2f}"
        elif curr == "USD":
            bhd_val = billed / bhd_to_usd
            php_val = billed * usd_to_php
            return f"BD {bhd_val:,.2f} | ₱ {php_val:,.2f}"
        else:
            php_val = billed * bhd_to_php
            usd_val = billed * bhd_to_usd
            return f"₱ {php_val:,.2f} | $ {usd_val:,.2f}"

    df["Equivalent"] = df.apply(calc_eq, axis=1)

    # Sort & Grouping
    cat_order = {"100% Priority": 1, "Debts & Credits": 2, "Needs (50%)": 3, "Wants (30%)": 4, "Savings & Investments (20%)": 5}
    df["cat_rank"] = df["Main Category"].map(lambda x: cat_order.get(str(x), 9))
    df['Date_dt'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
    df = df.sort_values(by=["cat_rank", "Date_dt"], ascending=[True, True]).drop(columns=["cat_rank", "Date_dt"])
    
    df["Item #"] = range(1, len(df) + 1)
    
    for c in req_cols:
        if c not in df.columns:
            df[c] = ""
            
    return df[req_cols]

def save_data(df, file_name):
    df.to_csv(file_name, index=False)

# Sidebar Security Portal
st.sidebar.title("🔐 Access Control")

current_user = st.sidebar.selectbox("Select Profile", list(USER_PROFILES.keys()), index=0)
user_cfg = USER_PROFILES[current_user]

secret_val = st.secrets.get(user_cfg["sec_key"], user_cfg["def_key"])

if "auth_user" not in st.session_state:
    st.session_state["auth_user"] = None

pass_input = st.sidebar.text_input("Secret Passcode", type="password", key=f"pwd_{current_user}")

if st.sidebar.button("Unlock Portal / Sign In", type="primary"):
    if pass_input == secret_val:
        st.session_state["auth_user"] = current_user
        st.sidebar.success(f"Welcome back, {current_user}!")
        st.rerun()
    else:
        st.sidebar.error("Invalid Secret Passcode!")

if st.session_state["auth_user"] != current_user:
    st.sidebar.warning("🔐 Profile Locked. Enter passcode to access.")
    st.markdown(f'''
    <div class="notice-banner-red">
        <h3>🔒 Security Authentication Gate</h3>
        <p>Please enter your private passcode in the sidebar to unlock <b>{current_user}'s</b> Financial Command Center.</p>
    </div>
    ''', unsafe_allow_html=True)
    st.info("💡 **Default Passkeys for Reference**:\n- **Rogee**: `rogee2026` | **User 2**: `user2026` | **User 3**: `user32026` | **User 4**: `user42026` ")
    st.stop()

if st.sidebar.button("🔒 Lock Portal / Sign Out"):
    st.session_state["auth_user"] = None
    st.rerun()

DATA_FILE = user_cfg["data_file"]
df_expenses = load_data(DATA_FILE)

# Sidebar Settings
st.sidebar.markdown("---")
st.sidebar.title("💰 Monthly Take-Home Income")

salary_bhd = st.sidebar.number_input("Primary Salary (BD)", min_value=0.0, value=1200.0, step=50.0)
business_bhd = st.sidebar.number_input("Business Income (BD)", min_value=0.0, value=300.0, step=50.0)
sidelines_bhd = st.sidebar.number_input("Sidelines / Freelance (BD)", min_value=0.0, value=150.0, step=25.0)
other_income_bhd = st.sidebar.number_input("Other Income / Bonus (BD)", min_value=0.0, value=50.0, step=25.0)

total_income_bhd = salary_bhd + business_bhd + sidelines_bhd + other_income_bhd
total_income_php = total_income_bhd * bhd_to_php
total_income_usd = total_income_bhd * bhd_to_usd

st.sidebar.markdown(f'''
<div class="summary-card-green">
    <div style="font-size:0.85rem;">TOTAL COMBINED MONTHLY INCOME:</div>
    <div style="font-size:1.25rem; font-weight:800;">BD {total_income_bhd:,.2f}</div>
    <div style="font-size:0.82rem;">₱ {total_income_php:,.2f} PHP &nbsp;|&nbsp; $ {total_income_usd:,.2f} USD</div>
</div>
''', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 50/30/20 Target Benchmark (%)")
needs_pct = st.sidebar.slider("Needs Target % (Essentials)", 0, 100, 50)
wants_pct = st.sidebar.slider("Wants Target % (Lifestyle)", 0, 100, 30)
savings_pct = st.sidebar.slider("Savings Target % (Goals/Debt)", 0, 100, 20)

# Main Header Title & Time Badge
st.markdown('<div class="main-header">Rogee Financial Command Center</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Personal Finance & Multi-Currency Budgeting Engine (50/30/20 Framework)</div>', unsafe_allow_html=True)

now_utc = datetime.now(timezone.utc)
bh_time = now_utc + timedelta(hours=3)
ph_time = now_utc + timedelta(hours=8)

st.markdown(f'''
<div class="time-badge">
    📍 <b>Bahrain Time:</b> {bh_time.strftime("%d %b %Y, %I:%M %p")} AST &nbsp;|&nbsp; 
    🇵🇭 <b>Philippine Time:</b> {ph_time.strftime("%d %b %Y, %I:%M %p")} PST &nbsp;|&nbsp;
    👤 <b>Account:</b> {current_user}
</div>
''', unsafe_allow_html=True)

# Tabs Navigation
tab_dash, tab_add, tab_history, tab_proj, tab_mt5, tab_reports = st.tabs([
    "📊 Dashboard & Analytics",
    "➕ Record Expense / Payment",
    "📋 Transaction History & Ledger",
    "🔮 12-Month Projections",
    "📈 MT5 Pip Calculator",
    "📥 Reports & Data"
])

# Global Calculations
total_billed_bhd = 0.0
total_paid_bhd = 0.0
total_due_bhd = 0.0

actual_priority_bhd = 0.0
actual_debts_bhd = 0.0
actual_needs_bhd = 0.0
actual_wants_bhd = 0.0
actual_savings_bhd = 0.0

if not df_expenses.empty:
    for _, row in df_expenses.iterrows():
        b_bhd = convert_to_bhd(float(row["Billed Amount"]), row["Currency"])
        p_bhd = convert_to_bhd(float(row["Actual Paid"]), row["Currency"])
        d_bhd = max(0.0, b_bhd - p_bhd)

        total_billed_bhd += b_bhd
        total_paid_bhd += p_bhd
        total_due_bhd += d_bhd

        cat = str(row["Main Category"])
        if "100% Priority" in cat:
            actual_priority_bhd += p_bhd
        elif "Debts" in cat:
            actual_debts_bhd += p_bhd
        elif "Needs" in cat:
            actual_needs_bhd += p_bhd
        elif "Wants" in cat:
            actual_wants_bhd += p_bhd
        elif "Savings" in cat:
            actual_savings_bhd += p_bhd

total_spent_bhd = total_paid_bhd
remaining_cash_bhd = total_income_bhd - total_spent_bhd
remaining_cash_php = remaining_cash_bhd * bhd_to_php
remaining_cash_usd = remaining_cash_bhd * bhd_to_usd

savings_rate = (actual_savings_bhd / total_income_bhd * 100.0) if total_income_bhd > 0 else 0.0

# TAB 1: DASHBOARD
with tab_dash:
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Monthly Net Income", f"BD {total_income_bhd:,.2f}")
    m2.metric("Total Spent / Paid", f"BD {total_spent_bhd:,.2f}")
    
    if remaining_cash_bhd >= 0:
        m3.metric("Remaining Balance", f"BD {remaining_cash_bhd:,.2f}")
    else:
        m3.metric("Over Budget Balance", f"-BD {abs(remaining_cash_bhd):,.2f}", delta=f"-BD {abs(remaining_cash_bhd):,.2f}", delta_color="inverse")
        
    m4.metric("Savings & Debt Rate", f"{savings_rate:.1f}%")
    m5.metric("Total Expenses to be Paid", f"BD {total_billed_bhd:,.2f}", delta=f"Pending: BD {total_due_bhd:,.2f}", delta_color="inverse")

    st.markdown("---")
    st.subheader("📊 50/30/20 Benchmark Allocation Breakdown")

    needs_target_bhd = total_income_bhd * (needs_pct / 100.0)
    wants_target_bhd = total_income_bhd * (wants_pct / 100.0)
    savings_target_bhd = total_income_bhd * (savings_pct / 100.0)

    cat_data = [
        {"Category": "100% Priority Payments", "Target ($)": "Fixed Required", "Actual Paid (BD)": actual_priority_bhd, "Status": "Mandatory"},
        {"Category": "Debts & Credits", "Target ($)": "Fixed Required", "Actual Paid (BD)": actual_debts_bhd, "Status": "Priority Payoff"},
        {"Category": f"Needs ({needs_pct}%)", "Target ($)": f"BD {needs_target_bhd:,.2f}", "Actual Paid (BD)": actual_needs_bhd, "Status": "On Track" if actual_needs_bhd <= needs_target_bhd else "Over Target"},
        {"Category": f"Wants ({wants_pct}%)", "Target ($)": f"BD {wants_target_bhd:,.2f}", "Actual Paid (BD)": actual_wants_bhd, "Status": "On Track" if actual_wants_bhd <= wants_target_bhd else "Over Target"},
        {"Category": f"Savings ({savings_pct}%)", "Target ($)": f"BD {savings_target_bhd:,.2f}", "Actual Paid (BD)": actual_savings_bhd, "Status": "Goal Met" if actual_savings_bhd >= savings_target_bhd else "Under Goal"}
    ]
    st.dataframe(pd.DataFrame(cat_data), use_container_width=True, hide_index=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🎯 Target vs. Actual Spending (BHD)")
        chart_df = pd.DataFrame({
            "Category": ["Needs", "Wants", "Savings"],
            "Target": [needs_target_bhd, wants_target_bhd, savings_target_bhd],
            "Actual": [actual_needs_bhd, actual_wants_bhd, actual_savings_bhd]
        })
        fig_bar = go.Figure(data=[
            go.Bar(name='Target', x=chart_df['Category'], y=chart_df['Target'], marker_color='#93C5FD'),
            go.Bar(name='Actual', x=chart_df['Category'], y=chart_df['Actual'], marker_color='#1D4ED8')
        ])
        fig_bar.update_layout(barmode='group', yaxis_title="Amount (BD)", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("🥧 Actual Expense Share")
        if total_spent_bhd > 0:
            fig_pie = px.pie(
                values=[actual_priority_bhd, actual_debts_bhd, actual_needs_bhd, actual_wants_bhd, actual_savings_bhd],
                names=["100% Priority", "Debts & Credits", "Needs", "Wants", "Savings"],
                color_discrete_sequence=['#EF4444', '#F59E0B', '#2563EB', '#10B981', '#8B5CF6'],
                hole=0.45
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expense entries logged yet.")

# TAB 2: RECORD EXPENSE
with tab_add:
    st.subheader("➕ Record a New Expense or Payment Entry")

    col_cat1, col_cat2 = st.columns(2)
    with col_cat1:
        main_cat_input = st.selectbox(
            "Main Category",
            ["100% Priority", "Debts & Credits", "Needs (50%)", "Wants (30%)", "Savings & Investments (20%)"],
            key="add_main_cat"
        )

    if "100% Priority" in main_cat_input:
        sub_options = ["Rent / Mortgage", "Tuition & School Fees", "Insurance Premium", "Utility Bills", "Family Allowance"]
    elif "Debts" in main_cat_input:
        sub_options = ["Credit Card Minimum", "Personal Loan", "Car Loan", "Overdraft Payoff", "Friend/Family Loan"]
    elif "Needs" in main_cat_input:
        sub_options = ["Groceries", "Fuel & Transport", "Healthcare / Medicine", "Home Maintenance", "Work Expenses"]
    elif "Wants" in main_cat_input:
        sub_options = ["Dining Out & Coffee", "Shopping & Apparel", "Entertainment & Travel", "Subscriptions", "Hobbies"]
    else:
        sub_options = ["Emergency Fund", "Stock Portfolio", "Crypto Investment", "Real Estate Savings", "Retirement Fund"]

    with col_cat2:
        sub_cat_input = st.selectbox("Sub Category", sub_options, key="add_sub_cat")

    with st.form("add_expense_form", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            exp_date = st.date_input("Date", value=datetime.today())
            merchant = st.text_input("Merchant / Description", placeholder="e.g., Grocery Store, Landlord")
            curr_input = st.selectbox("Transaction Currency", ["BHD", "PHP", "USD"], index=0)

        with col_f2:
            billed_amt = st.number_input(f"Planned / Billed Amount ({curr_input})", min_value=0.01, step=5.0, value=50.0)
            actual_paid_amt = st.number_input(f"Actual Amount Paid ({curr_input})", min_value=0.0, step=5.0, value=50.0)
            payment_method = st.selectbox("Payment Method", ["Benefit Pay", "Remittance", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])

        submit_btn = st.form_submit_button("💾 Save Transaction Entry", type="primary")

        if submit_btn:
            new_entry = pd.DataFrame([{
                "Item #": len(df_expenses) + 1,
                "Date": str(exp_date),
                "Main Category": main_cat_input,
                "Sub Category": sub_cat_input,
                "Merchant/Description": merchant if merchant else "Unspecified",
                "Billed Amount": float(billed_amt),
                "Actual Paid": float(actual_paid_amt),
                "Currency": curr_input,
                "Pending Due": max(0.0, float(billed_amt) - float(actual_paid_amt)),
                "% Paid": round(min((float(actual_paid_amt) / float(billed_amt)) * 100.0, 100.0), 1) if float(billed_amt) > 0 else 100.0,
                "% Remaining": max(0.0, 100.0 - (round(min((float(actual_paid_amt) / float(billed_amt)) * 100.0, 100.0), 1) if float(billed_amt) > 0 else 100.0)),
                "Equivalent": "",
                "Status": "Paid" if float(actual_paid_amt) >= float(billed_amt) else ("Not Paid" if float(actual_paid_amt) <= 0 else "Partially Paid"),
                "Payment Method": payment_method
            }])
            
            df_updated = pd.concat([df_expenses, new_entry], ignore_index=True)
            save_data(df_updated, DATA_FILE)
            st.success(f"Successfully recorded '{merchant if merchant else sub_cat_input}' entry!")
            st.rerun()

# TAB 3: TRANSACTION HISTORY & LEDGER
with tab_history:
    st.subheader("📋 Recorded Expense History & Transaction Ledger")

    # NOTICE BANNER ABOVE TABLE
    if remaining_cash_bhd >= 0:
        st.markdown(f'''
        <div class="notice-banner-green">
            🟢 <b>WITHIN BUDGET STATUS:</b> You have available remaining income!<br>
            <b>Net Unspent Cash Balance:</b> BD {remaining_cash_bhd:,.2f} &nbsp;|&nbsp; ₱ {remaining_cash_php:,.2f} PHP &nbsp;|&nbsp; $ {remaining_cash_usd:,.2f} USD
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
        <div class="notice-banner-red">
            🚨 <b>OVER BUDGET STATUS NOTICE:</b> Total payments exceed your monthly income limit!<br>
            <b>Current Overage / Limit Deficit:</b> -BD {abs(remaining_cash_bhd):,.2f} &nbsp;|&nbsp; -₱ {abs(remaining_cash_php):,.2f} PHP &nbsp;|&nbsp; -$ {abs(remaining_cash_usd):,.2f} USD
        </div>
        ''', unsafe_allow_html=True)

    if not df_expenses.empty:
        cat_filter = st.multiselect(
            "Filter by Main Category",
            options=["100% Priority", "Debts & Credits", "Needs (50%)", "Wants (30%)", "Savings & Investments (20%)"],
            default=["100% Priority", "Debts & Credits", "Needs (50%)", "Wants (30%)", "Savings & Investments (20%)"]
        )

        df_filtered = df_expenses[df_expenses["Main Category"].isin(cat_filter)] if cat_filter else df_expenses

        st.markdown("#### ✏️ Interactive Editable Ledger")
        st.caption("Double-click any cell below to update amounts, dates, or payment statuses directly:")

        edited_df = st.data_editor(
            df_filtered,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Item #": st.column_config.NumberColumn("Item #", disabled=True),
                "Billed Amount": st.column_config.NumberColumn("Billed Amount", format="%.2f"),
                "Actual Paid": st.column_config.NumberColumn("Actual Paid", format="%.2f"),
                "Currency": st.column_config.SelectboxColumn("Currency", options=["BHD", "PHP", "USD"]),
                "Status": st.column_config.SelectboxColumn("Status", options=["Paid", "Partially Paid", "Not Paid"]),
                "Payment Method": st.column_config.SelectboxColumn("Payment Method", options=["Benefit Pay", "Remittance", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])
            },
            hide_index=True,
            key="ledger_editor"
        )

        if st.button("💾 Save Ledger Changes", type="primary"):
            save_data(edited_df, DATA_FILE)
            st.success("Ledger updates saved successfully!")
            st.rerun()

        st.markdown("---")
        st.markdown("#### 🎨 Color-Coded Status Ledger View")

        def style_rows(row):
            pct = float(row["% Paid"]) if "% Paid" in row and pd.notnull(row["% Paid"]) else 0.0
            if pct >= 100.0:
                return ['background-color: #D1FAE5; color: #065F46; font-weight: 600;'] * len(row)
            elif pct <= 0.0:
                return ['background-color: #FEE2E2; color: #991B1B; font-weight: 600;'] * len(row)
            return ['background-color: #FEF3C7; color: #92400E; font-weight: 600;'] * len(row)

        st.dataframe(
            df_filtered.style.apply(style_rows, axis=1),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        st.markdown("### 💰 Total Outstanding & Payment Ledger Summary")

        # Summary calculations
        billed_php_only = 0.0
        paid_php_only = 0.0
        due_php_only = 0.0

        for _, r in df_filtered.iterrows():
            if str(r["Currency"]).upper() == "PHP":
                b = float(r["Billed Amount"])
                p = float(r["Actual Paid"])
                d = max(0.0, b - p)
                billed_php_only += b
                paid_php_only += p
                due_php_only += d

        billed_php_in_bhd = billed_php_only / bhd_to_php
        paid_php_in_bhd = paid_php_only / bhd_to_php
        due_php_in_bhd = due_php_only / bhd_to_php

        tot_b_bhd = sum(convert_to_bhd(float(r["Billed Amount"]), r["Currency"]) for _, r in df_filtered.iterrows())
        tot_p_bhd = sum(convert_to_bhd(float(r["Actual Paid"]), r["Currency"]) for _, r in df_filtered.iterrows())
        tot_d_bhd = max(0.0, tot_b_bhd - tot_p_bhd)

        col_s1, col_s2, col_s3 = st.columns(3)

        with col_s1:
            st.markdown(f'''
            <div class="summary-card-blue">
                <div style="font-size:0.9rem; font-weight:800; color:#1E40AF;">📋 TOTAL BILLED / NEEDED TO PAY</div>
                <hr style="margin:6px 0; border-color:#BFDBFE;">
                <div style="font-size:0.85rem; color:#1E40AF;"><b>🇵🇭 PHP Record Total:</b> ₱ {billed_php_only:,.2f}</div>
                <div style="font-size:0.8rem; color:#1E40AF;">(Equivalent: BD {billed_php_in_bhd:,.2f})</div>
                <hr style="margin:6px 0; border-color:#BFDBFE;">
                <div style="font-size:1.1rem; font-weight:800; color:#1E40AF;">BD {tot_b_bhd:,.2f}</div>
                <div style="font-size:0.8rem; color:#1E40AF;">₱ {tot_b_bhd * bhd_to_php:,.2f} PHP | $ {tot_b_bhd * bhd_to_usd:,.2f} USD</div>
            </div>
            ''', unsafe_allow_html=True)

        with col_s2:
            st.markdown(f'''
            <div class="summary-card-green">
                <div style="font-size:0.9rem; font-weight:800; color:#166534;">🟢 TOTAL ACTUAL AMOUNT PAID</div>
                <hr style="margin:6px 0; border-color:#BBF7D0;">
                <div style="font-size:0.85rem; color:#166534;"><b>🇵🇭 PHP Record Paid:</b> ₱ {paid_php_only:,.2f}</div>
                <div style="font-size:0.8rem; color:#166534;">(Equivalent: BD {paid_php_in_bhd:,.2f})</div>
                <hr style="margin:6px 0; border-color:#BBF7D0;">
                <div style="font-size:1.1rem; font-weight:800; color:#166534;">BD {tot_p_bhd:,.2f}</div>
                <div style="font-size:0.8rem; color:#166534;">₱ {tot_p_bhd * bhd_to_php:,.2f} PHP | $ {tot_p_bhd * bhd_to_usd:,.2f} USD</div>
            </div>
            ''', unsafe_allow_html=True)

        with col_s3:
            st.markdown(f'''
            <div class="summary-card-red">
                <div style="font-size:0.9rem; font-weight:800; color:#991B1B;">🔴 TOTAL REMAINING PENDING DUE</div>
                <hr style="margin:6px 0; border-color:#FECACA;">
                <div style="font-size:0.85rem; color:#991B1B;"><b>🇵🇭 PHP Record Remaining:</b> ₱ {due_php_only:,.2f}</div>
                <div style="font-size:0.8rem; color:#991B1B;">(Equivalent: BD {due_php_in_bhd:,.2f})</div>
                <hr style="margin:6px 0; border-color:#FECACA;">
                <div style="font-size:1.1rem; font-weight:800; color:#991B1B;">BD {tot_d_bhd:,.2f}</div>
                <div style="font-size:0.8rem; color:#991B1B;">₱ {tot_d_bhd * bhd_to_php:,.2f} PHP | $ {tot_d_bhd * bhd_to_usd:,.2f} USD</div>
            </div>
            ''', unsafe_allow_html=True)

# TAB 4: 12-MONTH PROJECTIONS
with tab_proj:
    st.subheader("🔮 12-Month & Yearly Projected Budgeting Engine")
    st.caption("Plan and forecast your future expenses, income growth, and savings trajectory over the next 12 months:")

    cp1, cp2, cp3 = st.columns(3)
    with cp1:
        base_proj_income = st.number_input("Baseline Monthly Income (BD)", min_value=100.0, value=float(total_income_bhd), step=50.0)
        annual_growth = st.slider("Expected Annual Income Growth (%)", 0.0, 20.0, 5.0, step=0.5)
    with cp2:
        fixed_needs_proj = st.number_input("Monthly Fixed Needs & Debt (BD)", min_value=0.0, value=float(actual_priority_bhd + actual_debts_bhd + actual_needs_bhd), step=25.0)
        inflation_rate = st.slider("Projected Annual Inflation (%)", 0.0, 15.0, 3.0, step=0.5)
    with cp3:
        lifestyle_proj = st.number_input("Monthly Lifestyle Allowance (BD)", min_value=0.0, value=float(actual_wants_bhd), step=25.0)
        monthly_savings_goal = st.number_input("Monthly Savings Target (BD)", min_value=0.0, value=float(savings_target_bhd), step=25.0)

    proj_rows = []
    cum_savings = 0.0
    
    for m in range(1, 13):
        m_inc = base_proj_income * ((1.0 + (annual_growth / 100.0)) ** ((m - 1) / 12.0))
        m_needs = fixed_needs_proj * ((1.0 + (inflation_rate / 100.0)) ** ((m - 1) / 12.0))
        m_wants = lifestyle_proj
        m_exp = m_needs + m_wants
        m_surplus = m_inc - m_exp
        cum_savings += m_surplus

        proj_rows.append({
            "Month": f"Month {m}",
            "Projected Income (BD)": round(m_inc, 2),
            "Needs & Fixed (BD)": round(m_needs, 2),
            "Lifestyle Wants (BD)": round(m_wants, 2),
            "Total Expenses (BD)": round(m_exp, 2),
            "Net Surplus (BD)": round(m_surplus, 2),
            "Cumulative Wealth (BD)": round(cum_savings, 2)
        })

    df_proj = pd.DataFrame(proj_rows)

    tot_1y_inc = df_proj["Projected Income (BD)"].sum()
    tot_1y_exp = df_proj["Total Expenses (BD)"].sum()
    tot_1y_sav = df_proj["Net Surplus (BD)"].sum()

    st.markdown("---")
    kp1, kp2, kp3 = st.columns(3)
    kp1.metric("Total 1-Year Projected Income", f"BD {tot_1y_inc:,.2f}", delta=f"₱ {tot_1y_inc * bhd_to_php:,.2f} PHP")
    kp2.metric("Total 1-Year Projected Expenses", f"BD {tot_1y_exp:,.2f}", delta=f"₱ {tot_1y_exp * bhd_to_php:,.2f} PHP", delta_color="inverse")
    kp3.metric("Total 1-Year Net Savings Build-up", f"BD {tot_1y_sav:,.2f}", delta=f"₱ {tot_1y_sav * bhd_to_php:,.2f} PHP")

    st.markdown("---")
    st.dataframe(df_proj, use_container_width=True, hide_index=True)

    c_p1, c_p2 = st.columns(2)
    with c_p1:
        st.subheader("📊 Projected Monthly Income vs. Expenses")
        fig_p1 = go.Figure(data=[
            go.Bar(name='Income', x=df_proj['Month'], y=df_proj['Projected Income (BD)'], marker_color='#22C55E'),
            go.Bar(name='Expenses', x=df_proj['Month'], y=df_proj['Total Expenses (BD)'], marker_color='#EF4444')
        ])
        fig_p1.update_layout(barmode='group', yaxis_title="Amount (BD)", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_p1, use_container_width=True)

    with c_p2:
        st.subheader("📈 1-Year Cumulative Wealth & Savings Trajectory")
        fig_p2 = px.line(df_proj, x='Month', y='Cumulative Wealth (BD)', markers=True, line_shape='spline')
        fig_p2.update_traces(line_color='#3B82F6', line_width=3)
        fig_p2.update_layout(yaxis_title="Cumulative Wealth (BD)", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_p2, use_container_width=True)

# TAB 5: MT5 PIP CALCULATOR
with tab_mt5:
    st.subheader("📈 MT5 Pip Value & Position Size Calculator")
    st.caption("Calculate exact pip value, required margin, and potential P&L across major Forex and Commodities pairs:")

    cm1, cm2, cm3 = st.columns(3)
    with cm1:
        pair_select = st.selectbox("Trading Pair", ["USDPHP", "BHDPHP", "USDCAD", "EURUSD", "GBPUSD", "USDJPY", "XAUUSD (Gold)", "USDCHF", "AUDUSD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"])
        lot_size = st.number_input("Lot Size (Volume)", min_value=0.01, max_value=100.0, value=0.10, step=0.01)
    with cm2:
        account_equity = st.number_input("Account Equity ($)", min_value=10.0, value=1000.0, step=100.0)
        leverage = st.selectbox("Account Leverage", [100, 200, 400, 500, 1000], index=3)
    with cm3:
        entry_price = st.number_input("Entry Price", min_value=0.0001, value=1.0850 if "EUR" in pair_select else (2750.0 if "XAU" in pair_select else 58.40), format="%.4f")
        exit_price = st.number_input("Exit Price", min_value=0.0001, value=1.0900 if "EUR" in pair_select else (2760.0 if "XAU" in pair_select else 58.90), format="%.4f")

    # Pip Value Formula
    if "XAU" in pair_select:
        contract_size = 100
        pip_size = 0.10
    elif "JPY" in pair_select or "PHP" in pair_select:
        contract_size = 100000
        pip_size = 0.01
    else:
        contract_size = 100000
        pip_size = 0.0001

    pip_value_usd = lot_size * contract_size * pip_size
    pips_gained = abs(exit_price - entry_price) / pip_size
    profit_loss_usd = (exit_price - entry_price) * lot_size * contract_size if "XAU" not in pair_select else (exit_price - entry_price) * lot_size * 100
    req_margin_usd = (entry_price * lot_size * contract_size) / leverage

    st.markdown("---")
    pm1, pm2, pm3, pm4 = st.columns(4)
    pm1.metric("Pip Value ($)", f"${pip_value_usd:,.2f}")
    pm2.metric("Total Pips Movement", f"{pips_gained:,.1f} pips")
    pm3.metric("Required Margin ($)", f"${req_margin_usd:,.2f}")
    pm4.metric("Estimated Trade P&L ($)", f"${profit_loss_usd:,.2f}", delta=f"${profit_loss_usd:,.2f}")

# TAB 6: REPORTS & DATA
with tab_reports:
    st.subheader("📥 Download Financial Reports & Transaction Records")

    cr1, cr2 = st.columns(2)
    with cr1:
        st.markdown("#### 📊 CSV Transaction Ledger Export")
        if not df_expenses.empty:
            csv_bytes = df_expenses.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Full CSV Ledger",
                data=csv_bytes,
                file_name=f"financial_ledger_{current_user.lower().replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No transaction data available.")

    with cr2:
        st.markdown("#### 📜 Executive Financial Summary (.TXT)")
        rep_date = datetime.today().strftime("%Y-%m-%d")
        report_text = f"""
==================================================
ROGEE FINANCIAL COMMAND CENTER - EXECUTIVE REPORT
==================================================
Account Profile: {current_user}
Report Date    : {rep_date}
Bahrain Time   : {bh_time.strftime("%Y-%m-%d %I:%M %p")}
Philippine Time: {ph_time.strftime("%Y-%m-%d %I:%M %p")}
Exchange Rates : 1 BHD = {bhd_to_php:.2f} PHP = $ {bhd_to_usd:.2f} USD

--------------------------------------------------
1. COMBINED INCOME & CASH SUMMARY
--------------------------------------------------
- Primary Salary         : BD {salary_bhd:,.2f}
- Business Income        : BD {business_bhd:,.2f}
- Sidelines / Freelance  : BD {sidelines_bhd:,.2f}
- Other Income / Bonus   : BD {other_income_bhd:,.2f}
--------------------------------------------------
TOTAL COMBINED MONTHLY INCOME: BD {total_income_bhd:,.2f}
  - Equivalent in PHP   : ₱ {total_income_php:,.2f} PHP
  - Equivalent in USD   : $ {total_income_usd:,.2f} USD

--------------------------------------------------
2. EXPENSES & PAYMENT SUMMARY
--------------------------------------------------
- 100% Priority Payments : BD {actual_priority_bhd:,.2f}
- Debts & Credits        : BD {actual_debts_bhd:,.2f}
- Needs ({needs_pct}% Target)     : BD {actual_needs_bhd:,.2f}
- Wants ({wants_pct}% Target)     : BD {actual_wants_bhd:,.2f}
- Savings ({savings_pct}% Target) : BD {actual_savings_bhd:,.2f}
--------------------------------------------------
TOTAL EXPENSES PAID      : BD {total_spent_bhd:,.2f}
NET UNSPENT CASH BALANCE : BD {remaining_cash_bhd:,.2f}
==================================================
"""
        st.download_button(
            label="📥 Download Executive Report (.TXT)",
            data=report_text,
            file_name=f"executive_summary_{current_user.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )
