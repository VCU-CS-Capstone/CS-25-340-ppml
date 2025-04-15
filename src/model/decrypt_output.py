import tenseal as ts
import glob
import pandas as pd  # Import pandas for better matrix printing

# Paths
context_path = './model/params/tenseal_context.tenseal'
output_dir = './data/encrypted_output'

# Load context (with secret key)
with open(context_path, 'rb') as f:
    context = ts.context_from(f.read())

# Load encrypted predictions from individual .bin files
encrypted_preds = []
for file_path in sorted(glob.glob(f"{output_dir}/pred_*.bin")):
    with open(file_path, 'rb') as f:
        enc = ts.ckks_vector_from(context, f.read())
        encrypted_preds.append(enc)

if not encrypted_preds:
    raise ValueError("❌ No encrypted predictions were loaded.")

# Decrypt predictions
decrypted_preds = [vec.decrypt()[0] for vec in encrypted_preds]
classified_preds = [1 if pred > 0.5 else 0 for pred in decrypted_preds]

# Create a DataFrame to print the results as a matrix
df = pd.DataFrame({
    'Sample': range(1, len(decrypted_preds) + 1),
    'Decrypted Prediction (Logits)': decrypted_preds,
    'Classified Prediction (Threshold = 0.5)': classified_preds
})

# Print the matrix (DataFrame)
print("\nDecrypted and Classified Predictions Matrix:")
print(df)

