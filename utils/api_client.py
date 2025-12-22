import requests
import streamlit as st # type: ignore
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# ---- Cache wrapper ----
def daily_cache(key, fetch_fn):
    cached = st.session_state.get(key, None)
    last_fetch = st.session_state.get(f"{key}_time", None)
    today = datetime.today().date()

    if cached and last_fetch == today:
        return cached

    data = fetch_fn()
    st.session_state[key] = data
    st.session_state[f"{key}_time"] = today
    return data

# ---- API calls ----
def get_latest_data():
    res = requests.get(f"{BASE_URL}/latest-data-snapshot")
    res.raise_for_status()
    return res.json()

def get_latest_data_features():
    res = requests.get(f"{BASE_URL}/latest-data-feat")
    res.raise_for_status()
    return res.json()

def get_predictions():
    res = requests.get(f"{BASE_URL}/predict")
    res.raise_for_status()
    return res.json()

def get_news_sentiment():
    res = requests.get(f"{BASE_URL}/news-sentiment")
    res.raise_for_status()
    return res.json()

def get_prediction_history():
    res = requests.get(f"{BASE_URL}/history?ticker=None")
    res.raise_for_status()
    return res.json()
