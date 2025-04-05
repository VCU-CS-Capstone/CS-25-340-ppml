import pandas as pd
import os
from sklearn.preprocessing import MinMaxScaler, StandardScaler

# Step 1: Load the CSV file
input_file = "./src/data/synthetic_diabetes.csv"  # Make sure this path is correct
df = pd.read_csv(input_file)

# Verify the target column name
print("Columns in dataset:", df.columns.tolist())

# Step 2: Normalize the data
# Separate features and target
features = df.drop(columns=["Outcome"])  # Changed from "Disease" to "Outcome"
target = df["Outcome"]

# Option 1: Min-Max Scaling (range [0, 1])
scaler = MinMaxScaler()
normalized_features = scaler.fit_transform(features)

# Option 2: Standardization (mean=0, std=1)
# scaler = StandardScaler()
# normalized_features = scaler.fit_transform(features)

# Create normalized DataFrame
normalized_df = pd.DataFrame(normalized_features, columns=features.columns)
normalized_df["Outcome"] = target  # Changed from "Disease" to "Outcome"

# Display samples
print("\nNormalized Data Samples:")
print(normalized_df.head())

# Step 3: Save the normalized data
os.makedirs("./data", exist_ok=True)  # Ensure directory exists
output_file = "./data/normalized_synth_data.csv"
normalized_df.to_csv(output_file, index=False)

print(f"\nNormalized data saved to {output_file}")
print("Class distribution:")
print(normalized_df["Outcome"].value_counts(normalize=True))