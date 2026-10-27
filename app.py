import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Set Streamlit page config
st.set_page_config(
    page_title="Rogee's Financial Command Center",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for polished app feel
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 800; color: #1E3A8A; margin-bottom: 0.1rem; }
    .sub-header { font-size: 1.05rem; color: #4B5563; margin-bottom: 1.2rem; }
    .priority-banner { background-color: #FEF2F2; border: 1px solid #FECACA; border-left: 5px solid #EF4444; padding: 12px 16px; border-radius: 6px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "expenses.csv"

# Exchange rates relative to BHD (Base = 1 BHD)
EXCHANGE_RATES = {
    "BHD": {"symbol": "BD ", "rate": 1.0, "name": "Bahraini Dinar"},
    "PHP": {"symbol": "₱", "rate": 154.50, "name": "Philippine Peso"},
    "USD": {"symbol": "$", "rate": 2.65, "name": "US Dollar"}
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=["Date", "Main Category", "Sub Category", "Merchant/Description", "Amount", "Currency", "Amount (BHD)", "Payment Method"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df_expenses = load_data()

# Sidebar: User Settings
st.sidebar.title("⚙️ Command Center Settings")

display_curr = st.sidebar.selectbox("Display Currency", ["BHD (BD)", "PHP (₱)", "USD ($)"], index=0)
curr_code = display_curr.split()[0]
curr_symbol = EXCHANGE_RATES[curr_code]["symbol"]
rate_mult = EXCHANGE_RATES[curr_code]["rate"]

st.sidebar.markdown("---")
st.sidebar.subheader("💵 Income Settings (in BHD)")
bhd_salary = st.sidebar.number_input("Monthly Take-Home Salary (BHD)", min_value=0.0, value=1500.0, step=50.0)

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 100% Mandatory Payments & People to Pay")
st.sidebar.caption("Fixed 100% obligations (staff salary, family support, direct loans) deducted before 50/30/20 allocation.")
fixed_priority_bhd = st.sidebar.number_input("Mandatory 100% Payments Total (BHD)", min_value=0.0, value=300.0, step=25.0)

net_bhd_for_budget = max(0.0, bhd_salary - fixed_priority_bhd)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 50/30/20 Budget Allocations (%)")
st.sidebar.caption("Applied to remaining balance after 100% priority payments.")
needs_pct = st.sidebar.slider("Needs Target % (Essentials)", 0, 100, 50)
wants_pct = st.sidebar.slider("Wants Target % (Lifestyle)", 0, 100, 30)
savings_pct = st.sidebar.slider("Savings Target % (Goals/Debt)", 0, 100, 20)

total_pct = needs_pct + wants_pct + savings_pct
if total_pct != 100:
    st.sidebar.warning(f"Allocation total is {total_pct}%. It should sum to 100%.")

# Convert values for selected display currency
disp_salary = bhd_salary * rate_mult
disp_fixed = fixed_priority_bhd * rate_mult
disp_net_budget = net_bhd_for_budget * rate_mult

needs_target = disp_net_budget * (needs_pct / 100.0)
wants_target = disp_net_budget * (wants_pct / 100.0)
savings_target = disp_net_budget * (savings_pct / 100.0)

# Main Title Header
st.markdown('<div class="main-header">💰 Rogee&apos;s Financial Command Center</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multi-Currency Personal Finance Manager with 100% Mandatory Obligations & 50/30/20 Framework</div>', unsafe_allow_html=True)

# Income Equivalents Banner
eq_php = bhd_salary * EXCHANGE_RATES["PHP"]["rate"]
eq_usd = bhd_salary * EXCHANGE_RATES["USD"]["rate"]
st.info(f"💡 **Base Monthly Income Equivalents:** **{bhd_salary:,.2f} BHD** ≈ **₱{eq_php:,.2f} PHP** ≈ **${eq_usd:,.2f} USD**")

# Tabs
tab_dash, tab_add, tab_history, tab_calc, tab_guide = st.tabs([
    "📊 Dashboard & Analytics",
    "➕ Add Expense / Payment",
    "📜 Transaction History",
    "💱 Currency Converter",
    "📘 Deployment Guide"
])

# Calculate actual expenses in BHD
if not df_expenses.empty:
    actual_priority_bhd = df_expenses[df_expenses["Main Category"] == "100% Priority & People to Pay"]["Amount (BHD)"].sum()
    actual_needs_bhd = df_expenses[df_expenses["Main Category"] == "Needs (50%)"]["Amount (BHD)"].sum()
    actual_wants_bhd = df_expenses[df_expenses["Main Category"] == "Wants (30%)"]["Amount (BHD)"].sum()
    actual_savings_bhd = df_expenses[df_expenses["Main Category"] == "Savings & Debt (20%)"]["Amount (BHD)"].sum()
else:
    actual_priority_bhd = 0.0
    actual_needs_bhd = 0.0
    actual_wants_bhd = 0.0
    actual_savings_bhd = 0.0

total_spent_bhd = actual_priority_bhd + actual_needs_bhd + actual_wants_bhd + actual_savings_bhd
remaining_cash_bhd = bhd_salary - total_spent_bhd

# Convert actuals to display currency
actual_priority = actual_priority_bhd * rate_mult
actual_needs = actual_needs_bhd * rate_mult
actual_wants = actual_wants_bhd * rate_mult
actual_savings = actual_savings_bhd * rate_mult
total_spent = total_spent_bhd * rate_mult
remaining_cash = remaining_cash_bhd * rate_mult

# TAB 1: DASHBOARD
with tab_dash:
    # KPI Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Gross Monthly Income", f"{curr_symbol}{disp_salary:,.2f}")
    m2.metric("Total Spent / Paid", f"{curr_symbol}{total_spent:,.2f}", delta=f"-{curr_symbol}{total_spent:,.2f}", delta_color="inverse")
    m3.metric("Remaining Balance", f"{curr_symbol}{remaining_cash:,.2f}", delta=f"{curr_symbol}{remaining_cash:,.2f}")
    m4.metric("100% Mandatory Target", f"{curr_symbol}{disp_fixed:,.2f}")

    st.markdown("---")

    # Priority 100% Banner
    st.subheader("🚨 100% Mandatory Obligations & People to Pay")
    p_col1, p_col2 = st.columns([2, 1])
    with p_col1:
        priority_rem = disp_fixed - actual_priority
        if priority_rem > 0:
            st.warning(f"⚠️ **Pending 100% Payments:** {curr_symbol}{priority_rem:,.2f} remaining to be paid out of {curr_symbol}{disp_fixed:,.2f} budget.")
        else:
            st.success(f"✅ **100% Priority Payments Settled:** {curr_symbol}{actual_priority:,.2f} paid!")
    with p_col2:
        progress_val = min(1.0, max(0.0, actual_priority / disp_fixed if disp_fixed > 0 else 1.0))
        st.progress(progress_val, text=f"Priority Paid: {progress_val*100:.1f}%")

    st.markdown("---")

    st.subheader("📊 50/30/20 Budget Breakdown (From Remaining Disposable Income)")
    cat_data = [
        {"Category": "Needs (50%)", "Target Allocation": f"{needs_pct}%", f"Target ({curr_code})": needs_target, f"Actual Spent ({curr_code})": actual_needs, f"Remaining ({curr_code})": needs_target - actual_needs, "Status": "On Track" if actual_needs <= needs_target else "Over Budget"},
        {"Category": "Wants (30%)", "Target Allocation": f"{wants_pct}%", f"Target ({curr_code})": wants_target, f"Actual Spent ({curr_code})": actual_wants, f"Remaining ({curr_code})": wants_target - actual_wants, "Status": "On Track" if actual_wants <= wants_target else "Over Budget"},
        {"Category": "Savings & Debt (20%)", "Target Allocation": f"{savings_pct}%", f"Target ({curr_code})": savings_target, f"Actual Spent ({curr_code})": actual_savings, f"Remaining ({curr_code})": actual_savings - savings_target, "Status": "Goal Met" if actual_savings >= savings_target else "Under Goal"}
    ]
    df_cat_summary = pd.DataFrame(cat_data)

    st.dataframe(
        df_cat_summary.style.format({
            f"Target ({curr_code})": f"{curr_symbol}{{:,.2f}}",
            f"Actual Spent ({curr_code})": f"{curr_symbol}{{:,.2f}}",
            f"Remaining ({curr_code})": f"{curr_symbol}{{:,.2f}}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Budget Target vs. Actual Spent")
        chart_df = pd.DataFrame({
            "Category": ["Priority (100%)", "Needs (50%)", "Wants (30%)", "Savings (20%)"],
            "Target": [disp_fixed, needs_target, wants_target, savings_target],
            "Actual": [actual_priority, actual_needs, actual_wants, actual_savings]
        })
        fig_bar = go.Figure(data=[
            go.Bar(name='Target', x=chart_df['Category'], y=chart_df['Target'], marker_color='#93C5FD'),
            go.Bar(name='Actual', x=chart_df['Category'], y=chart_df['Actual'], marker_color='#1D4ED8')
        ])
        fig_bar.update_layout(
            barmode='group',
            yaxis_title=f"Amount ({curr_code})",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("Actual Expense Distribution")
        if total_spent > 0:
            fig_pie = px.pie(
                values=[actual_priority, actual_needs, actual_wants, actual_savings],
                names=["100% Priority", "Needs", "Wants", "Savings"],
                color_discrete_sequence=['#EF4444', '#2563EB', '#F59E0B', '#10B981'],
                hole=0.45
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No payments or expenses logged yet. Add your first payment in the 'Add Expense' tab!")

# TAB 2: ADD EXPENSE
with tab_add:
    st.subheader("Record a New Expense or Person Payment")

    with st.form("add_expense_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)

        with col_a:
            exp_date = st.date_input("Date", value=datetime.today())
            main_cat = st.selectbox("Category Group", [
                "100% Priority & People to Pay",
                "Needs (50%)",
                "Wants (30%)",
                "Savings & Debt (20%)"
            ])

            if "100%" in main_cat:
                sub_cats = [
                    "Household Helper / Staff Salary (100%)",
                    "Family Support & Remittance (100%)",
                    "Direct Mandatory Debt / Personal Loan",
                    "Fixed Emergency Bill (100%)"
                ]
            elif "Needs" in main_cat:
                sub_cats = ["Housing / Rent", "Utilities & Bills", "Groceries", "Transportation / Fuel", "Healthcare / Insurance"]
            elif "Wants" in main_cat:
                sub_cats = ["Dining Out & Coffee", "Entertainment & Streaming", "Shopping & Apparel", "Hobbies & Travel", "Subscriptions", "Miscellaneous"]
            else:
                sub_cats = ["Emergency Fund", "Investment Account", "Extra Debt Payoff", "Savings Goal"]

            sub_cat = st.selectbox("Sub-Category", sub_cats)

        with col_b:
            merchant = st.text_input("Recipient / Merchant / Description", placeholder="e.g., Helper Salary, Remittance, Grocery Store")
            
            c_input1, c_input2 = st.columns([2, 1])
            with c_input1:
                amount_input = st.number_input("Amount Paid", min_value=0.01, step=5.0, value=50.0)
            with c_input2:
                input_currency = st.selectbox("Currency", ["BHD", "PHP", "USD"], index=0)

            payment_method = st.selectbox("Payment Method", ["Bank Transfer", "Cash", "Credit Card", "Debit Card", "Remittance Service"])

        submit_btn = st.form_submit_button("Save Payment")

        if submit_btn:
            # Convert input amount to base BHD
            amount_bhd = amount_input / EXCHANGE_RATES[input_currency]["rate"]
            new_row = pd.DataFrame([{
                "Date": exp_date,
                "Main Category": main_cat,
                "Sub Category": sub_cat,
                "Merchant/Description": merchant if merchant else "Unspecified",
                "Amount": amount_input,
                "Currency": input_currency,
                "Amount (BHD)": amount_bhd,
                "Payment Method": payment_method
            }])
            df_expenses = pd.concat([df_expenses, new_row], ignore_index=True)
            save_data(df_expenses)
            st.success(f"Successfully recorded payment of {EXCHANGE_RATES[input_currency]['symbol']}{amount_input:,.2f} ({sub_cat})!")
            st.rerun()

# TAB 3: TRANSACTION HISTORY
with tab_history:
    st.subheader("📜 Recorded Expense & Payment History")

    if not df_expenses.empty:
        cat_filter = st.multiselect("Filter by Category", options=[
            "100% Priority & People to Pay",
            "Needs (50%)",
            "Wants (30%)",
            "Savings & Debt (20%)"
        ], default=[
            "100% Priority & People to Pay",
            "Needs (50%)",
            "Wants (30%)",
            "Savings & Debt (20%)"
        ])

        filtered_df = df_expenses[df_expenses["Main Category"].isin(cat_filter)] if cat_filter else df_expenses

        st.dataframe(
            filtered_df.sort_values(by="Date", ascending=False),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        if st.button("Clear All Expense Data", type="primary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.success("All expense logs cleared!")
            st.rerun()
    else:
        st.info("No transaction history found. Start recording payments in the 'Add Expense' tab!")

# TAB 4: CURRENCY CALCULATOR
with tab_calc:
    st.subheader("💱 Live Multi-Currency Converter (BHD ↔ PHP ↔ USD)")
    st.write("Current Base Conversion Rates:")
    st.caption("• **1 BHD (BD)** = 154.50 PHP (₱) = $2.65 USD")
    st.caption("• **1 USD ($)** = 58.30 PHP (₱) = 0.377 BHD (BD)")
    
    c_in1, c_in2 = st.columns(2)
    with c_in1:
        calc_amount = st.number_input("Amount to Convert", min_value=1.0, value=100.0, step=10.0)
        from_curr = st.selectbox("From Currency", ["BHD", "PHP", "USD"], index=0)
    with c_in2:
        to_curr = st.selectbox("To Currency", ["PHP", "USD", "BHD"], index=0)

    amount_in_bhd = calc_amount / EXCHANGE_RATES[from_curr]["rate"]
    converted_result = amount_in_bhd * EXCHANGE_RATES[to_curr]["rate"]
    st.success(f"### {EXCHANGE_RATES[from_curr]['symbol']}{calc_amount:,.2f} {from_curr} = **{EXCHANGE_RATES[to_curr]['symbol']}{converted_result:,.2f} {to_curr}**")

# TAB 5: DEPLOYMENT GUIDE
with tab_guide:
    st.subheader("📘 Deployment & Smartphone Access Instructions")
    st.markdown("""
    ### 📱 How to Access Rogee's Financial Command Center on Your Smartphone:
    
    #### Option A: Home Wi-Fi Access (Instant)
    1. Keep Command Prompt running on your PC: `streamlit run app.py`
    2. Note the Network URL shown in your terminal (e.g., `http://192.168.x.x:8501`).
    3. Open that URL in your phone's browser while connected to the same Wi-Fi network.
    4. Tap **Share > Add to Home Screen** on your phone for a 1-tap app icon!
    """)
