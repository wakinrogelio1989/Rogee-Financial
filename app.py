import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import os
import json
import requests
import base64

st.set_page_config(
    page_title="Rogee's Financial Command Center",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Mode & Light Mode Responsive Styling
st.markdown("""
<style>
    .main-header { font-size: 1.8rem; font-weight: 800; color: #1E3A8A; margin-bottom: 0.1rem; line-height: 1.2; }
    @media (prefers-color-scheme: dark) { .main-header { color: #60A5FA !important; } }
    .sub-header { font-size: 0.95rem; color: #4B5563; margin-bottom: 0.8rem; }
    @media (prefers-color-scheme: dark) { .sub-header { color: #9CA3AF !important; } }
    
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
        .time-badge {
            background-color: #1F2937 !important;
            border-color: #374151 !important;
            color: #F3F4F6 !important;
        }
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

    /* Metric Boxes Visibility Fix in Dark Mode */
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
        .stMetric { 
            background-color: #1F2937 !important; 
            border: 1px solid #374151 !important; 
        }
        div[data-testid="stMetricValue"] { 
            color: #60A5FA !important; 
        }
        div[data-testid="stMetricLabel"] { 
            color: #D1D5DB !important; 
        }
    }
</style>
""", unsafe_allow_html=True)

USER_PROFILES = {
    "Rogee": {"sec_key": "ROGEE_KEY", "def_key": "1989", "data_file": "expenses_rogee.csv", "config_file": "config_rogee.json", "invest_file": "investments_rogee.csv"},
    "Ferdie": {"sec_key": "USER2_KEY", "def_key": "Ce_0121119", "data_file": "expenses_user2.csv", "config_file": "config_user2.json", "invest_file": "investments_user2.csv"},
    "User 3": {"sec_key": "USER3_KEY", "def_key": "user32026", "data_file": "expenses_user3.csv", "config_file": "config_user3.json", "invest_file": "investments_user3.csv"},
    "User 4": {"sec_key": "USER4_KEY", "def_key": "user42026", "data_file": "expenses_user4.csv", "config_file": "config_user4.json", "invest_file": "investments_user4.csv"}
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
        st.markdown("<p style='text-align: center; color: #6B7280;'>Select your profile and enter your access key to unlock your dashboard.</p>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
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

def load_data(file_path):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df["Date"] = pd.to_datetime(df["Date"]).dt.date
            return df
        except Exception: pass
    return pd.DataFrame(columns=["Date", "Main Category", "Sub Category", "Merchant/Description", "Amount", "Currency", "Amount (BHD)", "Payment Method"])

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

def load_user_config(cfg_path):
    defaults = {"salary_bhd": 1500.0, "business_bhd": 0.0, "sidelines_bhd": 0.0, "other_income_bhd": 0.0, "fixed_priority_bhd": 300.0, "debts_pct": 10, "needs_pct": 50, "wants_pct": 20, "savings_pct": 20}
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r") as f:
                saved = json.load(f)
                defaults.update(saved)
        except Exception: pass
    return defaults

def save_user_config(cfg_path, cfg_dict):
    try:
        with open(cfg_path, "w") as f:
            json.dump(cfg_dict, f, indent=2)
    except Exception: pass

def load_investments(inv_path):
    if os.path.exists(inv_path):
        try: return pd.read_csv(inv_path)
        except Exception: pass
    return pd.DataFrame(columns=["Type", "Symbol/Ticker", "Platform", "Shares/Lots", "Avg Buy Price", "Current Price", "Notes"])

df_expenses = load_data(DATA_FILE)
df_invest = load_investments(INVEST_FILE)
user_cfg = load_user_config(CONFIG_FILE)

st.sidebar.title(f"⚙️ Settings ({current_user})")

display_curr = st.sidebar.selectbox("Display Currency", ["BHD (BD)", "PHP (₱)", "USD ($)"], index=0)
curr_code = display_curr.split()[0]

bhd_to_usd = rates_dict.get("USD", 1.0) / rates_dict.get("BHD", 0.377)
bhd_to_php = rates_dict.get("PHP", 58.50) / rates_dict.get("BHD", 0.377)

EXCHANGE_RATES = {
    "BHD": {"symbol": "BD ", "rate": 1.0, "name": "Bahraini Dinar"},
    "PHP": {"symbol": "₱", "rate": bhd_to_php, "name": "Philippine Peso"},
    "USD": {"symbol": "$", "rate": bhd_to_usd, "name": "US Dollar"}
}

curr_symbol = EXCHANGE_RATES[curr_code]["symbol"]
rate_mult = EXCHANGE_RATES[curr_code]["rate"]

st.sidebar.markdown("---")
st.sidebar.subheader("💵 Monthly Income Streams (BHD)")
salary_bhd = st.sidebar.number_input("Primary Salary (BHD)", min_value=0.0, value=float(user_cfg.get("salary_bhd", 1500.0)), step=50.0)
business_bhd = st.sidebar.number_input("Business Income (BHD)", min_value=0.0, value=float(user_cfg.get("business_bhd", 0.0)), step=50.0)
sidelines_bhd = st.sidebar.number_input("Sidelines / Freelance (BHD)", min_value=0.0, value=float(user_cfg.get("sidelines_bhd", 0.0)), step=50.0)
other_income_bhd = st.sidebar.number_input("Other Income (BHD)", min_value=0.0, value=float(user_cfg.get("other_income_bhd", 0.0)), step=50.0)

total_income_bhd = salary_bhd + business_bhd + sidelines_bhd + other_income_bhd
disp_total_income = total_income_bhd * rate_mult

st.sidebar.info(f"**Total Combined:** `{curr_symbol}{disp_total_income:,.2f}`")

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 100% Mandatory Payments")
fixed_priority_bhd = st.sidebar.number_input("Mandatory Obligations Target (BHD)", min_value=0.0, value=float(user_cfg.get("fixed_priority_bhd", 300.0)), step=25.0)
disp_fixed = fixed_priority_bhd * rate_mult

net_bhd_for_budget = max(0.0, total_income_bhd - fixed_priority_bhd)
disp_net_budget = net_bhd_for_budget * rate_mult

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Category Framework Allocation (%)")
debts_pct = st.sidebar.slider("Debts & Credits Target %", 0, 100, int(user_cfg.get("debts_pct", 10)))
needs_pct = st.sidebar.slider("Needs Target %", 0, 100, int(user_cfg.get("needs_pct", 50)))
wants_pct = st.sidebar.slider("Wants Target %", 0, 100, int(user_cfg.get("wants_pct", 20)))
savings_pct = st.sidebar.slider("Savings & Investments Target %", 0, 100, int(user_cfg.get("savings_pct", 20)))

total_pct = debts_pct + needs_pct + wants_pct + savings_pct
if total_pct != 100:
    st.sidebar.warning(f"Allocation sums to {total_pct}%. Ideally should sum to 100%.")

framework_title = f"{debts_pct}/{needs_pct}/{wants_pct}/{savings_pct} Framework"

current_cfg_state = {
    "salary_bhd": salary_bhd, "business_bhd": business_bhd, "sidelines_bhd": sidelines_bhd, "other_income_bhd": other_income_bhd,
    "fixed_priority_bhd": fixed_priority_bhd, "debts_pct": debts_pct, "needs_pct": needs_pct, "wants_pct": wants_pct, "savings_pct": savings_pct
}
if current_cfg_state != user_cfg:
    save_user_config(CONFIG_FILE, current_cfg_state)

st.sidebar.markdown("---")
if st.sidebar.button("🔒 Lock App / Log Out", use_container_width=True):
    st.session_state["authenticated"] = False
    st.session_state["current_user"] = None
    st.rerun()

debts_target = disp_net_budget * (debts_pct / 100.0)
needs_target = disp_net_budget * (needs_pct / 100.0)
wants_target = disp_net_budget * (wants_pct / 100.0)
savings_target = disp_net_budget * (savings_pct / 100.0)

utc_now = datetime.now(timezone.utc)
bh_time = utc_now + timedelta(hours=3)
ph_time = utc_now + timedelta(hours=8)

st.markdown('<div class="main-header">💰 Rogee\'s Financial Command Center</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Multi-Currency Personal Finance Manager ({framework_title})</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="time-badge">
    <b>Bahrain:</b> {bh_time.strftime("%d %b %Y, %I:%M %p")} &nbsp;|&nbsp; 
    <b>Philippines:</b> {ph_time.strftime("%d %b %Y, %I:%M %p")} &nbsp;|&nbsp; 
    <b>User:</b> {current_user}
</div>
""", unsafe_allow_html=True)

rate_mode_str = "Live Auto-Updated" if is_live_rates else "Benchmark Fixed"
st.markdown(f'<div class="rate-card">🌐 <b>Live FX Rates ({rate_mode_str}):</b> <b>1 BHD</b> = <b>₱{bhd_to_php:,.2f} PHP</b> | <b>1 BHD</b> = <b>${bhd_to_usd:,.2f} USD</b> | <b>1 USD</b> = <b>₱{(bhd_to_php/bhd_to_usd):,.2f} PHP</b> <span style="float: right;">Updated: {last_rate_update}</span></div>', unsafe_allow_html=True)

tab_dash, tab_add, tab_history, tab_forex, tab_invest, tab_reports, tab_guide = st.tabs([
    "📈 Dashboard & Analytics", "➕ Record Expense", "📜 Transaction History", "💱 Live Forex Engine", "📊 MT5 & COL Investments", "📥 Download Reports", "📘 User Guide"
])

if not df_expenses.empty:
    actual_priority_bhd = df_expenses[df_expenses["Main Category"] == "100% Priority & People to Pay"]["Amount (BHD)"].sum()
    actual_debts_bhd = df_expenses[df_expenses["Main Category"].str.contains("Debts", case=False, na=False)]["Amount (BHD)"].sum()
    actual_needs_bhd = df_expenses[df_expenses["Main Category"].str.contains("Needs", case=False, na=False)]["Amount (BHD)"].sum()
    actual_wants_bhd = df_expenses[df_expenses["Main Category"].str.contains("Wants", case=False, na=False)]["Amount (BHD)"].sum()
    actual_savings_bhd = df_expenses[df_expenses["Main Category"].str.contains("Savings", case=False, na=False)]["Amount (BHD)"].sum()
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
    st.subheader(f"📊 {framework_title} Allocation & Multi-Month Expense Trends")

    cat_data = [
        {"Category": f"Debts & Credits ({debts_pct}%)", "Target Allocation": f"{debts_pct}%", f"Target ({curr_code})": debts_target, f"Actual Spent ({curr_code})": actual_debts_disp, f"Difference ({curr_code})": debts_target - actual_debts_disp, "Status": "On Track" if actual_debts_disp <= debts_target else "Over Target"},
        {"Category": f"Needs ({needs_pct}%)", "Target Allocation": f"{needs_pct}%", f"Target ({curr_code})": needs_target, f"Actual Spent ({curr_code})": actual_needs_disp, f"Difference ({curr_code})": needs_target - actual_needs_disp, "Status": "On Track" if actual_needs_disp <= needs_target else "Over Target"},
        {"Category": f"Wants ({wants_pct}%)", "Target Allocation": f"{wants_pct}%", f"Target ({curr_code})": wants_target, f"Actual Spent ({curr_code})": actual_wants_disp, f"Difference ({curr_code})": wants_target - actual_wants_disp, "Status": "On Track" if actual_wants_disp <= wants_target else "Over Target"},
        {"Category": f"Savings & Investments ({savings_pct}%)", "Target Allocation": f"{savings_pct}%", f"Target ({curr_code})": savings_target, f"Actual Spent ({curr_code})": actual_savings_disp, f"Difference ({curr_code})": actual_savings_disp - savings_target, "Status": "Target Met" if actual_savings_disp >= savings_target else "Under Goal"}
    ]
    st.dataframe(pd.DataFrame(cat_data).style.format({
        f"Target ({curr_code})": f"{curr_symbol}{{:,.2f}}",
        f"Actual Spent ({curr_code})": f"{curr_symbol}{{:,.2f}}",
        f"Difference ({curr_code})": f"{curr_symbol}{{:,.2f}}"
    }), use_container_width=True, hide_index=True)

    st.markdown("---")

    if not df_expenses.empty:
        df_exp_copy = df_expenses.copy()
        df_exp_copy["YearMonth"] = pd.to_datetime(df_exp_copy["Date"]).dt.strftime("%Y-%m")
        df_exp_copy["DispAmount"] = df_exp_copy["Amount (BHD)"] * rate_mult

        col_ch1, col_ch2 = st.columns(2)
        with col_ch1:
            st.markdown("#### Target vs. Actual Spending (Net Budget)")
            chart_df = pd.DataFrame({
                "Category": ["Debts", "Needs", "Wants", "Savings"],
                "Target": [debts_target, needs_target, wants_target, savings_target],
                "Actual": [actual_debts_disp, actual_needs_disp, actual_wants_disp, actual_savings_disp]
            })
            fig_bar = go.Figure(data=[
                go.Bar(name="Target", x=chart_df["Category"], y=chart_df["Target"], marker_color="#93C5FD"),
                go.Bar(name="Actual", x=chart_df["Category"], y=chart_df["Actual"], marker_color="#1D4ED8")
            ])
            fig_bar.update_layout(barmode="group", margin=dict(l=10, r=10, t=25, b=10))
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_ch2:
            st.markdown("#### Overall Expense Share")
            fig_pie = px.pie(
                df_exp_copy, values="DispAmount", names="Main Category", hole=0.45,
                color_discrete_sequence=["#EF4444", "#8B5CF6", "#2563EB", "#F59E0B", "#10B981"]
            )
            fig_pie.update_layout(margin=dict(l=10, r=10, t=25, b=10))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("#### Multi-Month Category Summary Matrix")
        pivot_df = df_exp_copy.pivot_table(index="YearMonth", columns="Main Category", values="DispAmount", aggfunc="sum", fill_value=0.0)
        pivot_df["Total Monthly Spent"] = pivot_df.sum(axis=1)
        st.dataframe(pivot_df.style.format(f"{curr_symbol}{{:,.2f}}"), use_container_width=True)
    else:
        st.info("No expense records logged yet. Add your first payment in the 'Record Expense' tab!")

with tab_add:
    st.subheader(f"Record a New Payment / Expense ({current_user})")
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
                sub_cats = ["Credit Card Debt Payoff", "Bank Loan Repayment", "Car Loan Payment", "Housing Loan Payment", "Personal Debt Payoff"]
            elif "Needs" in main_cat:
                sub_cats = ["Housing / Rent / Mortgage", "Utilities & Bills", "Groceries", "Transportation / Fuel", "Healthcare / Insurance", "Minimum Debt Payments"]
            elif "Wants" in main_cat:
                sub_cats = ["Dining Out & Coffee", "Entertainment & Streaming", "Shopping & Apparel", "Hobbies & Travel", "Subscriptions", "Miscellaneous"]
            else:
                sub_cats = ["Emergency Fund", "COL Financial Stock Investments", "MT5 Trading Deposit", "Index Funds / Stocks", "Pension / Retirement", "Major Savings Goal"]

            sub_cat = st.selectbox("Sub-Category", sub_cats)

        with col_b:
            merchant = st.text_input("Merchant / Description / Payee", placeholder="e.g. Helper Salary, Bank Loan, Grocery")
            amount_input = st.number_input("Amount", min_value=0.01, step=5.0, value=25.0)
            input_currency = st.selectbox("Payment Currency", ["BHD", "PHP", "USD"], index=0)
            payment_method = st.selectbox("Payment Method", ["Benefit Pay", "Remittance", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])

        submit_btn = st.form_submit_button("Save Payment Record", use_container_width=True)

        if submit_btn:
            amount_bhd = amount_input if input_currency == "BHD" else (amount_input / bhd_to_php if input_currency == "PHP" else amount_input / bhd_to_usd)
            new_row = pd.DataFrame([{
                "Date": exp_date,
                "Main Category": main_cat,
                "Sub Category": sub_cat,
                "Merchant/Description": merchant if merchant else "Unspecified",
                "Amount": amount_input,
                "Currency": input_currency,
                "Amount (BHD)": amount_bhd,
                "Payment Method": payment_method
            }])
            df_expenses = pd.concat([df_expenses, new_row], ignore_index=True)
            save_data(df_expenses, DATA_FILE)
            st.success(f"Recorded payment of {EXCHANGE_RATES[input_currency]['symbol']}{amount_input:,.2f} ({sub_cat})!")
            st.rerun()

with tab_history:
    st.subheader(f"📜 Recorded Transaction History ({current\_user})") if not df\_expenses.empty: total\_recorded\_bhd = df\_expenses["Amount (BHD)"].sum() if "Amount (BHD)" in df\_expenses.columns else df\_expenses["Amount"].sum() total\_recorded\_disp = total\_recorded\_bhd \* rate\_mult st.info(f"💰 \*\*Total Recorded Expenses: {curr\_symbol}{total\_recorded\_disp:,.2f}\*\* (BD {total\_recorded\_bhd:,.2f} | ₱{total\_recorded\_bhd\*bhd\_to\_php:,.2f} | ${total\_recorded\_bhd\*bhd\_to\_usd:,.2f})") st.caption("✏️ \*\*How to Edit/Delete:\*\* Double-click any cell to change dates, amounts, or descriptions. Select checkbox rows to delete them, then click \*\*💾 Save Ledger Changes\*\*!") # Interactive Editable Table (allows inline editing and row deletion) edited\_df = st.data\_editor( df\_expenses.sort\_values(by="Date", ascending=False), num\_rows="dynamic", use\_container\_width=True, key=f"expense\_editor\_{current\_user}" ) col\_hist1, col\_hist2 = st.columns(2) with col\_hist1: if st.button("💾 Save Ledger Changes", type="primary", use\_container\_width=True): save\_data(edited\_df, DATA\_FILE) st.success("Ledger updated and saved successfully!") st.rerun() with col\_hist2: if st.button("🗑️ Clear Entire History", use\_container\_width=True): if os.path.exists(DATA\_FILE): os.remove(DATA\_FILE) st.success("All transaction logs cleared!") st.rerun() else: st.info("No transaction history found. Start recording payments in the 'Record Expense' tab!")

with tab_forex:
    st.subheader("💱 Live Multi-Currency & Cross Rates Engine")
    st.write("Convert any currency pair using live cross exchange rates.")

    col_fx1, col_fx2 = st.columns(2)
    with col_fx1:
        st.markdown("#### Live Pair Converter")
        calc_amt = st.number_input("Amount to Convert", min_value=0.01, value=100.0, step=10.0)
        pair_from = st.selectbox("From Currency", ["BHD", "PHP", "USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"], index=0)
        pair_to = st.selectbox("To Currency", ["PHP", "USD", "BHD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"], index=0)

        rate_from_usd = rates_dict.get(pair_from, 1.0)
        rate_to_usd = rates_dict.get(pair_to, 1.0)
        cross_rate = rate_to_usd / rate_from_usd
        converted_val = calc_amt * cross_rate

        st.success(f"### {calc_amt:,.2f} {pair_from} = **{converted_val:,.2f} {pair_to}**")
        st.info(f"💡 **Exchange Rate:** 1 {pair_from} = {cross_rate:,.4f} {pair_to}")

    with col_fx2:
        st.markdown("#### Live Major Pairs Dashboard")
        st.markdown(f"""
        * **1 BHD -> PHP:** ₱{(rates_dict.get("PHP", 58.5)/rates_dict.get("BHD", 0.377)):,.2f}
        * **1 BHD -> USD:** ${(rates_dict.get("USD", 1.0)/rates_dict.get("BHD", 0.377)):,.2f}
        * **1 USD -> PHP:** ₱{rates_dict.get("PHP", 58.5):,.2f}
        * **1 USD -> CHF (USD/CHF):** {rates_dict.get("CHF", 0.865):,.4f}
        * **1 AUD -> CAD (AUD/CAD):** {(rates_dict.get("CAD", 1.38)/rates_dict.get("AUD", 1.51)):,.4f}
        * **1 NZD -> USD (NZD/USD):** {(1.0/rates_dict.get("NZD", 1.66)):,.4f}
        """)
        if st.button("🔄 Force Refresh Live Rates Now"):
            st.cache_data.clear()
            st.rerun()

with tab_invest:
    st.subheader("📊 MT5 & COL Investments + Live Calculators")

    st.markdown("#### 🧮 Live MT5 Trading Calculators")
    calc_col1, calc_col2 = st.columns(2)
    with calc_col1:
        st.markdown("##### 📍 Pip Value Calculator")
        pip_pair = st.selectbox("Trading Pair", ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD (Gold)", "USDCHF", "AUDUSD"], index=0)
        pip_lots = st.number_input("Lot Size (Standard Lots)", min_value=0.01, value=1.0, step=0.1)
        pip_account_curr = st.selectbox("Account Currency", ["USD", "BHD", "PHP"], index=0)

        contract_size = 100000 if "XAUUSD" not in pip_pair else 100
        pip_size = 0.01 if "JPY" in pip_pair else (0.1 if "XAUUSD" in pip_pair else 0.0001)

        pip_val_usd = pip_lots * contract_size * pip_size
        pip_val_disp = pip_val_usd if pip_account_curr == "USD" else (pip_val_usd * 0.377 if pip_account_curr == "BHD" else pip_val_usd * bhd_to_php / bhd_to_usd)
        pip_sym = "$" if pip_account_curr == "USD" else ("BD " if pip_account_curr == "BHD" else "₱")

        st.success(f"**Pip Value (per pip):** `{pip_sym}{pip_val_disp:,.2f} {pip_account_curr}`")

    with calc_col2:
        st.markdown("##### 🛡️ Required Margin Calculator")
        m_lots = st.number_input("Trade Lot Size", min_value=0.01, value=1.0, step=0.1, key="m_lots")
        m_price = st.number_input("Asset Entry Price", min_value=0.0001, value=1.0850, step=0.01)
        m_leverage = st.selectbox("Account Leverage", [100, 200, 500, 1000], index=2)

        margin_req_usd = (m_lots * 100000 * m_price) / m_leverage
        st.success(f"**Required Margin:** `${margin_req_usd:,.2f} USD` (at 1:{m_leverage} leverage)")

    st.markdown("---")
    st.markdown("#### 📁 Portfolio & Assets Ledger")

    with st.form("add_investment_form", clear_on_submit=True):
        inv_col1, inv_col2 = st.columns(2)
        with inv_col1:
            inv_type = st.selectbox("Asset Class / Platform", ["COL Financial (PH Stocks)", "MetaTrader 5 (Forex / Indices)", "Crypto / Other"])
            ticker = st.text_input("Ticker / Asset Symbol", placeholder="e.g. ALI, BDO, EURUSD, XAUUSD")
            platform = st.text_input("Broker / Platform Name", placeholder="e.g. COL Financial, IC Markets, Exness")
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
            st.success(f"Added {ticker} to your portfolio tracker!")
            st.rerun()

    if not df_invest.empty:
        df_invest["Total Value"] = df_invest["Shares/Lots"] * df_invest["Current Price"]
        df_invest["Total Cost"] = df_invest["Shares/Lots"] * df_invest["Avg Buy Price"]
        df_invest["Profit / Loss"] = df_invest["Total Value"] - df_invest["Total Cost"]

        st.dataframe(df_invest, use_container_width=True, hide_index=True)
        col_tot1, col_tot2 = st.columns(2)
        with col_tot1: st.metric("Total Portfolio Equity", f"${df_invest['Total Value'].sum():,.2f}")
        with col_tot2:
            tot_pnl = df_invest["Profit / Loss"].sum()
            st.metric("Total Un-realized P&L", f"${tot_pnl:,.2f}", delta=f"${tot_pnl:,.2f}")

        if st.button("Clear Investment Ledger"):
            if os.path.exists(INVEST_FILE): os.remove(INVEST_FILE)
            st.rerun()

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
        total_exp_bhd = df_expenses["Amount (BHD)"].sum() if not df_expenses.empty else 0.0
        report_content = f"""
==================================================
ROGEE FINANCIAL COMMAND CENTER - EXECUTIVE REPORT
==================================================
User Profile   : {current_user}
Report Date    : {rep_date}
Bahrain Time   : {bh_time.strftime("%Y-%m-%d %I:%M %p")}
Philippine Time: {ph_time.strftime("%Y-%m-%d %I:%M %p")}
Exchange Rate  : 1 BHD = {bhd_to_php:,.2f} PHP = ${bhd_to_usd:,.2f} USD
Framework      : {framework_title} (Debts: {debts_pct}%, Needs: {needs_pct}%, Wants: {wants_pct}%, Savings: {savings_pct}%)

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
- Debts & Credits ({debts_pct}% Target) : BD {actual_debts_bhd:,.2f}
- Needs ({needs_pct}% Target)     : BD {actual_needs_bhd:,.2f}
- Wants ({wants_pct}% Target)     : BD {actual_wants_bhd:,.2f}
- Savings ({savings_pct}% Target) : BD {actual_savings_bhd:,.2f}
--------------------------------------------------
GRAND TOTAL EXPENSES     : BD {total_exp_bhd:,.2f}
NET REMAINING CASH       : BD {(total_income_bhd - total_exp_bhd):,.2f}
==================================================
"""
        st.download_button(label="📥 Download Executive Summary (.TXT)", data=report_content, file_name=f"financial_summary_{current_user.lower().replace(' ', '_')}.txt", mime="text/plain", use_container_width=True)

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
