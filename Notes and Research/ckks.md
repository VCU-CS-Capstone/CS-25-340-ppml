# CKKS (Cheon-Kim-Kim-Song) Scheme

The CKKS scheme is a **fully homomorphic encryption** (FHE) variant designed for **approximate arithmetic on real (floating‑point) data**, making it especially suitable for privacy‑preserving machine learning and data analytics.

---

## 1. Key Characteristics

- **Approximate Encoding**  
  - Encodes real numbers as complex values in the polynomial ring.  
  - Supports **addition** and **multiplication** with controlled precision loss.
- **Scale Management**  
  - Each ciphertext carries a fixed **scale** (e.g., 2⁴⁰) to manage precision.  
  - **Rescaling** (divide-by-scale) reduces noise and adjusts scale after multiplications.
- **Batching / Packing**  
  - Leverages **SIMD**: Packs multiple plaintext slots per ciphertext (half the polynomial degree).  
  - Enables **vectorized operations** (e.g., dot products) in one homomorphic call.

---

## 2. Encryption Context

1. **Polynomial Modulus Degree** (`N`)  
   - Typical values: 4096, 8192, 16384  
   - Ciphertext size ∝ N; security level increases with N.
2. **Coefficient Modulus**  
   - Chain of primes defining **bit‑length** at each level.  
   - Determines **noise budget** and multiplicative depth.
3. **Global Scale**  
   - Chosen as power of two (e.g., 2²⁰, 2⁴⁰).  
   - Should match plaintext scaling before encryption.

Example Context Creation:
```python
import tenseal as ts
ctx = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,
    coeff_mod_bit_sizes=[60, 40, 40, 60]
)
ctx.global_scale = 2**40
ctx.generate_galois_keys()
ctx.generate_relin_keys()
```

---

## 3. Core Operations

| Operation               | Method                         | Notes                                      |
|-------------------------|--------------------------------|--------------------------------------------|
| **Addition**            | `ct1 + ct2`                    | Adds two encrypted vectors slot‑wise       |
| **Subtraction**         | `ct1 - ct2`                    | Subtracts ciphertexts                      |
| **Scalar Multiplication** | `ct * scalar`                 | Multiply each slot by a plaintext constant |
| **Element‑wise Multiplication** | `ct1 * ct2`            | Requires **relinearization** after product |
| **Dot Product**         | `ct1.dot(ct2)`                 | Efficient sum of slot-wise products        |
| **Rotation**            | `ct.rotate(n)`                 | Shift slots by `n`, uses **Galois keys**   |
| **Rescale**             | `ct.rescale()`                 | Reduces noise and scale after multiplication |

---

## 4. Noise and Precision Management

- **Noise Budget**  
  - Each operation consumes part of the noise budget.  
  - **Rescaling** and **relinearization** free up budget.
- **Precision Loss**  
  - Multiple multiplications increase rounding errors.  
  - Choose **polynomial degree** and **scale** to balance precision vs. performance.

---

## 5. Performance & Limitations

- **Multiplicative Depth**  
  - Limited by coefficient modulus chain length.  
  - Deeper circuits require larger parameters or **bootstrapping**.
- **Bootstrapping**  
  - Refreshes ciphertext to full noise budget.  
  - Computationally expensive, rarely used in practice for CKKS-based ML.
- **Memory & Compute**  
  - Ciphertexts are large (MBs); operations are 10³–10⁴× slower than plaintext.

---

## 6. Use Cases in PPML

- **Encrypted Inference**: Compute linear layers, dot products, and vector additions on encrypted feature vectors.  
- **Secure Aggregation**: Average encrypted gradients or weight updates in federated learning without decryption.  
- **Private Statistics**: Sum, mean, and variance computations on encrypted datasets.

---

## 7. Best Practices

1. **Parameter Selection**: Tailor polynomial degree and coefficient modulus to required depth.  
2. **Scale Alignment**: Ensure plaintext data is scaled to match `ctx.global_scale`.  
3. **Key Management**: Keep **secret key** private; distribute **public context** only.  
4. **Batching Strategy**: Pack data to maximize vector operations efficiency.  
5. **Error Monitoring**: After operations, check **approximate result** against known bounds if possible.

---