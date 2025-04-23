import streamlit as st
import pandas as pd
import subprocess
import os
import requests

# Server endpoint
SERVER_URL = "http://localhost:8000"

# Streamlit setup
st.set_page_config(page_title="PPML Client", layout="wide")
st.title("🛡️ PPML Client")

# Ensure directories
os.makedirs("./data", exist_ok=True)
os.makedirs("./model/params", exist_ok=True)

# Download params.pkl if not present
if not os.path.exists("./model/params/params.pkl"):
    with st.spinner("Downloading encryption parameters..."):
        resp = requests.get(f"{SERVER_URL}/params/")
        if resp.status_code == 200:
            with open("./model/params/params.pkl", "wb") as f:
                f.write(resp.content)
            st.success("params.pkl downloaded.")
        else:
            st.error(f"Failed to fetch params: {resp.status_code}")

# File uploader: CSV or encrypted .pkl
uploaded = st.file_uploader("Upload your data (CSV or encrypted .pkl):", type=["csv", "pkl"])
if uploaded:
    file_path = os.path.join("./data", uploaded.name)
    with open(file_path, "wb") as f:
        f.write(uploaded.getbuffer())
    st.success(f"Saved {uploaded.name}.")

    # Encrypt if CSV
    if uploaded.name.lower().endswith(".csv"):
        enc = subprocess.run(
            ["python", "./model/encrypt.py"],
            capture_output=True, text=True
        )
        if enc.returncode != 0:
            st.error("Encryption failed:")
            st.code(enc.stderr)
            st.stop()
        st.success("Data encrypted to encrypted_user_data.pkl.")
        in_path = "./data/encrypted_user_data.pkl"
    else:
        in_path = file_path
        st.success("Using provided encrypted data.")

    # Submit for inference
if st.button("🔄 Submit for Inference"):
    with st.spinner("Sending encrypted data and public context to server..."):
        # Open both files
        with open(in_path, "rb") as f_data, open("./model/params/context_public.ckks", "rb") as f_ctx:
            files = {
                "encrypted": ("encrypted_user_data.pkl", f_data, "application/octet-stream"),
                "context":   ("context_public.ckks",      f_ctx,  "application/octet-stream"),
            }
            resp = requests.post(f"{SERVER_URL}/predict/", files=files)
    if resp.status_code == 200:
        out_path = os.path.join("./data", "encrypted_predictions.pkl")
        with open(out_path, "wb") as f:
            f.write(resp.content)
        st.success("Encrypted predictions received.")
    else:
        st.error(f"Server error {resp.status_code}:")
        st.code(resp.text)

    # Decrypt predictions
    if os.path.exists("./data/encrypted_predictions.pkl"):
        if st.button("🔓 Decrypt Predictions"):
            dec = subprocess.run(
                ["python", "./model/decrypt.py"],
                capture_output=True, text=True
            )
            if dec.returncode != 0:
                st.error("Decryption failed:")
                st.code(dec.stderr)
            else:
                st.success("Decryption succeeded.")
                df = pd.read_csv("./model/predictions.csv")
                st.subheader("Predictions:")
                st.dataframe(df)
                st.download_button(
                    "Download predictions.csv", df.to_csv(index=False), "predictions.csv", "text/csv"
                )
