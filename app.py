import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import os
import json
import requests
import base64

# Page Configuration
st.set_page_config(
    page_title="Rogee Financial Command Center",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Mobile Polish & Dark Mode Visibility
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

    /* Metric Boxes Visibility in Dark & Light Modes */
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

# User Profiles Configuration
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

# Live Forex Rates Fetcher
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
    except Exception:
        pass
    return base_rates, False, datetime.now().strftime("%Y-%m-%d %H:%M (Benchmark)")

rates_dict, is_live_rates, last_rate_update = fetch_live_rates()

# Authentication Check
def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = None
    if not st.session_state["authenticated"]:
        st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🔐 Rogee&apos;s Financial Command Center</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B7280;'>Select account profile and enter your private access key.</p>", unsafe_allow_html=True)
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

# Data Loaders & Savers
def load_data(file_path):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"]).dt.date
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=["Date", "Main Category", "Sub Category", "Merchant/Description", "Amount", "Currency", "Amount (BHD)", "Payment Method"])

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

def load_user_config(file_path):
    defaults = {
        "salary_bhd": 1500.0,
        "business_bhd": 0.0,
        "sidelines_bhd": 0.0,
        "other_income_bhd": 0.0,
        "fixed_priority_bhd": 300.0,
        "debts_pct": 15,
        "needs_pct": 45,
        "wants_pct": 20,
        "savings_pct": 20,
        "display_curr": "BHD (BD)"
    }
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                saved = json.load(f)
                defaults.update(saved)
        except Exception:
            pass
    return defaults

def save_user_config(file_path, config_dict):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=4)
    except Exception:
        pass

df_expenses = load_data(DATA_FILE)
saved_config = load_user_config(CONFIG_FILE)

# Sidebar Settings
st.sidebar.title(f"⚙️ Settings ({current_user})")

curr_options = ["BHD (BD)", "PHP (₱)", "USD ($)"]
curr_idx = curr_options.index(saved_config.get("display_curr", "BHD (BD)")) if saved_config.get("display_curr") in curr_options else 0
display_curr = st.sidebar.selectbox("Display Currency", curr_options, index=curr_idx)

# Conversion Rates
bhd_to_usd = rates_dict.get("USD", 1.0) / rates_dict.get("BHD", 0.377)
bhd_to_php = rates_dict.get("PHP", 58.50) / rates_dict.get("BHD", 0.377)

EXCHANGE_RATES = {
    "BHD": {"symbol": "BD ", "rate": 1.0, "name": "Bahraini Dinar"},
    "PHP": {"symbol": "₱", "rate": bhd_to_php, "name": "Philippine Peso"},
    "USD": {"symbol": "$", "rate": bhd_to_usd, "name": "US Dollar"}
}

curr_code = display_curr.split()[0]
curr_symbol = EXCHANGE_RATES[curr_code]["symbol"]
rate_mult = EXCHANGE_RATES[curr_code]["rate"]

st.sidebar.markdown("---")
st.sidebar.subheader("💵 Monthly Income Streams (BHD)")
salary_bhd = st.sidebar.number_input("Primary Salary (BHD)", min_value=0.0, value=float(saved_config.get("salary_bhd", 1500.0)), step=50.0)
business_bhd = st.sidebar.number_input("Business Income (BHD)", min_value=0.0, value=float(saved_config.get("business_bhd", 0.0)), step=50.0)
sidelines_bhd = st.sidebar.number_input("Sidelines / Freelance (BHD)", min_value=0.0, value=float(saved_config.get("sidelines_bhd", 0.0)), step=25.0)
other_income_bhd = st.sidebar.number_input("Other Income (BHD)", min_value=0.0, value=float(saved_config.get("other_income_bhd", 0.0)), step=25.0)

total_income_bhd = salary_bhd + business_bhd + sidelines_bhd + other_income_bhd
st.sidebar.info(f"**Total Income:** BD {total_income_bhd:,.2f} | ₱{total_income_bhd*bhd_to_php:,.2f} | ${total_income_bhd*bhd_to_usd:,.2f}")

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 Mandatory Priority Obligations")
fixed_priority_bhd = st.sidebar.number_input("100% Mandatory Payments (BHD)", min_value=0.0, value=float(saved_config.get("fixed_priority_bhd", 300.0)), step=25.0)

