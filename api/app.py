import os
import sqlite3
import json

from flask import Flask, request, jsonify, g
from netvlad.utils import extract_netvlad_descriptor

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
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM descriptors')
    result = cursor.fetchone()

    return jsonify({ 'message': json.dumps(result) })

@app.route('/recognize-place', methods=['POST'])
def recognize_place():
    if 'file' not in request.files:
        return 'No file part', 400

    query_image_path = save_query_image()
    descriptor = extract_netvlad_descriptor(query_image_path)
    # TODO: fazer a comparação da query com as imagens do dataset e retornar a classe
    save_image_descriptor(query_image_path, descriptor)

    return jsonify({
        'query_image': query_image_path,
        'descriptor': descriptor.tolist(),
    })

# UTILS
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
