import tenseal as ts
import pickle
import os

# Ensure the context file exists
context_path = "./model/params/context.ckks"
if not os.path.exists(context_path):
    raise FileNotFoundError("CKKS encryption context file not found. Expected at ./model/params/context.ckks")

# Load encryption context from client-provided file
with open(context_path, "rb") as f:
    context = ts.context_from(f.read())

# Load full model bundle (weights, intercept)
with open("./model/params/params.pkl", "rb") as f:
    model_bundle = pickle.load(f)

weights = model_bundle["weights"]
intercept = model_bundle["intercept"]

# Encrypt model weights
enc_weights = ts.ckks_vector(context, weights)
enc_intercept = ts.ckks_vector(context, [intercept])

# Load all encrypted user data from batch file
with open("./data/encrypted_user_data.pkl", "rb") as f:
    encrypted_rows = pickle.load(f)

vectors = [ts.ckks_vector_from(context, row) for row in encrypted_rows]

# Perform inference
all_preds = []
for enc_x in vectors:
    pred = enc_x.dot(enc_weights) + enc_intercept
    all_preds.append(pred.serialize())

# Save all encrypted predictions to one pkl
with open("./data/encrypted_predictions.pkl", "wb") as f:
    pickle.dump(all_preds, f)

print(f"Saved {len(all_preds)} encrypted predictions to ./data/encrypted_predictions.pkl")
