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

# Adaptive Light / Dark Mode CSS
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
        st.markdown("<p style='text-align: center; color: #6B7280;'>Select account profile and enter your private key.</p>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            with st.form("login_form"):
                selected_user = st.selectbox("Select Account Profile", list(USER_PROFILES.keys()))
                entered_pass = st.text_input("Enter Passkey", type="password", placeholder="••••••••")
                login_btn = st.form_submit_button("Unlock Command Center", use_container_width=True)

                if login_btn:
                    user_info = USER_PROFILES[selected_user]
                    sec_obj = getattr(st, "secrets", {})
                    correct_pass = sec_obj.get(user_info["sec_key"], user_info["def_key"])

                    if entered_pass == correct_pass:
                        st.session_state["authenticated"] = True
                        st.session_state["current_user"] = selected_user
                        st.success(f"Access granted for {selected_user}!")
                        st.rerun()
                    else:
                        st.error("Invalid passkey. Access denied.")
        st.stop()

check_authentication()

current_user = st.session_state["current_user"]
user_cfg = USER_PROFILES[current_user]
DATA_FILE = user_cfg["data_file"]
CONFIG_FILE = user_cfg["config_file"]
INVEST_FILE = user_cfg["invest_file"]

def load_user_config():
    defaults = {
        "salary_bhd": 1500.0,
        "business_bhd": 0.0,
        "sidelines_bhd": 0.0,
        "other_income_bhd": 0.0,
        "fixed_priority_bhd": 400.0,
        "debts_pct": 10,
        "needs_pct": 50,
        "wants_pct": 20,
        "savings_pct": 20,
        "currency_code": "BHD"
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                loaded = json.load(f)
                defaults.update(loaded)
        except Exception:
            pass
    return defaults

def save_user_config(cfg):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=4)
    except Exception:
        pass

cfg_data = load_user_config()

def load_expense_data(file_path):
    expected_cols = ["Item #", "Date", "Main Category", "Sub Category", "Merchant/Description", "Billed Amount", "Actual Paid", "Currency", "Pending Due", "% Paid", "% Remaining", "Equivalent", "Status", "Payment Method", "Amount (BHD)"]
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
            
            # Ensure essential numeric columns are numeric
            for num_col in ["Billed Amount", "Actual Paid", "Amount (BHD)", "Pending Due", "% Paid", "% Remaining"]:
                if num_col in df.columns:
                    df[num_col] = pd.to_numeric(df[num_col], errors="coerce").fillna(0.0)
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=expected_cols)

def save_expense_data(df, file_path):
    try:
        df.to_csv(file_path, index=False)
    except Exception:
        pass

df_expenses = load_expense_data(DATA_FILE)

def load_invest_data(file_path):
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except Exception:
            pass
    return pd.DataFrame(columns=["Type", "Symbol/Ticker", "Platform", "Shares/Lots", "Avg Buy Price", "Current Price", "Notes"])

df_invest = load_invest_data(INVEST_FILE)

# Sidebar Settings
st.sidebar.title(f"👤 {current_user} Settings")
if st.sidebar.button("🔒 Logout Profile", use_container_width=True):
    st.session_state["authenticated"] = False
    st.session_state["current_user"] = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("💵 Multi-Income Streams (BHD)")
salary_bhd = float(st.sidebar.number_input("Primary Salary (BHD)", min_value=0.0, value=float(cfg_data.get("salary_bhd", 1500.0)), step=50.0))
business_bhd = float(st.sidebar.number_input("Business Income (BHD)", min_value=0.0, value=float(cfg_data.get("business_bhd", 0.0)), step=50.0))
sidelines_bhd = float(st.sidebar.number_input("Sidelines / Freelance (BHD)", min_value=0.0, value=float(cfg_data.get("sidelines_bhd", 0.0)), step=50.0))
other_income_bhd = float(st.sidebar.number_input("Other Income (BHD)", min_value=0.0, value=float(cfg_data.get("other_income_bhd", 0.0)), step=50.0))

