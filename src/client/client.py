import streamlit as st
import pandas as pd
import subprocess
import os
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
# --- Configuration ---
SERVER_URL = "http://localhost:8000"

BASE_DIR            = os.path.dirname(__file__)
USER_DATA_PATH      = os.path.join(BASE_DIR, "./data/user_data.csv")
ENCRYPTED_DATA_PATH = os.path.join(BASE_DIR, "./data/encrypted_user_data.pkl")
ENCRYPTED_PRED_PATH = os.path.join(BASE_DIR, "encrypted_predictions.pkl")
CONTEXT_PATH        = os.path.join(BASE_DIR, "./params/context_public.ckks")
KEY_PATH            = os.path.join(BASE_DIR, "./params/context_private.ckks")
CLIENT_PARAM        = os.path.join(BASE_DIR, "./params/params.pkl")
PARAMS_PATH         = os.path.join(BASE_DIR, "../server/output/params.pkl")
PRED_CSV_PATH       = os.path.join(BASE_DIR, "./data/predictions.csv")

# Ensure folders exist
os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "params"), exist_ok=True)

st.set_page_config(page_title="PPML Client Encryption & Prediction", layout="wide")
st.title("🛡️ PPML Client: Encrypt, Submit & Decrypt")

st.sidebar.markdown("""
### 🔐 Workflow:
1. Upload raw CSV or encrypted `.pkl`  
2. Upload `params.pkl` (downloaded from server)  
3. Encrypt data (if CSV)  
4. Submit for encrypted inference  
5. Decrypt predictions  
""")

st.sidebar.markdown("### 📥 Download Model Parameters")

if os.path.exists(PARAMS_PATH):
    with open(PARAMS_PATH, "rb") as f:
        st.sidebar.download_button("Download params.pkl", f.read(), "params.pkl")
else:
    if st.sidebar.button("Fetch params.pkl from server"):
        try:
            r = requests.get(SERVER_URL + "/params", timeout=5)
            if r.status_code == 200:
                with open(PARAMS_PATH, "wb") as f:
                    f.write(r.content)
                st.sidebar.success("params.pkl downloaded.")
            else:
                st.sidebar.error(f"Server error: {r.status_code}")
        except Exception as e:
            st.sidebar.error(f"Download error: {e}")


