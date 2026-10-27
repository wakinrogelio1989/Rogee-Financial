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
    .user-badge { background-color: #DBEAFE; color: #1E40AF; padding: 6px 12px; border-radius: 20px; font-weight: 600; display: inline-block; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# ⚙️ EASY NOTEPAD CONFIGURATION SECTION
# You can change user names, passwords, and default data files right here!
# ==============================================================================

USER_PROFILES = {
    "Rogee": {
        "password": st.secrets.get("ROGEE_PASSWORD", "rogee2026"),  # Rogee's Password
        "data_file": "expenses_rogee.csv"
    },
    "User 2": {  # <--- RENAME "User 2" TO ANYTHING YOU WANT IN NOTEPAD (e.g., "Maria", "Wife", "Partner")
        "password": st.secrets.get("USER2_PASSWORD", "user2026"),  # <--- CHANGE USER 2'S PASSWORD HERE
        "data_file": "expenses_user2.csv"
    }
}

# ==============================================================================
# 🔐 SECURE LOGIN SYSTEM
# ==============================================================================

def check_login():
    if "logged_in_user" not in st.session_state:
        st.session_state["logged_in_user"] = None

    if st.session_state["logged_in_user"] is None:
        st.markdown("<h2 style='text-align: center;'>🔐 Rogee&apos;s Financial Command Center</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B7280;'>Select your account and enter your private password to access your budget center.</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            selected_user = st.selectbox("👤 Select User Account:", list(USER_PROFILES.keys()))
            entered_pwd = st.text_input("🔑 Enter Access Password:", type="password", key="login_pwd_input", placeholder="Type password and press Enter...")
            
            if st.button("🚀 Log In", use_container_width=True, type="primary"):
                correct_pwd = USER_PROFILES[selected_user]["password"]
                if entered_pwd == correct_pwd:
                    st.session_state["logged_in_user"] = selected_user
                    st.rerun()
                else:
                    st.error("❌ Incorrect password. Please try again.")

            st.markdown("---")
            st.info("""
            💡 **Default Passwords**:
            * **Rogee**: `rogee2026`
            * **User 2**: `user2026`
            *(You can change these passwords and names inside `app.py` using Notepad or Streamlit Secrets!)*
            """)
        return False
    return True

if not check_login():
    st.stop()

current_user = st.session_state["logged_in_user"]
DATA_FILE = USER_PROFILES[current_user]["data_file"]

# Live Currency Exchange Rates (Base: BHD)
EXCHANGE_RATES = {
    "BHD": {"symbol": "BD ", "rate": 1.0, "name": "Bahraini Dinar"},
    "PHP": {"symbol": "₱", "rate": 154.50, "name": "Philippine Peso"},
    "USD": {"symbol": "$", "rate": 2.65, "name": "US Dollar"}
}

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

# ==============================================================================
# ⚙️ SIDEBAR SETTINGS & CONTROL PANEL
# ==============================================================================

st.sidebar.title(f"⚙️ {current_user}'s Settings")
st.sidebar.markdown(f'<div class="user-badge">👤 Logged in as: <b>{current_user}</b></div>', unsafe_allow_html=True)

if st.sidebar.button("🔒 Log Out", type="secondary", use_container_width=True):
    st.session_state["logged_in_user"] = None
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

st.markdown(f'<div class="main-header">💰 {current_user}&apos;s Financial Command Center</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multi-User Private Finance Manager with Password Gate & 50/30/20 Framework</div>', unsafe_allow_html=True)

st.info(f"""
### 📊 Monthly Income Summary for {current_user}
* **Bahraini Dinar (Base Salary):** BD {bhd_salary:,.2f}
* **Philippine Peso Equivalent:** ₱{bhd_salary * 154.50:,.2f}
* **US Dollar Equivalent:** ${bhd_salary * 2.65:,.2f}
""")

tab_dash, tab_add, tab_history, tab_calc, tab_reports, tab_guide = st.tabs([
    "📈 Dashboard & Analytics",
    "➕ Record Expense / Payment",
    "📜 Transaction History",
    "💱 Currency Converter",
    "📥 Financial Reports & Downloads",
    "📘 App Guide & Notepad Editing"
])

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

with tab_dash:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Gross Monthly Income", f"{curr_symbol}{disp_salary:,.2f}")
    m2.metric("100% Priority Obligations", f"{curr_symbol}{disp_fixed:,.2f}")
    m3.metric("Total Spent To Date", f"{curr_symbol}{total_spent_disp:,.2f}", delta=f"-{curr_symbol}{total_spent_disp:,.2f}", delta_color="inverse")
    m4.metric("Remaining Net Cash", f"{curr_symbol}{remaining_cash_disp:,.2f}", delta=f"{curr_symbol}{remaining_cash_disp:,.2f}")

    st.markdown("---")

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

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📊 Target vs. Actual Spending")
        chart_df = pd.DataFrame({
            "Category": ["Needs (50%)", "Wants (30%)", "Savings (20%)"],
            "Target": [needs_target, wants_target, savings_target],
            "Actual": [actual_needs_disp, actual_wants_disp, actual_savings_disp]
        })
        fig_bar = go.Figure(data=[
            go.Bar(name='Target', x=chart_df['Category'], y=chart_df['Target'], marker_color='#93C5FD'),
            go.Bar(name='Actual', x=chart_df['Category'], y=chart_df['Actual'], marker_color='#1D4ED8')
        ])
        fig_bar.update_layout(
            barmode='group',
            yaxis_title=f"Amount ({curr_symbol})",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("🍕 Overall Spending Share")
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

    st.markdown("---")
    st.subheader("📈 Top Expense Sub-Categories & Timeline")
    
    if not df_expenses.empty:
        c3, c4 = st.columns(2)
        with c3:
            sub_summary = df_expenses.groupby("Sub Category")["Amount (BHD)"].sum().reset_index()
            sub_summary["Amount (Display)"] = sub_summary["Amount (BHD)"] * rate_mult
            sub_summary = sub_summary.sort_values(by="Amount (Display)", ascending=True).tail(8)
            
            fig_sub = px.bar(
                sub_summary, x="Amount (Display)", y="Sub Category", orientation='h',
                title="Top Spending Sub-Categories",
                color_discrete_sequence=['#3B82F6']
            )
            fig_sub.update_layout(xaxis_title=f"Amount ({curr_symbol})", yaxis_title="")
            st.plotly_chart(fig_sub, use_container_width=True)

        with c4:
            timeline_df = df_expenses.copy()
            timeline_df["Amount (Display)"] = timeline_df["Amount (BHD)"] * rate_mult
            timeline_df = timeline_df.sort_values(by="Date")
            timeline_df["Cumulative Amount"] = timeline_df["Amount (Display)"].cumsum()
            
            fig_time = px.line(
                timeline_df, x="Date", y="Cumulative Amount",
                title="Cumulative Expense Growth",
                markers=True, line_shape='linear'
            )
            fig_time.update_layout(yaxis_title=f"Cumulative Spent ({curr_symbol})")
            st.plotly_chart(fig_time, use_container_width=True)

with tab_add:
    st.subheader("Record a New Expense or Payment")

    with st.form("add_expense_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)

        with col_a:
            exp_date = st.date_input("Date", value=datetime.today())
            main_cat = st.selectbox("Budget Category", [
                "100% Priority & People to Pay",
                "Needs (50%)",
                "Wants (30%)",
                "Savings & Debt (20%)"
            ])
            
            if "100%" in main_cat:
                sub_cats = ["People to Pay (Staff / Helper Salary)", "Family Support & Remittance (100%)", "Direct Personal Loan / Mandatory Debt", "Fixed Emergency Bill (100%)"]
            elif "Needs" in main_cat:
                sub_cats = ["Housing / Rent / Mortgage", "Utilities & Electricity", "Groceries & Food Supplies", "Transportation / Fuel", "Healthcare & Insurance", "Minimum Debt Payments"]
            elif "Wants" in main_cat:
                sub_cats = ["Dining Out & Coffee", "Entertainment & Streaming", "Shopping & Apparel", "Hobbies & Travel", "Subscriptions", "Miscellaneous"]
            else:
                sub_cats = ["Emergency Fund", "Retirement Savings", "Stock Investments", "Extra Debt Payoff", "Major Goal Savings"]

            sub_cat = st.selectbox("Sub-Category", sub_cats)

        with col_b:
            merchant = st.text_input("Recipient / Merchant / Description", placeholder="e.g., Helper Name, Grocery Store, Utility Company")
            input_currency = st.selectbox("Payment Currency", ["BHD", "PHP", "USD"], index=0)
            amount_input = st.number_input(f"Amount Paid", min_value=0.01, step=5.0, value=50.0)
            payment_method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Credit Card", "Debit Card", "GCash / Remittance"])

        submit_btn = st.form_submit_button("💾 Save Payment")

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
            st.success(f"Successfully recorded payment of {EXCHANGE_RATES[input_currency]['symbol']}{amount_input:,.2f} for {merchant if merchant else sub_cat}!")
            st.rerun()

with tab_history:
    st.subheader(f"📜 {current_user}'s Recorded Transaction History")

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
        if st.button("🗑️ Clear All My Expense Data", type="primary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.success("Your transaction history has been cleared!")
            st.rerun()
    else:
        st.info("No transaction history found. Start recording payments in the 'Record Expense' tab!")

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

with tab_reports:
    st.subheader("📥 Download Financial Reports & Data Ledgers")
    st.write(f"Export your complete financial records for **{current_user}**.")

    col_rep1, col_rep2 = st.columns(2)

    with col_rep1:
        st.markdown("#### 📄 Complete CSV Transaction Ledger")
        st.caption("Download all recorded expenses in CSV format. Compatible with Excel, Google Sheets, or Apple Numbers.")
        if not df_expenses.empty:
            csv_bytes = df_expenses.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 Download {current_user}_Expenses.csv",
                data=csv_bytes,
                file_name=f"{current_user.lower()}_expenses.csv",
                mime="text/csv",
                type="primary"
            )
        else:
            st.info("No expense data recorded yet to export.")

    with col_rep2:
        st.markdown("#### 📝 Executive Budget Summary (.TXT)")
        st.caption("Download a text summary of your monthly income, priority payment progress, and 50/30/20 balance.")
        
        summary_text = f"""==================================================
ROGEE FINANCIAL COMMAND CENTER - EXECUTIVE REPORT
User Profile: {current_user}
Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
==================================================

1. INCOME EQUIVALENTS:
--------------------------------------------------
Base Monthly Income (BHD): BD {bhd_salary:,.2f}
Philippine Peso Equivalent: ₱{bhd_salary * 154.50:,.2f}
US Dollar Equivalent:       ${bhd_salary * 2.65:,.2f}

2. MANDATORY 100% OBLIGATIONS:
--------------------------------------------------
Fixed Priority Target:      BD {fixed_priority_bhd:,.2f}
Actual Priority Paid:       BD {actual_priority_bhd:,.2f}
Pending Priority Balance:   BD {max(0.0, fixed_priority_bhd - actual_priority_bhd):,.2f}

3. 50/30/20 BUDGET BREAKDOWN (Remaining Net Budget: BD {net_bhd_for_budget:,.2f}):
--------------------------------------------------
Needs (50% Target: BD {needs_target:,.2f})    -> Actual Spent: BD {actual_needs_bhd:,.2f}
Wants (30% Target: BD {wants_target:,.2f})    -> Actual Spent: BD {actual_wants_bhd:,.2f}
Savings (20% Target: BD {savings_target:,.2f}) -> Actual Spent: BD {actual_savings_bhd:,.2f}

4. NET CASH SUMMARY:
--------------------------------------------------
Total Monthly Income:       BD {bhd_salary:,.2f}
Total Expenses Recorded:    BD {total_spent_bhd:,.2f}
Remaining Balance:          BD {remaining_cash_bhd:,.2f}
==================================================
"""
        st.download_button(
            label=f"📄 Download {current_user}_Executive_Summary.txt",
            data=summary_text,
            file_name=f"{current_user.lower()}_executive_summary.txt",
            mime="text/plain"
        )

with tab_guide:
    st.subheader("📘 How to Rename Users & Edit Passwords in Notepad")
    st.markdown("""
    ### ✏️ How to Rename "User 2" and Set Custom Passwords:

    1. Open **`app.py`** in **Notepad** (or any text editor) on your computer.
    2. Look at lines 28–42 near the top of the file for the **`USER_PROFILES`** block:

    ```python
    USER_PROFILES = {
        "Rogee": {
            "password": "rogee2026",   # <-- Change Rogee's Password here
            "data_file": "expenses_rogee.csv"
        },
        "Maria": {                     # <-- Rename "User 2" to "Maria" (or any name)
            "password": "maria2026",   # <-- Change Maria's Password here
            "data_file": "expenses_maria.csv"
        }
    }
    ```

    3. **To Rename User 2**: Replace `"User 2"` with whatever name you want (e.g. `"Maria"`, `"Wife"`, `"Brother"`).
    4. **To Set User 2's Password**: Replace `"user2026"` with their private password.
    5. Save the file (**Ctrl + S**), and upload `app.py` to your GitHub repository!
    """)