total_income_bhd = float(salary_bhd + business_bhd + sidelines_bhd + other_income_bhd)

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 100% Mandatory Payments")
fixed_priority_bhd = float(st.sidebar.number_input("Mandatory 100% Target (BHD)", min_value=0.0, value=float(cfg_data.get("fixed_priority_bhd", 400.0)), step=25.0))

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Category Framework Allocation (%)")
debts_pct = int(st.sidebar.slider("Debts & Credits Target %", 0, 100, int(cfg_data.get("debts_pct", 10))))
needs_pct = int(st.sidebar.slider("Needs Target %", 0, 100, int(cfg_data.get("needs_pct", 50))))
wants_pct = int(st.sidebar.slider("Wants Target %", 0, 100, int(cfg_data.get("wants_pct", 20))))
savings_pct = int(st.sidebar.slider("Savings & Investments Target %", 0, 100, int(cfg_data.get("savings_pct", 20))))

tot_pct = debts_pct + needs_pct + wants_pct + savings_pct
if tot_pct != 100:
    st.sidebar.warning(f"Allocation total is {tot_pct}%. Ideally, it should equal 100%.")

framework_title = f"{debts_pct}/{needs_pct}/{wants_pct}/{savings_pct} Framework"

st.sidebar.markdown("---")
display_curr = st.sidebar.selectbox("Display Currency", ["BHD", "PHP", "USD"], index=0)

active_cfg = {
    "salary_bhd": salary_bhd,
    "business_bhd": business_bhd,
    "sidelines_bhd": sidelines_bhd,
    "other_income_bhd": other_income_bhd,
    "fixed_priority_bhd": fixed_priority_bhd,
    "debts_pct": debts_pct,
    "needs_pct": needs_pct,
    "wants_pct": wants_pct,
    "savings_pct": savings_pct,
    "currency_code": display_curr
}
save_user_config(active_cfg)

bhd_to_php = float(rates_dict.get("PHP", 58.50) / rates_dict.get("BHD", 0.377))
bhd_to_usd = float(rates_dict.get("USD", 1.0) / rates_dict.get("BHD", 0.377))

if display_curr == "BHD":
    curr_symbol = "BD "
    rate_mult = 1.0
    curr_code = "BHD"
elif display_curr == "PHP":
    curr_symbol = "₱"
    rate_mult = bhd_to_php
    curr_code = "PHP"
else:
    curr_symbol = "$"
    rate_mult = bhd_to_usd
    curr_code = "USD"

net_bhd_for_budget = max(0.0, float(total_income_bhd - fixed_priority_bhd))

disp_total_income = float(total_income_bhd * rate_mult)
disp_fixed = float(fixed_priority_bhd * rate_mult)
disp_net_budget = float(net_bhd_for_budget * rate_mult)

debts_target_bhd = float(net_bhd_for_budget * (debts_pct / 100.0))
needs_target_bhd = float(net_bhd_for_budget * (needs_pct / 100.0))
wants_target_bhd = float(net_bhd_for_budget * (wants_pct / 100.0))
savings_target_bhd = float(net_bhd_for_budget * (savings_pct / 100.0))

disp_debts_target = float(debts_target_bhd * rate_mult)
disp_needs_target = float(needs_target_bhd * rate_mult)
disp_wants_target = float(wants_target_bhd * rate_mult)
disp_savings_target = float(savings_target_bhd * rate_mult)

utc_now = datetime.now(timezone.utc)
bh_time = utc_now + timedelta(hours=3)
ph_time = utc_now + timedelta(hours=8)

st.markdown('<div class="main-header">💰 Rogee&apos;s Financial Command Center</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Personal Finance System • {framework_title}</div>', unsafe_allow_html=True)

