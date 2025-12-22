import requests
import streamlit as st # type: ignore
from datetime import datetime
import os
import io
import pandas as pd
import boto3
import json

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

# Environment variables
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY")
R2_SECRET_KEY = os.getenv("R2_SECRET_KEY")
R2_ENDPOINT = os.getenv("R2_ENDPOINT")  # e.g., https://<account>.r2.cloudflarestorage.com

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

# def write_csv(df: pd.DataFrame, file_name: str):
#     """Upload DataFrame to R2 as CSV."""
#     csv_buffer = io.StringIO()
#     df.to_csv(csv_buffer, index=False)
#     s3.put_object(Bucket=R2_BUCKET_NAME, Key=f"data/{file_name}", Body=csv_buffer.getvalue())
#     print(f"[INFO] File {file_name} uploaded to R2 bucket {R2_BUCKET_NAME}.")


def read_json(file_name: str):
    """Download a JSON file from R2 and return as Python object."""
    try:
        obj = s3.get_object(Bucket=R2_BUCKET_NAME, Key=f"data/{file_name}")
        return json.loads(obj['Body'].read().decode('utf-8'))
    except s3.exceptions.NoSuchKey:
        print(f"[WARN] File {file_name} not found in bucket. Returning empty dict.")
        return {}

# def write_json(data, file_name: str):
#     """Upload a Python object as JSON to R2."""
#     json_buffer = io.StringIO()
#     json.dump(data, json_buffer)
#     s3.put_object(Bucket=R2_BUCKET_NAME, Key=f"data/{file_name}", Body=json_buffer.getvalue())
#     print(f"[INFO] File {file_name} uploaded to R2 bucket {R2_BUCKET_NAME}.")


# def download_file(key: str, local_path: str):
#     """
#     Download any file (model, binary, etc.) from R2 to local disk
#     """
#     if os.path.exists(local_path):
#         print(f"[INFO] {local_path} already exists. Skipping download.")
#         return

#     os.makedirs(os.path.dirname(local_path), exist_ok=True)

#     with open(local_path, "wb") as f:
#         s3.download_fileobj(R2_BUCKET_NAME, key, f)

#     print(f"[INFO] Downloaded {key} -> {local_path}")


# def upload_file(local_path: str, key: str):
#     """
#     Upload any file (model, binary, etc.) to R2
#     """
#     with open(local_path, "rb") as f:
#         s3.upload_fileobj(f, R2_BUCKET_NAME, key)

#     print(f"[INFO] Uploaded {local_path} -> {key}")
