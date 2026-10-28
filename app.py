import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import os
import json

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Rogee Financial Command Center",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark/Light Mode Adaptive Styling
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

    .alert-banner-green { background-color: #ECFDF5; border: 1px solid #A7F3D0; border-left: 5px solid #10B981; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; color: #065F46 !important; font-weight: 600; }
    @media (prefers-color-scheme: dark) {
        .alert-banner-green { background-color: #064E3B !important; border-color: #047857 !important; color: #A7F3D0 !important; }
    }

    .alert-banner-red { background-color: #FEF2F2; border: 1px solid #FECACA; border-left: 5px solid #EF4444; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; color: #991B1B !important; font-weight: 600; }
    @media (prefers-color-scheme: dark) {
        .alert-banner-red { background-color: #450A0A !important; border-color: #7F1D1D !important; color: #FECACA !important; }
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

# User Passcode & Profile Setup
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
        "def_key": "user32026",
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

# Sidebar Profile Login Portal
st.sidebar.title("🔐 Account Access")
selected_user_profile = st.sidebar.selectbox("Select Account Profile", list(USER_PROFILES.keys()), index=0)
user_cfg = USER_PROFILES[selected_user_profile]

correct_passcode = st.secrets.get(user_cfg["sec_key"], user_cfg["def_key"]) if hasattr(st, "secrets") else user_cfg["def_key"]

if "authenticated_user" not in st.session_state:
    st.session_state["authenticated_user"] = None

if st.session_state["authenticated_user"] != selected_user_profile:
    st.markdown('<div class="main-header">🔒 Rogee Financial Command Center</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">Security Access Portal for <b>{selected_user_profile}</b></div>', unsafe_allow_html=True)
    
    entered_key = st.text_input(f"Enter Passcode for {selected_user_profile}", type="password")
    login_btn = st.button("Unlock Command Center", type="primary")
    
    if login_btn:
        if entered_key == correct_passcode:
            st.session_state["authenticated_user"] = selected_user_profile
            st.success("Access Granted! Loading Command Center...")
            st.rerun()
        else:
            st.error("Incorrect Passcode! Access Denied.")
    st.stop()

# Logout Option
if st.sidebar.button("🔒 Sign Out / Lock Portal"):
    st.session_state["authenticated_user"] = None
    st.rerun()

current_user = st.session_state["authenticated_user"]
DATA_FILE = user_cfg["data_file"]
CONFIG_FILE = user_cfg["config_file"]
INVEST_FILE = user_cfg["invest_file"]

# Time calculations
utc_now = datetime.now(timezone.utc)
bh_time = utc_now + timedelta(hours=3)
ph_time = utc_now + timedelta(hours=8)

# Currency & User Settings Loader
def load_config():
    defaults = {
        "salary_bhd": 1200.0,
        "business_bhd": 0.0,
        "sidelines_bhd": 0.0,
        "other_income_bhd": 0.0,
        "bhd_to_php": 155.0,
        "bhd_to_usd": 2.65,
        "display_currency": "BHD",
        "framework_mode": "50/30/20 Standard",
        "needs_pct": 50,
        "wants_pct": 30,
        "savings_pct": 20
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                saved = json.load(f)
                defaults.update(saved)
        except Exception:
            pass
    return defaults

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=4)
    except Exception:
        pass

cfg = load_config()

# Data Loader
def load_data():
    cols = [
        "Item #", "Date", "Main Category", "Sub Category", "Merchant/Description",
        "Billed Amount", "Actual Paid", "Currency", "Pending Due",
        "% Paid", "% Remaining", "Equivalent", "Status", "Payment Method"
    ]
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            for c in cols:
                if c not in df.columns:
                    if c == "Billed Amount" and "Amount" in df.columns:
                        df["Billed Amount"] = df["Amount"]
                    elif c == "Actual Paid" and "Amount" in df.columns:
                        df["Actual Paid"] = df["Amount"]
                    elif c == "Currency":
                        df["Currency"] = "BHD"
                    elif c == "Status":
                        df["Status"] = "Paid"
                    elif c == "Item #":
                        df["Item #"] = range(1, len(df) + 1)
                    else:
                        df[c] = ""
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            return df[cols]
        except Exception:
            pass
    return pd.DataFrame(columns=cols)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df_expenses = load_data()

# Sidebar Settings
st.sidebar.markdown("---")
st.sidebar.subheader("💰 Income & Currency Settings")

display_curr = st.sidebar.selectbox("Dashboard Primary Currency", ["BHD", "PHP", "USD"], index=["BHD", "PHP", "USD"].index(cfg.get("display_currency", "BHD")))
bhd_to_php = st.sidebar.number_input("Exchange Rate (1 BHD to PHP ₱)", min_value=1.0, value=float(cfg.get("bhd_to_php", 155.0)), step=0.5)
bhd_to_usd = st.sidebar.number_input("Exchange Rate (1 BHD to USD $)", min_value=0.1, value=float(cfg.get("bhd_to_usd", 2.65)), step=0.01)

st.sidebar.markdown("#### 💵 Monthly Income Streams (BHD)")
salary_bhd = st.sidebar.number_input("Primary Net Salary (BD)", min_value=0.0, value=float(cfg.get("salary_bhd", 1200.0)), step=25.0)
business_bhd = st.sidebar.number_input("Business Income (BD)", min_value=0.0, value=float(cfg.get("business_bhd", 0.0)), step=25.0)
sidelines_bhd = st.sidebar.number_input("Sidelines / Freelance (BD)", min_value=0.0, value=float(cfg.get("sidelines_bhd", 0.0)), step=25.0)
other_income_bhd = st.sidebar.number_input("Other Income / Bonuses (BD)", min_value=0.0, value=float(cfg.get("other_income_bhd", 0.0)), step=25.0)

total_income_bhd = salary_bhd + business_bhd + sidelines_bhd + other_income_bhd
total_income_php = total_income_bhd * bhd_to_php
total_income_usd = total_income_bhd * bhd_to_usd

st.sidebar.markdown(f"""
<div style="background-color: #ECFDF5; border: 1px solid #A7F3D0; padding: 10px; border-radius: 6px; margin-top: 5px;">
    <span style="font-size: 0.8rem; font-weight: 700; color: #065F46;">TOTAL COMBINED MONTHLY INCOME:</span><br>
    <span style="font-size: 1.1rem; font-weight: 800; color: #047857;">BD {total_income_bhd:,.2f}</span><br>
    <span style="font-size: 0.82rem; font-weight: 600; color: #065F46;">₱ {total_income_php:,.2f} &nbsp;|&nbsp; $ {total_income_usd:,.2f}</span>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("📐 Budget Framework Allocation")
framework_mode = st.sidebar.selectbox("Framework Model", ["50/30/20 Standard", "60/20/20 Aggressive Savings", "Custom % Split"])

if framework_mode == "50/30/20 Standard":
    needs_pct, wants_pct, savings_pct = 50, 30, 20
elif framework_mode == "60/20/20 Aggressive Savings":
    needs_pct, wants_pct, savings_pct = 60, 20, 20
else:
    needs_pct = st.sidebar.slider("Needs Target %", 0, 100, int(cfg.get("needs_pct", 50)))
    wants_pct = st.sidebar.slider("Wants Target %", 0, 100, int(cfg.get("wants_pct", 30)))
    savings_pct = st.sidebar.slider("Savings Target %", 0, 100, int(cfg.get("savings_pct", 20)))

# Save Config
new_cfg = {
    "salary_bhd": salary_bhd,
    "business_bhd": business_bhd,
    "sidelines_bhd": sidelines_bhd,
    "other_income_bhd": other_income_bhd,
    "bhd_to_php": bhd_to_php,
    "bhd_to_usd": bhd_to_usd,
    "display_currency": display_curr,
    "framework_mode": framework_mode,
    "needs_pct": needs_pct,
    "wants_pct": wants_pct,
    "savings_pct": savings_pct
}
save_config(new_cfg)

# Conversion Helper Function
def convert_to_bhd(val, curr):
    try:
        val = float(val)
    except (ValueError, TypeError):
        return 0.0
    if curr == "PHP":
        return val / bhd_to_php if bhd_to_php > 0 else 0.0
    elif curr == "USD":
        return val / bhd_to_usd if bhd_to_usd > 0 else 0.0
    return val  # Default BHD

def get_curr_symbol(curr):
    if curr == "PHP": return "₱"
    if curr == "USD": return "$"
    return "BD"

def format_curr(val_bhd, curr):
    if curr == "PHP":
        return f"₱{(val_bhd * bhd_to_php):,.2f}"
    elif curr == "USD":
        return f"${(val_bhd * bhd_to_usd):,.2f}"
    return f"BD {val_bhd:,.2f}"

# Header Section
st.markdown('<div class="main-header">Rogee Financial Command Center</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Personal Finance & Budgeting System &nbsp;|&nbsp; Logged in as: <b>{current_user}</b></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="time-badge">
    Bahrain Time: {bh_time.strftime("%d %b %Y, %I:%M %p")} AST &nbsp;|&nbsp; 
    Philippine Time: {ph_time.strftime("%d %b %Y, %I:%M %p")} PHT &nbsp;|&nbsp; 
    Exchange Rate: 1 BHD = {bhd_to_php:,.2f} PHP = ${bhd_to_usd:,.2f} USD
</div>
""", unsafe_allow_html=True)

# Calculate Ledger Metrics accurately with per-transaction Currency support!
if not df_expenses.empty:
    # Compute per-row BHD equivalents
    bhd_billed_series = []
    bhd_paid_series = []
    bhd_pending_series = []
    
    for _, row in df_expenses.iterrows():
        b_amt = float(row.get("Billed Amount", 0.0) if pd.notnull(row.get("Billed Amount")) else 0.0)
        p_amt = float(row.get("Actual Paid", 0.0) if pd.notnull(row.get("Actual Paid")) else 0.0)
        curr = str(row.get("Currency", "BHD")).strip().upper()
        
        b_bhd = convert_to_bhd(b_amt, curr)
        p_bhd = convert_to_bhd(p_amt, curr)
        pending_bhd = max(0.0, b_bhd - p_bhd)
        
        bhd_billed_series.append(b_bhd)
        bhd_paid_series.append(p_bhd)
        bhd_pending_series.append(pending_bhd)
    
    df_expenses["Billed_BHD"] = bhd_billed_series
    df_expenses["Paid_BHD"] = bhd_paid_series
    df_expenses["Pending_BHD"] = bhd_pending_series

    actual_priority_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Priority", case=False, na=False)]["Paid_BHD"].sum())
    actual_debts_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Debts", case=False, na=False)]["Paid_BHD"].sum())
    actual_needs_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Needs", case=False, na=False)]["Paid_BHD"].sum())
    actual_wants_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Wants", case=False, na=False)]["Paid_BHD"].sum())
    actual_savings_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Savings", case=False, na=False)]["Paid_BHD"].sum())

    total_billed_bhd = float(df_expenses["Billed_BHD"].sum())
    total_paid_bhd = float(df_expenses["Paid_BHD"].sum())
    total_pending_bhd = float(df_expenses["Pending_BHD"].sum())
else:
    actual_priority_bhd = actual_debts_bhd = actual_needs_bhd = actual_wants_bhd = actual_savings_bhd = 0.0
    total_billed_bhd = total_paid_bhd = total_pending_bhd = 0.0

total_spent_bhd = total_paid_bhd
remaining_cash_bhd = total_income_bhd - total_spent_bhd

# Tabs Setup
tab_dash, tab_add, tab_history, tab_proj, tab_calc, tab_reports, tab_guide = st.tabs([
    "📊 Dashboard & Analytics",
    "➕ Record Expense",
    "📋 Transaction History",
    "🔮 12-Month Projections",
    "📈 MT5 Pip & Margin Calculator",
    "📥 Download Reports",
    "📘 Guide"
])

# TAB 1: DASHBOARD
with tab_dash:
    if remaining_cash_bhd < 0:
        over_bhd = abs(remaining_cash_bhd)
        st.markdown(f"""
        <div class="alert-banner-red">
            ⚠️ OVER BUDGET ALERT: Total payments exceed your monthly income by 
            <b>BD {over_bhd:,.2f}</b> (₱ {over_bhd * bhd_to_php:,.2f} | $ {over_bhd * bhd_to_usd:,.2f})!
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="alert-banner-green">
            🟢 NET SURPLUS BALANCE: You have <b>BD {remaining_cash_bhd:,.2f}</b> 
            (₱ {remaining_cash_bhd * bhd_to_php:,.2f} | $ {remaining_cash_bhd * bhd_to_usd:,.2f}) remaining unspent.
        </div>
        """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Monthly Income", format_curr(total_income_bhd, display_curr))
    m2.metric("Total Expenses Planned/Billed", format_curr(total_billed_bhd, display_curr), delta=f"Pending: {format_curr(total_pending_bhd, display_curr)}")
    m3.metric("Total Actual Paid", format_curr(total_paid_bhd, display_curr), delta=f"-{format_curr(total_paid_bhd, display_curr)}", delta_color="inverse")
    
    if remaining_cash_bhd >= 0:
        m4.metric("Net Cash Remaining", format_curr(remaining_cash_bhd, display_curr), delta=f"+{format_curr(remaining_cash_bhd, display_curr)}")
    else:
        m4.metric("Over Budget Balance", format_curr(remaining_cash_bhd, display_curr), delta=f"{format_curr(remaining_cash_bhd, display_curr)}", delta_color="inverse")

    st.markdown("---")
    st.subheader("📊 50/30/20 Target vs. Actual Expense Breakdown")

    needs_target_bhd = total_income_bhd * (needs_pct / 100.0)
    wants_target_bhd = total_income_bhd * (wants_pct / 100.0)
    savings_target_bhd = total_income_bhd * (savings_pct / 100.0)

    cat_summary_data = [
        {"Category": "Mandatory 100% Priority", "Target (%)": "100%", "Target Amount": "Priority", "Actual Paid": format_curr(actual_priority_bhd, display_curr), "Status": "Mandatory"},
        {"Category": "Debts & Credits", "Target (%)": "Fixed", "Target Amount": "Commitments", "Actual Paid": format_curr(actual_debts_bhd, display_curr), "Status": "Active Debt"},
        {"Category": "Needs (Essentials)", "Target (%)": f"{needs_pct}%", "Target Amount": format_curr(needs_target_bhd, display_curr), "Actual Paid": format_curr(actual_needs_bhd, display_curr), "Status": "On Track" if actual_needs_bhd <= needs_target_bhd else "Over Target"},
        {"Category": "Wants (Lifestyle)", "Target (%)": f"{wants_pct}%", "Target Amount": format_curr(wants_target_bhd, display_curr), "Actual Paid": format_curr(actual_wants_bhd, display_curr), "Status": "On Track" if actual_wants_bhd <= wants_target_bhd else "Over Target"},
        {"Category": "Savings & Investments", "Target (%)": f"{savings_pct}%", "Target Amount": format_curr(savings_target_bhd, display_curr), "Actual Paid": format_curr(actual_savings_bhd, display_curr), "Status": "Goal Met" if actual_savings_bhd >= savings_target_bhd else "Under Goal"}
    ]
    st.dataframe(pd.DataFrame(cat_summary_data), use_container_width=True, hide_index=True)

    c_chart1, c_chart2 = st.columns(2)
    with c_chart1:
        st.subheader("Target vs. Actual Spending")
        fig_bar = go.Figure(data=[
            go.Bar(name='Target', x=['Needs', 'Wants', 'Savings'], y=[needs_target_bhd, wants_target_bhd, savings_target_bhd], marker_color='#93C5FD'),
            go.Bar(name='Actual Paid', x=['Needs', 'Wants', 'Savings'], y=[actual_needs_bhd, actual_wants_bhd, actual_savings_bhd], marker_color='#1D4ED8')
        ])
        fig_bar.update_layout(barmode='group', margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    with c_chart2:
        st.subheader("Actual Spending Share")
        if total_paid_bhd > 0:
            fig_pie = px.pie(
                values=[actual_priority_bhd, actual_debts_bhd, actual_needs_bhd, actual_wants_bhd, actual_savings_bhd],
                names=['100% Priority', 'Debts', 'Needs', 'Wants', 'Savings'],
                color_discrete_sequence=['#EF4444', '#F59E0B', '#3B82F6', '#8B5CF6', '#10B981'],
                hole=0.4
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No paid transactions logged yet.")

# TAB 2: ADD EXPENSE
with tab_add:
    st.subheader("➕ Record a New Expense / Payment")
    
    # Real-time sub-category updating without needing page refresh!
    main_cat_choice = st.selectbox(
        "Main Category", 
        ["100% Priority Payments", "Debts & Credits", "Needs (50%)", "Wants (30%)", "Savings & Investments (20%)"],
        key="add_main_cat_select"
    )

    if "Priority" in main_cat_choice:
        sub_cat_options = ["Emergency Housing / Rent", "Medical Emergency", "Legal / Critical Obligation", "Urgent Family Support"]
    elif "Debts" in main_cat_choice:
        sub_cat_options = ["Credit Card Payment", "Personal Loan", "Car Loan", "Bank Overdraft", "Pawnshop / Money Owed"]
    elif "Needs" in main_cat_choice:
        sub_cat_options = ["Housing / Rent", "Electricity & Water", "Groceries", "Transport / Fuel", "Internet & Phone", "Insurance"]
    elif "Wants" in main_cat_choice:
        sub_cat_options = ["Dining Out & Coffee", "Shopping & Clothes", "Entertainment & Streaming", "Travel & Leisure", "Hobbies"]
    else:
        sub_cat_options = ["Emergency Fund Deposit", "Stock / Forex Investment", "Crypto Savings", "Real Estate Fund", "Retirement Account"]

    sub_cat_choice = st.selectbox("Sub Category", sub_cat_options, key="add_sub_cat_select")

    with st.form("record_expense_form", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            exp_date = st.date_input("Transaction Date", value=datetime.today())
            merchant_desc = st.text_input("Merchant / Description", placeholder="e.g. Electric Bill, Grocery Store, Credit Card")
            trans_curr = st.selectbox("Transaction Currency", ["BHD", "PHP", "USD"], index=0)
        
        with col_f2:
            billed_amt = st.number_input(f"Planned / Billed Amount ({trans_curr})", min_value=0.0, value=50.0, step=5.0)
            status_init = st.selectbox("Payment Status", ["Paid", "Partially Paid", "Pending Payment", "Not Paid"], index=0)
            
            def_paid_amt = billed_amt if status_init == "Paid" else (0.0 if "Not" in status_init or "Pending" in status_init else billed_amt * 0.5)
            actual_paid_amt = st.number_input(f"Actual Amount Paid ({trans_curr})", min_value=0.0, value=float(def_paid_amt), step=5.0)
            pay_method = st.selectbox("Payment Method", ["Benefit Pay", "Remittance", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])

        submit_exp = st.form_submit_button("💾 Save Transaction to Ledger")

        if submit_exp:
            p_due = max(0.0, billed_amt - actual_paid_amt)
            pct_p = (actual_paid_amt / billed_amt * 100.0) if billed_amt > 0 else 100.0
            pct_r = 100.0 - pct_p
            
            # Exact status calculation
            if pct_p >= 100.0:
                final_status = "Paid"
            elif pct_p == 0.0:
                final_status = "Not Paid"
            else:
                final_status = "Partially Paid"

            # Compute Equivalent String
            if trans_curr == "PHP":
                eq_bhd = billed_amt / bhd_to_php if bhd_to_php > 0 else 0
                eq_usd = eq_bhd * bhd_to_usd
                eq_str = f"BD {eq_bhd:,.2f} | $ {eq_usd:,.2f}"
            elif trans_curr == "USD":
                eq_bhd = billed_amt / bhd_to_usd if bhd_to_usd > 0 else 0
                eq_php = eq_bhd * bhd_to_php
                eq_str = f"BD {eq_bhd:,.2f} | ₱ {eq_php:,.2f}"
            else: # BHD
                eq_php = billed_amt * bhd_to_php
                eq_usd = billed_amt * bhd_to_usd
                eq_str = f"₱ {eq_php:,.2f} | $ {eq_usd:,.2f}"

            item_num = len(df_expenses) + 1
            new_entry = {
                "Item #": item_num,
                "Date": exp_date,
                "Main Category": main_cat_choice,
                "Sub Category": sub_cat_choice,
                "Merchant/Description": merchant_desc if merchant_desc else "Unspecified",
                "Billed Amount": float(billed_amt),
                "Actual Paid": float(actual_paid_amt),
                "Currency": trans_curr,
                "Pending Due": float(p_due),
                "% Paid": f"{pct_p:.1f}%",
                "% Remaining": f"{pct_r:.1f}%",
                "Equivalent": eq_str,
                "Status": final_status,
                "Payment Method": pay_method
            }
            df_expenses = pd.concat([df_expenses, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(df_expenses)
            st.success(f"Successfully recorded transaction: {trans_curr} {billed_amt:,.2f} for '{merchant_desc}'!")
            st.rerun()

# TAB 3: TRANSACTION HISTORY
with tab_history:
    st.subheader("📋 Transaction History & Ledger")

    if not df_expenses.empty:
        # Sorting & Categorical Grouping
        cat_order = ["100% Priority Payments", "Debts & Credits", "Needs (50%)", "Wants (30%)", "Savings & Investments (20%)"]
        
        df_display = df_expenses.copy()
        df_display["Date"] = pd.to_datetime(df_display["Date"]).dt.date
        
        # Categorical Sort
        df_display["Cat_Rank"] = df_display["Main Category"].apply(lambda x: cat_order.index(x) if x in cat_order else 99)
        df_display = df_display.sort_values(by=["Cat_Rank", "Date"], ascending=[True, True]).drop(columns=["Cat_Rank"])
        df_display["Item #"] = range(1, len(df_display) + 1)

        # Recalculate columns dynamically to ensure 100% accuracy on currency or amount edits!
        recalc_b_bhd = []
        recalc_p_bhd = []
        recalc_due = []
        recalc_pct_p = []
        recalc_pct_r = []
        recalc_eq = []
        recalc_status = []

        for _, row in df_display.iterrows():
            b = float(row["Billed Amount"]) if pd.notnull(row["Billed Amount"]) else 0.0
            p = float(row["Actual Paid"]) if pd.notnull(row["Actual Paid"]) else 0.0
            c = str(row["Currency"]).strip().upper() if pd.notnull(row["Currency"]) else "BHD"
            
            due = max(0.0, b - p)
            pct_paid = (p / b * 100.0) if b > 0 else 100.0
            pct_rem = 100.0 - pct_paid
            
            if pct_paid >= 100.0: st_val = "Paid"
            elif pct_paid == 0.0: st_val = "Not Paid"
            else: st_val = "Partially Paid"

            if c == "PHP":
                eq_b = b / bhd_to_php if bhd_to_php > 0 else 0
                eq_u = eq_b * bhd_to_usd
                eq_text = f"BD {eq_b:,.2f} | $ {eq_u:,.2f}"
            elif c == "USD":
                eq_b = b / bhd_to_usd if bhd_to_usd > 0 else 0
                eq_p = eq_b * bhd_to_php
                eq_text = f"BD {eq_b:,.2f} | ₱ {eq_p:,.2f}"
            else: # BHD
                eq_p = b * bhd_to_php
                eq_u = b * bhd_to_usd
                eq_text = f"₱ {eq_p:,.2f} | $ {eq_u:,.2f}"

            recalc_due.append(due)
            recalc_pct_p.append(f"{pct_paid:.1f}%")
            recalc_pct_r.append(f"{pct_rem:.1f}%")
            recalc_eq.append(eq_text)
            recalc_status.append(st_val)

        df_display["Pending Due"] = recalc_due
        df_display["% Paid"] = recalc_pct_p
        df_display["% Remaining"] = recalc_pct_r
        df_display["Equivalent"] = recalc_eq
        df_display["Status"] = recalc_status

        display_cols = [
            "Item #", "Date", "Main Category", "Sub Category", "Merchant/Description",
            "Billed Amount", "Actual Paid", "Currency", "Pending Due",
            "% Paid", "% Remaining", "Equivalent", "Status", "Payment Method"
        ]

        st.markdown("#### 🟢🟡🔴 Status Color-Highlighted Ledger View")
        st.caption("🟢 Green = Paid (100%) | 🟡 Yellow = Partially Paid | 🔴 Red = Unpaid (0%)")

        # HTML Color Styled Ledger
        def style_status_row(row):
            st_val = str(row["Status"])
            if st_val == "Paid":
                return ['background-color: #D1FAE5; color: #065F46; font-weight: 500;'] * len(row)
            elif st_val == "Partially Paid":
                return ['background-color: #FEF3C7; color: #92400E; font-weight: 500;'] * len(row)
            else:
                return ['background-color: #FEE2E2; color: #991B1B; font-weight: 500;'] * len(row)

        styled_df = df_display[display_cols].style.apply(style_status_row, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### ✏️ Interactive Ledger Editor")
        st.caption("Edit Billed Amount, Actual Paid, Currency, or Merchant details below, then click **Save Ledger Changes**.")

        edited_df = st.data_editor(
            df_display[display_cols],
            column_config={
                "Currency": st.column_config.SelectboxColumn("Currency", options=["BHD", "PHP", "USD"]),
                "Main Category": st.column_config.SelectboxColumn("Main Category", options=cat_order),
                "Status": st.column_config.SelectboxColumn("Status", options=["Paid", "Partially Paid", "Pending Payment", "Not Paid"]),
                "Payment Method": st.column_config.SelectboxColumn("Payment Method", options=["Benefit Pay", "Remittance", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])
            },
            disabled=["Item #", "Pending Due", "% Paid", "% Remaining", "Equivalent"],
            use_container_width=True,
            hide_index=True,
            key="ledger_editor"
        )

        if st.button("💾 Save Ledger Changes", type="primary"):
            save_data(edited_df)
            st.success("Ledger updated successfully!")
            st.rerun()

        st.markdown("---")
        st.subheader("💰 Total Outstanding & Payment Ledger Summary")

        # Compute exact totals by native currency
        php_rows = df_display[df_display["Currency"] == "PHP"]
        bhd_rows = df_display[df_display["Currency"] == "BHD"]
        usd_rows = df_display[df_display["Currency"] == "USD"]

        php_billed_total = float(php_rows["Billed Amount"].sum())
        php_paid_total = float(php_rows["Actual Paid"].sum())
        php_pending_total = float(php_rows["Pending Due"].sum())

        php_billed_eq_bhd = php_billed_total / bhd_to_php if bhd_to_php > 0 else 0.0
        php_paid_eq_bhd = php_paid_total / bhd_to_php if bhd_to_php > 0 else 0.0
        php_pending_eq_bhd = php_pending_total / bhd_to_php if bhd_to_php > 0 else 0.0

        sum_col1, sum_col2, sum_col3 = st.columns(3)
        
        with sum_col1:
            st.markdown(f"""
            <div style="background-color: #F3F4F6; border: 1px solid #D1D5DB; padding: 12px; border-radius: 8px;">
                <h4 style="margin: 0; color: #1F2937;">📋 Total Billed / Needed</h4>
                <hr style="margin: 8px 0;">
                <b>🇵🇭 PHP Currency Records:</b><br>
                <span style="font-size: 1.1rem; font-weight: 800; color: #2563EB;">₱ {php_billed_total:,.2f}</span>
                <span style="font-size: 0.85rem; color: #4B5563;">(BD {php_billed_eq_bhd:,.2f})</span><br><br>
                <b>🌍 Grand Total (All Currencies):</b><br>
                <span style="font-size: 1.15rem; font-weight: 800; color: #1E3A8A;">BD {total_billed_bhd:,.2f}</span><br>
                <span style="font-size: 0.85rem; color: #4B5563;">₱ {total_billed_bhd * bhd_to_php:,.2f} &nbsp;|&nbsp; $ {total_billed_bhd * bhd_to_usd:,.2f}</span>
            </div>
            """, unsafe_allow_html=True)

        with sum_col2:
            st.markdown(f"""
            <div style="background-color: #ECFDF5; border: 1px solid #A7F3D0; padding: 12px; border-radius: 8px;">
                <h4 style="margin: 0; color: #065F46;">🟢 Total Actual Paid</h4>
                <hr style="margin: 8px 0;">
                <b>🇵🇭 PHP Currency Records:</b><br>
                <span style="font-size: 1.1rem; font-weight: 800; color: #059669;">₱ {php_paid_total:,.2f}</span>
                <span style="font-size: 0.85rem; color: #065F46;">(BD {php_paid_eq_bhd:,.2f})</span><br><br>
                <b>🌍 Grand Total (All Currencies):</b><br>
                <span style="font-size: 1.15rem; font-weight: 800; color: #047857;">BD {total_paid_bhd:,.2f}</span><br>
                <span style="font-size: 0.85rem; color: #065F46;">₱ {total_paid_bhd * bhd_to_php:,.2f} &nbsp;|&nbsp; $ {total_paid_bhd * bhd_to_usd:,.2f}</span>
            </div>
            """, unsafe_allow_html=True)

        with sum_col3:
            st.markdown(f"""
            <div style="background-color: #FEF2F2; border: 1px solid #FECACA; padding: 12px; border-radius: 8px;">
                <h4 style="margin: 0; color: #991B1B;">🔴 Total Pending Unpaid</h4>
                <hr style="margin: 8px 0;">
                <b>🇵🇭 PHP Currency Records:</b><br>
                <span style="font-size: 1.1rem; font-weight: 800; color: #DC2626;">₱ {php_pending_total:,.2f}</span>
                <span style="font-size: 0.85rem; color: #991B1B;">(BD {php_pending_eq_bhd:,.2f})</span><br><br>
                <b>🌍 Grand Total (All Currencies):</b><br>
                <span style="font-size: 1.15rem; font-weight: 800; color: #991B1B;">BD {total_pending_bhd:,.2f}</span><br>
                <span style="font-size: 0.85rem; color: #991B1B;">₱ {total_pending_bhd * bhd_to_php:,.2f} &nbsp;|&nbsp; $ {total_pending_bhd * bhd_to_usd:,.2f}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🗑️ Clear All Transaction Ledger Records", type="secondary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.success("Ledger reset successfully!")
            st.rerun()
    else:
        st.info("No transactions recorded yet. Go to '➕ Record Expense' to add your first entry!")

# TAB 4: 12-MONTH PROJECTIONS
with tab_proj:
    st.subheader("🔮 12-Month & Yearly Projected Budgeting Engine")
    st.caption("Forecast future monthly expenses, income growth, inflation impacts, and long-term savings potential.")

    p_col1, p_col2 = st.columns(2)
    with p_col1:
        proj_base_income = st.number_input("Base Monthly Income (BHD)", min_value=0.0, value=float(total_income_bhd), step=50.0)
        proj_income_growth = st.slider("Expected Annual Income Growth (%)", 0.0, 25.0, 3.0, step=0.5)
        proj_fixed_needs = st.number_input("Monthly Fixed Needs & Debts (BHD)", min_value=0.0, value=float(needs_target_bhd), step=25.0)
    
    with p_col2:
        proj_inflation = st.slider("Estimated Annual Inflation Rate (%)", 0.0, 15.0, 2.5, step=0.5)
        proj_wants = st.number_input("Monthly Lifestyle Allowance (BHD)", min_value=0.0, value=float(wants_target_bhd), step=25.0)
        proj_monthly_savings_goal = st.number_input("Target Monthly Savings (BHD)", min_value=0.0, value=float(savings_target_bhd), step=25.0)

    # Calculate 12 Month Table
    months = [f"Month {i}" for i in range(1, 13)]
    proj_rows = []
    cum_savings = 0.0

    for m in range(1, 13):
        m_inc = proj_base_income * (1 + (proj_income_growth / 100.0) * ((m - 1) / 12.0))
        m_exp = (proj_fixed_needs + proj_wants) * (1 + (proj_inflation / 100.0) * ((m - 1) / 12.0))
        m_net = m_inc - m_exp
        cum_savings += m_net
        
        proj_rows.append({
            "Month": f"Month {m}",
            "Projected Income (BD)": round(m_inc, 2),
            "Projected Expenses (BD)": round(m_exp, 2),
            "Net Surplus (BD)": round(m_net, 2),
            "Cumulative Wealth (BD)": round(cum_savings, 2),
            "Cumulative Wealth (₱ PHP)": round(cum_savings * bhd_to_php, 2)
        })

    df_proj = pd.DataFrame(proj_rows)

    tot_proj_inc = df_proj["Projected Income (BD)"].sum()
    tot_proj_exp = df_proj["Projected Expenses (BD)"].sum()
    tot_proj_sav = df_proj["Net Surplus (BD)"].sum()

    pr_m1, pr_m2, pr_m3 = st.columns(3)
    pr_m1.metric("1-Year Projected Total Income", f"BD {tot_proj_inc:,.2f}", delta=f"₱ {tot_proj_inc * bhd_to_php:,.2f}")
    pr_m2.metric("1-Year Projected Total Expenses", f"BD {tot_proj_exp:,.2f}", delta=f"-BD {tot_proj_exp:,.2f}", delta_color="inverse")
    pr_m3.metric("1-Year Potential Net Savings Accumulation", f"BD {tot_proj_sav:,.2f}", delta=f"₱ {tot_proj_sav * bhd_to_php:,.2f}")

    st.markdown("---")
    st.dataframe(df_proj, use_container_width=True, hide_index=True)

    fig_proj = go.Figure()
    fig_proj.add_trace(go.Bar(x=df_proj["Month"], y=df_proj["Projected Income (BD)"], name="Projected Income", marker_color="#3B82F6"))
    fig_proj.add_trace(go.Bar(x=df_proj["Month"], y=df_proj["Projected Expenses (BD)"], name="Projected Expenses", marker_color="#EF4444"))
    fig_proj.add_trace(go.Scatter(x=df_proj["Month"], y=df_proj["Cumulative Wealth (BD)"], name="Cumulative Savings Growth", yaxis="y2", line=dict(color="#10B981", width=3)))

    fig_proj.update_layout(
        title="12-Month Projected Cash Flow & Cumulative Savings Growth",
        barmode="group",
        yaxis=dict(title="Monthly Amount (BHD)"),
        yaxis2=dict(title="Cumulative Savings (BHD)", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_proj, use_container_width=True)

# TAB 5: MT5 PIP & MARGIN CALCULATOR
with tab_calc:
    st.subheader("📈 MT5 Pip & Lot Size Position Calculator")
    st.caption("Calculate exact pip values, required margin, and risk management parameters across major currency pairs.")

    calc_pair = st.selectbox("Trading Asset / Currency Pair", [
        "USDPHP", "BHDPHP", "USDCAD", "EURUSD", "GBPUSD", "USDJPY",
        "XAUUSD (Gold)", "USDCHF", "AUDUSD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"
    ])

    c_p1, c_p2, c_p3 = st.columns(3)
    with c_p1:
        account_balance = st.number_input("Account Balance ($ USD)", min_value=10.0, value=1000.0, step=100.0)
        risk_pct = st.slider("Risk Per Trade (%)", 0.5, 10.0, 1.0, step=0.5)
    
    with c_p2:
        lot_size = st.number_input("Lot Size (Lots)", min_value=0.01, max_value=100.0, value=0.10, step=0.01)
        leverage = st.selectbox("Account Leverage", [50, 100, 200, 400, 500, 1000], index=4)

    with c_p3:
        sl_pips = st.number_input("Stop Loss (Pips)", min_value=1.0, value=20.0, step=5.0)
        tp_pips = st.number_input("Take Profit (Pips)", min_value=1.0, value=40.0, step=5.0)

    # Standard Forex calculations
    is_jpy = "JPY" in calc_pair
    is_gold = "XAUUSD" in calc_pair
    is_php = "PHP" in calc_pair

    if is_gold:
        contract_size = 100
        pip_size = 0.10
    elif is_jpy:
        contract_size = 100000
        pip_size = 0.01
    elif is_php:
        contract_size = 100000
        pip_size = 0.01
    else:
        contract_size = 100000
        pip_size = 0.0001

    pip_value_usd = lot_size * contract_size * pip_size
    risk_amount_usd = account_balance * (risk_pct / 100.0)
    rec_lot_size = risk_amount_usd / (sl_pips * (pip_value_usd / lot_size)) if sl_pips > 0 else 0.01

    margin_req_usd = (lot_size * contract_size) / leverage

    st.markdown("---")
    st.markdown("#### 📊 Calculation Results")

    res_col1, res_col2, res_col3, res_col4 = st.columns(4)
    res_col1.metric("Pip Value per Pip ($)", f"${pip_value_usd:.2f}", delta=f"₱ {pip_value_usd * (bhd_to_php/bhd_to_usd):,.2f}")
    res_col2.metric("Max Dollar Risk ($)", f"${risk_amount_usd:.2f}", delta=f"{risk_pct}% of Balance")
    res_col3.metric("Recommended Lot Size", f"{rec_lot_size:.2f} Lots")
    res_col4.metric("Required Margin ($)", f"${margin_req_usd:.2f}", delta=f"Leverage 1:{leverage}")

# TAB 6: DOWNLOAD REPORTS
with tab_reports:
    st.subheader("📥 Download Financial Reports & Data Exports")

    rep_col1, rep_col2 = st.columns(2)
    with rep_col1:
        st.markdown("#### 📊 CSV Transaction Ledger")
        if not df_expenses.empty:
            csv_bytes = df_expenses.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Complete CSV Ledger",
                data=csv_bytes,
                file_name=f"financial_ledger_{current_user.lower().replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No transactions logged yet.")

    with rep_col2:
        st.markdown("#### 📜 Executive Financial Summary (.TXT)")
        rep_date_str = datetime.today().strftime("%Y-%m-%d")
        summary_txt = f"""
==================================================
ROGEE FINANCIAL COMMAND CENTER - EXECUTIVE REPORT
==================================================
User Profile   : {current_user}
Report Date    : {rep_date_str}
Bahrain Time   : {bh_time.strftime("%Y-%m-%d %I:%M %p")} AST
Philippine Time: {ph_time.strftime("%Y-%m-%d %I:%M %p")} PHT
Exchange Rate  : 1 BHD = {bhd_to_php:,.2f} PHP = ${bhd_to_usd:,.2f} USD
Framework      : {framework_mode}

--------------------------------------------------
1. INCOME SUMMARY
--------------------------------------------------
- Primary Net Salary      : BD {salary_bhd:,.2f}
- Business Income         : BD {business_bhd:,.2f}
- Sidelines / Freelance   : BD {sidelines_bhd:,.2f}
- Other Income / Bonuses  : BD {other_income_bhd:,.2f}
--------------------------------------------------
TOTAL COMBINED INCOME     : BD {total_income_bhd:,.2f}
   - Equivalent in PHP    : ₱ {total_income_php:,.2f}
   - Equivalent in USD    : $ {total_income_usd:,.2f}

--------------------------------------------------
2. TRANSACTION LEDGER SUMMARY
--------------------------------------------------
- Total Billed / Planned  : BD {total_billed_bhd:,.2f} (₱ {total_billed_bhd * bhd_to_php:,.2f})
- Total Actual Paid       : BD {total_paid_bhd:,.2f} (₱ {total_paid_bhd * bhd_to_php:,.2f})
- Total Pending Unpaid    : BD {total_pending_bhd:,.2f} (₱ {total_pending_bhd * bhd_to_php:,.2f})
--------------------------------------------------
NET SURPLUS / REMAINING   : BD {remaining_cash_bhd:,.2f} (₱ {remaining_cash_bhd * bhd_to_php:,.2f})
==================================================
"""
        st.download_button(
            label="📥 Download Executive Financial Report (.TXT)",
            data=summary_txt,
            file_name=f"executive_summary_{current_user.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# TAB 7: GUIDE
with tab_guide:
    st.subheader("📘 Security & Configuration Guide")
    st.markdown("""
    ### 🔐 Passcode & Security Setup:
    To configure private passkeys for your account profiles on Streamlit Cloud:
    1. Go to your Streamlit Cloud dashboard.
    2. Click **App Settings > Secrets**.
    3. Enter your private passkeys in TOML format:
       ```toml
       ROGEE_KEY = "YourPrivatePasscode"
       USER2_KEY = "User2Passcode"
       USER3_KEY = "User3Passcode"
       USER4_KEY = "User4Passcode"
       ```
    4. Save changes and your app will be password protected!
    """)
