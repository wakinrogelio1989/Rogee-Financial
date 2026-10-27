import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

st.set_page_config(page_title="Rogee's Financial Command Center", page_icon="💰", layout="wide")

# --- ACCESS CONTROL GATE ---
def verify_user_access():
    secret_val = st.secrets.get('APP_' + 'KEY', 'rogee2026')
    def check_submission():
        if st.session_state.get('user_pass_key') == secret_val:
            st.session_state['user_auth'] = True
            if 'user_pass_key' in st.session_state:
                del st.session_state['user_pass_key']
        else:
            st.session_state['user_auth'] = False

    if 'user_auth' not in st.session_state:
        st.title('🔐 Rogee&apos;s Financial Command Center')
        st.caption('Enter your access passkey to unlock your financial dashboard.')
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.text_input('Access Passkey:', type='password', on_change=check_submission, key='user_pass_key')
            st.info('💡 Default Passkey: **`rogee2026`** (Configurable in Streamlit Secrets).')
        return False
    elif not st.session_state['user_auth']:
        st.title('🔐 Rogee&apos;s Financial Command Center')
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.text_input('Access Passkey:', type='password', on_change=check_submission, key='user_pass_key')
            st.error('❌ Incorrect passkey. Please try again.')
        return False
    else:
        return True

if not verify_user_access():
    st.stop()

DATA_FILE = 'expenses.csv'
EXCHANGE_RATES = {'BHD': {'symbol': 'BD ', 'rate': 1.0}, 'PHP': {'symbol': '₱', 'rate': 154.50}, 'USD': {'symbol': '$', 'rate': 2.65}}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=['Date', 'Main Category', 'Sub Category', 'Merchant/Description', 'Amount', 'Currency', 'Amount (BHD)', 'Payment Method'])

def save_data(df): df.to_csv(DATA_FILE, index=False)
df_expenses = load_data()

st.sidebar.title('⚙️ Settings')
display_curr = st.sidebar.selectbox('Display Currency', ['BHD (BD)', 'PHP (₱)', 'USD ($)'], index=0)
curr_code = display_curr.split()[0]
curr_symbol = EXCHANGE_RATES[curr_code]['symbol']
rate_mult = EXCHANGE_RATES[curr_code]['rate']

bhd_salary = st.sidebar.number_input('Monthly Take-Home Salary (BHD)', min_value=0.0, value=1500.0, step=50.0)
fixed_priority_bhd = st.sidebar.number_input('Mandatory 100% Payments Total (BHD)', min_value=0.0, value=300.0, step=25.0)
net_bhd_for_budget = max(0.0, bhd_salary - fixed_priority_bhd)

needs_pct = st.sidebar.slider('Needs Target %', 0, 100, 50)
wants_pct = st.sidebar.slider('Wants Target %', 0, 100, 30)
savings_pct = st.sidebar.slider('Savings Target %', 0, 100, 20)

if st.sidebar.button('🔒 Lock App'):
    st.session_state['user_auth'] = False
    st.rerun()

disp_salary = bhd_salary * rate_mult
disp_fixed = fixed_priority_bhd * rate_mult
disp_net_budget = net_bhd_for_budget * rate_mult

needs_target = disp_net_budget * (needs_pct / 100.0)
wants_target = disp_net_budget * (wants_pct / 100.0)
savings_target = disp_net_budget * (savings_pct / 100.0)

st.title('💰 Rogee&apos;s Financial Command Center')
st.caption('Multi-Currency Personal Finance Manager with Security Gate & 50/30/20 Framework')

st.info(f'''### 📊 Income Summary\n* **Base Salary:** BD {bhd_salary:,.2f}\n* **Peso Equivalent:** ₱{bhd_salary * 154.50:,.2f}\n* **USD Equivalent:** ${bhd_salary * 2.65:,.2f}''')

tab_dash, tab_add, tab_history, tab_calc, tab_guide = st.tabs(['📈 Dashboard', '➕ Add Expense', '📜 History', '💱 Converter', '📘 Security Setup'])

