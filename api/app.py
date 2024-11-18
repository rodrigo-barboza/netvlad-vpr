from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def home():
    return jsonify({"message": "pong"})

if __name__ == '__main__':
    app.run(debug=True)
