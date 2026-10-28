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

# Custom High-Contrast CSS styling for both Light & Dark Modes
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.1rem;
        line-height: 1.2;
    }
    @media (prefers-color-scheme: dark) {
        .main-header { color: #60A5FA !important; }
    }
    .sub-header {
        font-size: 1.0rem;
        color: #4B5563;
        margin-bottom: 1.0rem;
    }
    @media (prefers-color-scheme: dark) {
        .sub-header { color: #9CA3AF !important; }
    }
    
    .time-badge {
        background-color: #F3F4F6;
        border: 1px solid #E5E7EB;
        color: #1F2937 !important;
        padding: 8px 14px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 15px;
        display: block;
        width: 100%;
        text-align: center;
    }
    @media (prefers-color-scheme: dark) {
        .time-badge {
            background-color: #1F2937 !important;
            border-color: #374151 !important;
            color: #F3F4F6 !important;
        }
    }

    /* High Contrast Summary Cards Below Table */
    .summary-card-blue {
        background-color: #EFF6FF !important;
        border: 1px solid #BFDBFE !important;
        border-left: 5px solid #2563EB !important;
        padding: 14px 18px !important;
        border-radius: 8px !important;
        margin-bottom: 12px !important;
        color: #1E40AF !important;
    }
    .summary-card-blue * { color: #1E40AF !important; }
    
    .summary-card-green {
        background-color: #F0FDF4 !important;
        border: 1px solid #BBF7D0 !important;
        border-left: 5px solid #16A34A !important;
        padding: 14px 18px !important;
        border-radius: 8px !important;
        margin-bottom: 12px !important;
        color: #166534 !important;
    }
    .summary-card-green * { color: #166534 !important; }

    .summary-card-red {
        background-color: #FEF2F2 !important;
        border: 1px solid #FECACA !important;
        border-left: 5px solid #DC2626 !important;
        padding: 14px 18px !important;
        border-radius: 8px !important;
        margin-bottom: 12px !important;
        color: #991B1B !important;
    }
    .summary-card-red * { color: #991B1B !important; }

    @media (prefers-color-scheme: dark) {
        .summary-card-blue {
            background-color: #1E3A8A !important;
            border-color: #3B82F6 !important;
            color: #DBEAFE !important;
        }
        .summary-card-blue * { color: #DBEAFE !important; }

        .summary-card-green {
            background-color: #064E3B !important;
            border-color: #10B981 !important;
            color: #D1FAE5 !important;
        }
        .summary-card-green * { color: #D1FAE5 !important; }

        .summary-card-red {
            background-color: #7F1D1D !important;
            border-color: #EF4444 !important;
            color: #FEE2E2 !important;
        }
        .summary-card-red * { color: #FEE2E2 !important; }
    }

    /* Metric Card Styling */
    .stMetric {
        background-color: #F9FAFB !important;
        padding: 10px 14px !important;
        border-radius: 8px !important;
        border: 1px solid #E5E7EB !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        color: #1E3A8A !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #374151 !important;
        font-weight: 600 !important;
    }
    @media (prefers-color-scheme: dark) {
        .stMetric {
            background-color: #1F2937 !important;
            border: 1px solid #374151 !important;
        }
        div[data-testid="stMetricValue"] { color: #60A5FA !important; }
        div[data-testid="stMetricLabel"] { color: #D1D5DB !important; }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SECURITY & AUTHENTICATION GATE
# ---------------------------------------------------------
USER_PROFILES = {
    "Rogee": {
        "sec_key": "ROGEE_KEY",
        "def_key": "rogee2026",
        "data_file": "expenses_rogee.csv",
        "config_file": "config_rogee.json"
    },
    "User 2": {
        "sec_key": "USER2_KEY",
        "def_key": "user2026",
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

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = "Rogee"

if not st.session_state["authenticated"]:
    st.markdown('<div class="main-header">🔒 Rogee Financial Security Portal</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Please authenticate with your user credentials to access your financial dashboard.</div>', unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("login_form"):
            selected_user = st.selectbox("Select Profile", list(USER_PROFILES.keys()), index=0)
            entered_key = st.text_input("Secret Passcode", type="password", placeholder="Enter passcode")
            login_submitted = st.form_submit_button("🔓 Unlock Command Center", use_container_width=True)
            
            if login_submitted:
                target_user = USER_PROFILES[selected_user]
                expected_pass = st.secrets.get(target_user["sec_key"], target_user["def_key"]) if hasattr(st, "secrets") else target_user["def_key"]
                
                if entered_key == expected_pass:
                    st.session_state["authenticated"] = True
                    st.session_state["current_user"] = selected_user
                    st.success(f"Welcome back, {selected_user}! Loading your financial command center...")
                    st.rerun()
                else:
                    st.error("Incorrect passcode! Access denied.")
        
        st.info("💡 **Default Passkeys for Reference**:\n- Rogee: `rogee2026`\n- User 2: `user2026`\n- User 3: `user32026`\n- User 4: `user42026`")
    st.stop()

# ---------------------------------------------------------
# ACTIVE USER CONFIG & DATA PATHS
# ---------------------------------------------------------
current_user = st.session_state["current_user"]
profile_info = USER_PROFILES[current_user]
DATA_FILE = profile_info["data_file"]
CONFIG_FILE = profile_info["config_file"]

# Time calculations
utc_now = datetime.now(timezone.utc)
bh_time = utc_now.astimezone(timezone(timedelta(hours=3)))
ph_time = utc_now.astimezone(timezone(timedelta(hours=8)))

# Data loading function
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
            
            # Migration check for older CSV files
            if "Billed Amount" not in df.columns:
                if "Amount" in df.columns:
                    df["Billed Amount"] = pd.to_numeric(df["Amount"], errors='coerce').fillna(0.0)
                else:
                    df["Billed Amount"] = 0.0
            
            if "Actual Paid" not in df.columns:
                if "Amount" in df.columns:
                    df["Actual Paid"] = pd.to_numeric(df["Amount"], errors='coerce').fillna(0.0)
                else:
                    df["Actual Paid"] = 0.0
            
            if "Currency" not in df.columns:
                df["Currency"] = "BHD"
            
            if "Status" not in df.columns:
                df["Status"] = "Paid"
            
            if "Payment Method" not in df.columns:
                df["Payment Method"] = "Bank Transfer"

            if "Main Category" not in df.columns:
                df["Main Category"] = "Needs (50%)"

            if "Sub Category" not in df.columns:
                df["Sub Category"] = "General"

            if "Merchant/Description" not in df.columns:
                df["Merchant/Description"] = "Unspecified"

            return df
        except Exception as e:
            pass
            
    cols = ["Date", "Main Category", "Sub Category", "Merchant/Description", "Billed Amount", "Actual Paid", "Currency", "Status", "Payment Method"]
    return pd.DataFrame(columns=cols)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df_expenses = load_data()

# ---------------------------------------------------------
# SIDEBAR CONFIGURATION
# ---------------------------------------------------------
st.sidebar.title(f"👤 {current_user}'s Financial Settings")

if st.sidebar.button("🔒 Sign Out / Lock App", type="secondary", use_container_width=True):
    st.session_state["authenticated"] = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("💱 Exchange Rates")
bhd_to_php = st.sidebar.number_input("1 BHD = PHP (₱)", min_value=1.0, value=155.0, step=0.5)
bhd_to_usd = st.sidebar.number_input("1 BHD = USD ($)", min_value=0.1, value=2.65, step=0.01)

st.sidebar.markdown("---")
st.sidebar.subheader("💵 Monthly Take-Home Income Streams (BHD)")
salary_bhd = st.sidebar.number_input("Primary Net Salary (BD)", min_value=0.0, value=1200.0, step=50.0)
business_bhd = st.sidebar.number_input("Business / Investment Income (BD)", min_value=0.0, value=250.0, step=25.0)
sidelines_bhd = st.sidebar.number_input("Sidelines / Freelance (BD)", min_value=0.0, value=100.0, step=10.0)
other_income_bhd = st.sidebar.number_input("Other Income / Allowance (BD)", min_value=0.0, value=0.0, step=10.0)

total_income_bhd = salary_bhd + business_bhd + sidelines_bhd + other_income_bhd
total_income_php = total_income_bhd * bhd_to_php
total_income_usd = total_income_bhd * bhd_to_usd

st.sidebar.markdown(f"""
<div class="summary-card-green" style="padding: 10px 14px !important; margin-top: 8px;">
    <b>TOTAL COMBINED MONTHLY INCOME:</b><br/>
    <span style="font-size: 1.15rem; font-weight: 800;">BD {total_income_bhd:,.2f}</span><br/>
    <small>₱ {total_income_php:,.2f} PHP &nbsp;|&nbsp; ${total_income_usd:,.2f} USD</small>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 50/30/20 Budget Allocations (%)")
needs_pct = st.sidebar.slider("Needs Target % (Essentials)", 0, 100, 50)
wants_pct = st.sidebar.slider("Wants Target % (Lifestyle)", 0, 100, 30)
savings_pct = st.sidebar.slider("Savings & Debt Target %", 0, 100, 20)

# Calculate Targets
needs_target_bhd = total_income_bhd * (needs_pct / 100.0)
wants_target_bhd = total_income_bhd * (wants_pct / 100.0)
savings_target_bhd = total_income_bhd * (savings_pct / 100.0)

# ---------------------------------------------------------
# MAIN APP HEADER & TIME BADGE
# ---------------------------------------------------------
st.markdown('<div class="main-header">Rogee Financial Command Center</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multi-Currency Personal Finance Manager & 50/30/20 Budgeting Engine</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="time-badge">
    🇧🇭 <b>Bahrain Time:</b> {bh_time.strftime("%d %b %Y, %I:%M %p")} AST &nbsp;|&nbsp; 
    🇵🇭 <b>Philippine Time:</b> {ph_time.strftime("%d %b %Y, %I:%M %p")} PST &nbsp;|&nbsp; 
    👤 <b>Active Profile:</b> {current_user}
</div>
""", unsafe_allow_html=True)

# Helper function to convert transaction amount to BHD
def get_bhd_amount(row, amount_col):
    val = float(row.get(amount_col, 0.0)) if pd.notnull(row.get(amount_col, 0.0)) else 0.0
    curr = str(row.get("Currency", "BHD")).upper().strip()
    if curr == "PHP":
        return val / bhd_to_php
    elif curr == "USD":
        return val / bhd_to_usd
    return val

# Calculate Actual Spent in BHD across dataframe
if not df_expenses.empty:
    df_temp = df_expenses.copy()
    df_temp["Paid_BHD"] = df_temp.apply(lambda r: get_bhd_amount(r, "Actual Paid"), axis=1)
    df_temp["Billed_BHD"] = df_temp.apply(lambda r: get_bhd_amount(r, "Billed Amount"), axis=1)
    
    actual_needs_bhd = float(df_temp[df_temp["Main Category"].str.contains("Needs", case=False, na=False)]["Paid_BHD"].sum())
    actual_wants_bhd = float(df_temp[df_temp["Main Category"].str.contains("Wants", case=False, na=False)]["Paid_BHD"].sum())
    actual_savings_bhd = float(df_temp[df_temp["Main Category"].str.contains("Savings|Investments", case=False, na=False)]["Paid_BHD"].sum())
    actual_priority_bhd = float(df_temp[df_temp["Main Category"].str.contains("100% Priority", case=False, na=False)]["Paid_BHD"].sum())
    actual_debts_bhd = float(df_temp[df_temp["Main Category"].str.contains("Debts", case=False, na=False)]["Paid_BHD"].sum())

    total_spent_bhd = float(df_temp["Paid_BHD"].sum())
    total_billed_bhd = float(df_temp["Billed_BHD"].sum())
else:
    actual_needs_bhd = 0.0
    actual_wants_bhd = 0.0
    actual_savings_bhd = 0.0
    actual_priority_bhd = 0.0
    actual_debts_bhd = 0.0
    total_spent_bhd = 0.0
    total_billed_bhd = 0.0

remaining_cash_bhd = total_income_bhd - total_spent_bhd
remaining_cash_php = remaining_cash_bhd * bhd_to_php
remaining_cash_usd = remaining_cash_bhd * bhd_to_usd

total_pending_bhd = total_billed_bhd - total_spent_bhd
total_pending_php = total_pending_bhd * bhd_to_php
total_pending_usd = total_pending_bhd * bhd_to_usd

# ---------------------------------------------------------
# TABS DECLARATION
# ---------------------------------------------------------
tab_dash, tab_add, tab_history, tab_proj, tab_pip, tab_reports, tab_guide = st.tabs([
    "📊 Dashboard & Analytics",
    "➕ Record Expense",
    "📋 Transaction History",
    "🔮 12-Month Projections",
    "📈 MT5 Pip Calculator",
    "📥 Download Reports",
    "📘 Security Guide"
])

# ---------------------------------------------------------
# TAB 1: DASHBOARD & ANALYTICS
# ---------------------------------------------------------
with tab_dash:
    # BUDGET STATUS NOTICE BANNER
    if remaining_cash_bhd >= 0:
        st.markdown(f"""
        <div class="summary-card-green">
            <b>🟢 WITHIN BUDGET STATUS:</b> You have available remaining income!<br/>
            <b>Net Unspent Cash Balance:</b> BD {remaining_cash_bhd:,.2f} &nbsp;|&nbsp; ₱ {remaining_cash_php:,.2f} PHP &nbsp;|&nbsp; ${remaining_cash_usd:,.2f} USD
        </div>
        """, unsafe_allow_html=True)
    else:
        over_bhd = abs(remaining_cash_bhd)
        over_php = abs(remaining_cash_php)
        over_usd = abs(remaining_cash_usd)
        st.markdown(f"""
        <div class="summary-card-red">
            <b>🚨 OVER BUDGET STATUS NOTICE:</b> Total payments exceed your monthly income limit!<br/>
            <b>Current Overage / Limit Deficit:</b> -BD {over_bhd:,.2f} &nbsp;|&nbsp; -₱ {over_php:,.2f} PHP &nbsp;|&nbsp; -${over_usd:,.2f} USD
        </div>
        """, unsafe_allow_html=True)

    # TOP METRICS CARDS
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Monthly Income", f"BD {total_income_bhd:,.2f}", delta=f"₱{total_income_php:,.0f} PHP")
    m2.metric("Total Expenses Billed", f"BD {total_billed_bhd:,.2f}", delta=f"Pending: BD {total_pending_bhd:,.2f}", delta_color="off")
    m3.metric("Total Actual Paid", f"BD {total_spent_bhd:,.2f}", delta=f"-BD {total_spent_bhd:,.2f}", delta_color="inverse")
    
    if remaining_cash_bhd >= 0:
        m4.metric("Remaining Net Cash", f"BD {remaining_cash_bhd:,.2f}", delta=f"₱{remaining_cash_php:,.0f} PHP")
    else:
        m4.metric("Over Budget Balance", f"-BD {abs(remaining_cash_bhd):,.2f}", delta=f"-₱{abs(remaining_cash_php):,.0f} PHP", delta_color="inverse")

    st.markdown("---")
    st.subheader("📊 50/30/20 Allocation Benchmark Breakdown")

    cat_data = [
        {"Category": "Needs (50%)", "Target Allocation": f"{needs_pct}%", "Target (BD)": needs_target_bhd, "Actual Paid (BD)": actual_needs_bhd, "Difference (BD)": needs_target_bhd - actual_needs_bhd, "Status": "On Track" if actual_needs_bhd <= needs_target_bhd else "Over Target"},
        {"Category": "Wants (30%)", "Target Allocation": f"{wants_pct}%", "Target (BD)": wants_target_bhd, "Actual Paid (BD)": actual_wants_bhd, "Difference (BD)": wants_target_bhd - actual_wants_bhd, "Status": "On Track" if actual_wants_bhd <= wants_target_bhd else "Over Target"},
        {"Category": "Savings & Debt (20%)", "Target Allocation": f"{savings_pct}%", "Target (BD)": savings_target_bhd, "Actual Paid (BD)": actual_savings_bhd, "Difference (BD)": savings_target_bhd - actual_savings_bhd, "Status": "Target Met" if actual_savings_bhd >= savings_target_bhd else "Under Goal"}
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
    # VISUAL CHARTS (Target vs Actual Bar & Expense Share Pie)
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🎯 Target vs. Actual Spending (BD)")
        chart_df = pd.DataFrame({
            "Category": ["Needs", "Wants", "Savings"],
            "Target": [needs_target_bhd, wants_target_bhd, savings_target_bhd],
            "Actual": [actual_needs_bhd, actual_wants_bhd, actual_savings_bhd]
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

    with c2:
        st.subheader("🥧 Actual Spending Share")
        if total_spent_bhd > 0:
            fig_pie = px.pie(
                values=[actual_needs_bhd, actual_wants_bhd, actual_savings_bhd, actual_priority_bhd, actual_debts_bhd],
                names=["Needs", "Wants", "Savings", "100% Priority", "Debts"],
                color_discrete_sequence=['#2563EB', '#F59E0B', '#10B981', '#DC2626', '#8B5CF6'],
                hole=0.45
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expense records logged yet. Add your first expense in the '➕ Record Expense' tab!")

# ---------------------------------------------------------
# TAB 2: RECORD NEW EXPENSE
# ---------------------------------------------------------
with tab_add:
    st.subheader("➕ Record a New Payment or Expense")

    col_cat1, col_cat2 = st.columns(2)
    with col_cat1:
        main_cat_choice = st.selectbox(
            "Select Main Category",
            ["100% Priority", "Debts & Credits", "Needs (50%)", "Wants (30%)", "Savings & Investments (20%)"],
            key="add_main_cat_select"
        )
    
    # Sub-categories mapping based on main category
    if "Priority" in main_cat_choice:
        sub_cat_options = ["Rent / Mortgage", "Essential Utilities", "Emergency Debt Repayment", "Family Remittance"]
    elif "Debts" in main_cat_choice:
        sub_cat_options = ["Credit Card Payment", "Bank Loan", "Personal Loan", "Interest Payment"]
    elif "Needs" in main_cat_choice:
        sub_cat_options = ["Groceries & Food", "Utilities & Bills", "Healthcare & Medicine", "Fuel & Transport", "Insurance"]
    elif "Wants" in main_cat_choice:
        sub_cat_options = ["Dining Out", "Shopping", "Entertainment & Subscriptions", "Travel & Hobbies", "Miscellaneous"]
    else:
        sub_cat_options = ["Emergency Fund", "Stock Investments", "Crypto / Trading", "Real Estate", "Long-term Savings"]

    with col_cat2:
        sub_cat_choice = st.selectbox("Select Sub-Category", sub_cat_options, key="add_sub_cat_select")

    st.markdown("---")

    with st.form("add_expense_form", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            exp_date = st.date_input("Date", value=datetime.today())
            merchant = st.text_input("Merchant / Description", placeholder="e.g. Electricity Bill, Car Fuel, Grocery Store")
            currency_choice = st.selectbox("Transaction Currency", ["BHD", "PHP", "USD"], index=0)
            
        with col_f2:
            billed_amount = st.number_input(f"Planned / Billed Amount ({currency_choice})", min_value=0.0, value=50.0, step=5.0)
            actual_paid = st.number_input(f"Actual Amount Paid ({currency_choice})", min_value=0.0, value=50.0, step=5.0)
            payment_method = st.selectbox("Payment Method", ["Benefit Pay", "Remittance", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])

        submit_btn = st.form_submit_button("💾 Save Expense Entry", use_container_width=True)

        if submit_btn:
            # Auto status determination
            if actual_paid >= billed_amount and billed_amount > 0:
                status_val = "Paid"
            elif actual_paid > 0:
                status_val = "Partially Paid"
            else:
                status_val = "Not Paid"

            new_row = pd.DataFrame([{
                "Date": exp_date,
                "Main Category": main_cat_choice,
                "Sub Category": sub_cat_choice,
                "Merchant/Description": merchant if merchant else "Unspecified",
                "Billed Amount": billed_amount,
                "Actual Paid": actual_paid,
                "Currency": currency_choice,
                "Status": status_val,
                "Payment Method": payment_method
            }])
            
            df_expenses = pd.concat([df_expenses, new_row], ignore_index=True)
            save_data(df_expenses)
            st.success(f"Successfully recorded {currency_choice} {actual_paid:,.2f} for '{merchant if merchant else sub_cat_choice}'!")
            st.rerun()

# ---------------------------------------------------------
# TAB 3: TRANSACTION HISTORY & LEDGER
# ---------------------------------------------------------
with tab_history:
    st.subheader("📋 Recorded Expense History & Transaction Ledger")

    # NOTICE BANNER ABOVE TABLE
    if remaining_cash_bhd >= 0:
        st.markdown(f"""
        <div class="summary-card-green">
            <b>🟢 WITHIN BUDGET STATUS:</b> You have available remaining income!<br/>
            <b>Net Unspent Cash Balance:</b> BD {remaining_cash_bhd:,.2f} &nbsp;|&nbsp; ₱ {remaining_cash_php:,.2f} PHP &nbsp;|&nbsp; ${remaining_cash_usd:,.2f} USD
        </div>
        """, unsafe_allow_html=True)
    else:
        over_bhd = abs(remaining_cash_bhd)
        over_php = abs(remaining_cash_php)
        over_usd = abs(remaining_cash_usd)
        st.markdown(f"""
        <div class="summary-card-red">
            <b>🚨 OVER BUDGET STATUS NOTICE:</b> Total payments exceed your monthly income limit!<br/>
            <b>Current Overage / Limit Deficit:</b> -BD {over_bhd:,.2f} &nbsp;|&nbsp; -₱ {over_php:,.2f} PHP &nbsp;|&nbsp; -${over_usd:,.2f} USD
        </div>
        """, unsafe_allow_html=True)

    if not df_expenses.empty:
        # Category Filter
        cat_options = ["100% Priority", "Debts & Credits", "Needs (50%)", "Wants (30%)", "Savings & Investments (20%)"]
        selected_cats = st.multiselect("Filter by Category", options=cat_options, default=cat_options)
        
        filtered_df = df_expenses[df_expenses["Main Category"].isin(selected_cats)] if selected_cats else df_expenses
        
        # Sort chronologically by date
        filtered_df = filtered_df.sort_values(by="Date", ascending=True).reset_index(drop=True)
        filtered_df.index = filtered_df.index + 1
        filtered_df.index.name = "Item #"
        
        # Compute dynamic derived columns for display
        df_display = filtered_df.copy()
        
        df_display["Billed Amount"] = pd.to_numeric(df_display["Billed Amount"], errors='coerce').fillna(0.0)
        df_display["Actual Paid"] = pd.to_numeric(df_display["Actual Paid"], errors='coerce').fillna(0.0)
        
        df_display["Pending Due"] = (df_display["Billed Amount"] - df_display["Actual Paid"]).clip(lower=0.0)
        
        def calc_pct_paid(row):
            b = row["Billed Amount"]
            a = row["Actual Paid"]
            return (a / b * 100.0) if b > 0 else (100.0 if a > 0 else 0.0)

        df_display["% Paid"] = df_display.apply(calc_pct_paid, axis=1)
        df_display["% Remaining"] = (100.0 - df_display["% Paid"]).clip(lower=0.0)

        def calc_equivalent(row):
            curr = str(row["Currency"]).upper().strip()
            p = row["Actual Paid"]
            if curr == "PHP":
                bhd_val = p / bhd_to_php
                usd_val = bhd_val * bhd_to_usd
                return f"BD {bhd_val:,.2f} | ${usd_val:,.2f}"
            elif curr == "USD":
                bhd_val = p / bhd_to_usd
                php_val = bhd_val * bhd_to_php
                return f"BD {bhd_val:,.2f} | ₱{php_val:,.2f}"
            else: # BHD
                php_val = p * bhd_to_php
                usd_val = p * bhd_to_usd
                return f"₱{php_val:,.2f} | ${usd_val:,.2f}"

        df_display["Equivalent"] = df_display.apply(calc_equivalent, axis=1)

        # -----------------------------------------------------
        # TABLE 1: EDITABLE TRANSACTION DATA EDITOR
        # -----------------------------------------------------
        st.subheader("✏️ Editable Transaction Ledger")
        st.caption("You can edit values directly in this table and click **'Save Ledger Changes'** below.")

        edited_df = st.data_editor(
            df_display,
            column_order=[
                "Date", "Main Category", "Sub Category", "Merchant/Description",
                "Billed Amount", "Actual Paid", "Currency", "Pending Due",
                "% Paid", "% Remaining", "Equivalent", "Status", "Payment Method"
            ],
            column_config={
                "Date": st.column_config.DateColumn("Date", required=True),
                "Main Category": st.column_config.SelectboxColumn("Main Category", options=cat_options, required=True),
                "Sub Category": st.column_config.TextColumn("Sub Category"),
                "Merchant/Description": st.column_config.TextColumn("Merchant/Description"),
                "Billed Amount": st.column_config.NumberColumn("Billed Amount", format="%.2f"),
                "Actual Paid": st.column_config.NumberColumn("Actual Paid", format="%.2f"),
                "Currency": st.column_config.SelectboxColumn("Currency", options=["BHD", "PHP", "USD"], required=True),
                "Pending Due": st.column_config.NumberColumn("Pending Due", format="%.2f", disabled=True),
                "% Paid": st.column_config.NumberColumn("% Paid", format="%.1f%%", disabled=True),
                "% Remaining": st.column_config.NumberColumn("% Remaining", format="%.1f%%", disabled=True),
                "Equivalent": st.column_config.TextColumn("Equivalent", disabled=True),
                "Status": st.column_config.SelectboxColumn("Status", options=["Paid", "Partially Paid", "Not Paid"], required=True),
                "Payment Method": st.column_config.SelectboxColumn("Payment Method", options=["Benefit Pay", "Remittance", "Bank Transfer", "Credit Card", "Debit Card", "Cash"], required=True)
            },
            use_container_width=True,
            num_rows="dynamic",
            key="ledger_data_editor"
        )

        if st.button("💾 Save Ledger Changes", type="primary"):
            save_df = edited_df.reset_index(drop=True)
            # Recompute auto status before saving
            def update_status(r):
                b = float(r["Billed Amount"])
                a = float(r["Actual Paid"])
                if a >= b and b > 0:
                    return "Paid"
                elif a > 0:
                    return "Partially Paid"
                else:
                    return "Not Paid"
            
            save_df["Status"] = save_df.apply(update_status, axis=1)
            cols_to_save = ["Date", "Main Category", "Sub Category", "Merchant/Description", "Billed Amount", "Actual Paid", "Currency", "Status", "Payment Method"]
            save_data(save_df[cols_to_save])
            st.success("Ledger changes saved successfully!")
            st.rerun()

        st.markdown("---")

        # -----------------------------------------------------
        # TABLE 2: COLOR-HIGHLIGHTED STATUS LEDGER VIEW
        # -----------------------------------------------------
        st.subheader("🎨 Status-Highlighted Color Ledger View")
        st.caption("🟢 Green = 100% Paid  |  🟡 Yellow = Partially Paid  |  🔴 Red = 0% Unpaid")

        def style_rows(row):
            pct = row["% Paid"]
            if pct >= 100.0:
                # Green
                return ['background-color: #D1FAE5; color: #065F46; font-weight: 600;'] * len(row)
            elif pct > 0.0:
                # Yellow
                return ['background-color: #FEF3C7; color: #92400E; font-weight: 600;'] * len(row)
            else:
                # Red
                return ['background-color: #FEE2E2; color: #991B1B; font-weight: 600;'] * len(row)

        styled_df = df_display.style.apply(style_rows, axis=1).format({
            "Billed Amount": "{:,.2f}",
            "Actual Paid": "{:,.2f}",
            "Pending Due": "{:,.2f}",
            "% Paid": "{:.1f}%",
            "% Remaining": "{:.1f}%"
        })

        st.dataframe(styled_df, use_container_width=True)

        st.markdown("---")

        # -----------------------------------------------------
        # SUMMARY CARDS BELOW TRANSACTIONS (HIGH CONTRAST)
        # -----------------------------------------------------
        st.subheader("💰 Total Outstanding & Payment Ledger Summary")

        # Separate PHP specific records vs BHD/USD records
        php_rows = df_display[df_display["Currency"] == "PHP"]
        php_billed = float(php_rows["Billed Amount"].sum()) if not php_rows.empty else 0.0
        php_paid = float(php_rows["Actual Paid"].sum()) if not php_rows.empty else 0.0
        php_pending = float(php_rows["Pending Due"].sum()) if not php_rows.empty else 0.0

        cnt_paid = len(df_display[df_display["Status"] == "Paid"])
        cnt_partial = len(df_display[df_display["Status"] == "Partially Paid"])
        cnt_unpaid = len(df_display[df_display["Status"] == "Not Paid"])

        col_s1, col_s2, col_s3 = st.columns(3)

        with col_s1:
            st.markdown(f"""
            <div class="summary-card-blue">
                <h4 style="margin:0 0 8px 0; color:#1E40AF !important;">📋 Total Billed / Needed</h4>
                <p style="margin:2px 0; font-weight:700; color:#1E3A8A !important; font-size:1.1rem;">
                    BD {total_billed_bhd:,.2f}
                </p>
                <p style="margin:2px 0; font-size:0.85rem; color:#1E40AF !important;">
                    <b>🇵🇭 PHP Records:</b> ₱{php_billed:,.2f} PHP (BD {php_billed/bhd_to_php:,.2f})
                </p>
                <p style="margin:2px 0; font-size:0.85rem; color:#1E40AF !important;">
                    <b>Grand Total:</b> ₱{total_billed_bhd*bhd_to_php:,.2f} PHP | ${total_billed_bhd*bhd_to_usd:,.2f} USD
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col_s2:
            st.markdown(f"""
            <div class="summary-card-green">
                <h4 style="margin:0 0 8px 0; color:#166534 !important;">🟢 Total Actual Paid</h4>
                <p style="margin:2px 0; font-weight:700; color:#065F46 !important; font-size:1.1rem;">
                    BD {total_spent_bhd:,.2f}
                </p>
                <p style="margin:2px 0; font-size:0.85rem; color:#166534 !important;">
                    <b>🇵🇭 PHP Records:</b> ₱{php_paid:,.2f} PHP (BD {php_paid/bhd_to_php:,.2f})
                </p>
                <p style="margin:2px 0; font-size:0.85rem; color:#166534 !important;">
                    <b>Grand Total:</b> ₱{total_spent_bhd*bhd_to_php:,.2f} PHP | ${total_spent_bhd*bhd_to_usd:,.2f} USD
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col_s3:
            st.markdown(f"""
            <div class="summary-card-red">
                <h4 style="margin:0 0 8px 0; color:#991B1B !important;">🔴 Total Pending Remaining</h4>
                <p style="margin:2px 0; font-weight:700; color:#7F1D1D !important; font-size:1.1rem;">
                    BD {total_pending_bhd:,.2f}
                </p>
                <p style="margin:2px 0; font-size:0.85rem; color:#991B1B !important;">
                    <b>🇵🇭 PHP Records:</b> ₱{php_pending:,.2f} PHP (BD {php_pending/bhd_to_php:,.2f})
                </p>
                <p style="margin:2px 0; font-size:0.85rem; color:#991B1B !important;">
                    <b>Grand Total:</b> ₱{total_pending_bhd*bhd_to_php:,.2f} PHP | ${total_pending_bhd*bhd_to_usd:,.2f} USD
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="summary-card-blue" style="text-align: center; padding: 10px !important;">
            <b>📊 Payment Status Counts:</b> &nbsp;&nbsp;
            <span style="color:#166534; font-weight:700;">🟢 Paid: {cnt_paid}</span> &nbsp;|&nbsp; 
            <span style="color:#B45309; font-weight:700;">🟡 Partially Paid: {cnt_partial}</span> &nbsp;|&nbsp; 
            <span style="color:#991B1B; font-weight:700;">🔴 Not Paid: {cnt_unpaid}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🗑️ Clear All Expense Data", type="primary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.success("All transaction records cleared successfully!")
            st.rerun()
    else:
        st.info("No transaction history records found. Start adding expenses in the '➕ Record Expense' tab!")

# ---------------------------------------------------------
# TAB 4: 12-MONTH PROJECTIONS & SAVINGS ENGINE
# ---------------------------------------------------------
with tab_proj:
    st.subheader("🔮 12-Month Projected Budgeting & Savings Engine")
    st.markdown("Forecast your monthly expenses, income growth, inflation, and future savings potential over the next 12 months.")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        proj_base_income = st.number_input("Base Projected Monthly Income (BD)", min_value=0.0, value=total_income_bhd if total_income_bhd > 0 else 1500.0, step=50.0)
        proj_income_growth = st.slider("Expected Annual Income Growth (%)", 0.0, 20.0, 3.0, step=0.5)
        proj_fixed_needs = st.number_input("Projected Fixed Monthly Needs/Debts (BD)", min_value=0.0, value=actual_needs_bhd + actual_priority_bhd + actual_debts_bhd if (actual_needs_bhd + actual_priority_bhd + actual_debts_bhd) > 0 else 700.0, step=25.0)

    with col_p2:
        proj_inflation = st.slider("Annual Inflation Rate (%)", 0.0, 10.0, 2.5, step=0.5)
        proj_wants = st.number_input("Projected Lifestyle Allowance (BD)", min_value=0.0, value=actual_wants_bhd if actual_wants_bhd > 0 else 300.0, step=20.0)
        proj_monthly_target_savings = st.number_input("Target Monthly Savings Contribution (BD)", min_value=0.0, value=actual_savings_bhd if actual_savings_bhd > 0 else 300.0, step=25.0)

    # 12-Month Calculation Matrix
    months_list = [f"Month {m}" for m in range(1, 13)]
    proj_rows = []
    
    cumulative_savings = 0.0

    for m in range(1, 13):
        monthly_growth = (proj_income_growth / 100.0) * ((m - 1) / 12.0)
        monthly_income = proj_base_income * (1.0 + monthly_growth)
        
        monthly_inflation = (proj_inflation / 100.0) * ((m - 1) / 12.0)
        monthly_needs = proj_fixed_needs * (1.0 + monthly_inflation)
        monthly_wants = proj_wants * (1.0 + monthly_inflation)
        
        total_exp = monthly_needs + monthly_wants
        net_surplus = monthly_income - total_exp
        cumulative_savings += net_surplus

        proj_rows.append({
            "Month": f"Month {m}",
            "Income (BD)": monthly_income,
            "Needs & Debts (BD)": monthly_needs,
            "Lifestyle (BD)": monthly_wants,
            "Total Expenses (BD)": total_exp,
            "Net Surplus (BD)": net_surplus,
            "Cumulative Savings (BD)": cumulative_savings
        })

    df_proj = pd.DataFrame(proj_rows)

    tot_1yr_income = df_proj["Income (BD)"].sum()
    tot_1yr_expenses = df_proj["Total Expenses (BD)"].sum()
    tot_1yr_savings = df_proj["Net Surplus (BD)"].sum()

    st.markdown("---")
    pm1, pm2, pm3 = st.columns(3)
    pm1.metric("1-Year Projected Income", f"BD {tot_1yr_income:,.2f}", delta=f"₱{tot_1yr_income*bhd_to_php:,.0f} PHP")
    pm2.metric("1-Year Projected Expenses", f"BD {tot_1yr_expenses:,.2f}", delta=f"₱{tot_1yr_expenses*bhd_to_php:,.0f} PHP", delta_color="inverse")
    pm3.metric("1-Year Savings Potential", f"BD {tot_1yr_savings:,.2f}", delta=f"₱{tot_1yr_savings*bhd_to_php:,.0f} PHP")

    st.markdown("---")
    st.subheader("📅 12-Month Projections Matrix")
    st.dataframe(
        df_proj.style.format({
            "Income (BD)": "BD {:,.2f}",
            "Needs & Debts (BD)": "BD {:,.2f}",
            "Lifestyle (BD)": "BD {:,.2f}",
            "Total Expenses (BD)": "BD {:,.2f}",
            "Net Surplus (BD)": "BD {:,.2f}",
            "Cumulative Savings (BD)": "BD {:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    pc1, pc2 = st.columns(2)

    with pc1:
        st.subheader("📈 Monthly Income vs. Expenses Forecast")
        fig_proj_bar = go.Figure(data=[
            go.Bar(name='Income', x=df_proj['Month'], y=df_proj['Income (BD)'], marker_color='#10B981'),
            go.Bar(name='Expenses', x=df_proj['Month'], y=df_proj['Total Expenses (BD)'], marker_color='#EF4444')
        ])
        fig_proj_bar.update_layout(barmode='group', margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_proj_bar, use_container_width=True)

    with pc2:
        st.subheader("💰 1-Year Cumulative Wealth Growth")
        fig_proj_line = px.line(
            df_proj, x='Month', y='Cumulative Savings (BD)',
            title="Cumulative Savings & Emergency Fund Growth",
            markers=True, color_discrete_sequence=['#2563EB']
        )
        fig_proj_line.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_proj_line, use_container_width=True)

# ---------------------------------------------------------
# TAB 5: MT5 PIP & MARGIN CALCULATOR
# ---------------------------------------------------------
with tab_pip:
    st.subheader("📈 MT5 Trading Pip & Margin Calculator")
    st.markdown("Calculate risk, pip value, and margin requirements for MetaTrader 5 trading across major currency pairs.")

    col_mt1, col_mt2 = st.columns(2)
    with col_mt1:
        pair_choice = st.selectbox(
            "Currency Pair / Symbol",
            ["USDPHP", "BHDPHP", "USDCAD", "EURUSD", "GBPUSD", "USDJPY", "XAUUSD (Gold)", "USDCHF", "AUDUSD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"],
            index=0
        )
        leverage = st.selectbox("Account Leverage", ["1:100", "1:200", "1:500", "1:1000"], index=2)
        lev_val = float(leverage.split(":")[1])
        lot_size = st.number_input("Lot Size (Volume)", min_value=0.01, max_value=100.0, value=0.10, step=0.01)

    with col_mt2:
        entry_price = st.number_input("Entry Price", min_value=0.0001, value=58.50 if "PHP" in pair_choice else (2700.0 if "XAU" in pair_choice else 1.0850), step=0.0001, format="%.4f")
        stop_loss_pips = st.number_input("Stop Loss (Pips)", min_value=1.0, value=30.0, step=1.0)

    # Pip value calculation logic
    if "PHP" in pair_choice:
        pip_size = 0.01
        contract_size = 100000
        pip_val_usd = (pip_size / entry_price) * contract_size * lot_size if entry_price > 0 else 0.0
    elif "XAU" in pair_choice:
        pip_size = 0.10
        contract_size = 100
        pip_val_usd = pip_size * contract_size * lot_size
    elif "JPY" in pair_choice:
        pip_size = 0.01
        contract_size = 100000
        pip_val_usd = (pip_size / entry_price) * contract_size * lot_size if entry_price > 0 else 0.0
    else:
        pip_size = 0.0001
        contract_size = 100000
        pip_val_usd = pip_size * contract_size * lot_size

    required_margin_usd = (contract_size * lot_size * entry_price) / lev_val if lev_val > 0 else 0.0
    total_risk_usd = pip_val_usd * stop_loss_pips
    
    pip_val_bhd = pip_val_usd / bhd_to_usd
    total_risk_bhd = total_risk_usd / bhd_to_usd
    total_risk_php = total_risk_bhd * bhd_to_php

    st.markdown("---")
    tc1, tc2, tc3 = st.columns(3)
    tc1.metric("Pip Value", f"${pip_val_usd:,.2f} USD", delta=f"BD {pip_val_bhd:,.3f}")
    tc2.metric("Required Margin", f"${required_margin_usd:,.2f} USD", delta=f"BD {required_margin_usd/bhd_to_usd:,.2f}")
    tc3.metric("Total Trade Risk", f"${total_risk_usd:,.2f} USD", delta=f"BD {total_risk_bhd:,.2f} | ₱{total_risk_php:,.0f} PHP", delta_color="inverse")

# ---------------------------------------------------------
# TAB 6: DOWNLOAD REPORTS
# ---------------------------------------------------------
with tab_reports:
    st.subheader("📥 Download Financial Reports & Export Ledger")

    cr1, cr2 = st.columns(2)
    with cr1:
        st.markdown("#### 📊 Export CSV Transaction Ledger")
        if not df_expenses.empty:
            csv_data = df_expenses.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download CSV Ledger File",
                data=csv_data,
                file_name=f"financial_ledger_{current_user.lower().replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No transaction records available to export.")

    with cr2:
        st.markdown("#### 📜 Download Executive Financial Summary (.TXT)")
        rep_date = datetime.today().strftime("%Y-%m-%d")
        report_content = f"""
==================================================
ROGEE FINANCIAL COMMAND CENTER - EXECUTIVE REPORT
==================================================
User Profile   : {current_user}
Report Date    : {rep_date}
Bahrain Time   : {bh_time.strftime("%Y-%m-%d %I:%M %p")}
Philippine Time: {ph_time.strftime("%Y-%m-%d %I:%M %p")}
Exchange Rates : 1 BHD = {bhd_to_php:,.2f} PHP = ${bhd_to_usd:,.2f} USD

--------------------------------------------------
1. INCOME & CASH BALANCE SUMMARY
--------------------------------------------------
- Primary Salary         : BD {salary_bhd:,.2f}
- Business Income        : BD {business_bhd:,.2f}
- Sidelines / Freelance  : BD {sidelines_bhd:,.2f}
- Other Income           : BD {other_income_bhd:,.2f}
--------------------------------------------------
TOTAL COMBINED INCOME    : BD {total_income_bhd:,.2f}
   - Equivalent in PHP   : ₱ {total_income_php:,.2f} PHP
   - Equivalent in USD   : ${total_income_usd:,.2f} USD

--------------------------------------------------
2. EXPENSES & PAYMENTS SUMMARY
--------------------------------------------------
- Total Billed / Planned : BD {total_billed_bhd:,.2f}
- Total Actual Paid      : BD {total_spent_bhd:,.2f}
- Total Pending Balance  : BD {total_pending_bhd:,.2f}
--------------------------------------------------
NET UNSPENT CASH BALANCE : BD {remaining_cash_bhd:,.2f}
   - Equivalent in PHP   : ₱ {remaining_cash_php:,.2f} PHP
   - Equivalent in USD   : ${remaining_cash_usd:,.2f} USD
==================================================
"""
        st.download_button(
            label="📥 Download Executive Summary Report",
            data=report_content,
            file_name=f"executive_report_{current_user.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# ---------------------------------------------------------
# TAB 7: SECURITY & DEPLOYMENT GUIDE
# ---------------------------------------------------------
with tab_guide:
    st.subheader("📘 Security & Streamlit Secrets Setup")
    st.markdown("""
    ### 🔐 Configuring Passkeys on Streamlit Cloud:
    To configure custom private passkeys for your accounts:
    1. Go to your **Streamlit Community Cloud Dashboard**.
    2. Click on your deployed app settings and select **Secrets**.
    3. Enter your custom secrets in TOML format:
       ```toml
       ROGEE_KEY = "YourPrivatePasscode1"
       USER2_KEY = "YourPrivatePasscode2"
       USER3_KEY = "YourPrivatePasscode3"
       USER4_KEY = "YourPrivatePasscode4"
       ```
    4. Save your secrets. Your app will automatically authenticate using these custom keys!
    """)
