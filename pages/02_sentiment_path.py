import streamlit as st # type: ignore
import pandas as pd
from utils.api_client import get_news_sentiment, daily_cache

st.set_page_config(page_title="Sentiment Path", layout="wide")

st.title("📰 News & Sentiment Dashboard")

news_data = daily_cache("news_sentiment", get_news_sentiment)

# Convert to DataFrame for display
news_df = pd.DataFrame(news_data["news"])

st.subheader("Latest News Sentiment")
st.dataframe(news_df)

# Optional summary KPIs
st.subheader("Sentiment Summary")
st.metric("Positive Count", news_df["pos_count"].sum())
st.metric("Negative Count", news_df["neg_count"].sum())
st.metric("Neu Sentiment", news_df["neu_count"].sum())
