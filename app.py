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

    .positive-banner { background-color: #F0FDF4; border: 1px solid #BBF7D0; border-left: 5px solid #22C55E; padding: 12px 16px; border-radius: 6px; margin-bottom: 14px; color: #166534 !important; font-size: 1.05rem; }
    .positive-banner * { color: #166534 !important; }
    @media (prefers-color-scheme: dark) {
        .positive-banner { background-color: #052E16 !important; border-color: #14532D !important; border-left: 5px solid #22C55E !important; color: #BBF7D0 !important; }
        .positive-banner * { color: #BBF7D0 !important; }
    }

    .negative-banner { background-color: #FEF2F2; border: 1px solid #FECACA; border-left: 5px solid #EF4444; padding: 12px 16px; border-radius: 6px; margin-bottom: 14px; color: #991B1B !important; font-size: 1.05rem; }
    .negative-banner * { color: #991B1B !important; }
    @media (prefers-color-scheme: dark) {
        .negative-banner { background-color: #450A0A !important; border-color: #7F1D1D !important; border-left: 5px solid #EF4444 !important; color: #FECACA !important; }
        .negative-banner * { color: #FECACA !important; }
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
        st.markdown("<p style='text-align: center; color: #6B7280;'>Select your user profile and enter your access passkey.</p>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            sel_user = st.selectbox("Select User Profile", list(USER_PROFILES.keys()))
            pass_input = st.text_input("Passkey / Security Code", type="password")
            
            p_info = USER_PROFILES[sel_user]
            expected_key = st.secrets.get(p_info["sec_key"], p_info["def_key"])
            
            if st.button("Unlock Command Center", type="primary", use_container_width=True):
                if pass_input == expected_key:
                    st.session_state["authenticated"] = True
                    st.session_state["current_user"] = sel_user
                    st.success(f"Welcome back, {sel_user}!")
                    st.rerun()
                else:
                    st.error("Invalid passkey. Please check and try again.")
        return False
    return True

if not check_authentication():
    st.stop()

current_user = st.session_state["current_user"]
user_info = USER_PROFILES[current_user]

DATA_FILE = user_info["data_file"]
CONFIG_FILE = user_info["config_file"]
INVEST_FILE = user_info["invest_file"]

def load_user_config():
    default_config = {
        "monthly_salary": 5000.0,
        "business_income": 0.0,
        "sidelines_income": 0.0,
        "other_income": 0.0,
        "currency_symbol": "BD",
        "debts_pct": 15,
        "needs_pct": 45,
        "wants_pct": 20,
        "savings_pct": 20
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                saved = json.load(f)
                default_config.update(saved)
        except Exception:
            pass
    return default_config

def save_user_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except Exception:
        pass

user_config = load_user_config()

def load_data():
    expected_cols = [
        "Item #", "Date", "Main Category", "Sub Category", "Merchant/Description",
        "Billed Amount", "Actual Paid", "Currency", "Pending Due", "% Paid", "% Remaining",
        "Equivalent", "Status", "Payment Method", "Amount_BHD", "Paid_BHD"
    ]
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
            
            # Legacy column conversion
            if "Billed Amount" not in df.columns:
                if "Amount" in df.columns: df["Billed Amount"] = df["Amount"]
                elif "Amount (BHD)" in df.columns: df["Billed Amount"] = df["Amount (BHD)"]
                else: df["Billed Amount"] = 0.0
            
            if "Actual Paid" not in df.columns:
                if "Amount Paid" in df.columns: df["Actual Paid"] = df["Amount Paid"]
                else: df["Actual Paid"] = df["Billed Amount"]

            if "Currency" not in df.columns: df["Currency"] = "BHD"
            if "Payment Method" not in df.columns: df["Payment Method"] = "Bank Transfer"
            
            # Ensure numbers
            df["Billed Amount"] = pd.to_numeric(df["Billed Amount"], errors="coerce").fillna(0.0)
            df["Actual Paid"] = pd.to_numeric(df["Actual Paid"], errors="coerce").fillna(0.0)
            
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=expected_cols)

def save_data(df, filepath=DATA_FILE):
    df.to_csv(filepath, index=False)

df_expenses = load_data()

# Sidebar Settings
st.sidebar.title(f"⚙️ Settings ({current_user})")

curr_symbol = st.sidebar.selectbox("Display Currency", ["BD", "₱", "$", "€", "£", "A$"], index=0)

bhd_rate = rates_dict.get("BHD", 0.377)
php_rate = rates_dict.get("PHP", 58.50)
usd_rate = rates_dict.get("USD", 1.0)

bhd_to_php = php_rate / bhd_rate if bhd_rate > 0 else 155.08
bhd_to_usd = usd_rate / bhd_rate if bhd_rate > 0 else 2.6525

if curr_symbol == "BD": rate_mult = 1.0
elif curr_symbol == "₱": rate_mult = bhd_to_php
elif curr_symbol == "$": rate_mult = bhd_to_usd
elif curr_symbol == "€": rate_mult = (rates_dict.get("EUR", 0.92) / bhd_rate)
elif curr_symbol == "£": rate_mult = (rates_dict.get("GBP", 0.78) / bhd_rate)
elif curr_symbol == "A$": rate_mult = (rates_dict.get("AUD", 1.51) / bhd_rate)
else: rate_mult = 1.0

st.sidebar.markdown("---")
st.sidebar.subheader("💵 Income Streams (BHD)")
salary_bhd = st.sidebar.number_input(f"Primary Salary (BD)", min_value=0.0, value=float(user_config.get("monthly_salary", 5000.0)), step=50.0)
business_bhd = st.sidebar.number_input(f"Business Income (BD)", min_value=0.0, value=float(user_config.get("business_income", 0.0)), step=50.0)
sidelines_bhd = st.sidebar.number_input(f"Sidelines / Freelance (BD)", min_value=0.0, value=float(user_config.get("sidelines_income", 0.0)), step=50.0)
other_income_bhd = st.sidebar.number_input(f"Other Income (BD)", min_value=0.0, value=float(user_config.get("other_income", 0.0)), step=50.0)

total_income_bhd = salary_bhd + business_bhd + sidelines_bhd + other_income_bhd
disp_total_income = total_income_bhd * rate_mult

st.sidebar.markdown("---")
st.sidebar.subheader("📊 4-Category Ratios (%)")

debts_pct = st.sidebar.slider("Debts & Credits %", 0, 100, int(user_config.get("debts_pct", 15)))
needs_pct = st.sidebar.slider("Needs % (Essentials)", 0, 100, int(user_config.get("needs_pct", 45)))
wants_pct = st.sidebar.slider("Wants % (Lifestyle)", 0, 100, int(user_config.get("wants_pct", 20)))
savings_pct = st.sidebar.slider("Savings & Investments %", 0, 100, int(user_config.get("savings_pct", 20)))

tot_ratio = debts_pct + needs_pct + wants_pct + savings_pct
if tot_ratio != 100:
    st.sidebar.warning(f"Allocation total is {tot_ratio}%. Recommended sum is 100%.")

framework_title = f"{debts_pct}/{needs_pct}/{wants_pct}/{savings_pct} Framework"

# Save config updates
new_cfg = {
    "monthly_salary": salary_bhd,
    "business_income": business_bhd,
    "sidelines_income": sidelines_bhd,
    "other_income": other_income_bhd,
    "currency_symbol": curr_symbol,
    "debts_pct": debts_pct,
    "needs_pct": needs_pct,
    "wants_pct": wants_pct,
    "savings_pct": savings_pct
}
if new_cfg != user_config:
    save_user_config(new_cfg)

if st.sidebar.button("🔒 Lock & Logout"):
    st.session_state["authenticated"] = False
    st.session_state["current_user"] = None
    st.rerun()

# Time Clock Header
utc_now = datetime.now(timezone.utc)
bh_time = utc_now + timedelta(hours=3)
ph_time = utc_now + timedelta(hours=8)

time_html = f"""<div class="time-badge">
    <b>Account:</b> {current_user} &nbsp;|&nbsp; 
    <b>Bahrain Time:</b> {bh_time.strftime("%d %b %Y, %I:%M %p")} AST &nbsp;|&nbsp; 
    <b>Philippine Time:</b> {ph_time.strftime("%d %b %Y, %I:%M %p")} PHT
</div>"""
st.markdown(time_html, unsafe_allow_html=True)

# Main Title Header
st.markdown(f'<div class="main-header">Rogee Financial Command Center</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Personal Salary & Expense Manager — {framework_title}</div>', unsafe_allow_html=True)

# Process expenses dataframe and calculate BHD normalized values
if not df_expenses.empty:
    # Ensure numeric
    df_expenses["Billed Amount"] = pd.to_numeric(df_expenses["Billed Amount"], errors="coerce").fillna(0.0)
    df_expenses["Actual Paid"] = pd.to_numeric(df_expenses["Actual Paid"], errors="coerce").fillna(0.0)
    
    # Calculate BHD normalized amounts
    def conv_to_bhd(row, val_col):
        val = float(row[val_col])
        curr = str(row.get("Currency", "BHD")).upper()
        if curr == "PHP": return val / bhd_to_php if bhd_to_php > 0 else val
        elif curr == "USD": return val / bhd_to_usd if bhd_to_usd > 0 else val
        return val

    df_expenses["Amount_BHD"] = df_expenses.apply(lambda r: conv_to_bhd(r, "Billed Amount"), axis=1)
    df_expenses["Paid_BHD"] = df_expenses.apply(lambda r: conv_to_bhd(r, "Actual Paid"), axis=1)
    
    # Status Auto-Calculation
    def calc_status_row(row):
        billed = float(row["Billed Amount"])
        paid = float(row["Actual Paid"])
        if billed <= 0:
            pct = 100.0 if paid > 0 else 0.0
        else:
            pct = (paid / billed) * 100.0
        
        if pct >= 99.99 or paid >= billed and billed > 0:
            return "Paid", 100.0, 0.0, 0.0
        elif pct <= 0.01 or paid <= 0:
            return "Not Paid", 0.0, 100.0, billed
        else:
            pct_p = round(min(pct, 99.9), 1)
            pct_r = round(100.0 - pct_p, 1)
            rem_due = max(billed - paid, 0.0)
            return "Partially Paid", pct_p, pct_r, rem_due

    res = df_expenses.apply(calc_status_row, axis=1)
    df_expenses["Status"] = [r[0] for r in res]
    df_expenses["% Paid"] = [f"{r[1]:.1f}%" for r in res]
    df_expenses["% Remaining"] = [f"{r[2]:.1f}%" for r in res]
    df_expenses["Pending Due"] = [r[3] for r in res]

    def make_equiv(row):
        bhd = float(row["Amount_BHD"])
        php = bhd * bhd_to_php
        usd = bhd * bhd_to_usd
        return f"BD {bhd:,.2f} (₱{php:,.2f} | ${usd:,.2f})"

    df_expenses["Equivalent"] = df_expenses.apply(make_equiv, axis=1)

else:
    df_expenses["Amount_BHD"] = 0.0
    df_expenses["Paid_BHD"] = 0.0

# Aggregations
actual_priority_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("100% Priority", na=False)]["Paid_BHD"].sum()) if not df_expenses.empty else 0.0
actual_debts_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Debts", na=False)]["Paid_BHD"].sum()) if not df_expenses.empty else 0.0
actual_needs_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Needs", na=False)]["Paid_BHD"].sum()) if not df_expenses.empty else 0.0
actual_wants_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Wants", na=False)]["Paid_BHD"].sum()) if not df_expenses.empty else 0.0
actual_savings_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Savings", na=False)]["Paid_BHD"].sum()) if not df_expenses.empty else 0.0

total_spent_bhd = actual_priority_bhd + actual_debts_bhd + actual_needs_bhd + actual_wants_bhd + actual_savings_bhd
net_remaining_bhd = total_income_bhd - total_spent_bhd

net_remaining_disp = net_remaining_bhd * rate_mult
total_spent_disp = total_spent_bhd * rate_mult

savings_rate = (actual_savings_bhd / total_income_bhd * 100) if total_income_bhd > 0 else 0.0

# Prominent Net Balance / Over-Budget Banner
rem_php = net_remaining_bhd * bhd_to_php
rem_usd = net_remaining_bhd * bhd_to_usd

if net_remaining_bhd >= 0:
    banner_html = f"""<div class="positive-banner">
        <b>🟢 POSITIVE NET REMAINING CASH:</b> BD {net_remaining_bhd:,.2f} &nbsp;|&nbsp; ₱{rem_php:,.2f} &nbsp;|&nbsp; ${rem_usd:,.2f}
        <br><small>You are within your income budget! Keep building your savings and investment targets.</small>
    </div>"""
else:
    over_bhd = abs(net_remaining_bhd)
    over_php = over_bhd * bhd_to_php
    over_usd = over_bhd * bhd_to_usd
    banner_html = f"""<div class="negative-banner">
        <b>⚠️ OVER BUDGET ALERT (NEGATIVE REMAINING CASH):</b> -BD {over_bhd:,.2f} &nbsp;|&nbsp; -₱{over_php:,.2f} &nbsp;|&nbsp; -${over_usd:,.2f}
        <br><small>Your total recorded spending exceeds your total monthly income! Review your 'Wants' or 'Debts' to balance your ledger.</small>
    </div>"""

st.markdown(banner_html, unsafe_allow_html=True)

# Navigation Tabs
tab_dash, tab_add, tab_history, tab_invest, tab_reports, tab_guide = st.tabs([
    "📊 Dashboard & Analytics",
    "➕ Record Expense",
    "📜 Transaction History",
    "📈 MT5 & COL Investments",
    "📥 Download Reports",
    "📘 User Guide"
])

# TAB 1: DASHBOARD
with tab_dash:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Monthly Combined Income", f"{curr_symbol}{disp_total_income:,.2f}", f"BD {total_income_bhd:,.2f}")
    m2.metric("Total Actual Spent", f"{curr_symbol}{total_spent_disp:,.2f}", delta=f"-{curr_symbol}{total_spent_disp:,.2f}", delta_color="inverse")
    
    if net_remaining_bhd >= 0:
        m3.metric("Net Cash Remaining", f"{curr_symbol}{net_remaining_disp:,.2f}", delta=f"+{curr_symbol}{net_remaining_disp:,.2f}")
    else:
        m3.metric("Over Budget Balance", f"{curr_symbol}{net_remaining_disp:,.2f}", delta=f"{curr_symbol}{net_remaining_disp:,.2f}", delta_color="inverse")
        
    m4.metric("Savings Rate", f"{savings_rate:.1f}%", delta=f"{savings_rate - savings_pct:.1f}% vs Target")

    st.markdown("---")

    # Allocation Targets vs Actuals
    net_allocable_bhd = max(total_income_bhd - actual_priority_bhd, 0.0)
    
    target_debts_bhd = net_allocable_bhd * (debts_pct / 100.0)
    target_needs_bhd = net_allocable_bhd * (needs_pct / 100.0)
    target_wants_bhd = net_allocable_bhd * (wants_pct / 100.0)
    target_savings_bhd = net_allocable_bhd * (savings_pct / 100.0)

    st.subheader(f"📊 {framework_title} Benchmark Allocation Summary")
    
    cat_summary_data = [
        {"Category": "Mandatory 100% Priority", "Target %": "100%", "Target Amount": f"BD {actual_priority_bhd:,.2f}", "Actual Spent": f"BD {actual_priority_bhd:,.2f}", "Status": "Fixed Obligation"},
        {"Category": f"Debts & Credits ({debts_pct}%)", "Target %": f"{debts_pct}%", "Target Amount": f"BD {target_debts_bhd:,.2f}", "Actual Spent": f"BD {actual_debts_bhd:,.2f}", "Status": "On Track" if actual_debts_bhd <= target_debts_bhd else "Over Target"},
        {"Category": f"Needs ({needs_pct}%)", "Target %": f"{needs_pct}%", "Target Amount": f"BD {target_needs_bhd:,.2f}", "Actual Spent": f"BD {actual_needs_bhd:,.2f}", "Status": "On Track" if actual_needs_bhd <= target_needs_bhd else "Over Target"},
        {"Category": f"Wants ({wants_pct}%)", "Target %": f"{wants_pct}%", "Target Amount": f"BD {target_wants_bhd:,.2f}", "Actual Spent": f"BD {actual_wants_bhd:,.2f}", "Status": "On Track" if actual_wants_bhd <= target_wants_bhd else "Over Target"},
        {"Category": f"Savings & Investments ({savings_pct}%)", "Target %": f"{savings_pct}%", "Target Amount": f"BD {target_savings_bhd:,.2f}", "Actual Spent": f"BD {actual_savings_bhd:,.2f}", "Status": "Goal Met" if actual_savings_bhd >= target_savings_bhd else "Below Goal"}
    ]
    st.dataframe(pd.DataFrame(cat_summary_data), use_container_width=True, hide_index=True)

    st.markdown("---")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.subheader("Target vs. Actual Spending (BD)")
        chart_df = pd.DataFrame({
            "Category": ["Debts", "Needs", "Wants", "Savings"],
            "Target": [target_debts_bhd, target_needs_bhd, target_wants_bhd, target_savings_bhd],
            "Actual": [actual_debts_bhd, actual_needs_bhd, actual_wants_bhd, actual_savings_bhd]
        })
        fig_bar = go.Figure(data=[
            go.Bar(name='Target Target', x=chart_df['Category'], y=chart_df['Target'], marker_color='#93C5FD'),
            go.Bar(name='Actual Paid', x=chart_df['Category'], y=chart_df['Actual'], marker_color='#1D4ED8')
        ])
        fig_bar.update_layout(barmode='group', margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_c2:
        st.subheader("Actual Expense Distribution Share")
        if total_spent_bhd > 0:
            fig_pie = px.pie(
                values=[actual_priority_bhd, actual_debts_bhd, actual_needs_bhd, actual_wants_bhd, actual_savings_bhd],
                names=["Priority", "Debts", "Needs", "Wants", "Savings"],
                color_discrete_sequence=['#EF4444', '#F59E0B', '#2563EB', '#8B5CF6', '#10B981'],
                hole=0.45
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expense transactions recorded yet.")

# TAB 2: RECORD EXPENSE
with tab_add:
    st.subheader("➕ Record a New Payment / Expense")
    
    # Real-time reactive Category selectbox OUTSIDE the form so sub-categories update instantly!
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        cat_options = [
            "100% Priority & People to Pay",
            f"Debts & Credits ({debts_pct}%)",
            f"Needs ({needs_pct}%)",
            f"Wants ({wants_pct}%)",
            f"Savings & Investments ({savings_pct}%)"
        ]
        selected_main_cat = st.selectbox("Select Main Category", cat_options, key="record_main_cat_select")
        
    with col_sel2:
        if "Priority" in selected_main_cat:
            sub_options = ["Family Salary / Remittance", "House Rent / Allowance", "Tithes & Obligations", "Priority Loan Payoff", "Emergency Family Support"]
        elif "Debts" in selected_main_cat:
            sub_options = ["Credit Card Minimum", "Bank Personal Loan", "Car Loan Installment", "Housing Loan", "Peer / Family Debt"]
        elif "Needs" in selected_main_cat:
            sub_options = ["Housing / Rent", "Utilities & Bills (Electricity/Water)", "Groceries & Supplies", "Transportation / Fuel", "Healthcare & Medicine", "Insurance Premiums"]
        elif "Wants" in selected_main_cat:
            sub_options = ["Dining Out & Coffee", "Shopping & Apparel", "Entertainment & Streaming", "Hobbies & Travel", "Subscriptions", "Miscellaneous"]
        else:
            sub_options = ["Emergency Fund Deposit", "COL Stock Investment", "MT5 Trading Account Deposit", "Index Funds / ETFs", "Pension & Long-Term Savings"]
            
        selected_sub_cat = st.selectbox("Select Sub-Category", sub_options, key="record_sub_cat_select")

    st.markdown("---")

    with st.form("add_expense_form", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            exp_date = st.date_input("Transaction Date", value=datetime.today())
            merchant = st.text_input("Merchant / Description", placeholder="e.g., Landlord Rent, Bank Loan, Supermarket")
        with f2:
            billed_amt = st.number_input("Billed / Planned Amount", min_value=0.0, value=100.0, step=10.0)
            actual_paid_amt = st.number_input("Actual Amount Paid", min_value=0.0, value=100.0, step=10.0)
        with f3:
            curr_type = st.selectbox("Currency Paid In", ["BHD", "PHP", "USD"], index=0)
            pay_method = st.selectbox("Payment Method", ["Benefit Pay", "Remittance", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])

        submit_btn = st.form_submit_button("💾 Save Payment Record", type="primary", use_container_width=True)

        if submit_btn:
            # Auto-calculate status
            if billed_amt <= 0:
                calc_status = "Paid" if actual_paid_amt > 0 else "Not Paid"
            else:
                p_ratio = (actual_paid_amt / billed_amt) * 100.0
                if p_ratio >= 99.99 or actual_paid_amt >= billed_amt: calc_status = "Paid"
                elif p_ratio <= 0.01 or actual_paid_amt <= 0: calc_status = "Not Paid"
                else: calc_status = "Partially Paid"

            new_entry = pd.DataFrame([{
                "Item #": len(df_expenses) + 1,
                "Date": exp_date,
                "Main Category": selected_main_cat,
                "Sub Category": selected_sub_cat,
                "Merchant/Description": merchant if merchant else selected_sub_cat,
                "Billed Amount": billed_amt,
                "Actual Paid": actual_paid_amt,
                "Currency": curr_type,
                "Pending Due": max(billed_amt - actual_paid_amt, 0.0),
                "% Paid": f"{min((actual_paid_amt/billed_amt*100.0 if billed_amt>0 else 100.0), 100.0):.1f}%",
                "% Remaining": f"{max(100.0 - (actual_paid_amt/billed_amt*100.0 if billed_amt>0 else 100.0), 0.0):.1f}%",
                "Equivalent": "",
                "Status": calc_status,
                "Payment Method": pay_method
            }])
            
            df_expenses = pd.concat([df_expenses, new_entry], ignore_index=True)
            save_data(df_expenses)
            st.success(f"Successfully recorded payment for '{merchant if merchant else selected_sub_cat}' ({curr_type} {actual_paid_amt:,.2f})!")
            st.rerun()

# TAB 3: TRANSACTION HISTORY
with tab_history:
    st.subheader(f"📜 Transaction Ledger & Payment Status ({current_user})")

    if not df_expenses.empty:
        # Pre-process & sort chronologically grouped by main category
        df_display = df_expenses.copy()
        
        # Ensure correct column types
        df_display["Billed Amount"] = pd.to_numeric(df_display["Billed Amount"], errors="coerce").fillna(0.0)
        df_display["Actual Paid"] = pd.to_numeric(df_display["Actual Paid"], errors="coerce").fillna(0.0)
        
        # Update Status & Percentages dynamically
        def update_ledger_row(row):
            b = float(row["Billed Amount"])
            p = float(row["Actual Paid"])
            if b <= 0:
                pct = 100.0 if p > 0 else 0.0
            else:
                pct = (p / b) * 100.0
            
            if pct >= 99.99 or (p >= b and b > 0):
                return "Paid", 100.0, 0.0, 0.0
            elif pct <= 0.01 or p <= 0:
                return "Not Paid", 0.0, 100.0, b
            else:
                p_pct = round(min(pct, 99.9), 1)
                r_pct = round(100.0 - p_pct, 1)
                due = max(b - p, 0.0)
                return "Partially Paid", p_pct, r_pct, due

        up_res = df_display.apply(update_ledger_row, axis=1)
        df_display["Status"] = [r[0] for r in up_res]
        df_display["% Paid"] = [f"{r[1]:.1f}%" for r in up_res]
        df_display["% Remaining"] = [f"{r[2]:.1f}%" for r in up_res]
        df_display["Pending Due"] = [r[3] for r in up_res]

        # Categorical custom ordering & chronological sorting
        cat_order_map = {
            "100% Priority & People to Pay": 1,
            f"Debts & Credits ({debts_pct}%)": 2,
            f"Needs ({needs_pct}%)": 3,
            f"Wants ({wants_pct}%)": 4,
            f"Savings & Investments ({savings_pct}%)": 5
        }
        df_display["Cat_Rank"] = df_display["Main Category"].map(lambda x: next((v for k, v in cat_order_map.items() if k in str(x)), 3))
        
        df_display["Date"] = pd.to_datetime(df_display["Date"], errors="coerce").dt.date
        df_display = df_display.sort_values(by=["Cat_Rank", "Date"], ascending=[True, True]).reset_index(drop=True)
        df_display["Item #"] = range(1, len(df_display) + 1)
        df_display.drop(columns=["Cat_Rank"], errors="ignore", inplace=True)

        # Totals
        tot_billed_bhd = float(df_display.apply(lambda r: conv_to_bhd(r, "Billed Amount"), axis=1).sum())
        tot_paid_bhd = float(df_display.apply(lambda r: conv_to_bhd(r, "Actual Paid"), axis=1).sum())
        tot_due_bhd = max(tot_billed_bhd - tot_paid_bhd, 0.0)

        # Count of Paid / Partially Paid / Not Paid
        cnt_paid = len(df_display[df_display["Status"] == "Paid"])
        cnt_partial = len(df_display[df_display["Status"] == "Partially Paid"])
        cnt_not_paid = len(df_display[df_display["Status"] == "Not Paid"])

        st.markdown(f"#### 📊 Payment Status Counts: 🟢 {cnt_paid} Paid &nbsp;|&nbsp; 🟡 {cnt_partial} Partially Paid &nbsp;|&nbsp; 🔴 {cnt_not_paid} Unpaid")

        st.caption("✏️ **Editable Ledger:** Double-click Billed Amount, Actual Paid, Category, or Description to make edits. Row colors automatically update: 🟢 Green (Paid / 100%), 🟡 Yellow (Partially Paid), 🔴 Red (0% Unpaid).")

        # Row color styler function for table view
        def highlight_status_rows(df_sub):
            def style_row(row):
                st_val = str(row["Status"])
                if st_val == "Paid":
                    return ['background-color: #D1FAE5; color: #065F46; font-weight: 600;'] * len(row)
                elif st_val == "Partially Paid":
                    return ['background-color: #FEF3C7; color: #92400E; font-weight: 600;'] * len(row)
                else:
                    return ['background-color: #FEE2E2; color: #991B1B; font-weight: 600;'] * len(row)
            return df_sub.style.apply(style_row, axis=1)

        cols_order = [
            "Item #", "Date", "Main Category", "Sub Category", "Merchant/Description",
            "Billed Amount", "Actual Paid", "Currency", "Pending Due", "% Paid", "% Remaining",
            "Equivalent", "Status", "Payment Method"
        ]
        
        # Filter existing columns
        show_cols = [c for c in cols_order if c in df_display.columns]

        # Display Editable Table Grid
        edited_grid = st.data_editor(
            df_display[show_cols],
            use_container_width=True,
            num_rows="dynamic",
            key=f"grid_editor_{current_user}"
        )

        c_sav1, c_sav2 = st.columns(2)
        with c_sav1:
            if st.button("💾 Save Ledger Updates", type="primary", use_container_width=True):
                save_data(edited_grid, DATA_FILE)
                st.success("Ledger saved and synced successfully!")
                st.rerun()
        with c_sav2:
            if st.button("🗑️ Delete All History", use_container_width=True):
                if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
                st.success("Ledger cleared!")
                st.rerun()

        st.markdown("---")
        st.subheader("🎨 Status-Highlighted Color Ledger View")
        st.dataframe(highlight_status_rows(df_display[show_cols]), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("💰 Total Outstanding & Payment Ledger Summary")
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.markdown("##### 📋 Total Billed / Planned")
            st.write(f"**BD:** BD {tot_billed_bhd:,.2f}")
            st.write(f"**PHP:** ₱{(tot_billed_bhd * bhd_to_php):,.2f}")
            st.write(f"**USD:** ${(tot_billed_bhd * bhd_to_usd):,.2f}")
            
        with col_s2:
            st.markdown("##### ✅ Total Amount Paid")
            st.write(f"**BD:** BD {tot_paid_bhd:,.2f}")
            st.write(f"**PHP:** ₱{(tot_paid_bhd * bhd_to_php):,.2f}")
            st.write(f"**USD:** ${(tot_paid_bhd * bhd_to_usd):,.2f}")

        with col_s3:
            st.markdown("##### ⏳ Total Pending / Unpaid")
            st.write(f"**BD:** BD {tot_due_bhd:,.2f}")
            st.write(f"**PHP:** ₱{(tot_due_bhd * bhd_to_php):,.2f}")
            st.write(f"**USD:** ${(tot_due_bhd * bhd_to_usd):,.2f}")

    else:
        st.info("No transaction history recorded yet. Add your first payment in the 'Record Expense' tab!")

# TAB 4: MT5 & COL INVESTMENTS
with tab_invest:
    st.subheader("📈 MT5 & COL Investments Command Center")
    
    col_inv1, col_inv2 = st.columns(2)
    
    with col_inv1:
        st.markdown("### 📍 Live MT5 Pip Value Calculator")
        symbol_pair = st.selectbox("Forex / Asset Pair", ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD (Gold)", "USDCHF", "AUDCAD", "NZDUSD"], index=0)
        lot_size = st.number_input("Trade Volume (Lots)", min_value=0.01, value=1.0, step=0.1)
        acc_currency = st.selectbox("Account Currency", ["USD", "BHD", "PHP"], index=0)

        # Pip value calculations
        if "JPY" in symbol_pair: pip_size = 0.01
        elif "XAUUSD" in symbol_pair: pip_size = 0.10
        else: pip_size = 0.0001

        base_pip_usd = lot_size * 100000 * pip_size
        if acc_currency == "BHD": pip_val_disp = base_pip_usd * bhd_rate
        elif acc_currency == "PHP": pip_val_disp = base_pip_usd * php_rate
        else: pip_val_disp = base_pip_usd

        st.success(f"**Value per Pip:** {acc_currency} {pip_val_disp:,.2f}")

    with col_inv2:
        st.markdown("### 🛡️ Live MT5 Required Margin Calculator")
        trade_lots = st.number_input("Position Size (Lots)", min_value=0.01, value=1.0, step=0.1, key="margin_lots")
        leverage_ratio = st.selectbox("Account Leverage", [100, 200, 400, 500, 1000], index=3)
        
        contract_val_usd = trade_lots * 100000
        req_margin_usd = contract_val_usd / leverage_ratio
        req_margin_bhd = req_margin_usd * bhd_rate
        req_margin_php = req_margin_usd * php_rate

        st.info(f"**Required Margin:** ${req_margin_usd:,.2f} USD | BD {req_margin_bhd:,.2f} | ₱{req_margin_php:,.2f}")

    st.markdown("---")
    st.markdown("### 💱 Live Forex Market Engine")
    
    f_c1, f_c2, f_c3, f_c4 = st.columns(4)
    f_c1.metric("1 BHD → PHP", f"₱{bhd_to_php:,.2f}")
    f_c2.metric("1 BHD → USD", f"${bhd_to_usd:,.2f}")
    
    chf_rate = rates_dict.get("CHF", 0.865)
    aud_rate = rates_dict.get("AUD", 1.51)
    cad_rate = rates_dict.get("CAD", 1.38)
    nzd_rate = rates_dict.get("NZD", 1.66)
    
    f_c3.metric("USD / CHF", f"{chf_rate:.4f}")
    f_c4.metric("AUD / CAD", f"{(cad_rate / aud_rate if aud_rate > 0 else 0.91):.4f}")

    st.markdown("---")
    st.markdown("### 📊 Investment Portfolio Ledger")
    
    # Load investments dataframe
    def load_investments():
        if os.path.exists(INVEST_FILE):
            try: return pd.read_csv(INVEST_FILE)
            except Exception: pass
        return pd.DataFrame(columns=["Date", "Asset Name", "Platform", "Units", "Buy Price ($)", "Current Price ($)", "Invested ($)", "Current Value ($)", "Profit / Loss ($)"])

    df_invest = load_investments()
    
    with st.form("add_investment_form", clear_on_submit=True):
        col_i1, col_i2, col_i3 = st.columns(3)
        with col_i1:
            inv_date = st.date_input("Date Invested", value=datetime.today())
            asset_name = st.text_input("Asset Name", placeholder="e.g. COL: SM, MT5: XAUUSD, S&P 500")
        with col_i2:
            platform_name = st.selectbox("Platform / Broker", ["COL Financial", "MT5 Trading", "Crypto Wallet", "Bank Fixed Deposit"])
            inv_units = st.number_input("Shares / Units", min_value=0.001, value=10.0, step=1.0)
        with col_i3:
            buy_p = st.number_input("Average Buy Price ($)", min_value=0.01, value=50.0, step=1.0)
            curr_p = st.number_input("Current Market Price ($)", min_value=0.01, value=55.0, step=1.0)

        if st.form_submit_button("➕ Add Investment Entry"):
            inv_tot = inv_units * buy_p
            curr_val = inv_units * curr_p
            pnl = curr_val - inv_tot
            
            new_inv = pd.DataFrame([{
                "Date": inv_date,
                "Asset Name": asset_name if asset_name else "Stock / Asset",
                "Platform": platform_name,
                "Units": inv_units,
                "Buy Price ($)": buy_p,
                "Current Price ($)": curr_p,
                "Invested ($)": inv_tot,
                "Current Value ($)": curr_val,
                "Profit / Loss ($)": pnl
            }])
            df_invest = pd.concat([df_invest, new_inv], ignore_index=True)
            df_invest.to_csv(INVEST_FILE, index=False)
            st.success("Investment asset added!")
            st.rerun()

    if not df_invest.empty:
        st.dataframe(df_invest, use_container_width=True, hide_index=True)
        tot_pnl = float(df_invest["Profit / Loss ($)"].sum()) if "Profit / Loss ($)" in df_invest.columns else 0.0
        st.metric("Total Un-realized P&L ($)", f"${tot_pnl:,.2f}", delta=f"${tot_pnl:,.2f}")

# TAB 5: REPORTS & EXPORT
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
2. EXPENSES & PAYMENT STATUS SUMMARY
--------------------------------------------------
- Mandatory 100% Payments: BD {actual_priority_bhd:,.2f}
- Debts & Credits        : BD {actual_debts_bhd:,.2f}
- Needs ({needs_pct}% Target)     : BD {actual_needs_bhd:,.2f}
- Wants ({wants_pct}% Target)     : BD {actual_wants_bhd:,.2f}
- Savings ({savings_pct}% Target) : BD {actual_savings_bhd:,.2f}
--------------------------------------------------
GRAND TOTAL EXPENSES PAID: BD {total_exp_bhd:,.2f}
NET REMAINING CASH       : BD {net_remaining_bhd:,.2f}
--------------------------------------------------
Status Counts: {cnt_paid if 'cnt_paid' in locals() else 0} Paid | {cnt_partial if 'cnt_partial' in locals() else 0} Partially Paid | {cnt_not_paid if 'cnt_not_paid' in locals() else 0} Unpaid
==================================================
"""
        st.download_button(
            label="📥 Download Executive Summary (.TXT)",
            data=report_content,
            file_name=f"financial_summary_{current_user.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# TAB 6: USER GUIDE
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
