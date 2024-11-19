import os
import sqlite3
import json
import pandas as pd
import numpy as np

from collections import Counter
from flask import Flask, request, jsonify, g
from netvlad.utils import extract_netvlad_descriptor
from netvlad.NetVLADComparator import NetVLADComparator

app = Flask(__name__)

app.config['DATABASE'] = 'database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'

# DATABASE
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# ROUTES
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({ 'message': 'pong' })

@app.route('/recognize-place', methods=['POST'])
def recognize_place():
    if 'file' not in request.files:
        return 'No file part', 400

    query_image_path = save_query_image()
    descriptor = extract_netvlad_descriptor(query_image_path)
    single_best_match_class = single_best_match(descriptor)

    return jsonify({
        'query_image': query_image_path,
        'descriptor': descriptor.tolist(),
        'single_best_match_class': single_best_match_class,
    })


# UTILS
def single_best_match(query_descriptor):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM descriptors')
    all_descriptors = cursor.fetchall()

    best_match_class = None
    best_similarity = float('inf')
    netvlad_comparator = NetVLADComparator()

    for descriptor_id, descriptor_class, dataset_descriptor in all_descriptors:
        descriptor = np.array(json.loads(dataset_descriptor), dtype=np.float32)
        similarity = netvlad_comparator.compare_descriptors(query_descriptor, descriptor, 'euclidean')

        if similarity < best_similarity:
            best_similarity = similarity
            best_match_class = descriptor_class

    cursor.close()
    db.close()

    return best_match_class

def multimatch(query_descriptor, top_n=5):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM descriptors')
    all_descriptors = cursor.fetchall()

    netvlad_comparator = NetVLADComparator()

    similarities = []

    for descriptor_id, descriptor_class, dataset_descriptor in all_descriptors:
        dataset_descriptor = np.array(json.loads(dataset_descriptor), dtype=np.float32)
        similarity = netvlad_comparator.compare_descriptors(query_descriptor, dataset_descriptor, 'cosine')
        similarities.append((similarity, descriptor_class))

    similarities.sort(key=lambda x: x[0])
    top_matches = similarities[:top_n]
    top_classes = [match[1] for match in top_matches]
    class_counts = Counter(top_classes)
    best_match_class = class_counts.most_common(1)[0][0]

    return best_match_class

def describe_dataset_images():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, 'dataset/labeled_dataset.csv')
    data = pd.read_csv(csv_path, sep=';', header=None, names=['filename', 'class', 'nan'], engine='python')

    for _, row in data.iterrows():
        filename = row['filename']
        class_name = row['class']
        dataset_image = os.path.join(base_dir, 'dataset', filename)
        descriptor = extract_netvlad_descriptor(dataset_image)
        save_image_descriptor(class_name, descriptor)

    return 'described dataset images'


def save_query_image():
    file = request.files['file']
    filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filename)

    return filename


def save_image_descriptor(query_image_path, descriptor):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO descriptors (class, descriptor) VALUES (?, ?)',
        (query_image_path, json.dumps(descriptor.tolist()))
    )
    db.commit()


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
