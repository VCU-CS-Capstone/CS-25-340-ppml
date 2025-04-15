import tenseal as ts
import json
import os

# Paths
context_path = './model/params/tenseal_context.tenseal'
encrypted_data_path = './data/encrypted_user_data'         # single input file
norm_param_path = './model/params/norm_param.json'
encrypted_output_path = './data/encrypted_output'          # single output file

# Load TenSEAL context (must include secret key)
try:
    with open(context_path, 'rb') as f:
        context = ts.context_from(f.read())
except FileNotFoundError:
    raise FileNotFoundError(f"CKKS context not found at path: {context_path}")

# Load model parameters
with open(norm_param_path, 'r') as f:
    norm = json.load(f)
    global_weights = norm['global_weights']
    global_intercept = norm['global_intercept']

# Encrypt weights and intercept
enc_weights = ts.ckks_vector(context, global_weights)
enc_intercept = ts.ckks_vector(context, [global_intercept])

# Load encrypted user vectors from a single file
encrypted_data_vectors = []
try:
    with open(encrypted_data_path, 'rb') as f:
        while True:
            try:
                vec = ts.ckks_vector_from(context, f.read())
                encrypted_data_vectors.append(vec)
            except Exception:
                break
except FileNotFoundError:
    raise FileNotFoundError(f"Encrypted user data not found at: {encrypted_data_path}")

if not encrypted_data_vectors:
    raise ValueError("No valid encrypted vectors found in file.")

# Perform encrypted inference
encrypted_outputs = []
for vec in encrypted_data_vectors:
    output = vec.dot(enc_weights)
    output += enc_intercept
    encrypted_outputs.append(output)

# Save all encrypted outputs into one file
with open(encrypted_output_path, 'wb') as f:
    for out in encrypted_outputs:
        f.write(out.serialize())

print(f"✅ Encrypted inference complete. Saved {len(encrypted_outputs)} predictions to: {encrypted_output_path}")
