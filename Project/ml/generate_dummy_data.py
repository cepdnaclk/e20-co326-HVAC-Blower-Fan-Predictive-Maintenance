import os
import pandas as pd
import numpy as np

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Generate normal data
np.random.seed(42)
num_normal_samples = 200

normal_data = pd.DataFrame({
    'vib_rms': np.random.normal(loc=0.3, scale=0.05, size=num_normal_samples),
    'vib_peak': np.random.normal(loc=1.0, scale=0.15, size=num_normal_samples),
    'current_rms': np.random.normal(loc=1.5, scale=0.1, size=num_normal_samples),
    'current_std': np.random.normal(loc=0.1, scale=0.02, size=num_normal_samples)
})

# Save normal data
normal_filepath = os.path.join('data', 'fan_normal_data.csv')
normal_data.to_csv(normal_filepath, index=False)
print(f"Generated normal data at {normal_filepath}")

# Generate fault data
num_fault_samples = 50

fault_data = pd.DataFrame({
    'vib_rms': np.random.normal(loc=2.0, scale=0.5, size=num_fault_samples),
    'vib_peak': np.random.normal(loc=3.5, scale=0.8, size=num_fault_samples),
    'current_rms': np.random.normal(loc=3.0, scale=0.5, size=num_fault_samples),
    'current_std': np.random.normal(loc=0.5, scale=0.1, size=num_fault_samples)
})

# Save fault data
fault_filepath = os.path.join('data', 'fan_fault_data.csv')
fault_data.to_csv(fault_filepath, index=False)
print(f"Generated fault data at {fault_filepath}")
