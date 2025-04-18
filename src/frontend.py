import streamlit as st
import pandas as pd
import subprocess
import os
import matplotlib.pyplot as plt
import seaborn as sns
import csv
import time
import numpy as np

# Initialize session state variables if they don't exist
if 'predictions_loaded' not in st.session_state:
    st.session_state.predictions_loaded = False
if 'df_with_preds' not in st.session_state:
    st.session_state.df_with_preds = None
if 'zero_count' not in st.session_state:
    st.session_state.zero_count = 0
if 'one_count' not in st.session_state:
    st.session_state.one_count = 0

st.set_page_config(page_title="PPML Diabetes Predictor", layout="wide")

st.title("🔒 Privacy-Preserving Diabetes Prediction")
st.markdown("Upload patient health data to make encrypted predictions using a federated, privacy-preserving model.")

# Sidebar for project info and documentation
with st.sidebar:
    st.header("About This Project")
    st.markdown("""
    This application uses homomorphic encryption to perform predictions on sensitive 
    health data without exposing the raw information.
    
    **How it works:**
    1. Your data is encrypted locally
    2. ML inference happens on encrypted data
    3. Results are decrypted for viewing
    
    **Features:**
    - Homomorphic encryption with TenSEAL
    - Federated learning model
    - Private inference
    """)
    
    st.header("Required Data Format")
    st.markdown("""
    The CSV should include these columns:
    - Pregnancies
    - Glucose
    - BloodPressure
    - SkinThickness
    - Insulin
    - BMI
    - DiabetesPedigreeFunction
    - Age
    """)

# Check for required directories
os.makedirs("./data", exist_ok=True)
os.makedirs("./model", exist_ok=True)
os.makedirs("./model/params", exist_ok=True)

# Check for model files
model_params_exist = os.path.exists("./model/params/norm_param.json")
context_exists = os.path.exists("./model/params/context.ckks")

# Display status
col1, col2 = st.columns([1, 1])
with col1:
    if model_params_exist:
        st.success("✅ Model parameters found")
    else:
        st.warning("⚠️ No model parameters found. Model will be trained on startup.")
        
with col2:
    if context_exists:
        st.success("✅ Encryption context found")
    else:
        st.info("ℹ️ Encryption context will be generated during processing")

# File uploader
uploaded_file = st.file_uploader("Upload a CSV file with patient data:", type=["csv"])

if uploaded_file is not None:
    # Load and display data
    try:
        df = pd.read_csv(uploaded_file)
        st.subheader("📋 Data Preview")
        st.dataframe(df.head())
        
        # Basic data validation
        expected_columns = ["Pregnancies", "Glucose", "BloodPressure", "SkinThickness", 
                           "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"]
        
        missing_cols = [col for col in expected_columns if col not in df.columns]
        
        if missing_cols:
            st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
        else:
            # Remove outcome column if present (we're predicting this)
            if "Outcome" in df.columns:
                st.info("'Outcome' column found in data. This will be ignored as it's what we're predicting.")
                
            # Save the uploaded data
            df.to_csv("./data/user_data.csv", index=False)
            
            # Processing button
            if st.button("Run Privacy-Preserving Inference", type="primary"):
                with st.spinner("Processing data..."):
                    # Step 1: Train model if needed
                    if not model_params_exist:
                        progress_text = "Training federated model..."
                        with st.status(progress_text) as status:
                            result = subprocess.run(["python", "./model/train_model.py"], 
                                                 capture_output=True, text=True)
                            if result.returncode != 0:
                                st.error("❌ Error training model")
                                st.code(result.stderr)
                                status.update(label="Model training failed", state="error")
                            else:
                                st.success("✅ Model trained successfully")
                                status.update(label="Model trained successfully", state="complete")
                    
                    # Step 2: Encrypt data
                    progress_text = "Encrypting data..."
                    with st.status(progress_text) as status:
                        result = subprocess.run(["python", "./model/prepare_encrypt_data.py"], 
                                              capture_output=True, text=True)
                        if result.returncode != 0:
                            st.error("❌ Error encrypting data")
                            st.code(result.stderr)
                            status.update(label="Data encryption failed", state="error")
                        else:
                            st.success("✅ Data encrypted successfully")
                            status.update(label="Data encrypted successfully", state="complete")
                    
                    # Step 3: Run inference
                    progress_text = "Running encrypted inference..."
                    with st.status(progress_text) as status:
                        result = subprocess.run(["python", "./model/inference.py"], 
                                              capture_output=True, text=True)
                        if result.returncode != 0:
                            st.error("❌ Error during inference")
                            st.code(result.stderr)
                            status.update(label="Inference failed", state="error")
                        else:
                            st.success("✅ Inference completed successfully")
                            status.update(label="Inference completed successfully", state="complete")
                            st.text(result.stdout)
                    
                    # Step 4: Decrypt predictions
                    progress_text = "Decrypting predictions..."
                    with st.status(progress_text) as status:
                        result = subprocess.run(["python", "./model/decrypt_output.py"], 
                                              capture_output=True, text=True)
                        if result.returncode != 0:
                            st.error("❌ Error decrypting predictions")
                            st.code(result.stderr)
                            status.update(label="Decryption failed", state="error")
                        else:
                            st.success("✅ Predictions decrypted successfully")
                            status.update(label="Predictions decrypted successfully", state="complete")
                            for line in result.stdout.splitlines():
                                st.text(line)
                
                # Display results if available
                if os.path.exists("./model/predictions.csv"):
                    # Set session state to indicate predictions are loaded
                    st.session_state.predictions_loaded = True
                    
                    # Load predictions
                    predictions_df = pd.read_csv("./model/predictions.csv")
                    
                    # Store counts in session state
                    st.session_state.zero_count = (predictions_df["Prediction"] == 0).sum()
                    st.session_state.one_count = (predictions_df["Prediction"] == 1).sum()
                    
                    # Add predictions to original data and store in session state
                    df_with_preds = df.copy()
                    df_with_preds["Prediction"] = predictions_df["Prediction"].values
                    df_with_preds["Score"] = predictions_df["Score"].values
                    st.session_state.df_with_preds = df_with_preds
                else:
                    st.error("❌ No prediction results found. There might be an error in the pipeline.")
    except Exception as e:
        st.error(f"Error processing the file: {str(e)}")

