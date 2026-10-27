import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

st.set_page_config(page_title="Rogee Financial Command Center", page_icon="💰", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>.main-header { font-size: 2.2rem; font-weight: 800; color: #1E3A8A; margin-bottom: 0.1rem; }.sub-header { font-size: 1.05rem; color: #4B5563; margin-bottom: 1.2rem; }.priority-banner { background-color: #FEF2F2; border: 1px solid #FECACA; border-left: 5px solid #EF4444; padding: 14px 18px; border-radius: 8px; margin-bottom: 18px; }.income-card { background-color: #F0FDF4; border: 1px solid #BBF7D0; border-left: 5px solid #22C55E; padding: 14px 18px; border-radius: 8px; margin-bottom: 18px; }</style>""", unsafe_allow_html=True)

USER_PROFILES = {"Rogee": {"s_key": "ROGEE_KEY", "d_pass": "rogee1989", "data_file": "expenses_rogee.csv"}, "Ferdie": {"s_key": "USER2_KEY", "d_pass": "ue_0121119", "data_file": "expenses_user2.csv"}}
EXCHANGE_RATES = {"BHD": {"symbol": "BD ", "rate": 1.0, "name": "Bahraini Dinar"}, "PHP": {"symbol": "₱", "rate": 154.50, "name": "Philippine Peso"}, "USD": {"symbol": "USD ", "rate": 2.65, "name": "US Dollar"}}

def check_authentication():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["current_user"] = None
    if not st.session_state["authenticated"]:
        st.markdown("<h2 style='text-align: center;'>🔐 Rogee Financial Command Center</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B7280;'>Please select your profile and enter your key to unlock your dashboard.</p>", unsafe_allow_html=True)
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
                        st.success("Welcome back!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid access key. Please try again.")
        return False
    return True

if not check_authentication(): st.stop()
current_user = st.session_state["current_user"]
user_config = USER_PROFILES[current_user]
DATA_FILE = user_config["data_file"]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            df["Date"] = pd.to_datetime(df["Date"]).dt.date
            return df
        except Exception: pass
    return pd.DataFrame(columns=["Date", "Main Category", "Sub Category", "Merchant/Description", "Amount", "Currency", "Amount (BHD)", "Payment Method"])

def save_data(df): df.to_csv(DATA_FILE, index=False)
df_expenses = load_data()

st.sidebar.title("👤 Settings (" + str(current_user) + ")")
if st.sidebar.button("🔒 Lock & Log Out", use_container_width=True):
    st.session_state["authenticated"] = False
    st.session_state["current_user"] = None
    st.rerun()

st.sidebar.markdown("---")
display_curr = st.sidebar.selectbox("Display Currency", ["BHD (BD)", "PHP (₱)", "USD"], index=0)
curr_code = display_curr.split()[0]
curr_symbol = EXCHANGE_RATES[curr_code]["symbol"]
rate_mult = EXCHANGE_RATES[curr_code]["rate"]

st.sidebar.markdown("---")
st.sidebar.subheader("💵 Monthly Income Streams (BHD)")
st.sidebar.caption("Enter monthly earnings across all active sources:")
salary_bhd = st.sidebar.number_input("1. Primary Salary (BHD)", min_value=0.0, value=1200.0, step=50.0)
business_bhd = st.sidebar.number_input("2. Business Income (BHD)", min_value=0.0, value=200.0, step=25.0)
sidelines_bhd = st.sidebar.number_input("3. Sidelines / Freelance (BHD)", min_value=0.0, value=100.0, step=25.0)
other_income_bhd = st.sidebar.number_input("4. Other Income (BHD)", min_value=0.0, value=0.0, step=25.0)

total_income_bhd = salary_bhd + business_bhd + sidelines_bhd + other_income_bhd
st.sidebar.markdown("### **Total Monthly Income: BD " + f"{total_income_bhd:,.2f}" + "**")

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 100% Mandatory Obligations")
st.sidebar.caption("Fixed obligations (staff salary, remittance, loans) deducted before 50/30/20 budget allocation.")
fixed_priority_bhd = st.sidebar.number_input("Mandatory 100% Payments Total (BHD)", min_value=0.0, value=300.0, step=25.0)
net_bhd_for_budget = max(0.0, total_income_bhd - fixed_priority_bhd)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 50/30/20 Allocations (%)")
needs_pct = st.sidebar.slider("Needs Target % (Essentials)", 0, 100, 50)
wants_pct = st.sidebar.slider("Wants Target % (Lifestyle)", 0, 100, 30)
savings_pct = st.sidebar.slider("Savings Target % (Goals/Debt)", 0, 100, 20)
total_pct = needs_pct + wants_pct + savings_pct
if total_pct != 100: st.sidebar.warning("Allocation total is " + str(total_pct) + "%. Please adjust sliders to sum to 100%.")

disp_total_income = total_income_bhd * rate_mult
disp_fixed = fixed_priority_bhd * rate_mult
disp_net_budget = net_bhd_for_budget * rate_mult
needs_target = disp_net_budget * (needs_pct / 100.0)
wants_target = disp_net_budget * (wants_pct / 100.0)
savings_target = disp_net_budget * (savings_pct / 100.0)

st.markdown("<div class='main-header'>💰 Rogee Financial Command Center</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Multi-Source Income & Finance Manager | Active Account: <b>" + str(current_user) + "</b></div>", unsafe_allow_html=True)

inc_card_html = "<div class='income-card'><h4 style='margin: 0; color: #166534;'>💵 Combined Monthly Income Breakdown (" + str(curr_code) + ")</h4><p style='margin-top: 5px; margin-bottom: 0px; color: #15803D;'>• <b>Primary Salary:</b> " + str(curr_symbol) + f"{(salary_bhd * rate_mult):,.2f}" + " &nbsp;|&nbsp; • <b>Business:</b> " + str(curr_symbol) + f"{(business_bhd * rate_mult):,.2f}" + " &nbsp;|&nbsp; • <b>Sidelines:</b> " + str(curr_symbol) + f"{(sidelines_bhd * rate_mult):,.2f}" + " &nbsp;|&nbsp; • <b>Other:</b> " + str(curr_symbol) + f"{(other_income_bhd * rate_mult):,.2f}" + "<br>🌟 <b>TOTAL COMBINED INCOME: " + str(curr_symbol) + f"{disp_total_income:,.2f}" + "</b> (Equivalent to: <b>₱" + f"{(total_income_bhd * 154.50):,.2f}" + " PHP</b> | <b>$" + f"{(total_income_bhd * 2.65):,.2f}" + " USD</b>)</p></div>"
st.markdown(inc_card_html, unsafe_allow_html=True)

tab_dash, tab_add, tab_history, tab_reports, tab_calc, tab_guide = st.tabs(["📈 Dashboard & Analytics", "➕ Record Expense / Payment", "📜 Transaction History", "📥 Reports & Export", "💱 Currency Converter", "📘 App Guide & Security"])

if not df_expenses.empty:
    actual_priority_bhd = df_expenses[df_expenses["Main Category"] == "100% Priority & People to Pay"]["Amount (BHD)"].sum()
    actual_needs_bhd = df_expenses[df_expenses["Main Category"] == "Needs (50%)"]["Amount (BHD)"].sum()
    actual_wants_bhd = df_expenses[df_expenses["Main Category"] == "Wants (30%)"]["Amount (BHD)"].sum()
    actual_savings_bhd = df_expenses[df_expenses["Main Category"] == "Savings & Debt (20%)"]["Amount (BHD)"].sum()
else: actual_priority_bhd = actual_needs_bhd = actual_wants_bhd = actual_savings_bhd = 0.0

total_spent_bhd = actual_priority_bhd + actual_needs_bhd + actual_wants_bhd + actual_savings_bhd
remaining_cash_bhd = total_income_bhd - total_spent_bhd
actual_priority_disp = actual_priority_bhd * rate_mult
actual_needs_disp = actual_needs_bhd * rate_mult
actual_wants_disp = actual_wants_bhd * rate_mult
actual_savings_disp = actual_savings_bhd * rate_mult
total_spent_disp = total_spent_bhd * rate_mult
remaining_cash_disp = remaining_cash_bhd * rate_mult

with tab_dash:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Monthly Income", f"{curr_symbol}{disp_total_income:,.2f}")
    m2.metric("100% Priority Obligations", f"{curr_symbol}{disp_fixed:,.2f}")
    m3.metric("Total Spent To Date", f"{curr_symbol}{total_spent_disp:,.2f}", delta=f"-{curr_symbol}{total_spent_disp:,.2f}", delta_color="inverse")
    m4.metric("Remaining Cash Balance", f"{curr_symbol}{remaining_cash_disp:,.2f}", delta=f"{curr_symbol}{remaining_cash_disp:,.2f}")
    st.markdown("---")
    st.markdown("<div class='priority-banner'>🚨 100% Mandatory Obligations Progress</div>", unsafe_allow_html=True)
    p_col1, p_col2 = st.columns([2, 1])
    with p_col1:
        priority_pct = min(100.0, (actual_priority_bhd / fixed_priority_bhd * 100.0)) if fixed_priority_bhd > 0 else 0.0
        st.progress(priority_pct / 100.0)
        st.write("Paid **" + f"{curr_symbol}{actual_priority_disp:,.2f}" + "** of **" + f"{curr_symbol}{disp_fixed:,.2f}" + f"** mandatory obligations ({priority_pct:.1f}% paid).")
    with p_col2:
        rem_priority_disp = max(0.0, disp_fixed - actual_priority_disp)
        st.metric("Pending Priority Payments", f"{curr_symbol}{rem_priority_disp:,.2f}")
    st.subheader("📊 50/30/20 Allocation Benchmark Breakdown")
    st.caption("Allocations calculated from remaining net budget: **" + f"{curr_symbol}{disp_net_budget:,.2f}" + "** (Total Income minus 100% Priority Obligations).")
    cat_data = [{"Category": "Needs (50%)", "Target Allocation": f"{needs_pct}%", f"Target ({curr_code})": needs_target, f"Actual Spent ({curr_code})": actual_needs_disp, f"Difference ({curr_code})": needs_target - actual_needs_disp, "Status": "On Track" if actual_needs_disp <= needs_target else "Over Budget"}, {"Category": "Wants (30%)", "Target Allocation": f"{wants_pct}%", f"Target ({curr_code})": wants_target, f"Actual Spent ({curr_code})": actual_wants_disp, f"Difference ({curr_code})": wants_target - actual_wants_disp, "Status": "On Track" if actual_wants_disp <= wants_target else "Over Budget"}, {"Category": "Savings & Debt (20%)", "Target Allocation": f"{savings_pct}%", f"Target ({curr_code})": savings_target, f"Actual Spent ({curr_code})": actual_savings_disp, f"Difference ({curr_code})": actual_savings_disp - savings_target, "Status": "Target Met" if actual_savings_disp >= savings_target else "Under Goal"}]
    df_cat_summary = pd.DataFrame(cat_data)
    st.dataframe(df_cat_summary.style.format({f"Target ({curr_code})": f"{curr_symbol}{{:,.2f}}", f"Actual Spent ({curr_code})": f"{curr_symbol}{{:,.2f}}", f"Difference ({curr_code})": f"{curr_symbol}{{:,.2f}}"}), use_container_width=True, hide_index=True)
    st.markdown("---")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("🎯 Target vs. Actual Spending")
        chart_df = pd.DataFrame({"Category": ["Needs (50%)", "Wants (30%)", "Savings (20%)"], "Target": [needs_target, wants_target, savings_target], "Actual": [actual_needs_disp, actual_wants_disp, actual_savings_disp]})
        fig_bar = go.Figure(data=[go.Bar(name="Target Budget", x=chart_df["Category"], y=chart_df["Target"], marker_color="#93C5FD"), go.Bar(name="Actual Spent", x=chart_df["Category"], y=chart_df["Actual"], marker_color="#1D4ED8")])
        fig_bar.update_layout(barmode="group", yaxis_title=f"Amount ({curr_symbol})", margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_bar, use_container_width=True)
    with col_g2:
        st.subheader("🍕 Total Expense Share Breakdown")
        if total_spent_disp > 0:
            fig_pie = px.pie(values=[actual_priority_disp, actual_needs_disp, actual_wants_disp, actual_savings_disp], names=["100% Mandatory", "Needs (50%)", "Wants (30%)", "Savings (20%)"], color_discrete_sequence=["#EF4444", "#2563EB", "#F59E0B", "#10B981"], hole=0.45)
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else: st.info("No expenses logged yet. Add your first payment in the Record Expense tab!")
    if not df_expenses.empty:
        st.markdown("---")
        col_g3, col_g4 = st.columns(2)
        with col_g3:
            st.subheader("🏷️ Top Expense Sub-Categories")
            sub_summary = df_expenses.groupby("Sub Category")["Amount (BHD)"].sum() * rate_mult
            sub_df = sub_summary.reset_index().sort_values(by="Amount (BHD)", ascending=True)
            fig_sub = px.bar(sub_df, x="Amount (BHD)", y="Sub Category", orientation="h", labels={"Amount (BHD)": f"Total Spent ({curr_symbol})"}, color_discrete_sequence=["#3B82F6"])
            fig_sub.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_sub, use_container_width=True)
        with col_g4:
            st.subheader("📈 Cumulative Spending Timeline")
            df_sorted = df_expenses.sort_values(by="Date").copy()
            df_sorted["Cumulative BHD"] = df_sorted["Amount (BHD)"].cumsum() * rate_mult
            fig_line = px.line(df_sorted, x="Date", y="Cumulative BHD", markers=True, labels={"Cumulative BHD": f"Cumulative Spent ({curr_symbol})"}, color_discrete_sequence=["#8B5CF6"])
            fig_line.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_line, use_container_width=True)

