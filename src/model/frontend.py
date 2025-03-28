import streamlit as st
import pandas as pd
import subprocess
import os

st.set_page_config(page_title="PPML Diabetes Predictor", layout="centered")

st.title("🛡️ Privacy-Preserving Diabetes Prediction")
st.markdown("Upload patient health data to make encrypted predictions using a federated, privacy-preserving model.")

uploaded_file = st.file_uploader("Upload a CSV file (must match diabetes format)", type=["csv"])

# Check if model exists
model_exists = os.path.exists("encrypted_model.pkl")
if model_exists:
    st.success("✅ Encrypted model file found. Ready for inference.")
else:
    st.warning("⚠️ No encrypted model found. Model will be trained on startup.")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df.head())

    if st.button("Run Privacy-Preserving Inference"):
        # Save uploaded file as new_data.csv
        df.to_csv("demo_data.csv", index=False)

        with st.spinner("Encrypting & predicting..."):
            result = subprocess.run(["python", "ciphertext_model.py"], capture_output=True, text=True)

        st.success("✔ Processing complete!")

        # Show captured output
        if result.stdout:
            output = result.stdout.splitlines()
            show = False
            for line in output:
                # Start printing when we find relevant lines
                if any(k in line.lower() for k in ["mcc", "prediction", "distribution", "high-risk", "potential"]):
                    show = True
                if show:
                    st.markdown(f"```{line}```")
        else:
            st.error("⚠ No output received. Check if ciphertext_model.py ran without errors.")

        # Optional: show backend errors
        if result.stderr:
            st.markdown("**Debug Output:**")
            st.text(result.stderr)
