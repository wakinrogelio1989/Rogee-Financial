import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import os
import json
import urllib.request

# Set Streamlit page config
st.set_page_config(
    page_title="Rogee Financial Command Center",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for polished app feel & dark mode readability
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .notice-banner-green {
        background-color: #D1FAE5;
        border-left: 6px solid #10B981;
        padding: 12px 16px;
        border-radius: 6px;
        color: #065F46;
        font-weight: 600;
        margin-bottom: 15px;
    }
    .notice-banner-red {
        background-color: #FEE2E2;
        border-left: 6px solid #EF4444;
        padding: 12px 16px;
        border-radius: 6px;
        color: #991B1B;
        font-weight: 600;
        margin-bottom: 15px;
    }
    .card-blue {
        background-color: #EFF6FF;
        border-top: 4px solid #2563EB;
        padding: 15px;
        border-radius: 8px;
        color: #1E40AF;
    }
    .card-green {
        background-color: #F0FDF4;
        border-top: 4px solid #16A34A;
        padding: 15px;
        border-radius: 8px;
        color: #166534;
    }
    .card-red {
        background-color: #FEF2F2;
        border-top: 4px solid #DC2626;
        padding: 15px;
        border-radius: 8px;
        color: #991B1B;
    }
    .card-gold {
        background-color: #FEF3C7;
        border-top: 4px solid #D97706;
        padding: 15px;
        border-radius: 8px;
        color: #78350F;
    }
</style>
""", unsafe_allow_html=True)

DATA_FILE_DEFAULT = "expenses.csv"
STOCKS_FILE_DEFAULT = "stocks_rogee.csv"

# MASTER COLUMN ORDER FOR TRANSACTION LEDGER
MASTER_COLS = [
    "Item #",
    "Date",
    "Main Category",
    "Sub Category",
    "Merchant/Description",
    "Billed Amount",
    "Actual Paid",
    "Currency",
    "Pending Due",
    "% Paid",
    "% Remaining",
    "Equivalent",
    "Status",
    "Payment Method"
]

# Live Currency Rates Helper with Cache
@st.cache_data(ttl=3600)
def fetch_live_rates():
    try:
        url = "https://open.er-api.com/v6/latest/BHD"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            rates = data.get("rates", {})
            return rates.get("PHP", 155.0), rates.get("USD", 2.65), True
    except Exception:
        return 155.0, 2.65, False

bhd_to_php, bhd_to_usd, is_live = fetch_live_rates()

def get_user_file_paths(username):
    clean_user = username.lower().replace(" ", "_")
    data_file = f"expenses_{clean_user}.csv"
    stocks_file = f"stocks_{clean_user}.csv"
    proj_file = f"projections_{clean_user}.csv"
    settings_file = f"settings_{clean_user}.json"
    
    # Auto-migrate default data if user-specific file is missing
    if not os.path.exists(data_file) and os.path.exists(DATA_FILE_DEFAULT):
        try:
            df = pd.read_csv(DATA_FILE_DEFAULT)
            df.to_csv(data_file, index=False)
        except Exception:
            pass
    return data_file, stocks_file, proj_file, settings_file

def load_user_settings(settings_file):
    defaults = {"salary_bhd": 500.0, "sideline_bhd": 0.0, "business_bhd": 0.0, "other_bhd": 0.0}
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r") as f:
                saved = json.load(f)
                defaults.update(saved)
        except Exception:
            pass
    return defaults

def save_user_settings(settings_dict, settings_file):
    try:
        with open(settings_file, "w") as f:
            json.dump(settings_dict, f, indent=4)
    except Exception:
        pass

def load_data(data_file):
    if os.path.exists(data_file):
        try:
            df = pd.read_csv(data_file)
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date']).dt.date
            df = df.reindex(columns=MASTER_COLS)
            return df
        except Exception:
            pass
    return pd.DataFrame(columns=MASTER_COLS)

def save_data(df, data_file):
    df = df.reindex(columns=MASTER_COLS)
    df.to_csv(data_file, index=False)

def load_stocks(stocks_file):
    if os.path.exists(stocks_file):
        try:
            df = pd.read_csv(stocks_file)
            return df
        except Exception:
            pass
    return pd.DataFrame([
        {"Ticker": "SM", "Name": "SM Investments", "Shares": 500, "Avg Price (PHP/USD)": 850.0, "Currency": "PHP", "Market Price (PHP/USD)": 890.0},
        {"Ticker": "BDO", "Name": "BDO Unibank", "Shares": 1200, "Avg Price (PHP/USD)": 140.0, "Currency": "PHP", "Market Price (PHP/USD)": 152.0},
        {"Ticker": "MT5-EURUSD", "Name": "MT5 Forex Capital", "Shares": 1, "Avg Price (PHP/USD)": 2500.0, "Currency": "USD", "Market Price (PHP/USD)": 2650.0}
    ])

def save_stocks(df, stocks_file):
    df.to_csv(stocks_file, index=False)

# PASSCODE ACCESS CONTROL
USER_PASSCODES = {
    "Rogee": os.environ.get("ROGEE_KEY", "rogee2026"),
    "User 2": os.environ.get("USER2_KEY", "user2026"),
    "User 3": os.environ.get("USER3_KEY", "user2026"),
    "User 4": os.environ.get("USER4_KEY", "user2026")
}

if "authenticated_user" not in st.session_state:
    st.session_state["authenticated_user"] = None

if st.session_state["authenticated_user"] is None:
    st.markdown('<div style="text-align:center; padding: 2.5rem 1rem;"><h1 style="color:#1E3A8A; font-size: 2.5rem;">🔒 Rogee Financial Portal</h1><p style="color:#4B5563; font-size: 1.1rem;">Select your profile and enter your private passkey to access your personal financial command center.</p></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.form("login_form"):
            selected_user = st.selectbox("Select Profile", list(USER_PASSCODES.keys()))
            entered_passcode = st.text_input("Enter Passkey", type="password")
            login_submit = st.form_submit_button("🔓 Unlock Portal", use_container_width=True)
            if login_submit:
                if entered_passcode == USER_PASSCODES.get(selected_user):
                    st.session_state["authenticated_user"] = selected_user
                    st.success(f"Welcome back, {selected_user}!")
                    st.rerun()
                else:
                    st.error("Invalid passkey. Please check and try again.")
        with st.expander("💡 Default Passkeys Reference"):
            st.info("**Rogee**: `rogee2026` | **User 2 / 3 / 4**: `user2026`\n*Passkeys can also be configured securely in Streamlit Cloud Secrets.*")
    st.stop()

# ACTIVE USER CONTEXT
active_user = st.session_state["authenticated_user"]
user_data_file, user_stocks_file, user_proj_file, user_settings_file = get_user_file_paths(active_user)

# LOAD PERSISTENT USER SETTINGS
user_settings = load_user_settings(user_settings_file)

# SIDEBAR: SETTINGS & TARGETS
st.sidebar.title(f"👤 {active_user}'s Settings")

if st.sidebar.button("🔒 Sign Out / Lock Portal", use_container_width=True):
    st.session_state["authenticated_user"] = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("💵 Income Streams")

salary_bhd = st.sidebar.number_input("Primary Monthly Salary (BHD)", min_value=0.0, value=float(user_settings.get("salary_bhd", 500.0)), step=10.0)
sideline_bhd = st.sidebar.number_input("Sideline / Freelance Income (BHD)", min_value=0.0, value=float(user_settings.get("sideline_bhd", 0.0)), step=10.0)
business_bhd = st.sidebar.number_input("Business Income (BHD)", min_value=0.0, value=float(user_settings.get("business_bhd", 0.0)), step=10.0)
other_bhd = st.sidebar.number_input("Other Income / Bonus (BHD)", min_value=0.0, value=float(user_settings.get("other_bhd", 0.0)), step=10.0)

# Auto-save income settings if updated
current_settings = {
    "salary_bhd": salary_bhd,
    "sideline_bhd": sideline_bhd,
    "business_bhd": business_bhd,
    "other_bhd": other_bhd
}
if current_settings != user_settings:
    save_user_settings(current_settings, user_settings_file)

total_income_bhd = salary_bhd + sideline_bhd + business_bhd + other_bhd
total_income_php = total_income_bhd * bhd_to_php
total_income_usd = total_income_bhd * bhd_to_usd

st.sidebar.markdown(f"""
<div style="background-color:#F0FDF4; border:1px solid #BBF7D0; padding:10px; border-radius:6px; margin-bottom:12px;">
    <span style="color:#166534; font-size:0.85rem; font-weight:600;">Total Combined Income</span><br/>
    <strong style="color:#15803D; font-size:1.1rem;">BD {total_income_bhd:,.2f} BHD</strong><br/>
    <span style="color:#4B5563; font-size:0.85rem;">₱ {total_income_php:,.2f} PHP | ${total_income_usd:,.2f} USD</span>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Allocation Framework Targets (%)")
needs_pct = st.sidebar.slider("Needs & Debts Target %", 0, 100, 50)
wants_pct = st.sidebar.slider("Wants Target %", 0, 100, 30)
savings_pct = st.sidebar.slider("Savings Target %", 0, 100, 20)

total_pct = needs_pct + wants_pct + savings_pct
if total_pct != 100:
    st.sidebar.warning(f"Allocation total is {total_pct}%. Adjust to equal exactly 100%.")

# DYNAMIC FRAMEWORK TITLE
framework_title = f"{needs_pct}/{wants_pct}/{savings_pct} Budget Framework"

# CALCULATE TARGET AMOUNTS IN BHD
needs_target = total_income_bhd * (needs_pct / 100.0)
wants_target = total_income_bhd * (wants_pct / 100.0)
savings_target = total_income_bhd * (savings_pct / 100.0)

# MAIN HEADER
st.markdown('<div class="main-header">Rogee Financial Command Center</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Personal Finance & Investment Dashboard based on the <b>{framework_title}</b></div>', unsafe_allow_html=True)

# LOAD USER EXPENSES & STOCKS
df_expenses = load_data(user_data_file)
df_stocks = load_stocks(user_stocks_file)

# HELPER: RECALCULATE EXPENSE LEDGER
def recalculate_ledger(df):
    if df.empty:
        return pd.DataFrame(columns=MASTER_COLS)
    
    df = df.copy()
    if 'Billed Amount' not in df.columns and 'Amount' in df.columns:
        df['Billed Amount'] = df['Amount']
    if 'Actual Paid' not in df.columns:
        df['Actual Paid'] = df['Billed Amount']
    if 'Currency' not in df.columns:
        df['Currency'] = "BHD"
        
    df['Billed Amount'] = pd.to_numeric(df['Billed Amount'], errors='coerce').fillna(0.0)
    df['Actual Paid'] = pd.to_numeric(df['Actual Paid'], errors='coerce').fillna(0.0)
    
    df['Pending Due'] = df['Billed Amount'] - df['Actual Paid']
    df['% Paid'] = df.apply(lambda r: round((r['Actual Paid'] / r['Billed Amount'] * 100), 1) if r['Billed Amount'] > 0 else 100.0, axis=1)
    df['% Remaining'] = df.apply(lambda r: round((r['Pending Due'] / r['Billed Amount'] * 100), 1) if r['Billed Amount'] > 0 else 0.0, axis=1)
    
    def get_status(r):
        if r['Pending Due'] <= 0 or r['% Paid'] >= 100:
            return "Paid"
        elif r['Actual Paid'] > 0:
            return "Partially Paid"
        else:
            return "Not Paid"
            
    df['Status'] = df.apply(get_status, axis=1)
    
    def get_equiv(r):
        curr = str(r['Currency']).upper()
        amt = r['Billed Amount']
        if curr == "PHP":
            bd_val = amt / bhd_to_php
            usd_val = bd_val * bhd_to_usd
            return f"BD {bd_val:,.2f} | ${usd_val:,.2f}"
        elif curr == "USD":
            bd_val = amt / bhd_to_usd
            php_val = bd_val * bhd_to_php
            return f"BD {bd_val:,.2f} | ₱ {php_val:,.2f}"
        else:
            php_val = amt * bhd_to_php
            usd_val = amt * bhd_to_usd
            return f"₱ {php_val:,.2f} | ${usd_val:,.2f}"
            
    df['Equivalent'] = df.apply(get_equiv, axis=1)
    df['Item #'] = range(1, len(df) + 1)
    
    # Reindex columns to MASTER_COLS
    df = df.reindex(columns=MASTER_COLS)
    return df

df_expenses = recalculate_ledger(df_expenses)

# CALCULATE ACTUAL SPENDING BY MAIN CATEGORY (In BHD Equivalent)
def calc_bhd_spent(cat_keyword):
    if df_expenses.empty:
        return 0.0
    sub = df_expenses[df_expenses['Main Category'].str.contains(cat_keyword, case=False, na=False)]
    total_bd = 0.0
    for _, r in sub.iterrows():
        curr = str(r['Currency']).upper()
        amt = float(r['Actual Paid'])
        if curr == "PHP":
            total_bd += amt / bhd_to_php
        elif curr == "USD":
            total_bd += amt / bhd_to_usd
        else:
            total_bd += amt
    return total_bd

actual_needs = calc_bhd_spent("Needs") + calc_bhd_spent("Debts")
actual_wants = calc_bhd_spent("Wants")
actual_savings = calc_bhd_spent("Savings")

total_spent_bhd = actual_needs + actual_wants + actual_savings
remaining_cash_bhd = total_income_bhd - total_spent_bhd
savings_rate = (actual_savings / total_income_bhd * 100) if total_income_bhd > 0 else 0.0

# TABS
tab_dash, tab_add, tab_history, tab_stocks, tab_proj, tab_mt5, tab_converter = st.tabs([
    "📊 Dashboard & Analytics",
    "➕ Record Expense",
    "📋 Transaction History",
    "📈 MT5 & COL Investments",
    "🔮 12-Month Projections",
    "📐 MT5 Pip Calculator",
    "💱 Live Currency Converter"
])

# TAB 1: DASHBOARD
with tab_dash:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Monthly Net Income", f"BD {total_income_bhd:,.2f}", f"₱ {total_income_php:,.0f} PHP")
    m2.metric("Total Spent", f"BD {total_spent_bhd:,.2f}", delta=f"-BD {total_spent_bhd:,.2f}", delta_color="inverse")
    
    if remaining_cash_bhd >= 0:
        m3.metric("Remaining Balance", f"BD {remaining_cash_bhd:,.2f}", delta=f"BD {remaining_cash_bhd:,.2f}")
    else:
        m3.metric("Over Budget Deficit", f"-BD {abs(remaining_cash_bhd):,.2f}", delta=f"-BD {abs(remaining_cash_bhd):,.2f}", delta_color="inverse")
        
    m4.metric("Savings & Investment Rate", f"{savings_rate:.1f}%", delta=f"{savings_rate - savings_pct:.1f}% vs Target")
    
    st.markdown("---")
    st.subheader(f"📊 {framework_title} Allocation Breakdown")
    
    cat_data = [
        {"Category": f"Needs & Debts ({needs_pct}%)", "Target Allocation": f"{needs_pct}%", "Target (BHD)": needs_target, "Actual Spent (BHD)": actual_needs, "Difference (BHD)": needs_target - actual_needs, "Status": "On Track" if actual_needs <= needs_target else "Over Target"},
        {"Category": f"Wants ({wants_pct}%)", "Target Allocation": f"{wants_pct}%", "Target (BHD)": wants_target, "Actual Spent (BHD)": actual_wants, "Difference (BHD)": wants_target - actual_wants, "Status": "On Track" if actual_wants <= wants_target else "Over Target"},
        {"Category": f"Savings ({savings_pct}%)", "Target Allocation": f"{savings_pct}%", "Target (BHD)": savings_target, "Actual Spent (BHD)": actual_savings, "Difference (BHD)": actual_savings - savings_target, "Status": "Target Met" if actual_savings >= savings_target else "Under Goal"}
    ]
    df_cat_summary = pd.DataFrame(cat_data)
    
    st.dataframe(
        df_cat_summary.style.format({
            "Target (BHD)": "BD {:,.2f}",
            "Actual Spent (BHD)": "BD {:,.2f}",
            "Difference (BHD)": "BD {:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Target vs. Actual Spending (BHD)")
        chart_df = pd.DataFrame({
            "Category": ["Needs & Debts", "Wants", "Savings"],
            "Target": [needs_target, wants_target, savings_target],
            "Actual": [actual_needs, actual_wants, actual_savings]
        })
        fig_bar = go.Figure(data=[
            go.Bar(name='Target Target', x=chart_df['Category'], y=chart_df['Target'], marker_color='#93C5FD'),
            go.Bar(name='Actual Spent', x=chart_df['Category'], y=chart_df['Actual'], marker_color='#1D4ED8')
        ])
        fig_bar.update_layout(
            barmode='group',
            yaxis_title="Amount (BHD)",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with c2:
        st.subheader("Actual Expense Distribution Share")
        if total_spent_bhd > 0:
            fig_pie = px.pie(
                values=[actual_needs, actual_wants, actual_savings],
                names=["Needs & Debts", "Wants", "Savings"],
                color_discrete_sequence=['#2563EB', '#F59E0B', '#10B981'],
                hole=0.45
            )
            fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expenses logged yet. Add your first expense in the 'Record Expense' tab!")

# TAB 2: ADD EXPENSE
with tab_add:
    st.subheader("Record a New Expense or Bill Payment")
    
    with st.form("add_expense_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        
        with col_a:
            exp_date = st.date_input("Transaction Date", value=datetime.today())
            main_cat = st.selectbox("Main Category", [
                f"Needs & Debts ({needs_pct}%)",
                f"Wants ({wants_pct}%)",
                f"Savings ({savings_pct}%)",
                "100% Priority",
                "Debts & Credits Payoff"
            ])
            
            if "Needs" in main_cat or "Debts" in main_cat or "Priority" in main_cat:
                sub_cats = ["Housing / Rent / Mortgage", "Utilities & Bills", "Groceries", "Transportation / Fuel", "Healthcare / Insurance", "Personal Loan", "Settle Debt", "Tuition & Family"]
            elif "Wants" in main_cat:
                sub_cats = ["Dining Out & Coffee", "Entertainment & Streaming", "Shopping & Apparel", "Hobbies & Travel", "Subscriptions", "Miscellaneous"]
            else:
                sub_cats = ["Emergency Fund", "Retirement / Savings", "Stock Investments", "Extra Debt Payoff", "Major Goal Savings"]
                
            sub_cat = st.selectbox("Sub-Category", sub_cats)
            merchant = st.text_input("Merchant / Description / Payee", placeholder="e.g. EWA Utility, Flat Rent, Coop Loan")
            
        with col_b:
            exp_curr = st.selectbox("Payment Currency", ["BHD", "PHP", "USD"], index=0)
            billed_amt = st.number_input(f"Billed / Target Amount ({exp_curr})", min_value=0.0, step=5.0, value=50.0)
            actual_paid = st.number_input(f"Actual Amount Paid ({exp_curr})", min_value=0.0, step=5.0, value=50.0)
            payment_method = st.selectbox("Payment Method", ["Bank Transfer", "Credit Card", "Debit Card", "Cash", "GCash"])
            
        submit_btn = st.form_submit_button("💾 Save Expense Log", use_container_width=True)
        
        if submit_btn:
            new_row = pd.DataFrame([{
                "Item #": len(df_expenses) + 1,
                "Date": exp_date,
                "Main Category": main_cat,
                "Sub Category": sub_cat,
                "Merchant/Description": merchant if merchant else "Unspecified",
                "Billed Amount": billed_amt,
                "Actual Paid": actual_paid,
                "Currency": exp_curr,
                "Payment Method": payment_method
            }])
            
            df_combined = pd.concat([df_expenses, new_row], ignore_index=True)
            df_updated = recalculate_ledger(df_combined)
            save_data(df_updated, user_data_file)
            st.success(f"Successfully added expense log for '{merchant if merchant else sub_cat}' ({exp_curr} {actual_paid:,.2f})!")
            st.rerun()

# TAB 3: TRANSACTION HISTORY
with tab_history:
    st.subheader("📋 Recorded Expense History & Payment Ledger")
    
    # REAL-TIME BUDGET NOTICE BANNER ABOVE TRANSACTIONS
    if remaining_cash_bhd >= 0:
        st.markdown(f"""
        <div class="notice-banner-green">
            🟢 WITHIN BUDGET STATUS: You have available unspent net cash balance!<br/>
            <span style="font-size: 1.1rem; font-weight:700;">Net Unspent Cash Balance: BD {remaining_cash_bhd:,.2f} BHD &nbsp;|&nbsp; ₱ {remaining_cash_bhd * bhd_to_php:,.2f} PHP &nbsp;|&nbsp; ${remaining_cash_bhd * bhd_to_usd:,.2f} USD</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="notice-banner-red">
            🚨 OVER BUDGET STATUS NOTICE: Total payments exceed your monthly income limit!<br/>
            <span style="font-size: 1.1rem; font-weight:700;">Current Overage / Limit Deficit: -BD {abs(remaining_cash_bhd):,.2f} BHD &nbsp;|&nbsp; -₱ {abs(remaining_cash_bhd) * bhd_to_php:,.2f} PHP &nbsp;|&nbsp; -${abs(remaining_cash_bhd) * bhd_to_usd:,.2f} USD</span>
        </div>
        """, unsafe_allow_html=True)

    if not df_expenses.empty:
        st.markdown("##### ✏️ Interactive Editable Ledger Grid")
        st.caption("Double-click any cell to edit details directly, then click 'Save Ledger Changes'. Column sequence is locked to MASTER_COLS.")
        
        # Ensure df_expenses follows MASTER_COLS order
        df_expenses = df_expenses.reindex(columns=MASTER_COLS)
        
        edited_df = st.data_editor(
            df_expenses,
            column_order=MASTER_COLS,
            use_container_width=True,
            hide_index=True,
            key="ledger_editor"
        )
        
        c_save, c_clear = st.columns([2, 1])
        with c_save:
            if st.button("💾 Save Ledger Changes", type="primary", use_container_width=True):
                recalc_df = recalculate_ledger(edited_df)
                save_data(recalc_df, user_data_file)
                st.success("Ledger changes saved successfully!")
                st.rerun()
                
        st.markdown("---")
        st.markdown("##### 🎨 Status-Highlighted Color Ledger View")
        
        def highlight_status(row):
            status = str(row.get("Status", "")).strip()
            if status == "Paid":
                return ['background-color: #D1FAE5; color: #065F46; font-weight: 500;'] * len(row)
            elif status == "Partially Paid":
                return ['background-color: #FEF3C7; color: #92400E; font-weight: 500;'] * len(row)
            else:
                return ['background-color: #FEE2E2; color: #991B1B; font-weight: 500;'] * len(row)
                
        st.dataframe(
            df_expenses.style.apply(highlight_status, axis=1),
            use_container_width=True,
            hide_index=True
        )
        
        # TOTAL OUTSTANDING & PAYMENT LEDGER SUMMARY BELOW TRANSACTIONS
        st.markdown("---")
        st.subheader("💰 Total Outstanding & Payment Ledger Summary")
        
        # Calculate summary metrics by currency
        bhd_items = df_expenses[df_expenses['Currency'] == "BHD"]
        php_items = df_expenses[df_expenses['Currency'] == "PHP"]
        usd_items = df_expenses[df_expenses['Currency'] == "USD"]
        
        bhd_billed = bhd_items['Billed Amount'].sum() if not bhd_items.empty else 0.0
        bhd_paid = bhd_items['Actual Paid'].sum() if not bhd_items.empty else 0.0
        bhd_pending = bhd_items['Pending Due'].sum() if not bhd_items.empty else 0.0
        
        php_billed = php_items['Billed Amount'].sum() if not php_items.empty else 0.0
        php_paid = php_items['Actual Paid'].sum() if not php_items.empty else 0.0
        php_pending = php_items['Pending Due'].sum() if not php_items.empty else 0.0
        
        usd_billed = usd_items['Billed Amount'].sum() if not usd_items.empty else 0.0
        usd_paid = usd_items['Actual Paid'].sum() if not usd_items.empty else 0.0
        usd_pending = usd_items['Pending Due'].sum() if not usd_items.empty else 0.0
        
        # Conversions to BHD
        php_billed_in_bhd = php_billed / bhd_to_php
        php_paid_in_bhd = php_paid / bhd_to_php
        php_pending_in_bhd = php_pending / bhd_to_php
        
        usd_billed_in_bhd = usd_billed / bhd_to_usd
        usd_paid_in_bhd = usd_paid / bhd_to_usd
        usd_pending_in_bhd = usd_pending / bhd_to_usd
        
        # GRAND TOTALS CONVERTED ALL TO BHD
        grand_total_billed_bhd = bhd_billed + php_billed_in_bhd + usd_billed_in_bhd
        grand_total_paid_bhd = bhd_paid + php_paid_in_bhd + usd_paid_in_bhd
        grand_total_pending_bhd = bhd_pending + php_pending_in_bhd + usd_pending_in_bhd
        
        s1, s2, s3, s4 = st.columns(4)
        
        with s1:
            st.markdown(f"""
            <div class="card-blue">
                <h4 style="margin:0; color:#1E40AF;">🇧🇭 BHD Currency Bills</h4>
                <hr style="margin:8px 0; border-color:#93C5FD;"/>
                <b>Total Billed:</b> BD {bhd_billed:,.2f}<br/>
                <b>Total Paid:</b> BD {bhd_paid:,.2f}<br/>
                <b>Pending Due:</b> <span style="color:#991B1B; font-weight:700;">BD {bhd_pending:,.2f}</span>
            </div>
            """, unsafe_allow_html=True)
            
        with s2:
            st.markdown(f"""
            <div class="card-gold">
                <h4 style="margin:0; color:#78350F;">🇵🇭 PHP Currency Bills</h4>
                <hr style="margin:8px 0; border-color:#FDE68A;"/>
                <b>Total Billed:</b> ₱ {php_billed:,.2f}<br/>
                <small style="color:#4B5563;">↳ Equivalent: BD {php_billed_in_bhd:,.2f}</small><br/>
                <b>Total Paid:</b> ₱ {php_paid:,.2f}<br/>
                <small style="color:#4B5563;">↳ Equivalent: BD {php_paid_in_bhd:,.2f}</small><br/>
                <b>Pending Due:</b> <span style="color:#991B1B; font-weight:700;">₱ {php_pending:,.2f}</span><br/>
                <small style="color:#991B1B; font-weight:600;">↳ Equivalent: BD {php_pending_in_bhd:,.2f}</small>
            </div>
            """, unsafe_allow_html=True)
            
        with s3:
            st.markdown(f"""
            <div class="card-green">
                <h4 style="margin:0; color:#166534;">💵 USD Currency Bills</h4>
                <hr style="margin:8px 0; border-color:#A7F3D0;"/>
                <b>Total Billed:</b> ${usd_billed:,.2f}<br/>
                <small style="color:#4B5563;">↳ Equivalent: BD {usd_billed_in_bhd:,.2f}</small><br/>
                <b>Total Paid:</b> ${usd_paid:,.2f}<br/>
                <small style="color:#4B5563;">↳ Equivalent: BD {usd_paid_in_bhd:,.2f}</small><br/>
                <b>Pending Due:</b> <span style="color:#991B1B; font-weight:700;">${usd_pending:,.2f}</span><br/>
                <small style="color:#991B1B; font-weight:600;">↳ Equivalent: BD {usd_pending_in_bhd:,.2f}</small>
            </div>
            """, unsafe_allow_html=True)
            
        with s4:
            st.markdown(f"""
            <div class="card-red">
                <h4 style="margin:0; color:#991B1B;">🌍 Combined Grand Total (In BD)</h4>
                <hr style="margin:8px 0; border-color:#FCA5A5;"/>
                <b>Grand Billed Total:</b> <br/><span style="font-size:1.1rem; font-weight:700; color:#1E40AF;">BD {grand_total_billed_bhd:,.2f}</span><br/>
                <b>Grand Actual Paid:</b> <br/><span style="font-size:1.1rem; font-weight:700; color:#166534;">BD {grand_total_paid_bhd:,.2f}</span><br/>
                <b>Grand Pending Due:</b> <br/><span style="font-size:1.1rem; font-weight:700; color:#991B1B;">BD {grand_total_pending_bhd:,.2f}</span>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        
        # EXPORT CSV WITH LOCKED COLUMN ORDER
        csv_data = df_expenses.reindex(columns=MASTER_COLS).to_csv(index=False)
        st.download_button(
            label="📥 Download Transaction Ledger CSV",
            data=csv_data,
            file_name=f"rogee_ledger_{active_user.lower()}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No expense transactions recorded yet. Add an expense using the 'Record Expense' tab!")

# TAB 4: STOCKS & TRADING
with tab_stocks:
    st.subheader("📈 MT5 & COL Financial Investment Portfolio")
    st.caption("Manage Philippine stock investments (COL Financial) and Forex trading accounts (MT5).")
    
    if not df_stocks.empty:
        edited_stocks = st.data_editor(
            df_stocks,
            use_container_width=True,
            hide_index=True,
            key="stocks_editor"
        )
        
        if st.button("💾 Save Stock Portfolio Changes", type="primary"):
            save_stocks(edited_stocks, user_stocks_file)
            st.success("Stock portfolio updated!")
            st.rerun()
            
        # PORTFOLIO VALUATION SUMMARY
        total_val_bhd = 0.0
        for _, r in edited_stocks.iterrows():
            curr = str(r.get("Currency", "PHP")).upper()
            mkt_price = float(r.get("Market Price (PHP/USD)", 0.0))
            shares = float(r.get("Shares", 0.0))
            val = mkt_price * shares
            if curr == "PHP":
                total_val_bhd += val / bhd_to_php
            elif curr == "USD":
                total_val_bhd += val / bhd_to_usd
            else:
                total_val_bhd += val
                
        st.markdown("---")
        v1, v2, v3 = st.columns(3)
        v1.metric("Total Portfolio Value (BHD)", f"BD {total_val_bhd:,.2f}")
        v2.metric("Equivalent Portfolio Value (PHP)", f"₱ {total_val_bhd * bhd_to_php:,.2f} PHP")
        v3.metric("Equivalent Portfolio Value (USD)", f"${total_val_bhd * bhd_to_usd:,.2f} USD")
    else:
        st.info("No stock assets logged yet.")

# TAB 5: 12-MONTH PROJECTIONS
with tab_proj:
    st.subheader("🔮 12-Month Projected Budget & Wealth Engine")
    st.caption("Edit future month-by-month targets directly in the table below to customize your financial forecast.")
    
    # Initialize projection table dataframe
    proj_months = [f"Month {i}" for i in range(1, 13)]
    default_proj_data = []
    for i, m in enumerate(proj_months, 1):
        inc = total_income_bhd * (1 + (i * 0.005))
        needs = inc * (needs_pct / 100.0)
        wants = inc * (wants_pct / 100.0)
        sav = inc * (savings_pct / 100.0)
        default_proj_data.append({
            "Month": m,
            "Projected Income (BHD)": round(inc, 2),
            "Needs & Debts (BHD)": round(needs, 2),
            "Wants (BHD)": round(wants, 2),
            "Savings & Investment (BHD)": round(sav, 2),
            "Net Surplus (BHD)": round(inc - (needs + wants + sav), 2)
        })
        
    if os.path.exists(user_proj_file):
        try:
            df_proj = pd.read_csv(user_proj_file)
        except Exception:
            df_proj = pd.DataFrame(default_proj_data)
    else:
        df_proj = pd.DataFrame(default_proj_data)
        
    edited_proj = st.data_editor(
        df_proj,
        use_container_width=True,
        hide_index=True,
        key="proj_editor"
    )
    
    p_col1, p_col2 = st.columns([1, 1])
    with p_col1:
        if st.button("💾 Save 12-Month Projections", type="primary", use_container_width=True):
            edited_proj.to_csv(user_proj_file, index=False)
            st.success("Projections updated successfully!")
            st.rerun()
    with p_col2:
        proj_csv = edited_proj.to_csv(index=False)
        st.download_button(
            label="📥 Download 12-Month Forecast CSV",
            data=proj_csv,
            file_name=f"12_month_projections_{active_user.lower()}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    st.markdown("---")
    fig_proj = go.Figure()
    fig_proj.add_trace(go.Bar(x=edited_proj["Month"], y=edited_proj["Projected Income (BHD)"], name="Projected Income", marker_color="#3B82F6"))
    fig_proj.add_trace(go.Bar(x=edited_proj["Month"], y=edited_proj["Savings & Investment (BHD)"], name="Savings", marker_color="#10B981"))
    fig_proj.update_layout(barmode="group", title="12-Month Income vs. Savings Trajectory (BHD)", yaxis_title="Amount (BHD)")
    st.plotly_chart(fig_proj, use_container_width=True)

# TAB 6: MT5 PIP CALCULATOR
with tab_mt5:
    st.subheader("📐 MT5 Pip Value & Risk Calculator")
    st.caption("Calculate exact pip value and lot sizing for MetaTrader 5 position management.")
    
    col_mt1, col_mt2 = st.columns(2)
    with col_mt1:
        pair = st.selectbox("Trading Asset / Pair", ["USDPHP", "BHDPHP", "EURUSD", "GBPUSD", "USDJPY", "XAUUSD (Gold)", "USDCAD"])
        lot_size = st.number_input("Lot Size", min_value=0.01, step=0.01, value=0.10)
        entry_price = st.number_input("Entry Price", min_value=0.0, value=1.0850 if "EUR" in pair else (2700.0 if "XAU" in pair else 155.0))
        exit_price = st.number_input("Exit / Target Price", min_value=0.0, value=1.0900 if "EUR" in pair else (2720.0 if "XAU" in pair else 156.0))
        
    with col_mt2:
        pip_diff = abs(exit_price - entry_price) * (100 if "JPY" in pair or "PHP" in pair else (10 if "XAU" in pair else 10000))
        est_pnl_usd = pip_diff * lot_size * 10
        est_pnl_bhd = est_pnl_usd / bhd_to_usd
        est_pnl_php = est_pnl_bhd * bhd_to_php
        
        st.markdown(f"""
        <div class="card-blue">
            <h4 style="margin:0;">📊 Trade Calculation Summary</h4>
            <hr style="margin:8px 0; border-color:#93C5FD;"/>
            <b>Pip Movement:</b> {pip_diff:,.1f} Pips<br/>
            <b>Estimated Profit / Loss (USD):</b> ${est_pnl_usd:,.2f}<br/>
            <b>Estimated Profit / Loss (BHD):</b> BD {est_pnl_bhd:,.2f}<br/>
            <b>Estimated Profit / Loss (PHP):</b> ₱ {est_pnl_php:,.2f}
        </div>
        """, unsafe_allow_html=True)

# TAB 7: LIVE CURRENCY CONVERTER
with tab_converter:
    st.subheader("💱 On-the-Spot Live Currency Converter")
    st.caption(f"Real-time market rates fetched automatically. Status: {'🟢 Connected Live' if is_live else '🟡 Fallback Offline Mode'}")
    
    c_conv1, c_conv2 = st.columns(2)
    with c_conv1:
        from_curr = st.selectbox("From Currency", ["BHD", "PHP", "USD", "EUR", "GBP", "CAD", "AED", "SAR"], index=0)
        conv_amt = st.number_input("Amount to Convert", min_value=0.0, value=100.0, step=10.0)
    with c_conv2:
        to_curr = st.selectbox("To Currency", ["PHP", "BHD", "USD", "EUR", "GBP", "CAD", "AED", "SAR"], index=0)
        
        # Rate logic
        rates = {"BHD": 1.0, "PHP": bhd_to_php, "USD": bhd_to_usd, "EUR": bhd_to_usd * 0.92, "GBP": bhd_to_usd * 0.78, "CAD": bhd_to_usd * 1.38, "AED": 3.67 * (bhd_to_usd/2.65), "SAR": 3.75 * (bhd_to_usd/2.65)}
        
        converted_val = (conv_amt / rates.get(from_curr, 1.0)) * rates.get(to_curr, 1.0)
        st.markdown(f"""
        <div class="card-green" style="margin-top:25px;">
            <h3 style="margin:0;">Conversion Result:</h3>
            <span style="font-size:1.8rem; font-weight:700;">{conv_amt:,.2f} {from_curr} = {converted_val:,.2f} {to_curr}</span>
        </div>
        """, unsafe_allow_html=True)
