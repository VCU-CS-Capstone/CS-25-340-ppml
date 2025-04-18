import streamlit as st
import pandas as pd
import subprocess
import os
import matplotlib.pyplot as plt
import seaborn as sns
import csv
import numpy as np

os.makedirs(".streamlit", exist_ok=True)
config_path = ".streamlit/config.toml"
if not os.path.exists(config_path):
    with open(config_path, "w") as f:
        f.write("""[server]\nmaxUploadSize = 1000\n""")

st.set_page_config(page_title="PPML Diabetes Predictor", layout="wide")

st.title("🔒 Privacy-Preserving Diabetes Prediction")
st.markdown("Upload encrypted patient data to run secure predictions using a federated, privacy-preserving model.")

# Sidebar
with st.sidebar:
    st.header("About This Project")
    st.markdown("""
    This application uses homomorphic encryption to perform predictions on sensitive 
    health data without exposing the raw information.

    **How it works:**
    - Data is encrypted on the client machine
    - The server performs ML inference on encrypted data
    - Results are decrypted and summarized

    **Tech:** TenSEAL (CKKS), Federated Logistic Regression, Differential Privacy
    """)

# Upload encrypted .pkl file
encrypted_file = st.file_uploader("Upload encrypted batch_vectors.pkl", type=["pkl"])

# Upload the original (unencrypted) data used for encryption for analysis/visualization only
reference_csv = st.file_uploader("Upload original CSV used for encryption (optional, for visualization only)", type=["csv"])

if encrypted_file is not None:
    with open("./data/encrypted_user_data.pkl", "wb") as f:
        f.write(encrypted_file.getbuffer())
    st.success("Encrypted data uploaded successfully.")

    # Run inference
    progress_text = "Running encrypted inference..."
    with st.status(progress_text) as status:
        result = subprocess.run(["python", "./model/inference.py"], capture_output=True, text=True)
        if result.returncode != 0:
            st.error("❌ Error during inference")
            st.code(result.stderr)
            status.update(label="Inference failed", state="error")
        else:
            st.success("✅ Inference completed successfully")
            status.update(label="Inference completed successfully", state="complete")

    # Run decryption
    progress_text = "Decrypting predictions..."
    with st.status(progress_text) as status:
        result = subprocess.run(["python", "./model/decrypt_output.py"], capture_output=True, text=True)
        if result.returncode != 0:
            st.error("❌ Error decrypting predictions")
            st.code(result.stderr)
            status.update(label="Decryption failed", state="error")
        else:
            st.success("✅ Predictions decrypted successfully")
            status.update(label="Predictions decrypted successfully", state="complete")

    # Load and display predictions if available
    if os.path.exists("./model/predictions.csv"):
        preds_df = pd.read_csv("./model/predictions.csv")
        st.subheader("🔍 Prediction Results")
        st.metric("Non-diabetic (0)", (preds_df["Prediction"] == 0).sum())
        st.metric("Diabetic (1)", (preds_df["Prediction"] == 1).sum())

        if reference_csv is not None:
            original_df = pd.read_csv(reference_csv)
            if "Outcome" in original_df.columns:
                original_df = original_df.drop(columns=["Outcome"])
            original_df["Prediction"] = preds_df["Prediction"].values
            original_df["Score"] = preds_df["Score"].values
            st.subheader("📊 Visual Analysis")
            tab1, tab2, tab3 = st.tabs(["Prediction Breakdown", "Feature Correlation", "Feature Exploration"])

            with tab1:
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.pie([
                    (original_df["Prediction"] == 0).sum(),
                    (original_df["Prediction"] == 1).sum()
                ],
                labels=["Non-diabetic (0)", "Diabetic (1)"],
                autopct='%1.1f%%', startangle=90,
                colors=['#3498db', '#e74c3c'])
                ax.axis('equal')
                st.pyplot(fig)

            with tab2:
                fig, ax = plt.subplots(figsize=(12, 10))
                numeric_df = original_df.select_dtypes(include=['number'])
                corr = numeric_df.corr()
                sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
                ax.set_title("Feature Correlation Heatmap")
                st.pyplot(fig)

            with tab3:
                feature = st.selectbox("Select a feature to explore:", [col for col in original_df.columns if col not in ["Prediction", "Score"]])
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.boxplot(data=original_df, x="Prediction", y=feature, ax=ax)
                ax.set_title(f"{feature} by Prediction")
                st.pyplot(fig)

                fig, ax = plt.subplots(figsize=(10, 6))
                sns.histplot(data=original_df, x=feature, hue="Prediction", multiple="dodge", kde=True, ax=ax)
                ax.set_title(f"Distribution of {feature} by Prediction")
                st.pyplot(fig)

        else:
            st.info("Upload the original CSV to unlock full analysis features.")

        csv = preds_df.to_csv(index=False)
        st.download_button("Download Prediction Results", data=csv, file_name="predictions.csv", mime="text/csv")

else:
    st.info("Awaiting encrypted input file for prediction.")
