# TensorFlow Encrpyted

TF Encrypted is a Python library built on top of TensorFlow that enables privacy-preserving machine learning by providing tools for performing computations on encrypted data. It is primarily focused on implementing secure multi-party computation (MPC) protocols in TensorFlow, which allows multiple parties to jointly compute on sensitive data without revealing their inputs.

## Privacy-Preserving Machine Learning:

* TF Encrypted allows secure machine learning on encrypted data, enabling operations like training and inference while protecting sensitive information (e.g., medical, financial data).
* It leverages advanced cryptographic techniques like secure computation and homomorphic encryption.

## Built on TensorFlow:

* The library integrates seamlessly with TensorFlow, meaning you can continue using familiar TensorFlow workflows (e.g., defining models, layers) while adding a layer of security for sensitive data.
* You can switch between regular TensorFlow computations and encrypted computations with minimal changes to your existing codebase.

## Secure Computation Techniques:

* Secret Sharing: Splits data into shares, distributed among several parties, so no single party can reconstruct the original data unless a certain threshold of shares is combined.
* Multi-Party Computation (MPC): Ensures that computations on shared data are performed securely, with only the final result revealed and intermediate steps kept confidential.
* Homomorphic Encryption (HE): TF Encrypted supports homomorphic encryption, allowing some computations to be performed directly on encrypted data.

## Flexible Deployment Models:

* Supports both local simulations and distributed setups where different parties run computations on different machines.
* It is especially useful in scenarios where sensitive data from multiple sources needs to be used for training machine learning models without revealing data to other parties.

## Use Cases:

* Collaborative Learning: Enables different organizations (e.g., hospitals, banks) to collaboratively train machine learning models on combined datasets without sharing raw data.
* Federated Learning: Useful for distributed training, where each party trains a local model on its own data, and a central server aggregates updates.
* Privacy-Preserving Inference: Allows running a trained machine learning model on encrypted user data, enabling predictions without revealing input data to the model owner.

## Workflow Example:

1. Define the Model: You first define your machine learning model using TensorFlow, as you normally would.
2. Encrypt Data: The data is encrypted using TF Encrypted’s secure computation tools (e.g., secret sharing). This allows for secure computations on the encrypted data.
3. Perform Computation: TF Encrypted enables privacy-preserving computation, such as secure model training or inference, where the data remains encrypted throughout the computation process.
4. Decrypt Results: After the computation, the results (e.g., predictions, model updates) are decrypted using the secret-sharing mechanism.


## Basic Code Example:

```py
import tensorflow as tf
import tf_encrypted as tfe

# Define a simple model in TensorFlow
def build_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(128, activation='relu', input_shape=(28*28,)),
        tf.keras.layers.Dense(10, activation='softmax')
    ])
    return model

# Create the TFE secure environment
tfe.set_protocol(tfe.protocols.SecureNN())

# Encrypt and secure the model
encrypted_model = tfe.keras.Sequential.from_config(build_model().get_config())

# Define encrypted data (can be secret shared among parties)
x_encrypted = tfe.define_private_input(tf.ones((1, 28*28)))

# Perform secure inference
y_encrypted = encrypted_model(x_encrypted)

# Decrypt the result
y_plain = tfe.decrypt(y_encrypted)
```

In the example, the model is built using TensorFlow, but then it is converted into a secure encrypted model with ```tfe.keras.Sequential.from_config()```. The computations (inference) are performed on the encrypted data, and only the final result is decrypted.

## More Resources

* [Github Repository](https://github.com/tf-encrypted/tf-encrypted)
* [Documentation](https://tf-encrypted.readthedocs.io/en/latest/)
* [Official Website](https://tf-encrypted.io/)
