import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler

# Step 1: Load the CSV file
input_file = "./data/raw_med_data.csv"  # Replace with your CSV file path
df = pd.read_csv(input_file)

# Display the first 5 rows of the original data
print("Original Data:")
print(df.head())

# Step 2: Normalize the data
# Choose either Min-Max Scaling or Standardization

# Option 1: Min-Max Scaling (range [0, 1])
scaler = MinMaxScaler()
normalized_data = scaler.fit_transform(df.iloc[:, :-1])  # Normalize all columns except the target

# Option 2: Standardization (mean=0, std=1)
# scaler = StandardScaler()
# normalized_data = scaler.fit_transform(df.iloc[:, :-1])  # Normalize all columns except the target

# Create a DataFrame with the normalized data
normalized_df = pd.DataFrame(normalized_data, columns=df.columns[:-1])

# Add the target column back to the normalized DataFrame
normalized_df["Disease"] = df["Disease"]

# Display the first 5 rows of the normalized data
print("\nNormalized Data:")
print(normalized_df.head())

# Step 3: Save the normalized data to a new CSV file
output_file = "./data/normalized_med_data.csv"  # Replace with your desired output file path
normalized_df.to_csv(output_file, index=False)

print(f"\nNormalized data saved to {output_file}")