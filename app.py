import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import os
import json
import requests
import base64

# Streamlit Page Config
st.set_page_config(
    page_title="Rogee Financial Command Center",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Adaptive CSS for Light & Dark Mode
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

    .priority-banner { background-color: #FEF2F2; border: 1px solid #FECACA; border-left: 5px solid #EF4444; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; color: #991B1B !important; }
    .priority-banner * { color: #991B1B !important; }
    @media (prefers-color-scheme: dark) {
        .priority-banner { background-color: #450A0A !important; border-color: #7F1D1D !important; border-left: 5px solid #EF4444 !important; color: #FECACA !important; }
        .priority-banner * { color: #FECACA !important; }
    }

    .income-card { background-color: #F0FDF4; border: 1px solid #BBF7D0; border-left: 5px solid #22C55E; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; color: #166534 !important; }
    .income-card * { color: #166534 !important; }
    @media (prefers-color-scheme: dark) {
        .income-card { background-color: #052E16 !important; border-color: #14532D !important; border-left: 5px solid #22C55E !important; color: #BBF7D0 !important; }
        .income-card * { color: #BBF7D0 !important; }
    }

    .rate-card { background-color: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #3B82F6; padding: 8px 12px; border-radius: 6px; margin-bottom: 12px; font-size: 0.85rem; color: #1E40AF !important; }
    .rate-card * { color: #1E40AF !important; }
    @media (prefers-color-scheme: dark) {
        .rate-card { background-color: #1E3A8A !important; border-color: #1D4ED8 !important; border-left: 4px solid #60A5FA !important; color: #BFDBFE !important; }
        .rate-card * { color: #BFDBFE !important; }
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

# User Account Profiles
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
        "data_file": "expenses_ferdie.csv",
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

# Live Currency FX Fetcher
@st.cache_data(ttl=3600)
def fetch_live_rates():
    base_rates = {
        "USD": 1.0, "BHD": 0.377, "PHP": 58.50, "EUR": 0.92, "GBP": 0.78,
        "JPY": 152.0, "CHF": 0.865, "AUD": 1.51, "CAD": 1.38, "NZD": 1.66
    }
    try:
        api_u = base64.b64decode("aHR0cHM6Ly9vcGVuLmVyLWFwaS5jb20vdjYvbGF0ZXN0L1VTRA==").decode("utf-8")
        r = requests.get(api_u, timeout=4)
        if r.status_code == 200:
            data = r.json().get("rates", {})
            needed = ["USD", "BHD", "PHP", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"]
            if "BHD" in data and "PHP" in data:
                fetched = {k: float(data[k]) for k in needed if k in data}
                for k, v in base_rates.items():
                    if k not in fetched:
                        fetched[k] = v
                return fetched, True, datetime.now().strftime("%Y-%m-%d %H:%M")
    except Exception:
        pass
    return base_rates, False, datetime.now().strftime("%Y-%m-%d %H:%M (Benchmark)")

rates_dict, is_live_rates, last_rate_update = fetch_live_rates()

# Authentication Gate
def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = None

    if not st.session_state["authenticated"]:
        st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🔐 Rogee&apos;s Financial Command Center</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B7280;'>Select profile and enter your private access key.</p>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            with st.form("login_form"):
                selected_user = st.selectbox("Select Account Profile", list(USER_PROFILES.keys()))
                entered_pass = st.text_input("Enter Access Key", type="password", placeholder="••••••••")
                login_btn = st.form_submit_button("🔓 Unlock Dashboard", use_container_width=True)

                if login_btn:
                    user_info = USER_PROFILES[selected_user]
                    sec_obj = getattr(st, "secrets", {})
                    expected_pass = sec_obj.get(user_info["sec_key"], user_info["def_key"])

                    if entered_pass == expected_pass:
                        st.session_state["authenticated"] = True
                        st.session_state["current_user"] = selected_user
                        st.success(f"Welcome back, {selected_user}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid access key. Please try again.")
        return False
    return True

if not check_authentication():
    st.stop()

current_user = st.session_state["current_user"]
user_config = USER_PROFILES[current_user]
DATA_FILE = user_config["data_file"]
CONFIG_FILE = user_config["config_file"]
INVEST_FILE = user_config["invest_file"]

# Load/Save Config Settings
def load_user_config():
    default_cfg = {
        "income_salary": 1500.0,
        "income_business": 0.0,
        "income_sidelines": 0.0,
        "income_other": 0.0,
        "fixed_priority": 300.0,
        "debts_pct": 15,
        "needs_pct": 45,
        "wants_pct": 20,
        "savings_pct": 20,
        "currency_symbol": "BD ",
        "display_currency": "BHD"
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                saved_cfg = json.load(f)
                default_cfg.update(saved_cfg)
        except Exception:
            pass
    return default_cfg

def save_user_config(cfg):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=4)
    except Exception:
        pass

user_cfg = load_user_config()

# Load/Save Expenses Data
def load_data(file_path):
    cols = [
        "Item #", "Date", "Main Category", "Sub Category", "Merchant/Description",
        "Billed Amount", "Actual Paid", "Currency", "Pending Due", "% Paid", "% Remaining",
        "Equivalent (BHD / PHP / USD)", "Status", "Payment Method", "Billed (BHD)", "Paid (BHD)"
    ]
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"]).dt.date
            for c in cols:
                if c not in df.columns:
                    df[c] = ""
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=cols)

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

df_expenses = load_data(DATA_FILE)

# Sidebar Budget Settings
st.sidebar.title(f"⚙️ Budget Settings ({current_user})")

salary_bhd = st.sidebar.number_input("Primary Salary (BHD)", min_value=0.0, value=float(user_cfg["income_salary"]), step=50.0)
business_bhd = st.sidebar.number_input("Business Income (BHD)", min_value=0.0, value=float(user_cfg["income_business"]), step=50.0)
sidelines_bhd = st.sidebar.number_input("Sidelines / Freelance (BHD)", min_value=0.0, value=float(user_cfg["income_sidelines"]), step=50.0)
other_income_bhd = st.sidebar.number_input("Other Income (BHD)", min_value=0.0, value=float(user_cfg["income_other"]), step=50.0)

total_income_bhd = salary_bhd + business_bhd + sidelines_bhd + other_income_bhd
st.sidebar.info(f"💵 **Total Monthly Income:** BD {total_income_bhd:,.2f}")

st.sidebar.markdown("---")
fixed_priority_bhd = st.sidebar.number_input("100% Priority & Mandatory Obligations (BHD)", min_value=0.0, value=float(user_cfg["fixed_priority"]), step=20.0)
net_bhd_for_budget = max(0.0, total_income_bhd - fixed_priority_bhd)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 4-Category Net Allocation (%)")
debts_pct = st.sidebar.slider("Debts & Credits Target %", 0, 100, int(user_cfg["debts_pct"]))
needs_pct = st.sidebar.slider("Needs Target % (Essentials)", 0, 100, int(user_cfg["needs_pct"]))
wants_pct = st.sidebar.slider("Wants Target % (Lifestyle)", 0, 100, int(user_cfg["wants_pct"]))
savings_pct = st.sidebar.slider("Savings & Investments %", 0, 100, int(user_cfg["savings_pct"]))

tot_pct = debts_pct + needs_pct + wants_pct + savings_pct
framework_title = f"{debts_pct}/{needs_pct}/{wants_pct}/{savings_pct} Framework"
if tot_pct != 100:
    st.sidebar.warning(f"Allocation total is {tot_pct}%. Adjust to equal 100%.")

display_curr = st.sidebar.selectbox("Display Currency", ["BHD", "PHP", "USD"], index=0)

# Save settings
user_cfg.update({
    "income_salary": salary_bhd,
    "income_business": business_bhd,
    "income_sidelines": sidelines_bhd,
    "income_other": other_income_bhd,
    "fixed_priority": fixed_priority_bhd,
    "debts_pct": debts_pct,
    "needs_pct": needs_pct,
    "wants_pct": wants_pct,
    "savings_pct": savings_pct,
    "display_currency": display_curr
})
save_user_config(user_cfg)

# Rates conversion
bhd_rate = rates_dict.get("BHD", 0.377)
php_rate = rates_dict.get("PHP", 58.50)
usd_rate = rates_dict.get("USD", 1.0)

bhd_to_php = php_rate / bhd_rate if bhd_rate > 0 else 154.50
bhd_to_usd = usd_rate / bhd_rate if bhd_rate > 0 else 2.65

if display_curr == "BHD":
    curr_symbol = "BD "
    rate_mult = 1.0
elif display_curr == "PHP":
    curr_symbol = "₱"
    rate_mult = bhd_to_php
else:
    curr_symbol = "$"
    rate_mult = bhd_to_usd

# Calculations
debts_target_bhd = net_bhd_for_budget * (debts_pct / 100.0)
needs_target_bhd = net_bhd_for_budget * (needs_pct / 100.0)
wants_target_bhd = net_bhd_for_budget * (wants_pct / 100.0)
savings_target_bhd = net_bhd_for_budget * (savings_pct / 100.0)

disp_total_income = total_income_bhd * rate_mult
disp_fixed = fixed_priority_bhd * rate_mult
disp_net = net_bhd_for_budget * rate_mult

# Header & Clocks
utc_now = datetime.now(timezone.utc)
bh_time = utc_now + timedelta(hours=3)
ph_time = utc_now + timedelta(hours=8)

st.markdown('<div class="main-header">💰 Rogee&apos;s Financial Command Center</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Personal Multi-Currency Finance Tracker based on the <b>{framework_title}</b></div>', unsafe_allow_html=True)

st.markdown(
    f'<div class="time-badge">'
    f'🇧🇭 <b>Bahrain:</b> {bh_time.strftime("%d %b %Y, %I:%M %p")} &nbsp;|&nbsp; '
    f'🇵🇭 <b>Philippines:</b> {ph_time.strftime("%d %b %Y, %I:%M %p")} &nbsp;|&nbsp; '
    f'👤 <b>Account:</b> {current_user}'
    f'</div>',
    unsafe_allow_html=True
)

rate_mode_str = "Live Auto-Updated" if is_live_rates else "Benchmark Rates"
st.markdown(
    f'<div class="rate-card">🌐 <b>Live FX Engine ({rate_mode_str}):</b> '
    f'<b>1 BHD</b> = <b>₱{bhd_to_php:,.2f} PHP</b> | '
    f'<b>1 BHD</b> = <b>${bhd_to_usd:,.2f} USD</b> | '
    f'<b>1 USD</b> = <b>₱{(bhd_to_php/bhd_to_usd):,.2f} PHP</b>'
    f'<span style="float: right; color: #6B7280; font-size: 0.85rem;">Updated: {last_rate_update}</span></div>',
    unsafe_allow_html=True
)

# App Tabs
tab_dash, tab_add, tab_history, tab_forex, tab_invest, tab_reports, tab_guide = st.tabs([
    "📈 Dashboard & Analytics",
    "➕ Record Expense",
    "📜 Transaction History",
    "💱 Live Forex Engine",
    "📊 MT5 & COL Investments",
    "📥 Download Reports",
    "📘 User Guide"
])

# Actual Expenses Summaries
if not df_expenses.empty:
    if "Paid (BHD)" in df_expenses.columns and df_expenses["Paid (BHD)"].notna().any():
        actual_priority_bhd = df_expenses[df_expenses["Main Category"].str.contains("100% Priority", na=False)]["Paid (BHD)"].sum()
        actual_debts_bhd = df_expenses[df_expenses["Main Category"].str.contains("Debts", na=False)]["Paid (BHD)"].sum()
        actual_needs_bhd = df_expenses[df_expenses["Main Category"].str.contains("Needs", na=False)]["Paid (BHD)"].sum()
        actual_wants_bhd = df_expenses[df_expenses["Main Category"].str.contains("Wants", na=False)]["Paid (BHD)"].sum()
        actual_savings_bhd = df_expenses[df_expenses["Main Category"].str.contains("Savings", na=False)]["Paid (BHD)"].sum()
    elif "Amount (BHD)" in df_expenses.columns:
        actual_priority_bhd = df_expenses[df_expenses["Main Category"].str.contains("100% Priority", na=False)]["Amount (BHD)"].sum()
        actual_debts_bhd = df_expenses[df_expenses["Main Category"].str.contains("Debts", na=False)]["Amount (BHD)"].sum()
        actual_needs_bhd = df_expenses[df_expenses["Main Category"].str.contains("Needs", na=False)]["Amount (BHD)"].sum()
        actual_wants_bhd = df_expenses[df_expenses["Main Category"].str.contains("Wants", na=False)]["Amount (BHD)"].sum()
        actual_savings_bhd = df_expenses[df_expenses["Main Category"].str.contains("Savings", na=False)]["Amount (BHD)"].sum()
    else:
        actual_priority_bhd, actual_debts_bhd, actual_needs_bhd, actual_wants_bhd, actual_savings_bhd = 0.0, 0.0, 0.0, 0.0, 0.0
else:
    actual_priority_bhd, actual_debts_bhd, actual_needs_bhd, actual_wants_bhd, actual_savings_bhd = 0.0, 0.0, 0.0, 0.0, 0.0

total_spent_bhd = actual_priority_bhd + actual_debts_bhd + actual_needs_bhd + actual_wants_bhd + actual_savings_bhd
remaining_cash_bhd = total_income_bhd - total_spent_bhd

actual_priority_disp = actual_priority_bhd * rate_mult
actual_debts_disp = actual_debts_bhd * rate_mult
actual_needs_disp = actual_needs_bhd * rate_mult
actual_wants_disp = actual_wants_bhd * rate_mult
actual_savings_disp = actual_savings_bhd * rate_mult

total_spent_disp = total_spent_bhd * rate_mult
remaining_cash_disp = remaining_cash_bhd * rate_mult

# TAB 1: DASHBOARD
with tab_dash:
    st.markdown('<div class="income-card">', unsafe_allow_html=True)
    st.subheader("💵 Total Monthly Income Breakdown")
    c_inc1, c_inc2, c_inc3, c_inc4 = st.columns(4)
    c_inc1.metric("Primary Salary", f"BD {salary_bhd:,.2f}")
    c_inc2.metric("Business Income", f"BD {business_bhd:,.2f}")
    c_inc3.metric("Sidelines / Freelance", f"BD {sidelines_bhd:,.2f}")
    c_inc4.metric("Other Income", f"BD {other_income_bhd:,.2f}")
    st.write(f"**Total Combined Income:** `{curr_symbol}{disp_total_income:,.2f}` (BD {total_income_bhd:,.2f} | ₱{total_income_bhd*bhd_to_php:,.2f} | ${total_income_bhd*bhd_to_usd:,.2f})")
    st.markdown('</div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Income", f"{curr_symbol}{disp_total_income:,.2f}")
    m2.metric("100% Priority Target", f"{curr_symbol}{disp_fixed:,.2f}")
    m3.metric("Total Spent To Date", f"{curr_symbol}{total_spent_disp:,.2f}", delta=f"-{curr_symbol}{total_spent_disp:,.2f}", delta_color="inverse")
    m4.metric("Remaining Net Cash", f"{curr_symbol}{remaining_cash_disp:,.2f}", delta=f"{curr_symbol}{remaining_cash_disp:,.2f}")

    st.markdown("---")
    st.markdown('<div class="priority-banner">', unsafe_allow_html=True)
    st.subheader("🚨 100% Mandatory Obligations Progress")
    p_col1, p_col2 = st.columns([2, 1])
    with p_col1:
        priority_pct = min(100.0, (actual_priority_bhd / fixed_priority_bhd * 100.0)) if fixed_priority_bhd > 0 else 0.0
        st.progress(priority_pct / 100.0)
        st.write(f"Paid **{curr_symbol}{actual_priority_disp:,.2f}** of **{curr_symbol}{disp_fixed:,.2f}** mandatory obligations ({priority_pct:.1f}% paid).")
    with p_col2:
        rem_priority_disp = max(0.0, disp_fixed - actual_priority_disp)
        st.metric("Pending Priority Payments", f"{curr_symbol}{rem_priority_disp:,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader(f"📊 {framework_title} Net Allocation Breakdown")

    cat_table_data = [
        {"Category": f"Debts & Credits ({debts_pct}%)", "Target Allocation": f"{debts_pct}%", "Target Amount": debts_target_bhd * rate_mult, "Actual Paid": actual_debts_disp, "Difference": (debts_target_bhd * rate_mult) - actual_debts_disp, "Status": "On Track" if actual_debts_disp <= debts_target_bhd * rate_mult else "Over Target"},
        {"Category": f"Needs ({needs_pct}%)", "Target Allocation": f"{needs_pct}%", "Target Amount": needs_target_bhd * rate_mult, "Actual Paid": actual_needs_disp, "Difference": (needs_target_bhd * rate_mult) - actual_needs_disp, "Status": "On Track" if actual_needs_disp <= needs_target_bhd * rate_mult else "Over Target"},
        {"Category": f"Wants ({wants_pct}%)", "Target Allocation": f"{wants_pct}%", "Target Amount": wants_target_bhd * rate_mult, "Actual Paid": actual_wants_disp, "Difference": (wants_target_bhd * rate_mult) - actual_wants_disp, "Status": "On Track" if actual_wants_disp <= wants_target_bhd * rate_mult else "Over Target"},
        {"Category": f"Savings & Investments ({savings_pct}%)", "Target Allocation": f"{savings_pct}%", "Target Amount": savings_target_bhd * rate_mult, "Actual Paid": actual_savings_disp, "Difference": actual_savings_disp - (savings_target_bhd * rate_mult), "Status": "Goal Met" if actual_savings_disp >= savings_target_bhd * rate_mult else "Under Goal"}
    ]
    df_cat_summary = pd.DataFrame(cat_table_data)
    st.dataframe(
        df_cat_summary.style.format({
            "Target Amount": f"{curr_symbol}{{:,.2f}}",
            "Actual Paid": f"{curr_symbol}{{:,.2f}}",
            "Difference": f"{curr_symbol}{{:,.2f}}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    col_ch1, col_ch2 = st.columns(2)

    with col_ch1:
        st.subheader("Target vs. Actual Spending")
        chart_df = pd.DataFrame({
            "Category": ["Debts", "Needs", "Wants", "Savings"],
            "Target": [debts_target_bhd * rate_mult, needs_target_bhd * rate_mult, wants_target_bhd * rate_mult, savings_target_bhd * rate_mult],
            "Actual": [actual_debts_disp, actual_needs_disp, actual_wants_disp, actual_savings_disp]
        })
        fig_bar = go.Figure(data=[
            go.Bar(name='Target', x=chart_df['Category'], y=chart_df['Target'], marker_color='#93C5FD'),
            go.Bar(name='Actual', x=chart_df['Category'], y=chart_df['Actual'], marker_color='#1D4ED8')
        ])
        fig_bar.update_layout(barmode='group', margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_ch2:
        st.subheader("Actual Spending Share")
        if total_spent_disp > 0:
            fig_pie = px.pie(
                values=[actual_priority_disp, actual_debts_disp, actual_needs_disp, actual_wants_disp, actual_savings_disp],
                names=["100% Priority", "Debts", "Needs", "Wants", "Savings"],
                color_discrete_sequence=['#EF4444', '#8B5CF6', '#2563EB', '#F59E0B', '#10B981'],
                hole=0.45
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expense records logged yet.")

# TAB 2: RECORD EXPENSE
with tab_add:
    st.subheader(f"➕ Record a New Payment / Expense ({current_user})")

    with st.form("add_expense_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)

        with col_a:
            exp_date = st.date_input("Date", value=datetime.today())
            
            cat_options = [
                "100% Priority & People to Pay",
                f"Debts & Credits ({debts_pct}%)",
                f"Needs ({needs_pct}%)",
                f"Wants ({wants_pct}%)",
                f"Savings & Investments ({savings_pct}%)"
            ]
            main_cat = st.selectbox("Category", cat_options)

            if "100%" in main_cat:
                sub_cats = ["People to Pay (Household Helper / Staff)", "Family Support & Remittance (100%)", "Direct Mandatory Loan / Debt", "Fixed Mandatory Utility / Bill"]
            elif "Debts" in main_cat:
                sub_cats = ["Credit Card Payment", "Personal Bank Loan", "Auto / Car Loan", "Housing Mortgage / Loan", "Friend / Personal Borrowed Repayment"]
            elif "Needs" in main_cat:
                sub_cats = ["Housing / Rent", "Utilities & Bills", "Groceries & Supplies", "Transportation / Fuel", "Healthcare / Insurance", "Minimum Debt Payments"]
            elif "Wants" in main_cat:
                sub_cats = ["Dining Out & Coffee", "Entertainment & Streaming", "Shopping & Apparel", "Hobbies & Travel", "Subscriptions", "Miscellaneous"]
            else:
                sub_cats = ["Emergency Fund", "COL Stock Investments (PH)", "MT5 Forex & Trading Deposit", "Index Funds / Mutual Funds", "Pension / Retirement", "Major Goal Savings"]

            sub_cat = st.selectbox("Sub-Category", sub_cats)
            merchant = st.text_input("Merchant / Description / Payee", placeholder="e.g. Landlord, Helper Salary, Credit Card Bill")

        with col_b:
            input_currency = st.selectbox("Payment Currency", ["BHD", "PHP", "USD"], index=0)
            billed_amount = st.number_input(f"Billed / Planned Amount ({input_currency})", min_value=0.01, step=5.0, value=25.0)
            
            status_choice = st.selectbox("Payment Status", ["Paid", "Pending Payment", "Partially Paid", "Not Paid"], index=0)
            
            default_paid = billed_amount if status_choice == "Paid" else (0.0 if status_choice in ["Pending Payment", "Not Paid"] else billed_amount * 0.5)
            actual_paid = st.number_input(f"Actual Amount Paid ({input_currency})", min_value=0.0, step=5.0, value=float(default_paid))
            
            payment_method = st.selectbox("Payment Method", ["Benefit Pay", "Remittance", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])

        submit_btn = st.form_submit_button("💾 Save Payment Record", use_container_width=True)

        if submit_btn:
            if input_currency == "BHD":
                billed_bhd = billed_amount
                paid_bhd = actual_paid
            elif input_currency == "PHP":
                billed_bhd = billed_amount / bhd_to_php
                paid_bhd = actual_paid / bhd_to_php
            else:
                billed_bhd = billed_amount / bhd_to_usd
                paid_bhd = actual_paid / bhd_to_usd

            pending_due_curr = max(0.0, billed_amount - actual_paid)
            pending_bhd = max(0.0, billed_bhd - paid_bhd)
            
            pct_paid = min(100.0, (actual_paid / billed_amount * 100.0)) if billed_amount > 0 else 100.0
            pct_rem = max(0.0, 100.0 - pct_paid)

            equiv_str = f"BD {billed_bhd:,.2f} (₱{billed_bhd*bhd_to_php:,.2f} | ${billed_bhd*bhd_to_usd:,.2f})"

            new_row = pd.DataFrame([{
                "Item #": len(df_expenses) + 1,
                "Date": exp_date,
                "Main Category": main_cat,
                "Sub Category": sub_cat,
                "Merchant/Description": merchant if merchant else "Unspecified",
                "Billed Amount": billed_amount,
                "Actual Paid": actual_paid,
                "Currency": input_currency,
                "Pending Due": pending_due_curr,
                "% Paid": f"{pct_paid:.1f}%",
                "% Remaining": f"{pct_rem:.1f}%",
                "Equivalent (BHD / PHP / USD)": equiv_str,
                "Status": status_choice,
                "Payment Method": payment_method,
                "Billed (BHD)": billed_bhd,
                "Paid (BHD)": paid_bhd
            }])

            df_expenses = pd.concat([df_expenses, new_row], ignore_index=True)
            save_data(df_expenses, DATA_FILE)
            st.success(f"Recorded record for {merchant if merchant else sub_cat} ({status_choice})!")
            st.rerun()

# TAB 3: TRANSACTION HISTORY
with tab_history:
    st.subheader(f"📜 Recorded Transaction History ({current_user})")

    if not df_expenses.empty:
        # Define Standard Category Grouping Order
        cat_order = {
            "100% Priority & People to Pay": 1,
            "Debts": 2,
            "Needs": 3,
            "Wants": 4,
            "Savings": 5
        }

        def get_cat_rank(cat_str):
            cat_str = str(cat_str)
            for k, rank in cat_order.items():
                if k in cat_str:
                    return rank
            return 99

        # Process and re-sort dataframe categorically and chronologically
        df_processed = df_expenses.copy()
        df_processed["Date"] = pd.to_datetime(df_processed["Date"]).dt.date
        df_processed["Cat_Rank"] = df_processed["Main Category"].apply(get_cat_rank)
        
        # Sort by Category Rank then Date
        df_sorted = df_processed.sort_values(by=["Cat_Rank", "Date"], ascending=[True, True]).reset_index(drop=True)
        df_sorted["Item #"] = range(1, len(df_sorted) + 1)
        df_sorted = df_sorted.drop(columns=["Cat_Rank"], errors="ignore")

        # Recalculate linked columns dynamically
        recalc_rows = []
        for idx, row in df_sorted.iterrows():
            c_curr = str(row.get("Currency", "BHD")).upper()
            c_billed = float(row.get("Billed Amount", 0.0)) if pd.notna(row.get("Billed Amount")) else 0.0
            c_paid = float(row.get("Actual Paid", 0.0)) if pd.notna(row.get("Actual Paid")) else 0.0
            
            if c_curr == "BHD":
                b_bhd = c_billed
                p_bhd = c_paid
            elif c_curr == "PHP":
                b_bhd = c_billed / bhd_to_php
                p_bhd = c_paid / bhd_to_php
            else:
                b_bhd = c_billed / bhd_to_usd
                p_bhd = c_paid / bhd_to_usd

            p_due_curr = max(0.0, c_billed - c_paid)
            p_pct_paid = min(100.0, (c_paid / c_billed * 100.0)) if c_billed > 0 else 100.0
            p_pct_rem = max(0.0, 100.0 - p_pct_paid)

            row["Billed (BHD)"] = b_bhd
            row["Paid (BHD)"] = p_bhd
            row["Pending Due"] = p_due_curr
            row["% Paid"] = f"{p_pct_paid:.1f}%"
            row["% Remaining"] = f"{p_pct_rem:.1f}%"
            row["Equivalent (BHD / PHP / USD)"] = f"BD {b_bhd:,.2f} (₱{b_bhd*bhd_to_php:,.2f} | ${b_bhd*bhd_to_usd:,.2f})"
            recalc_rows.append(row)

        df_sorted = pd.DataFrame(recalc_rows)

        # Desired Display Column Order (Billed Amount right after Merchant/Description)
        display_cols = [
            "Item #", "Date", "Main Category", "Sub Category", "Merchant/Description",
            "Billed Amount", "Actual Paid", "Currency", "Pending Due", "% Paid", "% Remaining",
            "Equivalent (BHD / PHP / USD)", "Status", "Payment Method"
        ]
        
        # Ensure all display columns exist
        for col_name in display_cols:
            if col_name not in df_sorted.columns:
                df_sorted[col_name] = ""

        df_display = df_sorted[display_cols].copy()

        st.caption("✏️ **Editable Columns:** Double-click Date, Categories, Description, Billed Amount, Actual Paid, Currency, Status, or Payment Method to edit. Other columns link and update automatically!")

        # Data Editor Table
        edited_df = st.data_editor(
            df_display,
            num_rows="dynamic",
            use_container_width=True,
            key=f"expense_editor_{current_user}",
            column_config={
                "Item #": st.column_config.NumberColumn("Item #", disabled=True),
                "Pending Due": st.column_config.NumberColumn("Pending Due", disabled=True),
                "% Paid": st.column_config.TextColumn("% Paid", disabled=True),
                "% Remaining": st.column_config.TextColumn("% Remaining", disabled=True),
                "Equivalent (BHD / PHP / USD)": st.column_config.TextColumn("Equivalent (BHD / PHP / USD)", disabled=True),
                "Status": st.column_config.SelectboxColumn("Status", options=["Paid", "Pending Payment", "Partially Paid", "Not Paid"]),
                "Currency": st.column_config.SelectboxColumn("Currency", options=["BHD", "PHP", "USD"]),
                "Payment Method": st.column_config.SelectboxColumn("Payment Method", options=["Benefit Pay", "Remittance", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])
            }
        )

        st.markdown("---")
        col_hist1, col_hist2 = st.columns(2)
        with col_hist1:
            if st.button("💾 Save Ledger Changes", type="primary", use_container_width=True):
                # Preserve BHD calculated columns on save
                save_data(df_sorted, DATA_FILE)
                st.success("Ledger changes saved successfully!")
                st.rerun()

        with col_hist2:
            if st.button("🗑️ Clear Entire History", use_container_width=True):
                if os.path.exists(DATA_FILE):
                    os.remove(DATA_FILE)
                st.success("All transaction logs cleared!")
                st.rerun()

        st.markdown("---")
        st.subheader("💰 Total Outstanding & Payment Summary Ledger")

        tot_billed_bhd = df_sorted["Billed (BHD)"].sum()
        tot_paid_bhd = df_sorted["Paid (BHD)"].sum()
        tot_pending_bhd = max(0.0, tot_billed_bhd - tot_paid_bhd)

        s_col1, s_col2, s_col3 = st.columns(3)

        with s_col1:
            st.markdown(
                f'<div class="rate-card">'
                f'📋 <b>Total Billed / Needed:</b><br>'
                f'• <b>BD:</b> BD {tot_billed_bhd:,.2f}<br>'
                f'• <b>PHP:</b> ₱{(tot_billed_bhd * bhd_to_php):,.2f}<br>'
                f'• <b>USD:</b> ${(tot_billed_bhd * bhd_to_usd):,.2f}'
                f'</div>',
                unsafe_allow_html=True
            )

        with s_col2:
            st.markdown(
                f'<div class="income-card">'
                f'✅ <b>Total Amount Paid:</b><br>'
                f'• <b>BD:</b> BD {tot_paid_bhd:,.2f}<br>'
                f'• <b>PHP:</b> ₱{(tot_paid_bhd * bhd_to_php):,.2f}<br>'
                f'• <b>USD:</b> ${(tot_paid_bhd * bhd_to_usd):,.2f}'
                f'</div>',
                unsafe_allow_html=True
            )

        with s_col3:
            st.markdown(
                f'<div class="priority-banner">'
                f'⏳ <b>Total Remaining Outstanding:</b><br>'
                f'• <b>BD:</b> BD {tot_pending_bhd:,.2f}<br>'
                f'• <b>PHP:</b> ₱{(tot_pending_bhd * bhd_to_php):,.2f}<br>'
                f'• <b>USD:</b> ${(tot_pending_bhd * bhd_to_usd):,.2f}'
                f'</div>',
                unsafe_allow_html=True
            )

    else:
        st.info("No transaction history found. Start recording payments in the 'Record Expense' tab!")

# TAB 4: LIVE FOREX ENGINE
with tab_forex:
    st.subheader("💱 Live Multi-Currency Cross Rate Engine")

    fx_col1, fx_col2 = st.columns(2)

    with fx_col1:
        st.markdown("#### Instant Currency Pair Calculator")
        calc_amt = st.number_input("Amount to Convert", min_value=1.0, value=100.0, step=10.0)
        
        fx_list = ["BHD", "PHP", "USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"]
        pair_from = st.selectbox("From Currency", fx_list, index=0)
        pair_to = st.selectbox("To Currency", fx_list, index=1)

        rate_from_usd = rates_dict.get(pair_from, 1.0)
        rate_to_usd = rates_dict.get(pair_to, 1.0)

        cross_rate = rate_to_usd / rate_from_usd if rate_from_usd > 0 else 1.0
        converted_val = calc_amt * cross_rate

        st.success(f"### {calc_amt:,.2f} {pair_from} = **{converted_val:,.2f} {pair_to}**")
        st.info(f"💡 **Exchange Rate:** 1 {pair_from} = {cross_rate:,.4f} {pair_to}")

    with fx_col2:
        st.markdown("#### Live Major & Cross Pairs Ticker")
        st.markdown(
            f"• **1 BHD → PHP:** ₱{(rates_dict.get('PHP', 58.5)/rates_dict.get('BHD', 0.377)):,.2f}<br>"
            f"• **1 BHD → USD:** ${(rates_dict.get('USD', 1.0)/rates_dict.get('BHD', 0.377)):,.2f}<br>"
            f"• **1 USD → PHP:** ₱{(rates_dict.get('PHP', 58.5)/rates_dict.get('USD', 1.0)):,.2f}<br>"
            f"• **1 USD → CHF (USDCHF):** {rates_dict.get('CHF', 0.865):,.4f}<br>"
            f"• **1 AUD → CAD (AUDCAD):** {(rates_dict.get('CAD', 1.38)/rates_dict.get('AUD', 1.51)):,.4f}<br>"
            f"• **1 NZD → USD (NZDUSD):** {(rates_dict.get('USD', 1.0)/rates_dict.get('NZD', 1.66)):,.4f}",
            unsafe_allow_html=True
        )

        if st.button("🔄 Force Refresh Live FX Rates"):
            st.cache_data.clear()
            st.rerun()

# TAB 5: MT5 & COL INVESTMENTS
with tab_invest:
    st.subheader("📊 MT5 Forex & COL Financial Portfolio Manager")

    st.markdown("#### 🧮 Live MetaTrader 5 Trading Calculators")
    calc_t1, calc_t2 = st.columns(2)

    with calc_t1:
        st.markdown("##### 📍 Pip Value Calculator")
        pip_pair = st.selectbox("Trading Pair", ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD (Gold)", "USDCHF", "AUDUSD"], index=0)
        lots = st.number_input("Lot Volume", min_value=0.01, step=0.01, value=0.10)
        account_curr = st.selectbox("Account Base Currency", ["USD", "BHD", "PHP"], index=0)

        pip_val_usd = (lots * 100000 * 0.0001) if "JPY" not in pip_pair else (lots * 100000 * 0.01 / 152.0)
        if "XAU" in pip_pair:
            pip_val_usd = lots * 100 * 0.10

        if account_curr == "USD":
            disp_pip = pip_val_usd
            c_sym = "$"
        elif account_curr == "BHD":
            disp_pip = pip_val_usd * bhd_rate
            c_sym = "BD "
        else:
            disp_pip = pip_val_usd * php_rate
            c_sym = "₱"

        st.success(f"**Pip Value ({lots} Lots):** `{c_sym}{disp_pip:,.2f}` per pip")

    with calc_t2:
        st.markdown("##### 🛡️ Required Margin Calculator")
        m_pair = st.selectbox("Asset Pair", ["Forex Majors (1:500)", "Gold / Metals (1:200)", "Indices / Crypto (1:100)"], index=0)
        m_lots = st.number_input("Trade Size (Lots)", min_value=0.01, step=0.01, value=0.10)
        leverage = st.selectbox("Account Leverage", [100, 200, 500, 1000], index=2)

        notional_usd = m_lots * 100000
        req_margin_usd = notional_usd / leverage
        st.success(f"**Required Margin:** `${req_margin_usd:,.2f} USD` (BD {req_margin_usd*bhd_rate:,.2f})")

    st.markdown("---")
    st.markdown("#### 📜 Asset & Stock Holdings Ledger")

    df_invest = load_data(INVEST_FILE)

    with st.form("add_investment_form", clear_on_submit=True):
        inv_c1, inv_c2 = st.columns(2)
        with inv_c1:
            inv_type = st.selectbox("Asset Class", ["COL Financial (PH Stocks)", "MetaTrader 5 (Forex / Gold)", "Crypto / Other"])
            ticker = st.text_input("Ticker Symbol", placeholder="e.g. ALI, BDO, EURUSD, XAUUSD")
            platform = st.text_input("Broker Platform", placeholder="e.g. COL Financial, Exness, IC Markets")
        with inv_c2:
            shares = st.number_input("Shares / Lots Owned", min_value=0.01, value=100.0)
            buy_price = st.number_input("Avg Purchase Price", min_value=0.0001, value=10.0)
            curr_price = st.number_input("Current Market Price", min_value=0.0001, value=12.0)

        inv_submit = st.form_submit_button("➕ Save Asset Record", use_container_width=True)
        if inv_submit:
            new_inv = pd.DataFrame([{
                "Type": inv_type,
                "Symbol/Ticker": ticker if ticker else "Unspecified",
                "Platform": platform if platform else "General",
                "Shares/Lots": shares,
                "Avg Buy Price": buy_price,
                "Current Price": curr_price,
                "Notes": f"Logged on {datetime.today().strftime('%Y-%m-%d')}"
            }])
            df_invest = pd.concat([df_invest, new_inv], ignore_index=True)
            save_data(df_invest, INVEST_FILE)
            st.success(f"Added {ticker} to holdings!")
            st.rerun()

    if not df_invest.empty and "Shares/Lots" in df_invest.columns:
        df_invest["Total Value"] = df_invest["Shares/Lots"] * df_invest["Current Price"]
        df_invest["Total Cost"] = df_invest["Shares/Lots"] * df_invest["Avg Buy Price"]
        df_invest["P&L ($)"] = df_invest["Total Value"] - df_invest["Total Cost"]

        st.dataframe(df_invest, use_container_width=True, hide_index=True)
        tot_val = df_invest["Total Value"].sum()
        tot_pnl = df_invest["P&L ($)"].sum()

        st.metric("Total Portfolio Equity", f"${tot_val:,.2f}", delta=f"${tot_pnl:,.2f} Total P&L")

# TAB 6: DOWNLOAD REPORTS
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
        st.markdown("#### 📜 Executive Summary Report (.TXT)")
        rep_date = datetime.today().strftime("%Y-%m-%d")
        total_exp_bhd = df_expenses["Paid (BHD)"].sum() if ("Paid (BHD)" in df_expenses.columns and not df_expenses.empty) else 0.0

        report_content = f"""==================================================
ROGEE FINANCIAL COMMAND CENTER - EXECUTIVE REPORT
==================================================
User Profile   : {current_user}
Report Date    : {rep_date}
Bahrain Time   : {bh_time.strftime('%Y-%m-%d %I:%M %p')}
Philippine Time: {ph_time.strftime('%Y-%m-%d %I:%M %p')}
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
   - Equivalent in PHP   : ₱{(total_income_bhd * bhd_to_php):,.2f}
   - Equivalent in USD   : ${(total_income_bhd * bhd_to_usd):,.2f}

--------------------------------------------------
2. EXPENSES BREAKDOWN BY CATEGORY
--------------------------------------------------
- Mandatory 100% Payments: BD {actual_priority_bhd:,.2f}
- Debts ({debts_pct}% Target)     : BD {actual_debts_bhd:,.2f}
- Needs ({needs_pct}% Target)     : BD {actual_needs_bhd:,.2f}
- Wants ({wants_pct}% Target)     : BD {actual_wants_bhd:,.2f}
- Savings ({savings_pct}% Target) : BD {actual_savings_bhd:,.2f}
--------------------------------------------------
GRAND TOTAL EXPENSES PAID: BD {total_exp_bhd:,.2f}
NET REMAINING CASH       : BD {(total_income_bhd - total_exp_bhd):,.2f}
==================================================
"""
        st.download_button(
            label="📥 Download Executive Summary (.TXT)",
            data=report_content,
            file_name=f"financial_summary_{current_user.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# TAB 7: USER GUIDE
with tab_guide:
    st.subheader("📘 Security & Configuration Guide")
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
