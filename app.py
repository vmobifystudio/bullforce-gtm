import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title="Bullforce GTM Scenario Planner", layout="wide")
st.title("📊 Bullforce GTM Scenario Planner")
st.markdown("""
This tool allows stakeholders to simulate user acquisition, retention, revenue, and marketing efficiency over a 24-month horizon based on adjustable assumptions.
""")

uploaded_file = st.sidebar.file_uploader("📁 Upload your Bullforce Excel file", type="xlsx")

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    growth_df = xls.parse("Growth Overview")

    # Extract direct Excel data for baseline
    months = [f"Month {i+1}" for i in range(len(growth_df))]
    paid_installs = growth_df["Android Installs"] + growth_df["iOS Installs"]
    verified_users = growth_df["Total Verified Customers"]
    total_spend = growth_df["Total Spend"].sum()

    st.sidebar.header("💰 Revenue Inputs")
    st.sidebar.markdown("Input your month-wise ARPU (₹299 default)")
    arpu_values = [st.sidebar.number_input(f"Month {i+1} ARPU (₹)", min_value=0, max_value=1000, value=299, key=f"arpu_{i}") for i in range(len(growth_df))]

    # Calculate retained users using funnel assumptions
    st.sidebar.header("🔁 Retention Assumptions")
    churn_start = st.sidebar.slider("Start Churn %", 0, 100, 25)
    churn_end = st.sidebar.slider("End Churn %", 0, 100, 10)
    churn_curve = np.linspace(churn_start/100, churn_end/100, len(growth_df))
    verified_to_active = st.sidebar.slider("Verified → Active User %", 10, 100, 90)

    retained_users = []
    revenue_by_month = []
    for i in range(len(growth_df)):
        retained = verified_users[i] * (verified_to_active / 100) * (1 - churn_curve[i])
        retained_users.append(retained)
        revenue_by_month.append(retained * arpu_values[i])

    total_verified = verified_users.sum()
    total_revenue = sum(revenue_by_month)
    blended_cac = total_spend / total_verified if total_verified else 0
    roi = (total_revenue - total_spend) / total_spend * 100

    df = pd.DataFrame({
        "Month": months,
        "Paid Installs": paid_installs,
        "Verified Users": verified_users,
        "Retained Users": retained_users,
        "Revenue (₹)": revenue_by_month
    })

    st.subheader("📈 User Growth, Retention & Revenue")
    fig = px.line(df, x="Month", y=["Paid Installs", "Verified Users", "Retained Users", "Revenue (₹)"], markers=True)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Verified Users", f"{int(total_verified):,}")
    col2.metric("Total Spend (₹)", f"{int(total_spend):,}")
    col3.metric("Total Revenue (₹)", f"{int(total_revenue):,}")
    col4.metric("ROI (%)", f"{roi:.1f}%")

    st.subheader("📄 Month-wise Data")
    st.dataframe(df, use_container_width=True)

else:
    st.warning("Please upload the Bullforce Excel file with the expected structure to begin.")
