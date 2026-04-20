import os
import pickle
import pandas as pd
import numpy as np

# Load artifacts
with open(os.path.join('artifacts', 'scaler.pkl'), 'rb') as f:
    scaler = pickle.load(f)
    
with open(os.path.join('artifacts', 'kmeans.pkl'), 'rb') as f:
    kmeans = pickle.load(f)
    
with open(os.path.join('artifacts', 'metadata.pkl'), 'rb') as f:
    metadata = pickle.load(f)
    
features = metadata['feature_order']
warning_threshold = metadata['warning_threshold']
critical_threshold = metadata['critical_threshold']

def evaluate(data_path, dataset_name):
    if not os.path.exists(data_path):
        print(f"File {data_path} not found. Skipping {dataset_name} evaluation.")
        return
        
    df = pd.read_csv(data_path)
    X = df[features]
    X_scaled = scaler.transform(X)
    
    distances = kmeans.transform(X_scaled)
    min_distances = np.min(distances, axis=1)
    
    warnings = np.sum((min_distances > warning_threshold) & (min_distances <= critical_threshold))
    criticals = np.sum(min_distances > critical_threshold)
    normals = len(min_distances) - warnings - criticals
    
    print(f"\n--- Evaluation on {dataset_name} ---")
    print(f"Total samples: {len(df)}")
    print(f"Normal samples: {normals} ({(normals/len(df))*100:.1f}%)")
    print(f"Warning samples: {warnings} ({(warnings/len(df))*100:.1f}%)")
    print(f"Critical samples: {criticals} ({(criticals/len(df))*100:.1f}%)")
    print(f"Mean Distance: {np.mean(min_distances):.4f}")
    print(f"Max Distance: {np.max(min_distances):.4f}")

evaluate(os.path.join('data', 'fan_normal_data.csv'), "Normal Data")
evaluate(os.path.join('data', 'fan_fault_data.csv'), "Fault Data")
