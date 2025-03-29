import streamlit as st
import pandas as pd
import subprocess
import os
import matplotlib.pyplot as plt
import seaborn as sns
import ast
import json

st.set_page_config(page_title="PPML Diabetes Predictor", layout="centered")

st.title("🧠 Privacy-Preserving Diabetes Prediction")
st.markdown("Upload patient health data to make encrypted predictions using a federated, privacy-preserving model.")

uploaded_file = st.file_uploader("Upload a CSV file (must match diabetes format):", type=["csv"])

model_exists = os.path.exists("encrypted_model.pkl")
if model_exists:
    st.markdown("<div style='padding: 0.5em; background-color: #1f2937; border-radius: 0.5em; color: white;'>✅ Encrypted model file found. Ready for inference.</div>", unsafe_allow_html=True)
else:
    st.markdown("<div style='padding: 0.5em; background-color: #7f1d1d; border-radius: 0.5em; color: white;'>⚠️ No encrypted model found. Model will be trained on startup.</div>", unsafe_allow_html=True)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("📋 Uploaded Data Preview")
    st.dataframe(df.head())

    if st.button("Run Privacy-Preserving Inference"):
        df.to_csv("new_data.csv", index=False)

        with st.spinner("Encrypting & predicting..."):
            result = subprocess.run(["python", "ciphertext_model.py"], capture_output=True, text=True)

        st.markdown("""
<div style='padding: 0.5em; background-color: #1e3a8a; border-radius: 0.5em; color: white;'>
✔ Inference completed!<br>
<span style='color: #dbeafe;'>Prediction Breakdown will appear below if available.</span>
</div>
""", unsafe_allow_html=True)

        output = result.stdout.splitlines()
        show = False
        predictions = []

        for line in output:
            if any(k in line.lower() for k in ["mcc", "prediction", "distribution"]):
                show = True
            if show:
                st.markdown(f"<div style='background-color: #111827; padding: 0.5em; border-radius: 0.25em; color: #d1d5db; font-family: monospace;'>{line}</div>", unsafe_allow_html=True)
            if "Predictions for new dataset" in line:
                try:
                    predictions = ast.literal_eval(line.split(":", 1)[1].strip())
                except Exception as e:
                    st.warning("⚠ Failed to parse predictions from output.")

        if not predictions and os.path.exists("predictions.json"):
            try:
                with open("predictions.json") as f:
                    predictions = json.load(f)
            except:
                st.warning("⚠ Could not load predictions from file.")

        if predictions and len(predictions) == len(df):
            zero_count = predictions.count(0)
            one_count = predictions.count(1)
            st.markdown(f"<div style='background-color: #111827; padding: 0.5em; border-radius: 0.25em; color: #d1d5db; font-family: monospace;'>Prediction Breakdown: {zero_count} non-diabetic, {one_count} diabetic</div>", unsafe_allow_html=True)
            if abs(zero_count - one_count) > 0.6 * len(predictions):
                st.warning("⚠ Prediction results show class imbalance — this could indicate a biased or undertrained model.")

            with st.expander("🔍 Feature Correlation Heatmap"):
                st.subheader("📊 Feature Correlation Heatmap")
                try:
                    corr = df.drop(columns=["Prediction"], errors="ignore").corr()
                    fig, ax = plt.subplots()
                    sns.heatmap(corr, cmap="coolwarm", annot=True, fmt=".2f", ax=ax)
                    st.pyplot(fig)
                except Exception as e:
                    st.warning(f"Could not display heatmap: {e}")

            df["Prediction"] = predictions

            with st.expander("📌 Feature Distributions by Prediction"):
                st.subheader("📌 Feature Distributions by Prediction")
                numeric_columns = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
                features = [col for col in numeric_columns if col not in ["Prediction"]]
                for feature in features:
                    try:
                        fig, ax = plt.subplots()
                        sns.histplot(data=df, x=feature, hue="Prediction", multiple="stack", palette="husl", kde=True, ax=ax)
                        ax.set_title(f"{feature} Distribution by Prediction")
                        st.pyplot(fig)
                    except Exception as e:
                        st.warning(f"Could not plot feature '{feature}': {e}")

        else:
            st.markdown("<div style='padding: 0.5em; background-color: #b91c1c; border-radius: 0.5em; color: white;'>⚠ No output received. Check if ciphertext_model.py ran without errors.</div>", unsafe_allow_html=True)

        if result.stderr:
            with st.expander("🔧 Backend Log"):
                st.text(result.stderr)
