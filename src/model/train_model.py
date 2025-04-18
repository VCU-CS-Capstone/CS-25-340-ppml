import tenseal as ts
import pandas as pd
import numpy as np
import pickle
import os
from cryptography.fernet import Fernet, InvalidToken
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import matthews_corrcoef
import json

# Load training data
data = pd.read_csv("../data/diabetes.csv")
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
    
# Federated Training with DP
model_file = "./model/trained_model.pkl"
if os.path.exists(model_file):
    try:
        with open(model_file, "rb") as f:
            model = f.read()
        global_weights, global_intercept = pickle.loads(model)
        print("Loaded pre-trained model.")
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
    # Differential Privacy Parameters
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
        
    # Save model
    with open(model_file, "wb") as f:
        model = pickle.dumps((global_weights, global_intercept))
        f.write(model)
    print("Saved trained model.")
    
    # Save parameters
    norm_param = {
        'mean': X_mean.tolist(),
        'std': X_std.tolist(),
        'global_weights': global_weights.tolist(),
        'global_intercept': global_intercept   
    }

    os.makedirs('./model/params', exist_ok=True)
    json_obj = json.dumps(norm_param, indent=4)
    with open('./model/params/norm_param.json', 'w') as f:
        f.write(json_obj)
    
# Training Evaluation
train_preds = (X @ global_weights + global_intercept) > 0.5
train_mcc = matthews_corrcoef(y, train_preds)
print(f"MCC on training set: {train_mcc:.4f}")