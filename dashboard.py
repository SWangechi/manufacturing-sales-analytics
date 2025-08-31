import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv("powerbi_feed.csv")
df["Month"] = pd.to_datetime(df["Month"])

st.set_page_config(page_title="Manufacturing Dashboard", layout="wide")

st.title("📊 Manufacturing Sales Dashboard")

st.sidebar.header("Filters")
start_date = st.sidebar.date_input("Start Date", df["Month"].min())
end_date = st.sidebar.date_input("End Date", df["Month"].max())

filtered_df = df[(df["Month"] >= pd.to_datetime(start_date)) & (df["Month"] <= pd.to_datetime(end_date))]


col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"{filtered_df['Total Sales'].sum():,.0f}")
col2.metric("Product A Sales", f"{filtered_df['Product_A_Sales'].sum():,.0f}")
col3.metric("Product B Sales", f"{filtered_df['Product_B_Sales'].sum():,.0f}")


fig_line = px.line(filtered_df, x="Month", y=["Product_A_Sales", "Product_B_Sales", "Total Sales"],
                   title="Sales Trend Over Time")
st.plotly_chart(fig_line, use_container_width=True)


fig_bar = px.bar(filtered_df.melt(id_vars="Month", value_vars=["Product_A_Sales", "Product_B_Sales"]),
                 x="variable", y="value", color="variable", barmode="group",
                 title="Product Comparison")
st.plotly_chart(fig_bar, use_container_width=True)