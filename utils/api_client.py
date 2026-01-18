import requests
import streamlit as st # type: ignore
from datetime import datetime
import io
import pandas as pd
import boto3
import json
import botocore

# ---- Cache wrapper ----
def daily_cloud_cache(key: str, fetch_fn):
    """
    Cache cloud-fetched data once per day in Streamlit session_state
    """
    today = date.today()

    cached = st.session_state.get(key)
    cached_date = st.session_state.get(f"{key}__date")

    # Return cached if already fetched today
    if cached is not None and cached_date == today:
        return cached

    # Fetch fresh from cloud
    data = fetch_fn()

    # Store in session
    st.session_state[key] = data
    st.session_state[f"{key}__date"] = today

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

resp = s3.list_objects_v2(Bucket=R2_BUCKET_NAME)
print(resp.get("Contents", []))

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







