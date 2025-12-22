import streamlit as st # type: ignore
import pandas as pd
from utils.api_client import get_latest_data, get_predictions, daily_cache


st.set_page_config(page_title="Model Path", layout="wide")

st.title("📈 Model Path Dashboard")

# ---- Fetch data with daily caching ----
latest_data = daily_cache("latest_data", get_latest_data)
predictions = daily_cache("predictions", get_predictions)

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
