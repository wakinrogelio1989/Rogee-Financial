import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import os
import json

# Set Streamlit page config
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

# Session State Auth Gate
if "authenticated_user" not in st.session_state:
    st.session_state["authenticated_user"] = None

if st.session_state["authenticated_user"] is None:
    st.markdown('<div class="main-header">🔒 Rogee Financial Command Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Please select your account profile and enter your secret passcode to enter.</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    col_gate1, col_gate2, col_gate3 = st.columns([1, 2, 1])
    with col_gate2:
        selected_prof = st.selectbox("Select Account Profile", list(USER_PROFILES.keys()), index=0)
        entered_pass = st.text_input("Secret Passcode", type="password")
        
        prof_info = USER_PROFILES[selected_prof]
        expected_pass = prof_info["def_key"]
        try:
            if prof_info["sec_key"] in st.secrets:
                expected_pass = st.secrets[prof_info["sec_key"]]
        except Exception:
            pass
            
        if st.button("🔓 Authenticate & Open Dashboard", use_container_width=True, type="primary"):
            if entered_pass == expected_pass:
                st.session_state["authenticated_user"] = selected_prof
                st.success(f"Welcome back, {selected_prof}!")
                st.rerun()
            else:
                st.error("Incorrect passcode. Please check your credentials.")
        
        st.markdown("---")
        st.info("💡 **Default Credentials:**\n- Rogee: `rogee2026`\n- User 2: `user2026`\n- User 3: `user32026`\n- User 4: `user42026`")
    st.stop()

# Authenticated User
current_user = st.session_state["authenticated_user"]
user_cfg = USER_PROFILES[current_user]
DATA_FILE = user_cfg["data_file"]
CONFIG_FILE = user_cfg["config_file"]
INVEST_FILE = user_cfg["invest_file"]

# Sidebar Header & Sign Out
st.sidebar.markdown(f"### 👤 Logged in: **{current_user}**")
if st.sidebar.button("🔒 Lock Portal / Sign Out", use_container_width=True):
    st.session_state["authenticated_user"] = None
    st.rerun()

st.sidebar.markdown("---")

# Load Config Settings
def load_config():
    defaults = {
        "salary_bhd": 1200.0,
        "business_bhd": 0.0,
        "sidelines_bhd": 0.0,
        "other_income_bhd": 0.0,
        "bhd_to_php": 155.0,
        "bhd_to_usd": 2.65,
        "needs_pct": 45,
        "wants_pct": 20,
        "savings_pct": 20,
        "debts_pct": 15
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                defaults.update(data)
        except Exception:
            pass
    return defaults

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=4)
    except Exception:
        pass

cfg = load_config()

# Sidebar Inputs
st.sidebar.title("⚙️ Budget & Income Settings")

st.sidebar.subheader("💵 Monthly Take-Home Income Streams")
salary_bhd = st.sidebar.number_input("Primary Salary (BHD)", min_value=0.0, value=float(cfg["salary_bhd"]), step=50.0)
business_bhd = st.sidebar.number_input("Business Income (BHD)", min_value=0.0, value=float(cfg["business_bhd"]), step=50.0)
sidelines_bhd = st.sidebar.number_input("Sidelines / Freelance (BHD)", min_value=0.0, value=float(cfg["sidelines_bhd"]), step=50.0)
other_income_bhd = st.sidebar.number_input("Other Income / Bonus (BHD)", min_value=0.0, value=float(cfg["other_income_bhd"]), step=50.0)

total_income_bhd = salary_bhd + business_bhd + sidelines_bhd + other_income_bhd

st.sidebar.markdown("---")
st.sidebar.subheader("💱 Live Exchange Rates")
bhd_to_php = st.sidebar.number_input("1 BHD = PHP (₱)", min_value=1.0, value=float(cfg["bhd_to_php"]), step=0.5)
bhd_to_usd = st.sidebar.number_input("1 BHD = USD ($)", min_value=0.1, value=float(cfg["bhd_to_usd"]), step=0.01)

# Combined Income Banner in Sidebar
tot_income_php = total_income_bhd * bhd_to_php
tot_income_usd = total_income_bhd * bhd_to_usd

st.sidebar.markdown(f"""
<div class="income-card">
    <div style="font-weight: 700; font-size: 0.85rem;">💰 TOTAL COMBINED MONTHLY INCOME</div>
    <div style="font-size: 1.15rem; font-weight: 800; margin-top: 4px;">BD {total_income_bhd:,.2f}</div>
    <div style="font-size: 0.82rem; margin-top: 2px;">₱ {tot_income_php:,.2f} PHP &nbsp;|&nbsp; ${tot_income_usd:,.2f} USD</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 4-Category Framework Targets (%)")
debts_pct = st.sidebar.slider("Debts & Credits Target %", 0, 100, int(cfg["debts_pct"]))
needs_pct = st.sidebar.slider("Needs Target % (Essentials)", 0, 100, int(cfg["needs_pct"]))
wants_pct = st.sidebar.slider("Wants Target % (Lifestyle)", 0, 100, int(cfg["wants_pct"]))
savings_pct = st.sidebar.slider("Savings & Investments Target %", 0, 100, int(cfg["savings_pct"]))

tot_alloc = debts_pct + needs_pct + wants_pct + savings_pct
if tot_alloc != 100:
    st.sidebar.warning(f"Total allocation is {tot_alloc}%. Recommended total is 100%.")

# Save Config on Change
new_cfg = {
    "salary_bhd": salary_bhd,
    "business_bhd": business_bhd,
    "sidelines_bhd": sidelines_bhd,
    "other_income_bhd": other_income_bhd,
    "bhd_to_php": bhd_to_php,
    "bhd_to_usd": bhd_to_usd,
    "needs_pct": needs_pct,
    "wants_pct": wants_pct,
    "savings_pct": savings_pct,
    "debts_pct": debts_pct
}
if new_cfg != cfg:
    save_config(new_cfg)

# Target Calculations
debts_target = total_income_bhd * (debts_pct / 100.0)
needs_target = total_income_bhd * (needs_pct / 100.0)
wants_target = total_income_bhd * (wants_pct / 100.0)
savings_target = total_income_bhd * (savings_pct / 100.0)

# Load Expense Ledger
def load_expenses():
    cols = [
        "Item #", "Date", "Main Category", "Sub Category", "Merchant/Description",
        "Billed Amount", "Actual Paid", "Currency", "Pending Due", "% Paid",
        "% Remaining", "Equivalent", "Status", "Payment Method", "Billed_BHD", "Paid_BHD"
    ]
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
            # Ensure required columns exist
            for col in cols:
                if col not in df.columns:
                    if col in ["Billed Amount", "Actual Paid", "Pending Due", "% Paid", "% Remaining", "Billed_BHD", "Paid_BHD"]:
                        df[col] = 0.0
                    elif col == "Currency":
                        df[col] = "BHD"
                    elif col == "Status":
                        df[col] = "Not Paid"
                    elif col == "Item #":
                        df[col] = range(1, len(df) + 1)
                    else:
                        df[col] = "N/A"
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=cols)

def save_expenses(df):
    df.to_csv(DATA_FILE, index=False)

df_expenses = load_expenses()

# Helper function to compute BHD equivalent for any amount based on selected currency
def convert_to_bhd(amount, curr):
    amount = float(amount) if pd.notnull(amount) else 0.0
    curr = str(curr).upper() if pd.notnull(curr) else "BHD"
    if curr in ["PHP", "₱"]:
        return amount / bhd_to_php if bhd_to_php > 0 else 0.0
    elif curr in ["USD", "$"]:
        return amount / bhd_to_usd if bhd_to_usd > 0 else 0.0
    return amount # Default BHD

def format_equivalent_string(billed_amt, curr):
    billed_amt = float(billed_amt) if pd.notnull(billed_amt) else 0.0
    curr = str(curr).upper() if pd.notnull(curr) else "BHD"
    if curr in ["PHP", "₱"]:
        bhd_val = billed_amt / bhd_to_php if bhd_to_php > 0 else 0.0
        usd_val = bhd_val * bhd_to_usd
        return f"BD {bhd_val:,.2f} | $ {usd_val:,.2f}"
    elif curr in ["USD", "$"]:
        bhd_val = billed_amt / bhd_to_usd if bhd_to_usd > 0 else 0.0
        php_val = bhd_val * bhd_to_php
        return f"BD {bhd_val:,.2f} | ₱ {php_val:,.2f}"
    else: # BHD
        php_val = billed_amt * bhd_to_php
        usd_val = billed_amt * bhd_to_usd
        return f"₱ {php_val:,.2f} | $ {usd_val:,.2f}"

# Recalculate row metrics whenever expenses are loaded or updated
if not df_expenses.empty:
    df_expenses["Billed Amount"] = pd.to_numeric(df_expenses["Billed Amount"], errors="coerce").fillna(0.0)
    df_expenses["Actual Paid"] = pd.to_numeric(df_expenses["Actual Paid"], errors="coerce").fillna(0.0)
    df_expenses["Currency"] = df_expenses["Currency"].fillna("BHD").astype(str)
    
    # Compute row conversions
    bhd_billed_list = []
    bhd_paid_list = []
    equiv_str_list = []
    pending_list = []
    pct_paid_list = []
    pct_rem_list = []
    status_list = []
    
    for _, row in df_expenses.iterrows():
        b_amt = float(row["Billed Amount"])
        p_amt = float(row["Actual Paid"])
        curr = str(row["Currency"]).upper()
        
        b_bhd = convert_to_bhd(b_amt, curr)
        p_bhd = convert_to_bhd(p_amt, curr)
        
        pend = max(0.0, b_amt - p_amt)
        pct_p = (p_amt / b_amt * 100.0) if b_amt > 0 else (100.0 if p_amt > 0 else 0.0)
        pct_r = max(0.0, 100.0 - pct_p)
        
        if pct_p >= 99.99:
            st_val = "Paid"
        elif pct_p <= 0.01:
            st_val = "Not Paid"
        else:
            st_val = "Partially Paid"
            
        eq_str = format_equivalent_string(b_amt, curr)
        
        bhd_billed_list.append(b_bhd)
        bhd_paid_list.append(p_bhd)
        equiv_str_list.append(eq_str)
        pending_list.append(pend)
        pct_paid_list.append(pct_p)
        pct_rem_list.append(pct_r)
        status_list.append(st_val)
        
    df_expenses["Billed_BHD"] = bhd_billed_list
    df_expenses["Paid_BHD"] = bhd_paid_list
    df_expenses["Pending Due"] = pending_list
    df_expenses["% Paid"] = pct_paid_list
    df_expenses["% Remaining"] = pct_rem_list
    df_expenses["Status"] = status_list
    df_expenses["Equivalent"] = equiv_str_list

# Header Time Badges
now_utc = datetime.now(timezone.utc)
bh_time = now_utc.astimezone(timezone(timedelta(hours=3)))
ph_time = now_utc.astimezone(timezone(timedelta(hours=8)))

st.markdown('<div class="main-header">Rogee Financial Command Center</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Multi-Currency Personal Finance Manager (50/30/20 & Custom Frameworks)</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="time-badge">
    🇧🇭 <b>Bahrain:</b> {bh_time.strftime("%d %b %Y, %I:%M %p")} AST &nbsp;|&nbsp; 
    🇵🇭 <b>Philippines:</b> {ph_time.strftime("%d %b %Y, %I:%M %p")} PHT &nbsp;|&nbsp; 
    👤 <b>Profile:</b> {current_user}
</div>
""", unsafe_allow_html=True)

# Main Navigation Tabs
tab_dash, tab_add, tab_history, tab_proj, tab_mt5, tab_reports, tab_guide = st.tabs([
    "📊 Dashboard & Analytics",
    "➕ Record Expense / Payment",
    "📜 Transaction History",
    "🔮 12-Month Projections",
    "📈 MT5 Pip & Margin Calculator",
    "📥 Download Reports",
    "📘 Guide & Secrets"
])

# Actual Spending Calculations in BHD
actual_priority_bhd = float(df_expenses[df_expenses["Main Category"] == "100% Priority & People to Pay"]["Paid_BHD"].sum()) if not df_expenses.empty else 0.0
actual_debts_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Debts", case=False, na=False)]["Paid_BHD"].sum()) if not df_expenses.empty else 0.0
actual_needs_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Needs", case=False, na=False)]["Paid_BHD"].sum()) if not df_expenses.empty else 0.0
actual_wants_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Wants", case=False, na=False)]["Paid_BHD"].sum()) if not df_expenses.empty else 0.0
actual_savings_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Savings", case=False, na=False)]["Paid_BHD"].sum()) if not df_expenses.empty else 0.0

total_spent_bhd = actual_priority_bhd + actual_debts_bhd + actual_needs_bhd + actual_wants_bhd + actual_savings_bhd
total_billed_bhd = float(df_expenses["Billed_BHD"].sum()) if not df_expenses.empty else 0.0
total_pending_bhd = max(0.0, total_billed_bhd - total_spent_bhd)

remaining_cash_bhd = total_income_bhd - total_spent_bhd
savings_rate = (actual_savings_bhd / total_income_bhd * 100.0) if total_income_bhd > 0 else 0.0

framework_title = f"{debts_pct}/{needs_pct}/{wants_pct}/{savings_pct} Framework"

# OVER-BUDGET ALERT BANNER
if remaining_cash_bhd < 0:
    over_bhd = abs(remaining_cash_bhd)
    over_php = over_bhd * bhd_to_php
    over_usd = over_bhd * bhd_to_usd
    st.markdown(f"""
    <div class="priority-banner">
        🚨 <b>OVER BUDGET ALERT!</b> Your total paid expenses exceed your monthly income by 
        <b>BD {over_bhd:,.2f}</b> (₱ {over_php:,.2f} PHP | ${over_usd:,.2f} USD).
    </div>
    """, unsafe_allow_html=True)
else:
    rem_php = remaining_cash_bhd * bhd_to_php
    rem_usd = remaining_cash_bhd * bhd_to_usd
    st.markdown(f"""
    <div class="income-card">
        💚 <b>NET REMAINING CASH UNSPENT:</b> <b>BD {remaining_cash_bhd:,.2f}</b> 
        (₱ {rem_php:,.2f} PHP &nbsp;|&nbsp; ${rem_usd:,.2f} USD)
    </div>
    """, unsafe_allow_html=True)

# TAB 1: DASHBOARD
with tab_dash:
    st.subheader(f"📊 Dashboard & Analytics ({framework_title})")
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Total Monthly Income", f"BD {total_income_bhd:,.2f}", delta=f"₱{(total_income_bhd*bhd_to_php):,.0f} PHP")
    col_m2.metric("Total Actual Paid", f"BD {total_spent_bhd:,.2f}", delta=f"-BD {total_spent_bhd:,.2f}", delta_color="inverse")
    col_m3.metric("Total Expenses Billed", f"BD {total_billed_bhd:,.2f}", delta=f"Pending: BD {total_pending_bhd:,.2f}")
    
    if remaining_cash_bhd >= 0:
        col_m4.metric("Remaining Net Cash", f"BD {remaining_cash_bhd:,.2f}", delta=f"₱{(remaining_cash_bhd*bhd_to_php):,.0f} PHP")
    else:
        col_m4.metric("Over Budget Deficit", f"-BD {abs(remaining_cash_bhd):,.2f}", delta=f"-₱{(abs(remaining_cash_bhd)*bhd_to_php):,.0f} PHP", delta_color="inverse")

    st.markdown("---")
    st.subheader("📋 Benchmark Allocation Breakdown & Targets")

    cat_data = [
        {"Category": "Mandatory 100% Priority", "Target %": "100% Direct", "Target (BHD)": total_income_bhd, "Actual Paid (BHD)": actual_priority_bhd, "Status": "Fixed Priority"},
        {"Category": f"Debts & Credits ({debts_pct}%)", "Target %": f"{debts_pct}%", "Target (BHD)": debts_target, "Actual Paid (BHD)": actual_debts_bhd, "Status": "On Track" if actual_debts_bhd <= debts_target else "Over Target"},
        {"Category": f"Needs ({needs_pct}%)", "Target %": f"{needs_pct}%", "Target (BHD)": needs_target, "Actual Paid (BHD)": actual_needs_bhd, "Status": "On Track" if actual_needs_bhd <= needs_target else "Over Target"},
        {"Category": f"Wants ({wants_pct}%)", "Target %": f"{wants_pct}%", "Target (BHD)": wants_target, "Actual Paid (BHD)": actual_wants_bhd, "Status": "On Track" if actual_wants_bhd <= wants_target else "Over Target"},
        {"Category": f"Savings & Investments ({savings_pct}%)", "Target %": f"{savings_pct}%", "Target (BHD)": savings_target, "Actual Paid (BHD)": actual_savings_bhd, "Status": "Goal Met" if actual_savings_bhd >= savings_target else "Under Goal"}
    ]
    df_cat_summary = pd.DataFrame(cat_data)
    
    st.dataframe(
        df_cat_summary.style.format({
            "Target (BHD)": "BD {:,.2f}",
            "Actual Paid (BHD)": "BD {:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.subheader("Target vs. Actual Spending (BHD)")
        chart_df = pd.DataFrame({
            "Category": ["Debts", "Needs", "Wants", "Savings"],
            "Target": [debts_target, needs_target, wants_target, savings_target],
            "Actual": [actual_debts_bhd, actual_needs_bhd, actual_wants_bhd, actual_savings_bhd]
        })
        fig_bar = go.Figure(data=[
            go.Bar(name='Target', x=chart_df['Category'], y=chart_df['Target'], marker_color='#93C5FD'),
            go.Bar(name='Actual', x=chart_df['Category'], y=chart_df['Actual'], marker_color='#1D4ED8')
        ])
        fig_bar.update_layout(
            barmode='group',
            yaxis_title="Amount (BHD)",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_c2:
        st.subheader("Actual Expense Distribution")
        if total_spent_bhd > 0:
            fig_pie = px.pie(
                values=[actual_priority_bhd, actual_debts_bhd, actual_needs_bhd, actual_wants_bhd, actual_savings_bhd],
                names=["100% Priority", "Debts & Credits", "Needs", "Wants", "Savings & Investments"],
                color_discrete_sequence=['#EF4444', '#F59E0B', '#2563EB', '#10B981', '#8B5CF6'],
                hole=0.45
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expense transactions recorded yet.")

# TAB 2: RECORD EXPENSE / PAYMENT
with tab_add:
    st.subheader("➕ Record a New Expense or Payment")
    
    # Real-time category selector OUTSIDE form for instant subcategory updates
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        sel_main_cat = st.selectbox("1. Select Main Category", [
            "100% Priority & People to Pay",
            f"Debts & Credits ({debts_pct}%)",
            f"Needs ({needs_pct}%)",
            f"Wants ({wants_pct}%)",
            f"Savings & Investments ({savings_pct}%)"
        ], key="rec_main_cat")
    
    if "Priority" in sel_main_cat:
        sub_options = ["Wife / Family Allowance", "Parents Allowance", "Tithe / Charity", "Emergency Support", "Child Support"]
    elif "Debts" in sel_main_cat:
        sub_options = ["Credit Card Minimum", "Credit Card Full Payment", "Personal Bank Loan", "Car Loan", "Housing Loan", "Friend/Personal Debt"]
    elif "Needs" in sel_main_cat:
        sub_options = ["Rent / Housing", "Electricity & Water (EWA)", "Telecom & Internet", "Groceries & Household", "Transportation & Fuel", "Healthcare & Medicine"]
    elif "Wants" in sel_main_cat:
        sub_options = ["Dining Out & Coffee", "Entertainment & Streaming", "Shopping & Apparel", "Hobbies & Travel", "Subscriptions", "Miscellaneous"]
    else: # Savings
        sub_options = ["Emergency Fund Deposit", "COL Financial Stocks (PHP)", "MT5 Forex Trading Deposit", "Crypto Investment", "Bank Savings Accumulation"]

    with col_f2:
        sel_sub_cat = st.selectbox("2. Select Sub-Category", sub_options, key="rec_sub_cat")

    st.markdown("---")
    
    with st.form("add_expense_form_clean", clear_on_submit=True):
        col_in1, col_in2 = st.columns(2)
        
        with col_in1:
            exp_date = st.date_input("Transaction Date", value=datetime.today())
            merchant = st.text_input("Merchant / Description / Payee", placeholder="e.g. Utility Company, Credit Card, COL Deposit")
            
            # CURRENCY SELECTOR IS PROMINENT
            rec_curr = st.selectbox("Transaction Currency", ["BHD", "PHP", "USD"], index=0, help="Select the currency of the amount you are entering.")
            
        with col_in2:
            billed_amt = st.number_input(f"Planned / Billed Amount ({rec_curr})", min_value=0.0, value=100.0, step=10.0, help=f"Enter amount in {rec_curr}.")
            
            # Default payment status
            pay_status = st.selectbox("Payment Status", ["Paid", "Partially Paid", "Not Paid"], index=0)
            
            default_paid = billed_amt if pay_status == "Paid" else (0.0 if pay_status == "Not Paid" else billed_amt * 0.5)
            actual_paid = st.number_input(f"Actual Amount Paid ({rec_curr})", min_value=0.0, value=float(default_paid), step=10.0, help=f"Enter actual amount paid in {rec_curr}.")
            
            pay_method = st.selectbox("Payment Method", ["Benefit Pay", "Remittance / Exchange", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])

        submit_btn = st.form_submit_button("💾 Save Expense Transaction", use_container_width=True, type="primary")

        if submit_btn:
            b_bhd = convert_to_bhd(billed_amt, rec_curr)
            p_bhd = convert_to_bhd(actual_paid, rec_curr)
            
            pend = max(0.0, billed_amt - actual_paid)
            pct_p = (actual_paid / billed_amt * 100.0) if billed_amt > 0 else (100.0 if actual_paid > 0 else 0.0)
            pct_r = max(0.0, 100.0 - pct_p)
            
            if pct_p >= 99.99:
                final_status = "Paid"
            elif pct_p <= 0.01:
                final_status = "Not Paid"
            else:
                final_status = "Partially Paid"
                
            eq_str = format_equivalent_string(billed_amt, rec_curr)
            
            new_entry = pd.DataFrame([{
                "Item #": len(df_expenses) + 1,
                "Date": exp_date,
                "Main Category": sel_main_cat,
                "Sub Category": sel_sub_cat,
                "Merchant/Description": merchant if merchant else "Unspecified Payee",
                "Billed Amount": billed_amt,
                "Actual Paid": actual_paid,
                "Currency": rec_curr,
                "Pending Due": pend,
                "% Paid": pct_p,
                "% Remaining": pct_r,
                "Equivalent": eq_str,
                "Status": final_status,
                "Payment Method": pay_method,
                "Billed_BHD": b_bhd,
                "Paid_BHD": p_bhd
            }])
            
            df_expenses = pd.concat([df_expenses, new_entry], ignore_index=True)
            save_expenses(df_expenses)
            st.success(f"Successfully recorded transaction: {rec_curr} {billed_amt:,.2f} for '{merchant if merchant else sel_sub_cat}'!")
            st.rerun()

# TAB 3: TRANSACTION HISTORY
with tab_history:
    st.subheader("📜 Recorded Expense History & Ledger")
    
    if not df_expenses.empty:
        # Category Filter
        cat_options = list(df_expenses["Main Category"].unique())
        selected_cats = st.multiselect("Filter by Category", options=cat_options, default=cat_options)
        
        filtered_df = df_expenses[df_expenses["Main Category"].isin(selected_cats)].copy() if selected_cats else df_expenses.copy()
        
        # Chronological Sort & Item Re-indexing
        filtered_df = filtered_df.sort_values(by=["Date", "Main Category"], ascending=[True, True]).reset_index(drop=True)
        filtered_df["Item #"] = range(1, len(filtered_df) + 1)
        
        # Recalculate row properties dynamically for display
        display_cols = [
            "Item #", "Date", "Main Category", "Sub Category", "Merchant/Description",
            "Billed Amount", "Actual Paid", "Currency", "Pending Due", "% Paid",
            "% Remaining", "Equivalent", "Status", "Payment Method"
        ]
        
        df_display = filtered_df[display_cols].copy()
        
        st.info("💡 **Editing Instructions:** You can double-click cells in the table below to edit Date, Categories, Description, Billed Amount, Actual Paid, Currency, Status, or Method. Click **💾 Save Ledger Changes** to update.")
        
        # Data Editor
        edited_df = st.data_editor(
            df_display,
            column_config={
                "Item #": st.column_config.NumberColumn("Item #", disabled=True),
                "Billed Amount": st.column_config.NumberColumn("Billed Amount", format="%.2f"),
                "Actual Paid": st.column_config.NumberColumn("Actual Paid", format="%.2f"),
                "Currency": st.column_config.SelectboxColumn("Currency", options=["BHD", "PHP", "USD"]),
                "Pending Due": st.column_config.NumberColumn("Pending Due", format="%.2f", disabled=True),
                "% Paid": st.column_config.NumberColumn("% Paid", format="%.1f%%", disabled=True),
                "% Remaining": st.column_config.NumberColumn("% Remaining", format="%.1f%%", disabled=True),
                "Equivalent": st.column_config.TextColumn("Equivalent (BHD/PHP/USD)", disabled=True),
                "Status": st.column_config.SelectboxColumn("Status", options=["Paid", "Partially Paid", "Not Paid"]),
                "Payment Method": st.column_config.SelectboxColumn("Payment Method", options=["Benefit Pay", "Remittance / Exchange", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])
            },
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True
        )
        
        col_s1, col_s2 = st.columns([1, 4])
        with col_s1:
            if st.button("💾 Save Ledger Changes", type="primary", use_container_width=True):
                # Update underlying dataframe
                edited_df["Billed Amount"] = pd.to_numeric(edited_df["Billed Amount"], errors="coerce").fillna(0.0)
                edited_df["Actual Paid"] = pd.to_numeric(edited_df["Actual Paid"], errors="coerce").fillna(0.0)
                
                # Recompute conversions
                b_bhd_col = []
                p_bhd_col = []
                for _, r in edited_df.iterrows():
                    b_bhd_col.append(convert_to_bhd(r["Billed Amount"], r["Currency"]))
                    p_bhd_col.append(convert_to_bhd(r["Actual Paid"], r["Currency"]))
                    
                edited_df["Billed_BHD"] = b_bhd_col
                edited_df["Paid_BHD"] = p_bhd_col
                
                save_expenses(edited_df)
                st.success("Ledger changes saved successfully!")
                st.rerun()

        st.markdown("---")
        st.subheader("🎨 Status-Highlighted Color Ledger View")
        
        # Color Highlighting Function
        def highlight_status_row(row):
            pct = float(row["% Paid"]) if pd.notnull(row["% Paid"]) else 0.0
            if pct >= 99.99:
                return ['background-color: #D1FAE5; color: #065F46; font-weight: 600;'] * len(row) # Light Green
            elif pct <= 0.01:
                return ['background-color: #FEE2E2; color: #991B1B; font-weight: 600;'] * len(row) # Light Red
            else:
                return ['background-color: #FEF3C7; color: #92400E; font-weight: 600;'] * len(row) # Light Yellow

        styled_ledger = df_display.style.apply(highlight_status_row, axis=1).format({
            "Billed Amount": "{:,.2f}",
            "Actual Paid": "{:,.2f}",
            "Pending Due": "{:,.2f}",
            "% Paid": "{:.1f}%",
            "% Remaining": "{:.1f}%"
        })
        
        st.dataframe(styled_ledger, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("💰 Total Outstanding & Payment Ledger Summary")
        
        # Calculations for PHP specific items and Overall totals
        df_php_items = df_expenses[df_expenses["Currency"].astype(str).str.upper() == "PHP"]
        php_billed_total = float(df_php_items["Billed Amount"].sum()) if not df_php_items.empty else 0.0
        php_paid_total = float(df_php_items["Actual Paid"].sum()) if not df_php_items.empty else 0.0
        php_pending_total = max(0.0, php_billed_total - php_paid_total)
        
        php_billed_bhd = php_billed_total / bhd_to_php if bhd_to_php > 0 else 0.0
        php_paid_bhd = php_paid_total / bhd_to_php if bhd_to_php > 0 else 0.0
        php_pending_bhd = php_pending_total / bhd_to_php if bhd_to_php > 0 else 0.0

        tot_billed_all_bhd = float(df_expenses["Billed_BHD"].sum()) if not df_expenses.empty else 0.0
        tot_paid_all_bhd = float(df_expenses["Paid_BHD"].sum()) if not df_expenses.empty else 0.0
        tot_pending_all_bhd = max(0.0, tot_billed_all_bhd - tot_paid_all_bhd)

        col_sum1, col_sum2, col_sum3 = st.columns(3)

        with col_sum1:
            st.markdown(f"""
            <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-left: 5px solid #3B82F6; padding: 12px; border-radius: 8px;">
                <h4 style="margin:0; color: #1E40AF;">📋 TOTAL BILLED / NEEDED TO PAY</h4>
                <hr style="margin: 8px 0;">
                <p style="margin:2px 0;"><b>🇵🇭 PHP Transactions Needed:</b><br><span style="font-size:1.1rem; color:#1D4ED8;"><b>₱ {php_billed_total:,.2f} PHP</b></span> (BD {php_billed_bhd:,.2f})</p>
                <hr style="margin: 8px 0;">
                <p style="margin:2px 0;"><b>🌍 Grand Total (All Currencies):</b><br>
                <b>BD {tot_billed_all_bhd:,.2f}</b><br>
                ₱ {(tot_billed_all_bhd * bhd_to_php):,.2f} PHP &nbsp;|&nbsp; ${(tot_billed_all_bhd * bhd_to_usd):,.2f} USD</p>
            </div>
            """, unsafe_allow_html=True)

        with col_sum2:
            st.markdown(f"""
            <div style="background-color: #F0FDF4; border: 1px solid #BBF7D0; border-left: 5px solid #22C55E; padding: 12px; border-radius: 8px;">
                <h4 style="margin:0; color: #166534;">🟢 TOTAL ACTUAL AMOUNT PAID</h4>
                <hr style="margin: 8px 0;">
                <p style="margin:2px 0;"><b>🇵🇭 PHP Transactions Paid:</b><br><span style="font-size:1.1rem; color:#15803D;"><b>₱ {php_paid_total:,.2f} PHP</b></span> (BD {php_paid_bhd:,.2f})</p>
                <hr style="margin: 8px 0;">
                <p style="margin:2px 0;"><b>🌍 Grand Total (All Currencies):</b><br>
                <b>BD {tot_paid_all_bhd:,.2f}</b><br>
                ₱ {(tot_paid_all_bhd * bhd_to_php):,.2f} PHP &nbsp;|&nbsp; ${(tot_paid_all_bhd * bhd_to_usd):,.2f} USD</p>
            </div>
            """, unsafe_allow_html=True)

        with col_sum3:
            st.markdown(f"""
            <div style="background-color: #FEF2F2; border: 1px solid #FECACA; border-left: 5px solid #EF4444; padding: 12px; border-radius: 8px;">
                <h4 style="margin:0; color: #991B1B;">🔴 TOTAL REMAINING PENDING DUE</h4>
                <hr style="margin: 8px 0;">
                <p style="margin:2px 0;"><b>🇵🇭 PHP Remaining Unpaid:</b><br><span style="font-size:1.1rem; color:#B91C1C;"><b>₱ {php_pending_total:,.2f} PHP</b></span> (BD {php_pending_bhd:,.2f})</p>
                <hr style="margin: 8px 0;">
                <p style="margin:2px 0;"><b>🌍 Grand Total (All Currencies):</b><br>
                <b>BD {tot_pending_all_bhd:,.2f}</b><br>
                ₱ {(tot_pending_all_bhd * bhd_to_php):,.2f} PHP &nbsp;|&nbsp; ${(tot_pending_all_bhd * bhd_to_usd):,.2f} USD</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🚨 Clear All Expense Data", type="primary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.success("All expense logs cleared!")
            st.rerun()
    else:
        st.info("No expense transactions recorded yet.")

# TAB 4: 12-MONTH PROJECTIONS
with tab_proj:
    st.subheader("🔮 12-Month & Yearly Projected Budgeting & Savings Engine")
    st.markdown("Forecast your detailed future monthly expenses, income growth, and potential savings over the next 12 months.")
    
    col_pj1, col_pj2 = st.columns(2)
    
    with col_pj1:
        proj_base_income = st.number_input("Base Projected Monthly Income (BHD)", min_value=0.0, value=float(total_income_bhd), step=50.0)
        proj_income_growth = st.slider("Expected Annual Income Growth (%)", 0.0, 20.0, 0.0, step=0.5)
        proj_fixed_needs = st.number_input("Monthly Fixed Needs & Priorities (BHD)", min_value=0.0, value=float(actual_priority_bhd + actual_needs_bhd + actual_debts_bhd), step=50.0)
        
    with col_pj2:
        proj_inflation = st.slider("Annual Expense Inflation Rate (%)", 0.0, 15.0, 2.5, step=0.5)
        proj_wants = st.number_input("Projected Lifestyle Allowance (BHD)", min_value=0.0, value=float(actual_wants_bhd), step=25.0)
        proj_target_savings = st.number_input("Monthly Target Savings (BHD)", min_value=0.0, value=float(savings_target), step=25.0)

    # 12-Month Simulation Calculation
    proj_months = []
    cum_savings = 0.0
    
    for m in range(1, 13):
        m_inc = proj_base_income * ((1.0 + (proj_income_growth / 100.0) / 12.0) ** (m - 1))
        m_exp = (proj_fixed_needs + proj_wants) * ((1.0 + (proj_inflation / 100.0) / 12.0) ** (m - 1))
        m_surplus = m_inc - m_exp
        cum_savings += m_surplus
        
        proj_months.append({
            "Month": f"Month {m}",
            "Projected Income (BHD)": round(m_inc, 2),
            "Fixed Commitments (BHD)": round(proj_fixed_needs * ((1.0 + (proj_inflation / 100.0) / 12.0) ** (m - 1)), 2),
            "Lifestyle Expenses (BHD)": round(proj_wants * ((1.0 + (proj_inflation / 100.0) / 12.0) ** (m - 1)), 2),
            "Total Projected Expenses (BHD)": round(m_exp, 2),
            "Monthly Net Surplus (BHD)": round(m_surplus, 2),
            "Cumulative Wealth (BHD)": round(cum_savings, 2)
        })
        
    df_proj = pd.DataFrame(proj_months)
    
    st.markdown("---")
    st.subheader("📊 12-Month Projected Cashflow Matrix")
    
    st.dataframe(
        df_proj.style.format({
            "Projected Income (BHD)": "BD {:,.2f}",
            "Fixed Commitments (BHD)": "BD {:,.2f}",
            "Lifestyle Expenses (BHD)": "BD {:,.2f}",
            "Total Projected Expenses (BHD)": "BD {:,.2f}",
            "Monthly Net Surplus (BHD)": "BD {:,.2f}",
            "Cumulative Wealth (BHD)": "BD {:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    col_p1, col_p2, col_p3 = st.columns(3)
    
    tot_proj_inc = df_proj["Projected Income (BHD)"].sum()
    tot_proj_exp = df_proj["Total Projected Expenses (BHD)"].sum()
    tot_proj_sav = df_proj["Monthly Net Surplus (BHD)"].sum()
    
    col_p1.metric("1-Year Projected Income", f"BD {tot_proj_inc:,.2f}", delta=f"₱{(tot_proj_inc*bhd_to_php):,.0f} PHP")
    col_p2.metric("1-Year Projected Expenses", f"BD {tot_proj_exp:,.2f}", delta=f"-BD {tot_proj_exp:,.2f}", delta_color="inverse")
    col_p3.metric("1-Year Net Savings Potential", f"BD {tot_proj_sav:,.2f}", delta=f"₱{(tot_proj_sav*bhd_to_php):,.0f} PHP")

    col_pc1, col_pc2 = st.columns(2)
    with col_pc1:
        st.subheader("Month-by-Month Projected Cash Flow")
        fig_proj_bar = go.Figure(data=[
            go.Bar(name='Projected Income', x=df_proj['Month'], y=df_proj['Projected Income (BHD)'], marker_color='#10B981'),
            go.Bar(name='Projected Expenses', x=df_proj['Month'], y=df_proj['Total Projected Expenses (BHD)'], marker_color='#EF4444')
        ])
        fig_proj_bar.update_layout(barmode='group', yaxis_title="BHD", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_proj_bar, use_container_width=True)

    with col_pc2:
        st.subheader("1-Year Cumulative Wealth & Savings Trend")
        fig_proj_line = px.line(df_proj, x="Month", y="Cumulative Wealth (BHD)", markers=True, title="Cumulative Wealth Growth")
        fig_proj_line.update_traces(line_color="#2563EB", line_width=3)
        fig_proj_line.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_proj_line, use_container_width=True)

# TAB 5: MT5 PIP & MARGIN CALCULATOR
with tab_mt5:
    st.subheader("📈 MT5 Pip Value & Required Margin Calculator")
    
    col_pip1, col_pip2 = st.columns(2)
    
    with col_pip1:
        st.markdown("#### 📍 Pip Value Calculator")
        pair_select = st.selectbox("Currency Pair", [
            "USDPHP", "BHDPHP", "USDCAD", "EURUSD", "GBPUSD", "USDJPY",
            "XAUUSD (Gold)", "USDCHF", "AUDUSD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"
        ])
        lot_size = st.number_input("Lot Volume (e.g., 0.10, 1.00)", min_value=0.01, value=1.00, step=0.10)
        account_curr = st.selectbox("Account Deposit Currency", ["USD", "BHD", "PHP"])

        # Pip value math
        if "JPY" in pair_select:
            pip_size = 0.01
            contract_size = 100000
        elif "XAU" in pair_select:
            pip_size = 0.10
            contract_size = 100
        elif "PHP" in pair_select:
            pip_size = 0.01
            contract_size = 100000
        else:
            pip_size = 0.0001
            contract_size = 100000

        pip_value_usd = lot_size * contract_size * pip_size
        if account_curr == "BHD":
            pip_val_disp = pip_value_usd / bhd_to_usd if bhd_to_usd > 0 else 0.0
            st.success(f"**Pip Value:** BD {pip_val_disp:.4f} BHD per Pip")
        elif account_curr == "PHP":
            pip_val_disp = (pip_value_usd / bhd_to_usd) * bhd_to_php if bhd_to_usd > 0 else 0.0
            st.success(f"**Pip Value:** ₱ {pip_val_disp:.2f} PHP per Pip")
        else:
            st.success(f"**Pip Value:** ${pip_value_usd:.2f} USD per Pip")

    with col_pip2:
        st.markdown("#### 🛡️ Required Margin Calculator")
        leverage = st.selectbox("Leverage Ratio", [100, 200, 400, 500, 1000], index=3)
        entry_price = st.number_input("Asset Price", min_value=0.0001, value=2650.0 if "XAU" in pair_select else (58.5 if "PHP" in pair_select else 1.0850), step=0.0001)

        req_margin_usd = (lot_size * contract_size * entry_price) / leverage
        if account_curr == "BHD":
            margin_disp = req_margin_usd / bhd_to_usd if bhd_to_usd > 0 else 0.0
            st.info(f"**Required Margin:** BD {margin_disp:,.2f} BHD")
        elif account_curr == "PHP":
            margin_disp = (req_margin_usd / bhd_to_usd) * bhd_to_php if bhd_to_usd > 0 else 0.0
            st.info(f"**Required Margin:** ₱ {margin_disp:,.2f} PHP")
        else:
            st.info(f"**Required Margin:** ${req_margin_usd:,.2f} USD")

# TAB 6: DOWNLOAD REPORTS
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
- 100% Priority Payments : BD {actual_priority_bhd:,.2f}
- Debts & Credits        : BD {actual_debts_bhd:,.2f}
- Needs ({needs_pct}% Target)     : BD {actual_needs_bhd:,.2f}
- Wants ({wants_pct}% Target)     : BD {actual_wants_bhd:,.2f}
- Savings ({savings_pct}% Target) : BD {actual_savings_bhd:,.2f}
--------------------------------------------------
GRAND TOTAL EXPENSES PAID: BD {total_spent_bhd:,.2f}
TOTAL BILLED / PLANNED   : BD {total_billed_bhd:,.2f}
TOTAL REMAINING PENDING  : BD {total_pending_bhd:,.2f}
NET CASH REMAINING       : BD {remaining_cash_bhd:,.2f}
==================================================
"""
        st.download_button(label="📥 Download Executive Summary (.TXT)", data=report_content, file_name=f"financial_summary_{current_user.lower().replace(' ', '_')}.txt", mime="text/plain", use_container_width=True)

# TAB 7: GUIDE & SECRETS
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
