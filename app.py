import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import os
import json
import requests

st.set_page_config(
    page_title="Rogee's Financial Command Center",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 800; color: #1E3A8A; margin-bottom: 0.1rem; }
    .sub-header { font-size: 1.05rem; color: #4B5563; margin-bottom: 1.2rem; }
    .time-card { background-color: #F3F4F6; border: 1px solid #D1D5DB; border-radius: 8px; padding: 10px 15px; text-align: center; }
    .priority-banner { background-color: #FEF2F2; border: 1px solid #FECACA; border-left: 5px solid #EF4444; padding: 14px 18px; border-radius: 8px; margin-bottom: 18px; }
    .income-card { background-color: #F0FDF4; border: 1px solid #BBF7D0; border-left: 5px solid #22C55E; padding: 14px 18px; border-radius: 8px; margin-bottom: 18px; }
    .rate-card { background-color: #EFF6FF; border: 1px solid #BFDBFE; border-left: 5px solid #3B82F6; padding: 12px 16px; border-radius: 8px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

USER_PROFILES = {
    "Rogee": {
        "sec_key": "ROGEE_KEY",
        "def_key": "rogee2026",
        "data_file": "expenses_rogee.csv",
        "config_file": "config_rogee.json",
        "invest_file": "investments_rogee.csv"
    },
    "User 2": {
        "sec_key": "USER2_KEY",
        "def_key": "user2026",
        "data_file": "expenses_user2.csv",
        "config_file": "config_user2.json",
        "invest_file": "investments_user2.csv"
    }
}

@st.cache_data(ttl=1800)
def fetch_live_rates():
    base_rates = {'USD': 1.0, 'BHD': 0.377, 'PHP': 58.50, 'EUR': 0.92, 'GBP': 0.78, 'JPY': 152.0}
    try:
        u = base64.b64decode('aHR0cHM6Ly9vcGVuLmVyLWFwaS5jb20vdjYvbGF0ZXN0L1VTRA==').decode('utf-8')
        r = requests.get(u, timeout=4)
        if r.status_code == 200:
            data = r.json().get('rates', {})
            if 'BHD' in data and 'PHP' in data:
                return {k: float(data[k]) for k in ['USD', 'BHD', 'PHP', 'EUR', 'GBP', 'JPY'] if k in data}, True, datetime.now().strftime('%Y-%m-%d %H:%M')
    except Exception:
        pass
    return base_rates, False, datetime.now().strftime('%Y-%m-%d %H:%M (Benchmark)')

rates_dict, is_live_rates, last_rate_update = fetch_live_rates()

def check_authentication():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
        st.session_state['current_user'] = None
    
    if not st.session_state['authenticated']:
        st.markdown("<h2 style='text-align: center;'>Rogee&apos;s Financial Command Center</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B7280;'>Select profile and enter your private access key.</p>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            with st.form('login_form'):
                selected_user = st.selectbox('Select Account Profile', list(USER_PROFILES.keys()))
                entered_pass = st.text_input('Enter Access Key', type='password', placeholder='Access key')
                login_btn = st.form_submit_button('Unlock Dashboard', use_container_width=True)
                
                if login_btn:
                    user_info = USER_PROFILES[selected_user]
                    sec_obj = getattr(st, 'secrets', {})
                    expected_pass = sec_obj.get(user_info['sec_key'], user_info['def_key'])
                    
                    if entered_pass == expected_pass:
                        st.session_state['authenticated'] = True
                        st.session_state['current_user'] = selected_user
                        st.success(f'Welcome back, {selected_user}!')
                        st.rerun()
                    else:
                        st.error('Invalid access key. Please try again.')
        return False
    return True

if not check_authentication():
    st.stop()

current_user = st.session_state['current_user']
user_config = USER_PROFILES[current_user]
DATA_FILE = user_config['data_file']
CONFIG_FILE = user_config['config_file']
INVEST_FILE = user_config['invest_file']

def load_user_config():
    defaults = {
        'salary_bhd': 1500.0,
        'business_bhd': 0.0,
        'sidelines_bhd': 0.0,
        'other_income_bhd': 0.0,
        'fixed_priority_bhd': 300.0,
        'needs_pct': 50,
        'wants_pct': 30,
        'savings_pct': 20
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                saved = json.load(f)
                defaults.update(saved)
        except Exception:
            pass
    return defaults

def save_user_config(cfg):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(cfg, f, indent=4)
    except Exception:
        pass

cfg = load_user_config()

def load_data(file_path):
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=['Date', 'Main Category', 'Sub Category', 'Merchant/Description', 'Amount', 'Currency', 'Amount (BHD)', 'Payment Method'])

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

df_expenses = load_data(DATA_FILE)

def load_investments(file_path):
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except Exception:
            pass
    return pd.DataFrame(columns=['Type', 'Symbol/Ticker', 'Platform', 'Shares/Lots', 'Avg Buy Price', 'Current Price', 'Notes'])

df_invest = load_investments(INVEST_FILE)

st.sidebar.title('⚙️ Command Center Settings')
st.sidebar.markdown('**Current User:** ')

if st.sidebar.button('🔒 Lock App / Log Out', use_container_width=True):
    st.session_state['authenticated'] = False
    st.rerun()

st.sidebar.markdown('---')
st.sidebar.subheader('💱 Currency Display')
display_curr = st.sidebar.selectbox('Display Currency', ['BHD (BD)', 'PHP (₱)', 'USD ($)'], index=0)
curr_code = display_curr.split()[0]

bhd_to_usd = rates_dict.get('USD', 1.0) / rates_dict.get('BHD', 0.377)
bhd_to_php = rates_dict.get('PHP', 58.5) / rates_dict.get('BHD', 0.377)

EXCHANGE_RATES = {
    'BHD': {'symbol': 'BD ', 'rate': 1.0, 'name': 'Bahraini Dinar'},
    'PHP': {'symbol': '₱', 'rate': bhd_to_php, 'name': 'Philippine Peso'},
    'USD': {'symbol': '$', 'rate': bhd_to_usd, 'name': 'US Dollar'}
}

curr_symbol = EXCHANGE_RATES[curr_code]['symbol']
rate_mult = EXCHANGE_RATES[curr_code]['rate']

st.sidebar.markdown('---')
st.sidebar.subheader('💵 Income Streams (BHD)')
salary_bhd = st.sidebar.number_input('Primary Salary (BHD)', min_value=0.0, value=float(cfg['salary_bhd']), step=50.0)
business_bhd = st.sidebar.number_input('Business Income (BHD)', min_value=0.0, value=float(cfg['business_bhd']), step=25.0)
sidelines_bhd = st.sidebar.number_input('Sidelines / Freelance (BHD)', min_value=0.0, value=float(cfg['sidelines_bhd']), step=25.0)
other_income_bhd = st.sidebar.number_input('Other Income (BHD)', min_value=0.0, value=float(cfg['other_income_bhd']), step=25.0)

total_income_bhd = salary_bhd + business_bhd + sidelines_bhd + other_income_bhd
st.sidebar.markdown('### **Total Income: BD ' + str(round(total_income_bhd, 2)) + '**')

st.sidebar.markdown('---')
st.sidebar.subheader('🚨 100% Mandatory Payments')
fixed_priority_bhd = st.sidebar.number_input('Mandatory 100% Total (BHD)', min_value=0.0, value=float(cfg['fixed_priority_bhd']), step=25.0)

net_bhd_for_budget = max(0.0, total_income_bhd - fixed_priority_bhd)

st.sidebar.markdown('---')
st.sidebar.subheader('📊 50/30/20 Allocations (%)')
needs_pct = st.sidebar.slider('Needs Target %', 0, 100, int(cfg['needs_pct']))
wants_pct = st.sidebar.slider('Wants Target %', 0, 100, int(cfg['wants_pct']))
savings_pct = st.sidebar.slider('Savings Target %', 0, 100, int(cfg['savings_pct']))

if needs_pct + wants_pct + savings_pct != 100:
    st.sidebar.warning('Allocation total = ' + str(needs_pct + wants_pct + savings_pct) + '%. Should equal 100%.')

updated_cfg = {
    'salary_bhd': salary_bhd,
    'business_bhd': business_bhd,
    'sidelines_bhd': sidelines_bhd,
    'other_income_bhd': other_income_bhd,
    'fixed_priority_bhd': fixed_priority_bhd,
    'needs_pct': needs_pct,
    'wants_pct': wants_pct,
    'savings_pct': savings_pct
}
save_user_config(updated_cfg)

disp_total_income = total_income_bhd * rate_mult
disp_fixed = fixed_priority_bhd * rate_mult
disp_net_budget = net_bhd_for_budget * rate_mult

needs_target = disp_net_budget * (needs_pct / 100.0)
wants_target = disp_net_budget * (wants_pct / 100.0)
savings_target = disp_net_budget * (savings_pct / 100.0)

st.markdown('<div class="main-header">💰 Rogee&apos;s Financial Command Center</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multi-Currency Personal Finance & Investment Platform</div>', unsafe_allow_html=True)

utc_now = datetime.now(timezone.utc)
bh_time = utc_now + timedelta(hours=3)
ph_time = utc_now + timedelta(hours=8)

col_t1, col_t2 = st.columns(2)
with col_t1:
    st.markdown('<div class="time-card"><b>🇧🇭 Bahrain Date & Time (AST / UTC+3)</b><br><span style="font-size: 1.25rem; font-weight: 700; color: #1E3A8A;">' + bh_time.strftime('%A, %b %d, %Y | %I:%M:%S %p') + '</span></div>', unsafe_allow_html=True)

with col_t2:
    st.markdown('<div class="time-card"><b>🇵🇭 Philippines Date & Time (PHT / UTC+8)</b><br><span style="font-size: 1.25rem; font-weight: 700; color: #065F46;">' + ph_time.strftime('%A, %b %d, %Y | %I:%M:%S %p') + '</span></div>', unsafe_allow_html=True)

st.markdown('<br>', unsafe_allow_html=True)

rate_mode_str = '🟢 Auto-Updated' if is_live_rates else '🟡 Benchmark Mode'
st.markdown('<div class="rate-card">🌐 <b>Live Exchange Rates Engine (' + rate_mode_str + '):</b> <b>1 BHD</b> = <b>₱' + str(round(bhd_to_php, 2)) + ' PHP</b> | <b>1 BHD</b> = <b>$' + str(round(bhd_to_usd, 2)) + ' USD</b> | <b>1 USD</b> = <b>₱' + str(round(bhd_to_php/bhd_to_usd, 2)) + ' PHP</b><span style="float: right; color: #6B7280; font-size: 0.85rem;">Updated: ' + last_rate_update + '</span></div>', unsafe_allow_html=True)

tab_dash, tab_add, tab_history, tab_forex, tab_invest, tab_reports, tab_guide = st.tabs([
    '📈 Dashboard & Analytics',
    '➕ Record Expense',
    '📜 Transaction History',
    '💱 Live Forex Engine',
    '📊 MT5 & COL Investments',
    '📥 Download Reports',
    '📘 User Guide'
])

if not df_expenses.empty:
    actual_priority_bhd = df_expenses[df_expenses['Main Category'] == '100% Priority & People to Pay']['Amount (BHD)'].sum()
    actual_needs_bhd = df_expenses[df_expenses['Main Category'] == 'Needs (50%)']['Amount (BHD)'].sum()
    actual_wants_bhd = df_expenses[df_expenses['Main Category'] == 'Wants (30%)']['Amount (BHD)'].sum()
    actual_savings_bhd = df_expenses[df_expenses['Main Category'] == 'Savings & Debt (20%)']['Amount (BHD)'].sum()
else:
    actual_priority_bhd, actual_needs_bhd, actual_wants_bhd, actual_savings_bhd = 0.0, 0.0, 0.0, 0.0

total_spent_bhd = actual_priority_bhd + actual_needs_bhd + actual_wants_bhd + actual_savings_bhd
remaining_cash_bhd = total_income_bhd - total_spent_bhd

actual_priority_disp = actual_priority_bhd * rate_mult
actual_needs_disp = actual_needs_bhd * rate_mult
actual_wants_disp = actual_wants_bhd * rate_mult
actual_savings_disp = actual_savings_bhd * rate_mult

total_spent_disp = total_spent_bhd * rate_mult
remaining_cash_disp = remaining_cash_bhd * rate_mult

with tab_dash:
    st.markdown('<div class="income-card">', unsafe_allow_html=True)
    st.subheader('💵 Total Monthly Income Breakdown')
    c_inc1, c_inc2, c_inc3, c_inc4 = st.columns(4)
    c_inc1.metric('Primary Salary', 'BD ' + str(round(salary_bhd, 2)))
    c_inc2.metric('Business Income', 'BD ' + str(round(business_bhd, 2)))
    c_inc3.metric('Sidelines / Freelance', 'BD ' + str(round(sidelines_bhd, 2)))
    c_inc4.metric('Other Income', 'BD ' + str(round(other_income_bhd, 2)))
    st.write('**Total Combined Income:** ' + curr_symbol + str(round(disp_total_income, 2)) + ' (BD ' + str(round(total_income_bhd, 2)) + ')')
    st.markdown('</div>', unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric('Total Income', curr_symbol + str(round(disp_total_income, 2)))
    m2.metric('100% Priority Target', curr_symbol + str(round(disp_fixed, 2)))
    m3.metric('Total Spent To Date', curr_symbol + str(round(total_spent_disp, 2)))
    m4.metric('Remaining Net Cash', curr_symbol + str(round(remaining_cash_disp, 2)))

    st.markdown('---')

    st.markdown('<div class="priority-banner">', unsafe_allow_html=True)
    st.subheader('🚨 100% Mandatory Obligations Progress')
    p_col1, p_col2 = st.columns([2, 1])
    with p_col1:
        priority_pct = min(100.0, (actual_priority_bhd / fixed_priority_bhd * 100.0)) if fixed_priority_bhd > 0 else 0.0
        st.progress(priority_pct / 100.0)
        st.write('Paid **' + curr_symbol + str(round(actual_priority_disp, 2)) + '** of **' + curr_symbol + str(round(disp_fixed, 2)) + '** mandatory obligations.')
    with p_col2:
        rem_priority_disp = max(0.0, disp_fixed - actual_priority_disp)
        st.metric('Pending Priority Payments', curr_symbol + str(round(rem_priority_disp, 2)))
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('---')
    st.subheader('📊 Multi-Month Expense Trends & Category Breakdown')
    
    if not df_expenses.empty:
        df_exp_copy = df_expenses.copy()
        df_exp_copy['YearMonth'] = pd.to_datetime(df_exp_copy['Date']).dt.strftime('%Y-%m')
        df_exp_copy['DispAmount'] = df_exp_copy['Amount (BHD)'] * rate_mult

        col_ch1, col_ch2 = st.columns(2)
        with col_ch1:
            st.markdown('#### Monthly Expense Comparison Over Time')
            monthly_trend = df_exp_copy.groupby(['YearMonth', 'Main Category'])['DispAmount'].sum().reset_index()
            fig_trend = px.bar(
                monthly_trend, 
                x='YearMonth', 
                y='DispAmount', 
                color='Main Category', 
                barmode='stack',
                labels={'DispAmount': 'Amount (' + curr_code + ')', 'YearMonth': 'Month'},
                color_discrete_map={
                    '100% Priority & People to Pay': '#EF4444',
                    'Needs (50%)': '#2563EB',
                    'Wants (30%)': '#F59E0B',
                    'Savings & Debt (20%)': '#10B981'
                }
            )
            fig_trend.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_trend, use_container_width=True)

        with col_ch2:
            st.markdown('#### Spending Share by Main Category')
            fig_pie = px.pie(
                df_exp_copy, 
                values='DispAmount', 
                names='Main Category',
                hole=0.45,
                color='Main Category',
                color_discrete_map={
                    '100% Priority & People to Pay': '#EF4444',
                    'Needs (50%)': '#2563EB',
                    'Wants (30%)': '#F59E0B',
                    'Savings & Debt (20%)': '#10B981'
                }
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown('#### Multi-Month Category Summary Matrix')
        pivot_df = df_exp_copy.pivot_table(index='YearMonth', columns='Main Category', values='DispAmount', aggfunc='sum', fill_value=0.0)
        pivot_df['Total Monthly Spent'] = pivot_df.sum(axis=1)
        st.dataframe(pivot_df, use_container_width=True)

    else:
        st.info("No expense data recorded yet. Add your first payment in the 'Record Expense' tab!")
with tab_add:
    st.subheader("Record a New Payment / Expense (" + current_user + ")")
    with st.form("add_expense_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            exp_date = st.date_input("Date", value=datetime.today())
            main_cat = st.selectbox("Category", ["100% Priority & People to Pay", "Needs (50%)", "Wants (30%)", "Savings & Debt (20%)"])
            if "100%" in main_cat: sub_cats = ["People to Pay (Household Helper / Staff)", "Family Support & Remittance (100%)", "Direct Mandatory Loan / Debt", "Fixed Mandatory Utility / Bill"]
            elif "Needs" in main_cat: sub_cats = ["Housing / Rent / Mortgage", "Utilities & Bills", "Groceries", "Transportation / Fuel", "Healthcare / Insurance", "Minimum Debt Payments"]
            elif "Wants" in main_cat: sub_cats = ["Dining Out & Coffee", "Entertainment & Streaming", "Shopping & Apparel", "Hobbies & Travel", "Subscriptions", "Miscellaneous"]
            else: sub_cats = ["Emergency Fund", "Retirement / 401(k) / IRA", "Stock Investments (COL / Brokerage)", "Forex & Trading Deposit", "Major Goal Savings"]
            sub_cat = st.selectbox("Sub-Category", sub_cats)
        with col_b:
            merchant = st.text_input("Merchant / Description / Payee", placeholder="e.g. Household Helper Salary, Landlord, Grocery")
            amount_input = st.number_input("Amount", min_value=0.01, step=5.0, value=25.0)
            input_currency = st.selectbox("Payment Currency", ["BHD", "PHP", "USD"], index=0)
            payment_method = st.selectbox("Payment Method", ["Bank Transfer", "Credit Card", "Debit Card", "Cash"])
        submit_btn = st.form_submit_button("Save Payment Record", use_container_width=True)
        if submit_btn:
            amount_bhd = amount_input if input_currency == "BHD" else (amount_input / bhd_to_php if input_currency == "PHP" else amount_input / bhd_to_usd)
            new_row = pd.DataFrame([{"Date": exp_date, "Main Category": main_cat, "Sub Category": sub_cat, "Merchant/Description": merchant if merchant else "Unspecified", "Amount": amount_input, "Currency": input_currency, "Amount (BHD)": amount_bhd, "Payment Method": payment_method}])
            df_expenses = pd.concat([df_expenses, new_row], ignore_index=True)
            save_data(df_expenses, DATA_FILE)
            st.success("Recorded payment of " + EXCHANGE_RATES[input_currency]["symbol"] + str(round(amount_input, 2)) + " (" + sub_cat + ")!")
            st.rerun()

with tab_history:
    st.subheader("📜 Recorded Transaction History (" + current_user + ")")
    if not df_expenses.empty:
        total_recorded_bhd = df_expenses["Amount (BHD)"].sum()
        total_recorded_disp = total_recorded_bhd * rate_mult
        st.info("💰 **Total Recorded Expenses: " + curr_symbol + str(round(total_recorded_disp, 2)) + "** (BD " + str(round(total_recorded_bhd, 2)) + " | ₱" + str(round(total_recorded_bhd*bhd_to_php, 2)) + " | $" + str(round(total_recorded_bhd*bhd_to_usd, 2)) + ")")
        cat_filter = st.multiselect("Filter by Category", options=["100% Priority & People to Pay", "Needs (50%)", "Wants (30%)", "Savings & Debt (20%)"], default=["100% Priority & People to Pay", "Needs (50%)", "Wants (30%)", "Savings & Debt (20%)"])
        filtered_df = df_expenses[df_expenses["Main Category"].isin(cat_filter)] if cat_filter else df_expenses
        st.dataframe(filtered_df.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True)
        st.markdown("---")
        if st.button("🗑️ Clear All Expense Data", type="primary"):
            if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
            st.success("All transaction logs cleared!")
            st.rerun()
    else: st.info("No transaction history found.")

with tab_forex:
    st.subheader("💱 Live Forex Exchange Rates & Pair Selector")
    st.caption("Live financial rates updated daily across global currencies.")
    fx_col1, fx_col2 = st.columns(2)
    with fx_col1:
        st.markdown("#### Currency Pair Selector")
        pair_from = st.selectbox("Base Currency (From)", ["BHD", "USD", "PHP", "EUR", "GBP", "JPY"], index=0)
        pair_to = st.selectbox("Target Currency (To)", ["PHP", "USD", "BHD", "EUR", "GBP", "JPY"], index=0)
        calc_amt = st.number_input("Amount in " + pair_from, min_value=1.0, value=100.0, step=10.0)
        rate_from_usd = rates_dict.get(pair_from, 1.0)
        rate_to_usd = rates_dict.get(pair_to, 1.0)
        cross_rate = rate_to_usd / rate_from_usd
        converted_val = calc_amt * cross_rate
        st.success("### " + str(round(calc_amt, 2)) + " " + pair_from + " = **" + str(round(converted_val, 2)) + " " + pair_to + "**")
        st.info("💡 **Exchange Rate:** 1 " + pair_from + " =  " + pair_to)
    with fx_col2:
        st.markdown("#### Live Major Pairs Dashboard")
        st.markdown("* **1 BHD -> PHP:** ₱" + str(round(rates_dict.get("PHP", 58.5)/rates_dict.get("BHD", 0.377), 2)))
        st.markdown("* **1 BHD -> USD:** $" + str(round(rates_dict.get("USD", 1.0)/rates_dict.get("BHD", 0.377), 2)))
        st.markdown("* **1 USD -> PHP:** ₱" + str(round(rates_dict.get("PHP", 58.5)/rates_dict.get("USD", 1.0), 2)))
        st.markdown("* **1 EUR -> USD:** $" + str(round(rates_dict.get("USD", 1.0)/rates_dict.get("EUR", 0.92), 4)))
        st.markdown("* **1 GBP -> USD:** $" + str(round(rates_dict.get("USD", 1.0)/rates_dict.get("GBP", 0.78), 4)))
        st.markdown("* **1 USD -> JPY:** ¥" + str(round(rates_dict.get("JPY", 152.0)/rates_dict.get("USD", 1.0), 2)))
        if st.button("🔄 Force Refresh Live Rates Now"):
            st.cache_data.clear()
            st.rerun()

with tab_invest:
    st.subheader("📊 MT5 Forex & COL Financial Portfolio Manager")
    st.caption("Track your MetaTrader 5 trading accounts and COL Financial stock equity in one place.")
    st.markdown("> **Note on Live Trading Integration:**")
    st.markdown("> * **MetaTrader 5 (MT5):** Track balance, equity, margin, and open trading positions.")
    st.markdown("> * **COL Financial:** Track Philippine stock equity, portfolio holdings, and dividend gains.")
    with st.form("add_investment_form", clear_on_submit=True):
        inv_col1, inv_col2 = st.columns(2)
        with inv_col1:
            inv_type = st.selectbox("Asset Class / Platform", ["COL Financial (PH Stocks)", "MetaTrader 5 (Forex / Indices)", "Crypto / Other"])
            ticker = st.text_input("Ticker / Asset Symbol", placeholder="e.g., ALI, BDO, EURUSD, XAUUSD")
            platform = st.text_input("Broker / Platform Name", placeholder="e.g., COL Financial, IC Markets, Exness")
        with inv_col2:
            shares = st.number_input("Shares / Lots Owned", min_value=0.01, value=100.0)
            buy_price = st.number_input("Avg Purchase Price", min_value=0.0001, value=10.0)
            curr_price = st.number_input("Current Market Price", min_value=0.0001, value=12.0)
        inv_submit = st.form_submit_button("Add Asset Record", use_container_width=True)
        if inv_submit:
            new_row = pd.DataFrame([{"Type": inv_type, "Symbol/Ticker": ticker if ticker else "Unspecified", "Platform": platform if platform else "General", "Shares/Lots": shares, "Avg Buy Price": buy_price, "Current Price": curr_price, "Notes": "Recorded on " + datetime.today().strftime("%Y-%m-%d")}])
            df_invest = pd.concat([df_invest, new_row], ignore_index=True)
            df_invest.to_csv(INVEST_FILE, index=False)
            st.success("Added " + ticker + " to your investment tracker!")
            st.rerun()
    if not df_invest.empty:
        st.markdown("#### Current Investment Portfolio Ledger")
        df_invest["Total Value"] = df_invest["Shares/Lots"] * df_invest["Current Price"]
        df_invest["Total Cost"] = df_invest["Shares/Lots"] * df_invest["Avg Buy Price"]
        df_invest["Profit / Loss"] = df_invest["Total Value"] - df_invest["Total Cost"]
        df_invest["Gain %"] = (df_invest["Profit / Loss"] / df_invest["Total Cost"]) * 100
        st.dataframe(df_invest, use_container_width=True, hide_index=True)
        col_tot1, col_tot2 = st.columns(2)
        with col_tot1: st.metric("Total Portfolio Equity", "$" + str(round(df_invest["Total Value"].sum(), 2)))
        with col_tot2:
            tot_pnl = df_invest["Profit / Loss"].sum()
            st.metric("Total Un-realized P&L", "$" + str(round(tot_pnl, 2)), delta="$" + str(round(tot_pnl, 2)))
        if st.button("Clear Investment Ledger"):
            if os.path.exists(INVEST_FILE): os.remove(INVEST_FILE)
            st.rerun()

with tab_reports:
    st.subheader('📥 Download Financial Reports & Data')
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if not df_expenses.empty:
            csv_data = df_expenses.to_csv(index=False).encode('utf-8')
            st.download_button(label='📥 Download CSV Ledger', data=csv_data, file_name='financial_ledger_' + current_user.lower().replace(' ', '_') + '.csv', mime='text/csv', use_container_width=True)
        else: st.info('No transaction records available to export.')
    with col_r2:
        rep_date = datetime.today().strftime('%Y-%m-%d')
        total_exp_bhd = df_expenses['Amount (BHD)'].sum() if not df_expenses.empty else 0.0
        report_content = f"""
==================================================
ROGEE FINANCIAL COMMAND CENTER - EXECUTIVE REPORT
==================================================
User Profile   : {current_user}
Report Date    : {rep_date}
Bahrain Time   : {bh_time.strftime('%Y-%m-%d %I:%M %p')}
Philippine Time: {ph_time.strftime('%Y-%m-%d %I:%M %p')}
Exchange Rate  : 1 BHD = {bhd_to_php:,.2f} PHP =  USD

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
   - Equivalent in USD   : 

--------------------------------------------------
2. EXPENSES BREAKDOWN BY CATEGORY
--------------------------------------------------
- Mandatory 100% Payments: BD {actual_priority_bhd:,.2f}
- Needs (50% Target)     : BD {actual_needs_bhd:,.2f}
- Wants (30% Target)     : BD {actual_wants_bhd:,.2f}
- Savings & Debt (20%)   : BD {actual_savings_bhd:,.2f}
--------------------------------------------------
GRAND TOTAL EXPENSES     : BD {total_exp_bhd:,.2f}
NET REMAINING CASH       : BD {(total_income_bhd - total_exp_bhd):,.2f}
==================================================
"""
        st.download_button(label='📥 Download Executive Summary (.TXT)', data=report_content, file_name='financial_summary_' + current_user.lower().replace(' ', '_') + '.txt', mime='text/plain', use_container_width=True)

with tab_guide:
    st.subheader('📘 Security & Configuration Guide')
    st.markdown('Configure private access keys in Streamlit Cloud Secrets.')
