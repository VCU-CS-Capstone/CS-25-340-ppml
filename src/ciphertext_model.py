import tenseal as ts
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Load dataset
data = pd.read_csv("diabetes.csv")
X = data.drop(columns=["Outcome"]).values
y = data["Outcome"].values

# Normalize data to prevent scale explosion
X = X / np.max(X, axis=0)

# Train the model in plaintext
kf = KFold(n_splits=5, shuffle=True, random_state=42)
accuracies = []

for train_index, test_index in kf.split(X):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]
    
    # Train Logistic Regression
    model = LogisticRegression()
    model.fit(X_train, y_train)
    
    # Encrypt trained model weights
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60]
    )
    context.global_scale = 2**40
    context.generate_galois_keys()
    context.generate_relin_keys()
    
    encrypted_weights = ts.ckks_vector(context, model.coef_[0].tolist())
    encrypted_intercept = ts.ckks_vector(context, [model.intercept_[0]])
    
    # Encrypt test data
    encrypted_X_test = [ts.ckks_vector(context, row.tolist()) for row in X_test]
    
    # Perform encrypted inference
    correct = 0
    for x_enc, y_true in zip(encrypted_X_test, y_test):
        pred = x_enc.dot(encrypted_weights) + encrypted_intercept  # Encrypted prediction
        pred_label = 1 if pred.decrypt()[0] > 0.5 else 0  # Decrypt only the final result
        if pred_label == y_true:
            correct += 1
    
    acc = correct / len(y_test)
    accuracies.append(acc)

# Print Accuracy
print(f"Mean Accuracy: {np.mean(accuracies):.4f}")
