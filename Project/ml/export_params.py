import os
import pickle
import json

# Load artifacts
with open(os.path.join('artifacts', 'scaler.pkl'), 'rb') as f:
    scaler = pickle.load(f)
    
with open(os.path.join('artifacts', 'kmeans.pkl'), 'rb') as f:
    kmeans = pickle.load(f)
    
with open(os.path.join('artifacts', 'metadata.pkl'), 'rb') as f:
    metadata = pickle.load(f)
    
features = metadata['feature_order']

# Extract parameters
scaler_means = scaler.mean_.tolist()
scaler_scales = scaler.scale_.tolist()
centroids = kmeans.cluster_centers_.tolist()
warning_threshold = float(metadata['warning_threshold'])
critical_threshold = float(metadata['critical_threshold'])

# 1. Output JSON
model_params = {
    "feature_order": features,
    "scaler_means": scaler_means,
    "scaler_scales": scaler_scales,
    "centroids": centroids,
    "warning_threshold": warning_threshold,
    "critical_threshold": critical_threshold
}

with open("model_params.json", "w") as f:
    json.dump(model_params, f, indent=4)
    
print("Saved parameters to model_params.json")

# 2. Output C++ header block
cpp_code = f"""
// Auto-generated parameters for ESP32 KMeans Anomaly Detection
// Feature order: {', '.join(features)}

const float scalerMean[4] = {{{', '.join(f"{x:.6f}" for x in scaler_means)}}};
const float scalerStd[4] = {{{', '.join(f"{x:.6f}" for x in scaler_scales)}}};

const float centroids[2][4] = {{
    {{{', '.join(f"{x:.6f}" for x in centroids[0])}}},
    {{{', '.join(f"{x:.6f}" for x in centroids[1])}}}
}};

const float warningThreshold = {warning_threshold:.6f};
const float criticalThreshold = {critical_threshold:.6f};
"""

with open("model_params.h", "w") as f:
    f.write(cpp_code)
    
print("Saved C++ header snippet to model_params.h")
print("\n--- C++ Header Preview ---")
print(cpp_code)