with tab_add:
    st.subheader("➕ Record a New Expense / Payment (" + str(current_user) + ")")
    with st.form("add_expense_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            exp_date = st.date_input("Transaction Date", value=datetime.today())
            main_cat = st.selectbox("Category", ["100% Priority & People to Pay", "Needs (50%)", "Wants (30%)", "Savings & Debt (20%)"])
            if "100%" in main_cat: sub_cats = ["People to Pay (Staff/Helper Salary)", "Family Support & Remittance (100%)", "Direct Mandatory Debt / Loan", "Fixed Emergency Obligation"]
            elif "Needs" in main_cat: sub_cats = ["Housing / Rent / Mortgage", "Utilities & Bills", "Groceries", "Transportation / Fuel", "Healthcare & Insurance", "Minimum Debt Payments"]
            elif "Wants" in main_cat: sub_cats = ["Dining Out & Coffee", "Entertainment & Streaming", "Shopping & Apparel", "Hobbies & Travel", "Subscriptions", "Miscellaneous"]
            else: sub_cats = ["Emergency Fund", "Retirement / Savings", "Stock / Investments", "Extra Debt Payoff", "Major Goal Savings"]
            sub_cat = st.selectbox("Sub-Category", sub_cats)
        with col_b:
            merchant = st.text_input("Merchant / Recipient Description", placeholder="e.g., Staff Name, Landlord, Store Name")
            c_col1, c_col2 = st.columns([1, 2])
            with c_col1: input_currency = st.selectbox("Payment Currency", ["BHD", "PHP", "USD"], index=0)
            with c_col2: amount_input = st.number_input("Amount Paid", min_value=0.01, step=5.0, value=25.0)
            payment_method = st.selectbox("Payment Method", ["Bank Transfer", "Credit Card", "Debit Card", "Cash"])
        submit_btn = st.form_submit_button("💾 Save Transaction", use_container_width=True)
        if submit_btn:
            amount_bhd = amount_input / EXCHANGE_RATES[input_currency]["rate"]
            new_row = pd.DataFrame([{"Date": exp_date, "Main Category": main_cat, "Sub Category": sub_cat, "Merchant/Description": merchant if merchant else "Unspecified", "Amount": amount_input, "Currency": input_currency, "Amount (BHD)": amount_bhd, "Payment Method": payment_method}])
            df_expenses = pd.concat([df_expenses, new_row], ignore_index=True)
            save_data(df_expenses)
            st.success("Successfully recorded payment!")
            st.rerun()

with tab_history:
    st.subheader("📜 Recorded Transaction History (" + str(current_user) + ")")
    if not df_expenses.empty:
        cat_filter = st.multiselect("Filter by Category", options=["100% Priority & People to Pay", "Needs (50%)", "Wants (30%)", "Savings & Debt (20%)"], default=["100% Priority & People to Pay", "Needs (50%)", "Wants (30%)", "Savings & Debt (20%)"])
        filtered_df = df_expenses[df_expenses["Main Category"].isin(cat_filter)] if cat_filter else df_expenses
        st.dataframe(filtered_df.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
        st.markdown("---")
        if st.button("🗑️ Clear All Expense Data", type="primary"):
            if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
            st.success("All transaction logs cleared!")
            st.rerun()
    else: st.info("No transaction history found. Start recording payments in the Record Expense tab!")

with tab_reports:
    st.subheader("📥 Download Financial Reports & Data")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if not df_expenses.empty:
            csv_data = df_expenses.to_csv(index=False).encode("utf-8")
            st.download_button(label="📥 Download CSV Ledger", data=csv_data, file_name="ledger.csv", mime="text/csv", use_container_width=True)
        else: st.info("No transaction records available to export.")
    with col_r2:
        rep_d = str(datetime.today().strftime("%Y-%m-%d"))
        report_text = "ROGEE FINANCIAL SUMMARY REPORT
User: " + str(current_user) + "
Date: " + rep_d + "

INCOME STREAMS (BHD):
Primary Salary: BD " + str(salary_bhd) + "
Business Income: BD " + str(business_bhd) + "
Sidelines: BD " + str(sidelines_bhd) + "
Other Income: BD " + str(other_income_bhd) + "
TOTAL COMBINED INCOME: BD " + str(total_income_bhd)
        st.download_button(label="📥 Download Summary Report", data=report_text, file_name="summary.txt", mime="text/plain", use_container_width=True)

with tab_calc:
    st.subheader("💱 Live Multi-Currency Converter (BHD ↔ PHP ↔ USD)")
    c_in1, c_in2 = st.columns(2)
    with c_in1:
        calc_amount = st.number_input("Amount to Convert", min_value=1.0, value=100.0, step=10.0)
        from_curr = st.selectbox("From Currency", ["BHD", "PHP", "USD"], index=0)
    with c_in2: to_curr = st.selectbox("To Currency", ["PHP", "USD", "BHD"], index=0)
    amount_in_bhd = calc_amount / EXCHANGE_RATES[from_curr]["rate"]
    converted_result = amount_in_bhd * EXCHANGE_RATES[to_curr]["rate"]
    st.success("Converted Amount: " + str(round(converted_result, 2)) + " " + str(to_curr))

with tab_guide:
    st.subheader("📘 Security & App Configuration Guide")
    st.markdown("Configure account access keys via Streamlit Cloud Secrets or app settings.")
