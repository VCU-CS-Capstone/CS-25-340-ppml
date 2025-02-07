import numpy as np
import pandas as pd
from sklearn.datasets import make_classification

# Generate synthetic medical dataset with realistic ranges
np.random.seed(42)
n_samples = 10000

# Define realistic ranges for features
age = np.random.randint(18, 80, size=n_samples)  # Age: 18-79
bmi = np.random.uniform(18.5, 40.0, size=n_samples)  # BMI: 18.5-40.0
blood_pressure = np.random.randint(80, 180, size=n_samples)  # Blood Pressure: 80-179
cholesterol = np.random.randint(120, 300, size=n_samples)  # Cholesterol: 120-299

# Combine features into a dataset
X = np.column_stack((age, bmi, blood_pressure, cholesterol))

# Generate binary target (e.g., disease or no disease)
# Let's assume disease likelihood increases with age, BMI, blood pressure, and cholesterol
coefficients = np.array([0.05, 0.1, 0.02, 0.03])  # Weights for each feature
logits = np.dot(X, coefficients) + np.random.normal(0, 1, size=n_samples)  # Add noise
y = (logits > np.median(logits)).astype(int)  # Binary target

# Create a DataFrame
feature_names = ["Age", "BMI", "BloodPressure", "Cholesterol"]
df = pd.DataFrame(X, columns=feature_names)
df["Disease"] = y  # Add target column

# Save to CSV
df.to_csv("./data/raw_med_data.csv", index=False)

print("Raw dataset saved to raw_medical_data.csv")
print(df.head())  # Display first 5 rows