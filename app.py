import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import os
import json

st.set_page_config(
    page_title="Rogee Financial Command Center",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling with Dark Mode Adaptive Contrast & Table Highlights
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

# --- LOGIN SECURITY GATE ---
if "authenticated_user" not in st.session_state:
    st.session_state["authenticated_user"] = None

if st.session_state["authenticated_user"] is None:
    st.markdown("<div class='main-header'>🔒 Private Financial Portal</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Please select your user profile and enter your secret passcode to access your personal dashboard.</div>", unsafe_allow_html=True)
    
    col_l1, col_l2 = st.columns([1, 1])
    with col_l1:
        selected_user = st.selectbox("👤 Select User Profile", list(USER_PROFILES.keys()), index=0)
        prof_info = USER_PROFILES[selected_user]
        
        # Check Streamlit Secrets or Fallback
        correct_passkey = prof_info["def_key"]
        try:
            if prof_info["sec_key"] in st.secrets:
                correct_passkey = str(st.secrets[prof_info["sec_key"]])
        except Exception:
            pass

        passkey_input = st.text_input("🔑 Enter Secret Passcode", type="password")
        
        if st.button("🔓 Unlock Financial Dashboard", type="primary", use_container_width=True):
            if passkey_input == correct_passkey:
                st.session_state["authenticated_user"] = selected_user
                st.success(f"Welcome back, {selected_user}! Access granted.")
                st.rerun()
            else:
                st.error("Incorrect passcode! Please try again.")

    with col_l2:
        st.info(f"""
        ### 💡 Authentication Help:
        - **Default Passcode for {selected_user}:** `{prof_info['def_key']}`
        - **Data Privacy:** Each profile maintains an isolated ledger and settings file.
        - **Passcode Customization:** Passcodes can be customized via Streamlit Secrets (`{prof_info['sec_key']}`).
        """)
    
    st.stop()

# Set current active user
current_user = st.session_state["authenticated_user"]
USER_CONFIG = USER_PROFILES[current_user]

DATA_FILE = USER_CONFIG["data_file"]
CONFIG_FILE = USER_CONFIG["config_file"]
INVEST_FILE = USER_CONFIG["invest_file"]

# --- LOAD/SAVE CONFIG & DATA ---
def load_config():
    default_cfg = {
        "bhd_to_php": 155.50,
        "bhd_to_usd": 2.65,
        "salary_bhd": 500.0,
        "business_bhd": 0.0,
        "sidelines_bhd": 0.0,
        "other_income_bhd": 0.0,
        "debts_pct": 20,
        "needs_pct": 40,
        "wants_pct": 20,
        "savings_pct": 20,
        "currency_pref": "BHD"
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                default_cfg.update(data)
        except Exception:
            pass
    return default_cfg

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=4)

cfg = load_config()

def load_data():
    cols = [
        "Item #", "Date", "Main Category", "Sub Category", "Merchant/Description", 
        "Billed Amount", "Actual Paid", "Currency", "Pending Due", "% Paid", "% Remaining", 
        "Equivalent", "Status", "Payment Method"
    ]
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            # Ensure mandatory columns exist
            for col in cols:
                if col not in df.columns:
                    if col == "Billed Amount" and "Amount" in df.columns:
                        df["Billed Amount"] = df["Amount"]
                    elif col == "Actual Paid" and "Amount" in df.columns:
                        df["Actual Paid"] = df["Amount"]
                    elif col == "Currency":
                        df["Currency"] = "BHD"
                    elif col == "Status":
                        df["Status"] = "Paid"
                    else:
                        df[col] = 0.0 if "Amount" in col or "Due" in col or "%" in col else ""
            
            df["Date"] = pd.to_datetime(df["Date"]).dt.date
            df["Billed Amount"] = pd.to_numeric(df["Billed Amount"], errors="coerce").fillna(0.0)
            df["Actual Paid"] = pd.to_numeric(df["Actual Paid"], errors="coerce").fillna(0.0)
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=cols)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df_expenses = load_data()

# --- SIDEBAR & SETTINGS ---
st.sidebar.markdown(f"### 👤 Profile: **{current_user}**")
if st.sidebar.button("🔒 Lock Portal / Sign Out"):
    st.session_state["authenticated_user"] = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.title("⚙️ Currency & Income Settings")

bhd_to_php = st.sidebar.number_input("1 BHD to PHP (₱)", min_value=1.0, value=float(cfg["bhd_to_php"]), step=0.5)
bhd_to_usd = st.sidebar.number_input("1 BHD to USD ($)", min_value=0.1, value=float(cfg["bhd_to_usd"]), step=0.01)