net_bhd_for_budget = max(0.0, total_income_bhd - fixed_priority_bhd)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 4-Category Allocation Sliders (%)")
debts_pct = st.sidebar.slider("Debts & Credits Target %", 0, 100, int(saved_config.get("debts_pct", 15)))
needs_pct = st.sidebar.slider("Needs Target %", 0, 100, int(saved_config.get("needs_pct", 45)))
wants_pct = st.sidebar.slider("Wants Target %", 0, 100, int(saved_config.get("wants_pct", 20)))
savings_pct = st.sidebar.slider("Savings & Investments Target %", 0, 100, int(saved_config.get("savings_pct", 20)))

total_pct = debts_pct + needs_pct + wants_pct + savings_pct
if total_pct != 100:
    st.sidebar.warning(f"Allocation total is {total_pct}%. It should sum to 100%.")

framework_title = f"{debts_pct}/{needs_pct}/{wants_pct}/{savings_pct} Framework"

# Auto-save configuration on change
current_config_state = {
    "salary_bhd": salary_bhd,
    "business_bhd": business_bhd,
    "sidelines_bhd": sidelines_bhd,
    "other_income_bhd": other_income_bhd,
    "fixed_priority_bhd": fixed_priority_bhd,
    "debts_pct": debts_pct,
    "needs_pct": needs_pct,
    "wants_pct": wants_pct,
    "savings_pct": savings_pct,
    "display_curr": display_curr
}
if current_config_state != saved_config:
    save_user_config(CONFIG_FILE, current_config_state)

st.sidebar.markdown("---")
if st.sidebar.button("🔒 Lock App / Log Out", use_container_width=True):
    st.session_state["authenticated"] = False
    st.session_state["current_user"] = None
    st.rerun()

# Calculated Target Amounts
disp_total_income = total_income_bhd * rate_mult
disp_fixed = fixed_priority_bhd * rate_mult
disp_net_budget = net_bhd_for_budget * rate_mult

debts_target = disp_net_budget * (debts_pct / 100.0)
needs_target = disp_net_budget * (needs_pct / 100.0)
wants_target = disp_net_budget * (wants_pct / 100.0)
savings_target = disp_net_budget * (savings_pct / 100.0)

# Dual Timestamps
now_utc = datetime.now(timezone.utc)
bh_time = now_utc.astimezone(timezone(timedelta(hours=3)))
ph_time = now_utc.astimezone(timezone(timedelta(hours=8)))

# Main App Header & Clocks
st.markdown('<div class="main-header">💰 Rogee&apos;s Financial Command Center</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Multi-Currency Personal Finance Manager &nbsp;|&nbsp; <b>{framework_title}</b></div>', unsafe_allow_html=True)

st.markdown(f'''
<div class="time-badge">
    🇧🇭 <b>Bahrain:</b> {bh_time.strftime("%d %b %Y, %I:%M %p")} &nbsp;|&nbsp; 
    🇵🇭 <b>Philippines:</b> {ph_time.strftime("%d %b %Y, %I:%M %p")} &nbsp;|&nbsp; 
    👤 <b>Account:</b> {current_user}
</div>
''', unsafe_allow_html=True)

# Exchange Rate Status Bar
rate_mode_str = "🟢 Live API" if is_live_rates else "⚠️ Benchmark Rates"
st.markdown(f'<div class="rate-card">🌐 <b>Live Exchange Engine ({rate_mode_str}):</b> <b>1 BHD</b> = <b>₱{bhd_to_php:,.2f} PHP</b> | <b>1 BHD</b> = <b>${bhd_to_usd:,.2f} USD</b> | <b>1 USD</b> = <b>₱{bhd_to_php/bhd_to_usd:,.2f} PHP</b> <span style="float: right; color: #6B7280; font-size: 0.8rem;">Updated: {last_rate_update}</span></div>', unsafe_allow_html=True)

