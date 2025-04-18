import tenseal as ts
import pandas as pd
import pickle
import os
import json

# Load normalization parameters
with open("./model/params/norm_param.json", "r") as f:
    params = json.load(f)
mean = params["mean"]
std = params["std"]

# Load polynomial transformer
with open("./model/params/poly_transformer.pkl", "rb") as f:
    poly = pickle.load(f)

# Load input user data
input_path = "./data/user_data.csv"
df = pd.read_csv(input_path)
if "Outcome" in df.columns:
    df = df.drop(columns=["Outcome"])
data = df.values

# Normalize data
normalized_data = (data - mean) / std

# Apply polynomial transformation
X_poly = poly.transform(normalized_data)

# Create encryption context
context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,
    coeff_mod_bit_sizes=[60, 40, 40, 60]
)
context.global_scale = 2**40
context.generate_galois_keys()

# Save context
os.makedirs("./model/params", exist_ok=True)
with open("./model/params/context.ckks", "wb") as f:
    f.write(context.serialize(save_secret_key=True))

# Encrypt each row and collect into a batch
batch_encrypted = []
for row in X_poly:
    enc_vec = ts.ckks_vector(context, row)
    batch_encrypted.append(enc_vec.serialize())

# Save batch to a binary file using pickle
with open("./data/encrypted_user_data.pkl", "wb") as f:
    pickle.dump(batch_encrypted, f)

print(f"Encrypted and saved {len(batch_encrypted)} vectors to ./data/encrypted_user_data.pkl")