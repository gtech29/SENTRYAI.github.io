import numpy as np
from sklearn.ensemble import IsolationForest
import pandas as pd
from datetime import datetime

# Generate mock network data
def generate_mock_data(n_samples=500):
    np.random.seed(42)
    timestamps = [datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] for _ in range(n_samples)]
    source_ips = [f"{np.random.randint(1, 255)}.{np.random.randint(0, 255)}.{np.random.randint(0, 255)}.{np.random.randint(0, 255)}" for _ in range(n_samples)]
    # Simulate features: packet size (bytes), connection duration (seconds), and number of packets
    packet_sizes = np.random.normal(1500, 500, n_samples)  # Normal traffic
    durations = np.random.normal(5, 2, n_samples)  # Normal traffic
    packet_counts = np.random.normal(100, 30, n_samples)  # Normal traffic
    # Inject more anomalies
    anomaly_indices = np.random.choice(n_samples, size=50, replace=False)  # 50 anomalies
    packet_sizes[anomaly_indices[:20]] = np.random.uniform(5000, 10000, 20)  # Large packets
    durations[anomaly_indices[20:40]] = np.random.uniform(20, 50, 20)  # Long durations
    packet_counts[anomaly_indices[40:]] = np.random.uniform(500, 1000, 10)  # High packet counts

    data = pd.DataFrame({
        'timestamp': timestamps,
        'source_ip': source_ips,
        'packet_size': packet_sizes,
        'duration': durations,
        'packet_count': packet_counts
    })
    return data

# Anomaly detection using Isolation Forest
def detect_anomalies(data):
    features = data[['packet_size', 'duration', 'packet_count']]
    model = IsolationForest(contamination=0.1, random_state=42)  # 10% of data as anomalies
    predictions = model.fit_predict(features)
    anomaly_scores = model.score_samples(features)  # Lower scores indicate anomalies
    data['anomaly_score'] = -anomaly_scores  # Negative because lower is more anomalous
    data['is_anomaly'] = predictions  # -1 for anomalies, 1 for normal
    return data

# Example usage
if __name__ == "__main__":
    mock_data = generate_mock_data()
    results = detect_anomalies(mock_data)
    print(results.tail())  # Show the last few rows to see anomalies