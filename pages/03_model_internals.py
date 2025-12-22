# import streamlit as st # type: ignore
# import pandas as pd
# from utils.api_client import daily_cache, get_latest_data_features, get_prediction_history

# st.sidebar.title("Controls")

# ticker = st.sidebar.selectbox(
#     "Select Ticker",
#     ["AAPL", "MSFT", "TSLA", 'NVDA']
# )

# tab_overview, tab_prediction, tab_history = st.tabs(
#     ["Overview", "Prediction", "History"]
# )

# # with tab_overview:
# #     # latest price, indicators for ticker

# # with tab_prediction:
# #     # up/down prediction for ticker

# # with tab_history:
# #     # prediction history for ticker
    
# st.set_page_config(
#     page_title="Model Internals",
#     layout="wide"
# )

# st.title("🧠 Model Internals")

# st.caption(
#     "Inspect model versions, engineered features, and prediction history over time."
# )

# # =========================
# # SECTION 1: MODEL METADATA
# # =========================
# st.subheader("Model Metadata")

# latest_data = daily_cache("latest_data_features", get_latest_data_features)
# history = daily_cache("prediction_history", get_prediction_history)


# col1, col2 = st.columns(2)

# with col1:
#     st.metric("Model Version", history.get("model_version", "N/A"))

# with col2:
#     st.metric("Last Updated", latest_data.get("timestamp", "N/A"))

# st.divider()

# # =========================
# # SECTION 2: ENGINEERED FEATURES
# # =========================
# st.subheader("Engineered Features Snapshot")

# # If your endpoint already returns engineered features
# if "stocks" in latest_data:
#     features_df = pd.DataFrame(latest_data["stocks"])
#     st.dataframe(features_df, use_container_width=True)
# else:
#     st.info("No engineered feature snapshot available.")

# st.divider()

# # =========================
# # SECTION 3: PREDICTION HISTORY
# # =========================
# st.subheader("Prediction History")

# try:
#     history = daily_cache("prediction_history", get_prediction_history)

#     history_df = pd.DataFrame(history)
#     history_df = history_df.drop('model_version',axis=1)

#     if not history_df.empty:
#         st.dataframe(history_df, use_container_width=True)

#         # Optional: directional trend visualization
#         if "prediction" in history_df.columns:
#             st.subheader("Directional Trend Over Time")
#             history_df["prediction_numeric"] = history_df["prediction"].map(
#                 {"Up": 1, "Down": 0}
#             )
#             st.line_chart(history_df.set_index("timestamp")["prediction_numeric"])
#     else:
#         st.info("Prediction history is empty.")

# except Exception:
#     st.warning("Prediction history endpoint not available yet.")

# st.divider()

# # =========================
# # SECTION 4: RETRAINING NOTES
# # =========================
# st.subheader("Retraining & Stability")

# st.markdown(
#     """
# - Model retrains **weekly**
# - Predictions are cached **once per day**
# - Sentiment features are recalculated daily
# - This page helps detect drift and instability
# """
# )

import streamlit as st  # type: ignore
import pandas as pd
from utils.api_client import daily_cache, get_latest_data_features, get_prediction_history

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
latest_data = daily_cache("latest_data_features", get_latest_data_features)
history_data = daily_cache("prediction_history", get_prediction_history)

# =========================
# TAB 1: OVERVIEW
# =========================
with tab_overview:
    st.subheader("Model Metadata")
    st.metric("Model Version", history_data.get("model_version", "N/A"))
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
        history_df = pd.DataFrame(history_data)
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
