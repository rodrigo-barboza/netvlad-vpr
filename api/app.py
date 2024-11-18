from flask import Flask, jsonify
from netvlad.utils import extract_netvlad_descriptor

import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, '../dataset')

@app.route('/ping', methods=['GET'])
def home():
    return jsonify({"message": "pong"})

@app.route('/teste', methods=['GET'])
def generate_descriptors():
    descriptor = extract_netvlad_descriptor(os.path.join(DATASET_DIR, 'frame00001.png'))
    return jsonify(descriptor.tolist())

if __name__ == '__main__':
    app.run(debug=True)
