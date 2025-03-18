from dotenv import load_dotenv, find_dotenv
import sys
sys.path.append('..')
from ml.anomaly_detection import generate_mock_data, detect_anomalies
from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2 import Error
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Database connection
def get_db_connection():
    try:
        load_dotenv(find_dotenv())
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        return conn
    except Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

# Generate and store mock data with anomaly detection
@app.route('/generate-data', methods=['POST'])
def generate_data():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    # Generate and detect anomalies
    mock_data = generate_mock_data(n_samples=500)
    results = detect_anomalies(mock_data)

    # Insert into PostgreSQL (limit to 100 records for testing)
    cur = conn.cursor()
    for _, row in results.iterrows():
        cur.execute(
            "INSERT INTO logs (timestamp, source_ip, event_type, anomaly_score) VALUES (%s, %s, %s, %s)",
            (row['timestamp'], row['source_ip'], 
             'Suspicious Traffic' if row['is_anomaly'] == -1 else 'Normal Traffic', 
             float(row['anomaly_score']))
        )
        if cur.rowcount >= 100:  # Limit to 100 records
            break
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': f'Data generated and {min(100, len(results))} records stored successfully'})

# Fetch logs endpoint
@app.route('/logs', methods=['GET'])
def get_logs():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 10;")
    logs = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{'id': log[0], 'timestamp': str(log[1]), 'source_ip': log[2], 'event_type': log[3], 'anomaly_score': log[4]} for log in logs])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