st.sidebar.markdown("#### 💵 Monthly Income Streams (BHD)")
salary_bhd = st.sidebar.number_input("Primary Net Salary (BD)", min_value=0.0, value=float(cfg["salary_bhd"]), step=25.0)
business_bhd = st.sidebar.number_input("Business Income (BD)", min_value=0.0, value=float(cfg["business_bhd"]), step=25.0)
sidelines_bhd = st.sidebar.number_input("Sidelines / Freelance (BD)", min_value=0.0, value=float(cfg["sidelines_bhd"]), step=25.0)
other_income_bhd = st.sidebar.number_input("Other Income / Allowance (BD)", min_value=0.0, value=float(cfg["other_income_bhd"]), step=25.0)

total_income_bhd = float(salary_bhd + business_bhd + sidelines_bhd + other_income_bhd)
total_income_php = total_income_bhd * bhd_to_php
total_income_usd = total_income_bhd * bhd_to_usd

st.sidebar.markdown(f"""
<div class="income-card">
    <b>💰 TOTAL COMBINED MONTHLY INCOME:</b><br/>
    <span style="font-size:1.15rem; font-weight:800;">BD {total_income_bhd:,.2f}</span><br/>
    <span style="font-size:0.85rem;">₱{total_income_php:,.2f} | ${total_income_usd:,.2f}</span>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Category Allocation Targets (%)")
debts_pct = st.sidebar.slider("1. Debts & Credits Target %", 0, 100, int(cfg.get("debts_pct", 20)))
needs_pct = st.sidebar.slider("2. Essential Needs Target %", 0, 100, int(cfg.get("needs_pct", 40)))
wants_pct = st.sidebar.slider("3. Lifestyle Wants Target %", 0, 100, int(cfg.get("wants_pct", 20)))
savings_pct = st.sidebar.slider("4. Savings & Investments Target %", 0, 100, int(cfg.get("savings_pct", 20)))

tot_alloc = debts_pct + needs_pct + wants_pct + savings_pct
if tot_alloc != 100:
    st.sidebar.warning(f"⚠️ Allocation total is {tot_alloc}%. It should equal 100%.")

currency_pref = st.sidebar.selectbox("Active Currency Symbol", ["BHD", "PHP", "USD"], index=["BHD", "PHP", "USD"].index(cfg.get("currency_pref", "BHD")))

# Save config updates
new_cfg = {
    "bhd_to_php": bhd_to_php,
    "bhd_to_usd": bhd_to_usd,
    "salary_bhd": salary_bhd,
    "business_bhd": business_bhd,
    "sidelines_bhd": sidelines_bhd,
    "other_income_bhd": other_income_bhd,
    "debts_pct": debts_pct,
    "needs_pct": needs_pct,
    "wants_pct": wants_pct,
    "savings_pct": savings_pct,
    "currency_pref": currency_pref
}
save_config(new_cfg)

# Rates conversion helpers
rate_mult = 1.0 if currency_pref == "BHD" else (bhd_to_php if currency_pref == "PHP" else bhd_to_usd)
curr_symbol = "BD " if currency_pref == "BHD" else ("₱" if currency_pref == "PHP" else "$")

# --- MAIN APP HEADER & TIMES ---
now_utc = datetime.now(timezone.utc)
bh_time = now_utc + timedelta(hours=3)
ph_time = now_utc + timedelta(hours=8)

st.markdown('<div class="main-header">Rogee Financial Command Center</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multi-Currency Personal Finance & 12-Month Projected Budgeting Engine</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="time-badge">
    Location Clocks: Bahrain: {bh_time.strftime("%d %b %Y, %I:%M %p")} AST &nbsp;|&nbsp; 
    Philippines: {ph_time.strftime("%d %b %Y, %I:%M %p")} PHT &nbsp;|&nbsp; 
    Account Profile: <b>{current_user}</b>
</div>
""", unsafe_allow_html=True)

# Calculate spending totals
if not df_expenses.empty:
    df_expenses["Billed Amount"] = pd.to_numeric(df_expenses["Billed Amount"], errors="coerce").fillna(0.0)
    df_expenses["Actual Paid"] = pd.to_numeric(df_expenses["Actual Paid"], errors="coerce").fillna(0.0)
    
    total_billed_bhd = float(df_expenses["Billed Amount"].sum())
    total_paid_bhd = float(df_expenses["Actual Paid"].sum())
    total_pending_bhd = max(0.0, total_billed_bhd - total_paid_bhd)
