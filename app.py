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

# Custom Styling with Dark Mode Contrast Fixes
st.markdown("""
<style>
    .main-header { font-size: 1.8rem; font-weight: 800; color: #1E3A8A; margin-bottom: 0.1rem; line-height: 1.2; }
    .sub-header { font-size: 0.95rem; color: #4B5563; margin-bottom: 0.8rem; }
    .time-badge { background-color: #F3F4F6; border: 1px solid #E5E7EB; color: #1F2937 !important; padding: 6px 12px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; margin-bottom: 12px; display: inline-block; width: 100%; text-align: center; }
    
    /* Contrast Containers */
    .priority-banner { background-color: #FEF2F2; border: 1px solid #FECACA; border-left: 5px solid #EF4444; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; color: #111827 !important; }
    .priority-banner * { color: #111827 !important; }
    
    .income-card { background-color: #F0FDF4; border: 1px solid #BBF7D0; border-left: 5px solid #22C55E; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; color: #111827 !important; }
    .income-card * { color: #111827 !important; }
    
    .rate-card { background-color: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #3B82F6; padding: 8px 12px; border-radius: 6px; margin-bottom: 12px; font-size: 0.85rem; color: #111827 !important; }
    .rate-card * { color: #111827 !important; }
    
    /* Metrics Visibility Fix */
    .stMetric { background-color: #F9FAFB !important; padding: 8px; border-radius: 6px; border: 1px solid #E5E7EB !important; }
    div[data-testid="stMetricValue"] { font-size: 1.15rem !important; font-weight: 800 !important; color: #1E3A8A !important; }
    div[data-testid="stMetricLabel"] { color: #374151 !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

# User Profiles Configuration (Added User 4)
USER_PROFILES = {
    "Rogee": {
        "sec_key": "ROGEE_KEY",
        "def_key": "rogee2026",
        "data_file": "expenses_rogee.csv",
        "config_file": "config_rogee.json",
        "invest_file": "investments_rogee.csv"
    },
    "User 2": {
        "sec_key": "USER2_KEY",
        "def_key": "user2026",
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

# Live FX Engine
@st.cache_data(ttl=3600)
def fetch_live_rates():
    base_rates = {
        "USD": 1.0, "BHD": 0.377, "PHP": 58.50, "EUR": 0.92,
        "GBP": 0.78, "JPY": 152.0, "CHF": 0.865, "AUD": 1.51,
        "CAD": 1.38, "NZD": 1.66
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
                    if k not in fetched: fetched[k] = v
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
        st.markdown("<p style='text-align: center; color: #6B7280;'>Select profile and enter your private access key to unlock dashboard.</p>", unsafe_allow_html=True)
        
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

# Data & Config Loaders
def load_user_config():
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

def load_data(file_path):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df["Date"] = pd.to_datetime(df["Date"]).dt.date
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=["Date", "Main Category", "Sub Category", "Merchant/Description", "Amount", "Currency", "Amount (BHD)", "Payment Method"])

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

def load_investments(file_path):
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except Exception:
            pass
    return pd.DataFrame(columns=["Type", "Symbol/Ticker", "Platform", "Shares/Lots", "Avg Buy Price", "Current Price", "Notes"])

user_cfg = load_user_config()
df_expenses = load_data(DATA_FILE)
df_invest = load_investments(INVEST_FILE)

# SIDEBAR: SETTINGS & TARGETS
st.sidebar.title(f"⚙️ Settings ({current_user})")

st.sidebar.subheader("💱 Currency Display")
display_curr = st.sidebar.selectbox("Display Currency", ["BHD (BD)", "PHP (₱)", "USD ($)"], index=["BHD (BD)", "PHP (₱)", "USD ($)"].index(user_cfg.get("display_curr", "BHD (BD)")))

EXCHANGE_RATES = {
    "BHD": {"symbol": "BD ", "rate": 1.0, "name": "Bahraini Dinar"},
    "PHP": {"symbol": "₱", "rate": float(rates_dict.get("PHP", 58.50) / rates_dict.get("BHD", 0.377)), "name": "Philippine Peso"},
    "USD": {"symbol": "$", "rate": float(rates_dict.get("USD", 1.0) / rates_dict.get("BHD", 0.377)), "name": "US Dollar"}
}

curr_code = display_curr.split()[0]
curr_symbol = EXCHANGE_RATES[curr_code]["symbol"]
rate_mult = EXCHANGE_RATES[curr_code]["rate"]
bhd_to_php = EXCHANGE_RATES["PHP"]["rate"]
bhd_to_usd = EXCHANGE_RATES["USD"]["rate"]

st.sidebar.markdown("---")
st.sidebar.subheader("💵 Income Streams (BHD)")
salary_bhd = st.sidebar.number_input("Primary Salary (BHD)", min_value=0.0, value=float(user_cfg["salary_bhd"]), step=50.0)
business_bhd = st.sidebar.number_input("Business Income (BHD)", min_value=0.0, value=float(user_cfg["business_bhd"]), step=50.0)
sidelines_bhd = st.sidebar.number_input("Sidelines / Freelance (BHD)", min_value=0.0, value=float(user_cfg["sidelines_bhd"]), step=50.0)
other_income_bhd = st.sidebar.number_input("Other Income (BHD)", min_value=0.0, value=float(user_cfg["other_income_bhd"]), step=50.0)

total_income_bhd = salary_bhd + business_bhd + sidelines_bhd + other_income_bhd

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 100% Priority & Mandatory Obligations")
fixed_priority_bhd = st.sidebar.number_input("Mandatory Obligations Target (BHD)", min_value=0.0, value=float(user_cfg["fixed_priority_bhd"]), step=25.0)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 4-Category Allocation Framework Targets (%)")
st.sidebar.caption("Allocations applied to net budget after deducting 100% priority obligations.")

debts_pct = st.sidebar.slider("Debts & Credits Target %", 0, 100, int(user_cfg.get("debts_pct", 15)))
needs_pct = st.sidebar.slider("Needs Target % (Essentials)", 0, 100, int(user_cfg.get("needs_pct", 45)))
wants_pct = st.sidebar.slider("Wants Target % (Lifestyle)", 0, 100, int(user_cfg.get("wants_pct", 20)))
savings_pct = st.sidebar.slider("Savings & Investments Target %", 0, 100, int(user_cfg.get("savings_pct", 20)))

total_alloc_pct = debts_pct + needs_pct + wants_pct + savings_pct
if total_alloc_pct != 100:
    st.sidebar.warning(f"Total allocation is {total_alloc_pct}%. It should equal 100%.")

# Save updated config
updated_cfg = {
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
save_user_config(updated_cfg)

# Calculate Targets
net_bhd_for_budget = max(0.0, total_income_bhd - fixed_priority_bhd)

disp_total_income = total_income_bhd * rate_mult
disp_fixed = fixed_priority_bhd * rate_mult
disp_net_budget = net_bhd_for_budget * rate_mult

debts_target = disp_net_budget * (debts_pct / 100.0)
needs_target = disp_net_budget * (needs_pct / 100.0)
wants_target = disp_net_budget * (wants_pct / 100.0)
savings_target = disp_net_budget * (savings_pct / 100.0)

framework_title = f"{debts_pct}/{needs_pct}/{wants_pct}/{savings_pct} Framework"

st.sidebar.markdown("---")
if st.sidebar.button("🔒 Lock / Log Out", use_container_width=True):
    st.session_state["authenticated"] = False
    st.session_state["current_user"] = None
    st.rerun()

# DUAL REGIONAL CLOCKS
now_utc = datetime.now(timezone.utc)
bh_time = now_utc + timedelta(hours=3)
ph_time = now_utc + timedelta(hours=8)

# MAIN HEADER & DUAL TIME BADGE
st.markdown('<div class="main-header">💰 Rogee Financial Command Center</div>', unsafe_allow_html=True)
st.markdown(f'<div class="time-badge">🇧🇭 <b>Bahrain:</b> {bh_time.strftime("%d %b %Y, %I:%M %p")} &nbsp;|&nbsp; 🇵🇭 <b>Philippines:</b> {ph_time.strftime("%d %b %Y, %I:%M %p")} &nbsp;|&nbsp; 👤 <b>Account:</b> {current_user}</div>', unsafe_allow_html=True)

# LIVE FX RATE CARD
rate_mode_str = "🟢 Live Auto-Updated Rate" if is_live_rates else "⚠️ Benchmark Exchange Rates"
st.markdown(f'<div class="rate-card">🌐 <b>Live FX Engine ({rate_mode_str}):</b> <b>1 BHD</b> = <b>₱{bhd_to_php:,.2f} PHP</b> | <b>1 BHD</b> = <b>${bhd_to_usd:,.2f} USD</b> | <b>1 USD</b> = <b>₱{(bhd_to_php/bhd_to_usd):,.2f} PHP</b><span style="float: right; color: #6B7280; font-size: 0.8rem;">Updated: {last_rate_update}</span></div>', unsafe_allow_html=True)

# MAIN TABS
tab_dash, tab_add, tab_history, tab_forex, tab_invest, tab_reports, tab_guide = st.tabs([
    "📈 Dashboard & Analytics",
    "➕ Record Expense",
    "📜 Transaction History",
    "💱 Live Forex Engine",
    "📊 MT5 & COL Investments",
    "📥 Download Reports",
    "📘 User Guide"
])

# Actual Spending Calculations
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
    st.subheader(f"📊 {framework_title} Net Allocation Benchmark Breakdown")
    st.caption(f"Targets calculated from net budget: **{curr_symbol}{disp_net_budget:,.2f}** (Income minus 100% Priority Payments).")

    cat_data = [
        {"Category": f"Debts & Credits ({debts_pct}%)", "Target %": f"{debts_pct}%", f"Target ({curr_code})": debts_target, f"Actual Spent ({curr_code})": actual_debts_disp, f"Difference ({curr_code})": debts_target - actual_debts_disp, "Status": "On Track" if actual_debts_disp <= debts_target else "Over Target"},
        {"Category": f"Needs ({needs_pct}%)", "Target %": f"{needs_pct}%", f"Target ({curr_code})": needs_target, f"Actual Spent ({curr_code})": actual_needs_disp, f"Difference ({curr_code})": needs_target - actual_needs_disp, "Status": "On Track" if actual_needs_disp <= needs_target else "Over Target"},
        {"Category": f"Wants ({wants_pct}%)", "Target %": f"{wants_pct}%", f"Target ({curr_code})": wants_target, f"Actual Spent ({curr_code})": actual_wants_disp, f"Difference ({curr_code})": wants_target - actual_wants_disp, "Status": "On Track" if actual_wants_disp <= wants_target else "Over Target"},
        {"Category": f"Savings & Investments ({savings_pct}%)", "Target %": f"{savings_pct}%", f"Target ({curr_code})": savings_target, f"Actual Spent ({curr_code})": actual_savings_disp, f"Difference ({curr_code})": actual_savings_disp - savings_target, "Status": "Target Met" if actual_savings_disp >= savings_target else "Under Goal"}
    ]
    df_cat_summary = pd.DataFrame(cat_data)
    
    st.dataframe(
        df_cat_summary.style.format({
            f"Target ({curr_code})": f"{curr_symbol}{{:,.2f}}",
            f"Actual Spent ({curr_code})": f"{curr_symbol}{{:,.2f}}",
            f"Difference ({curr_code})": f"{curr_symbol}{{:,.2f}}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.subheader("📈 Interactive Multi-Category Visualizations")

    c_ch1, c_ch2 = st.columns(2)
    with c_ch1:
        st.markdown("#### Target vs. Actual Category Allocation")
        chart_df = pd.DataFrame({
            "Category": ["Debts/Credits", "Needs", "Wants", "Savings/Invest"],
            "Target": [debts_target, needs_target, wants_target, savings_target],
            "Actual": [actual_debts_disp, actual_needs_disp, actual_wants_disp, actual_savings_disp]
        })
        fig_bar = go.Figure(data=[
            go.Bar(name='Target', x=chart_df['Category'], y=chart_df['Target'], marker_color='#93C5FD'),
            go.Bar(name='Actual', x=chart_df['Category'], y=chart_df['Actual'], marker_color='#1D4ED8')
        ])
        fig_bar.update_layout(
            barmode='group',
            yaxis_title=f"Amount ({curr_code})",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c_ch2:
        st.markdown("#### Expense Share Across All Categories")
        if total_spent_disp > 0:
            fig_pie = px.pie(
                values=[actual_priority_disp, actual_debts_disp, actual_needs_disp, actual_wants_disp, actual_savings_disp],
                names=["100% Priority", "Debts & Credits", "Needs", "Wants", "Savings & Invest"],
                color_discrete_sequence=['#EF4444', '#8B5CF6', '#2563EB', '#F59E0B', '#10B981'],
                hole=0.45
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expense records logged yet. Add your first payment in 'Record Expense'!")

    if not df_expenses.empty:
        st.markdown("---")
        st.markdown("#### Monthly Expense Comparison Over Time (Multi-Month Trend)")
        df_exp_copy = df_expenses.copy()
        df_exp_copy["YearMonth"] = pd.to_datetime(df_exp_copy["Date"]).dt.strftime("%Y-%m")
        df_exp_copy["DispAmount"] = df_exp_copy["Amount (BHD)"] * rate_mult

        monthly_trend = df_exp_copy.groupby(["YearMonth", "Main Category"])["DispAmount"].sum().reset_index()
        fig_trend = px.bar(
            monthly_trend, 
            x="YearMonth", 
            y="DispAmount", 
            color="Main Category", 
            barmode="stack",
            labels={"DispAmount": f"Amount ({curr_code})", "YearMonth": "Month"}
        )
        fig_trend.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown("#### Multi-Month Category Summary Matrix Table")
        pivot_df = df_exp_copy.pivot_table(index="YearMonth", columns="Main Category", values="DispAmount", aggfunc="sum", fill_value=0.0)
        pivot_df["Total Monthly Spent"] = pivot_df.sum(axis=1)
        st.dataframe(pivot_df.style.format(f"{curr_symbol}{{:,.2f}}"), use_container_width=True)

# TAB 2: RECORD A NEW PAYMENT
with tab_add:
    st.subheader(f"Record a New Payment / Expense ({current_user})")

    main_cat_options = [
        "100% Priority & People to Pay",
        f"Debts & Credits ({debts_pct}%)",
        f"Needs ({needs_pct}%)",
        f"Wants ({wants_pct}%)",
        f"Savings & Investments ({savings_pct}%)"
    ]

    with st.form("add_expense_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)

        with col_a:
            exp_date = st.date_input("Payment Date", value=datetime.today())
            main_cat = st.selectbox("Expense Category", main_cat_options)
            
            if "100%" in main_cat:
                sub_cats = ["People to Pay (Household Helper / Staff)", "Family Support & Remittance (100%)", "Direct Mandatory Loan / Debt", "Fixed Mandatory Utility / Bill"]
            elif "Debts" in main_cat:
                sub_cats = ["Credit Card Minimum/Full Payment", "Personal / Bank Loan Payoff", "Car Loan / Auto Financing", "Mortgage / Housing Loan", "Informal / Peer Debt Payoff"]
            elif "Needs" in main_cat:
                sub_cats = ["Housing / Rent / Mortgage", "Utilities & Bills", "Groceries", "Transportation / Fuel", "Healthcare / Insurance", "Childcare & Education"]
            elif "Wants" in main_cat:
                sub_cats = ["Dining Out & Coffee", "Entertainment & Streaming", "Shopping & Apparel", "Hobbies & Travel", "Subscriptions", "Miscellaneous"]
            else:
                sub_cats = ["Emergency Fund", "Stock Investments (COL / Brokerage)", "Forex & Trading Deposit (MT5)", "Mutual Funds / Index Funds", "Retirement / Pension", "Major Goal Savings"]

            sub_cat = st.selectbox("Sub-Category", sub_cats)

        with col_b:
            merchant = st.text_input("Merchant / Description / Payee", placeholder="e.g. Household Helper Salary, Landlord, BDO Credit Card, COL Deposit")
            amount_input = st.number_input("Amount", min_value=0.01, step=5.0, value=25.0)
            input_currency = st.selectbox("Payment Currency", ["BHD", "PHP", "USD"], index=0)
            payment_method = st.selectbox("Payment Method", ["Benefit Pay", "Remittance", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])

        submit_btn = st.form_submit_button("💾 Save Payment Record", use_container_width=True)

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

# TAB 3: TRANSACTION HISTORY
with tab_history:
    st.subheader(f"📜 Recorded Transaction History ({current_user})")

    if not df_expenses.empty:
        total_recorded_bhd = df_expenses["Amount (BHD)"].sum()
        total_recorded_disp = total_recorded_bhd * rate_mult

        st.info(f"💰 **Total Recorded Expenses: {curr_symbol}{total_recorded_disp:,.2f}** (BD {total_recorded_bhd:,.2f} | ₱{total_recorded_bhd*bhd_to_php:,.2f} | ${total_recorded_bhd*bhd_to_usd:,.2f})")

        cat_filter = st.multiselect("Filter by Category", options=main_cat_options, default=main_cat_options)
        
        filtered_df = df_expenses[df_expenses["Main Category"].isin(cat_filter)] if cat_filter else df_expenses
        st.dataframe(filtered_df.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)

        st.markdown("---")
        if st.button("🗑️ Clear All Expense Data", type="primary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.success("All transaction records cleared!")
            st.rerun()
    else:
        st.info("No transaction records found. Start adding payments in 'Record Expense'!")

# TAB 4: LIVE FOREX ENGINE
with tab_forex:
    st.subheader("💱 Live Multi-Currency Converter & Major Pairs Dashboard")

    fx_col1, fx_col2 = st.columns(2)

    with fx_col1:
        st.markdown("#### Live Pair Converter")
        calc_amt = st.number_input("Amount to Convert", min_value=1.0, value=100.0, step=10.0)
        pair_from = st.selectbox("From Currency", ["BHD", "PHP", "USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"], index=0)
        pair_to = st.selectbox("To Currency", ["PHP", "USD", "BHD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"], index=0)

        rate_from_usd = float(rates_dict.get(pair_from, 1.0))
        rate_to_usd = float(rates_dict.get(pair_to, 1.0))

        cross_rate = rate_to_usd / rate_from_usd if rate_from_usd > 0 else 1.0
        converted_val = calc_amt * cross_rate

        st.success(f"### {calc_amt:,.2f} {pair_from} = **{converted_val:,.2f} {pair_to}**")
        st.info(f"💡 **Cross Exchange Rate:** 1 {pair_from} = {cross_rate:,.4f} {pair_to}")

    with fx_col2:
        st.markdown("#### Live Major & Cross Pairs Ticker")
        st.markdown(f"""
        * **1 BHD → PHP:** ₱{(rates_dict.get("PHP", 58.50)/rates_dict.get("BHD", 0.377)):,.2f} PHP
        * **1 BHD → USD:** ${(rates_dict.get("USD", 1.0)/rates_dict.get("BHD", 0.377)):,.2f} USD
        * **1 USD → PHP:** ₱{(rates_dict.get("PHP", 58.50)/rates_dict.get("USD", 1.0)):,.2f} PHP
        * **1 USD → CHF (USD/CHF):** {rates_dict.get("CHF", 0.865):,.4f} CHF
        * **1 AUD → CAD (AUD/CAD):** {(rates_dict.get("CAD", 1.38)/rates_dict.get("AUD", 1.51)):,.4f} CAD
        * **1 NZD → USD (NZD/USD):** {(rates_dict.get("USD", 1.0)/rates_dict.get("NZD", 1.66)):,.4f} USD
        * **1 EUR → USD (EUR/USD):** {(rates_dict.get("USD", 1.0)/rates_dict.get("EUR", 0.92)):,.4f} USD
        * **1 GBP → USD (GBP/USD):** {(rates_dict.get("USD", 1.0)/rates_dict.get("GBP", 0.78)):,.4f} USD
        """)

        if st.button("🔄 Force Refresh Live Rates Now"):
            st.cache_data.clear()
            st.rerun()

# TAB 5: MT5 & COL INVESTMENTS + FOREX CALCULATORS
with tab_invest:
    st.subheader("📊 MT5 Forex & COL Financial Portfolio Manager + Forex Calculators")

    st.markdown("---")
    st.markdown("### 🧮 Live MT5 Trading Calculators (Pip Value & Margin)")

    calc_col1, calc_col2 = st.columns(2)

    with calc_col1:
        st.markdown("#### 📍 Pip Value Calculator")
        pip_pair = st.selectbox("Trading Pair", ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD (Gold)", "USDCHF", "AUDUSD", "USDCAD"], index=0)
        lot_size = st.number_input("Lot Size (Standard Lots)", min_value=0.01, value=1.00, step=0.01)
        account_curr = st.selectbox("Account Base Currency", ["USD", "BHD", "PHP"], index=0)

        # Base 1 pip calculation
        if "JPY" in pip_pair:
            pip_val_usd = (0.01 / rates_dict.get("JPY", 152.0)) * (lot_size * 100000)
        elif "XAUUSD" in pip_pair:
            pip_val_usd = 0.10 * (lot_size * 100) # 1 pip = $0.10 per standard 100oz lot
        else:
            pip_val_usd = 10.0 * lot_size # $10 per pip for EURUSD/GBPUSD standard lot

        if account_curr == "USD":
            pip_val_disp = pip_val_usd
            symbol_p = "$"
        elif account_curr == "BHD":
            pip_val_disp = pip_val_usd * 0.377
            symbol_p = "BD "
        else:
            pip_val_disp = pip_val_usd * float(rates_dict.get("PHP", 58.50))
            symbol_p = "₱"

        st.success(f"**Value of 1 Pip:** `{symbol_p}{pip_val_disp:,.2f} {account_curr}`")

    with calc_col2:
        st.markdown("#### 🛡️ Required Margin Calculator")
        m_pair = st.selectbox("Forex / Asset Pair", ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "USDCHF", "AUDUSD"], index=0, key="m_pair")
        m_lots = st.number_input("Trade Size (Lots)", min_value=0.01, value=1.00, step=0.01, key="m_lots")
        leverage = st.selectbox("Account Leverage", [100, 200, 400, 500, 1000], index=1)
        m_account_curr = st.selectbox("Account Currency", ["USD", "BHD", "PHP"], index=0, key="m_curr")

        contract_size = 100000 if "XAUUSD" not in m_pair else 100
        position_usd = m_lots * contract_size
        margin_usd = position_usd / leverage

        if m_account_curr == "USD":
            margin_disp = margin_usd
            symbol_m = "$"
        elif m_account_curr == "BHD":
            margin_disp = margin_usd * 0.377
            symbol_m = "BD "
        else:
            margin_disp = margin_usd * float(rates_dict.get("PHP", 58.50))
            symbol_m = "₱"

        st.success(f"**Required Margin:** `{symbol_m}{margin_disp:,.2f} {m_account_curr}` (at 1:{leverage} Leverage)")

    st.markdown("---")
    st.markdown("### 💼 Investment Holdings Ledger")

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

        inv_submit = st.form_submit_button("💾 Save Asset Record", use_container_width=True)
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
            st.success(f"Added {ticker} to your investment portfolio!")
            st.rerun()

    if not df_invest.empty:
        st.markdown("#### Current Investment Portfolio Ledger")
        df_invest["Total Value"] = df_invest["Shares/Lots"] * df_invest["Current Price"]
        df_invest["Total Cost"] = df_invest["Shares/Lots"] * df_invest["Avg Buy Price"]
        df_invest["Profit / Loss"] = df_invest["Total Value"] - df_invest["Total Cost"]
        df_invest["Gain %"] = (df_invest["Profit / Loss"] / df_invest["Total Cost"]) * 100

        st.dataframe(df_invest, use_container_width=True, hide_index=True)

        col_tot1, col_tot2 = st.columns(2)
        with col_tot1:
            st.metric("Total Portfolio Value ($)", f"${df_invest['Total Value'].sum():,.2f}")
        with col_tot2:
            tot_pnl = df_invest["Profit / Loss"].sum()
            st.metric("Total Un-realized P&L ($)", f"${tot_pnl:,.2f}", delta=f"${tot_pnl:,.2f}")

        if st.button("🗑️ Clear Investment Ledger"):
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

        report_content = f"""==================================================
ROGEE FINANCIAL COMMAND CENTER - EXECUTIVE REPORT
==================================================
User Profile   : {current_user}
Report Date    : {rep_date}
Bahrain Time   : {bh_time.strftime('%Y-%m-%d %I:%M %p')}
Philippine Time: {ph_time.strftime('%Y-%m-%d %I:%M %p')}
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
- Debts & Credits ({debts_pct}% Target): BD {actual_debts_bhd:,.2f}
- Needs ({needs_pct}% Target)     : BD {actual_needs_bhd:,.2f}
- Wants ({wants_pct}% Target)     : BD {actual_wants_bhd:,.2f}
- Savings & Invest ({savings_pct}%): BD {actual_savings_bhd:,.2f}
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
