import tenseal as ts
import os
import csv

# Load encryption context
with open("./model/params/context.ckks", "rb") as f:
    context = ts.context_from(f.read())

# Load and decrypt predictions
pred_folder = "./data/predictions"
pred_files = sorted([f for f in os.listdir(pred_folder) if f.endswith(".bin")])

zero_count = 0
one_count = 0
predictions = []

for file in pred_files:
    with open(os.path.join(pred_folder, file), "rb") as f:
        enc_pred = ts.ckks_vector_from(context, f.read())
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