# Navigation Tabs
tab_dash, tab_add, tab_history, tab_forex, tab_invest, tab_reports, tab_guide = st.tabs([
    "📈 Dashboard",
    "➕ Record Expense",
    "📜 Transaction History",
    "💱 Live Forex",
    "📊 MT5 & COL Investments",
    "📥 Download Reports",
    "📘 User Guide"
])

# Actual Spending Calculations
if not df_expenses.empty:
    actual_priority_bhd = df_expenses[df_expenses["Main Category"].str.contains("100%", na=False)]["Amount (BHD)"].sum()
    actual_debts_bhd = df_expenses[df_expenses["Main Category"].str.contains("Debts", na=False)]["Amount (BHD)"].sum()
    actual_needs_bhd = df_expenses[df_expenses["Main Category"].str.contains("Needs", na=False)]["Amount (BHD)"].sum()
    actual_wants_bhd = df_expenses[df_expenses["Main Category"].str.contains("Wants", na=False)]["Amount (BHD)"].sum()
    actual_savings_bhd = df_expenses[df_expenses["Main Category"].str.contains("Savings", na=False)]["Amount (BHD)"].sum()
else:
    actual_priority_bhd = actual_debts_bhd = actual_needs_bhd = actual_wants_bhd = actual_savings_bhd = 0.0

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
    m1.metric("Gross Monthly Income", f"{curr_symbol}{disp_total_income:,.2f}")
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
    st.caption(f"Allocations calculated from remaining net budget: **{curr_symbol}{disp_net_budget:,.2f}** (Income minus 100% Priority Payments).")

    cat_data = [
        {"Category": f"Debts & Credits ({debts_pct}%)", "Target Allocation": f"{debts_pct}%", f"Target ({curr_code})": debts_target, f"Actual Spent ({curr_code})": actual_debts_disp, f"Difference ({curr_code})": debts_target - actual_debts_disp, "Status": "On Track" if actual_debts_disp <= debts_target else "Over Target"},
        {"Category": f"Needs ({needs_pct}%)", "Target Allocation": f"{needs_pct}%", f"Target ({curr_code})": needs_target, f"Actual Spent ({curr_code})": actual_needs_disp, f"Difference ({curr_code})": needs_target - actual_needs_disp, "Status": "On Track" if actual_needs_disp <= needs_target else "Over Target"},
        {"Category": f"Wants ({wants_pct}%)", "Target Allocation": f"{wants_pct}%", f"Target ({curr_code})": wants_target, f"Actual Spent ({curr_code})": actual_wants_disp, f"Difference ({curr_code})": wants_target - actual_wants_disp, "Status": "On Track" if actual_wants_disp <= wants_target else "Over Target"},
        {"Category": f"Savings & Investments ({savings_pct}%)", "Target Allocation": f"{savings_pct}%", f"Target ({curr_code})": savings_target, f"Actual Spent ({curr_code})": actual_savings_disp, f"Difference ({curr_code})": actual_savings_disp - savings_target, "Status": "Target Met" if actual_savings_disp >= savings_target else "Under Goal"}
    ]
    df_cat_summary = pd.DataFrame(cat_data)
    st.dataframe(df_cat_summary.style.format({
        f"Target ({curr_code})": f"{curr_symbol}{{:,.2f}}",
        f"Actual Spent ({curr_code})": f"{curr_symbol}{{:,.2f}}",
        f"Difference ({curr_code})": f"{curr_symbol}{{:,.2f}}"
    }), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("📊 Category Charts & Multi-Month Expense Analytics")

    if not df_expenses.empty:
        df_exp_copy = df_expenses.copy()
        df_exp_copy["YearMonth"] = pd.to_datetime(df_exp_copy["Date"]).dt.strftime("%Y-%m")
        df_exp_copy["DispAmount"] = df_exp_copy["Amount (BHD)"] * rate_mult

        col_ch1, col_ch2 = st.columns(2)
        with col_ch1:
            st.markdown("#### Target vs. Actual Spending")
            chart_df = pd.DataFrame({
                "Category": ["Debts", "Needs", "Wants", "Savings"],
                "Target": [debts_target, needs_target, wants_target, savings_target],
                "Actual": [actual_debts_disp, actual_needs_disp, actual_wants_disp, actual_savings_disp]
            })
            fig_bar = go.Figure(data=[
                go.Bar(name='Target', x=chart_df['Category'], y=chart_df['Target'], marker_color='#93C5FD'),
                go.Bar(name='Actual', x=chart_df['Category'], y=chart_df['Actual'], marker_color='#1D4ED8')
            ])
            fig_bar.update_layout(barmode='group', yaxis_title=f"Amount ({curr_code})", margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_ch2:
            st.markdown("#### Overall Expense Share")
            fig_pie = px.pie(
                df_exp_copy,
                values='DispAmount',
                names='Main Category',
                hole=0.45,
                color_discrete_sequence=['#EF4444', '#8B5CF6', '#2563EB', '#F59E0B', '#10B981']
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("#### Monthly Expense Comparison Over Time")
        monthly_trend = df_exp_copy.groupby(['YearMonth', 'Main Category'])['DispAmount'].sum().reset_index()
        fig_trend = px.bar(
            monthly_trend,
            x='YearMonth',
            y='DispAmount',
            color='Main Category',
            barmode='stack',
            labels={'DispAmount': f'Amount ({curr_code})', 'YearMonth': 'Month'}
        )
        fig_trend.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown("#### Multi-Month Category Summary Matrix")
        pivot_df = df_exp_copy.pivot_table(index='YearMonth', columns='Main Category', values='DispAmount', aggfunc='sum', fill_value=0.0)
        pivot_df['Total Monthly Spent'] = pivot_df.sum(axis=1)
        st.dataframe(pivot_df.style.format(f"{curr_symbol}{{:,.2f}}"), use_container_width=True)
    else:
        st.info("No expense data recorded yet. Add your first payment in the 'Record Expense' tab!")

# TAB 2: RECORD EXPENSE
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
                sub_cats = ["Credit Card Payment", "Personal / Bank Loan", "Car Loan / Auto Financing", "Housing Loan / Mortgage", "Other Debt Payoff"]
            elif "Needs" in main_cat:
                sub_cats = ["Housing / Rent / Mortgage", "Utilities & Bills", "Groceries", "Transportation / Fuel", "Healthcare / Insurance", "Minimum Debt Payments"]
            elif "Wants" in main_cat:
                sub_cats = ["Dining Out & Coffee", "Entertainment & Streaming", "Shopping & Apparel", "Hobbies & Travel", "Subscriptions", "Miscellaneous"]
            else:
                sub_cats = ["Emergency Fund", "Retirement / 401(k) / IRA", "Stock Investments (COL / Brokerage)", "Forex & Trading Deposit", "Major Goal Savings"]

            sub_cat = st.selectbox("Sub-Category", sub_cats)

        with col_b:
            merchant = st.text_input("Merchant / Description / Payee", placeholder="e.g. Helper Salary, Bank Loan, Grocery")
            amount_input = st.number_input("Amount", min_value=0.01, step=5.0, value=25.0)
            input_currency = st.selectbox("Payment Currency", ["BHD", "PHP", "USD"], index=0)
            payment_method = st.selectbox("Payment Method", ["Bank Transfer", "Credit Card", "Debit Card", "Cash", "Benefit Pay", "Remittance"])

        submit_btn = st.form_submit_button("Save Payment Record", use_container_width=True)
        if submit_btn:
            if input_currency == "BHD":
                amount_bhd = amount_input
            elif input_currency == "PHP":
                amount_bhd = amount_input / bhd_to_php
            else:
                amount_bhd = amount_input / bhd_to_usd

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

# TAB 3: TRANSACTION HISTORY (WITH EDIT & DELETE)
with tab_history:
    st.subheader(f"📜 Recorded Transaction History ({current_user})")

    if not df_expenses.empty:
        total_recorded_bhd = df_expenses["Amount (BHD)"].sum() if "Amount (BHD)" in df_expenses.columns else df_expenses["Amount"].sum()
        total_recorded_disp = total_recorded_bhd * rate_mult

        st.info(f"💰 **Total Recorded Expenses: {curr_symbol}{total_recorded_disp:,.2f}** (BD {total_recorded_bhd:,.2f} | ₱{total_recorded_bhd*bhd_to_php:,.2f} | ${total_recorded_bhd*bhd_to_usd:,.2f})")

        st.caption("✏️ **How to Edit or Delete:** Double-click any cell to modify values directly. Select checkbox rows to delete them, then click **💾 Save Ledger Changes**!")

        # Interactive Editable Data Grid
        edited_df = st.data_editor(
            df_expenses.sort_values(by="Date", ascending=False),
            num_rows="dynamic",
            use_container_width=True,
            key=f"expense_editor_{current_user}"
        )

        col_hist1, col_hist2 = st.columns(2)
        with col_hist1:
            if st.button("💾 Save Ledger Changes", type="primary", use_container_width=True):
                save_data(edited_df, DATA_FILE)
                st.success("Transaction history updated and saved successfully!")
                st.rerun()

        with col_hist2:
            if st.button("🗑️ Clear Entire History", use_container_width=True):
                if os.path.exists(DATA_FILE):
                    os.remove(DATA_FILE)
                st.success("All transaction logs cleared!")
                st.rerun()
    else:
        st.info("No transaction history found. Start recording payments in the 'Record Expense' tab!")

# TAB 4: LIVE FOREX ENGINE
with tab_forex:
    st.subheader("💱 Live Forex Rate Engine & Pair Selector")

    fx_col1, fx_col2 = st.columns(2)
    with fx_col1:
        st.markdown("#### Currency Pair Cross Calculator")
        calc_amt = st.number_input("Amount to Convert", min_value=1.0, value=100.0, step=10.0)
        pair_from = st.selectbox("From Currency", ["BHD", "PHP", "USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"], index=0)
        pair_to = st.selectbox("To Currency", ["PHP", "USD", "BHD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"], index=0)

        rate_from_usd = rates_dict.get(pair_from, 1.0)
        rate_to_usd = rates_dict.get(pair_to, 1.0)
        cross_rate = rate_to_usd / rate_from_usd
        converted_val = calc_amt * cross_rate

        st.success(f"### {calc_amt:,.2f} {pair_from} = **{converted_val:,.2f} {pair_to}**")
        st.info(f"💡 **Exchange Rate:** 1 {pair_from} = {cross_rate:.4f} {pair_to}")

    with fx_col2:
        st.markdown("#### Major Forex Pairs Live Ticker")
        st.write(f"* **BHD → PHP:** ₱{rates_dict.get('PHP', 58.5)/rates_dict.get('BHD', 0.377):,.2f}")
        st.write(f"* **BHD → USD:** ${rates_dict.get('USD', 1.0)/rates_dict.get('BHD', 0.377):,.2f}")
        st.write(f"* **USD → PHP:** ₱{rates_dict.get('PHP', 58.5)/rates_dict.get('USD', 1.0):,.2f}")
        st.write(f"* **USD → CHF:** {rates_dict.get('CHF', 0.865):,.4f}")
        st.write(f"* **AUD → CAD:** {rates_dict.get('CAD', 1.38)/rates_dict.get('AUD', 1.51):,.4f}")
        st.write(f"* **NZD → USD:** ${1.0/rates_dict.get('NZD', 1.66):,.4f}")

        if st.button("🔄 Force Refresh Live Rates Now", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

# TAB 5: MT5 & COL INVESTMENTS & CALCULATORS
with tab_invest:
    st.subheader("📊 MT5 Forex & COL Financial Portfolio Manager")
    st.caption("Track MetaTrader 5 trading accounts, COL Financial stock equity, and calculate Pip Values & Margins.")

    # Pip & Margin Calculators
    st.markdown("---")
    st.markdown("### 🧮 Live Trading Calculators (Pip & Margin)")
    c_calc1, c_calc2 = st.columns(2)

    with c_calc1:
        st.markdown("#### 📍 Pip Value Calculator")
        calc_symbol = st.selectbox("Symbol / Pair", ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD (Gold)", "USDCHF", "AUDUSD"], index=0)
        calc_lots = st.number_input("Lot Size", min_value=0.01, step=0.01, value=1.0)
        calc_acc_curr = st.selectbox("Account Currency", ["USD", "BHD", "PHP"], index=0)

        # Pip value math
        if "JPY" in calc_symbol:
            pip_usd = calc_lots * 1000.0  # 1 pip = 0.01 in JPY pairs
        elif "XAU" in calc_symbol:
            pip_usd = calc_lots * 10.0    # 1 pip/point in Gold
        else:
            pip_usd = calc_lots * 10.0    # 1 pip = 0.0001 = $10 per lot

        if calc_acc_curr == "USD":
            pip_val_disp = pip_usd
            pip_sym = "$"
        elif calc_acc_curr == "BHD":
            pip_val_disp = pip_usd * rates_dict.get("BHD", 0.377)
            pip_sym = "BD "
        else:
            pip_val_disp = pip_usd * rates_dict.get("PHP", 58.50)
            pip_sym = "₱"

        st.success(f"**Pip Value:** `{pip_sym}{pip_val_disp:,.2f}` per 1 Pip")

    with c_calc2:
        st.markdown("#### 🛡️ Required Margin Calculator")
        m_symbol = st.selectbox("Pair Symbol", ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"], index=0)
        m_lots = st.number_input("Trade Volume (Lots)", min_value=0.01, step=0.01, value=1.0, key="m_lots")
        leverage = st.selectbox("Leverage", [100, 200, 500, 1000], index=2)

        contract_size = 100000 if "XAU" not in m_symbol and "BTC" not in m_symbol else (100 if "XAU" in m_symbol else 1)
        req_margin_usd = (m_lots * contract_size) / leverage
        st.success(f"**Required Margin:** `${req_margin_usd:,.2f} USD` (at 1:{leverage} Leverage)")

    st.markdown("---")
    st.markdown("### 💼 Portfolio Holdings Ledger")

    df_invest = load_data(INVEST_FILE)
    if df_invest.empty:
        df_invest = pd.DataFrame(columns=["Type", "Symbol/Ticker", "Platform", "Shares/Lots", "Avg Buy Price", "Current Price", "Notes"])

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
            save_data(df_invest, INVEST_FILE)
            st.success(f"Added {ticker} to your investment tracker!")
            st.rerun()

    if not df_invest.empty:
        df_invest["Total Value"] = df_invest["Shares/Lots"] * df_invest["Current Price"]
        df_invest["Total Cost"] = df_invest["Shares/Lots"] * df_invest["Avg Buy Price"]
        df_invest["Profit / Loss"] = df_invest["Total Value"] - df_invest["Total Cost"]
        df_invest["Gain %"] = (df_invest["Profit / Loss"] / df_invest["Total Cost"]) * 100

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

# TAB 6: REPORTS & EXPORT
with tab_reports:
    st.subheader("📥 Download Financial Reports & Data")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("#### 📊 CSV Transaction Ledger")
        if not df_expenses.empty:
            csv_data = df_expenses.to_csv(index=False).encode("utf-8")
            st.download_button(label="📥 Download CSV Ledger", data=csv_data, file_name=f"financial_ledger_{current_user.lower().replace(' ', '_')}.csv", mime="text/csv", use_container_width=True)
        else:
            st.info("No transaction records available to export.")

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
- Debts ({debts_pct}% Target)     : BD {actual_debts_bhd:,.2f}
- Needs ({needs_pct}% Target)     : BD {actual_needs_bhd:,.2f}
- Wants ({wants_pct}% Target)     : BD {actual_wants_bhd:,.2f}
- Savings ({savings_pct}% Target)   : BD {actual_savings_bhd:,.2f}
--------------------------------------------------
GRAND TOTAL EXPENSES     : BD {total_exp_bhd:,.2f}
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
