import json
import tenseal as ts
import pandas as pd

# param paths
norm_path = './model/params/norm_param.json'
context_path = './model/params/tenseal_context.tenseal'
data_path = './data/raw/user_data.csv'

# load normalization parameter
try:
    with open(norm_path, 'r') as f:
        norm = json.load(f)
        X = norm['mean']
        std = norm['std']
        global_weights = norm['global_weights']
        global_intercept = norm['global_intercept']
        
except FileNotFoundError:
    print('param file not found')
    
# load ckks context
try:
    with open(context_path, 'rb') as f:
        context = ts.context_from(f.read())
except FileNotFoundError:
    print('context file not found')
    
user_data = pd.read_csv(data_path)
if "Outcome" in user_data.columns:
    data = user_data.drop(columns=["Outcome"]).values
    print("Outcome column ignored")
    
else:
    data = user_data.values
    
# Verify feature alignment

#if data.shape[1] != X.shape[1]:
#    raise ValueError(f"Expected {X.shape[1]} features, got {data.shape[1]}")

data = (data - X) / std

# Encrypt user data
encrypted_data = [ts.ckks_vector(context, row) for row in data]
encrypted_weights = ts.ckks_vector(context, global_weights)
encrypted_intercept = ts.ckks_vector(context, [global_intercept])
# encrypted_new_X = [ts.ckks_vector(context, row) for row in X]

# Save encrypted data to file
try:
    with open('./data/raw/encrypted_user_data', 'wb') as f:
        for encrypted_vector in encrypted_data:
            f.write(encrypted_vector.serialize())
    print(f"User data encrypted")
except Exception as e:
    print(f"Error saving encrypted user data: {e}")