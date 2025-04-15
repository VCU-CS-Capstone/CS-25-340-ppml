import pandas as pd
import numpy as np
from sklearn.datasets import make_classification
from sklearn.preprocessing import MinMaxScaler

def generate_diabetes_dataset(num_samples=1000):
    # Base statistical parameters (inspired by real diabetes data)
    params = {
        'Pregnancies': {'mean': 3.8, 'std': 3.4, 'min': 0, 'max': 17},
        'Glucose': {'mean': 120, 'std': 32, 'min': 40, 'max': 200},
        'BloodPressure': {'mean': 69, 'std': 19, 'min': 40, 'max': 122},
        'SkinThickness': {'mean': 20, 'std': 16, 'min': 0, 'max': 99},
        'Insulin': {'mean': 80, 'std': 115, 'min': 0, 'max': 850},
        'BMI': {'mean': 32, 'std': 8, 'min': 0, 'max': 68},
        'DiabetesPedigreeFunction': {'mean': 0.5, 'std': 0.3, 'min': 0.08, 'max': 2.5},
        'Age': {'mean': 33, 'std': 12, 'min': 21, 'max': 81}
    }
    
    # Generate correlated features with realistic distributions
    X, y = make_classification(
        n_samples=num_samples,
        n_features=8,
        n_informative=6,
        n_redundant=2,
        weights=[0.65, 0.35],  # 35% diabetes prevalence
        random_state=42
    )
    
    # Scale and transform to match real distributions
    data = pd.DataFrame(X, columns=params.keys())
    for col in params:
        col_params = params[col]
        # Transform to normal distribution with target stats
        data[col] = np.clip(
            data[col] * col_params['std'] + col_params['mean'],
            col_params['min'],
            col_params['max']
        )
        # Round appropriate columns to integers
        if col in ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'Age']:
            data[col] = data[col].round().astype(int)
    
    # Make some values 0 to mimic missing data (common in real dataset)
    for col in ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']:
        data.loc[data.sample(frac=0.05, random_state=42).index, col] = 0
    
    # Add outcome column
    data['Outcome'] = y
    
    # Post-processing for clinical realism
    data['Glucose'] = data['Glucose'].apply(lambda x: max(x, 40))  # Minimum plausible glucose
    data['BMI'] = data['BMI'].apply(lambda x: max(x, 18))  # Minimum plausible BMI
    
    # Truncation
    data['DiabetesPedigreeFunction'] = data['DiabetesPedigreeFunction'].apply(lambda x: np.floor(x * 1000) / 1000)  # Truncate to 3 decimal places
    data['BMI'] = data['BMI'].apply(lambda x: np.floor(x * 10) / 10)  # Truncate to 1 decimal place
    
    # Ensure some clinical correlations
    data.loc[data['Glucose'] > 140, 'Outcome'] = 1
    data.loc[data['BMI'] > 35, 'Outcome'] = 1
    
    return data

# Generate and save dataset
diabetes_data = generate_diabetes_dataset(50)
diabetes_data.to_csv('./data/user_data.csv', index=False)
print("Generated dataset with distribution:")
print(diabetes_data['Outcome'].value_counts(normalize=True))