import streamlit as st # type: ignore
import pandas as pd
from utils.api_client import read_json, daily_cache

st.set_page_config(page_title="Sentiment Path", layout="wide")

st.title("📰 News & Sentiment Dashboard")

news_data = daily_cache("news_sentiment", read_json("news_sent.json"))

# Convert to DataFrame for display
news_df = pd.DataFrame(news_data["news_sent"])

st.subheader("Latest News Sentiment")
st.dataframe(news_df)

# Optional summary KPIs
st.subheader("Sentiment Summary")
st.metric("Polarity Mean", news_df["pol_mean"].sum())
st.metric("Polarity Sum", news_df["pol_sum"].sum())
st.metric("Positive Count", news_df["pos_count"].sum())
st.metric("Negative Count", news_df["neg_count"].sum())
st.metric("Neu Sentiment", news_df["neu_count"].sum())

