from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # разрешить запросы с других доменов (для локальной разработки)

# Параметры подключения к БД
DB_HOST = 'localhost'
DB_NAME = 'beehive'
DB_USER = 'your_user'
DB_PASSWORD = 'your_password'

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )
    return conn

# Эндпоинт для приёма данных от ESP32
@app.route('/api/weight', methods=['POST'])
def add_weight():
    data = request.get_json()
    if not data or 'weight' not in data:
        return jsonify({'error': 'No weight provided'}), 400

    weight = data['weight']
    print(weight)
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
        return jsonify({'error': str(e)}), 500

# Эндпоинт для получения данных за последние N часов
@app.route('/api/weight/history', methods=['GET'])
def get_history():
    hours = request.args.get('hours', default=24, type=int)
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, weight_grams
            FROM weight_measurements
            WHERE timestamp > NOW() - INTERVAL '%s hours'
            ORDER BY timestamp
        """, (hours,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Отдаём HTML страницу
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)