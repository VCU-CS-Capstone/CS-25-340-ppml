# inference.py
import tenseal as ts
import json
import os
import glob

# Paths
context_path = './model/params/tenseal_context.tenseal'
input_dir = './data/encrypted_user_data'           # now a directory
norm_param_path = './model/params/norm_param.json'
output_dir = './data/encrypted_output'

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load TenSEAL context (must include secret key)
with open(context_path, 'rb') as f:
    context = ts.context_from(f.read())

# Load model parameters
with open(norm_param_path, 'r') as f:
    norm = json.load(f)
    global_weights = norm['global_weights']
    global_intercept = norm['global_intercept']

# Encrypt weights and intercept
enc_weights = ts.ckks_vector(context, global_weights)
enc_intercept = ts.ckks_vector(context, [global_intercept])

# Load encrypted vectors from directory
encrypted_data_vectors = []
input_files = sorted(glob.glob(f"{input_dir}/*.bin"))
if not input_files:
    raise ValueError("❌ No encrypted input files found.")

for file_path in input_files:
    with open(file_path, 'rb') as f:
        vec = ts.ckks_vector_from(context, f.read())
        encrypted_data_vectors.append(vec)

# Encrypted inference
for i, vec in enumerate(encrypted_data_vectors):
    output = vec.dot(enc_weights)
    output += enc_intercept
    with open(f"{output_dir}/pred_{i}.bin", "wb") as f:
        f.write(output.serialize())

print(f"✅ Encrypted inference complete. Saved {len(encrypted_data_vectors)} predictions to {output_dir}")
