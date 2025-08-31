import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.linear_model import LinearRegression
import io


df = pd.read_csv("powerbi_feed.csv")
df["Month"] = pd.to_datetime(df["Month"])

st.set_page_config(page_title="Manufacturing Dashboard", layout="wide")

st.title("📊 Manufacturing Sales Dashboard")


st.sidebar.header("Filters")
start_date = st.sidebar.date_input("Start Date", df["Month"].min())
end_date = st.sidebar.date_input("End Date", df["Month"].max())
forecast_months = st.sidebar.slider("Forecast Months", min_value=1, max_value=12, value=6)


forecast_target = st.sidebar.selectbox(
    "Choose Metric to Forecast",
    ["Total Sales", "Product_A_Sales", "Product_B_Sales"]
)


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



st.subheader(f"🔮 {forecast_target} Forecast with Confidence Intervals")

df_forecast = df.copy()
df_forecast["MonthIndex"] = np.arange(len(df_forecast))  

X = df_forecast[["MonthIndex"]]
y = df_forecast[forecast_target]

model = LinearRegression()
model.fit(X, y)


future_idx = np.arange(len(df_forecast), len(df_forecast) + forecast_months)
future_dates = pd.date_range(df_forecast["Month"].max() + pd.offsets.MonthBegin(), periods=forecast_months, freq="MS")
future_preds = model.predict(future_idx.reshape(-1, 1))

forecast_df = pd.DataFrame({"Month": future_dates, "Forecast": future_preds})


y_pred_train = model.predict(X)
residuals = y - y_pred_train
std_error = residuals.std()


forecast_df["Lower"] = forecast_df["Forecast"] - 1.96 * std_error
forecast_df["Upper"] = forecast_df["Forecast"] + 1.96 * std_error


plot_df = pd.concat(
    [
        df_forecast[["Month", forecast_target]].rename(columns={forecast_target: "Actual"}),
        forecast_df.rename(columns={"Forecast": "Forecast"})
    ],
    ignore_index=True
)


fig_forecast = go.Figure()


fig_forecast.add_trace(go.Scatter(
    x=df_forecast["Month"], y=df_forecast[forecast_target],
    mode="lines+markers", name="Actual"
))


fig_forecast.add_trace(go.Scatter(
    x=forecast_df["Month"], y=forecast_df["Forecast"],
    mode="lines+markers", name="Forecast", line=dict(color="blue")
))

fig_forecast.add_trace(go.Scatter(
    x=pd.concat([forecast_df["Month"], forecast_df["Month"][::-1]]),
    y=pd.concat([forecast_df["Upper"], forecast_df["Lower"][::-1]]),
    fill="toself", fillcolor="rgba(0, 0, 255, 0.1)", line=dict(color="rgba(255,255,255,0)"),
    hoverinfo="skip", showlegend=True, name="95% Confidence Interval"
))

fig_forecast.update_layout(title=f"{forecast_target} Forecast ({forecast_months} months ahead)",
                           xaxis_title="Month", yaxis_title=forecast_target)

st.plotly_chart(fig_forecast, use_container_width=True)


st.subheader("📥 Export Data")

export_df = pd.merge(
    filtered_df[["Month", forecast_target]],
    forecast_df,
    on="Month",
    how="outer"
).sort_values("Month")


csv_buffer = io.StringIO()
export_df.to_csv(csv_buffer, index=False)
st.download_button(
    label="Download CSV",
    data=csv_buffer.getvalue(),
    file_name=f"{forecast_target}_forecast.csv",
    mime="text/csv"
)


excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
    export_df.to_excel(writer, index=False, sheet_name="Forecast")
st.download_button(
    label="Download Excel",
    data=excel_buffer.getvalue(),
    file_name=f"{forecast_target}_forecast.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
