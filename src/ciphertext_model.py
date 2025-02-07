import tenseal as ts
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Step 1: Setup CKKS context
context = ts.context(ts.SCHEME_TYPE.CKKS, 8192, coeff_mod_bit_sizes=[60, 40, 40, 60])
context.generate_galois_keys()
context.global_scale = 2**40

# Step 2: Encrypt the training data

# Load preprocessed data
df = pd.read_csv("./data/normalized_med_data.csv")

# Separate features and target
X = df.drop(columns=["Disease"]).values
y = df["Disease"].values

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

enc_X_train = [ts.ckks_vector(context, x) for x in X_train]
enc_y_train = [ts.ckks_vector(context, [y]) for y in y_train]

# Step 3: Initialize encrypted weights and bias
enc_weights = [ts.ckks_vector(context, [0.0]) for _ in range(X_train.shape[1])]
enc_bias = ts.ckks_vector(context, [0.0])

# Step 4: Homomorphic training (gradient descent)
learning_rate = 0.01
num_epochs = 10

for epoch in range(num_epochs):
    for x, y in zip(enc_X_train, enc_y_train):
        # Forward pass: Compute encrypted logit
        logit = enc_bias
        for i in range(len(enc_weights)):
            logit = logit + enc_weights[i] * x[i]
        
        # Compute error (y - logit)
        error = y - logit
        
        # Backpropagation: Update weights and bias
        for i in range(len(enc_weights)):
            enc_weights[i] = enc_weights[i] + learning_rate * error * x[i]
        enc_bias = enc_bias + learning_rate * error

# Step 5: Decrypt the final model
decrypted_weights = [w.decrypt()[0] for w in enc_weights]
decrypted_bias = enc_bias.decrypt()[0]

print("Decrypted Weights:", decrypted_weights)
print("Decrypted Bias:", decrypted_bias)

# Step 6: Evaluate the encrypted model
def predict(X, weights, bias):
    return [1 if (np.dot(x, weights) + bias) > 0 else 0 for x in X]

predictions = predict(X_test, decrypted_weights, decrypted_bias)
accuracy = accuracy_score(y_test, predictions)
print(f"Encrypted Model Accuracy: {accuracy:.2f}")