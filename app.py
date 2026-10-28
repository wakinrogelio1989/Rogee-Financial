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

# Custom CSS styling with Dark Mode Adaptive Contrast & Status Color Rules
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
        "def_key": "user2026",
        "data_file": "expenses_user3.csv",
        "config_file": "config_user3.json",
        "invest_file": "investments_user3.csv"
    },
    "User 4": {
        "sec_key": "USER4_KEY",
        "def_key": "user2026",
        "data_file": "expenses_user4.csv",
        "config_file": "config_user4.json",
        "invest_file": "investments_user4.csv"
    }
}

# Login Gate
st.sidebar.title("🔐 User Account Login")
current_user = st.sidebar.selectbox("Select Profile", list(USER_PROFILES.keys()), index=0)
user_info = USER_PROFILES[current_user]

secret_passkey = st.secrets.get(user_info["sec_key"], user_info["def_key"])
entered_key = st.sidebar.text_input(f"Passkey for {current_user}", type="password", value=secret_passkey)

if entered_key != secret_passkey:
    st.error(f"Invalid Passkey for {current_user}. Please enter the correct password.")
    st.stop()

DATA_FILE = user_info["data_file"]
CONFIG_FILE = user_info["config_file"]
INVEST_FILE = user_info["invest_file"]

def load_user_config():
    defaults = {
        "salary_bhd": 1500.0,
        "business_bhd": 0.0,
        "sidelines_bhd": 0.0,
        "other_income_bhd": 0.0,
        "bhd_to_php": 156.25,
        "bhd_to_usd": 2.6525,
        "needs_pct": 45,
        "wants_pct": 20,
        "savings_pct": 20,
        "debts_pct": 15,
        "priority_allocation_bhd": 200.0,
        "curr_symbol": "BD"
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

cfg = load_user_config()

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            if "Date" in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
            
            if "Billed Amount" not in df.columns and "Amount" in df.columns:
                df["Billed Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
            if "Actual Paid" not in df.columns and "Amount" in df.columns:
                df["Actual Paid"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0.0)
            if "Currency" not in df.columns:
                df["Currency"] = "BHD"
            if "Status" not in df.columns:
                df["Status"] = "Paid"
            if "Payment Method" not in df.columns:
                df["Payment Method"] = "Bank Transfer"
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=[
        "Date", "Main Category", "Sub Category", "Merchant/Description",
        "Billed Amount", "Actual Paid", "Currency", "Payment Method"
    ])

def save_data(df, path):
    df.to_csv(path, index=False)

df_expenses = load_data()

# Sidebar: Financial Settings
st.sidebar.markdown("---")
st.sidebar.subheader("💰 Monthly Take-Home Income")

curr_symbol = st.sidebar.selectbox("Display Currency", ["BD", "PHP", "USD"], index=0)
salary_bhd = st.sidebar.number_input("Primary Monthly Salary (BHD)", min_value=0.0, value=float(cfg["salary_bhd"]), step=50.0)
business_bhd = st.sidebar.number_input("Business Income (BHD)", min_value=0.0, value=float(cfg["business_bhd"]), step=20.0)
sidelines_bhd = st.sidebar.number_input("Sidelines / Freelance (BHD)", min_value=0.0, value=float(cfg["sidelines_bhd"]), step=10.0)
other_income_bhd = st.sidebar.number_input("Other Income / Bonuses (BHD)", min_value=0.0, value=float(cfg["other_income_bhd"]), step=10.0)

total_income_bhd = salary_bhd + business_bhd + sidelines_bhd + other_income_bhd

st.sidebar.markdown("---")
st.sidebar.subheader("💱 Exchange Rates")
bhd_to_php = st.sidebar.number_input("1 BHD = PHP (₱)", min_value=1.0, value=float(cfg["bhd_to_php"]), step=0.5)
bhd_to_usd = st.sidebar.number_input("1 BHD = USD ($)", min_value=0.1, value=float(cfg["bhd_to_usd"]), step=0.01)

rate_mult = 1.0 if curr_symbol == "BD" else (bhd_to_php if curr_symbol == "PHP" else bhd_to_usd)
disp_total_income = total_income_bhd * rate_mult

st.sidebar.markdown(
    f'<div class="income-card">'
    f'<div style="font-size:0.8rem; font-weight:700; text-transform:uppercase;">TOTAL COMBINED MONTHLY INCOME</div>'
    f'<div style="font-size:1.3rem; font-weight:800; margin-top:2px;">{curr_symbol} {disp_total_income:,.2f}</div>'
    f'<div style="font-size:0.75rem; margin-top:4px;">BD {total_income_bhd:,.2f} | ₱{(total_income_bhd * bhd_to_php):,.2f} | ${(total_income_bhd * bhd_to_usd):,.2f}</div>'
    f'</div>',
    unsafe_allow_html=True
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ 4-Category Allocation Targets (%)")

priority_allocation_bhd = st.sidebar.number_input("100% Mandatory Priority (BHD)", min_value=0.0, value=float(cfg["priority_allocation_bhd"]), step=20.0)

debts_pct = st.sidebar.slider("Debts & Credits Target %", 0, 100, int(cfg["debts_pct"]))
needs_pct = st.sidebar.slider("Needs Target % (Essentials)", 0, 100, int(cfg["needs_pct"]))
wants_pct = st.sidebar.slider("Wants Target % (Lifestyle)", 0, 100, int(cfg["wants_pct"]))
savings_pct = st.sidebar.slider("Savings & Investments Target %", 0, 100, int(cfg["savings_pct"]))

alloc_sum = debts_pct + needs_pct + wants_pct + savings_pct
if alloc_sum != 100:
    st.sidebar.warning(f"Category Sliders total {alloc_sum}%. Should equal 100%.")

# Save config updates
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
    "debts_pct": debts_pct,
    "priority_allocation_bhd": priority_allocation_bhd,
    "curr_symbol": curr_symbol
}
save_user_config(new_cfg)

# Time calculations
utc_now = datetime.now(timezone.utc)
bh_time = utc_now + timedelta(hours=3)
ph_time = utc_now + timedelta(hours=8)

st.markdown('<div class="main-header">Rogee Financial Command Center</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Personalized Multi-Currency Budgeting, Analytics & Trading Command Center</div>', unsafe_allow_html=True)

st.markdown(
    f'<div class="time-badge">'
    f'Bahrain: {bh_time.strftime("%d %b %Y, %I:%M %p")} AST &nbsp;|&nbsp; '
    f'Philippines: {ph_time.strftime("%d %b %Y, %I:%M %p")} PHT &nbsp;|&nbsp; '
    f'Account: {current_user}'
    f'</div>',
    unsafe_allow_html=True
)

# Main Tabs
tab_dash, tab_add, tab_history, tab_forecast, tab_mt5, tab_invest, tab_reports, tab_guide = st.tabs([
    "📊 Dashboard & Analytics",
    "➕ Record Expense",
    "📜 Transaction History",
    "🔮 12-Month Projections",
    "📈 MT5 & Pip Calculator",
    "📈 Investment Tracker",
    "📥 Download Reports",
    "📘 Guide & Setup"
])

# Normalize currency function
def normalize_to_bhd(row):
    cur = str(row.get("Currency", "BHD")).upper()
    billed = float(row.get("Billed Amount", 0.0))
    paid = float(row.get("Actual Paid", 0.0))
    if cur == "PHP":
        return billed / bhd_to_php, paid / bhd_to_php
    elif cur == "USD":
        return billed / bhd_to_usd, paid / bhd_to_usd
    return billed, paid

if not df_expenses.empty:
    bhd_vals = df_expenses.apply(normalize_to_bhd, axis=1)
    df_expenses["Billed_BHD"] = [v[0] for v in bhd_vals]
    df_expenses["Paid_BHD"] = [v[1] for v in bhd_vals]
else:
    df_expenses["Billed_BHD"] = []
    df_expenses["Paid_BHD"] = []

# Actuals
actual_priority_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("100% Priority", na=False)]["Paid_BHD"].sum()) if not df_expenses.empty else 0.0
actual_debts_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Debts", na=False)]["Paid_BHD"].sum()) if not df_expenses.empty else 0.0
actual_needs_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Needs", na=False)]["Paid_BHD"].sum()) if not df_expenses.empty else 0.0
actual_wants_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Wants", na=False)]["Paid_BHD"].sum()) if not df_expenses.empty else 0.0
actual_savings_bhd = float(df_expenses[df_expenses["Main Category"].str.contains("Savings", na=False)]["Paid_BHD"].sum()) if not df_expenses.empty else 0.0

