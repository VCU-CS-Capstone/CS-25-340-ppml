from flask import Flask, render_template, request, jsonify
# import tenseal
import numpy as np
import json

app = Flask(__name__)

# Initialize context for TenSEAL
context = tenseal.context(
    scheme=tenseal.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,
    coeff_mod_bit_sizes=[60, 40, 40, 60]
)
context.global_scale = 2**40
context.generate_galois_keys()
context.generate_relin_keys()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt_data():
    data = request.json.get('data')
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        data = np.array(data, dtype=np.float32)
        encrypted_data = tenseal.ckks_vector(context, data).serialize()
        return jsonify({'encrypted_data': encrypted_data.hex()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/train', methods=['POST'])
def train_model():
    dataset = request.json.get('dataset')
    # Placeholder for ML model training logic
    return jsonify({'message': f'Training started on {dataset}!'})

@app.route('/visualize', methods=['GET'])
def visualize():
    # Placeholder for visualization logic
    return jsonify({'message': 'Visualization data sent'})

if __name__ == '__main__':
    app.run(debug=True)