# Step 1: Upload CSV or Encrypted PKL
uploaded_file = st.file_uploader("Upload your CSV or Encrypted PKL", type=["csv", "pkl"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        st.subheader("📄 Data Preview")
        st.dataframe(df.head())
        df.to_csv(USER_DATA_PATH, index=False)
        st.success(f"Saved to {USER_DATA_PATH}")

        # Step 2: Upload model parameters
        if not os.path.exists(CLIENT_PARAM):
            st.warning("`params.pkl` not found. Upload it below (downloaded from server).")
            uploaded_params = st.file_uploader("Upload `params.pkl` from server", type=["pkl"], key="params_upload")
            if uploaded_params:
                with open(CLIENT_PARAM, "wb") as f:
                    f.write(uploaded_params.read())
                st.success("✅ `params.pkl` uploaded and saved.")

        # Step 3: Encrypt the CSV
        if os.path.exists(CLIENT_PARAM) and st.button("🔐 Encrypt CSV"):
            with st.spinner("Encrypting..."):
                enc_proc = subprocess.run(["python", "encrypt.py"], capture_output=True, text=True)
            if enc_proc.returncode != 0:
                st.error("Encryption failed:")
                st.code(enc_proc.stderr)
            else:
                st.success("Encrypted to `encrypted_user_data.pkl`")

    elif uploaded_file.name.endswith(".pkl"):
        with open(ENCRYPTED_DATA_PATH, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("Encrypted PKL saved to `encrypted_user_data.pkl`")

# Step 4: Submit to Server
if os.path.exists(ENCRYPTED_DATA_PATH) and os.path.exists(CONTEXT_PATH):
    if st.button("🔄 Submit for Inference"):
        with st.spinner("Sending encrypted data..."):
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

# Step 5: Decrypt
if os.path.exists(ENCRYPTED_PRED_PATH) and st.button("🧩 Decrypt Predictions"):
    with st.spinner("Decrypting..."):
        dec_proc = subprocess.run(["python", "decrypt.py"], capture_output=True, text=True)
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
        st.download_button("Download `predictions.csv`", preds.to_csv(index=False), "predictions.csv")

if os.path.exists(PRED_CSV_PATH) and os.path.exists(USER_DATA_PATH):
    predictions_df = pd.read_csv(PRED_CSV_PATH)
    user_df = pd.read_csv(USER_DATA_PATH)
    if "Outcome" in user_df.columns:
        user_df = user_df.drop(columns=["Outcome"])

    user_df["Prediction"] = predictions_df["Prediction"]
    user_df["Score"] = predictions_df["Score"]

    st.subheader("🔍 Prediction Results")
    st.metric("Non-diabetic (0)", (user_df["Prediction"] == 0).sum())
    st.metric("Diabetic (1)", (user_df["Prediction"] == 1).sum())

    st.subheader("📋 Data with Predictions")
    st.dataframe(user_df)

    st.download_button(
        label="Download predictions.csv",
        data=user_df.to_csv(index=False),
        file_name="predictions.csv",
        mime="text/csv"
    )

    # Visualization Tabs
    st.subheader("📊 Visualizations")
    tab1, tab2, tab3 = st.tabs(["Prediction Distribution", "Feature Correlations", "Feature Analysis"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            fig1, ax1 = plt.subplots(figsize=(4.5, 4.5))
            ax1.pie(
                [(user_df["Prediction"] == 0).sum(), (user_df["Prediction"] == 1).sum()],
                labels=["Non-diabetic", "Diabetic"],
                autopct="%1.1f%%",
                startangle=90,
                colors=["#3498db", "#e74c3c"]
            )
            ax1.axis("equal")
            ax1.set_title("Prediction Breakdown", fontsize=10)
            st.pyplot(fig1)

        with col2:
            fig2, ax2 = plt.subplots(figsize=(5.5, 3.5))
            sns.histplot(user_df["Score"], bins=20, kde=True, ax=ax2)
            ax2.axvline(x=0.5, color='r', linestyle='--', label='Threshold')
            ax2.set_title("Score Distribution", fontsize=10)
            ax2.legend()
            st.pyplot(fig2)

    with tab2:
        fig3, ax3 = plt.subplots(figsize=(7.5, 6.5))
        corr = user_df.select_dtypes(include=np.number).corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm", ax=ax3)
        ax3.set_title("Correlation Heatmap", fontsize=12)
        st.pyplot(fig3)

    with tab3:
        feature = st.selectbox("Select a feature:", [col for col in user_df.columns if col not in ["Prediction", "Score"]])

        fig4, ax4 = plt.subplots(figsize=(6, 4))
        sns.boxplot(data=user_df, x="Prediction", y=feature, ax=ax4)
        ax4.set_title(f"{feature} by Prediction", fontsize=11)
        st.pyplot(fig4)

        fig5, ax5 = plt.subplots(figsize=(6, 4))
        sns.histplot(data=user_df, x=feature, hue="Prediction", kde=True, multiple="dodge", ax=ax5)
        ax5.set_title(f"{feature} Distribution by Prediction", fontsize=11)
        st.pyplot(fig5)

        if st.checkbox("Show descriptive statistics"):
            st.write(user_df.groupby("Prediction")[feature].describe())

# --- Reset Demo Button ---
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset Demo"):
    with st.spinner("Resetting..."):
        result = subprocess.run(["python", "reset.py"], capture_output=True, text=True)
        if result.returncode == 0:
            st.sidebar.success("Demo reset! Please refresh the app.")
        else:
            st.sidebar.error("Failed to reset.")
            st.sidebar.code(result.stderr)