total_spent_bhd = float(df_expenses["Paid_BHD"].sum()) if not df_expenses.empty else 0.0
total_billed_bhd = float(df_expenses["Billed_BHD"].sum()) if not df_expenses.empty else 0.0
total_pending_bhd = max(0.0, total_billed_bhd - total_spent_bhd)

remaining_cash_bhd = total_income_bhd - total_spent_bhd

# DASHBOARD TAB
with tab_dash:
    if remaining_cash_bhd < 0:
        over_amt = abs(remaining_cash_bhd)
        st.markdown(
            f'<div class="priority-banner">'
            f'⚠️ <b>OVER BUDGET ALERT:</b> Total expenses paid exceed income by <b>BD {over_amt:,.2f}</b> '
            f'(₱{(over_amt * bhd_to_php):,.2f} | ${(over_amt * bhd_to_usd):,.2f}). Please review your spending.'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="income-card">'
            f'🟢 <b>NET INCOME REMAINING SURPLUS:</b> You have <b>BD {remaining_cash_bhd:,.2f}</b> '
            f'(₱{(remaining_cash_bhd * bhd_to_php):,.2f} | ${(remaining_cash_bhd * bhd_to_usd):,.2f}) available.'
            f'</div>',
            unsafe_allow_html=True
        )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Monthly Income", f"{curr_symbol} {(total_income_bhd * rate_mult):,.2f}")
    m2.metric("Total Expenses Paid", f"{curr_symbol} {(total_spent_bhd * rate_mult):,.2f}")
    m3.metric("Total Expenses to be Paid", f"{curr_symbol} {(total_billed_bhd * rate_mult):,.2f}", delta=f"Pending: {curr_symbol} {(total_pending_bhd * rate_mult):,.2f}")
    
    if remaining_cash_bhd >= 0:
        m4.metric("Remaining Net Cash", f"{curr_symbol} {(remaining_cash_bhd * rate_mult):,.2f}")
    else:
        m4.metric("Over Budget Overage", f"-{curr_symbol} {(abs(remaining_cash_bhd) * rate_mult):,.2f}", delta="NEGATIVE BALANCE", delta_color="inverse")

    st.markdown("---")
    framework_title = f"{debts_pct}/{needs_pct}/{wants_pct}/{savings_pct} Budget Framework Breakdown"
    st.subheader(f"📊 {framework_title}")

    avail_after_priority = max(0.0, total_income_bhd - priority_allocation_bhd)
    target_debts_bhd = avail_after_priority * (debts_pct / 100.0)
    target_needs_bhd = avail_after_priority * (needs_pct / 100.0)
    target_wants_bhd = avail_after_priority * (wants_pct / 100.0)
    target_savings_bhd = avail_after_priority * (savings_pct / 100.0)

    cat_data = [
        {"Category": "100% Mandatory Priority", "Target (BHD)": priority_allocation_bhd, "Paid (BHD)": actual_priority_bhd, "Difference (BHD)": priority_allocation_bhd - actual_priority_bhd, "Status": "Paid" if actual_priority_bhd >= priority_allocation_bhd else "Pending"},
        {"Category": f"Debts & Credits ({debts_pct}%)", "Target (BHD)": target_debts_bhd, "Paid (BHD)": actual_debts_bhd, "Difference (BHD)": target_debts_bhd - actual_debts_bhd, "Status": "On Track" if actual_debts_bhd <= target_debts_bhd else "Over Target"},
        {"Category": f"Needs ({needs_pct}%)", "Target (BHD)": target_needs_bhd, "Paid (BHD)": actual_needs_bhd, "Difference (BHD)": target_needs_bhd - actual_needs_bhd, "Status": "On Track" if actual_needs_bhd <= target_needs_bhd else "Over Target"},
        {"Category": f"Wants ({wants_pct}%)", "Target (BHD)": target_wants_bhd, "Paid (BHD)": actual_wants_bhd, "Difference (BHD)": target_wants_bhd - actual_wants_bhd, "Status": "On Track" if actual_wants_bhd <= target_wants_bhd else "Over Target"},
        {"Category": f"Savings ({savings_pct}%)", "Target (BHD)": target_savings_bhd, "Paid (BHD)": actual_savings_bhd, "Difference (BHD)": actual_savings_bhd - target_savings_bhd, "Status": "Goal Met" if actual_savings_bhd >= target_savings_bhd else "Under Goal"}
    ]
    df_cat_summary = pd.DataFrame(cat_data)
    
    st.dataframe(
        df_cat_summary.style.format({
            "Target (BHD)": "BD {:,.2f}",
            "Paid (BHD)": "BD {:,.2f}",
            "Difference (BHD)": "BD {:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Target vs. Actual Payments")
        chart_df = pd.DataFrame({
            "Category": ["Priority", "Debts", "Needs", "Wants", "Savings"],
            "Target": [priority_allocation_bhd, target_debts_bhd, target_needs_bhd, target_wants_bhd, target_savings_bhd],
            "Actual": [actual_priority_bhd, actual_debts_bhd, actual_needs_bhd, actual_wants_bhd, actual_savings_bhd]
        })
        fig_bar = go.Figure(data=[
            go.Bar(name='Target', x=chart_df['Category'], y=chart_df['Target'], marker_color='#93C5FD'),
            go.Bar(name='Actual', x=chart_df['Category'], y=chart_df['Actual'], marker_color='#1D4ED8')
        ])
        fig_bar.update_layout(barmode='group', yaxis_title="Amount (BHD)", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("Actual Payment Distribution")
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

# ADD EXPENSE TAB (WITH INSTANT DYNAMIC SUB-CATEGORY DROPDOWN)
with tab_add:
    st.subheader("➕ Record a New Expense / Payment")

    col_cat1, col_cat2 = st.columns(2)
    with col_cat1:
        main_cat = st.selectbox("Select Main Category", [
            "100% Mandatory Priority & People to Pay",
            f"Debts & Credits ({debts_pct}%)",
            f"Needs ({needs_pct}%)",
            f"Wants ({wants_pct}%)",
            f"Savings & Investments ({savings_pct}%)"
        ], key="record_main_category_select")

    with col_cat2:
        if "Priority" in main_cat:
            sub_cats = ["Family Remittance", "House Rent", "Electricity & Water (EWA)", "Helper / Nanny Salary", "Child Tuition Fee", "Critical Medical"]
        elif "Debts" in main_cat:
            sub_cats = ["Credit Card Minimum", "Credit Card Full", "Bank Personal Loan", "Car Loan", "Housing Mortgage", "Private Loan"]
        elif "Needs" in main_cat:
            sub_cats = ["Groceries & Food", "Mobile & Internet", "Fuel & Transport", "Health & Insurance", "Home Maintenance", "School Supplies"]
        elif "Wants" in main_cat:
            sub_cats = ["Dining Out & Coffee", "Shopping & Apparel", "Streaming & Subscriptions", "Entertainment & Hobbies", "Vacation / Travel", "Miscellaneous"]
        else:
            sub_cats = ["Emergency Reserve", "COL Financial Stocks", "MT5 Forex Deposit", "MP2 Pag-IBIG Savings", "Time Deposit / Mutual Funds"]

        sub_cat = st.selectbox("Select Sub-Category", sub_cats, key="record_sub_category_select")

    with st.form("add_expense_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            exp_date = st.date_input("Transaction Date", value=datetime.today())
            merchant = st.text_input("Merchant / Description", placeholder="e.g. Lulu Hypermarket, Benefit Pay to Family")
            payment_method = st.selectbox("Payment Method", ["Benefit Pay", "Remittance / Exchange", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])
        with col_b:
            exp_currency = st.selectbox("Transaction Currency", ["BHD", "PHP", "USD"], index=0)
            billed_amt = st.number_input(f"Billed Amount ({exp_currency})", min_value=0.01, value=50.0, step=5.0)
            
            pay_status = st.selectbox("Payment Status", ["Paid", "Pending Payment", "Partially Paid"], index=0)
            def_paid = billed_amt if pay_status == "Paid" else (0.0 if pay_status == "Pending Payment" else billed_amt * 0.5)
            actual_paid = st.number_input(f"Actual Amount Paid ({exp_currency})", min_value=0.0, value=def_paid, step=5.0)

        submit_btn = st.form_submit_button("💾 Save Transaction to Ledger", use_container_width=True)

        if submit_btn:
            new_row = pd.DataFrame([{
                "Date": exp_date,
                "Main Category": main_cat,
                "Sub Category": sub_cat,
                "Merchant/Description": merchant if merchant else "Unspecified",
                "Billed Amount": float(billed_amt),
                "Actual Paid": float(actual_paid),
                "Currency": exp_currency,
                "Payment Method": payment_method
            }])
            df_expenses = pd.concat([df_expenses, new_row], ignore_index=True)
            save_data(df_expenses, DATA_FILE)
            st.success(f"Successfully recorded transaction for {exp_currency} {billed_amt:,.2f}!")
            st.rerun()

# TRANSACTION HISTORY TAB
with tab_history:
    st.subheader(f"📜 Recorded Transaction History ({current_user})")

    if not df_expenses.empty:
        df_display = df_expenses.copy()
        
        df_display["Billed Amount"] = pd.to_numeric(df_display["Billed Amount"], errors="coerce").fillna(0.0)
        df_display["Actual Paid"] = pd.to_numeric(df_display["Actual Paid"], errors="coerce").fillna(0.0)
        
        df_display["Pending Due"] = (df_display["Billed Amount"] - df_display["Actual Paid"]).clip(lower=0.0)
        
        df_display["% Paid"] = (df_display["Actual Paid"] / df_display["Billed Amount"].replace(0, 1) * 100).clip(0, 100).round(1)
        df_display["% Remaining"] = (100.0 - df_display["% Paid"]).round(1)
        
        def calc_status(pct):
            if pct >= 100.0: return "Paid"
            elif pct <= 0.0: return "Not Paid"
            else: return "Partially Paid"
            
        df_display["Status"] = df_display["% Paid"].apply(calc_status)

        def make_eq_str(row):
            c = str(row["Currency"]).upper()
            b = float(row["Billed Amount"])
            p = float(row["Actual Paid"])
            if c == "BHD":
                return f"₱{(p*bhd_to_php):,.2f} | ${(p*bhd_to_usd):,.2f}"
            elif c == "PHP":
                bhd = p / bhd_to_php
                return f"BD {bhd:,.2f} | ${(bhd*bhd_to_usd):,.2f}"
            else:
                bhd = p / bhd_to_usd
                return f"BD {bhd:,.2f} | ₱{(bhd*bhd_to_php):,.2f}"

        df_display["Equivalent (BHD / PHP / USD)"] = df_display.apply(make_eq_str, axis=1)

        cat_order = {
            "100% Mandatory Priority": 1,
            "Debts": 2,
            "Needs": 3,
            "Wants": 4,
            "Savings": 5
        }
        def get_cat_rank(cat_str):
            for k, v in cat_order.items():
                if k in str(cat_str): return v
            return 6

        df_display["cat_rank"] = df_display["Main Category"].apply(get_cat_rank)
        df_display = df_display.sort_values(by=["cat_rank", "Date"], ascending=[True, True]).reset_index(drop=True)
        
        df_display["Item #"] = range(1, len(df_display) + 1)

        cols_order = [
            "Item #", "Date", "Main Category", "Sub Category", "Merchant/Description",
            "Billed Amount", "Actual Paid", "Currency", "Pending Due", "% Paid", "% Remaining",
            "Equivalent (BHD / PHP / USD)", "Status", "Payment Method"
        ]
        df_display = df_display[[c for c in cols_order if c in df_display.columns]]

        def style_rows(row):
            status = str(row.get("Status", ""))
            pct_paid = float(row.get("% Paid", 0.0))
            if status == "Paid" or pct_paid >= 100.0:
                return ['background-color: #D1FAE5; color: #065F46; font-weight: 600;'] * len(row)
            elif status == "Partially Paid" or (pct_paid > 0.0 and pct_paid < 100.0):
                return ['background-color: #FEF3C7; color: #92400E; font-weight: 600;'] * len(row)
            else:
                return ['background-color: #FEE2E2; color: #991B1B; font-weight: 600;'] * len(row)

        st.markdown("#### 🎨 Status-Highlighted Transaction View (Green = 100% Paid, Yellow = Partial, Red = Unpaid)")
        
        st.dataframe(
            df_display.style.apply(style_rows, axis=1).format({
                "Billed Amount": "{:,.2f}",
                "Actual Paid": "{:,.2f}",
                "Pending Due": "{:,.2f}",
                "% Paid": "{:.1f}%",
                "% Remaining": "{:.1f}%"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        st.markdown("#### ✏️ Interactive Ledger Editor (Modify Cells & Save Changes)")
        
        edited_df = st.data_editor(
            df_display,
            num_rows="dynamic",
            use_container_width=True,
            key=f"editor_{current_user}",
            disabled=["Item #", "Pending Due", "% Paid", "% Remaining", "Equivalent (BHD / PHP / USD)"]
        )

        if st.button("💾 Save Ledger Changes", type="primary", use_container_width=True):
            save_cols = ["Date", "Main Category", "Sub Category", "Merchant/Description", "Billed Amount", "Actual Paid", "Currency", "Payment Method"]
            save_df = edited_df[[c for c in save_cols if c in edited_df.columns]]
            save_data(save_df, DATA_FILE)
            st.success("Ledger updated and saved successfully!")
            st.rerun()

        st.markdown("---")
        st.subheader("💰 Total Outstanding & Payment Ledger Summary")

        php_rows = df_display[df_display["Currency"] == "PHP"]
        php_billed = float(php_rows["Billed Amount"].sum()) if not php_rows.empty else 0.0
        php_paid = float(php_rows["Actual Paid"].sum()) if not php_rows.empty else 0.0
        php_pending = float(php_rows["Pending Due"].sum()) if not php_rows.empty else 0.0

        bhd_billed_tot = total_billed_bhd
        bhd_paid_tot = total_spent_bhd
        bhd_pending_tot = total_pending_bhd

        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown(
                f'<div class="rate-card">'
                f'<b>📋 TOTAL BILLED / NEEDED TO PAY:</b><br/>'
                f'• <b>PHP Records:</b> ₱{php_billed:,.2f} (BD {php_billed/bhd_to_php:,.2f})<br/>'
                f'• <b>Grand Total (All Currencies):</b><br/>'
                f'&nbsp;&nbsp;- BD {bhd_billed_tot:,.2f}<br/>'
                f'&nbsp;&nbsp;- ₱{(bhd_billed_tot * bhd_to_php):,.2f}<br/>'
                f'&nbsp;&nbsp;- ${(bhd_billed_tot * bhd_to_usd):,.2f}'
                f'</div>',
                unsafe_allow_html=True
            )

        with s2:
            st.markdown(
                f'<div class="income-card">'
                f'<b>🟢 TOTAL ACTUAL AMOUNT PAID:</b><br/>'
                f'• <b>PHP Records:</b> ₱{php_paid:,.2f} (BD {php_paid/bhd_to_php:,.2f})<br/>'
                f'• <b>Grand Total (All Currencies):</b><br/>'
                f'&nbsp;&nbsp;- BD {bhd_paid_tot:,.2f}<br/>'
                f'&nbsp;&nbsp;- ₱{(bhd_paid_tot * bhd_to_php):,.2f}<br/>'
                f'&nbsp;&nbsp;- ${(bhd_paid_tot * bhd_to_usd):,.2f}'
                f'</div>',
                unsafe_allow_html=True
            )

        with s3:
            st.markdown(
                f'<div class="priority-banner">'
                f'<b>🔴 TOTAL REMAINING PENDING DUE:</b><br/>'
                f'• <b>PHP Records:</b> ₱{php_pending:,.2f} (BD {php_pending/bhd_to_php:,.2f})<br/>'
                f'• <b>Grand Total (All Currencies):</b><br/>'
                f'&nbsp;&nbsp;- BD {bhd_pending_tot:,.2f}<br/>'
                f'&nbsp;&nbsp;- ₱{(bhd_pending_tot * bhd_to_php):,.2f}<br/>'
                f'&nbsp;&nbsp;- ${(bhd_pending_tot * bhd_to_usd):,.2f}'
                f'</div>',
                unsafe_allow_html=True
            )

    else:
        st.info("No transaction records found. Add your first payment in the 'Record Expense' tab!")

# 🔮 12-MONTH / YEARLY PROJECTED BUDGETING & FORECAST ENGINE
with tab_forecast:
    st.subheader("🔮 Future 12-Month Projected Budgeting & Savings Engine")
    st.markdown("Project your future monthly expenses, income growth, recurring commitments, and cumulative savings potential over the next 12 months.")

    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        proj_base_income = st.number_input("Base Projected Monthly Income (BHD)", min_value=0.0, value=float(total_income_bhd), step=50.0)
        income_growth_pct = st.slider("Expected Annual Income Growth (%)", 0.0, 20.0, 3.0, step=0.5)
    with f_col2:
        proj_monthly_needs = st.number_input("Projected Fixed Needs & Priority / Month (BHD)", min_value=0.0, value=float(priority_allocation_bhd + target_needs_bhd + target_debts_bhd), step=20.0)
        inflation_pct = st.slider("Expected Annual Expense Inflation (%)", 0.0, 15.0, 2.5, step=0.5)
    with f_col3:
        proj_monthly_wants = st.number_input("Projected Lifestyle Allowance / Month (BHD)", min_value=0.0, value=float(target_wants_bhd), step=10.0)
        target_savings_monthly = st.number_input("Target Monthly Savings Goal (BHD)", min_value=0.0, value=float(target_savings_bhd), step=10.0)

    st.markdown("---")
    st.markdown("#### 📅 12-Month Detailed Financial Projections Matrix")

    months = ["Month 1", "Month 2", "Month 3", "Month 4", "Month 5", "Month 6", "Month 7", "Month 8", "Month 9", "Month 10", "Month 11", "Month 12"]
    
    forecast_rows = []
    cum_savings = 0.0

    for i, m_name in enumerate(months):
        m_inc = proj_base_income * ((1 + (income_growth_pct / 100.0) / 12) ** i)
        m_needs = proj_monthly_needs * ((1 + (inflation_pct / 100.0) / 12) ** i)
        m_wants = proj_monthly_wants
        m_total_exp = m_needs + m_wants
        m_net_surplus = m_inc - m_total_exp
        cum_savings += m_net_surplus

        forecast_rows.append({
            "Month": m_name,
            "Projected Income (BHD)": round(m_inc, 2),
            "Essential Needs & Debts (BHD)": round(m_needs, 2),
            "Lifestyle Allowance (BHD)": round(m_wants, 2),
            "Total Projected Expenses (BHD)": round(m_total_exp, 2),
            "Net Monthly Surplus (BHD)": round(m_net_surplus, 2),
            "Cumulative Wealth / Savings (BHD)": round(cum_savings, 2)
        })

    df_forecast = pd.DataFrame(forecast_rows)

    st.dataframe(
        df_forecast.style.format({
            "Projected Income (BHD)": "BD {:,.2f}",
            "Essential Needs & Debts (BHD)": "BD {:,.2f}",
            "Lifestyle Allowance (BHD)": "BD {:,.2f}",
            "Total Projected Expenses (BHD)": "BD {:,.2f}",
            "Net Monthly Surplus (BHD)": "BD {:,.2f}",
            "Cumulative Wealth / Savings (BHD)": "BD {:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    tot_1y_inc = df_forecast["Projected Income (BHD)"].sum()
    tot_1y_exp = df_forecast["Total Projected Expenses (BHD)"].sum()
    tot_1y_savings = df_forecast["Net Monthly Surplus (BHD)"].sum()

    st.markdown("---")
    fc1, fc2, fc3 = st.columns(3)
    fc1.metric("Total 1-Year Projected Income", f"BD {tot_1y_inc:,.2f}", delta=f"₱{(tot_1y_inc*bhd_to_php):,.2f}")
    fc2.metric("Total 1-Year Projected Expenses", f"BD {tot_1y_exp:,.2f}", delta=f"₱{(tot_1y_exp*bhd_to_php):,.2f}")
    fc3.metric("Total 1-Year Projected Savings Potential", f"BD {tot_1y_savings:,.2f}", delta=f"₱{(tot_1y_savings*bhd_to_php):,.2f}")

    st.markdown("---")
    f_chart1, f_chart2 = st.columns(2)
    with f_chart1:
        st.subheader("12-Month Income vs. Projected Expenses")
        fig_f_bar = go.Figure(data=[
            go.Bar(name='Projected Income', x=df_forecast['Month'], y=df_forecast['Projected Income (BHD)'], marker_color='#10B981'),
            go.Bar(name='Projected Expenses', x=df_forecast['Month'], y=df_forecast['Total Projected Expenses (BHD)'], marker_color='#EF4444')
        ])
        fig_f_bar.update_layout(barmode='group', margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_f_bar, use_container_width=True)

    with f_chart2:
        st.subheader("Cumulative Wealth & Savings Growth Trend")
        fig_f_line = px.line(
            df_forecast, x="Month", y="Cumulative Wealth / Savings (BHD)",
            title="12-Month Forecast Accumulation",
            markers=True
        )
        fig_f_line.update_traces(line_color="#2563EB", line_width=3)
        st.plotly_chart(fig_f_line, use_container_width=True)

# MT5 PIP & MARGIN CALCULATOR TAB
with tab_mt5:
    st.subheader("📈 MT5 Pip Value & Required Margin Calculator")

    st.markdown("#### 1. Pip Value Calculator")
    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        pair = st.selectbox("Trading Pair", ["USDPHP", "BHDPHP", "USDCAD", "EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "USDCHF", "AUDUSD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"])
        account_ccy = st.selectbox("Account Currency", ["USD", "BHD", "PHP"])
    with mc2:
        lot_size = st.number_input("Lot Size (Volume)", min_value=0.01, max_value=100.0, value=0.10, step=0.01)
    with mc3:
        pips = st.number_input("Target Pips", min_value=1.0, value=20.0, step=1.0)

    if "JPY" in pair or "PHP" in pair:
        pip_val_usd_per_lot = 10.0 if "JPY" in pair else 1.8
    elif "XAU" in pair:
        pip_val_usd_per_lot = 10.0
    else:
        pip_val_usd_per_lot = 10.0

    pip_val_usd = lot_size * pip_val_usd_per_lot
    total_profit_usd = pip_val_usd * pips

    if account_ccy == "USD":
        disp_pip_val = pip_val_usd
        disp_profit = total_profit_usd
    elif account_ccy == "BHD":
        disp_pip_val = pip_val_usd / bhd_to_usd
        disp_profit = total_profit_usd / bhd_to_usd
    else:
        disp_pip_val = (pip_val_usd / bhd_to_usd) * bhd_to_php
        disp_profit = (total_profit_usd / bhd_to_usd) * bhd_to_php

    st.info(f"📍 **{pair} ({lot_size} Lots):** 1 Pip = **{account_ccy} {disp_pip_val:,.2f}** | Profit for {pips} pips = **{account_ccy} {disp_profit:,.2f}**")

    st.markdown("---")
    st.markdown("#### 2. Margin Calculator")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        leverage = st.selectbox("Account Leverage", [100, 200, 400, 500, 1000], index=3)
    with col_m2:
        contract_size = 100000
        req_margin_usd = (lot_size * contract_size) / leverage
        if account_ccy == "USD": disp_margin = req_margin_usd
        elif account_ccy == "BHD": disp_margin = req_margin_usd / bhd_to_usd
        else: disp_margin = (req_margin_usd / bhd_to_usd) * bhd_to_php

        st.metric(f"Required Margin ({account_ccy})", f"{account_ccy} {disp_margin:,.2f}", delta=f"1:{leverage} Leverage")

# INVESTMENT TRACKER TAB
with tab_invest:
    st.subheader("📈 Portfolio & Investment Asset Tracker")

    def load_investments():
        if os.path.exists(INVEST_FILE):
            try: return pd.read_csv(INVEST_FILE)
            except Exception: pass
        return pd.DataFrame(columns=["Asset Name", "Asset Class", "Amount Invested ($)", "Current Value ($)", "Date Added"])

    def save_investments(df):
        df.to_csv(INVEST_FILE, index=False)

    df_invest = load_investments()

    with st.form("add_invest_form", clear_on_submit=True):
        col_i1, col_i2 = st.columns(2)
        with col_i1:
            asset_name = st.text_input("Asset Name", placeholder="e.g. COL Financial - BDO, MT5 Gold, MP2 Savings")
            asset_class = st.selectbox("Asset Class", ["Stocks / Equities", "Forex Trading", "Real Estate", "Mutual Funds / ETFs", "Crypto / Commodities"])
        with col_i2:
            amt_inv = st.number_input("Amount Invested ($ USD)", min_value=1.0, value=500.0, step=50.0)
            curr_val = st.number_input("Current Value ($ USD)", min_value=0.0, value=550.0, step=50.0)

        sub_inv = st.form_submit_button("Add Asset to Portfolio", use_container_width=True)
        if sub_inv:
            new_inv = pd.DataFrame([{
                "Asset Name": asset_name if asset_name else "Unspecified",
                "Asset Class": asset_class,
                "Amount Invested ($)": amt_inv,
                "Current Value ($)": curr_val,
                "Date Added": datetime.today().strftime("%Y-%m-%d")
            }])
            df_invest = pd.concat([df_invest, new_inv], ignore_index=True)
            save_investments(df_invest)
            st.success("Investment asset added successfully!")
            st.rerun()

    if not df_invest.empty:
        df_invest["Profit / Loss"] = df_invest["Current Value ($)"] - df_invest["Amount Invested ($)"]
        df_invest["ROI %"] = (df_invest["Profit / Loss"] / df_invest["Amount Invested ($)"] * 100).round(2)
        
        st.dataframe(df_invest.style.format({
            "Amount Invested ($)": "${:,.2f}",
            "Current Value ($)": "${:,.2f}",
            "Profit / Loss": "${:,.2f}",
            "ROI %": "{:.2f}%"
        }), use_container_width=True, hide_index=True)

        tot_inv = float(df_invest["Amount Invested ($)"].sum())
        tot_val = float(df_invest["Current Value ($)"].sum())
        tot_pnl = tot_val - tot_inv

        st.metric("Total Portfolio Value", f"${tot_val:,.2f}", delta=f"${tot_pnl:,.2f} Total Return")

# REPORTS TAB
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

# GUIDE & SETUP TAB
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
