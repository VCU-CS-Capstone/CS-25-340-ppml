from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import uvicorn
import os
import subprocess

app = FastAPI()

MODEL_DIR   = "./model"
DATA_DIR    = "./data"
MODEL_FILE  = os.path.join(MODEL_DIR, "trained_model.pkl")
PARAMS_PATH = os.path.join(MODEL_DIR, "params.pkl")


def ensure_model():
    os.makedirs(MODEL_DIR, exist_ok=True)
    # If the model or params bundle is missing, retrain
    if not os.path.exists(MODEL_FILE) or not os.path.exists(PARAMS_PATH):
        print("⏳ Training model and generating params bundle...")
        result = subprocess.run(
            ["python", "./model/train.py"],  # or "train_model.py" if that's your script name
            cwd='.',
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Training failed:\n{result.stderr}")
        print("✅ Training complete; model.pkl and params.pkl are in place.")


# Serve both /params and /params/ to avoid trailing-slash issues
for route in ("/params", "/params/"):
    @app.get(route)
    async def get_params():
        ensure_model()
        if not os.path.exists(PARAMS_PATH):
            raise HTTPException(500, detail="Params bundle not found")
        return FileResponse(
            PARAMS_PATH,
            media_type="application/octet-stream",
            filename="params.pkl"
        )


@app.post("/predict/")
async def predict(encrypted: UploadFile = File(...)):
    ensure_model()

    # 1) save incoming encrypted_user_data.pkl
    os.makedirs(DATA_DIR, exist_ok=True)
    enc_in = os.path.join(DATA_DIR, "encrypted_user_data.pkl")
    with open(enc_in, "wb") as f:
        f.write(await encrypted.read())

    # 2) run inference.py
    result = subprocess.run(
        ["python", "inference.py"],
        cwd=MODEL_DIR,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise HTTPException(500, detail=f"Inference failed:\n{result.stderr}")

    # 3) return the encrypted predictions bundle
    enc_out = os.path.join(DATA_DIR, "encrypted_predictions.pkl")
    if not os.path.exists(enc_out):
        raise HTTPException(500, detail="Encrypted predictions not found")
    return FileResponse(
        enc_out,
        media_type="application/octet-stream",
        filename="encrypted_predictions.pkl"
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
