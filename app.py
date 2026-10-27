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
    page_title="Rogee's Financial Command Center",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Compact Styling for Mobile & Desktop
st.markdown("""
<style>
    .main-header { font-size: 1.8rem; font-weight: 800; color: #1E3A8A; margin-bottom: 0.1rem; line-height: 1.2; } .sub-header { font-size: 0.95rem; color: #4B5563; margin-bottom: 0.8rem; } .time-badge { background-color: #F3F4F6; border: 1px solid #E5E7EB; color: #1F2937 !important; padding: 6px 12px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; margin-bottom: 12px; display: inline-block; width: 100%; text-align: center; } /\* Box Containers - Force dark text on light backgrounds in Dark Mode \*/ .priority-banner { background-color: #FEF2F2; border: 1px solid #FECACA; border-left: 5px solid #EF4444; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; color: #111827 !important; } .priority-banner \* { color: #111827 !important; } .income-card { background-color: #F0FDF4; border: 1px solid #BBF7D0; border-left: 5px solid #22C55E; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; color: #111827 !important; } .income-card \* { color: #111827 !important; } .rate-card { background-color: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #3B82F6; padding: 8px 12px; border-radius: 6px; margin-bottom: 12px; font-size: 0.85rem; color: #111827 !important; } .rate-card \* { color: #111827 !important; } /\* Metric Boxes &amp; Numbers Visibility Fix \*/ .stMetric { background-color: #F9FAFB !important; padding: 8px; border-radius: 6px; border: 1px solid #E5E7EB !important; } div[data-testid="stMetricValue"] { font-size: 1.15rem !important; font-weight: 800 !important; color: #1E3A8A !important; } div[data-testid="stMetricLabel"] { color: #374151 !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

# User Account Profiles
USER_PROFILES = {
    "Rogee": {
        "sec_key": "ROGEE_KEY", "def_key": "rogee1989",
        "data_file": "expenses_rogee.csv", "config_file": "config_rogee.json", "invest_file": "investments_rogee.csv"
    },
    "Ferdie": {
        "sec_key": "USER2_KEY", "def_key": "Ce_0121119",
        "data_file": "expenses_user2.csv", "config_file": "config_user2.json", "invest_file": "investments_user2.csv"
    },
    "User 3": {
        "sec_key": "USER3_KEY", "def_key": "user32026",
        "data_file": "expenses_user3.csv", "config_file": "config_user3.json", "invest_file": "investments_user3.csv"
    }
}

# Live FX Engine
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
                    if k not in fetched: fetched[k] = v
                return fetched, True, datetime.now().strftime("%Y-%m-%d %H:%M")
    except Exception: pass
    return base_rates, False, datetime.now().strftime("%Y-%m-%d %H:%M (Benchmark)")

rates_dict, is_live_rates, last_rate_update = fetch_live_rates()

# Authentication Check
def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = None

    if not st.session_state["authenticated"]:
        st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🔐 Rogee&apos;s Financial Command Center</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B7280; font-size: 0.9rem;'>Select your account profile and enter your private key to unlock.</p>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                selected_user = st.selectbox("Select Account Profile", list(USER_PROFILES.keys()))
                entered_pass = st.text_input("Enter Access Key", type="password", placeholder="••••••••")
                login_btn = st.form_submit_button("🔓 Unlock Command Center", use_container_width=True)
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

# User Configurations Loader
def load_user_config():
    defaults = {
        "salary_bhd": 1500.0, "business_bhd": 0.0, "sidelines_bhd": 0.0, "other_income_bhd": 0.0,
        "fixed_priority_bhd": 300.0, "needs_pct": 50, "wants_pct": 30, "savings_pct": 20, "display_curr": "BHD (BD)"
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                saved = json.load(f)
                defaults.update(saved)
        except Exception: pass
    return defaults

def save_user_config(cfg):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=4)
    except Exception: pass

cfg = load_user_config()

# Data Loader
def load_data(file_path):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df["Date"] = pd.to_datetime(df["Date"]).dt.date
            return df
        except Exception: pass
    return pd.DataFrame(columns=["Date", "Main Category", "Sub Category", "Merchant/Description", "Amount", "Currency", "Amount (BHD)", "Payment Method"])

def save_data(df, file_path): df.to_csv(file_path, index=False)
df_expenses = load_data(DATA_FILE)

# Investments Loader
def load_investments():
    if os.path.exists(INVEST_FILE):
        try: return pd.read_csv(INVEST_FILE)
        except Exception: pass
    return pd.DataFrame(columns=["Type", "Symbol/Ticker", "Platform", "Shares/Lots", "Avg Buy Price", "Current Price", "Notes"])
df_invest = load_investments()

# Sidebar Controls
st.sidebar.title(f"⚙️ Settings ({current_user})")

display_curr = st.sidebar.selectbox("Display Currency", ["BHD (BD)", "PHP (₱)", "USD ($)"], index=["BHD (BD)", "PHP (₱)", "USD ($)"].index(cfg.get("display_curr", "BHD (BD)")))

# Currency rates
usd_rate = rates_dict.get("USD", 1.0)
bhd_rate = rates_dict.get("BHD", 0.377)
php_rate = rates_dict.get("PHP", 58.50)

bhd_to_usd = usd_rate / bhd_rate
bhd_to_php = php_rate / bhd_rate

EXCHANGE_RATES = {
    "BHD": {"symbol": "BD ", "rate": 1.0, "name": "Bahraini Dinar"},
    "PHP": {"symbol": "₱", "rate": bhd_to_php, "name": "Philippine Peso"},
    "USD": {"symbol": "$", "rate": bhd_to_usd, "name": "US Dollar"}
}

curr_code = display_curr.split()[0]
curr_symbol = EXCHANGE_RATES[curr_code]["symbol"]
rate_mult = EXCHANGE_RATES[curr_code]["rate"]

st.sidebar.markdown("---")
st.sidebar.subheader("💵 Income Streams (BHD)")
salary_bhd = st.sidebar.number_input("Primary Salary (BHD)", min_value=0.0, value=float(cfg.get("salary_bhd", 1500.0)), step=50.0)
business_bhd = st.sidebar.number_input("Business Income (BHD)", min_value=0.0, value=float(cfg.get("business_bhd", 0.0)), step=50.0)
sidelines_bhd = st.sidebar.number_input("Sidelines / Freelance (BHD)", min_value=0.0, value=float(cfg.get("sidelines_bhd", 0.0)), step=25.0)
other_income_bhd = st.sidebar.number_input("Other Income (BHD)", min_value=0.0, value=float(cfg.get("other_income_bhd", 0.0)), step=25.0)

total_income_bhd = salary_bhd + business_bhd + sidelines_bhd + other_income_bhd
st.sidebar.markdown(f"**Total Combined Income:** `BD {total_income_bhd:,.2f}`")

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 100% Mandatory Obligations")
fixed_priority_bhd = st.sidebar.number_input("Mandatory Obligations (BHD)", min_value=0.0, value=float(cfg.get("fixed_priority_bhd", 300.0)), step=25.0)

net_bhd_for_budget = max(0.0, total_income_bhd - fixed_priority_bhd)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Framework Target Allocation (%)")
needs_pct = st.sidebar.slider("Needs Target % (Essentials)", 0, 100, int(cfg.get("needs_pct", 50)))
wants_pct = st.sidebar.slider("Wants Target % (Lifestyle)", 0, 100, int(cfg.get("wants_pct", 30)))
savings_pct = st.sidebar.slider("Savings Target % (Goals/Debt)", 0, 100, int(cfg.get("savings_pct", 20)))

total_pct = needs_pct + wants_pct + savings_pct
if total_pct != 100:
    st.sidebar.warning(f"Allocation total is {total_pct}%. It should sum to 100%.")

# Auto-save configuration changes
cfg_updated = {
    "salary_bhd": salary_bhd, "business_bhd": business_bhd, "sidelines_bhd": sidelines_bhd, "other_income_bhd": other_income_bhd,
    "fixed_priority_bhd": fixed_priority_bhd, "needs_pct": needs_pct, "wants_pct": wants_pct, "savings_pct": savings_pct,
    "display_curr": display_curr
}
if cfg_updated != cfg: save_user_config(cfg_updated)

st.sidebar.markdown("---")
if st.sidebar.button("🔒 Lock App / Log Out", use_container_width=True):
    st.session_state["authenticated"] = False
    st.session_state["current_user"] = None
    st.rerun()

# Dynamic Framework Headings & Category Labels
framework_title = f"{needs_pct}/{wants_pct}/{savings_pct}"
cat_label_needs = f"Needs ({needs_pct}%)"
cat_label_wants = f"Wants ({wants_pct}%)"
cat_label_savings = f"Savings & Debt ({savings_pct}%)"
cat_label_priority = "100% Priority & People to Pay"

# Target Allocations
disp_total_income = total_income_bhd * rate_mult
disp_fixed = fixed_priority_bhd * rate_mult
disp_net_budget = net_bhd_for_budget * rate_mult

needs_target = disp_net_budget * (needs_pct / 100.0)
wants_target = disp_net_budget * (wants_pct / 100.0)
savings_target = disp_net_budget * (savings_pct / 100.0)

# Regional Clocks
utc_now = datetime.now(timezone.utc)
bh_time = utc_now + timedelta(hours=3)
ph_time = utc_now + timedelta(hours=8)

# Title & Time Badge
st.markdown('<div class="main-header">💰 Rogee&apos;s Financial Command Center</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Multi-Currency Personal Finance Manager ({framework_title} Framework)</div>', unsafe_allow_html=True)

st.markdown(f'''
<div class="time-badge">
    🇧🇭 <b>Bahrain:</b> {bh_time.strftime("%d %b %Y, %I:%M %p")} &nbsp;|&nbsp; 
    🇵🇭 <b>Philippines:</b> {ph_time.strftime("%d %b %Y, %I:%M %p")} &nbsp;|&nbsp; 
    👤 <b>User:</b> {current_user}
</div>
''', unsafe_allow_html=True)

rate_mode_str = "Live Auto-Updated" if is_live_rates else "Benchmark Exchange Rates"
st.markdown(f'''
<div class="rate-card">
    🌐 <b>Live FX Engine ({rate_mode_str}):</b> <b>1 BHD</b> = <b>₱{bhd_to_php:,.2f} PHP</b> | <b>1 BHD</b> = <b>${bhd_to_usd:,.2f} USD</b> | <b>1 USD</b> = <b>₱{(bhd_to_php/bhd_to_usd):,.2f} PHP</b>
    <span style="float: right; color: #6B7280;">Updated: {last_rate_update}</span>
</div>
''', unsafe_allow_html=True)

tab_dash, tab_add, tab_history, tab_forex, tab_invest, tab_reports, tab_guide = st.tabs([
    "📈 Dashboard & Analytics", "➕ Record Expense", "📜 Transaction History", "💱 Live Forex Engine",
    "📊 MT5 & COL Investments", "📥 Download Reports", "📘 User Guide"
])

if not df_expenses.empty:
    actual_priority_bhd = df_expenses[df_expenses["Main Category"].str.contains("100%|Priority", case=False, na=False)]["Amount (BHD)"].sum()
    actual_needs_bhd = df_expenses[df_expenses["Main Category"].str.contains("Needs", case=False, na=False)]["Amount (BHD)"].sum()
    actual_wants_bhd = df_expenses[df_expenses["Main Category"].str.contains("Wants", case=False, na=False)]["Amount (BHD)"].sum()
    actual_savings_bhd = df_expenses[df_expenses["Main Category"].str.contains("Savings", case=False, na=False)]["Amount (BHD)"].sum()
else:
    actual_priority_bhd, actual_needs_bhd, actual_wants_bhd, actual_savings_bhd = 0.0, 0.0, 0.0, 0.0

total_spent_bhd = actual_priority_bhd + actual_needs_bhd + actual_wants_bhd + actual_savings_bhd
remaining_cash_bhd = total_income_bhd - total_spent_bhd

actual_priority_disp = actual_priority_bhd * rate_mult
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
    st.subheader(f"📊 Multi-Month Expense Trends & {framework_title} Category Breakdown")
    
    if not df_expenses.empty:
        df_exp_copy = df_expenses.copy()
        df_exp_copy["YearMonth"] = pd.to_datetime(df_exp_copy["Date"]).dt.strftime("%Y-%m")
        df_exp_copy["DispAmount"] = df_exp_copy["Amount (BHD)"] * rate_mult

        col_ch1, col_ch2 = st.columns(2)
        with col_ch1:
            st.markdown("#### Monthly Expense Comparison Over Time")
            monthly_trend = df_exp_copy.groupby(["YearMonth", "Main Category"])["DispAmount"].sum().reset_index()
            fig_trend = px.bar(
                monthly_trend, 
                x="YearMonth", 
                y="DispAmount", 
                color="Main Category", 
                barmode="stack",
                labels={"DispAmount": f"Amount ({curr_code})", "YearMonth": "Month"}
            )
            fig_trend.update_layout(margin=dict(l=10, r=10, t=25, b=20))
            st.plotly_chart(fig_trend, use_container_width=True)

        with col_ch2:
            st.markdown("#### Spending Share by Main Category")
            fig_pie = px.pie(
                df_exp_copy, 
                values="DispAmount", 
                names="Main Category",
                hole=0.45
            )
            fig_pie.update_layout(margin=dict(l=10, r=10, t=25, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("#### Multi-Month Category Summary Matrix")
        pivot_df = df_exp_copy.pivot_table(index="YearMonth", columns="Main Category", values="DispAmount", aggfunc="sum", fill_value=0.0)
        pivot_df["Total Monthly Spent"] = pivot_df.sum(axis=1)
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
            category_options = [cat_label_priority, cat_label_needs, cat_label_wants, cat_label_savings]
            main_cat = st.selectbox("Category", category_options)
            
            if "100%" in main_cat or "Priority" in main_cat:
                sub_cats = ["People to Pay (Household Helper / Staff)", "Family Support & Remittance (100%)", "Direct Mandatory Loan / Debt", "Fixed Mandatory Utility / Bill"]
            elif "Needs" in main_cat:
                sub_cats = ["Housing / Rent / Mortgage", "Utilities & Bills", "Groceries", "Transportation / Fuel", "Healthcare / Insurance", "Minimum Debt Payments"]
            elif "Wants" in main_cat:
                sub_cats = ["Dining Out & Coffee", "Entertainment & Streaming", "Shopping & Apparel", "Hobbies & Travel", "Subscriptions", "Miscellaneous"]
            else:
                sub_cats = ["Emergency Fund", "Retirement / 401(k) / IRA", "Stock Investments (COL / Brokerage)", "Forex & Trading Deposit", "Major Goal Savings"]

            sub_cat = st.selectbox("Sub-Category", sub_cats)

        with col_b:
            merchant = st.text_input("Merchant / Description / Payee", placeholder="e.g. Household Helper Salary, Landlord, Grocery")
            amount_input = st.number_input("Amount", min_value=0.01, step=5.0, value=25.0)
            input_currency = st.selectbox("Payment Currency", ["BHD", "PHP", "USD"], index=0)
            
            # Payment Method now includes Benefit Pay and Remittance
            payment_method = st.selectbox("Payment Method", ["Benefit Pay", "Remittance", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])

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
            st.success(f"Recorded payment of {EXCHANGE_RATES[input_currency]['symbol']}{amount_input:,.2f} ({sub_cat}) via {payment_method}!")
            st.rerun()

# TAB 3: TRANSACTION HISTORY
with tab_history:
    st.subheader(f"📜 Recorded Transaction History ({current_user})")

    if not df_expenses.empty:
        total_recorded_bhd = df_expenses["Amount (BHD)"].sum()
        total_recorded_disp = total_recorded_bhd * rate_mult

        st.info(f"💰 **Total Recorded Expenses: {curr_symbol}{total_recorded_disp:,.2f}** (BD {total_recorded_bhd:,.2f} | ₱{total_recorded_bhd*bhd_to_php:,.2f} | ${total_recorded_bhd*bhd_to_usd:,.2f})")

        cat_filter = st.multiselect("Filter by Category", options=df_expenses["Main Category"].unique().tolist(), default=df_expenses["Main Category"].unique().tolist())

        filtered_df = df_expenses[df_expenses["Main Category"].isin(cat_filter)] if cat_filter else df_expenses
        st.dataframe(filtered_df.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)

        st.markdown("---")
        if st.button("🗑️ Clear All Expense Data", type="primary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.success("All transaction logs cleared!")
            st.rerun()
    else:
        st.info("No transaction history found.")

# TAB 4: LIVE FOREX ENGINE
with tab_forex:
    st.subheader("💱 Live Multi-Currency Cross Rate Engine")
    st.caption("Live global exchange rates refreshed hourly.")

    fx_col1, fx_col2 = st.columns(2)

    with fx_col1:
        st.markdown("#### Interactive Currency Pair Converter")
        calc_amt = st.number_input("Amount to Convert", min_value=0.01, value=100.0, step=10.0)
        
        # Currency List including USDCHF, AUDCAD, NZDUSD components
        all_fx = ["USD", "BHD", "PHP", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"]
        
        pair_from = st.selectbox("From Currency", all_fx, index=0)
        pair_to = st.selectbox("To Currency", all_fx, index=2)

        rate_from_usd = rates_dict.get(pair_from, 1.0)
        rate_to_usd = rates_dict.get(pair_to, 1.0)

        cross_rate = rate_to_usd / rate_from_usd
        converted_val = calc_amt * cross_rate

        st.success(f"### {calc_amt:,.2f} {pair_from} = **{converted_val:,.2f} {pair_to}**")
        st.info(f"💡 **Exchange Rate:** 1 {pair_from} = {cross_rate:,.4f} {pair_to}")

    with fx_col2:
        st.markdown("#### Major & Cross Currency Pairs Dashboard")
        
        chf_rate = rates_dict.get("CHF", 0.865)
        aud_rate = rates_dict.get("AUD", 1.51)
        cad_rate = rates_dict.get("CAD", 1.38)
        nzd_rate = rates_dict.get("NZD", 1.66)

        usd_chf = chf_rate / usd_rate
        aud_cad = cad_rate / aud_rate
        nzd_usd = usd_rate / nzd_rate

        st.markdown(f'''
        * **1 BHD → PHP:** ₱{(rates_dict.get("PHP", 58.5)/rates_dict.get("BHD", 0.377)):,.2f}
        * **1 BHD → USD:** ${(rates_dict.get("USD", 1.0)/rates_dict.get("BHD", 0.377)):,.2f}
        * **1 USD → PHP:** ₱{(rates_dict.get("PHP", 58.5)/rates_dict.get("USD", 1.0)):,.2f}
        * **1 USD → CHF (USD/CHF):** {usd_chf:,.4f} CHF
        * **1 AUD → CAD (AUD/CAD):** {aud_cad:,.4f} CAD
        * **1 NZD → USD (NZD/USD):** ${nzd_usd:,.4f} USD
        * **1 EUR → USD:** ${(rates_dict.get("USD", 1.0)/rates_dict.get("EUR", 0.92)):,.4f}
        * **1 GBP → USD:** ${(rates_dict.get("USD", 1.0)/rates_dict.get("GBP", 0.78)):,.4f}
        ''')

        if st.button("🔄 Force Refresh Live Rates"):
            st.cache_data.clear()
            st.rerun()

# TAB 5: MT5 & COL INVESTMENTS
with tab_invest:
    st.subheader("📊 MT5 Forex & COL Financial Portfolio Manager")
    st.caption("Track your MetaTrader 5 trading accounts and COL Financial stock equity.")

    with st.form("add_investment_form", clear_on_submit=True):
        inv_col1, inv_col2 = st.columns(2)
        with inv_col1:
            inv_type = st.selectbox("Asset Class / Platform", ["COL Financial (PH Stocks)", "MetaTrader 5 (Forex / Indices)", "Crypto / Other"])
            ticker = st.text_input("Ticker / Asset Symbol", placeholder="e.g. ALI, BDO, EURUSD, XAUUSD")
            platform = st.text_input("Broker / Platform Name", placeholder="e.g. COL Financial, IC Markets, Exness")
        with inv_col2:
            shares = st.number_input("Shares / Lots Owned", min_value=0.001, value=100.0)
            buy_price = st.number_input("Avg Purchase Price ($ or ₱)", min_value=0.0001, value=10.0)
            curr_price = st.number_input("Current Market Price ($ or ₱)", min_value=0.0001, value=12.0)

        inv_submit = st.form_submit_button("Add Asset Record", use_container_width=True)
        if inv_submit:
            new_inv = pd.DataFrame([{
                "Type": inv_type,
                "Symbol/Ticker": ticker if ticker else "Unspecified",
                "Platform": platform if platform else "General",
                "Shares/Lots": shares,
                "Avg Buy Price": buy_price,
                "Current Price": curr_price,
                "Notes": "Recorded on " + datetime.today().strftime("%Y-%m-%d")
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
Framework      : {framework_title} (Needs: {needs_pct}%, Wants: {wants_pct}%, Savings: {savings_pct}%)

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
- Needs ({needs_pct}% Target)     : BD {actual_needs_bhd:,.2f}
- Wants ({wants_pct}% Target)     : BD {actual_wants_bhd:,.2f}
- Savings & Debt ({savings_pct}%): BD {actual_savings_bhd:,.2f}
--------------------------------------------------
GRAND TOTAL EXPENSES     : BD {total_exp_bhd:,.2f}
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
    To configure private passkeys for Rogee, User 2, or User 3 on Streamlit Cloud:
    1. Open your Streamlit Cloud dashboard.
    2. Go to **App Settings > Secrets**.
    3. Add your private keys:
       ```toml
       ROGEE_KEY = "YourPrivatePassphrase"
       USER2_KEY = "User2Passphrase"
       USER3_KEY = "User3Passphrase"
       ```
    4. Click Save!
    """)
