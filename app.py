
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Bullforce GTM Scenario Planner", layout="wide")

st.title("📊 Bullforce GTM Scenario Planner")
st.markdown("""
This tool allows stakeholders to simulate user acquisition, retention, and marketing efficiency over a 24-month horizon based on adjustable assumptions.
""")

# Upload section
uploaded_file = st.sidebar.file_uploader("📁 Upload your Bullforce Excel file (with updated assumptions & retention)", type="xlsx")

def load_excel_data(file):
    xls = pd.ExcelFile(file)
    growth = xls.parse("Growth Overview")
    retention = xls.parse("Retention & Churn Model")
    return growth, retention

if uploaded_file:
    growth_df, retention_df = load_excel_data(uploaded_file)

    st.sidebar.header("🎯 Acquisition Inputs")
    cpi_android = st.sidebar.slider("Android CPI (₹)", 5, 100, 8)
    cpi_ios = st.sidebar.slider("iOS CPI (₹)", 10, 150, 25)
    install_to_signup = st.sidebar.slider("Install → Signup %", 10, 100, 30)
    signup_to_verified = st.sidebar.slider("Signup → Verified %", 10, 100, 40)
    verified_to_active = st.sidebar.slider("Verified → Active User %", 10, 100, 90)

    st.sidebar.header("🔁 Retention Inputs")
    churn_start = st.sidebar.slider("Start Churn %", 0, 100, 25)
    churn_end = st.sidebar.slider("End Churn %", 0, 100, 5)

    st.sidebar.header("📈 Growth & Mix")
    monthly_growth = st.sidebar.slider("Monthly Growth %", 0, 50, 10)
    referral_multiplier = st.sidebar.slider("Referral Multiplier", 1.0, 2.0, 1.1)
    organic_start = st.sidebar.slider("Initial Organic/Referral Share %", 0, 50, 5)
    organic_end = st.sidebar.slider("Final Organic/Referral Share %", 0, 50, 20)
    android_share = st.sidebar.slider("Android Share %", 0, 100, 70)
    ios_share = 100 - android_share

    st.sidebar.header("📦 Targets")
    duration = 24
    target_verified = 200000

    base_verified = growth_df["Total Verified Customers"].values[:duration]
    months = [f"Month {i+1}" for i in range(duration)]
    churn_curve = np.linspace(churn_start/100, churn_end/100, duration)
    organic_curve = np.linspace(organic_start/100, organic_end/100, duration)

    # Generate acquisition model
    paid_installs = []
    verified_users = []
    retained_users = []

    for i in range(duration):
        base = base_verified[i] if i < len(base_verified) else base_verified[-1] * (1 + monthly_growth/100) ** (i - len(base_verified) + 1)
        installs = base / ((install_to_signup/100) * (signup_to_verified/100))
        organic = installs * organic_curve[i]
        total_installs = installs + organic
        verified = total_installs * (install_to_signup/100) * (signup_to_verified/100)
        retained = verified * (verified_to_active/100) * (1 - churn_curve[i])

        paid_installs.append(total_installs)
        verified_users.append(verified)
        retained_users.append(retained)

    total_paid = np.sum(paid_installs)
    total_spend = total_paid * ((android_share/100) * cpi_android + (ios_share/100) * cpi_ios)
    blended_cac = total_spend / np.sum(verified_users)

    st.subheader("📈 User Growth & Retention")
    df = pd.DataFrame({
        "Month": months,
        "Paid Installs": paid_installs,
        "Verified Users": verified_users,
        "Retained Users": retained_users
    })
    st.line_chart(df.set_index("Month"))

    st.subheader("📊 Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Verified Users", f"{int(np.sum(verified_users)):,}")
    col2.metric("Total Spend (₹)", f"{int(total_spend):,}")
    col3.metric("Blended CAC (₹)", f"{int(blended_cac):,}")

    st.subheader("📄 Month-wise Data")
    st.dataframe(df, use_container_width=True)

else:
    st.warning("Please upload the Bullforce Excel file with the expected structure to begin.")