else:
    total_billed_bhd = 0.0
    total_paid_bhd = 0.0
    total_pending_bhd = 0.0

remaining_cash_bhd = total_income_bhd - total_paid_bhd

# Overage / Net Balance Alert Banner
if remaining_cash_bhd < 0:
    over_bhd = abs(remaining_cash_bhd)
    st.markdown(f"""
    <div class="priority-banner">
        ⚠️ <b>OVER BUDGET ALERT:</b> Payments exceed total income by 
        <b>BD {over_bhd:,.2f}</b> (₱{over_bhd*bhd_to_php:,.2f} | ${over_bhd*bhd_to_usd:,.2f})!
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="income-card">
        ✅ <b>NET CASH REMAINING UNSPENT:</b> 
        <b>BD {remaining_cash_bhd:,.2f}</b> (₱{remaining_cash_bhd*bhd_to_php:,.2f} | ${remaining_cash_bhd*bhd_to_usd:,.2f})
    </div>
    """, unsafe_allow_html=True)

# --- APP TABS ---
tab_dash, tab_add, tab_history, tab_proj, tab_mt5, tab_reports, tab_guide = st.tabs([
    "📊 Dashboard & Analytics", 
    "➕ Record Expense / Payment", 
    "📜 Transaction History", 
    "🔮 12-Month Projections",
    "📈 MT5 Pip & Margin Calc",
    "📥 Download Reports",
    "📘 Security Guide"
])

