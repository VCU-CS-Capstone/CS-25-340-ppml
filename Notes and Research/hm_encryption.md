# Homomorphic Encryption

Homomorphic encryption (HE) enables computation on ciphertexts, producing encrypted results that decrypt to the same output as if operations were performed on plaintext. This property is essential for privacy-preserving applications where data must remain confidential.

---

## 1. Basic Workflow

1. **Key Generation**: Generate a public/private key pair.
2. **Encryption**: Encrypt plaintext data with the public key → ciphertext.
3. **Evaluation**: Perform arithmetic operations (addition, multiplication) directly on ciphertexts.
4. **Decryption**: Private key holder decrypts the evaluated ciphertext to retrieve the result.

```text
Enc(m₁) = c₁  Enc(m₂) = c₂
Enc(m₁ + m₂) = c₁ ⊕ c₂   // homomorphic addition
Enc(m₁ ⋅ m₂) = c₁ ⊗ c₂   // homomorphic multiplication
Dec(c_eval) = m_eval
```  

---

## 2. HE Scheme Types

| Scheme       | Operations Supported        | Typical Use Cases                |
|--------------|-----------------------------|----------------------------------|
| **PHE**      | Add _or_ Mul                | Simple summation or product      |
| **SHE**      | Limited depth of both ops   | Fixed-depth polynomial eval      |
| **Leveled HE** | Both ops up to a predefined multiplicative depth | ML inference with known depth    |
| **FHE**      | Unbounded additions & multiplications via bootstrapping | Complex circuits, arbitrary programs |

### 2.1 Partially Homomorphic Encryption (PHE)
- **Addition**: Paillier, BFV without multiplication
- **Multiplication**: RSA, ElGamal

### 2.2 Somewhat & Leveled HE (SHE)
- Fixed-depth circuits; no expensive bootstrapping
- Used when multiplicative depth is known in advance

### 2.3 Fully Homomorphic Encryption (FHE)
- **Bootstrapping**: Refresh ciphertext noise to allow unlimited operations
- Examples: Gentry’s scheme, BGV, CKKS, TFHE

---

## 3. Scheme Components

1. **Plaintext Space**: Ring or vector space where messages live.
2. **Ciphertext Space**: Structured noise-bearing ring elements.
3. **Key Generation**:
   - `sk, pk = KeyGen()`
   - Bootstrapping keys for FHE refresh.
4. **Encryption**:
   - `c = Encrypt(pk, m)`
5. **Evaluation**:
   - `c_add = Add(c₁, c₂)`
   - `c_mul = Multiply(c₁, c₂)`
   - `c_rescale` / `c_relinearize` for scale management (CKKS).
6. **Decryption**:
   - `m = Decrypt(sk, c)`

---

## 4. CKKS Scheme for Approximate Arithmetic

- **Approximate HE**: Encodes real numbers as fixed-point values
- **Rescaling**: Maintains scale after multiplication
- **Applications**: Machine learning on floating-point data
- **Key Operations**: `rescale`, `relinearize`, `rotate` (for SIMD batching)

---

## 5. Performance Considerations

- **Noise Growth**: Controlled by scheme parameters and bootstrapping
- **Ciphertext Size**: Trade-off between security and speed
- **Bootstrapping Cost**: High overhead; use leveled HE when possible
- **Parallelization**: Use SIMD slots to pack many values in one ciphertext
- **Parameter Selection**: Balance security level (e.g., 128-bit) and multiplicative depth

---

## 6. Practical Libraries & Tools

- **Microsoft SEAL / TenSEAL**: CKKS, BFV support, easy C++/Python APIs
- **HElib**: BGV scheme, C++ library by IBM
- **PALISADE**: BFV, CKKS, BGV, includes FHEW and TFHE modules
- **TFHE**: Fast bootstrapping for boolean circuits

---

## 7. Use Cases in PPML

- **Encrypted Inference**: Perform neural network or logistic regression inference on ciphertexts
- **Secure Aggregation**: Sum encrypted model updates in federated learning
- **Private Querying**: Search or statistical queries on encrypted databases

---

## 8. Best Practices

- **Parameter Tuning**: Choose appropriate `poly_modulus_degree`, `coeff_mod_bit_sizes` for noise budget
- **Minimize Bootstrapping**: Use leveled HE for known-depth tasks
- **Use SIMD Packing**: Batch operations for throughput
- **Keep Secret Key Offline**: Only public key and evaluation keys distributed

---