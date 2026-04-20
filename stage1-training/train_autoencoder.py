"""
HVAC Fan — LSTM Autoencoder Training
======================================
Trains an LSTM Autoencoder on sequences of NORMAL fan feature windows.
The model learns to reconstruct normal patterns; abnormal data will have
high reconstruction error = anomaly score.

Usage:
    python train_autoencoder.py

Inputs:
    data/features_all.csv

Outputs:
    data/autoencoder_best.h5     — Best Keras model
    data/autoencoder.tflite      — TFLite version for server deployment
    data/ae_training_history.png — Loss curves
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
FEATURES_FILE = os.path.join(DATA_DIR, "features_all.csv")

# Sequence parameters
SEQ_LEN = 20       # 20 windows ≈ 20 × 2.56s ≈ 51 seconds of context
N_FEATURES = 12    # 12 feature columns

NORMAL_LABELS = ["normal", "normal_low"]

FEATURE_COLS = [
    "vib_rms", "vib_peak", "vib_crest", "vib_kurt",
    "cur_rms", "cur_std",
    "dom_freq", "spec_rms", "spec_cent",
    "band1", "band2", "band3"
]


def make_sequences(data: np.ndarray, seq_len: int) -> np.ndarray:
    """Create overlapping sequences from a 2D array of features."""
    sequences = []
    for i in range(len(data) - seq_len):
        sequences.append(data[i : i + seq_len])
    return np.array(sequences)


def main():
    print("=" * 60)
    print("  HVAC Fan — LSTM Autoencoder Training")
    print("=" * 60)

    # Check if TensorFlow is available
    try:
        import tensorflow as tf
        from tensorflow.keras import layers, Model, callbacks
        print(f"\n  TensorFlow version: {tf.__version__}")
        print(f"  GPU available: {len(tf.config.list_physical_devices('GPU')) > 0}")
    except ImportError:
        print("\n[ERROR] TensorFlow not installed.")
        print("  Install with: pip install tensorflow")
        print("\n  NOTE: The LSTM Autoencoder is OPTIONAL for Stage 1.")
        print("  The K-Means model alone is sufficient for ESP32 deployment.")
        print("  The Autoencoder runs on the server (Node-RED) in Stage 2.")
        return

    # ─── Load Data ───────────────────────────────────────────────
    if not os.path.exists(FEATURES_FILE):
        print(f"\n[ERROR] {FEATURES_FILE} not found.")
        print("  Run feature_engineering.py first.")
        return

    df = pd.read_csv(FEATURES_FILE)
    print(f"\nLoaded {len(df):,} feature vectors")

    # Filter normal data
    df_normal = df[df["label"].isin(NORMAL_LABELS)]
    X_normal = df_normal[FEATURE_COLS].values

    print(f"Normal data: {len(df_normal):,} vectors")

    if len(df_normal) < SEQ_LEN + 10:
        print(f"[ERROR] Need at least {SEQ_LEN + 10} normal vectors.")
        return

    # ─── Normalize ───────────────────────────────────────────────
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_normal)

    # ─── Create Sequences ────────────────────────────────────────
    X_seq = make_sequences(X_scaled, SEQ_LEN)
    print(f"Sequences: {X_seq.shape} (samples, timesteps, features)")

    # Split into train/val (90/10)
    split = int(len(X_seq) * 0.9)
    X_train = X_seq[:split]
    X_val = X_seq[split:]
    print(f"Train: {X_train.shape[0]}, Val: {X_val.shape[0]}")

    # ─── Build LSTM Autoencoder ──────────────────────────────────
    print("\n[STEP 1] Building LSTM Autoencoder architecture...")

    inp = layers.Input(shape=(SEQ_LEN, N_FEATURES), name="input")

    # Encoder
    x = layers.LSTM(64, return_sequences=True, name="encoder_lstm1")(inp)
    x = layers.Dropout(0.2)(x)
    x = layers.LSTM(32, return_sequences=False, name="encoder_lstm2")(x)
    bottleneck = layers.Dense(16, activation="relu", name="bottleneck")(x)

    # Decoder
    x = layers.RepeatVector(SEQ_LEN, name="repeat")(bottleneck)
    x = layers.LSTM(32, return_sequences=True, name="decoder_lstm1")(x)
    x = layers.Dropout(0.2)(x)
    x = layers.LSTM(64, return_sequences=True, name="decoder_lstm2")(x)
    out = layers.TimeDistributed(
        layers.Dense(N_FEATURES), name="output"
    )(x)

    model = Model(inputs=inp, outputs=out, name="LSTM_Autoencoder")
    model.compile(optimizer="adam", loss="mse")
    model.summary()

    # ─── Train ───────────────────────────────────────────────────
    print("\n[STEP 2] Training...")

    model_path = os.path.join(DATA_DIR, "autoencoder_best.h5")
    history = model.fit(
        X_train, X_train,
        epochs=50,
        batch_size=32,
        validation_data=(X_val, X_val),
        callbacks=[
            callbacks.EarlyStopping(
                patience=8, restore_best_weights=True, monitor="val_loss"
            ),
            callbacks.ModelCheckpoint(
                model_path, save_best_only=True, monitor="val_loss"
            ),
            callbacks.ReduceLROnPlateau(
                factor=0.5, patience=3, min_lr=1e-6
            ),
        ],
        verbose=1,
    )

    # ─── Plot Training History ───────────────────────────────────
    plt.figure(figsize=(10, 5))
    plt.plot(history.history["loss"], label="Train Loss", linewidth=2)
    plt.plot(history.history["val_loss"], label="Val Loss", linewidth=2)
    plt.xlabel("Epoch")
    plt.ylabel("MSE Loss")
    plt.title("LSTM Autoencoder — Training History")
    plt.legend()
    plt.grid(True, alpha=0.3)

    hist_path = os.path.join(DATA_DIR, "ae_training_history.png")
    plt.savefig(hist_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  Saved training plot → {hist_path}")

    # ─── Convert to TFLite ───────────────────────────────────────
    print("\n[STEP 3] Converting to TFLite...")
    try:
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        tflite_model = converter.convert()

        tflite_path = os.path.join(DATA_DIR, "autoencoder.tflite")
        with open(tflite_path, "wb") as f:
            f.write(tflite_model)
        print(f"  TFLite model: {len(tflite_model):,} bytes → {tflite_path}")
    except Exception as e:
        print(f"  [WARNING] TFLite conversion failed: {e}")
        print("  This is OK — TFLite is only needed for optional server deployment.")

    # ─── Summary ─────────────────────────────────────────────────
    final_train_loss = history.history["loss"][-1]
    final_val_loss = history.history["val_loss"][-1]

    print(f"\n{'='*60}")
    print(f"  LSTM Autoencoder Training Complete!")
    print(f"{'='*60}")
    print(f"  Final Train Loss: {final_train_loss:.6f}")
    print(f"  Final Val Loss:   {final_val_loss:.6f}")
    print(f"  Model: {model_path}")
    print(f"{'='*60}\n")
    print("  Next step: python validate_model.py")


if __name__ == "__main__":
    main()
