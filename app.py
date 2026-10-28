import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import os
import json
import base64

# Set Streamlit page config
st.set_page_config(
    page_title="Rogee Financial Command Center",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling with Dark/Light Mode High Contrast
st.markdown("""
<style>
    .main-header { font-size: 2.0rem; font-weight: 800; color: #1E3A8A; margin-bottom: 0.1rem; }
    .sub-header { font-size: 0.95rem; color: #4B5563; margin-bottom: 0.8rem; }
    
    .time-badge {
        background-color: #F3F4F6;
        border: 1px solid #D1D5DB;
        color: #1F2937 !important;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 12px;
        text-align: center;
    }

    .notice-within-budget {
        background-color: #ECFDF5;
        border: 2px solid #10B981;
        border-left: 6px solid #059669;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 16px;
        color: #064E3B !important;
    }
    .notice-within-budget h4 { margin: 0 0 4px 0; color: #065F46 !important; font-size: 1.1rem; }
    .notice-within-budget p { margin: 0; color: #047857 !important; font-weight: 700; font-size: 1.05rem; }

    .notice-over-budget {
        background-color: #FEF2F2;
        border: 2px solid #EF4444;
        border-left: 6px solid #DC2626;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 16px;
        color: #7F1D1D !important;
    }
    .notice-over-budget h4 { margin: 0 0 4px 0; color: #991B1B !important; font-size: 1.1rem; }
    .notice-over-budget p { margin: 0; color: #B91C1C !important; font-weight: 700; font-size: 1.05rem; }

    /* Summary Cards Below Transactions - HIGH CONTRAST READABLE TEXT */
    .summary-card-billed {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-left: 5px solid #2563EB;
        padding: 14px;
        border-radius: 8px;
        color: #1E3A8A !important;
    }
    .summary-card-billed h4 { margin: 0 0 6px 0; color: #1E40AF !important; font-size: 1.05rem; font-weight: 700; }
    .summary-card-billed .sum-val { font-size: 1.25rem; font-weight: 800; color: #1E3A8A !important; }
    .summary-card-billed .sum-sub { font-size: 0.9rem; color: #1D4ED8 !important; font-weight: 600; }

    .summary-card-paid {
        background-color: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-left: 5px solid #16A34A;
        padding: 14px;
        border-radius: 8px;
        color: #14532D !important;
    }
    .summary-card-paid h4 { margin: 0 0 6px 0; color: #166534 !important; font-size: 1.05rem; font-weight: 700; }
    .summary-card-paid .sum-val { font-size: 1.25rem; font-weight: 800; color: #14532D !important; }
    .summary-card-paid .sum-sub { font-size: 0.9rem; color: #15803D !important; font-weight: 600; }

    .summary-card-due {
        background-color: #FEF2F2;
        border: 1px solid #FECACA;
        border-left: 5px solid #DC2626;
        padding: 14px;
        border-radius: 8px;
        color: #7F1D1D !important;
    }
    .summary-card-due h4 { margin: 0 0 6px 0; color: #991B1B !important; font-size: 1.05rem; font-weight: 700; }
    .summary-card-due .sum-val { font-size: 1.25rem; font-weight: 800; color: #7F1D1D !important; }
    .summary-card-due .sum-sub { font-size: 0.9rem; color: #B91C1C !important; font-weight: 600; }

    .php-highlight-box {
        background-color: #FFFBEB;
        border: 1px solid #FDE68A;
        border-left: 4px solid #D97706;
        padding: 10px 14px;
        border-radius: 6px;
        margin-top: 10px;
        color: #78350F !important;
        font-weight: 600;
    }
    .php-highlight-box p { margin: 2px 0; color: #78350F !important; }

    .stMetric { background-color: #F9FAFB !important; padding: 10px; border-radius: 6px; border: 1px solid #E5E7EB !important; }
    div[data-testid="stMetricValue"] { font-size: 1.2rem !important; font-weight: 800 !important; color: #1E3A8A !important; }
    div[data-testid="stMetricLabel"] { color: #374151 !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

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

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = "Rogee"

if not st.session_state.authenticated:
    st.markdown('<div class="main-header">🔒 Rogee Financial Command Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Please authenticate with your user profile passkey to access your financial dashboard.</div>', unsafe_allow_html=True)
    
    col_l1, col_l2 = st.columns([1, 1])
    with col_l1:
        selected_user = st.selectbox("Select User Profile", list(USER_PROFILES.keys()), index=0)
        entered_pass = st.text_input("Enter Passcode", type="password")
        
        prof_info = USER_PROFILES[selected_user]
        expected_pass = st.secrets.get(prof_info["sec_key"], prof_info["def_key"])
        
        if st.button("🔓 Authenticate & Access Dashboard", type="primary", use_container_width=True):
            if entered_pass == expected_pass:
                st.session_state.authenticated = True
                st.session_state.current_user = selected_user
                st.success(f"Welcome back, {selected_user}!")
                st.rerun()
            else:
                st.error("Invalid passcode. Please try again.")
    st.stop()

current_user = st.session_state.current_user
user_cfg = USER_PROFILES[current_user]
DATA_FILE = user_cfg["data_file"]
CONFIG_FILE = user_cfg["config_file"]

bhd_to_php = 148.50
bhd_to_usd = 2.6525

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            if "Billed Amount" not in df.columns and "Amount" in df.columns:
                df.rename(columns={"Amount": "Billed Amount"}, inplace=True)
            if "Actual Paid" not in df.columns:
                df["Actual Paid"] = df["Billed Amount"]
            if "Currency" not in df.columns:
                df["Currency"] = "BHD"
            if "Status" not in df.columns:
                df["Status"] = "Paid"
            if "Payment Method" not in df.columns:
                df["Payment Method"] = "Bank Transfer"
            df["Date"] = pd.to_datetime(df["Date"]).dt.date
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=[
        "Item #", "Date", "Main Category", "Sub Category", "Merchant/Description",
        "Billed Amount", "Actual Paid", "Currency", "Pending Due", "% Paid", "% Remaining",
        "Equivalent", "Status", "Payment Method"
    ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df_expenses = load_data()

# Sidebar Settings
st.sidebar.title(f"⚙️ {current_user}'s Settings")
if st.sidebar.button("🔒 Lock Portal / Sign Out", use_container_width=True):
    st.session_state.authenticated = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("💵 Monthly Take-Home Income")
salary_bhd = st.sidebar.number_input("Primary Salary (BHD)", min_value=0.0, value=1200.0, step=50.0)
business_bhd = st.sidebar.number_input("Business Income (BHD)", min_value=0.0, value=0.0, step=50.0)
sidelines_bhd = st.sidebar.number_input("Sidelines / Freelance (BHD)", min_value=0.0, value=0.0, step=50.0)
other_income_bhd = st.sidebar.number_input("Other Income / Bonuses (BHD)", min_value=0.0, value=0.0, step=50.0)

total_income_bhd = salary_bhd + business_bhd + sidelines_bhd + other_income_bhd
total_income_php = total_income_bhd * bhd_to_php
total_income_usd = total_income_bhd * bhd_to_usd

st.sidebar.markdown(f"""
<div style="background-color: #F0FDF4; border: 1px solid #BBF7D0; border-left: 4px solid #16A34A; padding: 10px; border-radius: 6px; margin: 10px 0;">
    <div style="font-size: 0.8rem; font-weight: 700; color: #166534;">TOTAL COMBINED MONTHLY INCOME</div>
    <div style="font-size: 1.15rem; font-weight: 800; color: #14532D;">BD {total_income_bhd:,.2f}</div>
    <div style="font-size: 0.82rem; font-weight: 600; color: #15803D;">₱ {total_income_php:,.2f} | $ {total_income_usd:,.2f}</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 50/30/20 Benchmark Allocation")
needs_pct = st.sidebar.slider("Needs Target % (Essentials)", 0, 100, 50)
wants_pct = st.sidebar.slider("Wants Target % (Lifestyle)", 0, 100, 30)
savings_pct = st.sidebar.slider("Savings Target % (Goals/Debt)", 0, 100, 20)

needs_target_bhd = total_income_bhd * (needs_pct / 100.0)
wants_target_bhd = total_income_bhd * (wants_pct / 100.0)
savings_target_bhd = total_income_bhd * (savings_pct / 100.0)

st.markdown('<div class="main-header">Rogee Financial Command Center</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Personal Finance & Salary Budgeting Dashboard | 50/30/20 Framework</div>', unsafe_allow_html=True)

now_utc = datetime.now(timezone.utc)
bh_time = now_utc + timedelta(hours=3)
ph_time = now_utc + timedelta(hours=8)

st.markdown(f"""
<div class="time-badge">
    🇧🇭 <b>Bahrain Time:</b> {bh_time.strftime("%d %b %Y, %I:%M %p")} AST &nbsp;|&nbsp; 
    🇵🇭 <b>Philippine Time:</b> {ph_time.strftime("%d %b %Y, %I:%M %p")} PHT &nbsp;|&nbsp;
    👤 <b>Account Profile:</b> {current_user}
</div>
""", unsafe_allow_html=True)

# Helper function to convert any transaction row amount to BHD
def row_to_bhd(amount, curr):
    amt = float(amount) if pd.notnull(amount) else 0.0
    c = str(curr).upper() if pd.notnull(curr) else "BHD"
    if c == "PHP":
        return amt / bhd_to_php
    elif c == "USD":
        return amt / bhd_to_usd
    return amt

# Calculate totals converted to BHD
total_billed_bhd = 0.0
total_spent_bhd = 0.0
total_pending_bhd = 0.0

actual_needs_bhd = 0.0
actual_wants_bhd = 0.0
actual_savings_bhd = 0.0
actual_priority_bhd = 0.0
actual_debts_bhd = 0.0

if not df_expenses.empty:
    for _, r in df_expenses.iterrows():
        b_amt = float(r.get("Billed Amount", 0.0))
        p_amt = float(r.get("Actual Paid", 0.0))
        curr = str(r.get("Currency", "BHD"))
        
        b_bhd = row_to_bhd(b_amt, curr)
        p_bhd = row_to_bhd(p_amt, curr)
        d_bhd = max(0.0, b_bhd - p_bhd)
        
        total_billed_bhd += b_bhd
        total_spent_bhd += p_bhd
        total_pending_bhd += d_bhd
        
        cat = str(r.get("Main Category", ""))
        if "Needs" in cat: actual_needs_bhd += p_bhd
        elif "Wants" in cat: actual_wants_bhd += p_bhd
        elif "Savings" in cat: actual_savings_bhd += p_bhd
        elif "Priority" in cat: actual_priority_bhd += p_bhd
        elif "Debts" in cat: actual_debts_bhd += p_bhd

remaining_cash_bhd = total_income_bhd - total_spent_bhd
remaining_cash_php = remaining_cash_bhd * bhd_to_php
remaining_cash_usd = remaining_cash_bhd * bhd_to_usd

# Tabs
tab_dash, tab_add, tab_history, tab_proj, tab_calc, tab_reports, tab_guide = st.tabs([
    "📊 Dashboard & Analytics",
    "➕ Record Expense",
    "📋 Transaction History",
    "🔮 12-Month Projections",
    "📈 MT5 Pip Calculator",
    "📥 Download Reports",
    "📘 Security Guide"
])

# TAB 1: DASHBOARD
with tab_dash:
    if remaining_cash_bhd < 0:
        over_bhd = abs(remaining_cash_bhd)
        st.markdown(f"""
        <div class="notice-over-budget">
            <h4>🚨 OVER BUDGET WARNING!</h4>
            <p>Your total payments exceed your combined monthly income by <b>BD {over_bhd:,.2f}</b> (₱ {over_bhd * bhd_to_php:,.2f} | $ {over_bhd * bhd_to_usd:,.2f}).</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="notice-within-budget">
            <h4>🟢 BUDGET STATUS: WITHIN BUDGET</h4>
            <p>Net Surplus Cash Balance: <b>BD {remaining_cash_bhd:,.2f}</b> (₱ {remaining_cash_php:,.2f} | $ {remaining_cash_usd:,.2f})</p>
        </div>
        """, unsafe_allow_html=True)

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Monthly Combined Income", f"BD {total_income_bhd:,.2f}", delta=f"₱ {total_income_php:,.0f}")
    d2.metric("Total Actual Paid", f"BD {total_spent_bhd:,.2f}", delta=f"-BD {total_spent_bhd:,.2f}", delta_color="inverse")
    d3.metric("Total Expenses Billed", f"BD {total_billed_bhd:,.2f}", delta=f"Pending: BD {total_pending_bhd:,.2f}", delta_color="off")
    
    if remaining_cash_bhd >= 0:
        d4.metric("Net Cash Surplus", f"BD {remaining_cash_bhd:,.2f}", delta="Within Income Limit")
    else:
        d4.metric("Over Budget Overage", f"-BD {abs(remaining_cash_bhd):,.2f}", delta="OVER BUDGET LIMIT", delta_color="inverse")

    st.markdown("---")
    st.subheader("📊 50/30/20 Allocation & Category Performance")
    
    cat_summary_data = [
        {"Category": "Mandatory 100% Priority", "Target (BHD)": actual_priority_bhd, "Actual Paid (BHD)": actual_priority_bhd, "Status": "Fixed Obligation"},
        {"Category": "Debts & Credits", "Target (BHD)": actual_debts_bhd, "Actual Paid (BHD)": actual_debts_bhd, "Status": "Credit Payment"},
        {"Category": f"Needs ({needs_pct}% Target)", "Target (BHD)": needs_target_bhd, "Actual Paid (BHD)": actual_needs_bhd, "Status": "On Track" if actual_needs_bhd <= needs_target_bhd else "Over Target"},
        {"Category": f"Wants ({wants_pct}% Target)", "Target (BHD)": wants_target_bhd, "Actual Paid (BHD)": actual_wants_bhd, "Status": "On Track" if actual_wants_bhd <= wants_target_bhd else "Over Target"},
        {"Category": f"Savings ({savings_pct}% Target)", "Target (BHD)": savings_target_bhd, "Actual Paid (BHD)": actual_savings_bhd, "Status": "Goal Met" if actual_savings_bhd >= savings_target_bhd else "Under Goal"}
    ]
    st.dataframe(pd.DataFrame(cat_summary_data), use_container_width=True, hide_index=True)

    ch1, ch2 = st.columns(2)
    with ch1:
        st.subheader("Target vs. Actual Spending (BHD)")
        df_bar = pd.DataFrame({
            "Category": ["Needs", "Wants", "Savings"],
            "Target": [needs_target_bhd, wants_target_bhd, savings_target_bhd],
            "Actual": [actual_needs_bhd, actual_wants_bhd, actual_savings_bhd]
        })
        fig_b = go.Figure(data=[
            go.Bar(name='Target', x=df_bar['Category'], y=df_bar['Target'], marker_color='#93C5FD'),
            go.Bar(name='Actual', x=df_bar['Category'], y=df_bar['Actual'], marker_color='#1D4ED8')
        ])
        fig_b.update_layout(barmode='group', margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_b, use_container_width=True)

    with ch2:
        st.subheader("Expense Distribution by Category")
        if total_spent_bhd > 0:
            fig_p = px.pie(
                values=[actual_priority_bhd, actual_debts_bhd, actual_needs_bhd, actual_wants_bhd, actual_savings_bhd],
                names=["100% Priority", "Debts", "Needs", "Wants", "Savings"],
                hole=0.4
            )
            fig_p.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_p, use_container_width=True)
        else:
            st.info("No expense data logged yet.")

# TAB 2: RECORD EXPENSE
with tab_add:
    st.subheader("➕ Record a New Expense or Payment")
    
    sel_main_cat = st.selectbox(
        "Select 50/30/20 Main Category",
        ["100% Priority Payments", "Debts & Credits", "Needs (50%)", "Wants (30%)", "Savings & Debt (20%)"],
        key="add_main_cat_key"
    )
    
    if "Priority" in sel_main_cat:
        sub_opts = ["Rent / Mortgage", "Utilities (Electricity/Water)", "Family Remittance", "Insurance / Tuition"]
    elif "Debts" in sel_main_cat:
        sub_opts = ["Credit Card Payment", "Bank Loan Repayment", "Personal Loan", "Store Credit"]
    elif "Needs" in sel_main_cat:
        sub_opts = ["Groceries & Food", "Transportation & Fuel", "Healthcare & Pharmacy", "Mobile & Internet"]
    elif "Wants" in sel_main_cat:
        sub_opts = ["Dining Out & Coffee", "Shopping & Clothes", "Entertainment & Streaming", "Travel & Hobbies"]
    else:
        sub_opts = ["Emergency Savings", "Investment Fund", "Retirement Account", "Extra Debt Payoff"]

    sub_cat_val = st.selectbox("Select Sub-Category", sub_opts, key="add_sub_cat_key")

    with st.form("expense_record_form", clear_on_submit=True):
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            rec_date = st.date_input("Transaction Date", value=datetime.today())
            merchant_desc = st.text_input("Merchant / Description", placeholder="e.g. Utility Company, Grocery Store")
            tx_currency = st.selectbox("Transaction Currency", ["BHD", "PHP", "USD"], index=0)

        with fcol2:
            billed_val = st.number_input(f"Planned / Billed Amount ({tx_currency})", min_value=0.01, value=100.0, step=10.0)
            status_val = st.selectbox("Payment Status", ["Paid (100%)", "Not Paid (0%)", "Partially Paid"])
            
            def_actual = billed_val if status_val == "Paid (100%)" else (0.0 if status_val == "Not Paid (0%)" else billed_val * 0.5)
            actual_paid_val = st.number_input(f"Actual Amount Paid ({tx_currency})", min_value=0.0, value=def_actual, step=5.0)
            pay_method = st.selectbox("Payment Method", ["Benefit Pay", "Remittance", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])

        submit_tx = st.form_submit_button("💾 Save Transaction Entry", use_container_width=True)

        if submit_tx:
            b_val = float(billed_val)
            a_val = float(actual_paid_val)
            p_due = max(0.0, b_val - a_val)
            pct_paid = (a_val / b_val * 100.0) if b_val > 0 else 0.0
            pct_rem = max(0.0, 100.0 - pct_paid)
            
            if pct_paid >= 99.99: final_st = "Paid"
            elif pct_paid <= 0.01: final_st = "Not Paid"
            else: final_st = "Partially Paid"

            if tx_currency == "PHP":
                eq_str = f"BD {b_val / bhd_to_php:,.2f} | $ {b_val / 56.0:,.2f}"
            elif tx_currency == "USD":
                eq_str = f"BD {b_val / bhd_to_usd:,.2f} | ₱ {b_val * 56.0:,.2f}"
            else:
                eq_str = f"₱ {b_val * bhd_to_php:,.2f} | $ {b_val * bhd_to_usd:,.2f}"

            new_entry = pd.DataFrame([{
                "Item #": len(df_expenses) + 1,
                "Date": rec_date,
                "Main Category": sel_main_cat,
                "Sub Category": sub_cat_val,
                "Merchant/Description": merchant_desc if merchant_desc else sub_cat_val,
                "Billed Amount": b_val,
                "Actual Paid": a_val,
                "Currency": tx_currency,
                "Pending Due": p_due,
                "% Paid": f"{pct_paid:.1f}%",
                "% Remaining": f"{pct_rem:.1f}%",
                "Equivalent": eq_str,
                "Status": final_st,
                "Payment Method": pay_method
            }])
            df_expenses = pd.concat([df_expenses, new_entry], ignore_index=True)
            save_data(df_expenses)
            st.success(f"Saved {tx_currency} {b_val:,.2f} for '{merchant_desc if merchant_desc else sub_cat_val}'!")
            st.rerun()

# TAB 3: TRANSACTION HISTORY
with tab_history:
    st.subheader("📋 Recorded Expense & Transaction History Ledger")
    
    # REQUIREMENT 2: NOTICE ABOVE TRANSACTIONS TABLE
    if remaining_cash_bhd < 0:
        over_bhd = abs(remaining_cash_bhd)
        st.markdown(f"""
        <div class="notice-over-budget">
            <h4>🚨 OVER BUDGET NOTICE (LIMIT EXCEEDED)</h4>
            <p>You are currently over your budget limit by <b>-BD {over_bhd:,.2f}</b> (₱ {-over_bhd * bhd_to_php:,.2f} | -$ {-over_bhd * bhd_to_usd:,.2f}). Please review your unpaid bills below.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="notice-within-budget">
            <h4>🟢 BUDGET STATUS: WITHIN BUDGET</h4>
            <p>Remaining Net Cash Balance: <b>BD {remaining_cash_bhd:,.2f}</b> (₱ {remaining_cash_php:,.2f} | $ {remaining_cash_usd:,.2f}) available for future expenses or savings.</p>
        </div>
        """, unsafe_allow_html=True)

    if not df_expenses.empty:
        # Categorical grouping and date sorting
        cat_order = {"100% Priority Payments": 1, "Debts & Credits": 2, "Needs (50%)": 3, "Wants (30%)": 4, "Savings & Debt (20%)": 5}
        df_expenses["cat_rank"] = df_expenses["Main Category"].map(lambda x: cat_order.get(x, 99))
        df_sorted = df_expenses.sort_values(by=["cat_rank", "Date"], ascending=[True, True]).drop(columns=["cat_rank"])
        df_sorted["Item #"] = range(1, len(df_sorted) + 1)
        
        # Recalculate dynamic row columns
        display_rows = []
        for _, r in df_sorted.iterrows():
            b_val = float(r.get("Billed Amount", 0.0))
            a_val = float(r.get("Actual Paid", 0.0))
            curr = str(r.get("Currency", "BHD"))
            
            p_due = max(0.0, b_val - a_val)
            pct_paid = (a_val / b_val * 100.0) if b_val > 0 else 0.0
            pct_rem = max(0.0, 100.0 - pct_paid)
            
            if pct_paid >= 99.99: final_st = "Paid"
            elif pct_paid <= 0.01: final_st = "Not Paid"
            else: final_st = "Partially Paid"

            if curr == "PHP":
                eq_str = f"BD {b_val / bhd_to_php:,.2f} | $ {b_val / 56.0:,.2f}"
            elif curr == "USD":
                eq_str = f"BD {b_val / bhd_to_usd:,.2f} | ₱ {b_val * 56.0:,.2f}"
            else:
                eq_str = f"₱ {b_val * bhd_to_php:,.2f} | $ {b_val * bhd_to_usd:,.2f}"

            display_rows.append({
                "Item #": r["Item #"],
                "Date": r["Date"],
                "Main Category": r["Main Category"],
                "Sub Category": r["Sub Category"],
                "Merchant/Description": r["Merchant/Description"],
                "Billed Amount": b_val,
                "Actual Paid": a_val,
                "Currency": curr,
                "Pending Due": p_due,
                "% Paid": f"{pct_paid:.1f}%",
                "% Remaining": f"{pct_rem:.1f}%",
                "Equivalent": eq_str,
                "Status": final_st,
                "Payment Method": r["Payment Method"]
            })
        
        df_ledger = pd.DataFrame(display_rows)

        # Style function for table background colors
        def style_row_status(row):
            st_val = str(row["Status"])
            if st_val == "Paid":
                return ['background-color: #D1FAE5; color: #065F46; font-weight: 600;'] * len(row)
            elif st_val == "Partially Paid":
                return ['background-color: #FEF3C7; color: #92400E; font-weight: 600;'] * len(row)
            else:
                return ['background-color: #FEE2E2; color: #991B1B; font-weight: 600;'] * len(row)

        st.markdown("##### 🎨 Status-Highlighted Transaction Ledger (Editable Billed Amount & Actual Paid)")
        
        edited_df = st.data_editor(
            df_ledger.style.apply(style_row_status, axis=1),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Currency": st.column_config.SelectboxColumn("Currency", options=["BHD", "PHP", "USD"]),
                "Status": st.column_config.SelectboxColumn("Status", options=["Paid", "Not Paid", "Partially Paid"]),
                "Payment Method": st.column_config.SelectboxColumn("Payment Method", options=["Benefit Pay", "Remittance", "Bank Transfer", "Credit Card", "Debit Card", "Cash"])
            }
        )

        if st.button("💾 Save Ledger Changes", type="primary"):
            save_data(pd.DataFrame(edited_df))
            st.success("Ledger updated successfully!")
            st.rerun()

        st.markdown("---")
        
        # REQUIREMENT 1: SUMMARY BELOW TRANSACTIONS - HIGH CONTRAST & READABLE TEXT
        st.subheader("💰 Total Outstanding & Payment Ledger Summary")

        # Compute specific totals for PHP transactions and total transactions
        php_rows = df_ledger[df_ledger["Currency"] == "PHP"]
        php_billed = float(php_rows["Billed Amount"].sum()) if not php_rows.empty else 0.0
        php_paid = float(php_rows["Actual Paid"].sum()) if not php_rows.empty else 0.0
        php_due = float(php_rows["Pending Due"].sum()) if not php_rows.empty else 0.0

        col_s1, col_s2, col_s3 = st.columns(3)
        
        with col_s1:
            st.markdown(f"""
            <div class="summary-card-billed">
                <h4>📋 TOTAL BILLED / NEEDED</h4>
                <div class="sum-val">BD {total_billed_bhd:,.2f}</div>
                <div class="sum-sub">₱ {total_billed_bhd * bhd_to_php:,.2f} | $ {total_billed_bhd * bhd_to_usd:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_s2:
            st.markdown(f"""
            <div class="summary-card-paid">
                <h4>🟢 TOTAL ACTUAL PAID</h4>
                <div class="sum-val">BD {total_spent_bhd:,.2f}</div>
                <div class="sum-sub">₱ {total_spent_bhd * bhd_to_php:,.2f} | $ {total_spent_bhd * bhd_to_usd:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_s3:
            st.markdown(f"""
            <div class="summary-card-due">
                <h4>🔴 TOTAL REMAINING PENDING</h4>
                <div class="sum-val">BD {total_pending_bhd:,.2f}</div>
                <div class="sum-sub">₱ {total_pending_bhd * bhd_to_php:,.2f} | $ {total_pending_bhd * bhd_to_usd:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        # High contrast PHP specific transaction breakdown
        st.markdown(f"""
        <div class="php-highlight-box">
            <div style="font-size: 1.0rem; font-weight: 700; color: #78350F; margin-bottom: 4px;">🇵🇭 PHILIPPINE PESO (PHP) TRANSACTION RECORDS BREAKDOWN:</div>
            <p>• <b>PHP Total Billed Needed:</b> ₱ {php_billed:,.2f} &nbsp;(BD {php_billed / bhd_to_php:,.2f})</p>
            <p>• <b>PHP Total Actual Paid:</b> ₱ {php_paid:,.2f} &nbsp;(BD {php_paid / bhd_to_php:,.2f})</p>
            <p>• <b>PHP Total Pending Remaining:</b> ₱ {php_due:,.2f} &nbsp;(BD {php_due / bhd_to_php:,.2f})</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("⚠️ Clear All Ledger Records", type="secondary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.success("All transaction logs cleared!")
            st.rerun()

    else:
        st.info("No transaction history recorded yet. Add your first payment in '➕ Record Expense'!")

# TAB 4: 12-MONTH PROJECTIONS
with tab_proj:
    st.subheader("🔮 12-Month & Yearly Financial Budget Projections")
    st.markdown("Model your future monthly income, planned expenses, inflation impact, and projected cumulative savings over the next 12 months.")

    pcol1, pcol2, pcol3 = st.columns(3)
    with pcol1:
        proj_base_inc = st.number_input("Base Projected Income (BHD/mo)", min_value=0.0, value=total_income_bhd if total_income_bhd > 0 else 1200.0, step=50.0)
        proj_inc_growth = st.slider("Expected Annual Income Growth (%)", 0.0, 20.0, 3.0, 0.5)
    with pcol2:
        proj_fixed_exp = st.number_input("Projected Fixed Needs/Debts (BHD/mo)", min_value=0.0, value=total_billed_bhd * 0.6 if total_billed_bhd > 0 else 600.0, step=25.0)
        proj_inflation = st.slider("Expected Annual Inflation (%)", 0.0, 15.0, 2.5, 0.5)
    with pcol3:
        proj_discretionary = st.number_input("Projected Wants & Discretionary (BHD/mo)", min_value=0.0, value=250.0, step=25.0)
        proj_target_savings = st.number_input("Monthly Target Savings (BHD/mo)", min_value=0.0, value=250.0, step=25.0)

    proj_rows = []
    cum_savings = 0.0
    months_labels = ["Month 1", "Month 2", "Month 3", "Month 4", "Month 5", "Month 6", "Month 7", "Month 8", "Month 9", "Month 10", "Month 11", "Month 12"]
    
    for idx, m_name in enumerate(months_labels):
        inc_m = proj_base_inc * ((1 + (proj_inc_growth / 100.0) / 12) ** idx)
        exp_m = (proj_fixed_exp + proj_discretionary) * ((1 + (proj_inflation / 100.0) / 12) ** idx)
        surplus_m = inc_m - exp_m
        cum_savings += max(0.0, surplus_m)
        
        proj_rows.append({
            "Month": m_name,
            "Projected Income (BHD)": round(inc_m, 2),
            "Projected Expenses (BHD)": round(exp_m, 2),
            "Net Surplus / Savings (BHD)": round(surplus_m, 2),
            "Cumulative Wealth Savings (BHD)": round(cum_savings, 2),
            "Equivalent Cumulative (PHP)": f"₱ {cum_savings * bhd_to_php:,.2f}"
        })
    
    df_proj = pd.DataFrame(proj_rows)
    
    tot_proj_inc = df_proj["Projected Income (BHD)"].sum()
    tot_proj_exp = df_proj["Projected Expenses (BHD)"].sum()
    tot_proj_sav = df_proj["Net Surplus / Savings (BHD)"].sum()
    
    pm1, pm2, pm3 = st.columns(3)
    pm1.metric("Total 1-Year Projected Income", f"BD {tot_proj_inc:,.2f}", delta=f"₱ {tot_proj_inc * bhd_to_php:,.0f}")
    pm2.metric("Total 1-Year Projected Expenses", f"BD {tot_proj_exp:,.2f}", delta=f"₱ {tot_proj_exp * bhd_to_php:,.0f}")
    pm3.metric("Total 1-Year Projected Savings Potential", f"BD {tot_proj_sav:,.2f}", delta=f"₱ {tot_proj_sav * bhd_to_php:,.0f}")

    st.markdown("---")
    st.subheader("📊 12-Month Projected Growth & Wealth Accumulation Chart")
    
    fig_proj = go.Figure()
    fig_proj.add_trace(go.Bar(x=df_proj["Month"], y=df_proj["Projected Income (BHD)"], name="Projected Income", marker_color="#93C5FD"))
    fig_proj.add_trace(go.Bar(x=df_proj["Month"], y=df_proj["Projected Expenses (BHD)"], name="Projected Expenses", marker_color="#FCA5A5"))
    fig_proj.add_trace(go.Scatter(x=df_proj["Month"], y=df_proj["Cumulative Wealth Savings (BHD)"], name="Cumulative Savings", line=dict(color="#16A34A", width=4)))
    fig_proj.update_layout(barmode="group", margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_proj, use_container_width=True)

    st.dataframe(df_proj, use_container_width=True, hide_index=True)

# TAB 5: MT5 PIP CALCULATOR
with tab_calc:
    st.subheader("📈 MetaTrader 5 (MT5) Pip Value & Position Size Calculator")
    
    cc1, cc2 = st.columns(2)
    with cc1:
        pair = st.selectbox("Select Currency / Instrument Pair", ["USDPHP", "BHDPHP", "USDCAD", "EURUSD", "GBPUSD", "USDJPY", "XAUUSD (Gold)", "USDCHF", "AUDUSD", "NZDUSD"])
        account_bal_usd = st.number_input("Account Balance ($ USD)", min_value=10.0, value=1000.0, step=100.0)
        risk_pct = st.slider("Risk Per Trade (%)", 0.5, 10.0, 2.0, 0.5)
    with cc2:
        lot_size = st.number_input("Position Lot Size (Lots)", min_value=0.01, value=0.10, step=0.01)
        stop_loss_pips = st.number_input("Stop Loss Distance (Pips)", min_value=1.0, value=30.0, step=5.0)

    risk_amt_usd = account_bal_usd * (risk_pct / 100.0)
    
    if "JPY" in pair:
        pip_val_usd = lot_size * 10.0
    elif "XAU" in pair:
        pip_val_usd = lot_size * 10.0
    elif pair == "USDPHP":
        pip_val_usd = (lot_size * 100000.0 * 0.01) / 56.0
    elif pair == "BHDPHP":
        pip_val_usd = (lot_size * 100000.0 * 0.01) / 148.50
    else:
        pip_val_usd = lot_size * 10.0

    recommended_lot = (risk_amt_usd / (stop_loss_pips * (pip_val_usd / lot_size))) if stop_loss_pips > 0 else 0.01
    
    st.markdown("---")
    rc1, rc2, rc3 = st.columns(3)
    rc1.metric("Max Dollar Risk", f"${risk_amt_usd:,.2f}", delta=f"BD {risk_amt_usd / bhd_to_usd:,.2f}")
    rc2.metric(f"Pip Value ({pair})", f"${pip_val_usd:,.2f}", delta=f"For {lot_size} Lots")
    rc3.metric("Recommended Max Lot Size", f"{recommended_lot:.2f} Lots", delta="Based on Risk %")

# TAB 6: DOWNLOAD REPORTS
with tab_reports:
    st.subheader("📥 Download Financial Reports & CSV Data")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("#### 📊 CSV Transaction Ledger")
        if not df_expenses.empty:
            csv_data = df_expenses.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download CSV Ledger", data=csv_data, file_name=f"ledger_{current_user.lower()}.csv", mime="text/csv", use_container_width=True)
        else:
            st.info("No transaction data available.")
    with col_r2:
        st.markdown("#### 📜 Executive Financial Summary Report")
        rep_date = datetime.today().strftime("%Y-%m-%d")
        report_content = f"""
==================================================
ROGEE FINANCIAL COMMAND CENTER - EXECUTIVE REPORT
==================================================
User Profile   : {current_user}
Report Date    : {rep_date}
Bahrain Time   : {bh_time.strftime("%Y-%m-%d %I:%M %p")} AST
Philippine Time: {ph_time.strftime("%Y-%m-%d %I:%M %p")} PHT
Exchange Rate  : 1 BHD = {bhd_to_php:,.2f} PHP = ${bhd_to_usd:,.2f} USD

--------------------------------------------------
1. INCOME & CASH BALANCE SUMMARY
--------------------------------------------------
- Total Monthly Income : BD {total_income_bhd:,.2f} (₱ {total_income_php:,.2f} | $ {total_income_usd:,.2f})
- Total Billed Expenses: BD {total_billed_bhd:,.2f}
- Total Actual Paid    : BD {total_spent_bhd:,.2f}
- Total Pending Due    : BD {total_pending_bhd:,.2f}
- Net Cash Surplus     : BD {remaining_cash_bhd:,.2f} (₱ {remaining_cash_php:,.2f} | $ {remaining_cash_usd:,.2f})
==================================================
"""
        st.download_button("📥 Download Executive Summary (.TXT)", data=report_content, file_name=f"summary_{current_user.lower()}.txt", mime="text/plain", use_container_width=True)

# TAB 7: SECURITY GUIDE
with tab_guide:
    st.subheader("📘 Security & Configuration Guide")
    st.markdown("""
    ### 🔐 Passcode Setup Guide:
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
