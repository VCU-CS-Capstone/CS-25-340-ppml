import tenseal as ts
import pandas as pd
import numpy as np
import pickle
import os
from cryptography.fernet import Fernet, InvalidToken
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import matthews_corrcoef

# --- Load Dataset ---
data = pd.read_csv("diabetes.csv")
X = data.drop(columns=["Outcome"]).values
y = data["Outcome"].values

# Normalize data
X_mean = np.mean(X, axis=0)
X_std = np.std(X, axis=0)
X = (X - X_mean) / X_std

# Split into federated clients
n_clients = 5
X_clients = np.array_split(X, n_clients)
y_clients = np.array_split(y, n_clients)

# --- Initialize Encryption ---
context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,
    coeff_mod_bit_sizes=[60, 40, 40, 60]
)
context.global_scale = 2**40
context.generate_galois_keys()

# --- Secure Model Storage ---
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    with open("secret.key", "rb") as key_file:
        return key_file.read()

if not os.path.exists("secret.key"):
    generate_key()
key = load_key()
cipher = Fernet(key)

# --- Federated Training with DP ---
model_file = "encrypted_model.pkl"
if os.path.exists(model_file):
    try:
        with open(model_file, "rb") as f:
            encrypted_model = cipher.decrypt(f.read())
        global_weights, global_intercept = pickle.loads(encrypted_model)
        print("Loaded encrypted pre-trained model.")
    except (InvalidToken, pickle.UnpicklingError):
        print("Invalid model file. Training new model...")
        os.remove(model_file)
        train_new_model = True
    else:
        train_new_model = False
else:
    print("No pre-trained model found. Training a new one...")
    train_new_model = True

if train_new_model:
    # DP Parameters
    noise_scale = 0.1
    clip_threshold = 1.0
    
    global_weights = np.zeros(X.shape[1])
    global_intercept = 0
    num_epochs = 70
    
    for epoch in range(num_epochs):
        weight_updates = []
        intercept_updates = []
        
        for X_client, y_client in zip(X_clients, y_clients):
            model = LogisticRegression(max_iter=1000)
            model.fit(X_client, y_client)
            
            # Apply DP
            weights = np.clip(model.coef_[0], -clip_threshold, clip_threshold)
            weights += np.random.normal(0, noise_scale, weights.shape)
            
            intercept = np.clip(model.intercept_, -clip_threshold, clip_threshold)
            intercept += np.random.normal(0, noise_scale, intercept.shape)
            
            weight_updates.append(weights)
            intercept_updates.append(intercept[0])
        
        # Aggregate updates
        global_weights = np.mean(weight_updates, axis=0)
        global_intercept = np.mean(intercept_updates)
    
    # Save encrypted model
    with open(model_file, "wb") as f:
        encrypted_model = cipher.encrypt(pickle.dumps((global_weights, global_intercept)))
        f.write(encrypted_model)
    print("Saved encrypted trained model.")

# --- Training Evaluation ---
train_preds = (X @ global_weights + global_intercept) > 0.5
train_mcc = matthews_corrcoef(y, train_preds)
print(f"MCC on training set: {train_mcc:.4f}")

# --- New Data Prediction ---
new_data = pd.read_csv("new_data.csv")
if "Outcome" in new_data.columns:
    print("Warning: 'Outcome' column found but will be ignored for predictions")
    new_X = new_data.drop(columns=["Outcome"]).values
else:
    new_X = new_data.values

# Verify feature alignment
if new_X.shape[1] != X.shape[1]:
    raise ValueError(f"Expected {X.shape[1]} features, got {new_X.shape[1]}")

new_X = (new_X - X_mean) / X_std

# Encrypted predictions
encrypted_weights = ts.ckks_vector(context, global_weights)
encrypted_intercept = ts.ckks_vector(context, [global_intercept])
encrypted_new_X = [ts.ckks_vector(context, row) for row in new_X]

predictions = []
for x_enc in encrypted_new_X:
    pred = x_enc.dot(encrypted_weights) + encrypted_intercept
    predictions.append(1 if pred.decrypt()[0] > 0.5 else 0)

print("Predictions for new dataset:", predictions)

# --- Distribution Analysis ---
print(f"Prediction distribution: {predictions.count(0)} zeros, {predictions.count(1)} ones")
print(f"Training set distribution: {len(y) - sum(y)} zeros, {sum(y)} ones")

# --- High-Risk Case Detection ---
high_risk_cases = new_data[
    (new_data["Glucose"] > 180) | 
    (new_data["BMI"] > 30)
]
if not high_risk_cases.empty:
    print("Potential high-risk cases:")
    print(high_risk_cases)
else:
    print("No high-risk cases detected")