if not df_expenses.empty:
    actual_priority_bhd = df_expenses[df_expenses['Main Category'] == '100% Priority & People to Pay']['Amount (BHD)'].sum()
    actual_needs_bhd = df_expenses[df_expenses['Main Category'] == 'Needs (50%)']['Amount (BHD)'].sum()
    actual_wants_bhd = df_expenses[df_expenses['Main Category'] == 'Wants (30%)']['Amount (BHD)'].sum()
    actual_savings_bhd = df_expenses[df_expenses['Main Category'] == 'Savings & Debt (20%)']['Amount (BHD)'].sum()
else:
    actual_priority_bhd = actual_needs_bhd = actual_wants_bhd = actual_savings_bhd = 0.0

total_spent_bhd = actual_priority_bhd + actual_needs_bhd + actual_wants_bhd + actual_savings_bhd
remaining_cash_bhd = bhd_salary - total_spent_bhd
total_spent_disp = total_spent_bhd * rate_mult
remaining_cash_disp = remaining_cash_bhd * rate_mult
actual_priority_disp = actual_priority_bhd * rate_mult
actual_needs_disp = actual_needs_bhd * rate_mult
actual_wants_disp = actual_wants_bhd * rate_mult
actual_savings_disp = actual_savings_bhd * rate_mult

with tab_dash:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric('Gross Income', f'{curr_symbol}{disp_salary:,.2f}')
    m2.metric('100% Priority', f'{curr_symbol}{disp_fixed:,.2f}')
    m3.metric('Total Spent', f'{curr_symbol}{total_spent_disp:,.2f}')
    m4.metric('Remaining Balance', f'{curr_symbol}{remaining_cash_disp:,.2f}')
    st.markdown('---')
    st.subheader('📊 50/30/20 Allocation Summary')
    cat_data = [{'Category': 'Needs (50%)', 'Target': needs_target, 'Actual': actual_needs_disp}, {'Category': 'Wants (30%)', 'Target': wants_target, 'Actual': actual_wants_disp}, {'Category': 'Savings (20%)', 'Target': savings_target, 'Actual': actual_savings_disp}]
    st.dataframe(pd.DataFrame(cat_data), use_container_width=True, hide_index=True)

with tab_add:
    st.subheader('Record Payment')
    with st.form('add_exp'):
        exp_date = st.date_input('Date', value=datetime.today())
        main_cat = st.selectbox('Category Group', ['100% Priority & People to Pay', 'Needs (50%)', 'Wants (30%)', 'Savings & Debt (20%)'])
        sub_cat = st.text_input('Sub Category / Purpose', value='General')
        merchant = st.text_input('Merchant / Recipient')
        input_curr = st.selectbox('Currency', ['BHD', 'PHP', 'USD'])
        amount_input = st.number_input('Amount', min_value=0.01, value=50.0)
        pm = st.selectbox('Method', ['Bank Transfer', 'Cash', 'Credit Card'])
        if st.form_submit_button('Save'):
            amt_bhd = amount_input / EXCHANGE_RATES[input_curr]['rate']
            new_r = pd.DataFrame([{'Date': exp_date, 'Main Category': main_cat, 'Sub Category': sub_cat, 'Merchant/Description': merchant, 'Amount': amount_input, 'Currency': input_curr, 'Amount (BHD)': amt_bhd, 'Payment Method': pm}])
            df_expenses = pd.concat([df_expenses, new_r], ignore_index=True)
            save_data(df_expenses)
            st.success('Saved payment!')
            st.rerun()

with tab_history:
    st.subheader('Payment Log')
    if not df_expenses.empty: st.dataframe(df_expenses, use_container_width=True, hide_index=True)
    else: st.info('No transactions logged yet.')

with tab_calc:
    st.subheader('Currency Converter')
    amt = st.number_input('Convert Amount', min_value=1.0, value=100.0)
    fc = st.selectbox('From', ['BHD', 'PHP', 'USD'])
    tc = st.selectbox('To', ['PHP', 'USD', 'BHD'])
    res = (amt / EXCHANGE_RATES[fc]['rate']) * EXCHANGE_RATES[tc]['rate']
    st.success(f'{amt} {fc} = **{res:,.2f} {tc}**')

with tab_guide:
    st.subheader('📘 Passkey Configuration')
    st.markdown('Configure `APP_KEY` in Streamlit Cloud Secrets (Settings -> Secrets) to change your passkey.')