# Display results if predictions are loaded in session state
if st.session_state.predictions_loaded:
    st.subheader("🔍 Prediction Results")
    
    # Display summary
    col1, col2 = st.columns([1, 1])
    with col1:
        st.metric("Non-diabetic predictions (0)", st.session_state.zero_count)
    with col2:
        st.metric("Diabetic predictions (1)", st.session_state.one_count)
    
    # Display data with predictions
    st.subheader("Data with Predictions")
    st.dataframe(st.session_state.df_with_preds)
    
    # Download button for results
    csv = st.session_state.df_with_preds.to_csv(index=False)
    st.download_button(
        label="Download Results CSV",
        data=csv,
        file_name="diabetes_predictions.csv",
        mime="text/csv",
    )
    
    # Visualizations
    st.subheader("📊 Visualizations")
    
    # Create tabs for visualizations
    tab1, tab2, tab3 = st.tabs(["Prediction Distribution", "Feature Correlations", "Feature Analysis"])
    
    with tab1:
        # Pie chart of predictions
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie([st.session_state.zero_count, st.session_state.one_count], 
               labels=["Non-diabetic (0)", "Diabetic (1)"], 
               autopct='%1.1f%%', startangle=90, colors=['#3498db', '#e74c3c'])
        ax.axis('equal')
        st.pyplot(fig)
        
        # Histogram of scores
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(data=st.session_state.df_with_preds, x="Score", bins=20, kde=True, ax=ax)
        ax.axvline(x=0.5, color='r', linestyle='--', label='Decision Boundary')
        ax.set_title("Distribution of Prediction Scores")
        ax.set_xlabel("Score")
        ax.set_ylabel("Count")
        ax.legend()
        st.pyplot(fig)
    
    with tab2:
        # Correlation heatmap
        fig, ax = plt.subplots(figsize=(12, 10))
        numeric_df = st.session_state.df_with_preds.select_dtypes(include=['number'])
        corr = numeric_df.corr()
        mask = np.zeros_like(corr)
        mask[np.triu_indices_from(mask)] = True
        sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        ax.set_title("Feature Correlation Heatmap")
        st.pyplot(fig)
    
    with tab3:
        # Feature analysis by prediction
        col1, col2 = st.columns([1, 3])
        
        with col1:
            feature = st.selectbox(
                "Select feature to analyze:",
                options=[col for col in st.session_state.df_with_preds.columns if col not in ["Prediction", "Score"]]
            )
        
        with col2:
            if feature:
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.boxplot(data=st.session_state.df_with_preds, x="Prediction", y=feature, ax=ax)
                ax.set_title(f"{feature} by Prediction Outcome")
                ax.set_xlabel("Prediction (0: Non-diabetic, 1: Diabetic)")
                st.pyplot(fig)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.histplot(data=st.session_state.df_with_preds, x=feature, hue="Prediction", 
                            multiple="dodge", kde=True, ax=ax)
                ax.set_title(f"Distribution of {feature} by Prediction")
                st.pyplot(fig)
                
                if st.checkbox("Show descriptive statistics"):
                    st.write("Statistics by prediction group:")
                    st.write(st.session_state.df_with_preds.groupby("Prediction")[feature].describe())