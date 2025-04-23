# NHANES Diabetes Dataset (Cleaned & Combined)

This folder contains the cleaned and combined diabetes dataset derived from the **National Health and Nutrition Examination Survey (NHANES)** for use in our Privacy‑Preserving Machine Learning (PPML) pipeline. The final CSV mirrors the 8‑feature schema of the Pima Indians Diabetes Dataset but incorporates real NHANES measurements and supplements missing fields with synthetic data where necessary.

---

## 📖 Context

NHANES is a continuous survey program by the U.S. Centers for Disease Control and Prevention (CDC) that assesses health and nutritional status across a nationally representative sample. It collects laboratory, examination, and questionnaire data for thousands of participants every two years.

In this project, we leverage NHANES as **"user data"** to demonstrate homomorphic-encrypted inference. Compared to the classical Pima dataset (768 records), NHANES provides a larger, more diverse sample—ideal for testing encrypted inference under real-world variability.

---

## 🎯 Purpose & Usage

- **Encrypted Inference:** Clients encrypt their NHANES feature vectors and upload ciphertexts to the server. The server runs inference under TenSEAL's CKKS HE scheme and returns encrypted predictions.
- **Model Evaluation:** Decrypted predictions are compared against true `Outcome` labels to compute accuracy, MCC, and class-conditional error rates.

---

## 🔗 Data Extraction & Combination

We merge the following NHANES modules (2015–2016 cycle) by participant ID (`SEQN`):

| Source File     | NHANES Variable | Renamed Feature        |
|-----------------|-----------------|------------------------|
| `glucose.xpt`  | `LBXGLU`        | `Glucose`              |
| `blood_pressure.xpt`     | `BPXOSY1`       | `BloodPressure`        |
| `insulin.xpt`     | `LBXIN`         | `Insulin`              |
| `body_measurements.xpt`     | `BMXBMI`        | `BMI`                  |
| `demographics.xpt`    | `RIDAGEYR`      | `Age`                  |
| `diabetes_q.xpt`     | `DIQ010`        | `Outcome` |
| `pregnancies.xpt`     | `RHD167`        | `Pregnancies`          |

**Combination Steps:**
1. **Load & Select:** Read each file using `pandas.read_sas()`, selecting `SEQN` and the target variable.
2. **Clean & Map:**
   - Drop or fill missing values for numeric features.  
   - Map `Outcome` codes (1 → 1, 2 → 0).  
3. **Pregnancies Handling:**  
   - Cap values > 5 at `5` since 5 indicates 5 or more.
4. **Merge:** Inner join all tables on `SEQN` to retain complete records.

---

## 🧪 Synthetic Data Integration

NHANES lacks two Pima features, so we simulate:

| Feature                      | Synthetic Strategy                                            |
|------------------------------|---------------------------------------------------------------|
| **SkinThickness**            | `Normal(mean=20, σ=8)`, clipped to `[5, 50]`                  |
| **DiabetesPedigreeFunction** | `Normal(mean=0.5, σ=0.2)`, clipped to `[0, 2.5]`               |

These synthetic values ensure the dataset conforms to the 8‑feature format required by our Pima‑trained models.

---

## 📊 Final Schema & Output

The resulting `nhanes_diabetes_cleaned.csv` has the following columns in order:
```
Pregnancies, Glucose, BloodPressure, SkinThickness,
Insulin, BMI, DiabetesPedigreeFunction, Age, Outcome
```

Use this CSV for encrypted inference, model benchmarking, and further PPML experiments.

---

## 🛠️ Regeneration Instructions

1. Place NHANES `.xpt` source files in this directory.  
2. Enter `nhanes_dataset` folder with `cd src/data/nhanes_dataset`
2. Run:
   ```sh
   python3 combine_nhanes_datasets.py
   ```
3. Output: `nhanes_diabetes_cleaned.csv` ready for use.

---

## 📚 References

- NHANES Data Access: https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?Cycle=2021-2023

