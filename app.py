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

def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = None
    
    if not st.session_state["authenticated"]:
        st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🔐 Rogee&apos;s Financial Command Center</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B7280;'>Select your account profile and enter your private access key.</p>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            with st.form("login_form"):
                selected_user = st.selectbox("Select Account Profile", list(USER_PROFILES.keys()))
                entered_pass = st.text_input("Enter Access Key", type="password", placeholder="••••••••")
                login_btn = st.form_submit_button("Unlock Dashboard", use_container_width=True)
                
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
                        st.error("Invalid access key. Please try again.")
        st.stop()

check_authentication()

current_user = st.session_state["current_user"]
user_cfg = USER_PROFILES[current_user]
DATA_FILE = user_cfg["data_file"]
CONFIG_FILE = user_cfg["config_file"]
INVEST_FILE = user_cfg["invest_file"]

def load_data(file_path):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            # Ensure column names exist and migrate older format
            if "Billed Amount" not in df.columns:
                if "Amount" in df.columns:
                    df["Billed Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
                elif "Amount (BHD)" in df.columns:
                    df["Billed Amount"] = pd.to_numeric(df["Amount (BHD)"], errors="coerce").fillna(0.0)
                else:
                    df["Billed Amount"] = 0.0

            if "Actual Paid" not in df.columns:
                df["Actual Paid"] = df["Billed Amount"]

            if "Currency" not in df.columns:
                df["Currency"] = "BHD"

            if "Status" not in df.columns:
                df["Status"] = "Paid"

            if "Payment Method" not in df.columns:
                df["Payment Method"] = "Bank Transfer"

            if "Merchant/Description" not in df.columns:
                df["Merchant/Description"] = df["Merchant"] if "Merchant" in df.columns else "Unspecified"

            if "Main Category" not in df.columns:
                df["Main Category"] = "Needs"

            if "Sub Category" not in df.columns:
                df["Sub Category"] = "General"

            if "Date" not in df.columns:
                df["Date"] = datetime.today().strftime("%Y-%m-%d")

            df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%Y-%m-%d").fillna(datetime.today().strftime("%Y-%m-%d"))
            df["Billed Amount"] = pd.to_numeric(df["Billed Amount"], errors="coerce").fillna(0.0)
            df["Actual Paid"] = pd.to_numeric(df["Actual Paid"], errors="coerce").fillna(0.0)
            
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=[
        "Date", "Main Category", "Sub Category", "Merchant/Description",
        "Billed Amount", "Actual Paid", "Currency", "Status", "Payment Method"
    ])

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "salary_bhd": 1500.0, "business_bhd": 0.0, "sidelines_bhd": 0.0, "other_income_bhd": 0.0,
        "fixed_priority_bhd": 300.0, "debts_pct": 15, "needs_pct": 45, "wants_pct": 20, "savings_pct": 20,
        "display_currency": "BHD"
    }

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f)

def load_investments():
    if os.path.exists(INVEST_FILE):
        try:
            return pd.read_csv(INVEST_FILE)
        except Exception:
            pass
    return pd.DataFrame(columns=["Type", "Symbol/Ticker", "Platform", "Shares/Lots", "Avg Buy Price", "Current Price", "Notes"])

df_expenses = load_data(DATA_FILE)
app_cfg = load_config()
df_invest = load_investments()

st.sidebar.title(f"👤 {current_user}'s Settings")

display_curr = st.sidebar.selectbox("Dashboard Display Currency", ["BHD", "PHP", "USD"], index=["BHD", "PHP", "USD"].index(app_cfg.get("display_currency", "BHD")))

st.sidebar.markdown("---")
st.sidebar.subheader("💵 Monthly Income Streams (BHD)")
salary_bhd = st.sidebar.number_input("Primary Salary (BHD)", min_value=0.0, value=float(app_cfg.get("salary_bhd", 1500.0)), step=50.0)
business_bhd = st.sidebar.number_input("Business Income (BHD)", min_value=0.0, value=float(app_cfg.get("business_bhd", 0.0)), step=50.0)
sidelines_bhd = st.sidebar.number_input("Sidelines / Freelance (BHD)", min_value=0.0, value=float(app_cfg.get("sidelines_bhd", 0.0)), step=50.0)
other_income_bhd = st.sidebar.number_input("Other Income (BHD)", min_value=0.0, value=float(app_cfg.get("other_income_bhd", 0.0)), step=50.0)

