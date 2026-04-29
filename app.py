from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/weight', methods=['POST'])
def add_weight():
    return jsonify({"status": "ok", "message": "test"}), 200

@app.route('/')
def index():
    return jsonify({"status": "running"})