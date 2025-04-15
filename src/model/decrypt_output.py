import tenseal as ts

# Paths
context_with_secret_path = './model/params/tenseal_context.tenseal'  # this must include secret key
encrypted_output_path = './data/encrypted_output'

# Load TenSEAL context (with secret key)
try:
    with open(context_with_secret_path, 'rb') as f:
        context = ts.context_from(f.read())
except FileNotFoundError:
    raise FileNotFoundError("Secret context file not found.")

# Load encrypted predictions
encrypted_preds = []
try:
    with open(encrypted_output_path, 'rb') as f:
        while True:
            try:
                enc = ts.ckks_vector_from(context, f)
                encrypted_preds.append(enc)
            except Exception:
                break
except FileNotFoundError:
    raise FileNotFoundError("Encrypted output file not found.")

# Decrypt predictions
decrypted_preds = [vec.decrypt()[0] for vec in encrypted_preds]

# Thresholded predictions (optional)
classified_preds = [1 if pred > 0.5 else 0 for pred in decrypted_preds]

# Output
print("\nDecrypted Predictions (logits):")
for i, pred in enumerate(decrypted_preds):
    print(f"Sample {i+1}: {pred:.4f}")

print("\nClassified Predictions (threshold = 0.5):")
for i, label in enumerate(classified_preds):
    print(f"Sample {i+1}: {label}")
