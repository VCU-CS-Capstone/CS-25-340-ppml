import pandas as pd

# Load encrypted data
user_data = "./data/encrypted_user_data"
data = pd.read_csv(user_data)

if "Outcome" in data.columns:
    print('Ignoring "Outcome" column')
    x = data.drop(columns=["Outcome"]).values
else:
    x = data.values
