import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import os
import json
import requests
import base64

# Page Config
st.set_page_config(
    page_title="Rogee Financial Command Center",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling with Dark Mode Adaptive Contrast
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

    .overbudget-card { background-color: #FEF2F2; border: 1px solid #FCA5A5; border-left: 5px solid #DC2626; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; color: #991B1B !important; font-weight: 600; }
    @media (prefers-color-scheme: dark) {
        .overbudget-card { background-color: #450A0A !important; border-color: #991B1B !important; border-left: 5px solid #EF4444 !important; color: #FCA5A5 !important; }
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

@st.cache_data(ttl=3600)
def fetch_live_rates():
    base_rates = {"USD": 1.0, "BHD": 0.377, "PHP": 58.50, "EUR": 0.92, "GBP": 0.78, "JPY": 152.0, "CHF": 0.865, "AUD": 1.51, "CAD": 1.38, "NZD": 1.66}
    try:
        api_u = base64.b64decode("aHR0cHM6Ly9vcGVuLmVyLWFwaS5jb20vdjYvbGF0ZXN0L1VTRA==").decode("utf-8")
        r = requests.get(api_u, timeout=4)
        if r.status_code == 200:
            data = r.json().get("rates", {})
            needed = ["USD", "BHD", "PHP", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"]
            if "BHD" in data and "PHP" in data:
                fetched = {k: float(data[k]) for k in needed if k in data}
                for k, v in base_rates.items():
                    if k not in fetched: fetched[k] = v
                return fetched, True, datetime.now().strftime("%Y-%m-%d %H:%M")
    except Exception: pass
    return base_rates, False, datetime.now().strftime("%Y-%m-%d %H:%M (Benchmark)")

rates_dict, is_live_rates, last_rate_update = fetch_live_rates()

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
                login_btn = st.form_submit_button("Unlock Dashboard", use_container_width=True)
                
                if login_btn:
                    user_info = USER_PROFILES[selected_user]
                    sec_obj = getattr(st, "secrets", {})
                    valid_pass = sec_obj.get(user_info["sec_key"], user_info["def_key"])
                    
                    if entered_pass == valid_pass:
                        st.session_state["authenticated"] = True
                        st.session_state["current_user"] = selected_user
                        st.success(f"Access granted for {selected_user}!")
                        st.rerun()
                    else:
                        st.error("Invalid access key. Please try again.")
        st.stop()

check_authentication()

current_user = st.session_state["current_user"]
user_cfg = USER_PROFILES[current_user]

DATA_FILE = user_cfg["data_file"]
CONFIG_FILE = user_cfg["config_file"]
INVEST_FILE = user_cfg["invest_file"]

def load_user_config():
    defaults = {
        "salary_bhd": 1200.0,
        "business_bhd": 0.0,
        "sidelines_bhd": 0.0,
        "other_income_bhd": 0.0,
        "fixed_priority_bhd": 350.0,
        "debts_pct": 15,
        "needs_pct": 45,
        "wants_pct": 20,
        "savings_pct": 20,
        "display_currency": "BHD"
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                saved = json.load(f)
                defaults.update(saved)
        except Exception: pass
    return defaults

def save_user_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f)

config = load_user_config()

def load_data(filepath):
    cols = [
        "Item #", "Date", "Main Category", "Sub Category", "Merchant/Description",
        "Billed Amount", "Actual Paid", "Currency", "Pending Due", "% Paid", "% Remaining",
        "Equivalent (BHD / PHP / USD)", "Status", "Payment Method", "Billed_BHD", "Paid_BHD"
    ]
    if os.path.exists(filepath):
        try:
            df = pd.read_csv(filepath)
            
            # Migration logic for older CSV files
            if "Amount" in df.columns and "Billed Amount" not in df.columns:
                df["Billed Amount"] = df["Amount"]
            if "Amount (BHD)" in df.columns and "Billed Amount" not in df.columns:
                df["Billed Amount"] = df["Amount (BHD)"]
            if "Actual Paid" not in df.columns:
                df["Actual Paid"] = df.get("Billed Amount", 0.0)
            if "Currency" not in df.columns:
                df["Currency"] = "BHD"
            if "Status" not in df.columns:
                df["Status"] = "Paid"
            if "Merchant/Description" not in df.columns:
                df["Merchant/Description"] = df.get("Merchant", "Unspecified")

            df["Date"] = pd.to_datetime(df["Date"]).dt.date
            df["Billed Amount"] = pd.to_numeric(df["Billed Amount"], errors="coerce").fillna(0.0)
            df["Actual Paid"] = pd.to_numeric(df["Actual Paid"], errors="coerce").fillna(0.0)
            
            return df
        except Exception: pass
    return pd.DataFrame(columns=cols)

def save_data(df, filepath):
    df.to_csv(filepath, index=False)

df_expenses = load_data(DATA_FILE)

# Load investments
def load_investments():
    if os.path.exists(INVEST_FILE):
        try: return pd.read_csv(INVEST_FILE)
        except Exception: pass
    return pd.DataFrame(columns=["Type", "Symbol/Ticker", "Platform", "Shares/Lots", "Avg Buy Price", "Current Price", "Notes"])

df_invest = load_investments()

# SIDEBAR CONFIGURATION
st.sidebar.title(f"⚙️ Settings ({current_user})")

st.sidebar.subheader("💵 Monthly Income Streams (BHD)")
salary_bhd = st.sidebar.number_input("Primary Salary (BD)", min_value=0.0, value=float(config["salary_bhd"]), step=50.0)
business_bhd = st.sidebar.number_input("Business Income (BD)", min_value=0.0, value=float(config["business_bhd"]), step=50.0)
sidelines_bhd = st.sidebar.number_input("Sidelines / Freelance (BD)", min_value=0.0, value=float(config["sidelines_bhd"]), step=50.0)
other_income_bhd = st.sidebar.number_input("Other Income (BD)", min_value=0.0, value=float(config["other_income_bhd"]), step=50.0)

total_income_bhd = salary_bhd + business_bhd + sidelines_bhd + other_income_bhd

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 Mandatory Priority Obligations")
fixed_priority_bhd = st.sidebar.number_input("100% Fixed Priority Target (BD)", min_value=0.0, value=float(config["fixed_priority_bhd"]), step=25.0, help="Household helper, loan amortizations, mandatory bills")

net_budget_bhd = max(0.0, total_income_bhd - fixed_priority_bhd)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Category Framework Allocation (%)")

debts_pct = st.sidebar.slider("Debts & Credits Target %", 0, 100, int(config["debts_pct"]))
needs_pct = st.sidebar.slider("Needs Target %", 0, 100, int(config["needs_pct"]))
wants_pct = st.sidebar.slider("Wants Target %", 0, 100, int(config["wants_pct"]))
savings_pct = st.sidebar.slider("Savings & Investments Target %", 0, 100, int(config["savings_pct"]))

tot_framework_pct = debts_pct + needs_pct + wants_pct + savings_pct
if tot_framework_pct != 100:
    st.sidebar.warning(f"⚠️ Allocation total is {tot_framework_pct}%. Please adjust so it equals exactly 100%.")

framework_title = f"{debts_pct}/{needs_pct}/{wants_pct}/{savings_pct} Framework"

disp_currency = st.sidebar.selectbox("Preferred Display Currency", ["BHD (BD)", "PHP (₱)", "USD ($)"], index=["BHD (BD)", "PHP (₱)", "USD ($)"].index("BHD (BD)") if config.get("display_currency") == "BHD" else 0)

if st.sidebar.button("💾 Save User Settings", use_container_width=True):
    config["salary_bhd"] = salary_bhd
    config["business_bhd"] = business_bhd
    config["sidelines_bhd"] = sidelines_bhd
    config["other_income_bhd"] = other_income_bhd
    config["fixed_priority_bhd"] = fixed_priority_bhd
    config["debts_pct"] = debts_pct
    config["needs_pct"] = needs_pct
    config["wants_pct"] = wants_pct
    config["savings_pct"] = savings_pct
    config["display_currency"] = disp_currency.split()[0]
    save_user_config(config)
    st.sidebar.success("Settings saved successfully!")
    st.rerun()

bhd_to_php = rates_dict.get("PHP", 58.50) / rates_dict.get("BHD", 0.377)
bhd_to_usd = rates_dict.get("USD", 1.0) / rates_dict.get("BHD", 0.377)

if "PHP" in disp_currency:
    rate_mult = bhd_to_php
    curr_symbol = "₱"
    curr_code = "PHP"
elif "USD" in disp_currency:
    rate_mult = bhd_to_usd
    curr_symbol = "$"
    curr_code = "USD"
else:
    rate_mult = 1.0
    curr_symbol = "BD "
    curr_code = "BHD"

disp_total_income = total_income_bhd * rate_mult
disp_fixed = fixed_priority_bhd * rate_mult
disp_net_budget = net_budget_bhd * rate_mult

target_debts_disp = disp_net_budget * (debts_pct / 100.0)
target_needs_disp = disp_net_budget * (needs_pct / 100.0)
target_wants_disp = disp_net_budget * (wants_pct / 100.0)
target_savings_disp = disp_net_budget * (savings_pct / 100.0)

# Calculate BHD equivalents for expenses
if not df_expenses.empty:
    def calc_bhd(row, val_col):
        v = float(row.get(val_col, 0.0))
        c = str(row.get("Currency", "BHD")).upper()
        if c == "PHP": return v / bhd_to_php
        elif c == "USD": return v / bhd_to_usd
        return v

    df_expenses["Billed_BHD"] = df_expenses.apply(lambda r: calc_bhd(r, "Billed Amount"), axis=1)
    df_expenses["Paid_BHD"] = df_expenses.apply(lambda r: calc_bhd(r, "Actual Paid"), axis=1)
else:
    df_expenses["Billed_BHD"] = 0.0
    df_expenses["Paid_BHD"] = 0.0

# APP HEADER & TIME CLOCK
st.markdown("<div class='main-header'>💰 Rogee&apos;s Financial Command Center</div>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-header'>Personal Multi-Stream Budget & Investment Manager | {framework_title}</div>", unsafe_allow_html=True)

now_utc = datetime.now(timezone.utc)
bh_time = now_utc + timedelta(hours=3)
ph_time = now_utc + timedelta(hours=8)

time_str = f"🇧🇭 <b>Bahrain:</b> {bh_time.strftime('%d %b %Y, %I:%M %p')} AST &nbsp;|&nbsp; 🇵🇭 <b>Philippines:</b> {ph_time.strftime('%d %b %Y, %I:%M %p')} PHT &nbsp;|&nbsp; 👤 <b>Account:</b> {current_user}"
st.markdown(f"<div class='time-badge'>{time_str}</div>", unsafe_allow_html=True)

rate_mode_str = "Live FX API" if is_live_rates else "Offline Benchmarks"
st.markdown(f'<div class="rate-card">🌐 <b>Live Exchange Rates ({rate_mode_str}):</b> <b>1 BHD</b> = <b>₱{bhd_to_php:,.2f} PHP</b> | <b>1 BHD</b> = <b>${bhd_to_usd:,.2f} USD</b> | <b>1 USD</b> = <b>₱{(bhd_to_php/bhd_to_usd):,.2f} PHP</b><span style="float: right; color: #6B7280; font-size: 0.82rem;">Updated: {last_rate_update}</span></div>', unsafe_allow_html=True)

# NAVIGATION TABS
tab_dash, tab_add, tab_history, tab_forex, tab_invest, tab_reports, tab_guide = st.tabs([
    "📈 Dashboard & Analytics",
    "➕ Record Expense",
    "📜 Transaction History",
    "💱 Live Forex Engine",
    "📊 MT5 & COL Investments",
    "📥 Download Reports",
    "📘 User Guide"
])

# Actuals calculations
if not df_expenses.empty:
    actual_priority_bhd = float(df_expenses[df_expenses["Main Category"] == "100% Priority & People to Pay"]["Paid_BHD"].sum())
    actual_debts_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Debts", case=False, na=False)]["Paid_BHD"].sum())
    actual_needs_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Needs", case=False, na=False)]["Paid_BHD"].sum())
    actual_wants_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Wants", case=False, na=False)]["Paid_BHD"].sum())
    actual_savings_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Savings", case=False, na=False)]["Paid_BHD"].sum())
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

    # Over Budget Warning / Status Banner
    if remaining_cash_bhd < 0:
        over_amt_bhd = abs(remaining_cash_bhd)
        over_amt_disp = over_amt_bhd * rate_mult
        st.markdown(
            f'<div class="overbudget-card">⚠️ <b>OVER BUDGET ALERT:</b> You have exceeded your total monthly income by <b>{curr_symbol}{over_amt_disp:,.2f}</b> '
            f'(BD {over_amt_bhd:,.2f} | ₱{over_amt_bhd*bhd_to_php:,.2f} | ${over_amt_bhd*bhd_to_usd:,.2f})!</div>',
            unsafe_allow_html=True
        )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Monthly Income", f"{curr_symbol}{disp_total_income:,.2f}")
    m2.metric("100% Mandatory Target", f"{curr_symbol}{disp_fixed:,.2f}")
    m3.metric("Total Spent To Date", f"{curr_symbol}{total_spent_disp:,.2f}", delta=f"-{curr_symbol}{total_spent_disp:,.2f}", delta_color="inverse")
    
    if remaining_cash_bhd >= 0:
        m4.metric("Remaining Net Cash", f"{curr_symbol}{remaining_cash_disp:,.2f}", delta=f"{curr_symbol}{remaining_cash_disp:,.2f}")
    else:
        over_amt_disp = abs(remaining_cash_disp)
        m4.metric("Over Budget Balance", f"-{curr_symbol}{over_amt_disp:,.2f}", delta=f"-{curr_symbol}{over_amt_disp:,.2f} OVER BUDGET", delta_color="inverse")

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
    st.subheader(f"📊 {framework_title} Breakdown")

    cat_summary = [
        {"Category": f"Debts & Credits ({debts_pct}%)", "Target Amount": target_debts_disp, "Actual Paid": actual_debts_disp, "Difference": target_debts_disp - actual_debts_disp, "Status": "On Track" if actual_debts_disp <= target_debts_disp else "Over Target"},
        {"Category": f"Needs ({needs_pct}%)", "Target Amount": target_needs_disp, "Actual Paid": actual_needs_disp, "Difference": target_needs_disp - actual_needs_disp, "Status": "On Track" if actual_needs_disp <= target_needs_disp else "Over Target"},
        {"Category": f"Wants ({wants_pct}%)", "Target Amount": target_wants_disp, "Actual Paid": actual_wants_disp, "Difference": target_wants_disp - actual_wants_disp, "Status": "On Track" if actual_wants_disp <= target_wants_disp else "Over Target"},
        {"Category": f"Savings & Investments ({savings_pct}%)", "Target Amount": target_savings_disp, "Actual Paid": actual_savings_disp, "Difference": actual_savings_disp - target_savings_disp, "Status": "Target Met" if actual_savings_disp >= target_savings_disp else "Under Goal"}
    ]
    st.dataframe(
        pd.DataFrame(cat_summary).style.format({
            "Target Amount": f"{curr_symbol}{{:,.2f}}",
            "Actual Paid": f"{curr_symbol}{{:,.2f}}",
            "Difference": f"{curr_symbol}{{:,.2f}}"
        }),
        use_container_width=True,
        hide_index=True
    )

    col_ch1, col_ch2 = st.columns(2)
    with col_ch1:
        st.markdown("#### Target vs. Actual Spending")
        df_chart = pd.DataFrame({
            "Category": ["Debts", "Needs", "Wants", "Savings"],
            "Target": [target_debts_disp, target_needs_disp, target_wants_disp, target_savings_disp],
            "Actual": [actual_debts_disp, actual_needs_disp, actual_wants_disp, actual_savings_disp]
        })
        fig_bar = go.Figure(data=[
            go.Bar(name='Target', x=df_chart['Category'], y=df_chart['Target'], marker_color='#93C5FD'),
            go.Bar(name='Actual', x=df_chart['Category'], y=df_chart['Actual'], marker_color='#1D4ED8')
        ])
        fig_bar.update_layout(barmode='group', margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_ch2:
        st.markdown("#### Spending Share by Main Category")
        if total_spent_disp > 0:
            df_pie = pd.DataFrame({
                "Category": ["Priority (100%)", f"Debts ({debts_pct}%)", f"Needs ({needs_pct}%)", f"Wants ({wants_pct}%)", f"Savings ({savings_pct}%)"],
                "Amount": [actual_priority_disp, actual_debts_disp, actual_needs_disp, actual_wants_disp, actual_savings_disp]
            })
            df_pie = df_pie[df_pie["Amount"] > 0]
            fig_pie = px.pie(df_pie, values="Amount", names="Category", hole=0.45)
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expense data recorded yet. Add your first payment in the 'Record Expense' tab!")

    st.markdown("---")
    st.subheader("📊 Multi-Month Expense Trends & Summary Matrix")
    
    if not df_expenses.empty:
        df_exp_copy = df_expenses.copy()
        df_exp_copy["YearMonth"] = pd.to_datetime(df_exp_copy["Date"]).dt.strftime("%Y-%m")
        df_exp_copy["DispPaid"] = df_exp_copy["Paid_BHD"] * rate_mult

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("#### Monthly Expense Comparison Over Time")
            m_trend = df_exp_copy.groupby(["YearMonth", "Main Category"])["DispPaid"].sum().reset_index()
            fig_trend = px.bar(m_trend, x="YearMonth", y="DispPaid", color="Main Category", barmode="stack")
            fig_trend.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_trend, use_container_width=True)

        with col_m2:
            st.markdown("#### Multi-Month Summary Pivot Matrix")
            pivot_df = df_exp_copy.pivot_table(index="YearMonth", columns="Main Category", values="DispPaid", aggfunc="sum", fill_value=0.0)
            pivot_df["Total Monthly Spent"] = pivot_df.sum(axis=1)
            st.dataframe(pivot_df.style.format(f"{curr_symbol}{{:,.2f}}"), use_container_width=True)

# TAB 2: RECORD EXPENSE
with tab_add:
    st.subheader(f"Record a New Payment / Expense ({current_user})")
    
    cat_options = [
        "100% Priority & People to Pay",
        f"Debts & Credits ({debts_pct}%)",
        f"Needs ({needs_pct}%)",
        f"Wants ({wants_pct}%)",
        f"Savings & Investments ({savings_pct}%)"
    ]

    # Category selection OUTSIDE form so changing main_cat instantly updates sub_cat without needing manual page refresh!
    col_cat1, col_cat2 = st.columns(2)
    with col_cat1:
        sel_main_cat = st.selectbox("1. Select Main Category", cat_options, key="record_main_category_select")

    # Dynamic sub-categories based on selected main category
    if "100%" in sel_main_cat:
        sub_options = ["People to Pay (Household Helper / Staff)", "Family Support & Remittance (100%)", "Direct Mandatory Loan / Debt", "Fixed Mandatory Utility / Bill"]
    elif "Debts" in sel_main_cat:
        sub_options = ["Credit Card Payments", "Personal Bank Loans", "Car / Vehicle Loans", "Housing Mortgages", "Family / Peer Debt Settlement"]
    elif "Needs" in sel_main_cat:
        sub_options = ["Housing / Rent / Mortgage", "Utilities & Bills", "Groceries & Food", "Transportation & Fuel", "Healthcare & Insurance", "Education & Tuition"]
    elif "Wants" in sel_main_cat:
        sub_options = ["Dining Out & Coffee", "Entertainment & Streaming", "Shopping & Apparel", "Hobbies & Travel", "Subscriptions & Software", "Miscellaneous Lifestyle"]
    else:
        sub_options = ["Emergency Fund", "COL Financial (PH Stocks)", "MT5 Forex / Trading Deposit", "Index Funds / ETFs", "Retirement & Pension", "Major Goal Savings"]

    with col_cat2:
        sel_sub_cat = st.selectbox("2. Select Sub-Category", sub_options, key="record_sub_category_select")

    st.markdown("---")

    with st.form("add_expense_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            exp_date = st.date_input("Date", value=datetime.today())
            merchant = st.text_input("Merchant / Description / Payee", placeholder="e.g., Landlord, Helper Salary, Grocery Store")
            input_currency = st.selectbox("Currency", ["BHD", "PHP", "USD"], index=0)
            payment_status = st.selectbox("Payment Status", ["Paid", "Pending Payment", "Partially Paid", "Not Paid"], index=0)

        with col_b:
            billed_input = st.number_input("Billed Amount", min_value=0.01, step=5.0, value=25.0)
            actual_paid_input = st.number_input("Actual Amount Paid", min_value=0.0, step=5.0, value=25.0)
            payment_method = st.selectbox("Payment Method", ["Benefit Pay", "Remittance", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])

        submit_btn = st.form_submit_button("Save Payment Record", use_container_width=True)

        if submit_btn:
            calc_pending = max(0.0, billed_input - actual_paid_input)
            pct_paid_val = (actual_paid_input / billed_input * 100.0) if billed_input > 0 else 0.0
            pct_rem_val = max(0.0, 100.0 - pct_paid_val)

            # Convert to BHD equivalents
            if input_currency == "PHP":
                b_bhd = billed_input / bhd_to_php
                p_bhd = actual_paid_input / bhd_to_php
            elif input_currency == "USD":
                b_bhd = billed_input / bhd_to_usd
                p_bhd = actual_paid_input / bhd_to_usd
            else:
                b_bhd = billed_input
                p_bhd = actual_paid_input

            equiv_str = f"BD {p_bhd:,.2f} | ₱{p_bhd*bhd_to_php:,.2f} | ${p_bhd*bhd_to_usd:,.2f}"

            new_row = pd.DataFrame([{
                "Item #": len(df_expenses) + 1,
                "Date": exp_date,
                "Main Category": sel_main_cat,
                "Sub Category": sel_sub_cat,
                "Merchant/Description": merchant if merchant else "Unspecified",
                "Billed Amount": billed_input,
                "Actual Paid": actual_paid_input,
                "Currency": input_currency,
                "Pending Due": calc_pending,
                "% Paid": f"{pct_paid_val:.1f}%",
                "% Remaining": f"{pct_rem_val:.1f}%",
                "Equivalent (BHD / PHP / USD)": equiv_str,
                "Status": payment_status,
                "Payment Method": payment_method,
                "Billed_BHD": b_bhd,
                "Paid_BHD": p_bhd
            }])

            df_expenses = pd.concat([df_expenses, new_row], ignore_index=True)
            save_data(df_expenses, DATA_FILE)
            st.success(f"Recorded payment for '{merchant if merchant else sel_sub_cat}' ({sel_main_cat})!")
            st.rerun()

# TAB 3: TRANSACTION HISTORY
with tab_history:
    st.subheader(f"📜 Recorded Transaction History ({current_user})")

    if not df_expenses.empty:
        # Recalculate BHD amounts
        df_expenses["Billed Amount"] = pd.to_numeric(df_expenses["Billed Amount"], errors="coerce").fillna(0.0)
        df_expenses["Actual Paid"] = pd.to_numeric(df_expenses["Actual Paid"], errors="coerce").fillna(0.0)
        
        df_expenses["Billed_BHD"] = df_expenses.apply(lambda r: calc_bhd(r, "Billed Amount"), axis=1)
        df_expenses["Paid_BHD"] = df_expenses.apply(lambda r: calc_bhd(r, "Actual Paid"), axis=1)
        df_expenses["Pending_BHD"] = (df_expenses["Billed_BHD"] - df_expenses["Paid_BHD"]).clip(lower=0.0)

        tot_billed_bhd = float(df_expenses["Billed_BHD"].sum())
        tot_paid_bhd = float(df_expenses["Paid_BHD"].sum())
        tot_pending_bhd = float(df_expenses["Pending_BHD"].sum())

        paid_cnt = int((df_expenses["Status"] == "Paid").sum())
        partial_cnt = int((df_expenses["Status"] == "Partially Paid").sum())
        pending_cnt = int(len(df_expenses) - paid_cnt - partial_cnt)

        st.info(
            f"📊 **Summary Ledger Status Breakdown:** 🟢 **{paid_cnt} Paid** | 🟡 **{partial_cnt} Partially Paid** | 🔴 **{pending_cnt} Unpaid/Pending**\n\n"
            f"💰 **Total Billed:** BD {tot_billed_bhd:,.2f} | ₱{tot_billed_bhd*bhd_to_php:,.2f} | ${tot_billed_bhd*bhd_to_usd:,.2f} &nbsp;|&nbsp; "
            f"✅ **Total Paid:** BD {tot_paid_bhd:,.2f} | ₱{tot_paid_bhd*bhd_to_php:,.2f} | ${tot_paid_bhd*bhd_to_usd:,.2f} &nbsp;|&nbsp; "
            f"⏳ **Pending Due:** BD {tot_pending_bhd:,.2f} | ₱{tot_pending_bhd*bhd_to_php:,.2f} | ${tot_pending_bhd*bhd_to_usd:,.2f}"
        )

        # Over Budget Warning in History Tab if Total Paid exceeds Total Income
        if tot_paid_bhd > total_income_bhd:
            over_hist_bhd = tot_paid_bhd - total_income_bhd
            st.markdown(
                f'<div class="overbudget-card">⚠️ <b>TOTAL SPENT OVER BUDGET:</b> Total paid transactions exceed your monthly income by <b>BD {over_hist_bhd:,.2f}</b> '
                f'(₱{over_hist_bhd*bhd_to_php:,.2f} | ${over_hist_bhd*bhd_to_usd:,.2f})!</div>',
                unsafe_allow_html=True
            )

        # Category Grouping and Date Chronological Sorting
        cat_order = {
            "100% Priority & People to Pay": 1,
            f"Debts & Credits ({debts_pct}%)": 2,
            f"Needs ({needs_pct}%)": 3,
            f"Wants ({wants_pct}%)": 4,
            f"Savings & Investments ({savings_pct}%)": 5
        }
        
        df_sort = df_expenses.copy()
        df_sort["Cat_Rank"] = df_sort["Main Category"].map(lambda c: next((v for k, v in cat_order.items() if k in str(c)), 99))
        df_sort["Date_Dt"] = pd.to_datetime(df_sort["Date"])
        
        df_sort = df_sort.sort_values(by=["Cat_Rank", "Date_Dt"], ascending=[True, True]).reset_index(drop=True)
        df_sort["Item #"] = range(1, len(df_sort) + 1)

        # Update linked non-editable columns
        df_sort["Pending Due"] = (df_sort["Billed Amount"] - df_sort["Actual Paid"]).clip(lower=0.0)
        df_sort["% Paid"] = df_sort.apply(lambda r: f"{(r['Actual Paid']/r['Billed Amount']*100.0):.1f}%" if r['Billed Amount'] > 0 else "0.0%", axis=1)
        df_sort["% Remaining"] = df_sort.apply(lambda r: f"{max(0.0, 100.0 - (r['Actual Paid']/r['Billed Amount']*100.0)):.1f}%" if r['Billed Amount'] > 0 else "100.0%", axis=1)
        
        df_sort["Equivalent (BHD / PHP / USD)"] = df_sort.apply(
            lambda r: f"BD {r['Paid_BHD']:,.2f} | ₱{r['Paid_BHD']*bhd_to_php:,.2f} | ${r['Paid_BHD']*bhd_to_usd:,.2f}", axis=1
        )

        display_cols = [
            "Item #", "Date", "Main Category", "Sub Category", "Merchant/Description",
            "Billed Amount", "Actual Paid", "Currency", "Pending Due", "% Paid", "% Remaining",
            "Equivalent (BHD / PHP / USD)", "Status", "Payment Method"
        ]
        
        df_display = df_sort[display_cols].copy()

        st.caption("✏️ **Editable Ledger:** Double-click Billed Amount, Actual Paid, Category, or Description to modify. Check row boxes to delete. Non-editable columns automatically update.")

        # Interactive Data Editor
        edited_df = st.data_editor(
            df_display,
            num_rows="dynamic",
            use_container_width=True,
            key=f"editor_{current_user}",
            disabled=["Item #", "Pending Due", "% Paid", "% Remaining", "Equivalent (BHD / PHP / USD)"]
        )

        # Status Highlighted View
        st.markdown("#### 🎨 Status-Highlighted Transaction View")
        def style_status_rows(row):
            status = str(row.get("Status", "")).lower()
            if "paid" in status and "part" not in status and "not" not in status and "pend" not in status:
                return ["background-color: #D1FAE5; color: #065F46; font-weight: 500;"] * len(row)
            elif "part" in status:
                return ["background-color: #FEF3C7; color: #92400E; font-weight: 500;"] * len(row)
            else:
                return ["background-color: #FEE2E2; color: #991B1B; font-weight: 500;"] * len(row)

        st.dataframe(
            df_display.style.apply(style_status_rows, axis=1),
            use_container_width=True,
            hide_index=True
        )

        col_h1, col_h2 = st.columns(2)
        with col_h1:
            if st.button("💾 Save Ledger Changes", type="primary", use_container_width=True):
                save_data(edited_df, DATA_FILE)
                st.success("Transaction history updated and saved!")
                st.rerun()
        with col_h2:
            if st.button("🗑️ Clear Entire History", use_container_width=True):
                if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
                st.rerun()

        st.markdown("---")
        st.markdown("#### 💰 Total Outstanding & Payment Summary Ledger")
        
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            st.markdown('<div class="rate-card">', unsafe_allow_html=True)
            st.markdown("##### 📋 Total Billed / Needed")
            st.write(f"• **BD (BHD):** BD {tot_billed_bhd:,.2f}")
            st.write(f"• **₱ (PHP):** ₱{tot_billed_bhd*bhd_to_php:,.2f}")
            st.write(f"• **$ (USD):** ${tot_billed_bhd*bhd_to_usd:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)

        with s_col2:
            st.markdown('<div class="income-card">', unsafe_allow_html=True)
            st.markdown("##### ✅ Total Amount Paid")
            st.write(f"• **BD (BHD):** BD {tot_paid_bhd:,.2f}")
            st.write(f"• **₱ (PHP):** ₱{tot_paid_bhd*bhd_to_php:,.2f}")
            st.write(f"• **$ (USD):** ${tot_paid_bhd*bhd_to_usd:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)

        with s_col3:
            st.markdown('<div class="priority-banner">', unsafe_allow_html=True)
            st.markdown("##### ⏳ Total Outstanding Needed to Pay")
            st.write(f"• **BD (BHD):** BD {tot_pending_bhd:,.2f}")
            st.write(f"• **₱ (PHP):** ₱{tot_pending_bhd*bhd_to_php:,.2f}")
            st.write(f"• **$ (USD):** ${tot_pending_bhd*bhd_to_usd:,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("No transaction history found. Start recording payments in the 'Record Expense' tab!")

# TAB 4: FOREX ENGINE
with tab_forex:
    st.subheader("💱 Live Forex Rate Engine & Currency Pair Selector")
    
    fx_col1, fx_col2 = st.columns(2)
    with fx_col1:
        st.markdown("#### Currency Pair Converter")
        pair_from = st.selectbox("From Currency", ["BHD", "PHP", "USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"], index=0)
        pair_to = st.selectbox("To Currency", ["PHP", "BHD", "USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"], index=0)
        calc_amt = st.number_input("Amount to Convert", min_value=1.0, value=100.0, step=10.0)

        rate_from_usd = rates_dict.get(pair_from, 1.0)
        rate_to_usd = rates_dict.get(pair_to, 1.0)
        cross_rate = rate_to_usd / rate_from_usd if rate_from_usd > 0 else 1.0
        converted_val = calc_amt * cross_rate

        st.success(f"### {calc_amt:,.2f} {pair_from} = **{converted_val:,.2f} {pair_to}**")
        st.info(f"💡 **Exchange Rate:** 1 {pair_from} = {cross_rate:,.4f} {pair_to}")

    with fx_col2:
        st.markdown("#### Live Major Pairs Dashboard")
        st.markdown(f"* **1 BHD → PHP:** ₱{(rates_dict.get('PHP', 58.5)/rates_dict.get('BHD', 0.377)):,.2f}")
        st.markdown(f"* **1 BHD → USD:** ${(rates_dict.get('USD', 1.0)/rates_dict.get('BHD', 0.377)):,.2f}")
        st.markdown(f"* **1 USD → PHP:** ₱{(rates_dict.get('PHP', 58.5)/rates_dict.get('USD', 1.0)):,.2f}")
        st.markdown(f"* **1 USD → CHF:** {rates_dict.get('CHF', 0.865):,.4f} CHF")
        st.markdown(f"* **1 AUD → CAD:** {(rates_dict.get('CAD', 1.38)/rates_dict.get('AUD', 1.51)):,.4f} CAD")
        st.markdown(f"* **1 NZD → USD:** {(rates_dict.get('USD', 1.0)/rates_dict.get('NZD', 1.66)):,.4f} USD")

# TAB 5: MT5 & COL INVESTMENTS
with tab_invest:
    st.subheader("📊 MT5 Forex & COL Financial Portfolio Manager")
    st.caption("Track your MetaTrader 5 trading accounts and COL Financial stock equity in one place.")

    # Live Pip & Margin Calculators
    with st.expander("🧮 Live MT5 Trading Calculators (Pip Value & Required Margin)", expanded=True):
        calc_tab1, calc_tab2 = st.tabs(["📍 Pip Value Calculator", "🛡️ Required Margin Calculator"])
        
        with calc_tab1:
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                pip_pair = st.selectbox("Trading Asset Pair", ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD (Gold)", "USDCHF", "AUDUSD"], index=0)
                lot_size = st.number_input("Trade Lot Size", min_value=0.01, step=0.1, value=1.0)
            with p_col2:
                acc_curr = st.selectbox("Account Currency", ["USD", "BHD", "PHP"], index=0)
                
                # Pip math logic
                if "JPY" in pip_pair: pip_size = 0.01
                elif "XAU" in pip_pair: pip_size = 0.10
                else: pip_size = 0.0001
                
                contract = 100.0 if "XAU" in pip_pair else 100000.0
                pip_val_usd = lot_size * contract * pip_size
                
                if acc_curr == "BHD": pip_val_disp = pip_val_usd / bhd_to_usd; p_sym = "BD "
                elif acc_curr == "PHP": pip_val_disp = pip_val_usd * (bhd_to_php / bhd_to_usd); p_sym = "₱"
                else: pip_val_disp = pip_val_usd; p_sym = "$"

                st.metric("Pip Value per Pip", f"{p_sym}{pip_val_disp:,.2f}")

        with calc_tab2:
            m_col1, m_col2 = st.columns(2)
            with m_col1:
                m_pair = st.selectbox("Asset Pair", ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"], index=0)
                m_lots = st.number_input("Lot Volume", min_value=0.01, value=1.0)
            with m_col2:
                leverage = st.selectbox("Account Leverage", [100, 200, 400, 500, 1000], index=3)
                notional_usd = m_lots * (2000.0 if "XAU" in m_pair else 100000.0)
                req_margin_usd = notional_usd / leverage
                st.metric("Required Margin", f"${req_margin_usd:,.2f}", help="Estimated margin required in USD")

    st.markdown("---")

    with st.form("add_investment_form", clear_on_submit=True):
        inv_col1, inv_col2 = st.columns(2)
        with inv_col1:
            inv_type = st.selectbox("Asset Class / Platform", ["COL Financial (PH Stocks)", "MetaTrader 5 (Forex / Indices)", "Crypto / Other"])
            ticker = st.text_input("Ticker / Asset Symbol", placeholder="e.g., ALI, BDO, EURUSD, XAUUSD")
            platform = st.text_input("Broker / Platform Name", placeholder="e.g., COL Financial, IC Markets, Exness")
        with inv_col2:
            shares = st.number_input("Shares / Lots Owned", min_value=0.01, value=100.0)
            buy_price = st.number_input("Avg Purchase Price", min_value=0.0001, value=10.0)
            curr_price = st.number_input("Current Market Price", min_value=0.0001, value=12.0)

        inv_submit = st.form_submit_button("Add Asset Record", use_container_width=True)
        if inv_submit:
            new_inv = pd.DataFrame([{
                "Type": inv_type,
                "Symbol/Ticker": ticker if ticker else "Unspecified",
                "Platform": platform if platform else "General",
                "Shares/Lots": shares,
                "Avg Buy Price": buy_price,
                "Current Price": curr_price,
                "Notes": f"Recorded on {datetime.today().strftime('%Y-%m-%d')}"
            }])
            df_invest = pd.concat([df_invest, new_inv], ignore_index=True)
            df_invest.to_csv(INVEST_FILE, index=False)
            st.success(f"Added {ticker} to your investment tracker!")
            st.rerun()

    if not df_invest.empty:
        st.markdown("#### Current Investment Portfolio Ledger")
        df_invest["Total Value"] = df_invest["Shares/Lots"] * df_invest["Current Price"]
        df_invest["Total Cost"] = df_invest["Shares/Lots"] * df_invest["Avg Buy Price"]
        df_invest["Profit / Loss"] = df_invest["Total Value"] - df_invest["Total Cost"]
        df_invest["Gain %"] = (df_invest["Profit / Loss"] / df_invest["Total Cost"]) * 100.0

        st.dataframe(df_invest, use_container_width=True, hide_index=True)

        col_tot1, col_tot2 = st.columns(2)
        with col_tot1:
            st.metric("Total Portfolio Equity", f"${df_invest['Total Value'].sum():,.2f}")
        with col_tot2:
            tot_pnl = float(df_invest["Profit / Loss"].sum())
            st.metric("Total Un-realized P&L", f"${tot_pnl:,.2f}", delta=f"${tot_pnl:,.2f}")

        if st.button("Clear Investment Ledger"):
            if os.path.exists(INVEST_FILE): os.remove(INVEST_FILE)
            st.rerun()

# TAB 6: REPORTS & EXPORT
with tab_reports:
    st.subheader("📥 Download Financial Reports & Data")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("#### 📊 CSV Transaction Ledger")
        if not df_expenses.empty:
            csv_data = df_expenses.to_csv(index=False).encode("utf-8")
            st.download_button(label="📥 Download CSV Ledger", data=csv_data, file_name=f"financial_ledger_{current_user.lower().replace(' ', '_')}.csv", mime="text/csv", use_container_width=True)
        else: st.info("No transaction records available to export.")
    with col_r2:
        st.markdown("#### 📜 Executive Financial Summary Report")
        rep_date = datetime.today().strftime("%Y-%m-%d")
        total_exp_bhd = float(df_expenses["Paid_BHD"].sum()) if not df_expenses.empty and "Paid_BHD" in df_expenses.columns else 0.0
        report_content = f"""
==================================================
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
2. EXPENSES BREAKDOWN BY CATEGORY
--------------------------------------------------
- Mandatory 100% Payments: BD {actual_priority_bhd:,.2f}
- Debts & Credits        : BD {actual_debts_bhd:,.2f}
- Needs ({needs_pct}% Target)     : BD {actual_needs_bhd:,.2f}
- Wants ({wants_pct}% Target)     : BD {actual_wants_bhd:,.2f}
- Savings ({savings_pct}% Target) : BD {actual_savings_bhd:,.2f}
--------------------------------------------------
GRAND TOTAL EXPENSES PAID: BD {total_exp_bhd:,.2f}
NET REMAINING CASH       : BD {(total_income_bhd - total_exp_bhd):,.2f}
==================================================
"""
        st.download_button(label="📥 Download Executive Summary (.TXT)", data=report_content, file_name=f"financial_summary_{current_user.lower().replace(' ', '_')}.txt", mime="text/plain", use_container_width=True)

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
