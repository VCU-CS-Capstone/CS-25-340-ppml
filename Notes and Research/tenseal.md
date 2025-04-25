# TenSEAL

TenSEAL is an open‑source Python library built on Microsoft SEAL that makes it easy to perform homomorphic encryption (HE) in machine learning workflows. It provides high‑level abstractions for encrypting tensors (vectors/matrices) and performing common linear algebra operations on encrypted data.

---

## 1. Key Features

- **CKKS Scheme Support**  
  - Approximate arithmetic on real (floating‑point) data  
  - Ideal for ML tasks: dot products, matrix multiplications, aggregations  

- **Tensor APIs**  
  - `CKKSVector` for 1D arrays  
  - `CKKSMatrix` for 2D arrays (batch operations)  
  - Element‑wise operations, dot products, and scalar multiplication  

- **Key Management**  
  - Easy context creation: poly modulus, coefficient bits, scale  
  - Built‑in Galois & relinearization key generation  
  - Serialization / deserialization of context and encrypted tensors  

- **Interoperability**  
  - Integrates with PyTorch and NumPy arrays  
  - Can be combined with PySyft for MPC + HE hybrid workflows  

---

## 2. Installation

```bash
pip install tenseal
```

> Requires a C++ compiler and CMake to build the underlying Microsoft SEAL library.

---

## 3. Basic Usage

### 3.1 Creating an Encryption Context

```python
import tenseal as ts

# CKKS context with 8192 poly_modulus and 40‑bit scale
ctx = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,
    coeff_mod_bit_sizes=[60, 40, 40, 60]
)
ctx.global_scale = 2**40
ctx.generate_galois_keys()
ctx.generate_relin_keys()
```

### 3.2 Encrypting Data

```python
import numpy as np

data = np.array([1.2, 3.4, 5.6], dtype=float)
enc_vec = ts.ckks_vector(ctx, data)
```

### 3.3 Performing Encrypted Computations

```python
# Encrypted dot product
w = ts.ckks_vector(ctx, [0.5, 1.0, -0.3])
enc_result = enc_vec.dot(w)  # still encrypted
```

### 3.4 Decrypting Results

```python
result = enc_result.decrypt()  # a list of floats
```

---

## 4. Tensor Operations

- **Element‑wise addition / subtraction**: `enc_a + enc_b`  
- **Element‑wise multiplication**: `enc_a * enc_b`  
- **Matrix‑vector product**: `enc_matrix.mm(enc_vector)`  
- **Scalar operations**: `enc_vec * 3.14`  

---

## 5. Integration Patterns

- **Client‑side encryption**: Clients load the public context, encrypt their feature tensors, and send to server.  
- **Server‑side inference**: Server loads encrypted tensors, performs HE‑compatible model operations, and returns encrypted predictions.  
- **Decryption**: Client uses secret key embedded in context to decrypt results locally.

---

## 6. Performance Considerations

- **Batching / packing**: Leverage vector size = poly_modulus_degree/2 to encrypt many values in one ciphertext.  
- **Key-switching overhead**: Generating Galois & relin keys is expensive—do it once per context.  
- **Operation depth**: CKKS supports limited multiplicative depth before needing rescaling or bootstrapping.

---

## 7. Limitations & Tips

- **No native non‑linear activation**: Sigmoid/ReLU must be approximated as polynomials.  
- **Approximation error**: CKKS is approximate—track scale & rescale between operations to control noise growth.  
- **Context security**: Don’t share the secret key; only serialize the public context for clients.

---

## 8. Resources

- **GitHub**: https://github.com/OpenMined/TenSEAL  
- **Tutorials**: Official TenSEAL examples repository  
- **SEAL Docs**: Microsoft SEAL library documentation for deeper understanding

---