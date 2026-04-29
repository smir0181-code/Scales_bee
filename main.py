from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Параметры подключения к БД из переменных окружения (обязательно задайте их в Amvera)
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

def get_db_connection():
    if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
        raise Exception("Database credentials not fully set in environment")
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )

@app.route('/api/weight', methods=['POST'])
def add_weight():
    data = request.get_json()
    if not data or 'weight' not in data:
        return jsonify({'error': 'No weight provided'}), 400
    weight = data['weight']
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO weight_measurements (weight_grams) VALUES (%s)",
            (weight,)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'status': 'ok'}), 201
    except Exception as e:
        app.logger.error(f"DB error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/weight/history', methods=['GET'])
def get_history():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, weight_grams
            FROM weight_measurements
            ORDER BY timestamp DESC
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weight/history/clear', methods=['POST'])
def clear_history():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM weight_measurements")
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'status': 'cleared'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    # Если есть index.html в папке static – отдаём, иначе JSON
    if os.path.exists('static/index.html'):
        return send_from_directory('static', 'index.html')
    return jsonify({'message': 'Scales API is running'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)