import numpy as np
from sklearn.cluster import KMeans

# Stub for training a simple KMeans anomaly detector
def train_anomaly_model():
    print("Loading data...")
    # Generate some dummy normal data (vibration, current)
    normal_data = np.random.normal(loc=[1.2, 2.5], scale=[0.1, 0.2], size=(100, 2))
    
    print("Training K-Means (k=1) to find normal centroid...")
    kmeans = KMeans(n_clusters=1, random_state=42)
    kmeans.fit(normal_data)
    
    centroid = kmeans.cluster_centers_[0]
    print(f"Learned Centroid: {centroid}")
    
    # Simple strategy: Anomaly score is distance from centroid
    print("Threshold can be set based on max distance in normal data.")

if __name__ == "__main__":
    train_anomaly_model()
