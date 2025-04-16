import tenseal as ts
import os
import csv
import pickle

# Load encryption context
with open("./model/params/context.ckks", "rb") as f:
    context = ts.context_from(f.read())

# Load all encrypted predictions from batch .pkl file
with open("./data/encrypted_predictions.pkl", "rb") as f:
    encrypted_preds = pickle.load(f)

zero_count = 0
one_count = 0
predictions = []

for idx, pred_bytes in enumerate(encrypted_preds):
    enc_pred = ts.ckks_vector_from(context, pred_bytes)
    pred_value = enc_pred.decrypt()[0]
    label = 1 if pred_value > 0.5 else 0
    predictions.append((label, pred_value))
    if label == 1:
        one_count += 1
    else:
        zero_count += 1

print("Decrypted Predictions Summary:")
print(f"Total 0s: {zero_count}")
print(f"Total 1s: {one_count}")

# Save to CSV for frontend use
os.makedirs("./model", exist_ok=True)
with open("./model/predictions.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Prediction", "Score"])
    for label, score in predictions:
        writer.writerow([label, round(score, 4)])