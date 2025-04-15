import json
import tenseal as ts
import pandas as pd

# param paths
norm_path = './model/params/norm_param.json'
context_path = './model/params/tenseal_context.tenseal'
data_path = './data/user_data.csv'

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
    
# CKKS encrpytion context
context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,
    coeff_mod_bit_sizes=[60, 40, 40, 60]
)
context.global_scale = 2**40
context.generate_galois_keys()
context.generate_relin_keys()

# Save context to file
with open("./model/params/tenseal_context.tenseal", "wb") as f:
    f.write(context.serialize(save_public_key=True, save_secret_key=True))    
    
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
    with open('./data/encrypted_user_data', 'wb') as f:
        for encrypted_vector in encrypted_data:
            f.write(encrypted_vector.serialize())
    print(f"User data encrypted")
except Exception as e:
    print(f"Error saving encrypted user data: {e}")