import pandas as pd

# Load
user_data = "./data/raw/user_data.csv"
data = pd.read_csv(user_data)

if "Outcome" in data.columns:
    print('Ignoring "Outcome" column')
    x = data.drop(columns=["Outcome"]).values
else:
    x = data.values
