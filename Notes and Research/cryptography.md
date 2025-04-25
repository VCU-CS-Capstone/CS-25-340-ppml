# Cryptography

Cryptography is the science of securing communication and data through techniques that prevent unauthorized access. It plays a foundational role in information security by ensuring confidentiality, integrity, authentication, and non-repudiation. Below is an expanded set of principles, techniques, and practices—covering both classical and modern approaches relevant to Privacy-Preserving Machine Learning (PPML).

---

## 1. Principles of Cryptography

- **Confidentiality**: Only authorized parties can read data. Achieved through encryption (symmetric or asymmetric).
- **Integrity**: Data must remain unaltered. Ensured via cryptographic hashes and message authentication codes (MACs).
- **Authentication**: Verifies the identity of parties. Implemented via digital signatures and certificates.
- **Non-repudiation**: Prevents senders from denying their actions. Provided by digitally signing messages.
- **Availability**: Ensures services are accessible when needed (e.g., mitigating Denial of Service via rate-limiting).

---

## 2. Core Cryptographic Techniques

### 2.1 Symmetric Encryption (Secret-Key)
- **AES** (Advanced Encryption Standard): Block cipher, common modes: CBC, GCM (provides confidentiality + integrity).
- **ChaCha20-Poly1305**: Stream cipher with built-in MAC, ideal for high-speed or constrained environments.
- **Key Distribution**: Use Key Management Services (KMS) or secure channels (TLS) to exchange keys.

### 2.2 Asymmetric Encryption (Public-Key)
- **RSA**: Widely used for key exchange and digital signatures, key sizes ≥2048 bits.
- **ECC** (Elliptic Curve Cryptography): Equivalent security with smaller keys (e.g., P-256 curve).
- **Hybrid Encryption**: Combine asymmetric (for key exchange) + symmetric (for bulk data) for performance.

### 2.3 Hash Functions
- **SHA-2 Family** (SHA-256, SHA-512): Secure hash algorithms, collision-resistant.
- **SHA-3 Family**: Newer standard using Keccak sponge function.
- **Usage**: Password hashing (with salt + slow KDF like bcrypt/PBKDF2/Argon2), data integrity checks.

### 2.4 Message Authentication
- **HMAC** (Hash-based MAC) using SHA-256 or SHA-3.
- **AEAD** (Authenticated Encryption with Associated Data) modes like AES-GCM and ChaCha20-Poly1305.

### 2.5 Digital Signatures
- **RSA-PSS**: Probabilistic signature scheme.
- **ECDSA**: Elliptic curve signature.
- **EdDSA** (Ed25519): Modern, high-performance curve.
- **Use Cases**: Code signing, TLS certificates, blockchain transactions.

---

## 3. Advanced & PPML-Specific Techniques

### 3.1 Homomorphic Encryption (HE)
- **Partial (PHE)**: Supports either addition (Paillier) or multiplication (RSA).
- **Somewhat (SHE)**: Limited support for both operations up to a depth.
- **Fully (FHE)**: Arbitrary operations on ciphertexts (e.g., CKKS for floats).
- **Libraries**: Microsoft SEAL / TenSEAL, HElib, PALISADE.
- **Applications**: Encrypted inference, secure aggregation in federated learning.

### 3.2 Secure Multi-Party Computation (MPC)
- **Secret Sharing**: Shamir’s Secret Sharing, additive sharing.
- **Garbled Circuits**, **Oblivious Transfer**.
- **Frameworks**: PySyft, MP-SPDZ, SCALE-MAMBA.
- **Use Cases**: Joint model training without revealing raw data.

### 3.3 Zero-Knowledge Proofs (ZKP)
- **SNARKs / STARKs**: Succinct proofs for computation correctness.
- **Use Cases**: Verifiable computation, blockchain privacy (e.g., Zcash).

### 3.4 Differential Privacy (DP)
- **Laplace / Gaussian Mechanisms**: Add noise to outputs to protect individual records.
- **Epsilon (ε) Budget**: Quantifies privacy-utility tradeoff.
- **Tools**: Google DP library, TensorFlow Privacy.
- **Use Cases**: Model update masking, query-based data access.

---

## 4. Key Management & Infrastructure

- **Key Generation**: Use hardware security modules (HSM) or secure enclaves.
- **Key Storage**: KMS (AWS KMS, Azure Key Vault), encrypted vaults.
- **Rotation & Revocation**: Periodic key rotation, CRL/OCSP for certificates.
- **PKI**: Hierarchical trust with Certificate Authorities (CAs), TLS certificates.
- **Secret Sharing**: Distribute keys in parts to avoid single point of compromise.

---

## 5. Best Practices & Hardening

1. **Use vetted libraries**: OpenSSL, PyCryptodome, libsodium, SEAL.
2. **Avoid custom crypto**: Don’t implement algorithms from scratch.
3. **Enforce HTTPS/TLS**: Always encrypt in transit with strong cipher suites.
4. **Harden endpoints**: Rate-limiting, key usage auditing.
5. **Cryptographic agility**: Design systems to swap algorithms (e.g., quantum-safe curves) easily.
6. **Side-Channel Protection**: Constant-time operations, masking, hardware support.
7. **Regular Audits**: Penetration testing, code reviews, dependency scanning.

---

## 6. Common Attacks & Defenses

| Attack                       | Defense                                                              |
|------------------------------|----------------------------------------------------------------------|
| Man-in-the-Middle (MitM)     | TLS with certificate validation, HSTS                                 |
| Brute-Force / Dictionary     | Strong keys, rate-limiting, account lockout                          |
| Replay Attack                | Nonces, timestamps, session tokens                                   |
| Side-Channel (timing, power) | Constant-time code, masking, hardware protections                    |
| Collision Attacks            | Use collision-resistant hashes (SHA-256+), avoid MD5/SHA-1           |
| Quantum Attacks (future)     | Transition to post-quantum algorithms (e.g., lattice-based HE)       |

---

## 7. Glossary

- **HE**: Homomorphic Encryption  
- **MPC**: Multi-Party Computation  
- **DP**: Differential Privacy  
- **AEAD**: Authenticated Encryption with Associated Data  
- **KDF**: Key Derivation Function  
- **HSM**: Hardware Security Module

---