time_badge_html = f'<div class="time-badge">🇧🇭 <b>Bahrain:</b> {bh_time.strftime("%d %b %Y, %I:%M %p")} &nbsp;|&nbsp; 🇵🇭 <b>Philippines:</b> {ph_time.strftime("%d %b %Y, %I:%M %p")} &nbsp;|&nbsp; 👤 <b>Account:</b> {current_user}</div>'
st.markdown(time_badge_html, unsafe_allow_html=True)

rate_mode_str = "Live Auto-Updated" if is_live_rates else "Benchmark Fixed"
st.markdown(f'<div class="rate-card">🌐 <b>Live FX Engine ({rate_mode_str}):</b> <b>1 BHD</b> = <b>₱{bhd_to_php:,.2f} PHP</b> | <b>1 BHD</b> = <b>${bhd_to_usd:,.2f} USD</b> | <b>1 USD</b> = <b>₱{(bhd_to_php/bhd_to_usd):,.2f} PHP</b><span style="float: right; color: #6B7280; font-size: 0.8rem;">Updated: {last_rate_update}</span></div>', unsafe_allow_html=True)

tab_dash, tab_add, tab_history, tab_forex, tab_invest, tab_reports, tab_guide = st.tabs([
    "📈 Dashboard & Analytics",
    "➕ Record Expense",
    "📜 Transaction History",
    "💱 Live Forex Engine",
    "📊 MT5 & COL Investments",
    "📥 Download Reports",
    "📘 User Guide"
])

# Process Actual Spending Safely
if not df_expenses.empty:
    for c in ["Billed Amount", "Actual Paid", "Amount (BHD)"]:
        if c in df_expenses.columns:
            df_expenses[c] = pd.to_numeric(df_expenses[c], errors="coerce").fillna(0.0)
            
    amt_col = "Amount (BHD)" if "Amount (BHD)" in df_expenses.columns else "Amount"
    actual_priority_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("100% Priority", na=False)][amt_col].sum())
    actual_debts_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Debts & Credits", na=False)][amt_col].sum())
    actual_needs_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Needs", na=False)][amt_col].sum())
    actual_wants_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Wants", na=False)][amt_col].sum())
    actual_savings_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Savings", na=False)][amt_col].sum())
else:
    actual_priority_bhd = actual_debts_bhd = actual_needs_bhd = actual_wants_bhd = actual_savings_bhd = 0.0

total_spent_bhd = float(actual_priority_bhd + actual_debts_bhd + actual_needs_bhd + actual_wants_bhd + actual_savings_bhd)
remaining_cash_bhd = float(total_income_bhd - total_spent_bhd)

actual_priority_disp = float(actual_priority_bhd * rate_mult)
actual_debts_disp = float(actual_debts_bhd * rate_mult)
actual_needs_disp = float(actual_needs_bhd * rate_mult)
actual_wants_disp = float(actual_wants_bhd * rate_mult)
actual_savings_disp = float(actual_savings_bhd * rate_mult)

