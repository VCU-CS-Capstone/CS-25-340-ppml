# user_input.py

import tenseal as ts
import pandas as pd
import numpy as np
import json
import pickle

def load_normalization_params(path):
    with open(path, "r") as f:
        norm = json.load(f)
    return np.array(norm["mean"]), np.array(norm["std"])

def load_user_data(file_path):
    data = pd.read_csv(file_path)

    if "Outcome" in data.columns:
        print("Warning: 'Outcome' column found but will be ignored for predictions")
        data = data.drop(columns=["Outcome"])

    return data.values

def normalize_data(data, mean, std):
    return (data - mean) / std

def encrypt_data(data, context):
    return [ts.ckks_vector(context, row) for row in data]

def save_encrypted_data(encrypted_vectors, output_file="encrypted_user_input.pkl"):
    with open(output_file, "wb") as f:
        pickle.dump(encrypted_vectors, f)

# Load normalization params
norm_param_path = ''
input_data = ''
output_data = 'enc_user_data.pkl'
context = ''

X_mean, X_std = load_normalization_params(norm_param_path)

# Load and normalize user data
raw_data = load_user_data(input_data)
normalized = normalize_data(raw_data, X_mean, X_std)

# Load TenSEAL context
with open(context_file, "rb") as f:
    context = ts.context_from(f.read())

# Encrypt
encrypted_vectors = encrypt_data(normalized, context)

# Save encrypted vectors to file
save_encrypted_data(encrypted_vectors, output_file)
print(f"Encrypted user input saved to: {output_file}")
