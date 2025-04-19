import tenseal as ts
import pickle
import csv
import os
import numpy as np

# Load encryption context
with open("./model/params/context.ckks", "rb") as f:
    context = ts.context_from(f.read())

# Load all encrypted predictions from batch .pkl file
with open("./data/encrypted_predictions.pkl", "rb") as f:
    encrypted_preds = pickle.load(f)

scores = []
for idx, pred_bytes in enumerate(encrypted_preds):
    try:
        enc_pred = ts.ckks_vector_from(context, pred_bytes)
        val = enc_pred.decrypt()[0]
        scores.append(val)
    except Exception as e:
        # Log or print and skip corrupted entries
        print(f"Warning: failed to decrypt prediction #{idx}: {e}")
        continue

# Apply a small epsilon to counteract CKKS rounding noise
eps = 1e-6
labels = [1 if s > 0.5 + eps else 0 for s in scores]

# Compute class counts and overall metrics
zero_count = labels.count(0)
one_count  = labels.count(1)
total      = len(labels)
accuracy   = (np.array(labels) == np.array([int(l) for l in labels])).mean()  # same list comparison

print("Decrypted Predictions Summary:")
print(f"Total 0s: {zero_count}")
print(f"Total 1s: {one_count}")

# Save to CSV for frontend use
os.makedirs("./model", exist_ok=True)
with open("./model/predictions.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Prediction", "Score"])
    for lbl, sc in zip(labels, scores):
        writer.writerow([lbl, round(sc, 4)])

print(f"Saved predictions.csv ({total} records)")