total_spent_disp = float(total_spent_bhd * rate_mult)
remaining_cash_disp = float(remaining_cash_bhd * rate_mult)

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
        st.metric("Pending Mandatory Payments", f"{curr_symbol}{rem_priority_disp:,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader(f"📊 Framework Allocation Matrix ({framework_title})")

    cat_data = [
        {"Category": f"Debts & Credits ({debts_pct}%)", "Target Allocation": f"{debts_pct}%", "Target Amount": disp_debts_target, "Actual Spent": actual_debts_disp, "Variance": disp_debts_target - actual_debts_disp, "Status": "On Track" if actual_debts_disp <= disp_debts_target else "Over Target"},
        {"Category": f"Needs ({needs_pct}%)", "Target Allocation": f"{needs_pct}%", "Target Amount": disp_needs_target, "Actual Spent": actual_needs_disp, "Variance": disp_needs_target - actual_needs_disp, "Status": "On Track" if actual_needs_disp <= disp_needs_target else "Over Target"},
        {"Category": f"Wants ({wants_pct}%)", "Target Allocation": f"{wants_pct}%", "Target Amount": disp_wants_target, "Actual Spent": actual_wants_disp, "Variance": disp_wants_target - actual_wants_disp, "Status": "On Track" if actual_wants_disp <= disp_wants_target else "Over Target"},
        {"Category": f"Savings & Investments ({savings_pct}%)", "Target Allocation": f"{savings_pct}%", "Target Amount": disp_savings_target, "Actual Spent": actual_savings_disp, "Variance": actual_savings_disp - disp_savings_target, "Status": "Target Met" if actual_savings_disp >= disp_savings_target else "Under Goal"}
    ]
    df_cat_summary = pd.DataFrame(cat_data)
    st.dataframe(df_cat_summary.style.format({"Target Amount": f"{curr_symbol}{{:,.2f}}", "Actual Spent": f"{curr_symbol}{{:,.2f}}", "Variance": f"{curr_symbol}{{:,.2f}}"}), use_container_width=True, hide_index=True)

    st.markdown("---")
    col_ch1, col_ch2 = st.columns(2)
    with col_ch1:
        st.subheader("Target vs. Actual Spending")
        chart_df = pd.DataFrame({
            "Category": ["Debts", "Needs", "Wants", "Savings"],
            "Target": [disp_debts_target, disp_needs_target, disp_wants_target, disp_savings_target],
            "Actual": [actual_debts_disp, actual_needs_disp, actual_wants_disp, actual_savings_disp]
        })
        fig_bar = go.Figure(data=[
            go.Bar(name='Target', x=chart_df['Category'], y=chart_df['Target'], marker_color='#93C5FD'),
            go.Bar(name='Actual', x=chart_df['Category'], y=chart_df['Actual'], marker_color='#1D4ED8')
        ])
        fig_bar.update_layout(barmode='group', yaxis_title=f"Amount ({curr_code})", margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_ch2:
        st.subheader("Spending Share by Category")
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
            st.info("No expense data recorded yet.")

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
                sub_cats = ["Credit Card Debt", "Bank Loan / Personal Loan", "Car Loan / Auto Financing", "Mortgage / Housing Loan"]
            elif "Needs" in main_cat:
                sub_cats = ["Housing / Rent", "Utilities & Bills", "Groceries", "Transportation / Fuel", "Healthcare / Insurance"]
            elif "Wants" in main_cat:
                sub_cats = ["Dining Out & Coffee", "Entertainment & Streaming", "Shopping & Apparel", "Hobbies & Travel", "Subscriptions"]
            else:
                sub_cats = ["Emergency Fund", "COL Stock Investments", "MT5 Trading Deposit", "Index Funds / Mutual Funds", "Pension / Retirement"]

            sub_cat = st.selectbox("Sub-Category", sub_cats)

        with col_b:
            merchant = st.text_input("Merchant / Description / Payee", placeholder="e.g. Household Helper Salary, Landlord, Grocery")
            billed_input = float(st.number_input("Billed / Planned Amount", min_value=0.01, step=5.0, value=25.0))
            pay_status = st.selectbox("Payment Status", ["Paid", "Pending Payment", "Partially Paid", "Not Paid"], index=0)
            
            if pay_status == "Paid":
                def_paid = billed_input
            elif pay_status in ["Pending Payment", "Not Paid"]:
                def_paid = 0.0
            else:
                def_paid = billed_input / 2.0

            actual_paid_input = float(st.number_input("Actual Amount Paid", min_value=0.0, step=5.0, value=def_paid))
            input_currency = st.selectbox("Payment Currency", ["BHD", "PHP", "USD"], index=0)
            payment_method = st.selectbox("Payment Method", ["Benefit Pay", "Remittance", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])

        submit_btn = st.form_submit_button("Save Payment Record", use_container_width=True)

        if submit_btn:
            if input_currency == "BHD":
                amt_bhd = billed_input
            elif input_currency == "PHP":
                amt_bhd = billed_input / bhd_to_php
            else:
                amt_bhd = billed_input / bhd_to_usd

            pending_due = max(0.0, billed_input - actual_paid_input)
            pct_paid = (actual_paid_input / billed_input * 100.0) if billed_input > 0 else 0.0
            pct_rem = max(0.0, 100.0 - pct_paid)

            if input_currency == "BHD":
                equiv_str = f"BD {billed_input:,.2f} (₱{billed_input*bhd_to_php:,.2f} | ${billed_input*bhd_to_usd:,.2f})"
            elif input_currency == "PHP":
                equiv_str = f"₱{billed_input:,.2f} (BD {amt_bhd:,.2f} | ${amt_bhd*bhd_to_usd:,.2f})"
            else:
                equiv_str = f"${billed_input:,.2f} (BD {amt_bhd:,.2f} | ₱{amt_bhd*bhd_to_php:,.2f})"

            new_row = pd.DataFrame([{
                "Item #": len(df_expenses) + 1,
                "Date": exp_date,
                "Main Category": main_cat,
                "Sub Category": sub_cat,
                "Merchant/Description": merchant if merchant else "Unspecified",
                "Billed Amount": billed_input,
                "Actual Paid": actual_paid_input,
                "Currency": input_currency,
                "Pending Due": pending_due,
                "% Paid": pct_paid,
                "% Remaining": pct_rem,
                "Equivalent": equiv_str,
                "Status": pay_status,
                "Payment Method": payment_method,
                "Amount (BHD)": amt_bhd
            }])

            df_expenses = pd.concat([df_expenses, new_row], ignore_index=True)
            save_expense_data(df_expenses, DATA_FILE)
            st.success(f"Recorded transaction: {merchant if merchant else sub_cat} ({pay_status})!")
            st.rerun()

# TAB 3: TRANSACTION HISTORY
with tab_history:
    st.subheader(f"📜 Recorded Transaction History ({current_user})")

    if not df_expenses.empty:
        # Category ordering definition
        cat_order = {
            "100% Priority": 1,
            "Debts & Credits": 2,
            "Needs": 3,
            "Wants": 4,
            "Savings & Investments": 5
        }
        
        def get_cat_rank(cat_str):
            for k, rank in cat_order.items():
                if k in str(cat_str):
                    return rank
            return 99

        df_display = df_expenses.copy()
        
        # Safe numeric parsing
        for num_c in ["Billed Amount", "Actual Paid", "Amount (BHD)", "Pending Due"]:
            if num_c in df_display.columns:
                df_display[num_c] = pd.to_numeric(df_display[num_c], errors="coerce").fillna(0.0)

        # Update dynamic linked columns
        df_display["Pending Due"] = (df_display["Billed Amount"] - df_display["Actual Paid"]).clip(lower=0.0)
        df_display["% Paid"] = (df_display["Actual Paid"] / df_display["Billed Amount"] * 100.0).fillna(0.0)
        df_display["% Remaining"] = (100.0 - df_display["% Paid"]).clip(lower=0.0)

        # Categorical and Chronological Sorting
        df_display["CatRank"] = df_display["Main Category"].apply(get_cat_rank)
        df_display = df_display.sort_values(by=["CatRank", "Date"], ascending=[True, True]).drop(columns=["CatRank"])
        df_display["Item #"] = range(1, len(df_display) + 1)

        # Build Equivalent Column String
        def format_equiv(row):
            cur = str(row.get("Currency", "BHD"))
            b_amt = float(row.get("Billed Amount", 0.0))
            if cur == "BHD":
                return f"BD {b_amt:,.2f} (₱{b_amt*bhd_to_php:,.2f} | ${b_amt*bhd_to_usd:,.2f})"
            elif cur == "PHP":
                bhd_val = b_amt / bhd_to_php
                return f"₱{b_amt:,.2f} (BD {bhd_val:,.2f} | ${bhd_val*bhd_to_usd:,.2f})"
            else:
                bhd_val = b_amt / bhd_to_usd
                return f"${b_amt:,.2f} (BD {bhd_val:,.2f} | ₱{bhd_val*bhd_to_php:,.2f})"

        df_display["Equivalent"] = df_display.apply(format_equiv, axis=1)

        column_order = [
            "Item #", "Date", "Main Category", "Sub Category", "Merchant/Description",
            "Billed Amount", "Actual Paid", "Currency", "Pending Due", "% Paid",
            "% Remaining", "Equivalent", "Status", "Payment Method"
        ]
        
        # Ensure all columns exist
        for col in column_order:
            if col not in df_display.columns:
                df_display[col] = 0.0 if "Amount" in col or "%" in col or "Due" in col else "Unspecified"

        df_display = df_display[column_order]

        st.caption("✏️ **Editable Ledger:** Edit dates, categories, merchant descriptions, billed amounts, and actual paid directly in the table below. Linked columns update automatically!")

        edited_df = st.data_editor(
            df_display,
            num_rows="dynamic",
            use_container_width=True,
            key=f"editor_{current_user}",
            disabled=["Item #", "Pending Due", "% Paid", "% Remaining", "Equivalent"]
        )

        col_h1, col_h2 = st.columns(2)
        with col_h1:
            if st.button("💾 Save Ledger Changes", type="primary", use_container_width=True):
                # Recalculate Amount (BHD) upon save
                def calc_bhd(row):
                    curr = str(row["Currency"])
                    billed = float(row["Billed Amount"])
                    if curr == "BHD": return billed
                    elif curr == "PHP": return billed / bhd_to_php
                    else: return billed / bhd_to_usd

                edited_df["Amount (BHD)"] = edited_df.apply(calc_bhd, axis=1)
                save_expense_data(edited_df, DATA_FILE)
                st.success("Transaction history updated and saved successfully!")
                st.rerun()

        with col_h2:
            if st.button("🗑️ Clear Entire History", use_container_width=True):
                if os.path.exists(DATA_FILE):
                    os.remove(DATA_FILE)
                st.success("All transaction records cleared!")
                st.rerun()

        st.markdown("---")
        st.subheader("💰 Total Outstanding & Payment Summary Ledger")

        # Compute BHD totals safely
        def row_billed_bhd(row):
            c = str(row["Currency"])
            val = float(row["Billed Amount"])
            return val if c == "BHD" else (val / bhd_to_php if c == "PHP" else val / bhd_to_usd)

        def row_paid_bhd(row):
            c = str(row["Currency"])
            val = float(row["Actual Paid"])
            return val if c == "BHD" else (val / bhd_to_php if c == "PHP" else val / bhd_to_usd)

        sum_billed_bhd = float(df_display.apply(row_billed_bhd, axis=1).sum()) if not df_display.empty else 0.0
        sum_paid_bhd = float(df_display.apply(row_paid_bhd, axis=1).sum()) if not df_display.empty else 0.0
        sum_rem_bhd = max(0.0, float(sum_billed_bhd - sum_paid_bhd))

        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            st.markdown("#### 📋 Total Billed / Needed")
            st.write(f"• **BHD:** BD {sum_billed_bhd:,.2f}")
            st.write(f"• **PHP:** ₱{(sum_billed_bhd * bhd_to_php):,.2f}")
            st.write(f"• **USD:** ${(sum_billed_bhd * bhd_to_usd):,.2f}")

        with s_col2:
            st.markdown("#### ✅ Total Amount Paid")
            st.write(f"• **BHD:** BD {sum_paid_bhd:,.2f}")
            st.write(f"• **PHP:** ₱{(sum_paid_bhd * bhd_to_php):,.2f}")
            st.write(f"• **USD:** ${(sum_paid_bhd * bhd_to_usd):,.2f}")

        with s_col3:
            st.markdown("#### ⏳ Total Outstanding Due")
            st.write(f"• **BHD:** BD {sum_rem_bhd:,.2f}")
            st.write(f"• **PHP:** ₱{(sum_rem_bhd * bhd_to_php):,.2f}")
            st.write(f"• **USD:** ${(sum_rem_bhd * bhd_to_usd):,.2f}")

    else:
        st.info("No transaction history recorded yet.")

# TAB 4: FOREX ENGINE
with tab_forex:
    st.subheader("💱 Live Multi-Currency Exchange Engine")
    fx_col1, fx_col2 = st.columns(2)
    with fx_col1:
        st.markdown("#### Interactive Currency Converter")
        calc_amt = float(st.number_input("Amount to Convert", min_value=1.0, value=100.0, step=10.0))
        pair_from = st.selectbox("From Currency", ["BHD", "PHP", "USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"], index=0)
        pair_to = st.selectbox("To Currency", ["PHP", "USD", "BHD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"], index=0)

        rate_from_usd = float(rates_dict.get(pair_from, 1.0))
        rate_to_usd = float(rates_dict.get(pair_to, 1.0))
        cross_rate = float(rate_to_usd / rate_from_usd)
        converted_val = float(calc_amt * cross_rate)

        st.success(f"### {calc_amt:,.2f} {pair_from} = **{converted_val:,.2f} {pair_to}**")
        st.info(f"💡 **Exchange Rate:** 1 {pair_from} = {cross_rate:,.4f} {pair_to}")

    with fx_col2:
        st.markdown("#### Live Major & Cross Pairs Ticker")
        st.write(f"• **1 BHD → PHP:** ₱{bhd_to_php:,.2f} PHP")
        st.write(f"• **1 BHD → USD:** ${bhd_to_usd:,.2f} USD")
        st.write(f"• **1 USD → PHP:** ₱{(bhd_to_php/bhd_to_usd):,.2f} PHP")
        st.write(f"• **1 USD → CHF:** {rates_dict.get('CHF', 0.865):,.4f} CHF")
        st.write(f"• **1 AUD → CAD:** {(rates_dict.get('CAD', 1.38)/rates_dict.get('AUD', 1.51)):,.4f} CAD")
        st.write(f"• **1 NZD → USD:** {(1.0/rates_dict.get('NZD', 1.66)):,.4f} USD")

        if st.button("🔄 Force Refresh Rates Now"):
            st.cache_data.clear()
            st.rerun()

# TAB 5: INVESTMENTS & CALCULATORS
with tab_invest:
    st.subheader("📊 MT5 Forex & COL Financial Portfolio Manager")
    
    st.markdown("#### 🧮 Live MT5 Trading Calculators")
    calc_c1, calc_c2 = st.columns(2)
    with calc_c1:
        st.markdown("##### 📍 Pip Value Calculator")
        trade_pair = st.selectbox("Currency Pair / Asset", ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD (Gold)", "USDCHF", "AUDUSD"], index=0)
        lot_size = float(st.number_input("Trade Volume (Lots)", min_value=0.01, value=1.0, step=0.1))
        acc_curr = st.selectbox("Account Currency", ["USD", "BHD", "PHP"], index=0)

        base_pip = 10.0 if "XAUUSD" not in trade_pair else 100.0
        pip_val_usd = float(lot_size * base_pip)
        pip_val_disp = pip_val_usd if acc_curr == "USD" else (pip_val_usd * 0.377 if acc_curr == "BHD" else pip_val_usd * 58.5)
        st.info(f"**Pip Value:** {pip_val_disp:,.2f} {acc_curr} per pip")

    with calc_c2:
        st.markdown("##### 🛡️ Required Margin Calculator")
        margin_lots = float(st.number_input("Lot Size", min_value=0.01, value=1.0, step=0.1))
        leverage = st.selectbox("Account Leverage", [100, 200, 500, 1000], index=2)

        notional_usd = float(margin_lots * 100000.0)
        req_margin_usd = float(notional_usd / leverage)
        req_margin_disp = req_margin_usd if acc_curr == "USD" else (req_margin_usd * 0.377 if acc_curr == "BHD" else req_margin_usd * 58.5)
        st.info(f"**Required Margin:** {req_margin_disp:,.2f} {acc_curr} (at 1:{leverage} leverage)")

    st.markdown("---")
    with st.form("add_investment_form", clear_on_submit=True):
        st.markdown("#### Log New Asset / Trading Position")
        inv_col1, inv_col2 = st.columns(2)
        with inv_col1:
            inv_type = st.selectbox("Asset Class / Platform", ["COL Financial (PH Stocks)", "MetaTrader 5 (Forex / Indices)", "Crypto / Other"])
            ticker = st.text_input("Ticker / Symbol", placeholder="e.g., ALI, BDO, EURUSD, XAUUSD")
            platform = st.text_input("Broker / Platform", placeholder="e.g., COL Financial, Exness, IC Markets")
        with inv_col2:
            shares = float(st.number_input("Shares / Lots", min_value=0.01, value=100.0))
            buy_price = float(st.number_input("Avg Buy Price", min_value=0.0001, value=10.0))
            curr_price = float(st.number_input("Current Market Price", min_value=0.0001, value=12.0))

        inv_submit = st.form_submit_button("Save Asset Record", use_container_width=True)
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
            st.success(f"Added {ticker} to portfolio!")
            st.rerun()

    if not df_invest.empty:
        st.markdown("#### Current Investment Portfolio")
        df_invest["Shares/Lots"] = pd.to_numeric(df_invest["Shares/Lots"], errors="coerce").fillna(0.0)
        df_invest["Avg Buy Price"] = pd.to_numeric(df_invest["Avg Buy Price"], errors="coerce").fillna(0.0)
        df_invest["Current Price"] = pd.to_numeric(df_invest["Current Price"], errors="coerce").fillna(0.0)

        df_invest["Total Value"] = df_invest["Shares/Lots"] * df_invest["Current Price"]
        df_invest["Total Cost"] = df_invest["Shares/Lots"] * df_invest["Avg Buy Price"]
        df_invest["Profit / Loss"] = df_invest["Total Value"] - df_invest["Total Cost"]

        st.dataframe(df_invest, use_container_width=True, hide_index=True)

        col_tot1, col_tot2 = st.columns(2)
        with col_tot1:
            st.metric("Total Equity ($)", f"${df_invest['Total Value'].sum():,.2f}")
        with col_tot2:
            tot_pnl = float(df_invest['Profit / Loss'].sum())
            st.metric("Unrealized P&L ($)", f"${tot_pnl:,.2f}", delta=f"${tot_pnl:,.2f}")

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
        st.markdown("#### 📜 Executive Summary Report (.TXT)")
        rep_date = datetime.today().strftime("%Y-%m-%d")
        
        report_content = f"""==================================================
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
   - Equivalent in PHP   : ₱{(total_income_bhd * bhd_to_php):,.2f}
   - Equivalent in USD   : ${(total_income_bhd * bhd_to_usd):,.2f}

--------------------------------------------------
2. EXPENSES BREAKDOWN BY CATEGORY
--------------------------------------------------
- Mandatory 100% Payments: BD {actual_priority_bhd:,.2f}
- Debts ({debts_pct}%)            : BD {actual_debts_bhd:,.2f}
- Needs ({needs_pct}%)            : BD {actual_needs_bhd:,.2f}
- Wants ({wants_pct}%)            : BD {actual_wants_bhd:,.2f}
- Savings ({savings_pct}%)          : BD {actual_savings_bhd:,.2f}
--------------------------------------------------
GRAND TOTAL EXPENSES     : BD {total_spent_bhd:,.2f}
NET REMAINING CASH       : BD {remaining_cash_bhd:,.2f}
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
