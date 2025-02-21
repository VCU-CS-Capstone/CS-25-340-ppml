import tenseal as ts
import pandas as pd
import numpy as np
import pickle
from sklearn.linear_model import LogisticRegression
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

# Federated Training (Run Once, Then Save Model)
model_file = "plaintext_model.pkl"
try:
    # Try to load pre-trained plaintext model
    with open(model_file, "rb") as f:
        global_weights, global_intercept = pickle.load(f)
    print("Loaded pre-trained model.")
except FileNotFoundError:
    print("No pre-trained model found. Training a new one...")
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
    
    # Save plaintext model weights
    with open(model_file, "wb") as f:
        pickle.dump((global_weights, global_intercept), f)
    print("Saved trained model.")

# Encrypt the model on load
encrypted_global_weights = ts.ckks_vector(context, global_weights)
encrypted_global_intercept = ts.ckks_vector(context, [global_intercept])

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
