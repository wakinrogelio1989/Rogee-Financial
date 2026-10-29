import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import os
import json
import requests
import shutil

st.set_page_config(
    page_title="Rogee Financial Command Center",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

    .notice-banner-green { background-color: #ECFDF5; border: 1px solid #A7F3D0; border-left: 5px solid #10B981; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; color: #065F46 !important; font-weight: 600; }
    .notice-banner-green * { color: #065F46 !important; }
    @media (prefers-color-scheme: dark) {
        .notice-banner-green { background-color: #064E3B !important; border-color: #047857 !important; border-left: 5px solid #10B981 !important; color: #A7F3D0 !important; }
        .notice-banner-green * { color: #A7F3D0 !important; }
    }

    .notice-banner-red { background-color: #FEF2F2; border: 1px solid #FECACA; border-left: 5px solid #EF4444; padding: 10px 14px; border-radius: 6px; margin-bottom: 12px; color: #991B1B !important; font-weight: 600; }
    .notice-banner-red * { color: #991B1B !important; }
    @media (prefers-color-scheme: dark) {
        .notice-banner-red { background-color: #450A0A !important; border-color: #7F1D1D !important; border-left: 5px solid #EF4444 !important; color: #FECACA !important; }
        .notice-banner-red * { color: #FECACA !important; }
    }

    .summary-card-blue { background-color: #EFF6FF; border: 1px solid #BFDBFE; border-left: 4px solid #3B82F6; padding: 12px 14px; border-radius: 8px; margin-bottom: 12px; color: #1E40AF !important; }
    .summary-card-blue * { color: #1E40AF !important; }
    @media (prefers-color-scheme: dark) {
        .summary-card-blue { background-color: #1E3A8A !important; border-color: #1D4ED8 !important; color: #BFDBFE !important; }
        .summary-card-blue * { color: #BFDBFE !important; }
    }

    .summary-card-green { background-color: #F0FDF4; border: 1px solid #BBF7D0; border-left: 4px solid #22C55E; padding: 12px 14px; border-radius: 8px; margin-bottom: 12px; color: #166534 !important; }
    .summary-card-green * { color: #166534 !important; }
    @media (prefers-color-scheme: dark) {
        .summary-card-green { background-color: #052E16 !important; border-color: #14532D !important; color: #BBF7D0 !important; }
        .summary-card-green * { color: #BBF7D0 !important; }
    }

    .summary-card-red { background-color: #FEF2F2; border: 1px solid #FECACA; border-left: 4px solid #EF4444; padding: 12px 14px; border-radius: 8px; margin-bottom: 12px; color: #991B1B !important; }
    .summary-card-red * { color: #991B1B !important; }
    @media (prefers-color-scheme: dark) {
        .summary-card-red { background-color: #450A0A !important; border-color: #7F1D1D !important; color: #FECACA !important; }
        .summary-card-red * { color: #FECACA !important; }
    }

    .summary-card-purple { background-color: #F3E8FF; border: 1px solid #E9D5FF; border-left: 4px solid #A855F7; padding: 12px 14px; border-radius: 8px; margin-bottom: 12px; color: #6B21A8 !important; }
    .summary-card-purple * { color: #6B21A8 !important; }
    @media (prefers-color-scheme: dark) {
        .summary-card-purple { background-color: #3B0764 !important; border-color: #581C87 !important; color: #E9D5FF !important; }
        .summary-card-purple * { color: #E9D5FF !important; }
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
        "pass_key": "rogee2026",
        "data_file": "expenses_rogee.csv",
        "config_file": "config_rogee.json"
    },
    "User 2": {
        "pass_key": "user2026",
        "data_file": "expenses_user2.csv",
        "config_file": "config_user2.json"
    },
    "User 3": {
        "pass_key": "user32026",
        "data_file": "expenses_user3.csv",
        "config_file": "config_user3.json"
    },
    "User 4": {
        "pass_key": "user42026",
        "data_file": "expenses_user4.csv",
        "config_file": "config_user4.json"
    }
}

@st.cache_data(ttl=3600)
def fetch_live_exchange_rates():
    default_rates = {
        "BHD": 1.0,
        "PHP": 145.50,
        "USD": 2.65,
        "EUR": 2.45,
        "GBP": 2.10,
        "CAD": 3.62,
        "AED": 9.73,
        "SAR": 9.94
    }
    try:
        domain = "open" + ".er-api" + ".com"
        res = requests.get(f"https://{domain}/v6/latest/BHD", timeout=4)
        if res.status_code == 200:
            data = res.json()
            if data.get("result") == "success" and "rates" in data:
                rates = data["rates"]
                return {
                    "BHD": 1.0,
                    "PHP": float(rates.get("PHP", 145.50)),
                    "USD": float(rates.get("USD", 2.65)),
                    "EUR": float(rates.get("EUR", 2.45)),
                    "GBP": float(rates.get("GBP", 2.10)),
                    "CAD": float(rates.get("CAD", 3.62)),
                    "AED": float(rates.get("AED", 9.73)),
                    "SAR": float(rates.get("SAR", 9.94))
                }, True, datetime.now(timezone.utc).strftime("%d %b %Y, %I:%M %p UTC")
    except Exception:
        pass
    return default_rates, False, "Fallback Default Rates (Offline)"

live_rates_dict, is_live_online, rate_timestamp = fetch_live_exchange_rates()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = "Rogee"

st.sidebar.title("🔐 Authentication & Profile")
user_choice = st.sidebar.selectbox("Select User Profile", list(USER_PROFILES.keys()), index=list(USER_PROFILES.keys()).index(st.session_state.current_user))

if user_choice != st.session_state.current_user:
    st.session_state.current_user = user_choice
    st.session_state.authenticated = False
    st.rerun()

prof_meta = USER_PROFILES[st.session_state.current_user]
DATA_FILE = prof_meta["data_file"]
CONFIG_FILE = prof_meta["config_file"]
expected_key = prof_meta["pass_key"]

if not st.session_state.authenticated:
    st.title("🔒 Security Access Portal")
    st.info(f"Please enter the private access key for **{st.session_state.current_user}** to unlock your financial workspace.")
    pass_input = st.text_input("Enter Secret Passkey", type="password")
    if st.button("Unlock Command Center", type="primary"):
        if pass_input == expected_key:
            st.session_state.authenticated = True
            st.success("Access Granted! Loading Command Center...")
            st.rerun()
        else:
            st.error("Incorrect Passkey. Access Denied.")
    st.stop()

if st.sidebar.button("🔒 Sign Out / Lock Portal"):
    st.session_state.authenticated = False
    st.rerun()

current_user = st.session_state.current_user

def load_data():
    default_cols = ["Item #", "Date", "Main Category", "Sub Category", "Merchant/Description", "Billed Amount", "Actual Paid", "Currency", "Pending Due", "% Paid", "% Remaining", "Equivalent", "Status", "Payment Method"]
    
    if not os.path.exists(DATA_FILE) and os.path.exists("expenses.csv"):
        try:
            shutil.copy("expenses.csv", DATA_FILE)
        except Exception:
            pass

    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            if df.empty:
                return pd.DataFrame(columns=default_cols)
            
            if "Amount" in df.columns and "Billed Amount" not in df.columns:
                df["Billed Amount"] = df["Amount"]
            if "Actual Paid" not in df.columns:
                df["Actual Paid"] = df["Billed Amount"]
            if "Currency" not in df.columns:
                df["Currency"] = "BHD"
            if "Item #" not in df.columns:
                df["Item #"] = range(1, len(df) + 1)

            df["Billed Amount"] = pd.to_numeric(df["Billed Amount"], errors="coerce").fillna(0.0)
            df["Actual Paid"] = pd.to_numeric(df["Actual Paid"], errors="coerce").fillna(0.0)
            df["Pending Due"] = (df["Billed Amount"] - df["Actual Paid"]).clip(lower=0.0)

            df["% Paid"] = (df["Actual Paid"] / df["Billed Amount"] * 100).fillna(0.0).round(1)
            df["% Remaining"] = (100.0 - df["% Paid"]).clip(lower=0.0).round(1)

            def get_status(p_paid):
                if p_paid >= 99.9:
                    return "Paid"
                elif p_paid <= 0.1:
                    return "Not Paid"
                else:
                    return "Partially Paid"

            df["Status"] = df["% Paid"].apply(get_status)

            def calc_equivalent(row):
                curr = str(row.get("Currency", "BHD")).upper()
                b_amt = float(row.get("Billed Amount", 0.0))
                p_rate = live_rates_dict.get("PHP", 145.50)
                u_rate = live_rates_dict.get("USD", 2.65)
                
                if curr == "PHP":
                    bhd_val = b_amt / p_rate if p_rate > 0 else 0.0
                    usd_val = bhd_val * u_rate
                    return f"BD {bhd_val:,.2f} | ${usd_val:,.2f}"
                elif curr == "USD":
                    bhd_val = b_amt / u_rate if u_rate > 0 else 0.0
                    php_val = bhd_val * p_rate
                    return f"BD {bhd_val:,.2f} | ₱{php_val:,.2f}"
                else:
                    php_val = b_amt * p_rate
                    usd_val = b_amt * u_rate
                    return f"₱{php_val:,.2f} | ${usd_val:,.2f}"

            df["Equivalent"] = df.apply(calc_equivalent, axis=1)
            df['Date'] = pd.to_datetime(df['Date']).dt.date

            for col in default_cols:
                if col not in df.columns:
                    df[col] = ""
            
            return df[default_cols]
        except Exception:
            pass

    return pd.DataFrame(columns=default_cols)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df_expenses = load_data()

def load_config():
    defaults = {
        "salary_bhd": 1800.0,
        "business_bhd": 0.0,
        "sidelines_bhd": 0.0,
        "other_income_bhd": 0.0,
        "needs_pct": 50,
        "wants_pct": 30,
        "savings_pct": 20
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                saved = json.load(f)
                defaults.update(saved)
        except Exception:
            pass
    return defaults

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=4)
    except Exception:
        pass

user_cfg = load_config()

st.sidebar.markdown("---")
st.sidebar.title("⚙️ Income & Allocation Targets")

salary_bhd = st.sidebar.number_input("Primary Monthly Salary (BD)", min_value=0.0, value=float(user_cfg["salary_bhd"]), step=50.0)
business_bhd = st.sidebar.number_input("Business Income (BD)", min_value=0.0, value=float(user_cfg["business_bhd"]), step=50.0)
sidelines_bhd = st.sidebar.number_input("Sidelines / Freelance (BD)", min_value=0.0, value=float(user_cfg["sidelines_bhd"]), step=50.0)
other_income_bhd = st.sidebar.number_input("Other Income / Bonuses (BD)", min_value=0.0, value=float(user_cfg["other_income_bhd"]), step=50.0)

total_income_bhd = salary_bhd + business_bhd + sidelines_bhd + other_income_bhd
bhd_to_php = live_rates_dict.get("PHP", 145.50)
bhd_to_usd = live_rates_dict.get("USD", 2.65)

total_income_php = total_income_bhd * bhd_to_php
total_income_usd = total_income_bhd * bhd_to_usd

st.sidebar.markdown(f"""
<div class="summary-card-green">
    <div style="font-size: 0.82rem; font-weight: 700; text-transform: uppercase;">💵 TOTAL COMBINED MONTHLY INCOME</div>
    <div style="font-size: 1.35rem; font-weight: 800; margin-top: 2px;">BD {total_income_bhd:,.2f}</div>
    <div style="font-size: 0.8rem; opacity: 0.9;">Equivalent: ₱{total_income_php:,.2f} | ${total_income_usd:,.2f}</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

needs_pct = st.sidebar.slider("Needs Target % (Essentials)", 0, 100, int(user_cfg["needs_pct"]))
wants_pct = st.sidebar.slider("Wants Target % (Lifestyle)", 0, 100, int(user_cfg["wants_pct"]))
savings_pct = st.sidebar.slider("Savings & Debt Target %", 0, 100, int(user_cfg["savings_pct"]))

total_target_pct = needs_pct + wants_pct + savings_pct
if total_target_pct != 100:
    st.sidebar.warning(f"Allocation total is {total_target_pct}%. It should equal 100%.")

framework_title = f"{needs_pct}/{wants_pct}/{savings_pct}"
st.sidebar.markdown(f"**Dynamic Allocation Ratio:** `{framework_title} Framework`")

new_cfg = {
    "salary_bhd": salary_bhd,
    "business_bhd": business_bhd,
    "sidelines_bhd": sidelines_bhd,
    "other_income_bhd": other_income_bhd,
    "needs_pct": needs_pct,
    "wants_pct": wants_pct,
    "savings_pct": savings_pct
}
if new_cfg != user_cfg:
    save_config(new_cfg)

needs_target_bhd = total_income_bhd * (needs_pct / 100.0)
wants_target_bhd = total_income_bhd * (wants_pct / 100.0)
savings_target_bhd = total_income_bhd * (savings_pct / 100.0)

bh_time = datetime.now(timezone(timedelta(hours=3)))
ph_time = datetime.now(timezone(timedelta(hours=8)))

st.markdown('<div class="main-header">Rogee Financial Command Center</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Personal Finance & Budgeting Tracker based on the {framework_title} Framework</div>', unsafe_allow_html=True)

live_status_str = "🟢 Live Rates Online" if is_live_online else "🟡 Fallback Rates"
st.markdown(f"""<div class="time-badge">
    📍 <b>Bahrain:</b> {bh_time.strftime("%d %b %Y, %I:%M %p")} AST &nbsp;|&nbsp; 
    🇵🇭 <b>Philippines:</b> {ph_time.strftime("%d %b %Y, %I:%M %p")} PHT &nbsp;|&nbsp; 
    👤 <b>Account:</b> {current_user} &nbsp;|&nbsp; 
    💱 <b>Rates ({live_status_str}):</b> 1 BD = ₱{bhd_to_php:.2f} PHP = ${bhd_to_usd:.2f} USD
</div>""", unsafe_allow_html=True)

tab_dash, tab_add, tab_history, tab_proj, tab_mt5, tab_converter, tab_guide = st.tabs([
    "📊 Dashboard & Analytics",
    "➕ Record Expense / Payment",
    "📋 Transaction History & Ledger",
    "🔮 12-Month Projections",
    "📈 MT5 Pip Calculator",
    "💱 Live Currency Converter",
    "📘 Security & Guide"
])

def calc_bhd_value(row):
    curr = str(row.get("Currency", "BHD")).upper()
    paid = float(row.get("Actual Paid", 0.0))
    p_rate = live_rates_dict.get("PHP", 145.50)
    u_rate = live_rates_dict.get("USD", 2.65)
    if curr == "PHP":
        return paid / p_rate if p_rate > 0 else 0.0
    elif curr == "USD":
        return paid / u_rate if u_rate > 0 else 0.0
    return paid

def calc_bhd_billed(row):
    curr = str(row.get("Currency", "BHD")).upper()
    billed = float(row.get("Billed Amount", 0.0))
    p_rate = live_rates_dict.get("PHP", 145.50)
    u_rate = live_rates_dict.get("USD", 2.65)
    if curr == "PHP":
        return billed / p_rate if p_rate > 0 else 0.0
    elif curr == "USD":
        return billed / u_rate if u_rate > 0 else 0.0
    return billed

if not df_expenses.empty:
    df_expenses["BHD_Paid_Calc"] = df_expenses.apply(calc_bhd_value, axis=1)
    df_expenses["BHD_Billed_Calc"] = df_expenses.apply(calc_bhd_billed, axis=1)
else:
    df_expenses["BHD_Paid_Calc"] = 0.0
    df_expenses["BHD_Billed_Calc"] = 0.0

actual_priority_bhd = df_expenses[df_expenses["Main Category"].str.contains("100% Priority", na=False)]["BHD_Paid_Calc"].sum() if not df_expenses.empty else 0.0
actual_debts_bhd = df_expenses[df_expenses["Main Category"].str.contains("Debts & Credits", na=False)]["BHD_Paid_Calc"].sum() if not df_expenses.empty else 0.0
actual_needs_bhd = df_expenses[df_expenses["Main Category"].str.contains("Needs", na=False)]["BHD_Paid_Calc"].sum() if not df_expenses.empty else 0.0
actual_wants_bhd = df_expenses[df_expenses["Main Category"].str.contains("Wants", na=False)]["BHD_Paid_Calc"].sum() if not df_expenses.empty else 0.0
actual_savings_bhd = df_expenses[df_expenses["Main Category"].str.contains("Savings", na=False)]["BHD_Paid_Calc"].sum() if not df_expenses.empty else 0.0

total_actual_exp_bhd = actual_priority_bhd + actual_debts_bhd + actual_needs_bhd + actual_wants_bhd + actual_savings_bhd
total_billed_exp_bhd = df_expenses["BHD_Billed_Calc"].sum() if not df_expenses.empty else 0.0
total_pending_due_bhd = (total_billed_exp_bhd - total_actual_exp_bhd) if total_billed_exp_bhd > total_actual_exp_bhd else 0.0

remaining_cash_bhd = total_income_bhd - total_actual_exp_bhd
remaining_cash_php = remaining_cash_bhd * bhd_to_php
remaining_cash_usd = remaining_cash_bhd * bhd_to_usd

is_over_budget = remaining_cash_bhd < 0
over_budget_bhd = abs(remaining_cash_bhd) if is_over_budget else 0.0

# TAB 1: DASHBOARD
with tab_dash:
    if is_over_budget:
        st.markdown(f"""<div class="notice-banner-red">
            ⚠️ <b>OVER BUDGET ALERT:</b> Total payments exceed your monthly income limit! <br>
            <b>Current Overage Deficit:</b> -BD {over_budget_bhd:,.2f} &nbsp;|&nbsp; -₱{(over_budget_bhd * bhd_to_php):,.2f} PHP &nbsp;|&nbsp; -${(over_budget_bhd * bhd_to_usd):,.2f} USD
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="notice-banner-green">
            🟢 <b>MONTHLY CASH SURPLUS:</b> You are within your budget targets! <br>
            <b>Available Remaining Net Cash:</b> BD {remaining_cash_bhd:,.2f} &nbsp;|&nbsp; ₱{remaining_cash_php:,.2f} PHP &nbsp;|&nbsp; ${remaining_cash_usd:,.2f} USD
        </div>""", unsafe_allow_html=True)

    c_m1, c_m2, c_m3, c_m4, c_m5 = st.columns(5)
    c_m1.metric("Monthly Net Income", f"BD {total_income_bhd:,.2f}")
    c_m2.metric("Total Expenses Paid", f"BD {total_actual_exp_bhd:,.2f}")
    
    if is_over_budget:
        c_m3.metric("Over Budget Deficit", f"-BD {over_budget_bhd:,.2f}", delta=f"-BD {over_budget_bhd:,.2f}", delta_color="inverse")
    else:
        c_m3.metric("Remaining Net Cash", f"BD {remaining_cash_bhd:,.2f}", delta=f"BD {remaining_cash_bhd:,.2f}")
        
    c_m4.metric("Pending Due Balance", f"BD {total_pending_due_bhd:,.2f}")
    c_m5.metric("Total Billed Expenses", f"BD {total_billed_exp_bhd:,.2f}")

    st.markdown("---")
    st.subheader(f"📊 {framework_title} Benchmark Allocation Breakdown")

    cat_data = [
        {"Category": f"Needs ({needs_pct}%)", "Target Allocation": f"{needs_pct}%", "Target (BD)": needs_target_bhd, "Actual Paid (BD)": actual_needs_bhd, "Difference (BD)": needs_target_bhd - actual_needs_bhd, "Status": "On Track" if actual_needs_bhd <= needs_target_bhd else "Over Target"},
        {"Category": f"Wants ({wants_pct}%)", "Target Allocation": f"{wants_pct}%", "Target (BD)": wants_target_bhd, "Actual Paid (BD)": actual_wants_bhd, "Difference (BD)": wants_target_bhd - actual_wants_bhd, "Status": "On Track" if actual_wants_bhd <= wants_target_bhd else "Over Target"},
        {"Category": f"Savings & Debt ({savings_pct}%)", "Target Allocation": f"{savings_pct}%", "Target (BD)": savings_target_bhd, "Actual Paid (BD)": actual_savings_bhd, "Difference (BD)": actual_savings_bhd - savings_target_bhd, "Status": "Target Met" if actual_savings_bhd >= savings_target_bhd else "Under Goal"},
        {"Category": "100% Mandatory Priority", "Target Allocation": "Fixed", "Target (BD)": actual_priority_bhd, "Actual Paid (BD)": actual_priority_bhd, "Difference (BD)": 0.0, "Status": "Mandatory"},
        {"Category": "Debts & Credits", "Target Allocation": "Fixed", "Target (BD)": actual_debts_bhd, "Actual Paid (BD)": actual_debts_bhd, "Difference (BD)": 0.0, "Status": "Mandatory"}
    ]
    df_cat_summary = pd.DataFrame(cat_data)
    
    st.dataframe(
        df_cat_summary.style.format({
            "Target (BD)": "BD {:,.2f}",
            "Actual Paid (BD)": "BD {:,.2f}",
            "Difference (BD)": "BD {:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    ch1, ch2 = st.columns(2)

    with ch1:
        st.subheader("🎯 Target vs. Actual Spending (BD)")
        chart_df = pd.DataFrame({
            "Category": [f"Needs ({needs_pct}%)", f"Wants ({wants_pct}%)", f"Savings ({savings_pct}%)"],
            "Target": [needs_target_bhd, wants_target_bhd, savings_target_bhd],
            "Actual": [actual_needs_bhd, actual_wants_bhd, actual_savings_bhd]
        })
        fig_bar = go.Figure(data=[
            go.Bar(name='Target (BD)', x=chart_df['Category'], y=chart_df['Target'], marker_color='#93C5FD'),
            go.Bar(name='Actual Paid (BD)', x=chart_df['Category'], y=chart_df['Actual'], marker_color='#1D4ED8')
        ])
        fig_bar.update_layout(
            barmode='group',
            yaxis_title="Amount in BHD (BD)",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with ch2:
        st.subheader("🥧 Actual Expense Share Distribution")
        if total_actual_exp_bhd > 0:
            fig_pie = px.pie(
                values=[actual_needs_bhd, actual_wants_bhd, actual_savings_bhd, actual_priority_bhd, actual_debts_bhd],
                names=[f"Needs ({needs_pct}%)", f"Wants ({wants_pct}%)", f"Savings ({savings_pct}%)", "100% Priority", "Debts"],
                color_discrete_sequence=['#2563EB', '#F59E0B', '#10B981', '#EF4444', '#8B5CF6'],
                hole=0.45
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expense records logged yet. Add your first payment in the 'Record Expense / Payment' tab!")

# TAB 2: RECORD EXPENSE / PAYMENT
with tab_add:
    st.subheader("➕ Record a New Expense or Payment")

    col_cat1, col_cat2 = st.columns(2)
    with col_cat1:
        exp_date = st.date_input("Transaction Date", value=datetime.today())
        main_cat = st.selectbox("Category Allocation", [
            f"Needs ({needs_pct}%)",
            f"Wants ({wants_pct}%)",
            f"Savings & Debt ({savings_pct}%)",
            "100% Mandatory Priority Payments",
            "Debts & Credits"
        ])
    
    with col_cat2:
        if "Needs" in main_cat:
            sub_cats = ["Housing / Rent / Mortgage", "Utilities & Bills", "Groceries", "Transportation / Fuel", "Healthcare / Insurance", "Childcare / Education"]
        elif "Wants" in main_cat:
            sub_cats = ["Dining Out & Coffee", "Entertainment & Streaming", "Shopping & Apparel", "Hobbies & Travel", "Subscriptions", "Miscellaneous"]
        elif "Savings" in main_cat:
            sub_cats = ["Emergency Fund", "Retirement / Stocks", "Extra Debt Payoff", "Major Goal Savings"]
        elif "100%" in main_cat:
            sub_cats = ["Family Remittance", "House Rent", "Electricity & Water", "Sponsorship / Visa Fees", "School Tuition"]
        else:
            sub_cats = ["Credit Card Bill", "Personal Loan", "Car Financing", "Friend / Relative Debt Payoff"]

        sub_cat = st.selectbox("Sub-Category", sub_cats)

    st.markdown("---")

    with st.form("add_expense_form", clear_on_submit=True):
        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            merchant = st.text_input("Merchant / Description", placeholder="e.g. Rent, Electricity, Grocery")
            payment_method = st.selectbox("Payment Method", ["BenefitPay / Bank Transfer", "Credit Card", "Debit Card", "Cash", "Remittance"])

        with col_f2:
            tx_currency = st.selectbox("Transaction Currency", ["BHD", "PHP", "USD"], index=0)
            billed_amount = st.number_input(f"Planned / Billed Amount ({tx_currency})", min_value=0.01, step=10.0, value=100.0)

        with col_f3:
            actual_paid = st.number_input(f"Actual Amount Paid ({tx_currency})", min_value=0.0, step=10.0, value=100.0)

        submit_btn = st.form_submit_button("💾 Save Payment Record", type="primary", use_container_width=True)

        if submit_btn:
            new_item_num = len(df_expenses) + 1
            pending_due = max(0.0, billed_amount - actual_paid)
            
            p_paid = round((actual_paid / billed_amount * 100), 1) if billed_amount > 0 else 0.0
            p_rem = max(0.0, round(100.0 - p_paid, 1))

            if p_paid >= 99.9:
                status = "Paid"
            elif p_paid <= 0.1:
                status = "Not Paid"
            else:
                status = "Partially Paid"

            if tx_currency == "PHP":
                bhd_v = billed_amount / bhd_to_php
                usd_v = bhd_v * bhd_to_usd
                eq_str = f"BD {bhd_v:,.2f} | ${usd_v:,.2f}"
            elif tx_currency == "USD":
                bhd_v = billed_amount / bhd_to_usd
                php_v = bhd_v * bhd_to_php
                eq_str = f"BD {bhd_v:,.2f} | ₱{php_val:,.2f}"
            else:
                php_v = billed_amount * bhd_to_php
                usd_v = billed_amount * bhd_to_usd
                eq_str = f"₱{php_v:,.2f} | ${usd_v:,.2f}"

            new_row = pd.DataFrame([{
                "Item #": new_item_num,
                "Date": exp_date,
                "Main Category": main_cat,
                "Sub Category": sub_cat,
                "Merchant/Description": merchant if merchant else "Unspecified",
                "Billed Amount": billed_amount,
                "Actual Paid": actual_paid,
                "Currency": tx_currency,
                "Pending Due": pending_due,
                "% Paid": p_paid,
                "% Remaining": p_rem,
                "Equivalent": eq_str,
                "Status": status,
                "Payment Method": payment_method
            }])

            df_expenses_clean = df_expenses.drop(columns=["BHD_Paid_Calc", "BHD_Billed_Calc"], errors="ignore")
            df_updated = pd.concat([df_expenses_clean, new_row], ignore_index=True)
            save_data(df_updated)
            st.success(f"Successfully recorded payment for '{merchant if merchant else sub_cat}' ({tx_currency} {actual_paid:,.2f})!")
            st.rerun()

# TAB 3: TRANSACTION HISTORY & LEDGER
with tab_history:
    st.subheader("📋 Recorded Transaction Ledger & Payment Status")

    if is_over_budget:
        st.markdown(f"""<div class="notice-banner-red">
            🚨 <b>OVER BUDGET STATUS NOTICE:</b> Total payments exceed your monthly income limit! <br>
            <b>Current Overage / Limit Deficit:</b> -BD {over_budget_bhd:,.2f} &nbsp;|&nbsp; -₱{(over_budget_bhd * bhd_to_php):,.2f} PHP &nbsp;|&nbsp; -${(over_budget_bhd * bhd_to_usd):,.2f} USD
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="notice-banner-green">
            🟢 <b>WITHIN BUDGET STATUS:</b> You have available remaining income! <br>
            <b>Net Unspent Cash Balance:</b> BD {remaining_cash_bhd:,.2f} &nbsp;|&nbsp; ₱{remaining_cash_php:,.2f} PHP &nbsp;|&nbsp; ${remaining_cash_usd:,.2f} USD
        </div>""", unsafe_allow_html=True)

    if not df_expenses.empty:
        df_display = df_expenses.copy().drop(columns=["BHD_Paid_Calc", "BHD_Billed_Calc"], errors="ignore")

        def cat_rank(cat):
            cat = str(cat)
            if "100%" in cat: return 1
            if "Debts" in cat: return 2
            if "Needs" in cat: return 3
            if "Wants" in cat: return 4
            return 5

        df_display["_rank"] = df_display["Main Category"].apply(cat_rank)
        df_display = df_display.sort_values(by=["_rank", "Date"], ascending=[True, True]).drop(columns=["_rank"])
        df_display["Item #"] = range(1, len(df_display) + 1)

        st.markdown("#### ✏️ Interactive Editable Transaction Ledger")
        st.caption("You can edit any row below directly in the grid (e.g. adjust Billed Amount, Actual Paid, or Currency), then click **Save Ledger Changes**.")

        edited_df = st.data_editor(
            df_display,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config={
                "Item #": st.column_config.NumberColumn("Item #", disabled=True),
                "Billed Amount": st.column_config.NumberColumn("Billed Amount", format="%.2f"),
                "Actual Paid": st.column_config.NumberColumn("Actual Paid", format="%.2f"),
                "Currency": st.column_config.SelectboxColumn("Currency", options=["BHD", "PHP", "USD"]),
                "Status": st.column_config.SelectboxColumn("Status", options=["Paid", "Partially Paid", "Not Paid"]),
                "% Paid": st.column_config.NumberColumn("% Paid", format="%.1f%%"),
                "% Remaining": st.column_config.NumberColumn("% Remaining", format="%.1f%%")
            }
        )

        col_sav1, col_sav2 = st.columns([2, 1])
        with col_sav1:
            if st.button("💾 Save Ledger Changes", type="primary", use_container_width=True):
                save_data(edited_df)
                st.success("Transaction ledger updated successfully!")
                st.rerun()

        st.markdown("---")
        st.markdown("#### 🎨 Color-Coded Status Ledger View")
        st.caption("🟢 **Green**: 100% Paid | 🟡 **Yellow**: Partially Paid | 🔴 **Red**: Unpaid (0% Paid)")

        def style_rows(row):
            status = str(row.get("Status", ""))
            p_paid = float(row.get("% Paid", 0.0))
            if status == "Paid" or p_paid >= 99.9:
                return ['background-color: #D1FAE5; color: #065F46; font-weight: 500;'] * len(row)
            elif status == "Partially Paid" or (0.1 < p_paid < 99.9):
                return ['background-color: #FEF3C7; color: #92400E; font-weight: 500;'] * len(row)
            else:
                return ['background-color: #FEE2E2; color: #991B1B; font-weight: 500;'] * len(row)

        st.dataframe(
            df_display.style.apply(style_rows, axis=1),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        st.markdown("### 💰 Total Outstanding & Payment Ledger Summary")

        bhd_rows = df_display[df_display["Currency"] == "BHD"]
        php_rows = df_display[df_display["Currency"] == "PHP"]
        usd_rows = df_display[df_display["Currency"] == "USD"]

        bhd_billed = bhd_rows["Billed Amount"].sum() if not bhd_rows.empty else 0.0
        bhd_paid = bhd_rows["Actual Paid"].sum() if not bhd_rows.empty else 0.0
        bhd_pending = bhd_rows["Pending Due"].sum() if not bhd_rows.empty else 0.0

        php_billed = php_rows["Billed Amount"].sum() if not php_rows.empty else 0.0
        php_paid = php_rows["Actual Paid"].sum() if not php_rows.empty else 0.0
        php_pending = php_rows["Pending Due"].sum() if not php_rows.empty else 0.0

        php_billed_in_bhd = php_billed / bhd_to_php if bhd_to_php > 0 else 0.0
        php_paid_in_bhd = php_paid / bhd_to_php if bhd_to_php > 0 else 0.0
        php_pending_in_bhd = php_pending / bhd_to_php if bhd_to_php > 0 else 0.0

        usd_billed = usd_rows["Billed Amount"].sum() if not usd_rows.empty else 0.0
        usd_paid = usd_rows["Actual Paid"].sum() if not usd_rows.empty else 0.0
        usd_pending = usd_rows["Pending Due"].sum() if not usd_rows.empty else 0.0

        usd_billed_in_bhd = usd_billed / bhd_to_usd if bhd_to_usd > 0 else 0.0
        usd_paid_in_bhd = usd_paid / bhd_to_usd if bhd_to_usd > 0 else 0.0
        usd_pending_in_bhd = usd_pending / bhd_to_usd if bhd_to_usd > 0 else 0.0

        grand_total_billed_bhd = bhd_billed + php_billed_in_bhd + usd_billed_in_bhd
        grand_total_paid_bhd = bhd_paid + php_paid_in_bhd + usd_paid_in_bhd
        grand_total_pending_bhd = bhd_pending + php_pending_in_bhd + usd_pending_in_bhd

        col_s1, col_s2, col_s3, col_s4 = st.columns(4)

        with col_s1:
            st.markdown(f"""
            <div class="summary-card-blue">
                <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase;">🇧🇭 BHD CURRENCY BILLS</div>
                <hr style="margin: 6px 0;">
                <div><b>Total BHD Billed:</b> BD {bhd_billed:,.2f}</div>
                <div><b>Total BHD Paid:</b> BD {bhd_paid:,.2f}</div>
                <div><b>Total BHD Pending:</b> BD {bhd_pending:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_s2:
            st.markdown(f"""
            <div class="summary-card-purple">
                <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase;">🇵🇭 PHP CURRENCY BILLS</div>
                <hr style="margin: 6px 0;">
                <div><b>Total PHP Billed:</b> ₱{php_billed:,.2f} <br><small>(Eq: BD {php_billed_in_bhd:,.2f})</small></div>
                <div><b>Total PHP Paid:</b> ₱{php_paid:,.2f} <br><small>(Eq: BD {php_paid_in_bhd:,.2f})</small></div>
                <div><b>Total PHP Pending:</b> ₱{php_pending:,.2f} <br><small>(Eq: BD {php_pending_in_bhd:,.2f})</small></div>
            </div>
            """, unsafe_allow_html=True)

        with col_s3:
            st.markdown(f"""
            <div class="summary-card-green">
                <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase;">💵 USD CURRENCY BILLS</div>
                <hr style="margin: 6px 0;">
                <div><b>Total USD Billed:</b> ${usd_billed:,.2f} <br><small>(Eq: BD {usd_billed_in_bhd:,.2f})</small></div>
                <div><b>Total USD Paid:</b> ${usd_paid:,.2f} <br><small>(Eq: BD {usd_paid_in_bhd:,.2f})</small></div>
                <div><b>Total USD Pending:</b> ${usd_pending:,.2f} <br><small>(Eq: BD {usd_pending_in_bhd:,.2f})</small></div>
            </div>
            """, unsafe_allow_html=True)

        with col_s4:
            st.markdown(f"""
            <div class="summary-card-red">
                <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase;">🌍 COMBINED GRAND TOTAL (IN BD)</div>
                <hr style="margin: 6px 0;">
                <div><b>Grand Total Billed:</b> BD {grand_total_billed_bhd:,.2f}</div>
                <div><b>Grand Total Paid:</b> BD {grand_total_paid_bhd:,.2f}</div>
                <div><b>Grand Total Pending:</b> BD {grand_total_pending_bhd:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🗑️ Clear All Transaction Records", type="primary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.success("All transaction records cleared!")
            st.rerun()
    else:
        st.info("No transaction records found. Start adding payments in the 'Record Expense / Payment' tab!")

# TAB 4: 12-MONTH PROJECTIONS
with tab_proj:
    st.subheader("🔮 12-Month / 1-Year Projected Financial Planning Engine")
    st.caption("Forecast your future detailed expenses, income growth, inflation impacts, and long-term wealth accumulation over the next 12 months.")

    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        base_proj_income_bhd = st.number_input("Base Projected Monthly Income (BD)", min_value=100.0, value=float(total_income_bhd), step=50.0)
        proj_income_growth_pct = st.slider("Expected Annual Income Growth (%)", 0.0, 30.0, 5.0, 0.5)
    
    with col_p2:
        proj_fixed_needs_bhd = st.number_input("Monthly Fixed Commitments (BD)", min_value=0.0, value=float(actual_needs_bhd + actual_priority_bhd + actual_debts_bhd), step=20.0)
        proj_inflation_pct = st.slider("Estimated Annual Inflation (%)", 0.0, 15.0, 3.0, 0.5)

    with col_p3:
        proj_wants_bhd = st.number_input("Monthly Lifestyle Allowance (BD)", min_value=0.0, value=float(actual_wants_bhd), step=20.0)
        proj_savings_goal_bhd = st.number_input("Target Monthly Savings Contribution (BD)", min_value=0.0, value=float(savings_target_bhd), step=20.0)

    proj_rows = []
    cum_savings = 0.0

    for m in range(1, 13):
        m_inc = base_proj_income_bhd * ((1 + (proj_income_growth_pct / 100.0) / 12) ** (m - 1))
        m_needs = proj_fixed_needs_bhd * ((1 + (proj_inflation_pct / 100.0) / 12) ** (m - 1))
        m_wants = proj_wants_bhd * ((1 + (proj_inflation_pct / 100.0) / 12) ** (m - 1))
        m_total_exp = m_needs + m_wants + proj_savings_goal_bhd
        m_surplus = m_inc - m_total_exp
        cum_savings += (proj_savings_goal_bhd + max(0.0, m_surplus))

        proj_rows.append({
            "Month": f"Month {m}",
            "Projected Income (BD)": round(m_inc, 2),
            "Fixed Commitments (BD)": round(m_needs, 2),
            "Lifestyle Expenses (BD)": round(m_wants, 2),
            "Savings Contribution (BD)": round(proj_savings_goal_bhd, 2),
            "Total Projected Expenses (BD)": round(m_total_exp, 2),
            "Net Surplus (BD)": round(m_surplus, 2),
            "Cumulative Savings Build-up (BD)": round(cum_savings, 2)
        })

    df_proj = pd.DataFrame(proj_rows)

    tot_1yr_inc = df_proj["Projected Income (BD)"].sum()
    tot_1yr_exp = df_proj["Total Projected Expenses (BD)"].sum()
    tot_1yr_sav = df_proj["Cumulative Savings Build-up (BD)"].iloc[-1]

    st.markdown("---")
    pm1, pm2, pm3 = st.columns(3)
    pm1.metric("1-Year Projected Income", f"BD {tot_1yr_inc:,.2f}", f"₱{(tot_1yr_inc * bhd_to_php):,.2f} PHP")
    pm2.metric("1-Year Projected Expenses", f"BD {tot_1yr_exp:,.2f}", f"₱{(tot_1yr_exp * bhd_to_php):,.2f} PHP")
    pm3.metric("1-Year Net Wealth Build-up", f"BD {tot_1yr_sav:,.2f}", f"₱{(tot_1yr_sav * bhd_to_php):,.2f} PHP")

    st.markdown("---")
    st.markdown("#### 📅 12-Month Forecast Matrix")
    st.dataframe(
        df_proj.style.format({
            "Projected Income (BD)": "BD {:,.2f}",
            "Fixed Commitments (BD)": "BD {:,.2f}",
            "Lifestyle Expenses (BD)": "BD {:,.2f}",
            "Savings Contribution (BD)": "BD {:,.2f}",
            "Total Projected Expenses (BD)": "BD {:,.2f}",
            "Net Surplus (BD)": "BD {:,.2f}",
            "Cumulative Savings Build-up (BD)": "BD {:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    cp1, cp2 = st.columns(2)
    with cp1:
        st.subheader("📈 Projected Monthly Income vs. Expenses")
        fig_proj_bar = go.Figure(data=[
            go.Bar(name='Projected Income', x=df_proj['Month'], y=df_proj['Projected Income (BD)'], marker_color='#22C55E'),
            go.Bar(name='Total Expenses', x=df_proj['Month'], y=df_proj['Total Projected Expenses (BD)'], marker_color='#EF4444')
        ])
        fig_proj_bar.update_layout(barmode='group', yaxis_title="Amount in BHD (BD)", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_proj_bar, use_container_width=True)

    with cp2:
        st.subheader("💰 Cumulative 1-Year Savings Growth Trend")
        fig_line = px.line(df_proj, x="Month", y="Cumulative Savings Build-up (BD)", markers=True, title="Cumulative Wealth Growth (BD)")
        fig_line.update_traces(line_color="#10B981", line_width=3)
        fig_line.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_line, use_container_width=True)

# TAB 5: MT5 PIP CALCULATOR
with tab_mt5:
    st.subheader("📈 MetaTrader 5 (MT5) Pip & Position Size Calculator")
    st.caption("Precision trading risk calculator for Forex, Gold, and Cross Pairs.")

    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        pair_select = st.selectbox("Currency Pair / Asset", [
            "USDPHP", "BHDPHP", "USDCAD", "EURUSD", "GBPUSD", "USDJPY",
            "XAUUSD (Gold)", "USDCHF", "AUDUSD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"
        ])
        lot_size = st.number_input("Trading Lot Size (Standard Lots)", min_value=0.01, max_value=100.0, value=1.0, step=0.1)

    with col_t2:
        entry_price = st.number_input("Entry Price", min_value=0.00001, value=58.50 if "PHP" in pair_select else (2750.00 if "XAU" in pair_select else 1.0850), format="%.5f")
        exit_price = st.number_input("Exit / Target Price", min_value=0.00001, value=59.10 if "PHP" in pair_select else (2765.00 if "XAU" in pair_select else 1.0920), format="%.5f")

    with col_t3:
        leverage = st.selectbox("Account Leverage", ["1:100", "1:200", "1:500", "1:1000"], index=2)
        account_balance_usd = st.number_input("Trading Account Balance ($ USD)", min_value=10.0, value=1000.0, step=100.0)

    is_jpy = "JPY" in pair_select
    is_gold = "XAU" in pair_select
    
    if is_gold:
        pip_size = 0.10
        contract_size = 100
    elif is_jpy:
        pip_size = 0.01
        contract_size = 100000
    else:
        pip_size = 0.0001
        contract_size = 100000

    price_diff = abs(exit_price - entry_price)
    pips_gained = price_diff / pip_size

    if is_gold:
        pip_value_usd = lot_size * 10.0
    elif "USD" in pair_select and pair_select.endswith("USD"):
        pip_value_usd = lot_size * 10.0
    elif pair_select == "USDPHP":
        pip_value_usd = (lot_size * contract_size * pip_size) / entry_price if entry_price > 0 else 0.0
    else:
        pip_value_usd = lot_size * 10.0

    profit_usd = pips_gained * pip_value_usd if exit_price >= entry_price else - (pips_gained * pip_value_usd)
    lev_mult = int(leverage.split(":")[1])
    margin_req_usd = (lot_size * contract_size * entry_price) / lev_mult if not is_gold else (lot_size * 100 * entry_price) / lev_mult

    st.markdown("---")
    tc1, tc2, tc3, tc4 = st.columns(4)
    tc1.metric("Calculated Pips", f"{pips_gained:,.1f} Pips")
    tc2.metric("Pip Value ($ USD)", f"${pip_value_usd:,.2f} per Pip")
    tc3.metric("Estimated Position P&L", f"${profit_usd:,.2f}", delta=f"${profit_usd:,.2f}")
    tc4.metric("Required Margin ($ USD)", f"${margin_req_usd:,.2f}")

# TAB 6: LIVE CURRENCY CONVERTER
with tab_converter:
    st.subheader("💱 Live On-the-Spot Currency Converter")
    st.caption("Convert any amount instantly using live market exchange rates.")

    st.markdown(f"""
    <div class="summary-card-blue">
        <b>Live Exchange Rates Status:</b> {live_status_str} &nbsp;|&nbsp; <b>Timestamp:</b> {rate_timestamp} <br>
        <b>Rates against 1 BHD:</b> ₱{bhd_to_php:.2f} PHP &nbsp;|&nbsp; ${bhd_to_usd:.2f} USD &nbsp;|&nbsp; €{live_rates_dict.get('EUR', 2.45):.2f} EUR &nbsp;|&nbsp; £{live_rates_dict.get('GBP', 2.10):.2f} GBP
    </div>
    """, unsafe_allow_html=True)

    col_conv1, col_conv2, col_conv3 = st.columns(3)
    with col_conv1:
        conv_amount = st.number_input("Amount to Convert", min_value=0.01, value=100.0, step=10.0)
    
    with col_conv2:
        from_curr = st.selectbox("From Currency", ["BHD", "PHP", "USD", "EUR", "GBP", "CAD", "AED", "SAR"], index=0)

    with col_conv3:
        to_curr = st.selectbox("To Currency", ["PHP", "BHD", "USD", "EUR", "GBP", "CAD", "AED", "SAR"], index=0)

    from_rate = live_rates_dict.get(from_curr, 1.0)
    to_rate = live_rates_dict.get(to_curr, 1.0)

    bhd_equiv = conv_amount / from_rate if from_rate > 0 else 0.0
    converted_result = bhd_equiv * to_rate

    st.markdown("---")
    rc1, rc2 = st.columns(2)
    with rc1:
        st.markdown(f"""
        <div class="summary-card-green" style="text-align: center; padding: 20px;">
            <div style="font-size: 0.9rem; font-weight: 700;">CONVERSION RESULT</div>
            <div style="font-size: 2.2rem; font-weight: 800; margin: 10px 0;">{conv_amount:,.2f} {from_curr} = {converted_result:,.2f} {to_curr}</div>
            <div style="font-size: 0.85rem;">Exchange Rate: 1 {from_curr} = {(to_rate / from_rate if from_rate > 0 else 0.0):,.4f} {to_curr}</div>
        </div>
        """, unsafe_allow_html=True)

    with rc2:
        st.markdown("#### 🌐 Common BHD Conversions Quick Table")
        quick_df = pd.DataFrame([
            {"Currency": "Philippine Peso (PHP)", "1 BHD Equivalent": f"₱{bhd_to_php:,.2f}", f"{conv_amount:,.0f} BHD Value": f"₱{(conv_amount * bhd_to_php):,.2f}"},
            {"Currency": "US Dollar (USD)", "1 BHD Equivalent": f"${bhd_to_usd:,.2f}", f"{conv_amount:,.0f} BHD Value": f"${(conv_amount * bhd_to_usd):,.2f}"},
            {"Currency": "Euro (EUR)", "1 BHD Equivalent": f"€{live_rates_dict.get('EUR', 2.45):,.2f}", f"{conv_amount:,.0f} BHD Value": f"€{(conv_amount * live_rates_dict.get('EUR', 2.45)):,.2f}"},
            {"Currency": "British Pound (GBP)", "1 BHD Equivalent": f"£{live_rates_dict.get('GBP', 2.10):,.2f}", f"{conv_amount:,.0f} BHD Value": f"£{(conv_amount * live_rates_dict.get('GBP', 2.10)):,.2f}"}
        ])
        st.dataframe(quick_df, use_container_width=True, hide_index=True)

# TAB 7: SECURITY & DEPLOYMENT GUIDE
with tab_guide:
    st.subheader("📘 Security & Configuration Guide")
    st.markdown("""
    ### 🔐 Custom Access Keys Setup:
    To configure private passkeys for Rogee, User 2, User 3, or User 4 on Streamlit Cloud:
    1. Open your Streamlit Cloud dashboard.
    2. Go to **App Settings > Secrets**.
    3. Add your private keys using standard secret configuration.
    """)
