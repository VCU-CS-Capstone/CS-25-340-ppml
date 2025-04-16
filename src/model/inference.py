import tenseal as ts
import pickle
import json
import os

# Ensure the context file exists
context_path = "./model/params/context.ckks"
if not os.path.exists(context_path):
    raise FileNotFoundError("CKKS encryption context file not found. Expected at ./model/params/context.ckks")

# Load encryption context from client-provided file
with open(context_path, "rb") as f:
    context = ts.context_from(f.read())

# Load model weights and normalization params
with open("./model/params/norm_param.json", "r") as f:
    model_data = json.load(f)

weights = model_data["global_weights"]
intercept = model_data["global_intercept"]

# Encrypt model weights
enc_weights = ts.ckks_vector(context, weights)
enc_intercept = ts.ckks_vector(context, [intercept])

# Load all encrypted user data from batch file
with open("./data/encrypted_user_data/batch_vectors.pkl", "rb") as f:
    encrypted_rows = pickle.load(f)


vectors = [ts.ckks_vector_from(context, row) for row in encrypted_rows]

# Perform inference
os.makedirs("./data/predictions", exist_ok=True)
pred_paths = []
for idx, enc_x in enumerate(vectors):
    pred = enc_x.dot(enc_weights) + enc_intercept
    pred_bytes = pred.serialize()
    path = f"./data/predictions/pred_{idx}.bin"
    with open(path, "wb") as f:
        f.write(pred_bytes)
    pred_paths.append(path)

print(f"Saved {len(pred_paths)} encrypted predictions to ./data/predictions")