total_income_bhd = float(salary_bhd + business_bhd + sidelines_bhd + other_income_bhd)

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 100% Mandatory Obligations")
fixed_priority_bhd = st.sidebar.number_input("Mandatory Fixed Payments (BHD)", min_value=0.0, value=float(app_cfg.get("fixed_priority_bhd", 300.0)), step=25.0)

net_bhd_for_budget = max(0.0, total_income_bhd - fixed_priority_bhd)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Framework Allocations (%)")
debts_pct = st.sidebar.slider("Debts & Credits Target %", 0, 100, int(app_cfg.get("debts_pct", 15)))
needs_pct = st.sidebar.slider("Needs Target % (Essentials)", 0, 100, int(app_cfg.get("needs_pct", 45)))
wants_pct = st.sidebar.slider("Wants Target % (Lifestyle)", 0, 100, int(app_cfg.get("wants_pct", 20)))
savings_pct = st.sidebar.slider("Savings & Investments Target %", 0, 100, int(app_cfg.get("savings_pct", 20)))

total_pct = debts_pct + needs_pct + wants_pct + savings_pct
if total_pct != 100:
    st.sidebar.warning(f"Allocation total is {total_pct}%. It should equal 100%.")

framework_title = f"{debts_pct}/{needs_pct}/{wants_pct}/{savings_pct} Framework"

if st.sidebar.button("💾 Save Settings Memory", use_container_width=True):
    app_cfg.update({
        "salary_bhd": salary_bhd, "business_bhd": business_bhd, "sidelines_bhd": sidelines_bhd,
        "other_income_bhd": other_income_bhd, "fixed_priority_bhd": fixed_priority_bhd,
        "debts_pct": debts_pct, "needs_pct": needs_pct, "wants_pct": wants_pct,
        "savings_pct": savings_pct, "display_currency": display_curr
    })
    save_config(app_cfg)
    st.sidebar.success("Settings saved to your profile!")

bhd_to_php = float(rates_dict.get("PHP", 58.5) / rates_dict.get("BHD", 0.377))
bhd_to_usd = float(rates_dict.get("USD", 1.0) / rates_dict.get("BHD", 0.377))

if display_curr == "PHP":
    rate_mult = bhd_to_php; curr_symbol = "₱"; curr_code = "PHP"
elif display_curr == "USD":
    rate_mult = bhd_to_usd; curr_symbol = "$"; curr_code = "USD"
else:
    rate_mult = 1.0; curr_symbol = "BD "; curr_code = "BHD"

disp_total_income = total_income_bhd * rate_mult
disp_fixed = fixed_priority_bhd * rate_mult
disp_net_budget = net_bhd_for_budget * rate_mult

target_debts = disp_net_budget * (debts_pct / 100.0)
target_needs = disp_net_budget * (needs_pct / 100.0)
target_wants = disp_net_budget * (wants_pct / 100.0)
target_savings = disp_net_budget * (savings_pct / 100.0)

utc_now = datetime.now(timezone.utc)
bh_time = utc_now + timedelta(hours=3)
ph_time = utc_now + timedelta(hours=8)

st.markdown('<div class="main-header">💰 Rogee&apos;s Financial Command Center</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Multi-Currency Personal Wealth Management • Based on {framework_title}</div>', unsafe_allow_html=True)

st.markdown(f'''
<div class="time-badge">
    🇧🇭 <b>Bahrain Time:</b> {bh_time.strftime("%d %b %Y, %I:%M %p")} AST &nbsp;|&nbsp; 
    🇵🇭 <b>Philippine Time:</b> {ph_time.strftime("%d %b %Y, %I:%M %p")} PHT &nbsp;|&nbsp; 
    👤 <b>Account:</b> {current_user}
</div>
''', unsafe_allow_html=True)

