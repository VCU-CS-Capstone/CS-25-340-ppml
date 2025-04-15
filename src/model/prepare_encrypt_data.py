import json
import tenseal as ts
import pandas as pd
import os

# Paths
norm_path = './model/params/norm_param.json'
context_path = './model/params/tenseal_context.tenseal'
data_path = './data/user_data.csv'
output_folder = './data/encrypted_user_data'

os.makedirs(output_folder, exist_ok=True)

# Load normalization parameters
with open(norm_path, 'r') as f:
    norm = json.load(f)
X = norm['mean']
std = norm['std']

# Create TenSEAL context
context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,
    coeff_mod_bit_sizes=[40, 30, 30, 40]
)
context.global_scale = 2 ** 40
context.generate_galois_keys()
context.generate_relin_keys()

# Save context
with open(context_path, 'wb') as f:
    f.write(context.serialize(save_public_key=True, save_secret_key=True))

# Normalize data
df = pd.read_csv(data_path)
if "Outcome" in df.columns:
    df = df.drop(columns=["Outcome"])
data = ((df - X) / std).values

# Encrypt and save each row
for idx, row in enumerate(data):
    enc_vec = ts.ckks_vector(context, row)
    with open(f"{output_folder}/vector_{idx}.bin", 'wb') as f:
        f.write(enc_vec.serialize())

print(f"✅ Encrypted {len(data)} vectors saved to {output_folder}")
