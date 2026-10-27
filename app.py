import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import json

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
    .income-card { background-color: #F0FDF4; border: 1px solid #BBF7D0; border-left: 5px solid #22C55E; padding: 14px 18px; border-radius: 8px; margin-bottom: 18px; }
</style>
""", unsafe_allow_html=True)

# User Profiles and Configuration
USER_PROFILES = {
    "Rogee": {
        "s_key": "ROGEE_KEY",
        "d_pass": "rogee1989",
        "data_file": "expenses_rogee.csv",
        "config_file": "config_rogee.json"
    },
    "Ferdie": {
        "s_key": "USER2_KEY",
        "d_pass": "Ce_0121119",
        "data_file": "expenses_user2.csv",
        "config_file": "config_user2.json"
    }
}

EXCHANGE_RATES = {
    "BHD": {"symbol": "BD ", "rate": 1.0, "name": "Bahraini Dinar"},
    "PHP": {"symbol": "₱", "rate": 154.50, "name": "Philippine Peso"},
    "USD": {"symbol": "$", "rate": 2.65, "name": "US Dollar"}
}

# Helper: Load User Config
def load_user_config(config_file):
    default_cfg = {
        "salary_bhd": 200.0,
        "business_bhd": 0.0,
        "sidelines_bhd": 0.0,
        "other_income_bhd": 0.0,
        "fixed_priority_bhd": 50.0,
        "needs_pct": 50,
        "wants_pct": 30,
        "savings_pct": 20
    }
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                saved = json.load(f)
                default_cfg.update(saved)
        except Exception:
            pass
    return default_cfg

# Helper: Save User Config
def save_user_config(config_file, config_dict):
    try:
        with open(config_file, "w") as f:
            json.dump(config_dict, f, indent=4)
    except Exception:
        pass

# Authentication Gate
def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = None

    if not st.session_state["authenticated"]:
        st.markdown("<h2 style='text-align: center;'>🔐 Rogee&apos;s Financial Command Center</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B7280;'>Please select your account profile and enter your access key.</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                selected_user = st.selectbox("Select Account Profile", list(USER_PROFILES.keys()))
                entered_pass = st.text_input("Enter Access Key", type="password", placeholder="••••••••")
                login_btn = st.form_submit_button("🔓 Unlock Dashboard", use_container_width=True)
                
                if login_btn:
                    user_info = USER_PROFILES[selected_user]
                    sec_obj = getattr(st, "secrets", {})
                    expected_pass = sec_obj.get(user_info["s_key"], user_info["d_pass"])
                    if entered_pass == expected_pass:
                        st.session_state["authenticated"] = True
                        st.session_state["current_user"] = selected_user
                        st.success(f"Welcome back, {selected_user}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid access key. Please try again.")
        return False
    return True

if not check_authentication():
    st.stop()

current_user = st.session_state["current_user"]
user_info = USER_PROFILES[current_user]
DATA_FILE = user_info["data_file"]
CONFIG_FILE = user_info["config_file"]

# Load persisted user configuration
user_cfg = load_user_config(CONFIG_FILE)

# Load Transaction Data
def load_data(file_path):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=["Date", "Main Category", "Sub Category", "Merchant/Description", "Amount", "Currency", "Amount (BHD)", "Payment Method"])

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

df_expenses = load_data(DATA_FILE)

# Sidebar Configuration
st.sidebar.title("⚙️ Command Center Settings")
st.sidebar.caption(f"Active Account: **{current_user}**")

display_curr = st.sidebar.selectbox("Display Currency", ["BHD (BD)", "PHP (₱)", "USD ($)"], index=0)
curr_code = display_curr.split()[0]
curr_symbol = EXCHANGE_RATES[curr_code]["symbol"]
rate_mult = EXCHANGE_RATES[curr_code]["rate"]

st.sidebar.markdown("---")
st.sidebar.subheader("💵 Income Streams (in BHD)")
st.sidebar.caption("Changes are saved automatically and remain fixed across logins.")

salary_bhd = st.sidebar.number_input("Primary Salary (BHD)", min_value=0.0, value=float(user_cfg.get("salary_bhd", 200.0)), step=10.0)
business_bhd = st.sidebar.number_input("Business Income (BHD)", min_value=0.0, value=float(user_cfg.get("business_bhd", 0.0)), step=10.0)
sidelines_bhd = st.sidebar.number_input("Sidelines / Freelance (BHD)", min_value=0.0, value=float(user_cfg.get("sidelines_bhd", 0.0)), step=10.0)
other_income_bhd = st.sidebar.number_input("Other Income (BHD)", min_value=0.0, value=float(user_cfg.get("other_income_bhd", 0.0)), step=10.0)

total_income_bhd = salary_bhd + business_bhd + sidelines_bhd + other_income_bhd
st.sidebar.info(f"**Total Combined Income:** BD {total_income_bhd:,.2f}")

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 100% Mandatory Payments Total")
fixed_priority_bhd = st.sidebar.number_input("Mandatory Obligations Total (BHD)", min_value=0.0, value=float(user_cfg.get("fixed_priority_bhd", 50.0)), step=10.0)

net_bhd_for_budget = max(0.0, total_income_bhd - fixed_priority_bhd)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 50/30/20 Budget Allocations (%)")
needs_pct = st.sidebar.slider("Needs Target % (Essentials)", 0, 100, int(user_cfg.get("needs_pct", 50)))
wants_pct = st.sidebar.slider("Wants Target % (Lifestyle)", 0, 100, int(user_cfg.get("wants_pct", 30)))
savings_pct = st.sidebar.slider("Savings Target % (Goals/Debt)", 0, 100, int(user_cfg.get("savings_pct", 20)))

total_pct = needs_pct + wants_pct + savings_pct
if total_pct != 100:
    st.sidebar.warning(f"Allocation total is {total_pct}%. It should sum to 100%.")

# Persist updated sidebar settings to JSON
updated_cfg = {
    "salary_bhd": salary_bhd,
    "business_bhd": business_bhd,
    "sidelines_bhd": sidelines_bhd,
    "other_income_bhd": other_income_bhd,
    "fixed_priority_bhd": fixed_priority_bhd,
    "needs_pct": needs_pct,
    "wants_pct": wants_pct,
    "savings_pct": savings_pct
}
save_user_config(CONFIG_FILE, updated_cfg)

st.sidebar.markdown("---")
if st.sidebar.button("🔒 Lock App / Log Out", use_container_width=True):
    st.session_state["authenticated"] = False
    st.session_state["current_user"] = None
    st.rerun()

# Calculations in Selected Display Currency
disp_income = total_income_bhd * rate_mult
disp_fixed = fixed_priority_bhd * rate_mult
disp_net_budget = net_bhd_for_budget * rate_mult

needs_target = disp_net_budget * (needs_pct / 100.0)
wants_target = disp_net_budget * (wants_pct / 100.0)
savings_target = disp_net_budget * (savings_pct / 100.0)

# Main Title Header
st.markdown('<div class="main-header">💰 Rogee&apos;s Financial Command Center</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multi-Currency Personal Finance Manager with Persistent User Settings & 50/30/20 Framework</div>', unsafe_allow_html=True)

# Income Summary Banner
st.markdown('<div class="income-card">', unsafe_allow_html=True)
st.subheader("💵 Income Stream Breakdown & Multi-Currency Overview")
inc_c1, inc_c2, inc_c3 = st.columns([2, 1, 1])

with inc_c1:
    st.write(f"* **Primary Salary:** BD {salary_bhd:,.2f}")
    st.write(f"* **Business Earnings:** BD {business_bhd:,.2f}")
    st.write(f"* **Sidelines / Freelance:** BD {sidelines_bhd:,.2f}")
    st.write(f"* **Other Income:** BD {other_income_bhd:,.2f}")

with inc_c2:
    st.metric("Total Income (BHD)", f"BD {total_income_bhd:,.2f}")
    st.metric("Total Income (PHP)", f"₱{total_income_bhd * 154.50:,.2f}")

with inc_c3:
    st.metric("Total Income (USD)", f"${total_income_bhd * 2.65:,.2f}")
    st.metric("50/30/20 Net Pool", f"BD {net_bhd_for_budget:,.2f}")

st.markdown('</div>', unsafe_allow_html=True)

# Tabs Navigation
tab_dash, tab_add, tab_history, tab_reports, tab_calc, tab_guide = st.tabs([
    "📈 Dashboard & Analytics",
    "➕ Record Expense / Payment",
    "📜 Transaction History",
    "📥 Reports & Export",
    "💱 Currency Converter",
    "📘 Security & Guide"
])

# Actual Spending Calculations
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
remaining_cash_bhd = total_income_bhd - total_spent_bhd

actual_priority_disp = actual_priority_bhd * rate_mult
actual_needs_disp = actual_needs_bhd * rate_mult
actual_wants_disp = actual_wants_bhd * rate_mult
actual_savings_disp = actual_savings_bhd * rate_mult

total_spent_disp = total_spent_bhd * rate_mult
remaining_cash_disp = remaining_cash_bhd * rate_mult

# TAB 1: DASHBOARD
with tab_dash:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Gross Monthly Income", f"{curr_symbol}{disp_income:,.2f}")
    m2.metric("100% Priority Obligations", f"{curr_symbol}{disp_fixed:,.2f}")
    m3.metric("Total Spent To Date", f"{curr_symbol}{total_spent_disp:,.2f}", delta=f"-{curr_symbol}{total_spent_disp:,.2f}", delta_color="inverse")
    m4.metric("Remaining Cash Balance", f"{curr_symbol}{remaining_cash_disp:,.2f}", delta=f"{curr_symbol}{remaining_cash_disp:,.2f}")

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
        st.metric("Pending Mandatory Balance", f"{curr_symbol}{rem_priority_disp:,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("📊 50/30/20 Net Budget Allocation Breakdown")
    st.caption(f"Allocations calculated from remaining net budget: **{curr_symbol}{disp_net_budget:,.2f}** (Income minus 100% Priority Obligations).")

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

    ch1, ch2 = st.columns(2)

    with ch1:
        st.subheader("Target vs. Actual Spending")
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

    with ch2:
        st.subheader("Overall Expense Distribution")
        if total_spent_disp > 0:
            fig_pie = px.pie(
                values=[actual_priority_disp, actual_needs_disp, actual_wants_disp, actual_savings_disp],
                names=["100% Mandatory", "Needs (50%)", "Wants (30%)", "Savings (20%)"],
                color_discrete_sequence=['#EF4444', '#2563EB', '#F59E0B', '#10B981'],
                hole=0.45
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expenses logged yet. Add your first payment in the 'Record Expense' tab!")

    st.markdown("---")
    ch3, ch4 = st.columns(2)

    with ch3:
        st.subheader("Top Sub-Category Spending")
        if not df_expenses.empty:
            df_sub = df_expenses.groupby("Sub Category")["Amount (BHD)"].sum().reset_index()
            df_sub["Amount_Disp"] = df_sub["Amount (BHD)"] * rate_mult
            df_sub = df_sub.sort_values(by="Amount_Disp", ascending=True)
            fig_sub = px.bar(
                df_sub,
                x="Amount_Disp",
                y="Sub Category",
                orientation="h",
                color="Amount_Disp",
                color_continuous_scale="Blues",
                labels={"Amount_Disp": f"Amount ({curr_code})"}
            )
            fig_sub.update_layout(margin=dict(l=20, r=20, t=30, b=20), showlegend=False)
            st.plotly_chart(fig_sub, use_container_width=True)
        else:
            st.info("Log expenses to view sub-category rankings.")

    with ch4:
        st.subheader("Cumulative Spending Timeline")
        if not df_expenses.empty:
            df_time = df_expenses.copy()
            df_time["Amount_Disp"] = df_time["Amount (BHD)"] * rate_mult
            df_time = df_time.sort_values(by="Date")
            df_time["Cumulative"] = df_time["Amount_Disp"].cumsum()
            fig_line = px.line(
                df_time,
                x="Date",
                y="Cumulative",
                markers=True,
                labels={"Cumulative": f"Total Cumulative ({curr_code})"}
            )
            fig_line.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Log expenses to view spending over time.")

# TAB 2: RECORD EXPENSE / PAYMENT
with tab_add:
    st.subheader("Record a New Expense or Payment")

    with st.form("add_expense_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)

        with col_a:
            exp_date = st.date_input("Date", value=datetime.today())
            main_cat = st.selectbox("Budget Allocation Category", [
                "100% Priority & People to Pay",
                "Needs (50%)",
                "Wants (30%)",
                "Savings & Debt (20%)"
            ])
            
            if "100% Priority" in main_cat:
                sub_cats = ["People to Pay (Household Helper / Staff)", "Family Support & Remittance (100%)", "Direct Mandatory Loan Payment", "Fixed Emergency Obligation"]
            elif "Needs" in main_cat:
                sub_cats = ["Housing / Rent / Mortgage", "Utilities & Bills", "Groceries", "Transportation / Fuel", "Healthcare / Insurance", "Minimum Debt Payments"]
            elif "Wants" in main_cat:
                sub_cats = ["Dining Out & Coffee", "Entertainment & Streaming", "Shopping & Apparel", "Hobbies & Travel", "Subscriptions", "Miscellaneous"]
            else:
                sub_cats = ["Emergency Fund", "Retirement / Savings Account", "Stock Investments", "Extra Debt Payoff", "Major Goal Savings"]

            sub_cat = st.selectbox("Sub-Category", sub_cats)

        with col_b:
            merchant = st.text_input("Merchant / Recipient Description", placeholder="e.g., Staff Name, Grocery Store, Landlord")
            amount_input = st.number_input("Amount", min_value=0.01, step=5.0, value=25.0)
            input_currency = st.selectbox("Currency Paid In", ["BHD", "PHP", "USD"], index=0)
            payment_method = st.selectbox("Payment Method", ["Bank Transfer", "Cash", "Credit Card", "Debit Card"])

        submit_btn = st.form_submit_button("💾 Save Payment Record", use_container_width=True)

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
            save_data(df_expenses, DATA_FILE)
            st.success(f"Successfully recorded payment of {EXCHANGE_RATES[input_currency]['symbol']}{amount_input:,.2f} ({sub_cat})!")
            st.rerun()

# TAB 3: TRANSACTION HISTORY
with tab_history:
    st.subheader(f"📜 Recorded Transaction History ({current_user})")

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
        if st.button("🗑️ Clear All Expense Data", type="primary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.success("All transaction logs cleared!")
            st.rerun()
    else:
        st.info("No transaction history found. Start recording payments in the 'Record Expense' tab!")

# TAB 4: REPORTS & EXPORT
with tab_reports:
    st.subheader("📥 Download Financial Reports & Data")

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.markdown("### 📊 Export Transaction Ledger")
        if not df_expenses.empty:
            csv_data = df_expenses.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Full CSV Ledger",
                data=csv_data,
                file_name=f"financial_ledger_{current_user.lower().replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No transaction records available to export.")

    with col_r2:
        st.markdown("### 📄 Export Executive Summary Report")
        report_date = datetime.today().strftime("%Y-%m-%d")
        report_text = f"""ROGEE FINANCIAL COMMAND CENTER SUMMARY REPORT
Account User: {current_user}
Generated Date: {report_date}

1. INCOME STREAMS (BHD):
- Primary Salary: BD {salary_bhd:,.2f}
- Business Income: BD {business_bhd:,.2f}
- Sidelines / Freelance: BD {sidelines_bhd:,.2f}
- Other Income: BD {other_income_bhd:,.2f}
TOTAL COMBINED MONTHLY INCOME: BD {total_income_bhd:,.2f}

2. MANDATORY OBLIGATIONS & NET POOL:
- Mandatory 100% Obligations Target: BD {fixed_priority_bhd:,.2f}
- Net Disposable Budget Pool: BD {net_bhd_for_budget:,.2f}

3. CASH BALANCE OVERVIEW:
- Total Spent To Date: BD {total_spent_bhd:,.2f}
- Remaining Net Cash Balance: BD {remaining_cash_bhd:,.2f}
"""
        st.download_button(
            label="📥 Download Executive Summary (.TXT)",
            data=report_text,
            file_name=f"summary_report_{current_user.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# TAB 5: CURRENCY CONVERTER
with tab_calc:
    st.subheader("💱 Live Multi-Currency Converter (BHD ↔ PHP ↔ USD)")
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

# TAB 6: SECURITY & GUIDE
with tab_guide:
    st.subheader("📘 Security & Configuration Guide")
    st.markdown("""
    ### 🔐 Managing Accounts & Custom Passwords
    * **Persistent Settings**: Any changes you make to your salary, business earnings, or mandatory payments are saved to your account profile (`config_rogee.json` / `config_user2.json`).
    * **Separate Data Files**: Each profile maintains its own completely isolated transactions ledger.
    * **Streamlit Secrets Setup**: You can configure custom passwords in Streamlit Cloud under **Manage App > Settings > Secrets**:
      ```toml
      ROGEE_KEY = "YourCustomPassword1"
      USER2_KEY = "YourCustomPassword2"
      ```
    """)
