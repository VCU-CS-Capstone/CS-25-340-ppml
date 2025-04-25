import os
import shutil

def safe_remove(path):
    if os.path.isfile(path):
        os.remove(path)
        print(f"Removed file: {path}")
    elif os.path.isdir(path):
        shutil.rmtree(path)
        print(f"Removed directory: {path}")

# Client-side cleanup
safe_remove("./data/encrypted_user_data.pkl")
safe_remove("./data/predictions.csv")
safe_remove("./params")
safe_remove("./encrypted_predictions.pkl")

# Server-side cleanup
safe_remove("../server/output")
safe_remove("../server/trained_model.pkl")