import tenseal as ts
import pandas as pd
import numpy as np
import pickle
import os
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import matthews_corrcoef
from sklearn.preprocessing import PolynomialFeatures

# Load training data
data = pd.read_csv("./data/diabetes.csv")
X = data.drop(columns=["Outcome"]).values
y = data["Outcome"].values

# Normalize data
X_mean = np.mean(X, axis=0)
X_std = np.std(X, axis=0)
X = (X - X_mean) / X_std

# Polynomial expansion
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)

# Split into federated clients
n_clients = 5
X_clients = np.array_split(X_poly, n_clients)
y_clients = np.array_split(y, n_clients)

# Federated Training
model_file = "./model/trained_model.pkl"
if os.path.exists(model_file):
    try:
        with open(model_file, "rb") as f:
            model = f.read()
        global_weights, global_intercept = pickle.loads(model)
        print("Loaded pre-trained model.")
    except (pickle.UnpicklingError, Exception):
        print("Invalid model file. Training new model...")
        os.remove(model_file)
        train_new_model = True
    else:
        train_new_model = False
else:
    print("No pre-trained model found. Training a new one...")
    train_new_model = True

if train_new_model:
    global_weights = np.zeros(X_poly.shape[1])
    global_intercept = 0
    num_epochs = 70

    for epoch in range(num_epochs):
        weight_updates = []
        intercept_updates = []

        for X_client, y_client in zip(X_clients, y_clients):
            model = LogisticRegression(max_iter=1000)
            model.fit(X_client, y_client)

            weights = model.coef_[0]
            intercept = model.intercept_[0]

            weight_updates.append(weights)
            intercept_updates.append(intercept)

        global_weights = np.mean(weight_updates, axis=0)
        global_intercept = np.mean(intercept_updates)

    # Save model
    with open(model_file, "wb") as f:
        model = pickle.dumps((global_weights, global_intercept))
        f.write(model)
    print("Saved trained model.")

    # Save all params into one pickle bundle
    model_bundle = {
        "mean": X_mean,
        "std": X_std,
        "weights": global_weights,
        "intercept": global_intercept,
        "poly": poly
    }

    os.makedirs('./model/params', exist_ok=True)
    with open('./model/params/params.pkl', 'wb') as f:
        pickle.dump(model_bundle, f)

# Training Evaluation
train_preds = (X_poly @ global_weights + global_intercept) > 0.5
train_mcc = matthews_corrcoef(y, train_preds)
print(f"MCC on training set: {train_mcc:.4f}")