from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'beehive')
DB_USER = os.getenv('DB_USER', 'your_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password')

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        cursor_factory=RealDictCursor
    )

@app.route('/api/weight', methods=['POST'])
def add_weight():
    data = request.get_json()
    if not data or 'weight' not in data:
        return jsonify({'error': 'No weight provided'}), 400

    weight = data['weight']
    battery = data.get('battery')  # получим процент, если есть
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO weight_history (weight_grams, battery_percent) VALUES (%s, %s)",
            (weight, battery)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'status': 'ok'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weight/history', methods=['GET'])
def get_history():
    hours = request.args.get('hours', default=24, type=int)
    since = datetime.utcnow() - timedelta(hours=hours)
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT timestamp, weight_grams, battery_percent FROM weight_history WHERE timestamp >= %s ORDER BY timestamp ASC",
            (since,)
        )
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
        cur.execute("DELETE FROM weight_history")
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'status': 'cleared'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)










