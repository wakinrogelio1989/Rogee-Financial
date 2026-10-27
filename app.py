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

# Custom CSS styling
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 800; color: #1E3A8A; margin-bottom: 0.1rem; }
    .sub-header { font-size: 1.05rem; color: #4B5563; margin-bottom: 1.2rem; }
    .priority-banner { background-color: #FEF2F2; border: 1px solid #FECACA; border-left: 5px solid #EF4444; padding: 14px 18px; border-radius: 8px; margin-bottom: 18px; }
    .login-container { max-width: 450px; margin: 0 auto; padding: 30px; border-radius: 10px; background-color: #F8FAFC; border: 1px solid #E2E8F0; }
</style>
""", unsafe_allow_html=True)

# User Profiles Configuration (Passwords can also be set via Streamlit Secrets)
USER_PROFILES = {
    "Rogee": {
        "password": st.secrets.get("ROGEE_PASSWORD", "rogee1989"),
        "data_file": "expenses_rogee.csv"
    },
    "Ferdie": {
        "password": st.secrets.get("USER2_PASSWORD", "Ce_0121119"),
        "data_file": "expenses_user2.csv"
    }
}

# Currency Exchange Rates (Base: BHD)
EXCHANGE_RATES = {
    "BHD": {"symbol": "BD ", "rate": 1.0, "name": "Bahraini Dinar"},
    "PHP": {"symbol": "₱", "rate": 154.50, "name": "Philippine Peso"},
    "USD": {"symbol": "$", "rate": 2.65, "name": "US Dollar"}
}

# Multi-User Authentication Gate
def check_password():
    if "authenticated_user" in st.session_state:
        return True

    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🔐 Rogee&apos;s Financial Command Center</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6B7280;'>Private Multi-User Personal Finance Portal</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            selected_user = st.selectbox("Select Account Profile", list(USER_PROFILES.keys()))
            entered_password = st.text_input("Enter Passkey", type="password", placeholder="Enter password...")
            submit_login = st.form_submit_button("🔑 Login to Command Center", use_container_width=True)

            if submit_login:
                target_pass = USER_PROFILES[selected_user]["password"]
                if entered_password == target_pass:
                    st.session_state["authenticated_user"] = selected_user
                    st.success(f"Welcome back, {selected_user}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid password. Access denied.")
    return False

if not check_password():
    st.stop()

current_user = st.session_state["authenticated_user"]
DATA_FILE = USER_PROFILES[current_user]["data_file"]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            df["Date"] = pd.to_datetime(df["Date"]).dt.date
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=["Date", "Main Category", "Sub Category", "Merchant/Description", "Amount", "Currency", "Amount (BHD)", "Payment Method"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df_expenses = load_data()

# Sidebar Controls
st.sidebar.title("⚙️ Command Center Settings")
st.sidebar.markdown(f"**Current User:** `{current_user}`")

if st.sidebar.button("🔒 Log Out / Lock App"):
    del st.session_state["authenticated_user"]
    st.rerun()

st.sidebar.markdown("---")
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

disp_salary = bhd_salary * rate_mult
disp_fixed = fixed_priority_bhd * rate_mult
disp_net_budget = net_bhd_for_budget * rate_mult

needs_target = disp_net_budget * (needs_pct / 100.0)
wants_target = disp_net_budget * (wants_pct / 100.0)
savings_target = disp_net_budget * (savings_pct / 100.0)

# Main Header
st.markdown(f'<div class="main-header">💰 Rogee&apos;s Financial Command Center</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Personal Finance Tracker & Budget Portal | Account: <b>{current_user}</b></div>', unsafe_allow_html=True)

st.info(f"""
### 📊 Monthly Income Summary ({current_user})
* **Bahraini Dinar (Base Salary):** BD {bhd_salary:,.2f}
* **Philippine Peso Equivalent:** ₱{bhd_salary * 154.50:,.2f}
* **US Dollar Equivalent:** ${bhd_salary * 2.65:,.2f}
""")

# Main Tabs
tab_dash, tab_add, tab_history, tab_reports, tab_calc, tab_guide = st.tabs([
    "📈 Dashboard & Visuals",
    "➕ Record Expense / Payment",
    "📜 Transaction History",
    "📥 Download Reports",
    "💱 Currency Converter",
    "📘 Security & User Guide"
])

# Actual Expenses Calculations
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

actual_priority_disp = actual_priority_bhd * rate_mult
actual_needs_disp = actual_needs_bhd * rate_mult
actual_wants_disp = actual_wants_bhd * rate_mult
actual_savings_disp = actual_savings_bhd * rate_mult

total_spent_disp = total_spent_bhd * rate_mult
remaining_cash_disp = remaining_cash_bhd * rate_mult

# TAB 1: DASHBOARD
with tab_dash:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Gross Monthly Income", f"{curr_symbol}{disp_salary:,.2f}")
    m2.metric("100% Priority Obligations", f"{curr_symbol}{disp_fixed:,.2f}")
    m3.metric("Total Spent To Date", f"{curr_symbol}{total_spent_disp:,.2f}", delta=f"-{curr_symbol}{total_spent_disp:,.2f}", delta_color="inverse")
    m4.metric("Remaining Net Cash", f"{curr_symbol}{remaining_cash_disp:,.2f}", delta=f"{curr_symbol}{remaining_cash_disp:,.2f}")

    st.markdown("---")

    # Priority Obligations Progress Banner
    st.markdown('<div class="priority-banner">', unsafe_allow_html=True)
    st.subheader("🚨 100% Mandatory Obligations Progress")
    p_col1, p_col2 = st.columns([2, 1])
    with p_col1:
        priority_pct = min(100.0, (actual_priority_bhd / fixed_priority_bhd * 100.0)) if fixed_priority_bhd > 0 else 0.0
        st.progress(priority_pct / 100.0)
        st.write(f"Paid **{curr_symbol}{actual_priority_disp:,.2f}** of **{curr_symbol}{disp_fixed:,.2f}** mandatory obligations ({priority_pct:.1f}% paid).")
    with p_col2:
        rem_priority_disp = max(0.0, disp_fixed - actual_priority_disp)
        st.metric("Pending Priority Payments", f"{curr_symbol}{rem_priority_disp:,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("📊 50/30/20 Net Budget Allocation Breakdown")
    st.caption(f"Allocations calculated from remaining net budget: **{curr_symbol}{disp_net_budget:,.2f}** (Income minus 100% Priority Payments).")

    cat_data = [
        {"Category": "Needs (50%)", "Target Allocation": f"{needs_pct}%", f"Target ({curr_code})": needs_target, f"Actual Spent ({curr_code})": actual_needs_disp, f"Difference ({curr_code})": needs_target - actual_needs_disp, "Status": "On Track" if actual_needs_disp <= needs_target else "Over Target"},
        {"Category": "Wants (30%)", "Target Allocation": f"{wants_pct}%", f"Target ({curr_code})": wants_target, f"Actual Spent ({curr_code})": actual_wants_disp, f"Difference ({curr_code})": wants_target - actual_wants_disp, "Status": "On Track" if actual_wants_disp <= wants_target else "Over Target"},
        {"Category": "Savings & Debt (20%)", "Target Allocation": f"{savings_pct}%", f"Target ({curr_code})": savings_target, f"Actual Spent ({curr_code})": actual_savings_disp, f"Difference ({curr_code})": actual_savings_disp - savings_target, "Status": "Target Met" if actual_savings_disp >= savings_target else "Under Goal"}
    ]
    df_cat_summary = pd.DataFrame(cat_data)

    st.dataframe(
        df_cat_summary.style.format({
            f"Target ({curr_code})": f"{curr_symbol}{{:,.2f}}",
            f"Actual Spent ({curr_code})": f"{curr_symbol}{{:,.2f}}",
            f"Difference ({curr_code})": f"{curr_symbol}{{:,.2f}}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # Interactive Dashboard Charts
    st.subheader("📈 Interactive Analytics & Expense Visualizations")
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Target vs. Actual Spending (50/30/20)")
        chart_df = pd.DataFrame({
            "Category": ["Needs", "Wants", "Savings"],
            "Target": [needs_target, wants_target, savings_target],
            "Actual": [actual_needs_disp, actual_wants_disp, actual_savings_disp]
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
        st.subheader("Overall Spending Share Distribution")
        if total_spent_disp > 0:
            fig_pie = px.pie(
                values=[actual_priority_disp, actual_needs_disp, actual_wants_disp, actual_savings_disp],
                names=["100% Priority", "Needs (50%)", "Wants (30%)", "Savings (20%)"],
                color_discrete_sequence=['#EF4444', '#2563EB', '#F59E0B', '#10B981'],
                hole=0.45
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expenses logged yet. Add your first expense in the 'Record Expense' tab!")

    if not df_expenses.empty:
        st.markdown("---")
        c3, c4 = st.columns(2)
        with c3:
            st.subheader("Top Expense Sub-Categories")
            sub_summary = df_expenses.groupby("Sub Category")["Amount (BHD)"].sum().reset_index()
            sub_summary["Amount_Disp"] = sub_summary["Amount (BHD)"] * rate_mult
            sub_summary = sub_summary.sort_values(by="Amount_Disp", ascending=True)
            fig_sub = px.bar(
                sub_summary,
                x="Amount_Disp",
                y="Sub Category",
                orientation='h',
                labels={"Amount_Disp": f"Amount ({curr_code})", "Sub Category": "Category"},
                color_discrete_sequence=['#3B82F6']
            )
            fig_sub.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_sub, use_container_width=True)

        with c4:
            st.subheader("Cumulative Spending Timeline")
            df_sorted = df_expenses.sort_values(by="Date").copy()
            df_sorted["Cum_BHD"] = df_sorted["Amount (BHD)"].cumsum()
            df_sorted["Cum_Disp"] = df_sorted["Cum_BHD"] * rate_mult
            fig_line = px.line(
                df_sorted,
                x="Date",
                y="Cum_Disp",
                markers=True,
                labels={"Cum_Disp": f"Total Spent ({curr_code})", "Date": "Date"},
                color_discrete_sequence=['#059669']
            )
            fig_line.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_line, use_container_width=True)

# TAB 2: RECORD EXPENSE
with tab_add:
    st.subheader("Record a New Expense or Payment")

    with st.form("add_expense_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)

        with col_a:
            exp_date = st.date_input("Date", value=datetime.today())
            main_cat = st.selectbox("Payment Category", [
                "100% Priority & People to Pay",
                "Needs (50%)",
                "Wants (30%)",
                "Savings & Debt (20%)"
            ])

            if "100%" in main_cat:
                sub_cats = [
                    "People to Pay (Household Helper / Staff Salary)",
                    "Family Support & Remittance (100%)",
                    "Direct Mandatory Debt / Personal Loan",
                    "Fixed Emergency Bill (100%)"
                ]
            elif "Needs" in main_cat:
                sub_cats = [
                    "Housing / Rent / Mortgage",
                    "Utilities & Electricity",
                    "Groceries & Food",
                    "Transportation & Fuel",
                    "Healthcare & Insurance",
                    "Minimum Debt Payments"
                ]
            elif "Wants" in main_cat:
                sub_cats = [
                    "Dining Out & Coffee",
                    "Entertainment & Streaming",
                    "Shopping & Apparel",
                    "Hobbies & Travel",
                    "Subscriptions",
                    "Miscellaneous"
                ]
            else:
                sub_cats = [
                    "Emergency Fund Savings",
                    "Retirement / Investments",
                    "Extra Debt Payoff",
                    "Major Goal Savings"
                ]

            sub_cat = st.selectbox("Sub-Category", sub_cats)

        with col_b:
            merchant = st.text_input("Merchant / Recipient Name", placeholder="e.g., Staff Name, Utility Company, Grocery")
            
            c_amt1, c_amt2 = st.columns([2, 1])
            with c_amt1:
                amount_input = st.number_input("Amount", min_value=0.01, step=5.0, value=50.0)
            with c_amt2:
                input_currency = st.selectbox("Currency", ["BHD", "PHP", "USD"], index=0)

            payment_method = st.selectbox("Payment Method", ["Cash", "Debit Card", "Credit Card", "Bank Transfer"])

        submit_btn = st.form_submit_button("💾 Save Payment Entry", use_container_width=True)

        if submit_btn:
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
        st.info("No transaction history found. Start recording payments in the 'Record Expense' tab!")

# TAB 4: DOWNLOAD REPORTS
with tab_reports:
    st.subheader("📥 Export & Download Financial Reports")
    st.write(f"Download your complete, structured transaction records and summary reports for **{current_user}**.")

    r_col1, r_col2 = st.columns(2)

    with r_col1:
        st.markdown("#### 📄 Detailed Expense Ledger (CSV)")
        st.caption("Includes dates, categories, merchants, original currencies, and normalized BHD amounts for Microsoft Excel.")
        if not df_expenses.empty:
            csv_data = df_expenses.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 Download {current_user}_Expenses.csv",
                data=csv_data,
                file_name=f"{current_user}_Expenses_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.warning("No expense data available to download yet.")

    with r_col2:
        st.markdown("#### 📊 Executive Financial Summary Report (.TXT)")
        st.caption("A human-readable text report summarizing income, priority payments, allocations, and remaining net balance.")
        
        report_text = f"""==================================================
ROGEE'S FINANCIAL COMMAND CENTER - EXECUTIVE REPORT
User Profile: {current_user}
Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
==================================================

1. INCOME & CURRENCY EQUIVALENTS
   - Monthly Base Salary (BHD): BD {bhd_salary:,.2f}
   - Philippine Peso Equivalent: ₱{bhd_salary * 154.50:,.2f}
   - US Dollar Equivalent: ${bhd_salary * 2.65:,.2f}

2. 100% MANDATORY OBLIGATIONS & PEOPLE TO PAY
   - Target 100% Mandatory Total: BD {fixed_priority_bhd:,.2f}
   - Actual Paid To Date: BD {actual_priority_bhd:,.2f}
   - Pending Mandatory Obligations: BD {max(0.0, fixed_priority_bhd - actual_priority_bhd):,.2f}

3. NET DISPOSABLE BUDGET ALLOCATION (50/30/20)
   - Net Budget Base: BD {net_bhd_for_budget:,.2f}
   - Needs Target ({needs_pct}%): BD {net_bhd_for_budget * (needs_pct/100):,.2f} | Actual Spent: BD {actual_needs_bhd:,.2f}
   - Wants Target ({wants_pct}%): BD {net_bhd_for_budget * (wants_pct/100):,.2f} | Actual Spent: BD {actual_wants_bhd:,.2f}
   - Savings Target ({savings_pct}%): BD {net_bhd_for_budget * (savings_pct/100):,.2f} | Actual Spent: BD {actual_savings_bhd:,.2f}

4. SUMMARY TOTALS
   - Gross Total Spent (All Categories): BD {total_spent_bhd:,.2f}
   - Net Remaining Cash Balance: BD {remaining_cash_bhd:,.2f}
==================================================
"""
        st.download_button(
            label=f"📥 Download {current_user}_Executive_Report.txt",
            data=report_text,
            file_name=f"{current_user}_Financial_Report_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# TAB 5: CURRENCY CONVERTER
with tab_calc:
    st.subheader("💱 Live Multi-Currency Converter (BHD ↔ PHP ↔ USD)")
    st.caption("Instant exchange rate calculator for cross-currency budgeting.")

    c_in1, c_in2 = st.columns(2)
    with c_in1:
        calc_amount = st.number_input("Amount to Convert", min_value=1.0, value=100.0, step=10.0)
        from_curr = st.selectbox("From Currency", ["BHD", "PHP", "USD"], index=0)
    with c_in2:
        to_curr = st.selectbox("To Currency", ["PHP", "USD", "BHD"], index=0)

    amount_in_bhd = calc_amount / EXCHANGE_RATES[from_curr]["rate"]
    converted_result = amount_in_bhd * EXCHANGE_RATES[to_curr]["rate"]
    st.success(f"### {EXCHANGE_RATES[from_curr]['symbol']}{calc_amount:,.2f} {from_curr} = **{EXCHANGE_RATES[to_curr]['symbol']}{converted_result:,.2f} {to_curr}**")

# TAB 6: SECURITY & GUIDE
with tab_guide:
    st.subheader("📘 Security & App Configuration Guide")
    st.markdown("""
    ### 🔐 Password Protection & Account Customization
    
    * **Setting Private Passwords**:
      * To change user passwords securely on Streamlit Cloud, go to **App Settings > Secrets** and enter your passwords under `ROGEE_PASSWORD` and `USER2_PASSWORD`.
      * Alternatively, open `app.py` in Notepad and edit the `USER_PROFILES` dictionary near line 28.
    
    * **Renaming User Accounts**:
      * In `app.py`, change `"User 2"` in `USER_PROFILES` to any custom name (e.g., `"Maria"`, `"Alex"`, or `"Partner"`).
      * Each account maintains its own isolated data ledger file so financial data remains completely private between users!

    ---
    ### 📱 Mobile Access Setup
    1. Open your personal app URL on Safari (iPhone) or Chrome (Android).
    2. Tap **Share > Add to Home Screen** to create a 1-tap launcher icon on your smartphone.
    """)
