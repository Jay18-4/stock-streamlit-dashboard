import streamlit as st # type: ignore
import pandas as pd
from utils.api_client import read_csv, read_json, daily_cloud_cache


st.set_page_config(page_title="Model Path", layout="wide")

st.title("📈 Model Path Dashboard")

# ---- Fetch data with daily caching ----
latest_data = daily_cloud_cache(
    "latest_data",
    lambda: read_json("latest_data_snapshot.json")
)
predictions = daily_cloud_cache(
    "predictions",
    lambda: read_json("prediction_history.csv")
)

# ---- Convert stocks to DataFrame ----
stocks_df = pd.DataFrame(latest_data["stocks"])
pred_df = pd.DataFrame({
    "Ticker": predictions["ticker"],
    "Prediction": predictions["prediction"]
})

# ---- Merge stock + prediction ----
merged_df = stocks_df.merge(pred_df, on="Ticker", how="left")

st.subheader("Latest Stock Snapshot + Predictions")
st.dataframe(merged_df)

st.subheader("Predictions") 
for ticker,pred in zip(merged_df['Ticker'], merged_df['Prediction']):
    st.metric(f"{ticker} Direction", "Up" if pred == 1 else "Down")   

            
# ---- Optional: Plot Close prices ----
st.subheader("Stock Close Prices")
st.line_chart(stocks_df.set_index("Ticker")["Close"])


