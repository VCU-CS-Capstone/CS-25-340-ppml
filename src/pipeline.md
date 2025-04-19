# **Pipeline Documentation**  
**Last Updated:** April 18, 2025  
**Author:** Bryan Soerjanto  

---

## **1. Overview**  
This pipeline describes the workflow for:  
1. **Training a privacy-preserving machine learning (PPML) model** on real or synthetic diabetes data.  
2. **Encrypting user data using homomorphic encryption (CKKS)**.  
3. **Running inference on encrypted data** using the trained model.  
4. **Decrypting predictions** on the client side for results.  

---

## **2. Pipeline Steps**  

### **Step 1: Obtain Real Dataset (NHANES or Pima)**
- **Source:** Use either the [Pima Indians Diabetes Dataset](https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database) or a real-world cleaned NHANES dataset.  
- **Storage:** Place it in `./data/raw/`  
- **Example File:** `./data/raw/nhanes_diabetes_cleaned.csv`

### **Step 2: Train the Model**
- **Script:** `./model/train_model.py`  
- **Input:** Cleaned dataset (e.g., `./data/raw/nhanes_diabetes_cleaned.csv`)  
- **Output:**  
  - Trained model (`./model/trained_model.pkl`)  
  - Normalization & transformation parameters (`./model/params/params.pkl`)  
  - CKKS context (`./model/params/context.ckks`)  
  - Training metrics (`train_mcc.txt`, optional)  

#### **Command:**
```sh
python ./model/train_model.py 
```

### **Step 3: Encrypt User Data**
- **Script:** `./model/prepare_and_encrypt_data.py`  
- **Input:**  
  - Normalized user data (`./data/user_data.csv`)  
  - Parameters (`params.pkl`)  
- **Output:**  
  - Encrypted batch: `./data/encrypted_user_data.pkl`

#### **Command:**
```sh
python ./model/prepare_and_encrypt_data.py
```

### **Step 4: Run Encrypted Inference**
- **Script:** `./model/inference.py`  
- **Input:**  
  - Encrypted data file (`encrypted_user_data.pkl`)  
  - Model weights and CKKS context  
- **Output:**  
  - Encrypted predictions (`./data/encrypted_predictions.pkl`)  

#### **Command:**
```sh
python ./model/inference.py
```

### **Step 5: Decrypt Predictions**
- **Script:** `./model/decrypt_output.py`  
- **Input:**  
  - Encrypted predictions (`./data/encrypted_predictions.pkl`)  
  - CKKS context (with secret key)  
- **Output:**  
  - CSV with predictions and scores: `./model/predictions.csv`

#### **Command:**
```sh
python ./model/decrypt_output.py
```

---

## **3. Pipeline Diagram**  
```mermaid
graph TD
    A[Real Diabetes Dataset] --> B[Train Model]
    B -->|Save| C[trained_model.pkl + params.pkl + context.ckks]
    D[User Data (CSV)] --> E[Prepare & Encrypt Data]
    E --> F[Encrypted User Data]
    F --> G[Encrypted Inference]
    G --> H[Encrypted Predictions]
    H --> I[Decrypt Predictions]
    I --> J[Decrypted CSV Results]

    subgraph Training
        B
    end

    subgraph Inference Flow
        E --> F --> G --> H --> I --> J
    end
```

---

## **4. Key Considerations**  
✅ **PPML Architecture:** Combines logistic regression, federated training, and homomorphic encryption (CKKS).  
✅ **Accuracy Evaluation:** Decrypted predictions are compared to real `Outcome` labels when available.  
✅ **Security:** The model never sees raw data — all predictions are made on encrypted inputs.

---

## **5. Future Improvements**  
- Support for additional encryption schemes (e.g., BFV or FHEW)  
- Add support for polynomial/logistic regression inference via polynomial approximation  
- Enable secure model updates with encrypted gradients (full PPFL)  
- Add AUC/F1 metrics on decrypted results

---

## **6. How to Run Full Pipeline**  
```bash
# 1. Train the model
python ./model/train_model.py

# 2. Encrypt user data
python ./model/prepare_and_encrypt_data.py

# 3. Run encrypted inference
python ./model/inference.py

# 4. Decrypt the output
python ./model/decrypt_output.py
```

---
