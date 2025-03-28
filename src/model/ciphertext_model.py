import tenseal as ts
import pandas as pd
import numpy as np
import pickle
import os
from cryptography.fernet import Fernet, InvalidToken
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import matthews_corrcoef
from sklearn.model_selection import train_test_split

# Load dataset
data = pd.read_csv("diabetes.csv")
X = data.drop(columns=["Outcome"]).values
y = data["Outcome"].values

# Normalize data using training set statistics (mean & std)
X_mean = np.mean(X, axis=0)
X_std = np.std(X, axis=0)
X = (X - X_mean) / X_std  # Standardization

# Split dataset into federated clients (e.g., 5 clients for better distribution)
n_clients = 5
X_clients = np.array_split(X, n_clients)
y_clients = np.array_split(y, n_clients)

# Initialize TenSEAL context
context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,
    coeff_mod_bit_sizes=[60, 40, 40, 60]
)
context.global_scale = 2**40
context.generate_galois_keys()
context.generate_relin_keys()

# Secure AES Encryption for Model Storage
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

model_file = "encrypted_model.pkl"

# Federated Training (Run Once, Then Save Model)
if os.path.exists(model_file):
    try:
        # Try to load and decrypt pre-trained model
        with open(model_file, "rb") as f:
            encrypted_model = f.read()
        decrypted_model = cipher.decrypt(encrypted_model)
        global_weights, global_intercept = pickle.loads(decrypted_model)
        print("Loaded encrypted pre-trained model.")
        
        # Immediately encrypt into TenSEAL to prevent exposure
        encrypted_global_weights = ts.ckks_vector(context, global_weights)
        encrypted_global_intercept = ts.ckks_vector(context, [global_intercept])
        
        # Wipe plaintext variables
        del global_weights, global_intercept
    except (pickle.UnpicklingError, InvalidToken):
        print("Invalid or corrupt model file. Training a new one...")
        os.remove(model_file)  # Delete the corrupt model file
        train_new_model = True
    else:
        train_new_model = False
else:
    print("No pre-trained model found. Training a new one...")
    train_new_model = True

if train_new_model:
    global_weights = np.zeros(X.shape[1])
    global_intercept = 0
    num_epochs = 20  # Increased epochs for better training
    learning_rate = 0.01

    for epoch in range(num_epochs):
        weight_updates = []
        intercept_updates = []
        
        for X_client, y_client in zip(X_clients, y_clients):
            model = LogisticRegression()
            model.fit(X_client, y_client)
            
            # Store model updates
            weight_updates.append(model.coef_[0].tolist())
            intercept_updates.append(model.intercept_[0])
        
        # Aggregate model updates
        avg_weights = np.mean(weight_updates, axis=0)
        avg_intercept = np.mean(intercept_updates)
        
        # Update global model
        global_weights = avg_weights
        global_intercept = avg_intercept
    
    # Encrypt and save model weights
    serialized_model = pickle.dumps((global_weights, global_intercept))
    encrypted_model = cipher.encrypt(serialized_model)
    with open(model_file, "wb") as f:
        f.write(encrypted_model)
    print("Saved encrypted trained model.")
    
    # Immediately encrypt into TenSEAL to prevent exposure
    encrypted_global_weights = ts.ckks_vector(context, global_weights)
    encrypted_global_intercept = ts.ckks_vector(context, [global_intercept])
    
    # Wipe plaintext variables
    del global_weights, global_intercept

# ---------------- TRAINING SET MCC ----------------
# Compute MCC on training set
train_predictions = (X @ encrypted_global_weights.decrypt() + encrypted_global_intercept.decrypt()[0]) > 0.5
train_mcc = matthews_corrcoef(y, train_predictions)
print(f"MCC on training set: {train_mcc:.4f}")

# ---------------- PREDICTION ON NEW DATASET ----------------
# Load new dataset
new_data = pd.read_csv("new_data.csv")

# Check if labels exist in new_data
if "Outcome" in new_data.columns:
    y_true = new_data["Outcome"].values
    new_X = new_data.drop(columns=["Outcome"]).values
    labels_available = True
else:
    print("Warning: No 'Outcome' column found in new_data.csv. Skipping MCC calculation.")
    new_X = new_data.values  # Use all columns if labels are missing
    labels_available = False

# Normalize new data using training mean & std (instead of its own)
new_X = (new_X - X_mean) / X_std

# Encrypt new input data
encrypted_new_X = [ts.ckks_vector(context, row.tolist()) for row in new_X]

# Perform encrypted inference on new dataset
predictions = []
for x_enc in encrypted_new_X:
    pred = x_enc.dot(encrypted_global_weights) + encrypted_global_intercept  # Encrypted prediction
    decrypted_pred = 1 if pred.decrypt()[0] > 0.5 else 0  # Decrypt final prediction
    predictions.append(decrypted_pred)

# Print predictions
print("Predictions for new dataset:", predictions)

# Analyze prediction distribution
num_ones = sum(predictions)
num_zeros = len(predictions) - num_ones
print(f"Prediction distribution: {num_zeros} zeros, {num_ones} ones")

# Compare prediction proportion to training set
train_ones = sum(y)
train_zeros = len(y) - train_ones
print(f"Training set distribution: {train_zeros} zeros, {train_ones} ones")

# Identify high-risk cases (Glucose > 180 & BMI > 30 as risk factors)
high_risk_cases = new_data[(new_data["Glucose"] > 180) & (new_data["BMI"] > 30)]
if not high_risk_cases.empty:
    print("Potential high-risk cases:")
    print(high_risk_cases)
else:
    print("No obvious high-risk cases detected based on Glucose & BMI thresholds.")