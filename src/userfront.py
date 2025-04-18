import streamlit as st
import pandas as pd
import subprocess
import os

st.set_page_config(page_title="PPML Client Encryption", layout="wide")

st.title("🛡️ Client-Side Data Encryption")
st.markdown("""
Encrypt your health data using homomorphic encryption before sending it to the prediction server.

**Steps:**
1. Upload your CSV file
2. Ensure `param.pkl` is in `./model/params/`
3. Click to encrypt your data into `encrypted_user_data.pkl`
""")

# Sidebar
with st.sidebar:
    st.header("Encryption Requirements")
    st.markdown("""
    Before you can encrypt:
    - Download `params.pkl` from the model server
    - Place it in the `./model/params/` directory
    - The encryption context (`context.ckks`) will be generated automatically
    """)

os.makedirs("./data", exist_ok=True)
os.makedirs("./model/params", exist_ok=True)

uploaded_csv = st.file_uploader("Upload CSV file to encrypt:", type=["csv"])

if uploaded_csv is not None:
    df = pd.read_csv(uploaded_csv)
    st.subheader("📋 Data Preview")
    st.dataframe(df.head())
    df.to_csv("./data/user_data.csv", index=False)
    st.success("CSV saved to ./data/user_data.csv")

    # Check if norm_param.json exists
    norm_exists = os.path.exists("./model/params/params.pkl")

    if not norm_exists:
        st.error("Missing required file: params.pkl")
    else:
        if st.button("🔐 Encrypt Data"):
            with st.spinner("Encrypting your data..."):
                result = subprocess.run(["python", "./model/encrypt.py"], capture_output=True, text=True)
                if result.returncode != 0:
                    st.error("Encryption failed:")
                    st.code(result.stderr)
                else:
                    st.success("✅ Data encrypted successfully!")
                    st.markdown("Download your encrypted file to submit to the prediction server:")
                    with open("./data/encrypted_user_data.pkl", "rb") as f:
                        st.download_button("Download encrypted_user_data.pkl", data=f, file_name="encrypted_user_data.pkl")
else:
    st.info("Awaiting CSV file to begin encryption.")