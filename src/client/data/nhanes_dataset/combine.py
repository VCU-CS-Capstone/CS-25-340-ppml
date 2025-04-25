import pandas as pd
import numpy as np

# File paths (modify if needed)
files = {
    "glucose": "glucose.xpt",
    "insulin": "insulin.xpt",
    "bmi": "body_measures.xpt",
    "blood_pressure": "blood_pressure.xpt",
    "demographics": "demographics.xpt",
    "diabetes_questionnaire": "diabetes_q.xpt",
    "pregnancies": "pregnancies.xpt"
}

# Load data
print("Loading NHANES data files...")
df_glu = pd.read_sas(files["glucose"])[["SEQN", "LBXGLU"]]  # Fasting glucose
df_ins = pd.read_sas(files["insulin"])[["SEQN", "LBXIN"]]  # Serum insulin
df_bmi = pd.read_sas(files["bmi"])[["SEQN", "BMXBMI"]]  # BMI

bp = pd.read_sas(files["blood_pressure"])
df_bp = bp[["SEQN", "BPXOSY1"]].rename(columns={"BPXOSY1": "BloodPressure"})  # First systolic

age = pd.read_sas(files["demographics"])[["SEQN", "RIDAGEYR"]]  # Age
df_diq = pd.read_sas(files["diabetes_questionnaire"])[["SEQN", "DIQ010"]]  # Diabetes indicator

df_rhq = pd.read_sas(files["pregnancies"])[["SEQN", "RHD167"]]
df_rhq = df_rhq[df_rhq["RHD167"].between(0, 5)]  # Valid delivery counts only
df_rhq = df_rhq.rename(columns={"RHD167": "Pregnancies"})

# Merge all on SEQN
print("Merging datasets...")
df = df_glu.merge(df_ins, on="SEQN", how="inner") \
         .merge(df_bmi, on="SEQN", how="inner") \
         .merge(df_bp, on="SEQN", how="inner") \
         .merge(age, on="SEQN", how="inner") \
         .merge(df_diq, on="SEQN", how="inner") \
         .merge(df_rhq, on="SEQN", how="inner")

# Drop rows with missing values
df = df.dropna(subset=["LBXGLU", "LBXIN", "BMXBMI", "BloodPressure", "RIDAGEYR", "DIQ010", "Pregnancies"])

# Normalize diabetes outcome (1 = Yes, 0 = No)
df = df[df["DIQ010"].isin([1, 2])]
df["Outcome"] = df["DIQ010"].replace({2: 0})

# Rename columns to match Pima structure
df = df.rename(columns={
    "LBXGLU": "Glucose",
    "LBXIN": "Insulin",
    "BMXBMI": "BMI",
    "RIDAGEYR": "Age"
})

# Add synthetic DiabetesPedigreeFunction and SkinThickness
df["DiabetesPedigreeFunction"] = np.random.normal(loc=0.5, scale=0.2, size=df.shape[0]).clip(0, 2.5)
df["SkinThickness"] = np.random.normal(loc=20, scale=8, size=df.shape[0]).clip(5, 50)

# Reorder columns
expected_columns = [
    "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
    "Insulin", "BMI", "DiabetesPedigreeFunction", "Age", "Outcome"
]
df = df[expected_columns]

# Round numeric columns for clarity
df = df.round({
    "Pregnancies": 0,
    "Glucose": 0,
    "BloodPressure": 0,
    "SkinThickness": 0,
    "Insulin": 0,
    "BMI": 1,
    "DiabetesPedigreeFunction": 3,
    "Age": 0
})

# Save to CSV
print("Saving final cleaned dataset...")
df.to_csv("nhanes_diabetes_cleaned.csv", index=False)
print("Done! Saved as nhanes_diabetes_cleaned.csv with shape:", df.shape)
