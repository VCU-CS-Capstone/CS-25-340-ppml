import streamlit as st
import pandas as pd
import subprocess
import os
import requests

# --- Configuration ---
SERVER_URL = "http://localhost:8000"

BASE_DIR            = os.path.dirname(__file__)
USER_DATA_PATH      = os.path.join(BASE_DIR, "data/user_data.csv")
ENCRYPTED_DATA_PATH = os.path.join(BASE_DIR, "data/encrypted_user_data.pkl")
ENCRYPTED_PRED_PATH = os.path.join(BASE_DIR, "encrypted_predictions.pkl")
CONTEXT_PATH        = os.path.join(BASE_DIR, "params/context_public.ckks")
KEY_PATH            = os.path.join(BASE_DIR, "params/context_private.ckks")
PARAMS_PATH         = os.path.join(BASE_DIR, "params/params.pkl")
PRED_CSV_PATH       = os.path.join(BASE_DIR, "data/predictions.csv")

st.set_page_config(page_title="PPML Client Encryption & Prediction", layout="wide")
st.title("🛡️ PPML Client: Encrypt, Submit & Decrypt")

st.sidebar.markdown("""
### 🔐 Workflow:
1. Upload raw CSV or encrypted .pkl  
2. Download model parameters if needed  
3. Encrypt data (if CSV)  
4. Submit for encrypted inference  
5. Decrypt predictions  
""")

# Step 1: Upload
uploaded_file = st.file_uploader("Upload your CSV or Encrypted PKL", type=["csv", "pkl"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        st.subheader("📄 Data Preview")
        st.dataframe(df.head())
        df.to_csv(USER_DATA_PATH, index=False)
        st.success(f"Saved to {USER_DATA_PATH}")

        # Download params if not present
        if not os.path.exists(PARAMS_PATH):
            st.info("Downloading model parameters from server...")
            try:
                r = requests.get(SERVER_URL + "/params", timeout=5)
                if r.status_code == 200:
                    with open(PARAMS_PATH, "wb") as f:
                        f.write(r.content)
                    st.success("Downloaded params.pkl")
                else:
                    st.error("Failed to download params.pkl.")
            except Exception as e:
                st.error(f"Download error: {e}")

        if os.path.exists(PARAMS_PATH) and st.button("🔐 Encrypt CSV"):
            with st.spinner("Encrypting..."):
                enc_proc = subprocess.run(["python", "client/encrypt.py"], capture_output=True, text=True)
            if enc_proc.returncode != 0:
                st.error("Encryption failed:")
                st.code(enc_proc.stderr)
            else:
                st.success("Encrypted to encrypted_user_data.pkl")

    elif uploaded_file.name.endswith(".pkl"):
        with open(ENCRYPTED_DATA_PATH, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("Encrypted PKL saved.")

# Step 2: Submit to Server
if os.path.exists(ENCRYPTED_DATA_PATH) and os.path.exists(CONTEXT_PATH):
    if st.button("🔄 Submit for Inference"):
        with st.spinner("Sending encrypted data to server..."):
            with open(ENCRYPTED_DATA_PATH, "rb") as f_data, open(CONTEXT_PATH, "rb") as f_ctx:
                files = {
                    "encrypted": ("encrypted_user_data.pkl", f_data, "application/octet-stream"),
                    "context": ("context_public.ckks", f_ctx, "application/octet-stream")
                }
                resp = requests.post(SERVER_URL + "/predict/", files=files)

        if resp.status_code == 200:
            with open(ENCRYPTED_PRED_PATH, "wb") as f:
                f.write(resp.content)
            st.success("✅ Encrypted predictions received.")
        else:
            st.error(f"Server error {resp.status_code}:")
            st.code(resp.text)

# Step 3: Decrypt
if os.path.exists(ENCRYPTED_PRED_PATH) and st.button("🧩 Decrypt Predictions"):
    with st.spinner("Decrypting..."):
        dec_proc = subprocess.run(["python", "client/decrypt.py"], capture_output=True, text=True)
    if dec_proc.returncode != 0:
        st.error("Decryption failed:")
        st.code(dec_proc.stderr)
    else:
        st.success("✅ Decryption complete!")
        preds = pd.read_csv(PRED_CSV_PATH)
        st.subheader("📊 Prediction Results")
        st.metric("Non-diabetic (0)", (preds["Prediction"] == 0).sum())
        st.metric("Diabetic (1)", (preds["Prediction"] == 1).sum())
        st.dataframe(preds)
        st.download_button("Download predictions.csv", preds.to_csv(index=False), "predictions.csv")

else:
    st.info("Awaiting file upload to begin.")
