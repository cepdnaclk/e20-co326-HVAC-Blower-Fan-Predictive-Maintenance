import os
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# 1. Load data
data_path = os.path.join('data', 'fan_normal_data.csv')
print(f"Loading data from {data_path}")
df = pd.read_csv(data_path)

# 2. Select features
features = ['vib_rms', 'vib_peak', 'current_rms', 'current_std']
X = df[features]

# 3. Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 4. Train KMeans with 2 clusters
print("Training KMeans with 2 clusters...")
kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
kmeans.fit(X_scaled)

# 5. Compute distances to cluster centers
distances = kmeans.transform(X_scaled)
min_distances = np.min(distances, axis=1)

dist_mean = np.mean(min_distances)
dist_std = np.std(min_distances)
dist_max = np.max(min_distances)

print(f"Distance stats - Mean: {dist_mean:.4f}, Std: {dist_std:.4f}, Max: {dist_max:.4f}")

# 6. Suggest thresholds
warning_threshold = dist_mean + 2 * dist_std
critical_threshold = dist_mean + 3 * dist_std

print(f"Suggested Warning Threshold: {warning_threshold:.4f}")
print(f"Suggested Critical Threshold: {critical_threshold:.4f}")

# 7. Save artifacts
os.makedirs('artifacts', exist_ok=True)
with open(os.path.join('artifacts', 'scaler.pkl'), 'wb') as f:
    pickle.dump(scaler, f)
    
with open(os.path.join('artifacts', 'kmeans.pkl'), 'wb') as f:
    pickle.dump(kmeans, f)
    
metadata = {
    'warning_threshold': warning_threshold,
    'critical_threshold': critical_threshold,
    'feature_order': features
}
with open(os.path.join('artifacts', 'metadata.pkl'), 'wb') as f:
    pickle.dump(metadata, f)

print("Saved model artifacts to 'artifacts' directory.")
