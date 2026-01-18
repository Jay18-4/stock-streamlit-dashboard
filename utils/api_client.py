import requests
import streamlit as st # type: ignore
from datetime import datetime
import io
import pandas as pd
import boto3
import json
import botocore

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

# Environment variables
R2_BUCKET_NAME = st.secrets["R2_BUCKET_NAME"]
R2_ACCESS_KEY = st.secrets["R2_ACCESS_KEY"]
R2_SECRET_KEY = st.secrets["R2_SECRET_KEY"]
R2_ENDPOINT = st.secrets["R2_ENDPOINT"]

# Initialize the client
s3 = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY
)

def read_csv(file_name: str) -> pd.DataFrame:
    """Download CSV from R2 and return as DataFrame."""
    try:
        obj = s3.get_object(Bucket=R2_BUCKET_NAME, Key=f"data/{file_name}")
        return pd.read_csv(io.StringIO(obj['Body'].read().decode('utf-8')))
    except s3.exceptions.NoSuchKey:
        print(f"[WARN] File {file_name} not found in bucket. Returning empty DataFrame.")
        return pd.DataFrame()



def read_json(file_name: str):
    """Download a JSON file from R2 and return as Python object."""
    try:
        obj = s3.get_object(Bucket=R2_BUCKET_NAME, Key=f"data/{file_name}")
        return json.loads(obj['Body'].read().decode('utf-8'))
    # except s3.exceptions.NoSuchKey:
    #     print(f"[WARN] File {file_name} not found in bucket. Returning empty dict.")
    #     return {}
    except botocore.exceptions.ClientError as e:
        print("S3 ERROR:", e.response["Error"])
        raise




