import streamlit as st  # type: ignore
import pandas as pd
from utils.api_client import daily_cloud_cache, read_json, read_csv

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Model Internals",
    layout="wide"
)

st.title("🧠 Model Internals")
st.caption("Inspect model versions, engineered features, and prediction history over time.")

# =========================
# SIDEBAR TICKER SELECTION
# =========================
st.sidebar.title("Controls")
ticker_list = ["All","AAPL", "MSFT", "TSLA", "NVDA"]
selected_ticker = st.sidebar.selectbox(
    "Select Ticker",
    ticker_list
)

# =========================
# TABS
# =========================
tab_overview, tab_features, tab_history = st.tabs(
    ["Overview", "Features", "History"]
)

# =========================
# FETCH DATA (CACHED)
# =========================
latest_data = daily_cloud_cache(
    "latest_data_features",
    lambda: read_json("latest_data_feat.json")
)
history_data = daily_cloud_cache(
    "prediction_history",
    lambda: read_csv("prediction_history.csv")
)

# =========================
# TAB 1: OVERVIEW
# =========================
with tab_overview:
    st.subheader("Model Metadata")
    st.metric("Model Version", history_data["model_version"].iloc[-1])
    st.metric("Last Updated", latest_data.get("timestamp", "N/A"))


# =========================
# TAB 2: ENGINEERED FEATURES
# =========================
with tab_features:
    st.subheader(f"Engineered Features: {selected_ticker}")
    stocks_data = latest_data.get("stocks", [])
    
    if selected_ticker == "All":
        features_df = pd.DataFrame(stocks_data)
        st.dataframe(features_df, width='stretch')
    else:
        ticker_data = next(
            (item for item in latest_data.get("stocks", []) if item["Ticker"] == selected_ticker),
            None
        )
        if ticker_data:
            features_df = pd.DataFrame([ticker_data])
            st.dataframe(features_df, width='stretch')
        else:
            st.info(f"No engineered features available for {selected_ticker}.")

# =========================
# TAB 3: PREDICTION HISTORY
# =========================
with tab_history:
    st.subheader("Prediction History")
    try:
        history_df = history_data.copy()
        history_df = history_df.drop(columns=["model_version"])
        if not history_df.empty:
            if selected_ticker != "All":
                history_df = history_df[history_df["tickers"] == selected_ticker]
                history_df = history_df.drop(columns=["tickers"])
            
                
            history_df['direction'] = ['Up' if i == 1 else 'Down' for i in history_df['prediction']]
                
            st.dataframe(history_df, width='stretch')
            st.divider()
            # Optional: directional trend visualization
            history_df["prediction_numeric"] = history_df["prediction"].map({1: 1, 0: 0})
            st.line_chart(history_df.set_index("timestamp")["prediction_numeric"])
        else:
            st.info("Prediction history is empty.")
    except Exception as e:
        print(f'Error {str(e)}')
        st.warning("Prediction history endpoint not available yet.")

# =========================
# RETRAINING NOTES
# =========================
st.divider()
st.subheader("Retraining & Stability")
st.markdown(
    """
- Model retrains **weekly**
- Predictions are cached **once per day**
- Sentiment features are recalculated daily
- This page helps detect drift and instability
"""
)