rate_mode_str = "Live Auto-Updated" if is_live_rates else "Benchmark Rates"
st.markdown(f'<div class="rate-card">🌐 <b>Live FX Rates ({rate_mode_str}):</b> <b>1 BHD</b> = <b>₱{bhd_to_php:,.2f} PHP</b> | <b>1 BHD</b> = <b>${bhd_to_usd:,.2f} USD</b> | <b>1 USD</b> = <b>₱{(bhd_to_php/bhd_to_usd):,.2f} PHP</b> <span style="float: right; color: #6B7280; font-size: 0.8rem;">Updated: {last_rate_update}</span></div>', unsafe_allow_html=True)

tab_dash, tab_add, tab_history, tab_forex, tab_invest, tab_reports, tab_guide = st.tabs([
    "📈 Dashboard & Analytics", "➕ Record Expense", "📜 Transaction History",
    "💱 Live Forex Engine", "📊 MT5 & COL Investments", "📥 Download Reports", "📘 User Guide"
])

# Ensure columns exist on df_expenses for calculation
if "Billed Amount" not in df_expenses.columns:
    if "Amount" in df_expenses.columns:
        df_expenses["Billed Amount"] = pd.to_numeric(df_expenses["Amount"], errors="coerce").fillna(0.0)
    elif "Amount (BHD)" in df_expenses.columns:
        df_expenses["Billed Amount"] = pd.to_numeric(df_expenses["Amount (BHD)"], errors="coerce").fillna(0.0)
    else:
        df_expenses["Billed Amount"] = 0.0

if "Actual Paid" not in df_expenses.columns:
    df_expenses["Actual Paid"] = df_expenses["Billed Amount"]

if "Currency" not in df_expenses.columns:
    df_expenses["Currency"] = "BHD"

df_expenses["Billed Amount"] = pd.to_numeric(df_expenses["Billed Amount"], errors="coerce").fillna(0.0)
df_expenses["Actual Paid"] = pd.to_numeric(df_expenses["Actual Paid"], errors="coerce").fillna(0.0)

def get_bhd_val(row, col_name):
    if col_name not in row:
        return 0.0
    val = float(row[col_name])
    curr = str(row.get("Currency", "BHD")).upper()
    if curr == "PHP": return val / bhd_to_php
    elif curr == "USD": return val / bhd_to_usd
    return val

if not df_expenses.empty:
    df_expenses["Billed_BHD"] = df_expenses.apply(lambda r: get_bhd_val(r, "Billed Amount"), axis=1)
    df_expenses["Paid_BHD"] = df_expenses.apply(lambda r: get_bhd_val(r, "Actual Paid"), axis=1)
    
    actual_priority_bhd = float(df_expenses[df_expenses["Main Category"].astype(str).str.contains("100%", na=False)]["Paid_BHD"].sum())
    actual_debts_bhd = float(df_expenses[df_expenses["Main Category"].astype(str).str.contains("Debts", na=False)]["Paid_BHD"].sum())
    actual_needs_bhd = float(df_expenses[df_expenses["Main Category"].astype(str).str.contains("Needs", na=False)]["Paid_BHD"].sum())
    actual_wants_bhd = float(df_expenses[df_expenses["Main Category"].astype(str).str.contains("Wants", na=False)]["Paid_BHD"].sum())
    actual_savings_bhd = float(df_expenses[df_expenses["Main Category"].astype(str).str.contains("Savings", na=False)]["Paid_BHD"].sum())
else:
    actual_priority_bhd, actual_debts_bhd, actual_needs_bhd, actual_wants_bhd, actual_savings_bhd = 0.0, 0.0, 0.0, 0.0, 0.0