# --- TAB 1: DASHBOARD ---
with tab_dash:
    st.subheader("📊 Financial Overview & Spending Analytics")
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Monthly Net Income", f"{curr_symbol}{total_income_bhd*rate_mult:,.2f}", delta=f"BD {total_income_bhd:,.2f}")
    col_m2.metric("Total Expenses Billed", f"{curr_symbol}{total_billed_bhd*rate_mult:,.2f}", delta=f"BD {total_billed_bhd:,.2f}")
    col_m3.metric("Total Paid to Date", f"{curr_symbol}{total_paid_bhd*rate_mult:,.2f}", delta=f"-BD {total_paid_bhd:,.2f}", delta_color="inverse")
    
    if remaining_cash_bhd >= 0:
        col_m4.metric("Remaining Unspent Cash", f"{curr_symbol}{remaining_cash_bhd*rate_mult:,.2f}", delta=f"BD {remaining_cash_bhd:,.2f}")
    else:
        col_m4.metric("Over Budget Deficit", f"{curr_symbol}{remaining_cash_bhd*rate_mult:,.2f}", delta=f"-BD {abs(remaining_cash_bhd):,.2f}", delta_color="inverse")

    st.markdown("---")
    
    framework_title = f"{debts_pct}/{needs_pct}/{wants_pct}/{savings_pct} Category Framework Allocation"
    st.subheader(f"🎯 {framework_title}")
    
    # Target calculations
    target_debts = total_income_bhd * (debts_pct / 100.0)
    target_needs = total_income_bhd * (needs_pct / 100.0)
    target_wants = total_income_bhd * (wants_pct / 100.0)
    target_savings = total_income_bhd * (savings_pct / 100.0)

    # Actual spending per category
    def get_cat_spent(cat_name):
        if df_expenses.empty: return 0.0
        sub = df_expenses[df_expenses["Main Category"].str.contains(cat_name, case=False, na=False)]
        return float(sub["Actual Paid"].sum())

    act_priority = get_cat_spent("100% Priority")
    act_debts = get_cat_spent("Debts")
    act_needs = get_cat_spent("Needs")
    act_wants = get_cat_spent("Wants")
    act_savings = get_cat_spent("Savings")

    summary_rows = [
        {"Category": "Mandatory 100% Payments", "Target %": "100% Priority", "Target (BD)": act_priority, "Actual Paid (BD)": act_priority, "Status": "Mandatory Paid"},
        {"Category": "Debts & Credits", "Target %": f"{debts_pct}%", "Target (BD)": target_debts, "Actual Paid (BD)": act_debts, "Status": "On Track" if act_debts <= target_debts else "Over Target"},
        {"Category": "Essential Needs", "Target %": f"{needs_pct}%", "Target (BD)": target_needs, "Actual Paid (BD)": act_needs, "Status": "On Track" if act_needs <= target_needs else "Over Target"},
        {"Category": "Lifestyle Wants", "Target %": f"{wants_pct}%", "Target (BD)": target_wants, "Actual Paid (BD)": act_wants, "Status": "On Track" if act_wants <= target_wants else "Over Target"},
        {"Category": "Savings & Investments", "Target %": f"{savings_pct}%", "Target (BD)": target_savings, "Actual Paid (BD)": act_savings, "Status": "Goal Met" if act_savings >= target_savings else "Under Goal"}
    ]
    df_cat_summary = pd.DataFrame(summary_rows)
    
    st.dataframe(
        df_cat_summary.style.format({
            "Target (BD)": f"{curr_symbol}{{:,.2f}}",
            "Actual Paid (BD)": f"{curr_symbol}{{:,.2f}}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.subheader("📊 Target vs. Actual Paid (BD)")
        df_chart = pd.DataFrame({
            "Category": ["Debts", "Needs", "Wants", "Savings"],
            "Target": [target_debts, target_needs, target_wants, target_savings],
            "Actual Paid": [act_debts, act_needs, act_wants, act_savings]
        })
        fig_bar = go.Figure(data=[
            go.Bar(name='Target', x=df_chart['Category'], y=df_chart['Target'], marker_color='#93C5FD'),
            go.Bar(name='Actual Paid', x=df_chart['Category'], y=df_chart['Actual Paid'], marker_color='#1D4ED8')
        ])
        fig_bar.update_layout(barmode='group', margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_c2:
        st.subheader("🍰 Expense Distribution Share")
        if total_paid_bhd > 0:
            fig_pie = px.pie(
                values=[act_priority, act_debts, act_needs, act_wants, act_savings],
                names=["100% Priority", "Debts & Credits", "Needs", "Wants", "Savings"],
                hole=0.4
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No recorded expense transactions logged yet.")

# --- TAB 2: RECORD EXPENSE ---
with tab_add:
    st.subheader("➕ Record a New Expense or Payment")
    
    col_a, col_b = st.columns(2)
    with col_a:
        exp_date = st.date_input("Transaction Date", value=datetime.today())
        main_cat = st.selectbox("Main Category", [
            "100% Priority & People to Pay",
            f"Debts & Credits ({debts_pct}%)",
            f"Needs ({needs_pct}%)",
            f"Wants ({wants_pct}%)",
            f"Savings & Investments ({savings_pct}%)"
        ], key="record_main_cat")
        
        # Real-time subcategory options based on selection
        if "Priority" in main_cat:
            sub_cats = ["Family Allowance / Remittance", "House Rent", "Critical Utility Bills", "Urgent Debt Payment"]
        elif "Debts" in main_cat:
            sub_cats = ["Credit Card Payment", "Personal Bank Loan", "Car Loan", "Housing Mortgage", "Borrowed Money / Friend"]
        elif "Needs" in main_cat:
            sub_cats = ["Groceries & Supermarket", "Electricity & Water", "Mobile & Wifi Internet", "Transportation & Petrol", "Medical & Insurance"]
        elif "Wants" in main_cat:
            sub_cats = ["Dining Out & Fast Food", "Shopping & Clothes", "Entertainment & Outings", "Gadgets & Electronics", "Subscriptions"]
        else:
            sub_cats = ["Emergency Fund Deposit", "COL Financial Stock Investment", "MT5 Trading Capital Deposit", "Gold & Savings Account"]

        sub_cat = st.selectbox("Sub-Category", sub_cats)

    with col_b:
        merchant = st.text_input("Merchant / Description", placeholder="e.g. BenefitPay to Landlord, Hypermarket")
        
        col_amt1, col_amt2 = st.columns(2)
        with col_amt1:
            billed_amount = st.number_input("Billed / Planned Amount", min_value=0.01, value=50.0, step=5.0)
        with col_amt2:
            pay_curr = st.selectbox("Transaction Currency", ["BHD", "PHP", "USD"], index=0)

        pay_status = st.selectbox("Payment Status", ["Paid", "Pending Payment", "Partially Paid"], index=0)
        
        default_actual = billed_amount if pay_status == "Paid" else (0.0 if pay_status == "Pending Payment" else billed_amount * 0.5)
        actual_paid = st.number_input("Actual Amount Paid", min_value=0.0, value=float(default_actual), step=5.0)
        payment_method = st.selectbox("Payment Method", ["Benefit Pay", "Remittance", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])

    if st.button("💾 Save Transaction Entry", type="primary", use_container_width=True):
        # Convert currency to BHD for storage
        if pay_curr == "PHP":
            billed_bhd = billed_amount / bhd_to_php
            paid_bhd = actual_paid / bhd_to_php
        elif pay_curr == "USD":
            billed_bhd = billed_amount / bhd_to_usd
            paid_bhd = actual_paid / bhd_to_usd
        else:
            billed_bhd = billed_amount
            paid_bhd = actual_paid

        item_num = len(df_expenses) + 1
        
        new_row = pd.DataFrame([{
            "Item #": item_num,
            "Date": exp_date,
            "Main Category": main_cat,
            "Sub Category": sub_cat,
            "Merchant/Description": merchant if merchant else sub_cat,
            "Billed Amount": billed_bhd,
            "Actual Paid": paid_bhd,
            "Currency": pay_curr,
            "Pending Due": max(0.0, billed_bhd - paid_bhd),
            "% Paid": round((paid_bhd / billed_bhd * 100), 1) if billed_bhd > 0 else 0.0,
            "% Remaining": round((100.0 - (paid_bhd / billed_bhd * 100)), 1) if billed_bhd > 0 else 0.0,
            "Equivalent": f"BD {billed_bhd:,.2f} | ₱{billed_bhd*bhd_to_php:,.2f} | ${billed_bhd*bhd_to_usd:,.2f}",
            "Status": pay_status,
            "Payment Method": payment_method
        }])
        
        df_expenses = pd.concat([df_expenses, new_row], ignore_index=True)
        save_data(df_expenses)
        st.success("Successfully logged transaction!")
        st.rerun()

# --- TAB 3: TRANSACTION HISTORY ---
with tab_history:
    st.subheader(f"📜 Recorded Transaction History ({current_user})")
    
    if not df_expenses.empty:
        # Sorting & Re-indexing
        df_display = df_expenses.copy()
        df_display["Date"] = pd.to_datetime(df_display["Date"]).dt.date
        df_display = df_display.sort_values(by=["Main Category", "Date"], ascending=[True, True]).reset_index(drop=True)
        df_display["Item #"] = range(1, len(df_display) + 1)

        # Dynamic Recalculations
        df_display["Billed Amount"] = pd.to_numeric(df_display["Billed Amount"], errors="coerce").fillna(0.0)
        df_display["Actual Paid"] = pd.to_numeric(df_display["Actual Paid"], errors="coerce").fillna(0.0)
        df_display["Pending Due"] = (df_display["Billed Amount"] - df_display["Actual Paid"]).clip(lower=0.0)
        
        pct_paid_series = (df_display["Actual Paid"] / df_display["Billed Amount"] * 100.0).fillna(0.0).round(1)
        df_display["% Paid"] = pct_paid_series
        df_display["% Remaining"] = (100.0 - pct_paid_series).clip(lower=0.0).round(1)

        # Auto-update status based on % Paid
        def auto_status(row):
            p = row["% Paid"]
            if p >= 99.9: return "Paid"
            elif p <= 0.1: return "Not Paid"
            else: return "Partially Paid"

        df_display["Status"] = df_display.apply(auto_status, axis=1)

        # Update Equivalent strings
        df_display["Equivalent"] = df_display["Billed Amount"].apply(
            lambda x: f"BD {x:,.2f} (₱{x*bhd_to_php:,.2f} | ${x*bhd_to_usd:,.2f})"
        )

        st.caption("✏️ **Double-click any cell** to modify records. Row colors indicate status: 🟢 Green = Paid (100%), 🟡 Yellow = Partially Paid, 🔴 Red = Unpaid (0%).")

        # Color Styling Function for Table View
        def style_status_row(row):
            stat = str(row.get("Status", ""))
            pct = float(row.get("% Paid", 0))
            if stat == "Paid" or pct >= 99.9:
                return ["background-color: #D1FAE5; color: #065F46; font-weight: 600;"] * len(row)
            elif stat == "Partially Paid" or (0.1 < pct < 99.9):
                return ["background-color: #FEF3C7; color: #92400E; font-weight: 600;"] * len(row)
            else:
                return ["background-color: #FEE2E2; color: #991B1B; font-weight: 600;"] * len(row)

        st.markdown("#### 🎨 Color-Highlighted Ledger View")
        st.dataframe(
            df_display.style.apply(style_status_row, axis=1).format({
                "Billed Amount": "BD {:,.2f}",
                "Actual Paid": "BD {:,.2f}",
                "Pending Due": "BD {:,.2f}",
                "% Paid": "{:.1f}%",
                "% Remaining": "{:.1f}%"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        st.markdown("#### ✏️ Interactive Data Editor (Modify & Save)")
        
        edited_df = st.data_editor(
            df_display,
            num_rows="dynamic",
            use_container_width=True,
            key=f"data_editor_{current_user}"
        )

        col_h1, col_h2 = st.columns(2)
        with col_h1:
            if st.button("💾 Save Ledger Changes", type="primary", use_container_width=True):
                save_data(edited_df)
                st.success("Ledger updated successfully!")
                st.rerun()
        with col_h2:
            if st.button("🗑️ Clear Entire History", use_container_width=True):
                if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
                st.success("All transaction logs cleared!")
                st.rerun()

        # --- BOTTOM SUMMARY LEDGER ---
        st.markdown("---")
        st.subheader("💰 Total Outstanding & Payment Ledger Summary")

        tot_billed = float(df_display["Billed Amount"].sum())
        tot_paid = float(df_display["Actual Paid"].sum())
        tot_pending = float(df_display["Pending Due"].sum())

        # PHP Specific records
        df_php = df_display[df_display["Currency"] == "PHP"]
        tot_php_billed = float(df_php["Billed Amount"].sum() * bhd_to_php) if not df_php.empty else 0.0
        tot_php_paid = float(df_php["Actual Paid"].sum() * bhd_to_php) if not df_php.empty else 0.0
        tot_php_pending = float(df_php["Pending Due"].sum() * bhd_to_php) if not df_php.empty else 0.0

        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.markdown(f"""
            <div class="rate-card">
                <b>📋 TOTAL BILLED / NEEDED TO PAY:</b><br/>
                <span style="font-size:1.2rem; font-weight:800;">BD {tot_billed:,.2f}</span><br/>
                <span>₱{tot_billed*bhd_to_php:,.2f} | ${tot_billed*bhd_to_usd:,.2f}</span><br/><hr style="margin:4px 0;"/>
                <b>🇵🇭 PHP Specific Records:</b><br/>
                <b>₱{tot_php_billed:,.2f}</b> (BD {tot_php_billed/bhd_to_php:,.2f})
            </div>
            """, unsafe_allow_html=True)

        with col_s2:
            st.markdown(f"""
            <div class="income-card">
                <b>🟢 TOTAL ACTUAL AMOUNT PAID:</b><br/>
                <span style="font-size:1.2rem; font-weight:800;">BD {tot_paid:,.2f}</span><br/>
                <span>₱{tot_paid*bhd_to_php:,.2f} | ${tot_paid*bhd_to_usd:,.2f}</span><br/><hr style="margin:4px 0;"/>
                <b>🇵🇭 PHP Specific Paid:</b><br/>
                <b>₱{tot_php_paid:,.2f}</b> (BD {tot_php_paid/bhd_to_php:,.2f})
            </div>
            """, unsafe_allow_html=True)

        with col_s3:
            st.markdown(f"""
            <div class="priority-banner">
                <b>🔴 TOTAL REMAINING PENDING DUE:</b><br/>
                <span style="font-size:1.2rem; font-weight:800;">BD {tot_pending:,.2f}</span><br/>
                <span>₱{tot_pending*bhd_to_php:,.2f} | ${tot_pending*bhd_to_usd:,.2f}</span><br/><hr style="margin:4px 0;"/>
                <b>🇵🇭 PHP Specific Unpaid:</b><br/>
                <b>₱{tot_php_pending:,.2f}</b> (BD {tot_php_pending/bhd_to_php:,.2f})
            </div>
            """, unsafe_allow_html=True)

    else:
        st.info("No recorded transaction history found. Add your first payment in the 'Record Expense' tab!")

# --- TAB 4: 12-MONTH PROJECTIONS ---
with tab_proj:
    st.subheader("🔮 12-Month & Yearly Projected Budgeting Engine")
    st.markdown("Simulate your future detailed expenses, income growth, inflation impact, and cumulative wealth accumulation over the next 12 months.")

    col_pr1, col_pr2 = st.columns(2)
    with col_pr1:
        base_proj_income = st.number_input("Starting Monthly Projected Income (BD)", min_value=0.0, value=float(total_income_bhd), step=50.0)
        annual_growth_rate = st.slider("Expected Annual Income Growth / Raise (%)", 0.0, 25.0, 5.0, 0.5)
        proj_fixed_needs = st.number_input("Projected Fixed Needs & Commitments (BD/mo)", min_value=0.0, value=float(total_billed_bhd if total_billed_bhd > 0 else total_income_bhd*0.5), step=25.0)

    with col_pr2:
        inflation_rate = st.slider("Estimated Annual Inflation Rate (%)", 0.0, 15.0, 3.0, 0.5)
        proj_wants = st.number_input("Projected Lifestyle Allowance (BD/mo)", min_value=0.0, value=float(total_income_bhd*0.2), step=25.0)
        target_monthly_savings = st.number_input("Monthly Target Savings (BD/mo)", min_value=0.0, value=float(total_income_bhd*0.2), step=25.0)

    # Calculate 12-month projections table
    months = [f"Month {i}" for i in range(1, 13)]
    proj_data = []
    cumulative_savings = 0.0

    for i in range(12):
        # Monthly income with growth
        m_income = base_proj_income * ((1 + (annual_growth_rate / 100.0) / 12) ** i)
        # Monthly needs adjusted for inflation
        m_needs = proj_fixed_needs * ((1 + (inflation_rate / 100.0) / 12) ** i)
        m_wants = proj_wants
        m_exp = m_needs + m_wants
        m_surplus = m_income - m_exp
        cumulative_savings += m_surplus

        proj_data.append({
            "Month": months[i],
            "Projected Income (BD)": round(m_income, 2),
            "Projected Needs (BD)": round(m_needs, 2),
            "Lifestyle Wants (BD)": round(m_wants, 2),
            "Total Expenses (BD)": round(m_exp, 2),
            "Monthly Surplus (BD)": round(m_surplus, 2),
            "Cumulative Savings (BD)": round(cumulative_savings, 2)
        })

    df_proj = pd.DataFrame(proj_data)

    tot_1yr_income = float(df_proj["Projected Income (BD)"].sum())
    tot_1yr_exp = float(df_proj["Total Expenses (BD)"].sum())
    tot_1yr_savings = float(df_proj["Monthly Surplus (BD)"].sum())

    st.markdown("---")
    col_p1, col_p2, col_p3 = st.columns(3)
    col_p1.metric("1-Year Total Income", f"BD {tot_1yr_income:,.2f}", delta=f"₱{tot_1yr_income*bhd_to_php:,.2f}")
    col_p2.metric("1-Year Total Expenses", f"BD {tot_1yr_exp:,.2f}", delta=f"-₱{tot_1yr_exp*bhd_to_php:,.2f}", delta_color="inverse")
    col_p3.metric("1-Year Net Savings Potential", f"BD {tot_1yr_savings:,.2f}", delta=f"₱{tot_1yr_savings*bhd_to_php:,.2f}")

    st.markdown("---")
    st.markdown("#### 📅 12-Month Detailed Projections Table")
    st.dataframe(
        df_proj.style.format({
            "Projected Income (BD)": "BD {:,.2f}",
            "Projected Needs (BD)": "BD {:,.2f}",
            "Lifestyle Wants (BD)": "BD {:,.2f}",
            "Total Expenses (BD)": "BD {:,.2f}",
            "Monthly Surplus (BD)": "BD {:,.2f}",
            "Cumulative Savings (BD)": "BD {:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    col_pg1, col_pg2 = st.columns(2)
    with col_pg1:
        st.subheader("📊 Projected Income vs. Expenses (12 Months)")
        fig_proj = go.Figure(data=[
            go.Bar(name="Projected Income", x=df_proj["Month"], y=df_proj["Projected Income (BD)"], marker_color="#22C55E"),
            go.Bar(name="Total Expenses", x=df_proj["Month"], y=df_proj["Total Expenses (BD)"], marker_color="#EF4444")
        ])
        fig_proj.update_layout(barmode="group", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_proj, use_container_width=True)

    with col_pg2:
        st.subheader("📈 Cumulative Wealth Growth Trend")
        fig_line = px.line(
            df_proj, x="Month", y="Cumulative Savings (BD)", 
            title="Estimated Wealth & Reserve Growth",
            markers=True
        )
        fig_line.update_traces(line_color="#3B82F6", line_width=3)
        st.plotly_chart(fig_line, use_container_width=True)

# --- TAB 5: MT5 PIP & MARGIN CALCULATOR ---
with tab_mt5:
    st.subheader("📈 MT5 Pip Value & Required Margin Calculator")
    st.markdown("Calculate exact pip values and required margin for Forex, Gold, and major currency pairs across USD, BHD, and PHP account currencies.")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        pair = st.selectbox("Select Currency Pair", [
            "USDPHP", "BHDPHP", "USDCAD", "EURUSD", "GBPUSD", "USDJPY", 
            "XAUUSD", "USDCHF", "AUDUSD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"
        ])
        lot_size = st.number_input("Lot Volume (Lots)", min_value=0.01, value=1.0, step=0.1)
        account_currency = st.selectbox("Account Currency", ["USD", "BHD", "PHP"])

    with col_m2:
        leverage = st.selectbox("Account Leverage", [100, 200, 400, 500, 1000], index=3)
        entry_price = st.number_input("Current Instrument Price", min_value=0.0001, value=58.50 if "PHP" in pair else (2750.0 if "XAU" in pair else 1.0850), step=0.01)

    # Pip value calculation logic
    if "XAU" in pair:
        pip_unit = 0.01
        contract_size = 100
    elif "JPY" in pair or "PHP" in pair:
        pip_unit = 0.01
        contract_size = 100000
    else:
        pip_unit = 0.0001
        contract_size = 100000

    raw_pip_usd = (pip_unit / entry_price) * (lot_size * contract_size) if entry_price > 0 else 0.0
    
    if account_currency == "BHD":
        pip_val_disp = raw_pip_usd / bhd_to_usd
        sym_m = "BD "
    elif account_currency == "PHP":
        pip_val_disp = raw_pip_usd * (bhd_to_php / bhd_to_usd)
        sym_m = "₱"
    else:
        pip_val_disp = raw_pip_usd
        sym_m = "$"

    margin_usd = (lot_size * contract_size * entry_price) / leverage
    if account_currency == "BHD":
        margin_disp = margin_usd / bhd_to_usd
    elif account_currency == "PHP":
        margin_disp = margin_usd * (bhd_to_php / bhd_to_usd)
    else:
        margin_disp = margin_usd

    st.markdown("---")
    col_res1, col_res2 = st.columns(2)
    col_res1.metric(f"Exact Pip Value per 1 Pip ({pair})", f"{sym_m}{pip_val_disp:,.2f}")
    col_res2.metric(f"Required Margin (Leverage 1:{leverage})", f"{sym_m}{margin_disp:,.2f}")

# --- TAB 6: DOWNLOAD REPORTS ---
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
        report_content = f"""
==================================================
ROGEE FINANCIAL COMMAND CENTER - EXECUTIVE REPORT
==================================================
User Profile   : {current_user}
Report Date    : {rep_date}
Bahrain Time   : {bh_time.strftime("%Y-%m-%d %I:%M %p")}
Philippine Time: {ph_time.strftime("%Y-%m-%d %I:%M %p")}
Exchange Rate  : 1 BHD = {bhd_to_php:,.2f} PHP = ${bhd_to_usd:,.2f} USD
Framework      : {debts_pct}/{needs_pct}/{wants_pct}/{savings_pct}

--------------------------------------------------
1. INCOME & CASH BALANCE SUMMARY
--------------------------------------------------
- Primary Salary         : BD {salary_bhd:,.2f}
- Business Income        : BD {business_bhd:,.2f}
- Sidelines / Freelance  : BD {sidelines_bhd:,.2f}
- Other Income           : BD {other_income_bhd:,.2f}
--------------------------------------------------
TOTAL COMBINED INCOME    : BD {total_income_bhd:,.2f}
   - Equivalent in PHP   : PHP {total_income_php:,.2f}
   - Equivalent in USD   : USD ${total_income_usd:,.2f}

--------------------------------------------------
2. EXPENSES & PAYMENT STATUS
--------------------------------------------------
- Total Billed / Planned : BD {total_billed_bhd:,.2f}
- Total Actual Paid      : BD {total_paid_bhd:,.2f}
- Total Pending Due      : BD {total_pending_bhd:,.2f}
--------------------------------------------------
NET REMAINING CASH       : BD {remaining_cash_bhd:,.2f}
==================================================
"""
        st.download_button(label="📥 Download Executive Summary (.TXT)", data=report_content, file_name=f"financial_summary_{current_user.lower().replace(' ', '_')}.txt", mime="text/plain", use_container_width=True)

# --- TAB 7: SECURITY GUIDE ---
with tab_guide:
    st.subheader("📘 Security & Configuration Guide")
    st.markdown("""
    ### 🔐 Security Login Portal
    * **User Profiles**: Rogee, User 2, User 3, User 4.
    * **Default Passkeys**: `rogee2026`, `user2026`, `user32026`, `user42026`.
    * **Custom Passkeys**: Set private passkeys via Streamlit Secrets (`ROGEE_KEY`, `USER2_KEY`, etc.).
    * **Data Isolation**: Each user profile writes to its own isolated CSV and JSON files (`expenses_rogee.csv`, `expenses_user2.csv`, etc.).
    """)
