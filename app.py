import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import os
import json
import requests
import base64

# Set Streamlit page config
st.set_page_config(
    page_title="Rogee Financial Command Center",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling with adaptive dark/light mode support
st.markdown("""
<style>
    .main-header {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.1rem;
        line-height: 1.2;
    }
    @media (prefers-color-scheme: dark) {
        .main-header { color: #60A5FA !important; }
    }
    .sub-header {
        font-size: 0.95rem;
        color: #4B5563;
        margin-bottom: 0.8rem;
    }
    @media (prefers-color-scheme: dark) {
        .sub-header { color: #9CA3AF !important; }
    }
    .time-badge {
        background-color: #F3F4F6;
        border: 1px solid #E5E7EB;
        color: #1F2937 !important;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 12px;
        display: inline-block;
        width: 100%;
        text-align: center;
    }
    @media (prefers-color-scheme: dark) {
        .time-badge { background-color: #1F2937 !important; border-color: #374151 !important; color: #F3F4F6 !important; }
    }
    .priority-banner {
        background-color: #FEF2F2;
        border: 1px solid #FECACA;
        border-left: 5px solid #EF4444;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 12px;
        color: #991B1B !important;
    }
    .priority-banner * { color: #991B1B !important; }
    @media (prefers-color-scheme: dark) {
        .priority-banner { background-color: #450A0A !important; border-color: #7F1D1D !important; border-left: 5px solid #EF4444 !important; color: #FECACA !important; }
        .priority-banner * { color: #FECACA !important; }
    }
    .income-card {
        background-color: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-left: 5px solid #22C55E;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 12px;
        color: #166534 !important;
    }
    .income-card * { color: #166534 !important; }
    @media (prefers-color-scheme: dark) {
        .income-card { background-color: #052E16 !important; border-color: #14532D !important; border-left: 5px solid #22C55E !important; color: #BBF7D0 !important; }
        .income-card * { color: #BBF7D0 !important; }
    }
    .rate-card {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-left: 4px solid #3B82F6;
        padding: 8px 12px;
        border-radius: 6px;
        margin-bottom: 12px;
        font-size: 0.85rem;
        color: #1E40AF !important;
    }
    .rate-card * { color: #1E40AF !important; }
    @media (prefers-color-scheme: dark) {
        .rate-card { background-color: #1E3A8A !important; border-color: #1D4ED8 !important; border-left: 4px solid #60A5FA !important; color: #BFDBFE !important; }
        .rate-card * { color: #BFDBFE !important; }
    }
    .stMetric {
        background-color: #F9FAFB !important;
        padding: 8px 12px;
        border-radius: 6px;
        border: 1px solid #E5E7EB !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        color: #1E3A8A !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #374151 !important;
        font-weight: 600 !important;
    }
    @media (prefers-color-scheme: dark) {
        .stMetric { background-color: #1F2937 !important; border: 1px solid #374151 !important; }
        div[data-testid="stMetricValue"] { color: #60A5FA !important; }
        div[data-testid="stMetricLabel"] { color: #D1D5DB !important; }
    }
</style>
""", unsafe_allow_html=True)

# User profiles and authentication config
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
        "def_key": "uCe_0121119",
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

@st.cache_data(ttl=3600)
def fetch_live_rates():
    base_rates = {
        "USD": 1.0,
        "BHD": 0.377,
        "PHP": 58.50,
        "EUR": 0.92,
        "GBP": 0.78,
        "JPY": 152.0,
        "CHF": 0.865,
        "AUD": 1.51,
        "CAD": 1.38,
        "NZD": 1.66
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

def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = None
        
    if not st.session_state["authenticated"]:
        st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🔐 Rogee&apos;s Financial Command Center</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B7280;'>Select profile and enter your private access key to unlock your dashboard.</p>", unsafe_allow_html=True)
        
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
                        st.error("❌ Invalid access key. Access denied.")
        return False
    return True

if not check_authentication():
    st.stop()

current_user = st.session_state["current_user"]
user_config = USER_PROFILES[current_user]
DATA_FILE = user_config["data_file"]
CONFIG_FILE = user_config["config_file"]
INVEST_FILE = user_config["invest_file"]

def load_user_config():
    defaults = {
        "salary_bhd": 1500.0,
        "business_bhd": 0.0,
        "sidelines_bhd": 0.0,
        "other_income_bhd": 0.0,
        "fixed_priority_bhd": 200.0,
        "debts_pct": 15,
        "needs_pct": 45,
        "wants_pct": 20,
        "savings_pct": 20,
        "currency_code": "BHD"
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                saved = json.load(f)
                defaults.update(saved)
        except Exception:
            pass
    return defaults

def save_user_config(cfg):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=4)
    except Exception:
        pass

user_settings = load_user_config()

def load_data(file_path):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"]).dt.date
            
            # Migration/Ensuring columns exist
            required_cols = {
                "Main Category": "Needs (45%)",
                "Sub Category": "Unspecified",
                "Merchant/Description": "Unspecified",
                "Amount": 0.0,
                "Currency": "BHD",
                "Amount (BHD)": 0.0,
                "Payment Method": "Bank Transfer",
                "Payment Status": "Paid",
                "Actual Paid (BHD)": 0.0
            }
            for col, val in required_cols.items():
                if col not in df.columns:
                    if col == "Amount (BHD)":
                        df["Amount (BHD)"] = df["Amount"] if "Amount" in df.columns else 0.0
                    elif col == "Actual Paid (BHD)":
                        df["Actual Paid (BHD)"] = df["Amount (BHD)"] if "Amount (BHD)" in df.columns else 0.0
                    else:
                        df[col] = val
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=[
        "Date", "Main Category", "Sub Category", "Merchant/Description",
        "Amount", "Currency", "Amount (BHD)", "Actual Paid (BHD)", "Payment Method", "Payment Status"
    ])

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

def load_investments():
    if os.path.exists(INVEST_FILE):
        try:
            return pd.read_csv(INVEST_FILE)
        except Exception:
            pass
    return pd.DataFrame(columns=["Type", "Symbol/Ticker", "Platform", "Shares/Lots", "Avg Buy Price", "Current Price", "Notes"])

df_expenses = load_data(DATA_FILE)
df_invest = load_investments()

# Sidebar: User Settings
st.sidebar.title(f"⚙️ Settings ({current_user})")

if st.sidebar.button("🔒 Logout Profile", use_container_width=True):
    st.session_state["authenticated"] = False
    st.session_state["current_user"] = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("💵 Income Streams (BHD)")

salary_bhd = st.sidebar.number_input("Primary Salary (BD)", min_value=0.0, value=float(user_settings["salary_bhd"]), step=50.0)
business_bhd = st.sidebar.number_input("Business Income (BD)", min_value=0.0, value=float(user_settings["business_bhd"]), step=50.0)
sidelines_bhd = st.sidebar.number_input("Sidelines / Freelance (BD)", min_value=0.0, value=float(user_settings["sidelines_bhd"]), step=50.0)
other_income_bhd = st.sidebar.number_input("Other Income (BD)", min_value=0.0, value=float(user_settings["other_income_bhd"]), step=50.0)

total_income_bhd = salary_bhd + business_bhd + sidelines_bhd + other_income_bhd

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 Mandatory 100% Payments")
fixed_priority_bhd = st.sidebar.number_input("Mandatory Fixed Payments (BD)", min_value=0.0, value=float(user_settings["fixed_priority_bhd"]), step=25.0)

net_bhd_for_budget = max(0.0, total_income_bhd - fixed_priority_bhd)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 4-Category Allocation (%)")

debts_pct = st.sidebar.slider("Debts & Credits %", 0, 100, int(user_settings["debts_pct"]))
needs_pct = st.sidebar.slider("Needs Target % (Essentials)", 0, 100, int(user_settings["needs_pct"]))
wants_pct = st.sidebar.slider("Wants Target % (Lifestyle)", 0, 100, int(user_settings["wants_pct"]))
savings_pct = st.sidebar.slider("Savings & Investments %", 0, 100, int(user_settings["savings_pct"]))

sum_pct = debts_pct + needs_pct + wants_pct + savings_pct
if sum_pct != 100:
    st.sidebar.warning(f"Allocation total is {sum_pct}%. It should equal 100%.")

framework_title = f"{debts_pct}/{needs_pct}/{wants_pct}/{savings_pct} Framework"

st.sidebar.markdown("---")
st.sidebar.subheader("💱 Active Currency Display")
display_currency = st.sidebar.selectbox("Display Currency", ["BHD", "PHP", "USD"], index=["BHD", "PHP", "USD"].index(user_settings.get("currency_code", "BHD")))

# Save configuration changes
new_cfg = {
    "salary_bhd": salary_bhd,
    "business_bhd": business_bhd,
    "sidelines_bhd": sidelines_bhd,
    "other_income_bhd": other_income_bhd,
    "fixed_priority_bhd": fixed_priority_bhd,
    "debts_pct": debts_pct,
    "needs_pct": needs_pct,
    "wants_pct": wants_pct,
    "savings_pct": savings_pct,
    "currency_code": display_currency
}
if new_cfg != user_settings:
    save_user_config(new_cfg)

# Rates conversion math
bhd_to_usd = rates_dict.get("USD", 1.0) / rates_dict.get("BHD", 0.377)
bhd_to_php = rates_dict.get("PHP", 58.50) / rates_dict.get("BHD", 0.377)

if display_currency == "BHD":
    curr_symbol = "BD "
    curr_code = "BHD"
    rate_mult = 1.0
elif display_currency == "PHP":
    curr_symbol = "₱"
    curr_code = "PHP"
    rate_mult = bhd_to_php
else:
    curr_symbol = "$"
    curr_code = "USD"
    rate_mult = bhd_to_usd

# Calculate Targets
debts_target_bhd = net_bhd_for_budget * (debts_pct / 100.0)
needs_target_bhd = net_bhd_for_budget * (needs_pct / 100.0)
wants_target_bhd = net_bhd_for_budget * (wants_pct / 100.0)
savings_target_bhd = net_bhd_for_budget * (savings_pct / 100.0)

disp_total_income = total_income_bhd * rate_mult
disp_fixed = fixed_priority_bhd * rate_mult
disp_debts_target = debts_target_bhd * rate_mult
disp_needs_target = needs_target_bhd * rate_mult
disp_wants_target = wants_target_bhd * rate_mult
disp_savings_target = savings_target_bhd * rate_mult

# Dual Clocks (Bahrain UTC+3 and Philippines UTC+8)
now_utc = datetime.now(timezone.utc)
bh_time = now_utc.astimezone(timezone(timedelta(hours=3)))
ph_time = now_utc.astimezone(timezone(timedelta(hours=8)))

# Main Header Title & Badge
st.markdown('<div class="main-header">💰 Rogee&apos;s Financial Command Center</div>', unsafe_allow_html=True)

st.markdown(
    f'<div class="time-badge">'
    f'🇧🇭 <b>Bahrain:</b> {bh_time.strftime("%d %b %Y, %I:%M %p")} &nbsp;|&nbsp; '
    f'🇵🇭 <b>Philippines:</b> {ph_time.strftime("%d %b %Y, %I:%M %p")} &nbsp;|&nbsp; '
    f'<b>Account:</b> {current_user}'
    f'</div>',
    unsafe_allow_html=True
)

rate_mode_str = "Live Auto-Updated" if is_live_rates else "Benchmark Fixed"
st.markdown(
    f'<div class="rate-card">🌐 <b>Live FX Engine ({rate_mode_str}):</b> '
    f'<b>1 BHD</b> = <b>₱{bhd_to_php:,.2f} PHP</b> | '
    f'<b>1 BHD</b> = <b>${bhd_to_usd:,.2f} USD</b> | '
    f'<b>1 USD</b> = <b>₱{(bhd_to_php/bhd_to_usd):,.2f} PHP</b>'
    f'<span style="float: right; color: #6B7280; font-size: 0.8rem;">Updated: {last_rate_update}</span></div>',
    unsafe_allow_html=True
)

# Tabs Navigation
tab_dash, tab_add, tab_history, tab_forex, tab_invest, tab_reports, tab_guide = st.tabs([
    "📈 Dashboard & Analytics",
    "➕ Record Expense",
    "📜 Transaction History",
    "💱 Live Forex Engine",
    "📊 MT5 & COL Investments",
    "📥 Download Reports",
    "📘 User Guide"
])

# Actual Spending Calculation
if not df_expenses.empty:
    # Match category strings dynamically
    actual_priority_bhd = df_expenses[df_expenses["Main Category"].str.contains("100% Priority", na=False, case=False)]["Amount (BHD)"].sum()
    actual_debts_bhd = df_expenses[df_expenses["Main Category"].str.contains("Debts", na=False, case=False)]["Amount (BHD)"].sum()
    actual_needs_bhd = df_expenses[df_expenses["Main Category"].str.contains("Needs", na=False, case=False)]["Amount (BHD)"].sum()
    actual_wants_bhd = df_expenses[df_expenses["Main Category"].str.contains("Wants", na=False, case=False)]["Amount (BHD)"].sum()
    actual_savings_bhd = df_expenses[df_expenses["Main Category"].str.contains("Savings", na=False, case=False)]["Amount (BHD)"].sum()
    
    # Actual paid totals
    paid_priority_bhd = df_expenses[df_expenses["Main Category"].str.contains("100% Priority", na=False, case=False)]["Actual Paid (BHD)"].sum()
    paid_debts_bhd = df_expenses[df_expenses["Main Category"].str.contains("Debts", na=False, case=False)]["Actual Paid (BHD)"].sum()
    paid_needs_bhd = df_expenses[df_expenses["Main Category"].str.contains("Needs", na=False, case=False)]["Actual Paid (BHD)"].sum()
    paid_wants_bhd = df_expenses[df_expenses["Main Category"].str.contains("Wants", na=False, case=False)]["Actual Paid (BHD)"].sum()
    paid_savings_bhd = df_expenses[df_expenses["Main Category"].str.contains("Savings", na=False, case=False)]["Actual Paid (BHD)"].sum()
else:
    actual_priority_bhd = actual_debts_bhd = actual_needs_bhd = actual_wants_bhd = actual_savings_bhd = 0.0
    paid_priority_bhd = paid_debts_bhd = paid_needs_bhd = paid_wants_bhd = paid_savings_bhd = 0.0

total_billed_bhd = actual_priority_bhd + actual_debts_bhd + actual_needs_bhd + actual_wants_bhd + actual_savings_bhd
total_paid_bhd = paid_priority_bhd + paid_debts_bhd + paid_needs_bhd + paid_wants_bhd + paid_savings_bhd
total_pending_bhd = max(0.0, total_billed_bhd - total_paid_bhd)

remaining_cash_bhd = total_income_bhd - total_paid_bhd

# Currency conversions for display
disp_total_billed = total_billed_bhd * rate_mult
disp_total_paid = total_paid_bhd * rate_mult
disp_total_pending = total_pending_bhd * rate_mult
disp_remaining_cash = remaining_cash_bhd * rate_mult

# TAB 1: DASHBOARD
with tab_dash:
    st.markdown('<div class="income-card">', unsafe_allow_html=True)
    st.subheader("💵 Total Monthly Income Breakdown")
    c_inc1, c_inc2, c_inc3, c_inc4 = st.columns(4)
    c_inc1.metric("Primary Salary", f"BD {salary_bhd:,.2f}")
    c_inc2.metric("Business Income", f"BD {business_bhd:,.2f}")
    c_inc3.metric("Sidelines / Freelance", f"BD {sidelines_bhd:,.2f}")
    c_inc4.metric("Other Income", f"BD {other_income_bhd:,.2f}")
    st.write(f"**Total Combined Monthly Earnings:** `{curr_symbol}{disp_total_income:,.2f}` (BD {total_income_bhd:,.2f} | ₱{total_income_bhd*bhd_to_php:,.2f} | ${total_income_bhd*bhd_to_usd:,.2f})")
    st.markdown('</div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Income", f"{curr_symbol}{disp_total_income:,.2f}")
    m2.metric("Total Billed Expenses", f"{curr_symbol}{disp_total_billed:,.2f}")
    m3.metric("Total Actual Paid", f"{curr_symbol}{disp_total_paid:,.2f}", delta=f"-{curr_symbol}{disp_total_paid:,.2f}", delta_color="inverse")
    m4.metric("Remaining Net Cash", f"{curr_symbol}{disp_remaining_cash:,.2f}", delta=f"{curr_symbol}{disp_remaining_cash:,.2f}")

    st.markdown("---")

    st.markdown('<div class="priority-banner">', unsafe_allow_html=True)
    st.subheader("🚨 Mandatory 100% Obligations Progress")
    p_col1, p_col2 = st.columns([2, 1])
    with p_col1:
        priority_pct = min(100.0, (paid_priority_bhd / fixed_priority_bhd * 100.0)) if fixed_priority_bhd > 0 else 0.0
        st.progress(priority_pct / 100.0)
        disp_paid_prio = paid_priority_bhd * rate_mult
        st.write(f"Paid **{curr_symbol}{disp_paid_prio:,.2f}** of **{curr_symbol}{disp_fixed:,.2f}** mandatory obligations ({priority_pct:.1f}% paid).")
    with p_col2:
        rem_priority_bhd = max(0.0, fixed_priority_bhd - paid_priority_bhd)
        disp_rem_prio = rem_priority_bhd * rate_mult
        st.metric("Pending Priority Payments", f"{curr_symbol}{disp_rem_prio:,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader(f"📊 {framework_title} Benchmark Allocation Matrix")

    cat_summary_data = [
        {
            "Category": f"Debts & Credits ({debts_pct}%)",
            "Target Allocation": f"{debts_pct}%",
            f"Target ({curr_code})": debts_target_bhd * rate_mult,
            f"Billed ({curr_code})": actual_debts_bhd * rate_mult,
            f"Actual Paid ({curr_code})": paid_debts_bhd * rate_mult,
            f"Pending Due ({curr_code})": max(0.0, actual_debts_bhd - paid_debts_bhd) * rate_mult
        },
        {
            "Category": f"Needs ({needs_pct}%)",
            "Target Allocation": f"{needs_pct}%",
            f"Target ({curr_code})": needs_target_bhd * rate_mult,
            f"Billed ({curr_code})": actual_needs_bhd * rate_mult,
            f"Actual Paid ({curr_code})": paid_needs_bhd * rate_mult,
            f"Pending Due ({curr_code})": max(0.0, actual_needs_bhd - paid_needs_bhd) * rate_mult
        },
        {
            "Category": f"Wants ({wants_pct}%)",
            "Target Allocation": f"{wants_pct}%",
            f"Target ({curr_code})": wants_target_bhd * rate_mult,
            f"Billed ({curr_code})": actual_wants_bhd * rate_mult,
            f"Actual Paid ({curr_code})": paid_wants_bhd * rate_mult,
            f"Pending Due ({curr_code})": max(0.0, actual_wants_bhd - paid_wants_bhd) * rate_mult
        },
        {
            "Category": f"Savings & Investments ({savings_pct}%)",
            "Target Allocation": f"{savings_pct}%",
            f"Target ({curr_code})": savings_target_bhd * rate_mult,
            f"Billed ({curr_code})": actual_savings_bhd * rate_mult,
            f"Actual Paid ({curr_code})": paid_savings_bhd * rate_mult,
            f"Pending Due ({curr_code})": max(0.0, actual_savings_bhd - paid_savings_bhd) * rate_mult
        }
    ]
    df_cat_matrix = pd.DataFrame(cat_summary_data)
    st.dataframe(
        df_cat_matrix.style.format({
            f"Target ({curr_code})": f"{curr_symbol}{{:,.2f}}",
            f"Billed ({curr_code})": f"{curr_symbol}{{:,.2f}}",
            f"Actual Paid ({curr_code})": f"{curr_symbol}{{:,.2f}}",
            f"Pending Due ({curr_code})": f"{curr_symbol}{{:,.2f}}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.subheader("📈 Multi-Month Expense Analytics & Trends")

    if not df_expenses.empty:
        df_exp_copy = df_expenses.copy()
        df_exp_copy["YearMonth"] = pd.to_datetime(df_exp_copy["Date"]).dt.strftime("%Y-%m")
        df_exp_copy["DispPaid"] = df_exp_copy["Actual Paid (BHD)"] * rate_mult

        col_ch1, col_ch2 = st.columns(2)
        with col_ch1:
            st.markdown("#### Monthly Paid Expenses Over Time")
            monthly_trend = df_exp_copy.groupby(["YearMonth", "Main Category"])["DispPaid"].sum().reset_index()
            fig_trend = px.bar(
                monthly_trend,
                x="YearMonth",
                y="DispPaid",
                color="Main Category",
                barmode="stack",
                labels={"DispPaid": f"Amount ({curr_code})", "YearMonth": "Month"}
            )
            fig_trend.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_trend, use_container_width=True)

        with col_ch2:
            st.markdown("#### Category Distribution Share")
            fig_pie = px.pie(
                df_exp_copy,
                values="DispPaid",
                names="Main Category",
                hole=0.45
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No transaction history logged yet. Record your payments in the 'Record Expense' tab!")

# TAB 2: RECORD EXPENSE
with tab_add:
    st.subheader(f"Record a New Payment / Expense ({current_user})")

    category_options = [
        "100% Priority & People to Pay",
        f"Debts & Credits ({debts_pct}%)",
        f"Needs ({needs_pct}%)",
        f"Wants ({wants_pct}%)",
        f"Savings & Investments ({savings_pct}%)"
    ]

    with st.form("add_expense_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)

        with col_a:
            exp_date = st.date_input("Date", value=datetime.today())
            main_cat = st.selectbox("Category Framework", category_options)

            if "Priority" in main_cat:
                sub_cats = ["People to Pay (Household Helper / Staff)", "Family Support & Remittance (100%)", "Direct Mandatory Loan / Debt", "Fixed Mandatory Utility / Bill"]
            elif "Debts" in main_cat:
                sub_cats = ["Credit Card Payment", "Bank Loan Installment", "Car Loan", "Housing Mortgage", "Personal Debt Payoff"]
            elif "Needs" in main_cat:
                sub_cats = ["Rent / Housing", "Utilities & Electricity", "Groceries & Food", "Fuel & Transportation", "Medical & Insurance"]
            elif "Wants" in main_cat:
                sub_cats = ["Dining Out & Coffee", "Shopping & Clothes", "Entertainment & Streaming", "Travel & Hobbies", "Subscriptions"]
            else:
                sub_cats = ["Emergency Fund", "COL Stock Investment", "MT5 Forex Trading Deposit", "Index Funds / ETF", "Pension / Retirement Savings"]

            sub_cat = st.selectbox("Sub-Category", sub_cats)
            merchant = st.text_input("Merchant / Description / Payee", placeholder="e.g., Landlord, Helper Salary, Bank, Grocery")

        with col_b:
            input_currency = st.selectbox("Currency Choice", ["BHD", "PHP", "USD"], index=0)
            billed_input = st.number_input(f"Billed / Due Amount ({input_currency})", min_value=0.01, value=50.0, step=5.0)
            
            # Payment Status
            pay_status = st.selectbox("Payment Status", ["Paid", "Pending Payment", "Not Paid"], index=0)
            
            # Default paid amount depending on status
            default_paid = billed_input if pay_status == "Paid" else 0.0
            actual_paid_input = st.number_input(f"Actual Amount Paid ({input_currency})", min_value=0.0, value=default_paid, step=5.0)
            
            payment_method = st.selectbox("Payment Method", ["Benefit Pay", "Bank Transfer", "Remittance", "Credit Card", "Debit Card", "Cash"])

        submit_btn = st.form_submit_button("💾 Save Payment Record", use_container_width=True)

        if submit_btn:
            # Convert inputs to BHD base
            if input_currency == "BHD":
                amount_bhd = billed_input
                paid_bhd = actual_paid_input
            elif input_currency == "PHP":
                amount_bhd = billed_input / bhd_to_php
                paid_bhd = actual_paid_input / bhd_to_php
            else:
                amount_bhd = billed_input / bhd_to_usd
                paid_bhd = actual_paid_input / bhd_to_usd

            new_row = pd.DataFrame([{
                "Date": exp_date,
                "Main Category": main_cat,
                "Sub Category": sub_cat,
                "Merchant/Description": merchant if merchant else "Unspecified",
                "Amount": billed_input,
                "Currency": input_currency,
                "Amount (BHD)": amount_bhd,
                "Actual Paid (BHD)": paid_bhd,
                "Payment Method": payment_method,
                "Payment Status": pay_status
            }])

            df_expenses = pd.concat([df_expenses, new_row], ignore_index=True)
            save_data(df_expenses, DATA_FILE)
            st.success(f"Recorded payment: {input_currency} {billed_input:,.2f} for '{sub_cat}' ({pay_status})!")
            st.rerun()

# TAB 3: TRANSACTION HISTORY
with tab_history:
    st.subheader(f"📜 Recorded Transaction Ledger ({current_user})")

    if not df_expenses.empty:
        # Category order mapping for consistent category grouping
        cat_order_map = {
            "100% Priority & People to Pay": 1,
            "Debts & Credits": 2,
            "Needs": 3,
            "Wants": 4,
            "Savings & Investments": 5
        }
        
        def get_cat_rank(cat_str):
            for k, rank in cat_order_map.items():
                if k.lower() in str(cat_str).lower():
                    return rank
            return 6

        # Clone and format display dataframe
        df_display = df_expenses.copy()
        df_display["Cat_Rank"] = df_display["Main Category"].apply(get_cat_rank)
        
        # Sort chronologically by date within each category
        df_display = df_display.sort_values(by=["Cat_Rank", "Date"], ascending=[True, True]).reset_index(drop=True)
        
        # Adjust item numbers sequentially
        df_display["Item #"] = df_display.index + 1

        # Calculate percentages and remaining due
        df_display["Pending Due (BHD)"] = df_display.apply(
            lambda r: max(0.0, r["Amount (BHD)"] - r["Actual Paid (BHD)"]), axis=1
        )
        
        df_display["% Paid"] = df_display.apply(
            lambda r: round((r["Actual Paid (BHD)"] / r["Amount (BHD)"] * 100.0), 1) if r["Amount (BHD)"] > 0 else 0.0, axis=1
        )
        df_display["% Remaining"] = df_display["% Paid"].apply(lambda p: round(max(0.0, 100.0 - p), 1))

        # Add Row-Level Multi-Currency Equivalents beside BHD
        df_display["Billed Amount (BHD / PHP / USD)"] = df_display["Amount (BHD)"].apply(
            lambda b: f"BD {b:,.2f} (₱{b*bhd_to_php:,.2f} | ${b*bhd_to_usd:,.2f})"
        )
        df_display["Actual Paid (BHD / PHP / USD)"] = df_display["Actual Paid (BHD)"].apply(
            lambda b: f"BD {b:,.2f} (₱{b*bhd_to_php:,.2f} | ${b*bhd_to_usd:,.2f})"
        )
        df_display["Pending Due (BHD / PHP / USD)"] = df_display["Pending Due (BHD)"].apply(
            lambda b: f"BD {b:,.2f} (₱{b*bhd_to_php:,.2f} | ${b*bhd_to_usd:,.2f})"
        )

        st.caption("💡 **Chronologically Organized Ledger:** Categorized by group and ordered by date with auto-numbered items (#). Double-click cells to edit or select row checkboxes to delete.")

        # Column selection for editor view
        show_cols = [
            "Item #", "Date", "Main Category", "Sub Category", "Merchant/Description",
            "Payment Status", "% Paid", "% Remaining",
            "Billed Amount (BHD / PHP / USD)", "Actual Paid (BHD / PHP / USD)", "Pending Due (BHD / PHP / USD)",
            "Payment Method"
        ]

        edited_df = st.data_editor(
            df_display[show_cols],
            num_rows="dynamic",
            use_container_width=True,
            key=f"data_editor_{current_user}"
        )

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("💾 Save Ledger Modifications", type="primary", use_container_width=True):
                # Save changes back to original dataframe structure
                save_data(df_expenses, DATA_FILE)
                st.success("Ledger changes saved successfully!")
                st.rerun()

        with col_btn2:
            if st.button("🗑️ Clear Entire History File", use_container_width=True):
                if os.path.exists(DATA_FILE):
                    os.remove(DATA_FILE)
                st.success("Ledger file deleted successfully!")
                st.rerun()

        st.markdown("---")
        st.subheader("💵 Total Outstanding & Payment Summary Ledger")

        # Bottom Summary Totals for Billed, Paid, and Pending Due in BHD, PHP, and USD
        sum_billed_bhd = df_expenses["Amount (BHD)"].sum()
        sum_paid_bhd = df_expenses["Actual Paid (BHD)"].sum()
        sum_pending_bhd = max(0.0, sum_billed_bhd - sum_paid_bhd)

        sum_billed_php = sum_billed_bhd * bhd_to_php
        sum_paid_php = sum_paid_bhd * bhd_to_php
        sum_pending_php = sum_pending_bhd * bhd_to_php

        sum_billed_usd = sum_billed_bhd * bhd_to_usd
        sum_paid_usd = sum_paid_bhd * bhd_to_usd
        sum_pending_usd = sum_pending_bhd * bhd_to_usd

        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            st.metric(
                "Total Billed Amount Due",
                f"BD {sum_billed_bhd:,.2f}",
                delta=f"₱{sum_billed_php:,.2f} PHP | ${sum_billed_usd:,.2f} USD"
            )
        with s_col2:
            st.metric(
                "Total Actual Amount Paid",
                f"BD {sum_paid_bhd:,.2f}",
                delta=f"₱{sum_paid_php:,.2f} PHP | ${sum_paid_usd:,.2f} USD"
            )
        with s_col3:
            st.metric(
                "Total Outstanding Needed to Pay",
                f"BD {sum_pending_bhd:,.2f}",
                delta=f"₱{sum_pending_php:,.2f} PHP | ${sum_pending_usd:,.2f} USD",
                delta_color="inverse"
            )
    else:
        st.info("No transaction history found. Start logging payments in the 'Record Expense' tab!")

# TAB 4: LIVE FOREX ENGINE
with tab_forex:
    st.subheader("💱 Live Multi-Currency Cross Calculator")
    
    col_fx1, col_fx2 = st.columns(2)
    with col_fx1:
        calc_amt = st.number_input("Amount to Convert", min_value=1.0, value=100.0, step=10.0)
        pair_from = st.selectbox("From Currency", ["BHD", "PHP", "USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"], index=0)
        pair_to = st.selectbox("To Currency", ["PHP", "USD", "BHD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"], index=0)

        rate_from_usd = rates_dict.get(pair_from, 1.0)
        rate_to_usd = rates_dict.get(pair_to, 1.0)
        
        cross_rate = rate_to_usd / rate_from_usd
        converted_val = calc_amt * cross_rate

        st.success(f"### {calc_amt:,.2f} {pair_from} = **{converted_val:,.2f} {pair_to}**")
        st.info(f"💡 **Exchange Cross-Rate:** 1 {pair_from} = {cross_rate:,.4f} {pair_to}")

    with col_fx2:
        st.markdown("#### Live Major FX Ticker Rates")
        st.write(f"* **1 BHD → PHP:** ₱{bhd_to_php:,.2f} PHP")
        st.write(f"* **1 BHD → USD:** ${bhd_to_usd:,.2f} USD")
        st.write(f"* **1 USD → PHP:** ₱{(bhd_to_php/bhd_to_usd):,.2f} PHP")
        st.write(f"* **1 USD → CHF (USD/CHF):** {rates_dict.get('CHF', 0.865):,.4f} CHF")
        st.write(f"* **1 AUD → CAD (AUD/CAD):** {(rates_dict.get('CAD', 1.38)/rates_dict.get('AUD', 1.51)):,.4f} CAD")
        st.write(f"* **1 NZD → USD (NZD/USD):** {(rates_dict.get('USD', 1.0)/rates_dict.get('NZD', 1.66)):,.4f} USD")

        if st.button("🔄 Force Refresh Live Rates"):
            st.cache_data.clear()
            st.rerun()

# TAB 5: MT5 & COL INVESTMENTS
with tab_invest:
    st.subheader("📊 MT5 Forex & COL Financial Portfolio Manager")
    st.caption("Track your MetaTrader 5 trading accounts and COL Financial stock equity in one place.")

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
        st.markdown("#### Investment Portfolio Ledger")
        df_invest["Total Value"] = df_invest["Shares/Lots"] * df_invest["Current Price"]
        df_invest["Total Cost"] = df_invest["Shares/Lots"] * df_invest["Avg Buy Price"]
        df_invest["Profit / Loss"] = df_invest["Total Value"] - df_invest["Total Cost"]
        
        st.dataframe(df_invest, use_container_width=True, hide_index=True)

        col_tot1, col_tot2 = st.columns(2)
        with col_tot1:
            st.metric("Total Portfolio Equity", f"${df_invest['Total Value'].sum():,.2f}")
        with col_tot2:
            tot_pnl = df_invest["Profit / Loss"].sum()
            st.metric("Total Un-realized P&L", f"${tot_pnl:,.2f}", delta=f"${tot_pnl:,.2f}")

        if st.button("Clear Investment Ledger"):
            if os.path.exists(INVEST_FILE):
                os.remove(INVEST_FILE)
            st.rerun()

    st.markdown("---")
    st.subheader("🧮 Live MT5 Trading Calculators")

    calc_t1, calc_t2 = st.columns(2)
    with calc_t1:
        st.markdown("#### 📍 Pip Value Calculator")
        symbol_choice = st.selectbox("Trading Pair", ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD (Gold)", "USDCHF", "AUDUSD"], index=0)
        lot_size = st.number_input("Trade Volume (Lots)", min_value=0.01, value=1.00, step=0.1)
        acct_curr = st.selectbox("Account Base Currency", ["USD", "BHD", "PHP"], index=0)

        if "JPY" in symbol_choice:
            pip_in_usd = (0.01 / rates_dict.get("JPY", 152.0)) * (lot_size * 100000)
        elif "XAUUSD" in symbol_choice:
            pip_in_usd = 0.10 * (lot_size * 100)
        else:
            pip_in_usd = 0.0001 * (lot_size * 100000)

        if acct_curr == "BHD":
            pip_val_disp = pip_in_usd * rates_dict.get("BHD", 0.377)
            disp_sym = "BD "
        elif acct_curr == "PHP":
            pip_val_disp = pip_in_usd * rates_dict.get("PHP", 58.5)
            disp_sym = "₱"
        else:
            pip_val_disp = pip_in_usd
            disp_sym = "$"

        st.success(f"**Pip Value:** {disp_sym}{pip_val_disp:,.4f} per pip")

    with calc_t2:
        st.markdown("#### 🛡️ Required Margin Calculator")
        margin_lot = st.number_input("Margin Lot Size", min_value=0.01, value=1.00, step=0.1)
        leverage = st.selectbox("Account Leverage", ["1:100", "1:200", "1:500", "1:1000"], index=2)
        lev_denom = float(leverage.split(":")[1])

        notional_usd = margin_lot * 100000
        req_margin_usd = notional_usd / lev_denom

        st.info(f"**Required Margin:** ${req_margin_usd:,.2f} USD (BD {req_margin_usd*rates_dict.get('BHD', 0.377):,.2f} | ₱{req_margin_usd*rates_dict.get('PHP', 58.5):,.2f})")

# TAB 6: REPORTS & EXPORT
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
        
        report_content = f"""
==================================================
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
   - Equivalent in PHP   : PHP {(total_income_bhd * bhd_to_php):,.2f}
   - Equivalent in USD   : USD ${(total_income_bhd * bhd_to_usd):,.2f}

--------------------------------------------------
2. EXPENSES BREAKDOWN & OUTSTANDING DUE
--------------------------------------------------
- Mandatory 100% Payments: BD {actual_priority_bhd:,.2f} (Paid: BD {paid_priority_bhd:,.2f})
- Debts & Credits ({debts_pct}%) : BD {actual_debts_bhd:,.2f} (Paid: BD {paid_debts_bhd:,.2f})
- Needs ({needs_pct}% Target)     : BD {actual_needs_bhd:,.2f} (Paid: BD {paid_needs_bhd:,.2f})
- Wants ({wants_pct}% Target)     : BD {actual_wants_bhd:,.2f} (Paid: BD {paid_wants_bhd:,.2f})
- Savings & Inv ({savings_pct}%) : BD {actual_savings_bhd:,.2f} (Paid: BD {paid_savings_bhd:,.2f})
--------------------------------------------------
TOTAL BILLED EXPENSES    : BD {total_billed_bhd:,.2f}
TOTAL ACTUAL PAID        : BD {total_paid_bhd:,.2f}
TOTAL PENDING OUTSTANDING: BD {total_pending_bhd:,.2f}
   - Outstanding in PHP  : PHP {total_pending_bhd * bhd_to_php:,.2f}
   - Outstanding in USD  : USD ${total_pending_bhd * bhd_to_usd:,.2f}
NET REMAINING CASH       : BD {remaining_cash_bhd:,.2f}
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
