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

# High-Contrast Adaptive CSS Styling for Light & Dark Mode
st.markdown("""
<style>
    .main-header { font-size: 2.0rem; font-weight: 800; color: #1E3A8A; margin-bottom: 0.1rem; }
    @media (prefers-color-scheme: dark) { .main-header { color: #60A5FA !important; } }
    
    .sub-header { font-size: 0.95rem; color: #4B5563; margin-bottom: 1.0rem; }
    @media (prefers-color-scheme: dark) { .sub-header { color: #9CA3AF !important; } }

    /* Budget Notice Banners */
    .banner-within-budget {
        background-color: #ECFDF5 !important;
        border: 2px solid #10B981 !important;
        border-left: 8px solid #059669 !important;
        padding: 14px 18px !important;
        border-radius: 8px !important;
        margin-bottom: 16px !important;
        color: #064E3B !important;
        font-weight: 600 !important;
    }
    @media (prefers-color-scheme: dark) {
        .banner-within-budget {
            background-color: #064E3B !important;
            border-color: #059669 !important;
            color: #ECFDF5 !important;
        }
    }

    .banner-over-budget {
        background-color: #FEF2F2 !important;
        border: 2px solid #EF4444 !important;
        border-left: 8px solid #DC2626 !important;
        padding: 14px 18px !important;
        border-radius: 8px !important;
        margin-bottom: 16px !important;
        color: #7F1D1D !important;
        font-weight: 600 !important;
    }
    @media (prefers-color-scheme: dark) {
        .banner-over-budget {
            background-color: #7F1D1D !important;
            border-color: #DC2626 !important;
            color: #FEF2F2 !important;
        }
    }

    /* Summary Card Styling with Explicit Readable Colors */
    .summary-card-billed {
        background-color: #EFF6FF !important;
        border: 1px solid #BFDBFE !important;
        border-left: 5px solid #2563EB !important;
        padding: 14px !important;
        border-radius: 8px !important;
        color: #1E40AF !important;
    }
    .summary-card-billed h4, .summary-card-billed div, .summary-card-billed p, .summary-card-billed span {
        color: #1E40AF !important;
    }
    @media (prefers-color-scheme: dark) {
        .summary-card-billed {
            background-color: #1E3A8A !important;
            border-color: #3B82F6 !important;
        }
        .summary-card-billed h4, .summary-card-billed div, .summary-card-billed p, .summary-card-billed span {
            color: #DBEAFE !important;
        }
    }

    .summary-card-paid {
        background-color: #F0FDF4 !important;
        border: 1px solid #BBF7D0 !important;
        border-left: 5px solid #16A34A !important;
        padding: 14px !important;
        border-radius: 8px !important;
        color: #166534 !important;
    }
    .summary-card-paid h4, .summary-card-paid div, .summary-card-paid p, .summary-card-paid span {
        color: #166534 !important;
    }
    @media (prefers-color-scheme: dark) {
        .summary-card-paid {
            background-color: #14532D !important;
            border-color: #22C55E !important;
        }
        .summary-card-paid h4, .summary-card-paid div, .summary-card-paid p, .summary-card-paid span {
            color: #DCFCE7 !important;
        }
    }

    .summary-card-due {
        background-color: #FEF2F2 !important;
        border: 1px solid #FECACA !important;
        border-left: 5px solid #DC2626 !important;
        padding: 14px !important;
        border-radius: 8px !important;
        color: #991B1B !important;
    }
    .summary-card-due h4, .summary-card-due div, .summary-card-due p, .summary-card-due span {
        color: #991B1B !important;
    }
    @media (prefers-color-scheme: dark) {
        .summary-card-due {
            background-color: #7F1D1D !important;
            border-color: #EF4444 !important;
        }
        .summary-card-due h4, .summary-card-due div, .summary-card-due p, .summary-card-due span {
            color: #FEE2E2 !important;
        }
    }

    .summary-card-php {
        background-color: #FFFBEB !important;
        border: 1px solid #FDE68A !important;
        border-left: 5px solid #D97706 !important;
        padding: 14px !important;
        border-radius: 8px !important;
        margin-top: 14px !important;
        color: #78350F !important;
    }
    .summary-card-php h4, .summary-card-php div, .summary-card-php p, .summary-card-php span {
        color: #78350F !important;
    }
    @media (prefers-color-scheme: dark) {
        .summary-card-php {
            background-color: #78350F !important;
            border-color: #F59E0B !important;
        }
        .summary-card-php h4, .summary-card-php div, .summary-card-php p, .summary-card-php span {
            color: #FEF3C7 !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# User Passcode Configurations
USER_PROFILES = {
    "Rogee": {
        "sec_key": "ROGEE_KEY",
        "def_key": "1989",
        "data_file": "expenses_rogee.csv",
        "config_file": "config_rogee.json"
    },
    "Ferdie": {
        "sec_key": "USER2_KEY",
        "def_key": "Ce_0121119",
        "data_file": "expenses_user2.csv",
        "config_file": "config_user2.json"
    },
    "User 3": {
        "sec_key": "USER3_KEY",
        "def_key": "user32026",
        "data_file": "expenses_user3.csv",
        "config_file": "config_user3.json"
    },
    "User 4": {
        "sec_key": "USER4_KEY",
        "def_key": "user42026",
        "data_file": "expenses_user4.csv",
        "config_file": "config_user4.json"
    }
}

# Session authentication state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = "Rogee"

# Authentication Lock Gate
if not st.session_state["authenticated"]:
    st.markdown('<div class="main-header">🔒 Rogee Financial Command Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Please authenticate to unlock your private budget workspace</div>', unsafe_allow_html=True)
    
    with st.container():
        col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
        with col_l2:
            st.markdown("### 🔑 Security Access Portal")
            selected_user = st.selectbox("Select User Profile", list(USER_PROFILES.keys()), index=0)
            entered_pass = st.text_input("Enter Passcode", type="password")
            
            if st.button("Unlock Command Center", use_container_width=True, type="primary"):
                user_info = USER_PROFILES[selected_user]
                expected_pass = st.secrets.get(user_info["sec_key"], user_info["def_key"])
                if entered_pass == expected_pass:
                    st.session_state["authenticated"] = True
                    st.session_state["current_user"] = selected_user
                    st.success(f"Welcome back, {selected_user}!")
                    st.rerun()
                else:
                    st.error("Incorrect Passcode! Please try again.")
    st.stop()

# Active User Context
current_user = st.session_state["current_user"]
user_cfg = USER_PROFILES[current_user]
DATA_FILE = user_cfg["data_file"]
CONFIG_FILE = user_cfg["config_file"]

# Sidebar Navigation & User Info
st.sidebar.title(f"👤 {current_user}'s Workspace")
if st.sidebar.button("🔒 Lock Portal / Sign Out", use_container_width=True):
    st.session_state["authenticated"] = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("💱 Exchange Rates (Base: BHD)")
bhd_to_php = st.sidebar.number_input("1 BHD to PHP (₱)", min_value=1.0, value=155.0, step=0.5)
bhd_to_usd = st.sidebar.number_input("1 BHD to USD ($)", min_value=0.1, value=2.65, step=0.01)

st.sidebar.markdown("---")
st.sidebar.subheader("💵 Monthly Take-Home Income Streams (BHD)")
salary_bhd = st.sidebar.number_input("Primary Salary (BHD)", min_value=0.0, value=850.0, step=25.0)
business_bhd = st.sidebar.number_input("Business Income (BHD)", min_value=0.0, value=150.0, step=25.0)
sidelines_bhd = st.sidebar.number_input("Sidelines / Freelance (BHD)", min_value=0.0, value=100.0, step=25.0)
other_income_bhd = st.sidebar.number_input("Other Income / Bonus (BHD)", min_value=0.0, value=0.0, step=25.0)

total_income_bhd = salary_bhd + business_bhd + sidelines_bhd + other_income_bhd

# Total Income Display Banner in Sidebar
st.sidebar.markdown(f"""
<div style="background-color:#F0FDF4; border:1px solid #BBF7D0; border-left:4px solid #16A34A; padding:10px; border-radius:6px; margin-top:10px;">
    <div style="font-size:0.8rem; color:#166534; font-weight:700;">TOTAL COMBINED MONTHLY INCOME</div>
    <div style="font-size:1.2rem; color:#15803D; font-weight:800;">BD {total_income_bhd:,.2f}</div>
    <div style="font-size:0.75rem; color:#166534;">₱ {(total_income_bhd * bhd_to_php):,.2f} PHP &nbsp;|&nbsp; $ {(total_income_bhd * bhd_to_usd):,.2f} USD</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("50/30/20 Targets (%)")
needs_pct = st.sidebar.slider("Needs Target %", 0, 100, 50)
wants_pct = st.sidebar.slider("Wants Target %", 0, 100, 30)
savings_pct = st.sidebar.slider("Savings Target %", 0, 100, 20)

total_target_pct = needs_pct + wants_pct + savings_pct
if total_target_pct != 100:
    st.sidebar.warning(f"Allocation total is {total_target_pct}%. It should equal 100%.")

needs_target_bhd = total_income_bhd * (needs_pct / 100.0)
wants_target_bhd = total_income_bhd * (wants_pct / 100.0)
savings_target_bhd = total_income_bhd * (savings_pct / 100.0)

# Helper Functions for Data Processing
def load_data():
    cols = ["Date", "Main Category", "Sub Category", "Merchant/Description", "Billed Amount", "Actual Paid", "Currency", "Payment Method", "Status"]
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            for c in cols:
                if c not in df.columns:
                    if c == "Billed Amount" and "Amount" in df.columns:
                        df["Billed Amount"] = df["Amount"]
                    elif c == "Actual Paid" and "Amount" in df.columns:
                        df["Actual Paid"] = df["Amount"]
                    elif c == "Currency":
                        df["Currency"] = "BHD"
                    elif c == "Status":
                        df["Status"] = "Paid"
                    else:
                        df[c] = ""
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            df['Billed Amount'] = pd.to_numeric(df['Billed Amount'], errors='coerce').fillna(0.0)
            df['Actual Paid'] = pd.to_numeric(df['Actual Paid'], errors='coerce').fillna(0.0)
            return df[cols]
        except Exception:
            pass
    return pd.DataFrame(columns=cols)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def convert_to_bhd(amt, curr):
    amt = float(amt)
    if curr == "PHP":
        return amt / bhd_to_php if bhd_to_php > 0 else 0.0
    elif curr == "USD":
        return amt / bhd_to_usd if bhd_to_usd > 0 else 0.0
    return amt

df_expenses = load_data()

# Calculations across transactions
df_work = df_expenses.copy()
if not df_work.empty:
    df_work["BHD_Billed"] = df_work.apply(lambda r: convert_to_bhd(r["Billed Amount"], r["Currency"]), axis=1)
    df_work["BHD_Paid"] = df_work.apply(lambda r: convert_to_bhd(r["Actual Paid"], r["Currency"]), axis=1)
    df_work["BHD_Pending"] = (df_work["BHD_Billed"] - df_work["BHD_Paid"]).clip(lower=0.0)
else:
    df_work["BHD_Billed"] = 0.0
    df_work["BHD_Paid"] = 0.0
    df_work["BHD_Pending"] = 0.0

total_billed_bhd = float(df_work["BHD_Billed"].sum()) if not df_work.empty else 0.0
total_spent_bhd = float(df_work["BHD_Paid"].sum()) if not df_work.empty else 0.0
total_pending_bhd = float(df_work["BHD_Pending"].sum()) if not df_work.empty else 0.0
remaining_cash_bhd = total_income_bhd - total_spent_bhd

# Main Title & Time Display
bh_tz = timezone(timedelta(hours=3))
ph_tz = timezone(timedelta(hours=8))
bh_time = datetime.now(bh_tz)
ph_time = datetime.now(ph_tz)

st.markdown('<div class="main-header">Salary & Personal Budget Manager</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Logged in as <b>{current_user}</b> &nbsp;|&nbsp; Bahrain Time: {bh_time.strftime("%d %b %Y, %I:%M %p")} &nbsp;|&nbsp; Manila Time: {ph_time.strftime("%d %b %Y, %I:%M %p")}</div>', unsafe_allow_html=True)

# Tabs Navigation
tab_dash, tab_add, tab_history, tab_proj, tab_calc, tab_reports = st.tabs([
    "📊 Dashboard & Analytics",
    "➕ Record Expense",
    "📋 Transaction History",
    "🔮 12-Month Projections",
    "📈 MT5 Pip Calculator",
    "📥 Reports & Export"
])

# ------------------------------------------------------------------------------
# TAB 1: DASHBOARD & ANALYTICS
# ------------------------------------------------------------------------------
with tab_dash:
    # Budget Notice Banner
    if remaining_cash_bhd >= 0:
        st.markdown(f"""
        <div class="banner-within-budget">
            🟢 <b>WITHIN BUDGET NOTICE:</b> You are currently within your budget limit! <br/>
            <b>Remaining Available Net Income:</b> BD {remaining_cash_bhd:,.2f} &nbsp;|&nbsp; 
            ₱ {(remaining_cash_bhd * bhd_to_php):,.2f} PHP &nbsp;|&nbsp; 
            $ {(remaining_cash_bhd * bhd_to_usd):,.2f} USD
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="banner-over-budget">
            🚨 <b>OVER BUDGET WARNING:</b> Your total spending has exceeded your monthly income! <br/>
            <b>Budget Deficit / Overage:</b> -BD {abs(remaining_cash_bhd):,.2f} &nbsp;|&nbsp; 
            -₱ {(abs(remaining_cash_bhd) * bhd_to_php):,.2f} PHP &nbsp;|&nbsp; 
            -$ {(abs(remaining_cash_bhd) * bhd_to_usd):,.2f} USD
        </div>
        """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Monthly Income", f"BD {total_income_bhd:,.2f}")
    m2.metric("Total Actual Paid", f"BD {total_spent_bhd:,.2f}", delta=f"-BD {total_spent_bhd:,.2f}", delta_color="inverse")
    
    if remaining_cash_bhd >= 0:
        m3.metric("Remaining Net Cash", f"BD {remaining_cash_bhd:,.2f}", delta=f"+BD {remaining_cash_bhd:,.2f}")
    else:
        m3.metric("Over Budget Deficit", f"-BD {abs(remaining_cash_bhd):,.2f}", delta=f"-BD {abs(remaining_cash_bhd):,.2f}", delta_color="inverse")
        
    m4.metric("Total Expenses Billed", f"BD {total_billed_bhd:,.2f}", delta=f"Pending: BD {total_pending_bhd:,.2f}", delta_color="off")

    st.markdown("---")
    st.subheader("50/30/20 Target vs. Actual Expense Breakdown")

    actual_needs_bhd = float(df_work[df_work["Main Category"].str.contains("Needs", na=False)]["BHD_Paid"].sum()) if not df_work.empty else 0.0
    actual_wants_bhd = float(df_work[df_work["Main Category"].str.contains("Wants", na=False)]["BHD_Paid"].sum()) if not df_work.empty else 0.0
    actual_savings_bhd = float(df_work[df_work["Main Category"].str.contains("Savings", na=False)]["BHD_Paid"].sum()) if not df_work.empty else 0.0
    actual_priority_bhd = float(df_work[df_work["Main Category"].str.contains("Priority", na=False)]["BHD_Paid"].sum()) if not df_work.empty else 0.0
    actual_debts_bhd = float(df_work[df_work["Main Category"].str.contains("Debts", na=False)]["BHD_Paid"].sum()) if not df_work.empty else 0.0

    cat_summary = [
        {"Category": "Needs (50%)", "Target (BHD)": needs_target_bhd, "Actual Paid (BHD)": actual_needs_bhd, "Difference (BHD)": needs_target_bhd - actual_needs_bhd, "Status": "On Track" if actual_needs_bhd <= needs_target_bhd else "Over Target"},
        {"Category": "Wants (30%)", "Target (BHD)": wants_target_bhd, "Actual Paid (BHD)": actual_wants_bhd, "Difference (BHD)": wants_target_bhd - actual_wants_bhd, "Status": "On Track" if actual_wants_bhd <= wants_target_bhd else "Over Target"},
        {"Category": "Savings (20%)", "Target (BHD)": savings_target_bhd, "Actual Paid (BHD)": actual_savings_bhd, "Difference (BHD)": actual_savings_bhd - savings_target_bhd, "Status": "Goal Met" if actual_savings_bhd >= savings_target_bhd else "Under Goal"},
        {"Category": "100% Priority Payments", "Target (BHD)": 0.0, "Actual Paid (BHD)": actual_priority_bhd, "Difference (BHD)": -actual_priority_bhd, "Status": "Mandatory"},
        {"Category": "Debts & Credits", "Target (BHD)": 0.0, "Actual Paid (BHD)": actual_debts_bhd, "Difference (BHD)": -actual_debts_bhd, "Status": "Mandatory"}
    ]
    st.dataframe(pd.DataFrame(cat_summary), use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------
# TAB 2: RECORD EXPENSE
# ------------------------------------------------------------------------------
with tab_add:
    st.subheader("➕ Record a New Payment or Expense")

    col_cat1, col_cat2 = st.columns(2)
    with col_cat1:
        main_category = st.selectbox(
            "Main Category",
            ["100% Priority Payments", "Debts & Credits", "Needs (50%)", "Wants (30%)", "Savings & Investments (20%)"],
            key="add_main_cat"
        )
    with col_cat2:
        if "Priority" in main_category:
            sub_options = ["Emergency Medical", "House Rent", "Loan Payment", "Tuition Fee", "Essential Utility"]
        elif "Debts" in main_category:
            sub_options = ["Credit Card Debt", "Personal Loan", "Bank Overdraft", "Friend/Family Debt"]
        elif "Needs" in main_category:
            sub_options = ["Housing / Rent", "Utilities & Bills", "Groceries & Food", "Transportation / Fuel", "Healthcare / Insurance"]
        elif "Wants" in main_category:
            sub_options = ["Dining Out & Coffee", "Shopping & Apparel", "Entertainment & Travel", "Subscriptions", "Hobbies"]
        else:
            sub_options = ["Emergency Fund", "Stock / Crypto Investments", "Retirement Fund", "Goal Savings"]
            
        sub_category = st.selectbox("Sub Category", sub_options, key="add_sub_cat")

    with st.form("record_expense_form", clear_on_submit=True):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            exp_date = st.date_input("Transaction Date", value=datetime.today())
            merchant = st.text_input("Merchant / Description", placeholder="e.g., Grocery Store, Rent, Electricity")
            curr = st.selectbox("Transaction Currency", ["BHD", "PHP", "USD"], index=0)
        with f_col2:
            billed_amt = st.number_input("Planned / Billed Amount", min_value=0.0, step=5.0, value=50.0)
            paid_amt = st.number_input("Actual Amount Paid", min_value=0.0, step=5.0, value=50.0)
            pay_method = st.selectbox("Payment Method", ["Benefit Pay", "Remittance", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])

        submit_exp = st.form_submit_button("Save Transaction to Ledger", type="primary")

        if submit_exp:
            status_val = "Paid" if paid_amt >= billed_amt and billed_amt > 0 else ("Partially Paid" if paid_amt > 0 else "Not Paid")
            new_entry = pd.DataFrame([{
                "Date": exp_date,
                "Main Category": main_category,
                "Sub Category": sub_category,
                "Merchant/Description": merchant if merchant else "General Expense",
                "Billed Amount": billed_amt,
                "Actual Paid": paid_amt,
                "Currency": curr,
                "Payment Method": pay_method,
                "Status": status_val
            }])
            df_expenses = pd.concat([df_expenses, new_entry], ignore_index=True)
            save_data(df_expenses)
            st.success(f"Successfully recorded transaction: {merchant} ({curr} {paid_amt:,.2f})!")
            st.rerun()

# ------------------------------------------------------------------------------
# TAB 3: TRANSACTION HISTORY & LEDGER
# ------------------------------------------------------------------------------
with tab_history:
    st.subheader("📋 Recorded Expense History & Transaction Ledger")

    # 1. NOTICE BANNER ABOVE TRANSACTION HISTORY TABLE
    if remaining_cash_bhd >= 0:
        st.markdown(f"""
        <div class="banner-within-budget">
            🟢 <b>WITHIN BUDGET STATUS:</b> You have available remaining income! <br/>
            <b>Net Unspent Cash Balance:</b> BD {remaining_cash_bhd:,.2f} &nbsp;|&nbsp; 
            ₱ {(remaining_cash_bhd * bhd_to_php):,.2f} PHP &nbsp;|&nbsp; 
            $ {(remaining_cash_bhd * bhd_to_usd):,.2f} USD
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="banner-over-budget">
            🚨 <b>OVER BUDGET STATUS NOTICE:</b> Total payments exceed your monthly income limit! <br/>
            <b>Current Overage / Limit Deficit:</b> -BD {abs(remaining_cash_bhd):,.2f} &nbsp;|&nbsp; 
            -₱ {(abs(remaining_cash_bhd) * bhd_to_php):,.2f} PHP &nbsp;|&nbsp; 
            -$ {(abs(remaining_cash_bhd) * bhd_to_usd):,.2f} USD
        </div>
        """, unsafe_allow_html=True)

    if not df_expenses.empty:
        # Category Filter
        cat_choices = list(df_expenses["Main Category"].unique())
        selected_cats = st.multiselect("Filter by Category", options=cat_choices, default=cat_choices)
        
        df_filtered = df_expenses[df_expenses["Main Category"].isin(selected_cats)] if selected_cats else df_expenses
        
        # Chronological Sort
        df_filtered = df_filtered.sort_values(by="Date", ascending=True).reset_index(drop=True)
        df_filtered["Item #"] = df_filtered.index + 1

        # Calculate Display Columns
        df_display = df_filtered.copy()
        df_display["Pending Due"] = (df_display["Billed Amount"] - df_display["Actual Paid"]).clip(lower=0.0)
        
        def calc_paid_pct(row):
            b = float(row["Billed Amount"])
            p = float(row["Actual Paid"])
            if b <= 0:
                return 100.0 if p > 0 else 0.0
            return min((p / b) * 100.0, 100.0)

        df_display["% Paid"] = df_display.apply(calc_paid_pct, axis=1)
        df_display["% Remaining"] = 100.0 - df_display["% Paid"]

        def calc_status(row):
            pct = row["% Paid"]
            if pct >= 100.0:
                return "Paid"
            elif pct > 0.0:
                return "Partially Paid"
            return "Not Paid"

        df_display["Status"] = df_display.apply(calc_status, axis=1)

        def make_equiv(row):
            amt = float(row["Actual Paid"])
            c = row["Currency"]
            if c == "PHP":
                b = amt / bhd_to_php if bhd_to_php > 0 else 0.0
                u = b * bhd_to_usd
                return f"BD {b:,.2f} | $ {u:,.2f}"
            elif c == "USD":
                b = amt / bhd_to_usd if bhd_to_usd > 0 else 0.0
                p = b * bhd_to_php
                return f"BD {b:,.2f} | ₱ {p:,.2f}"
            else: # BHD
                p = amt * bhd_to_php
                u = amt * bhd_to_usd
                return f"₱ {p:,.2f} | $ {u:,.2f}"

        df_display["Equivalent"] = df_display.apply(make_equiv, axis=1)

        # Rearrange Column Order
        ordered_cols = [
            "Item #", "Date", "Main Category", "Sub Category", "Merchant/Description",
            "Billed Amount", "Actual Paid", "Currency", "Pending Due", "% Paid", "% Remaining",
            "Equivalent", "Status", "Payment Method"
        ]
        df_display = df_display[ordered_cols]

        # Row Color Highlighting
        def highlight_status(row):
            st_val = row["Status"]
            if st_val == "Paid":
                return ['background-color: #D1FAE5; color: #065F46; font-weight: 600;'] * len(row)
            elif st_val == "Partially Paid":
                return ['background-color: #FEF3C7; color: #92400E; font-weight: 600;'] * len(row)
            else:
                return ['background-color: #FEE2E2; color: #991B1B; font-weight: 600;'] * len(row)

        st.markdown("##### 🎨 Color Ledger (Green = Paid | Yellow = Partial | Red = Unpaid)")
        st.dataframe(
            df_display.style.apply(highlight_status, axis=1).format({
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
        
        # 2. HIGH-CONTRAST READABLE SUMMARY BELOW TRANSACTIONS
        st.subheader("💰 Total Outstanding & Payment Ledger Summary")
        
        # Total Computations
        tot_billed_php = sum([r["Billed Amount"] if r["Currency"] == "PHP" else (r["Billed Amount"] * bhd_to_php if r["Currency"] == "BHD" else (r["Billed Amount"] / bhd_to_usd * bhd_to_php if bhd_to_usd > 0 else 0)) for _, r in df_display.iterrows()])
        tot_paid_php = sum([r["Actual Paid"] if r["Currency"] == "PHP" else (r["Actual Paid"] * bhd_to_php if r["Currency"] == "BHD" else (r["Actual Paid"] / bhd_to_usd * bhd_to_php if bhd_to_usd > 0 else 0)) for _, r in df_display.iterrows()])
        tot_pending_php = tot_billed_php - tot_paid_php

        tot_billed_bhd_val = total_billed_bhd
        tot_paid_bhd_val = total_spent_bhd
        tot_pending_bhd_val = total_pending_bhd

        col_s1, col_s2, col_s3 = st.columns(3)

        with col_s1:
            st.markdown(f"""
            <div class="summary-card-billed">
                <h4 style="margin:0; font-size:1.0rem;">📋 Total Billed / Needed</h4>
                <div style="font-size:1.4rem; font-weight:800; margin-top:4px;">BD {tot_billed_bhd_val:,.2f}</div>
                <div style="font-size:0.85rem; margin-top:4px; font-weight:600;">
                    🇵🇭 ₱ {tot_billed_php:,.2f} PHP <br/>
                    🇺🇸 $ {(tot_billed_bhd_val * bhd_to_usd):,.2f} USD
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_s2:
            st.markdown(f"""
            <div class="summary-card-paid">
                <h4 style="margin:0; font-size:1.0rem;">🟢 Total Amount Paid</h4>
                <div style="font-size:1.4rem; font-weight:800; margin-top:4px;">BD {tot_paid_bhd_val:,.2f}</div>
                <div style="font-size:0.85rem; margin-top:4px; font-weight:600;">
                    🇵🇭 ₱ {tot_paid_php:,.2f} PHP <br/>
                    🇺🇸 $ {(tot_paid_bhd_val * bhd_to_usd):,.2f} USD
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_s3:
            st.markdown(f"""
            <div class="summary-card-due">
                <h4 style="margin:0; font-size:1.0rem;">🔴 Total Pending Remaining</h4>
                <div style="font-size:1.4rem; font-weight:800; margin-top:4px;">BD {tot_pending_bhd_val:,.2f}</div>
                <div style="font-size:0.85rem; margin-top:4px; font-weight:600;">
                    🇵🇭 ₱ {tot_pending_php:,.2f} PHP <br/>
                    🇺🇸 $ {(tot_pending_bhd_val * bhd_to_usd):,.2f} USD
                </div>
            </div>
            """, unsafe_allow_html=True)

        # PHP Specific Highlight Card
        php_rows = df_display[df_display["Currency"] == "PHP"]
        php_billed_raw = float(php_rows["Billed Amount"].sum()) if not php_rows.empty else 0.0
        php_paid_raw = float(php_rows["Actual Paid"].sum()) if not php_rows.empty else 0.0
        php_pending_raw = float(php_rows["Pending Due"].sum()) if not php_rows.empty else 0.0

        st.markdown(f"""
        <div class="summary-card-php">
            <h4 style="margin:0; font-size:1.05rem;">🇵🇭 PHP Transaction Specific Record Summary</h4>
            <div style="display:flex; justify-content:space-between; margin-top:8px; font-size:0.95rem; font-weight:700;">
                <span>Total PHP Billed: <b>₱ {php_billed_raw:,.2f}</b> (BD {(php_billed_raw / bhd_to_php if bhd_to_php > 0 else 0):,.2f})</span>
                <span>Total PHP Paid: <b>₱ {php_paid_raw:,.2f}</b> (BD {(php_paid_raw / bhd_to_php if bhd_to_php > 0 else 0):,.2f})</span>
                <span>PHP Remaining: <b>₱ {php_pending_raw:,.2f}</b> (BD {(php_pending_raw / bhd_to_php if bhd_to_php > 0 else 0):,.2f})</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("Clear My Expense Data", type="primary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.success("Expense logs cleared!")
            st.rerun()
    else:
        st.info("No recorded transactions found. Add your first expense in the 'Record Expense' tab!")

# ------------------------------------------------------------------------------
# TAB 4: 12-MONTH PROJECTIONS
# ------------------------------------------------------------------------------
with tab_proj:
    st.subheader("🔮 12-Month / Yearly Projected Budgeting & Savings Engine")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        base_proj_income = st.number_input("Base Monthly Income (BHD)", value=total_income_bhd, step=50.0)
        income_growth_rate = st.slider("Annual Income Growth Rate (%)", 0.0, 20.0, 3.0, step=0.5)
        fixed_needs_proj = st.number_input("Projected Fixed Needs (BHD/mo)", value=needs_target_bhd, step=25.0)
    with col_p2:
        inflation_rate = st.slider("Annual Inflation Rate (%)", 0.0, 15.0, 2.5, step=0.5)
        lifestyle_proj = st.number_input("Projected Wants & Lifestyle (BHD/mo)", value=wants_target_bhd, step=25.0)

    # Calculate 12-Month Data
    proj_rows = []
    cum_savings = 0.0
    for m in range(1, 13):
        m_inc = base_proj_income * ((1 + (income_growth_rate / 100.0) / 12) ** (m - 1))
        m_needs = fixed_needs_proj * ((1 + (inflation_rate / 100.0) / 12) ** (m - 1))
        m_wants = lifestyle_proj * ((1 + (inflation_rate / 100.0) / 12) ** (m - 1))
        m_exp = m_needs + m_wants
        m_surplus = m_inc - m_exp
        cum_savings += m_surplus
        proj_rows.append({
            "Month": f"Month {m}",
            "Income (BHD)": round(m_inc, 2),
            "Needs (BHD)": round(m_needs, 2),
            "Wants (BHD)": round(m_wants, 2),
            "Total Exp (BHD)": round(m_exp, 2),
            "Net Surplus (BHD)": round(m_surplus, 2),
            "Cum. Savings (BHD)": round(cum_savings, 2)
        })

    df_proj = pd.DataFrame(proj_rows)

    tot_proj_inc = float(df_proj["Income (BHD)"].sum())
    tot_proj_exp = float(df_proj["Total Exp (BHD)"].sum())
    tot_proj_sav = float(df_proj["Net Surplus (BHD)"].sum())

    st.markdown("---")
    pm1, pm2, pm3 = st.columns(3)
    pm1.metric("1-Year Projected Income", f"BD {tot_proj_inc:,.2f}", f"₱ {(tot_proj_inc * bhd_to_php):,.2f}")
    pm2.metric("1-Year Projected Expenses", f"BD {tot_proj_exp:,.2f}", f"₱ {(tot_proj_exp * bhd_to_php):,.2f}")
    pm3.metric("1-Year Net Savings Potential", f"BD {tot_proj_sav:,.2f}", f"₱ {(tot_proj_sav * bhd_to_php):,.2f}")

    st.markdown("---")
    st.dataframe(df_proj, use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------
# TAB 5: MT5 PIP CALCULATOR
# ------------------------------------------------------------------------------
with tab_calc:
    st.subheader("📈 MT5 Pip & Risk Calculator")
    
    col_pip1, col_pip2 = st.columns(2)
    with col_pip1:
        pair = st.selectbox("Trading Pair", ["USDPHP", "BHDPHP", "USDCAD", "EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "USDCHF", "AUDUSD", "NZDUSD"])
        lot_size = st.number_input("Lot Size (Lots)", min_value=0.01, value=1.0, step=0.01)
    with col_pip2:
        entry_price = st.number_input("Entry Price", value=1.0000, step=0.0001, format="%.4f")
        stop_pips = st.number_input("Stop Loss (Pips)", min_value=1.0, value=30.0, step=5.0)

    # Basic Pip Valuation
    pip_val = 10.0 * lot_size if "JPY" not in pair and "PHP" not in pair else 1000.0 * lot_size
    risk_usd = pip_val * stop_pips
    
    st.markdown("---")
    st.metric("Estimated Pip Value", f"${pip_val:,.2f} USD")
    st.metric("Total Trade Risk", f"${risk_usd:,.2f} USD", f"₱ {(risk_usd * 58.5):,.2f} PHP")

# ------------------------------------------------------------------------------
# TAB 6: REPORTS & EXPORT
# ------------------------------------------------------------------------------
with tab_reports:
    st.subheader("📥 Download Financial Reports")
    
    if not df_expenses.empty:
        csv_data = df_expenses.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Transaction CSV Ledger", data=csv_data, file_name=f"ledger_{current_user.lower()}.csv", mime="text/csv")
    else:
        st.info("No transactions logged to export.")
