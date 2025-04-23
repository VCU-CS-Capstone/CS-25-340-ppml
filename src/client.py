import streamlit as st
import pandas as pd
import subprocess
import os
import requests
import time

# --- Configuration ---
SERVER_URL = "http://localhost:8000"

st.set_page_config(page_title="PPML Client Encryption & Prediction", layout="wide")
st.title("🛡️ PPML Client: Encrypt, Submit & Decrypt")

os.makedirs("./model/params", exist_ok=True)
os.makedirs("./data", exist_ok=True)

st.sidebar.markdown("""
Upload your health data, encrypt it locally, and send it to the server for encrypted inference.  

**Workflow:**  
1. Upload your CSV  
2. Download model params from server if not already available  
3. Click "Encrypt"  
4. Click "Submit" to send encrypted data  
5. Receive encrypted predictions  
6. Decrypt and analyze
""")

# Step 1: Upload CSV or Encrypted PKL
csv_file = st.file_uploader("Upload your CSV or PKL file", type=["csv", "pkl"])

if csv_file:
    if csv_file.name.endswith(".csv"):
        df = pd.read_csv(csv_file)
        st.subheader("📄 Data Preview")
        st.dataframe(df.head())
        df.to_csv("./data/user_data.csv", index=False)
        st.success("Saved to ./data/user_data.csv")

        if not os.path.exists("./model/params/params.pkl"):
            st.info("Downloading model parameters from server...")
            try:
                r = requests.get(SERVER_URL + "/params", timeout=5)
                if r.status_code == 200:
                    with open("./model/params/params.pkl", "wb") as f:
                        f.write(r.content)
                    st.success("Downloaded params.pkl")
                else:
                    st.error("Failed to download params.pkl.")
            except Exception as e:
                st.error(f"Download error: {e}")

        if os.path.exists("./model/params/params.pkl") and st.button("🔐 Encrypt CSV"):
            with st.spinner("Encrypting..."):
                enc_proc = subprocess.run(["python", "model/encrypt.py"], capture_output=True, text=True)
            if enc_proc.returncode != 0:
                st.error("Encryption failed:")
                st.code(enc_proc.stderr)
            else:
                st.success("Encrypted to encrypted_user_data.pkl")

    elif csv_file.name.endswith(".pkl"):
        out_path = "./data/encrypted_user_data.pkl"
        with open(out_path, "wb") as f:
            f.write(csv_file.getbuffer())
        st.success("Encrypted file saved as encrypted_user_data.pkl")

# Step 2: Submit to Server
if os.path.exists("./data/encrypted_user_data.pkl") and os.path.exists("./model/params/context_public.ckks"):
    if st.button("🔄 Submit for Inference"):
        with st.spinner("Sending encrypted data..."):
            with open("./data/encrypted_user_data.pkl", "rb") as f_data, \
                 open("./model/params/context_public.ckks", "rb") as f_ctx:
                files = {
                    "encrypted": ("encrypted_user_data.pkl", f_data, "application/octet-stream"),
                    "context":   ("context_public.ckks",      f_ctx,  "application/octet-stream"),
                }
                resp = requests.post(f"{SERVER_URL}/predict/", files=files)
        if resp.status_code == 200:
            with open("./data/encrypted_predictions.pkl", "wb") as f:
                f.write(resp.content)
            st.success("✅ Encrypted predictions received.")
        else:
            st.error(f"Server error {resp.status_code}:")
            st.code(resp.text)

# Step 3: Decrypt
if os.path.exists("./data/encrypted_predictions.pkl") and st.button("🧩 Decrypt Predictions"):
    with st.spinner("Decrypting..."):
        dec_proc = subprocess.run(["python", "model/decrypt.py"], capture_output=True, text=True)
    if dec_proc.returncode != 0:
        st.error("Decryption failed:")
        st.code(dec_proc.stderr)
    else:
        st.success("✅ Decryption complete!")
        preds = pd.read_csv("./model/predictions.csv")
        st.subheader("📊 Prediction Results")
        st.metric("Non-diabetic (0)", (preds["Prediction"] == 0).sum())
        st.metric("Diabetic (1)", (preds["Prediction"] == 1).sum())
        st.dataframe(preds)
        st.download_button("Download predictions.csv", preds.to_csv(index=False), "predictions.csv")

else:
    st.info("Upload CSV or .pkl to begin.")