total_spent_bhd = float(actual_priority_bhd + actual_debts_bhd + actual_needs_bhd + actual_wants_bhd + actual_savings_bhd)
remaining_cash_bhd = float(total_income_bhd - total_spent_bhd)

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
    st.write(f"**Total Combined Income:** `{curr_symbol}{disp_total_income:,.2f}` (BD {total_income_bhd:,.2f} | ₱{(total_income_bhd*bhd_to_php):,.2f} | ${(total_income_bhd*bhd_to_usd):,.2f})")
    st.markdown('</div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Income", f"{curr_symbol}{disp_total_income:,.2f}")
    m2.metric("100% Mandatory Target", f"{curr_symbol}{disp_fixed:,.2f}")
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
        st.metric("Pending Mandatory Balance", f"{curr_symbol}{rem_priority_disp:,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader(f"📊 {framework_title} Benchmark Allocations")

    cat_data = [
        {"Category": f"Debts & Credits ({debts_pct}%)", "Target (%)": f"{debts_pct}%", "Target Amount": target_debts, "Actual Spent": actual_debts_disp, "Variance": target_debts - actual_debts_disp, "Status": "On Track" if actual_debts_disp <= target_debts else "Over Target"},
        {"Category": f"Needs ({needs_pct}%)", "Target (%)": f"{needs_pct}%", "Target Amount": target_needs, "Actual Spent": actual_needs_disp, "Variance": target_needs - actual_needs_disp, "Status": "On Track" if actual_needs_disp <= target_needs else "Over Target"},
        {"Category": f"Wants ({wants_pct}%)", "Target (%)": f"{wants_pct}%", "Target Amount": target_wants, "Actual Spent": actual_wants_disp, "Variance": target_wants - actual_wants_disp, "Status": "On Track" if actual_wants_disp <= target_wants else "Over Target"},
        {"Category": f"Savings & Investments ({savings_pct}%)", "Target (%)": f"{savings_pct}%", "Target Amount": target_savings, "Actual Spent": actual_savings_disp, "Variance": actual_savings_disp - target_savings, "Status": "Goal Met" if actual_savings_disp >= target_savings else "Under Goal"}
    ]
    df_cat_summary = pd.DataFrame(cat_data)
    st.dataframe(df_cat_summary.style.format({
        "Target Amount": f"{curr_symbol}{{:,.2f}}",
        "Actual Spent": f"{curr_symbol}{{:,.2f}}",
        "Variance": f"{curr_symbol}{{:,.2f}}"
    }), use_container_width=True, hide_index=True)

    st.markdown("---")
    c_ch1, c_ch2 = st.columns(2)
    with c_ch1:
        st.markdown("#### Target vs. Actual Spending")
        chart_df = pd.DataFrame({
            "Category": ["Debts", "Needs", "Wants", "Savings"],
            "Target": [target_debts, target_needs, target_wants, target_savings],
            "Actual": [actual_debts_disp, actual_needs_disp, actual_wants_disp, actual_savings_disp]
        })
        fig_bar = go.Figure(data=[
            go.Bar(name='Target', x=chart_df['Category'], y=chart_df['Target'], marker_color='#93C5FD'),
            go.Bar(name='Actual', x=chart_df['Category'], y=chart_df['Actual'], marker_color='#1D4ED8')
        ])
        fig_bar.update_layout(barmode='group', yaxis_title=f"Amount ({curr_code})", margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_bar, use_container_width=True)

    with c_ch2:
        st.markdown("#### Spending Share by Category")
        if total_spent_disp > 0:
            fig_pie = px.pie(
                values=[actual_priority_disp, actual_debts_disp, actual_needs_disp, actual_wants_disp, actual_savings_disp],
                names=["100% Priority", "Debts & Credits", "Needs", "Wants", "Savings & Investments"],
                color_discrete_sequence=['#EF4444', '#8B5CF6', '#2563EB', '#F59E0B', '#10B981'], hole=0.45
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.subheader("📊 Multi-Month Expense Trends & Category Breakdown")
    if not df_expenses.empty:
        df_exp_copy = df_expenses.copy()
        df_exp_copy["YearMonth"] = pd.to_datetime(df_exp_copy["Date"], errors="coerce").dt.strftime("%Y-%m").fillna("Unspecified")
        df_exp_copy["DispAmount"] = df_exp_copy["Paid_BHD"] * rate_mult

        col_ch1, col_ch2 = st.columns(2)
        with col_ch1:
            st.markdown("#### Monthly Expense Comparison Over Time")
            monthly_trend = df_exp_copy.groupby(["YearMonth", "Main Category"])["DispAmount"].sum().reset_index()
            fig_trend = px.bar(monthly_trend, x="YearMonth", y="DispAmount", color="Main Category", barmode="stack", labels={"DispAmount": f"Amount ({curr_code})", "YearMonth": "Month"})
            fig_trend.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_trend, use_container_width=True)

        with col_ch2:
            st.markdown("#### Multi-Month Category Summary Matrix")
            pivot_df = df_exp_copy.pivot_table(index="YearMonth", columns="Main Category", values="DispAmount", aggfunc="sum", fill_value=0.0)
            pivot_df["Total Spent"] = pivot_df.sum(axis=1)
            st.dataframe(pivot_df.style.format(f"{curr_symbol}{{:,.2f}}"), use_container_width=True)

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
            main_cat = st.selectbox("Main Category", cat_options)

            if "100%" in main_cat:
                sub_cats = ["People to Pay (Household Helper / Staff)", "Family Support & Remittance (100%)", "Direct Mandatory Loan", "Fixed Utility Bill"]
            elif "Debts" in main_cat:
                sub_cats = ["Credit Card Payment", "Personal Bank Loan", "Car / Auto Loan", "Housing Loan / Mortgage", "Other Debt Payoff"]
            elif "Needs" in main_cat:
                sub_cats = ["Rent / Housing", "Utilities & Electricity", "Groceries & Food", "Fuel & Transport", "Healthcare & Medicine", "Minimum Bill Payments"]
            elif "Wants" in main_cat:
                sub_cats = ["Dining Out & Coffee", "Shopping & Apparel", "Entertainment & Streaming", "Travel & Hobbies", "Subscriptions", "Miscellaneous"]
            else:
                sub_cats = ["Emergency Fund Deposit", "COL Stock Investments (PH)", "MT5 Forex Trading Deposit", "Index Funds / ETF", "Pension / Retirement"]

            sub_cat = st.selectbox("Sub-Category", sub_cats)

        with col_b:
            merchant = st.text_input("Merchant / Description / Payee", placeholder="e.g. Helper Salary, Landlord, BDO Credit Card")
            billed_amount = st.number_input("Billed / Planned Amount", min_value=0.01, step=5.0, value=25.0)
            pay_status = st.selectbox("Payment Status", ["Paid", "Pending Payment", "Partially Paid", "Not Paid"], index=0)
            
            default_paid = billed_amount if pay_status == "Paid" else (0.0 if pay_status in ["Pending Payment", "Not Paid"] else billed_amount / 2.0)
            actual_paid = st.number_input("Actual Amount Paid", min_value=0.0, step=5.0, value=float(default_paid))
            
            input_currency = st.selectbox("Payment Currency", ["BHD", "PHP", "USD"], index=0)
            payment_method = st.selectbox("Payment Method", ["Benefit Pay", "Remittance", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])

        submit_btn = st.form_submit_button("Save Payment Record", use_container_width=True)

        if submit_btn:
            new_row = pd.DataFrame([{
                "Date": exp_date.strftime("%Y-%m-%d"),
                "Main Category": main_cat,
                "Sub Category": sub_cat,
                "Merchant/Description": merchant if merchant else "Unspecified",
                "Billed Amount": float(billed_amount),
                "Actual Paid": float(actual_paid),
                "Currency": input_currency,
                "Status": pay_status,
                "Payment Method": payment_method
            }])
            df_expenses = pd.concat([df_expenses, new_row], ignore_index=True)
            save_data(df_expenses, DATA_FILE)
            st.success(f"Recorded payment of {input_currency} {actual_paid:,.2f} for '{merchant if merchant else sub_cat}'!")
            st.rerun()

with tab_history:
    st.subheader(f"📜 Recorded Transaction History ({current_user})")

    if not df_expenses.empty:
        df_hist = df_expenses.copy()

        # Ensure all columns exist before processing to avoid KeyError
        if "Billed Amount" not in df_hist.columns:
            if "Amount" in df_hist.columns:
                df_hist["Billed Amount"] = pd.to_numeric(df_hist["Amount"], errors="coerce").fillna(0.0)
            elif "Amount (BHD)" in df_hist.columns:
                df_hist["Billed Amount"] = pd.to_numeric(df_hist["Amount (BHD)"], errors="coerce").fillna(0.0)
            else:
                df_hist["Billed Amount"] = 0.0

        if "Actual Paid" not in df_hist.columns:
            df_hist["Actual Paid"] = df_hist["Billed Amount"]

        if "Currency" not in df_hist.columns: df_hist["Currency"] = "BHD"
        if "Status" not in df_hist.columns: df_hist["Status"] = "Paid"
        if "Payment Method" not in df_hist.columns: df_hist["Payment Method"] = "Bank Transfer"
        if "Merchant/Description" not in df_hist.columns:
            df_hist["Merchant/Description"] = df_hist["Merchant"] if "Merchant" in df_hist.columns else "Unspecified"
        if "Main Category" not in df_hist.columns: df_hist["Main Category"] = "Needs"
        if "Sub Category" not in df_hist.columns: df_hist["Sub Category"] = "General"
        if "Date" not in df_hist.columns: df_hist["Date"] = datetime.today().strftime("%Y-%m-%d")

        # Clean numeric fields safely
        df_hist["Billed Amount"] = pd.to_numeric(df_hist["Billed Amount"], errors="coerce").fillna(0.0)
        df_hist["Actual Paid"] = pd.to_numeric(df_hist["Actual Paid"], errors="coerce").fillna(0.0)

        # Define Category Sorting Order
        def get_cat_rank(cat_str):
            c_str = str(cat_str)
            if "100%" in c_str: return 1
            elif "Debts" in c_str: return 2
            elif "Needs" in c_str: return 3
            elif "Wants" in c_str: return 4
            elif "Savings" in c_str: return 5
            return 6

        df_hist["Cat_Rank"] = df_hist["Main Category"].apply(get_cat_rank)
        df_hist["Date_DT"] = pd.to_datetime(df_hist["Date"], errors="coerce").fillna(pd.Timestamp.today())
        
        # Sort by Category Rank then Chronologically by Date
        df_hist = df_hist.sort_values(by=["Cat_Rank", "Date_DT"], ascending=[True, True]).reset_index(drop=True)
        df_hist["Item #"] = range(1, len(df_hist) + 1)

        # Dynamic Calculations
        df_hist["Pending Due"] = (df_hist["Billed Amount"] - df_hist["Actual Paid"]).clip(lower=0.0)
        
        def calc_pct_paid(r):
            b = float(r["Billed Amount"])
            p = float(r["Actual Paid"])
            return round((p / b * 100.0), 1) if b > 0 else 0.0

        df_hist["% Paid"] = df_hist.apply(calc_pct_paid, axis=1)
        df_hist["% Remaining"] = (100.0 - df_hist["% Paid"]).clip(lower=0.0)

        def make_equiv_str(r):
            val = float(r["Actual Paid"])
            curr = str(r.get("Currency", "BHD")).upper()
            if curr == "BHD":
                bhd_val = val
            elif curr == "PHP":
                bhd_val = val / bhd_to_php
            else:
                bhd_val = val / bhd_to_usd
            php_val = bhd_val * bhd_to_php
            usd_val = bhd_val * bhd_to_usd
            return f"BD {bhd_val:,.2f} (₱{php_val:,.2f} | ${usd_val:,.2f})"

        df_hist["Equivalent"] = df_hist.apply(make_equiv_str, axis=1)

        cols_display = [
            "Item #", "Date", "Main Category", "Sub Category", "Merchant/Description",
            "Billed Amount", "Actual Paid", "Currency", "Pending Due", "% Paid", "% Remaining",
            "Equivalent", "Status", "Payment Method"
        ]

        # Ensure all columns exist in df_hist before slicing df_display
        for c in cols_display:
            if c not in df_hist.columns:
                df_hist[c] = 0.0 if c in ["Billed Amount", "Actual Paid", "Pending Due", "% Paid", "% Remaining"] else ""

        df_display = df_hist[cols_display].copy()

        st.caption("✏️ **Double-click any cell to edit amounts or details. Select rows to delete, then click '💾 Save Ledger Changes'.**")

        edited_df = st.data_editor(
            df_display,
            num_rows="dynamic",
            use_container_width=True,
            key=f"editor_{current_user}",
            disabled=["Item #", "Pending Due", "% Paid", "% Remaining", "Equivalent"]
        )

        col_sav1, col_sav2 = st.columns(2)
        with col_sav1:
            if st.button("💾 Save Ledger Changes", type="primary", use_container_width=True):
                save_df = edited_df.drop(columns=["Item #", "Pending Due", "% Paid", "% Remaining", "Equivalent"], errors="ignore")
                save_data(save_df, DATA_FILE)
                st.success("Ledger saved successfully!")
                st.rerun()

        with col_sav2:
            if st.button("🗑️ Clear Entire History", use_container_width=True):
                if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
                st.success("Transaction logs cleared!")
                st.rerun()

        st.markdown("---")
        st.subheader("💰 Total Outstanding & Payment Summary Ledger")

        # Compute Total Ledger Sums in Base BHD
        total_billed_bhd = sum([get_bhd_val(r, "Billed Amount") for _, r in df_hist.iterrows()])
        total_paid_bhd = sum([get_bhd_val(r, "Actual Paid") for _, r in df_hist.iterrows()])
        total_pending_bhd = max(0.0, total_billed_bhd - total_paid_bhd)

        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            st.markdown('<div class="rate-card">', unsafe_allow_html=True)
            st.markdown("#### 📋 Total Billed Amount Needed")
            st.write(f"• **BHD:** BD {total_billed_bhd:,.2f}")
            st.write(f"• **PHP:** ₱{(total_billed_bhd * bhd_to_php):,.2f}")
            st.write(f"• **USD:** ${(total_billed_bhd * bhd_to_usd):,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)

        with s_col2:
            st.markdown('<div class="income-card">', unsafe_allow_html=True)
            st.markdown("#### ✅ Total Actual Amount Paid")
            st.write(f"• **BHD:** BD {total_paid_bhd:,.2f}")
            st.write(f"• **PHP:** ₱{(total_paid_bhd * bhd_to_php):,.2f}")
            st.write(f"• **USD:** ${(total_paid_bhd * bhd_to_usd):,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)

        with s_col3:
            st.markdown('<div class="priority-banner">', unsafe_allow_html=True)
            st.markdown("#### ⏳ Total Outstanding Balance Due")
            st.write(f"• **BHD:** BD {total_pending_bhd:,.2f}")
            st.write(f"• **PHP:** ₱{(total_pending_bhd * bhd_to_php):,.2f}")
            st.write(f"• **USD:** ${(total_pending_bhd * bhd_to_usd):,.2f}")
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("No transaction records found. Add your first payment in the 'Record Expense' tab!")

with tab_forex:
    st.subheader("💱 Live Forex Rate Engine & Pair Converter")
    st.write(f"Conversion rates automatically updated: **1 BHD = ₱{bhd_to_php:,.2f} PHP = ${bhd_to_usd:,.2f} USD**")

    fx_col1, fx_col2 = st.columns(2)
    with fx_col1:
        st.markdown("#### Currency Pair Calculator")
        calc_amt = st.number_input("Amount to Convert", min_value=1.0, value=100.0, step=10.0)
        pair_from = st.selectbox("From Currency", ["BHD", "PHP", "USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"], index=0)
        pair_to = st.selectbox("To Currency", ["PHP", "USD", "BHD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"], index=0)

        rate_from_usd = float(rates_dict.get(pair_from, 1.0))
        rate_to_usd = float(rates_dict.get(pair_to, 1.0))

        if pair_from == "USD":
            cross_rate = rate_to_usd
        elif pair_to == "USD":
            cross_rate = 1.0 / rate_from_usd
        else:
            cross_rate = rate_to_usd / rate_from_usd

        converted_val = calc_amt * cross_rate
        st.success(f"### {calc_amt:,.2f} {pair_from} = **{converted_val:,.2f} {pair_to}**")
        st.info(f"💡 **Exchange Rate:** 1 {pair_from} = {cross_rate:,.4f} {pair_to}")

    with fx_col2:
        st.markdown("#### Live Major Pairs Dashboard")
        st.write(f"• **1 BHD → PHP:** ₱{bhd_to_php:,.2f} PHP")
        st.write(f"• **1 BHD → USD:** ${bhd_to_usd:,.2f} USD")
        st.write(f"• **1 USD → PHP:** ₱{(bhd_to_php/bhd_to_usd):,.2f} PHP")
        st.write(f"• **USD / CHF:** {rates_dict.get('CHF', 0.865):,.4f}")
        st.write(f"• **AUD / CAD:** {(rates_dict.get('CAD', 1.38)/rates_dict.get('AUD', 1.51)):,.4f}")
        st.write(f"• **NZD / USD:** {(1.0/rates_dict.get('NZD', 1.66)):,.4f}")

        if st.button("🔄 Force Refresh Live Rates Now"):
            st.cache_data.clear()
            st.rerun()

with tab_invest:
    st.subheader("📊 MT5 Forex & COL Financial Portfolio Manager")
    st.caption("Track your MetaTrader 5 trading accounts and COL Financial stock equity in one place.")

    st.markdown("#### 🧮 Live Trading Calculators")
    calc_t1, calc_t2 = st.columns(2)
    with calc_t1:
        st.markdown("##### 📍 Pip Value Calculator")
        pip_symbol = st.selectbox("Trading Asset", ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD (Gold)", "USDCHF", "AUDUSD"])
        lot_size = st.number_input("Lot Volume", min_value=0.01, value=1.0, step=0.1)
        acc_curr = st.selectbox("Account Currency", ["USD", "BHD", "PHP"])
        
        if "JPY" in pip_symbol:
            pip_val_usd = lot_size * 1000.0
        elif "Gold" in pip_symbol or "XAU" in pip_symbol:
            pip_val_usd = lot_size * 10.0
        else:
            pip_val_usd = lot_size * 10.0

        if acc_curr == "BHD": pip_val_disp = pip_val_usd * 0.377; sym = "BD "
        elif acc_curr == "PHP": pip_val_disp = pip_val_usd * bhd_to_php / bhd_to_usd; sym = "₱"
        else: pip_val_disp = pip_val_usd; sym = "$"

        st.info(f"**Pip Value:** {sym}{pip_val_disp:,.2f} per pip ({lot_size} lots)")

    with calc_t2:
        st.markdown("##### 🛡️ Required Margin Calculator")
        trade_lots = st.number_input("Position Size (Lots)", min_value=0.01, value=1.0, step=0.1)
        leverage = st.selectbox("Account Leverage", [100, 200, 500, 1000], index=2)
        margin_usd = (trade_lots * 100000) / leverage
        st.info(f"**Required Margin:** ${margin_usd:,.2f} USD (BD {(margin_usd*0.377):,.2f})")

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
                "Type": inv_type, "Symbol/Ticker": ticker if ticker else "Unspecified",
                "Platform": platform if platform else "General", "Shares/Lots": shares,
                "Avg Buy Price": buy_price, "Current Price": curr_price,
                "Notes": "Recorded on " + datetime.today().strftime("%Y-%m-%d")
            }])
            df_invest = pd.concat([df_invest, new_inv], ignore_index=True)
            df_invest.to_csv(INVEST_FILE, index=False)
            st.success(f"Added {ticker} to your portfolio tracker!")
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
            tot_pnl = float(df_invest["Profit / Loss"].sum())
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
