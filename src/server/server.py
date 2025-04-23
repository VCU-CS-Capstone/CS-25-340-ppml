from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import uvicorn
import os
import subprocess

app = FastAPI()

# --- Path Configuration ---
BASE_DIR      = os.path.dirname(__file__)
PARAMS_PATH   = os.path.join(BASE_DIR, "output/params.pkl")
CONTEXT_PATH  = os.path.join(BASE_DIR, "output/context_public.ckks")
MODEL_FILE    = os.path.join(BASE_DIR, "trained_model.pkl")
ENCRYPTED_IN  = os.path.join(BASE_DIR, "output/encrypted_user_data.pkl")
ENCRYPTED_OUT = os.path.join(BASE_DIR, "output/encrypted_predictions.pkl")

def ensure_model():
    # If model or parameters are missing, retrain
    if not os.path.exists(MODEL_FILE) or not os.path.exists(PARAMS_PATH):
        print("⏳ Training model and generating params...")
        result = subprocess.run(
            ["python", "train.py"],
            cwd=os.path.join(BASE_DIR),
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Training failed:\n{result.stderr}")
        print("✅ Training complete.")

@app.get("/params")
@app.get("/params/")
async def get_params():
    if not os.path.exists(PARAMS_PATH):
        raise HTTPException(500, detail="params.pkl not found")
    return FileResponse(PARAMS_PATH, media_type="application/octet-stream", filename="params.pkl")

@app.post("/predict/")
async def predict(encrypted: UploadFile = File(...), context: UploadFile = File(...)):
    ensure_model()

    # 1. Save uploaded encrypted data
    with open(ENCRYPTED_IN, "wb") as f:
        f.write(await encrypted.read())

    # 2. Save the client's public context
    with open(CONTEXT_PATH, "wb") as f:
        f.write(await context.read())

    # 3. Run inference
    result = subprocess.run(
        ["python", "inference.py"],
        cwd=os.path.join(BASE_DIR),
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise HTTPException(500, detail=f"Inference failed:\n{result.stderr}")

    # 4. Return encrypted predictions
    if not os.path.exists(ENCRYPTED_OUT):
        raise HTTPException(500, detail="Encrypted predictions not found.")
    return FileResponse(ENCRYPTED_OUT, media_type="application/octet-stream", filename="encrypted_predictions.pkl")

ensure_model()
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
