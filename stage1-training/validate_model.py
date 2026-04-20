"""
HVAC Fan — Model Validation & Threshold Calibration
=====================================================
Runs the trained K-Means model on ALL data (normal + warning + critical)
to calculate anomaly scores and find the optimal detection thresholds.

Usage:
    python validate_model.py

Inputs:
    data/features_all.csv
    data/kmeans_model.joblib
    data/scaler_params.json

Outputs:
    data/confusion_matrix.png      — Confusion matrix heatmap
    data/roc_curve.png             — ROC curve with AUC
    data/score_distribution.png    — Anomaly score distributions per label
    data/threshold_results.json    — Optimal thresholds
"""

import os
import json
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
    f1_score,
    precision_recall_curve,
    auc,
)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
FEATURES_FILE = os.path.join(DATA_DIR, "features_all.csv")
MODEL_FILE = os.path.join(DATA_DIR, "kmeans_model.joblib")
SCALER_FILE = os.path.join(DATA_DIR, "scaler_params.json")

FEATURE_COLS = [
    "vib_rms", "vib_peak", "vib_crest", "vib_kurt",
    "cur_rms", "cur_std",
    "dom_freq", "spec_rms", "spec_cent",
    "band1", "band2", "band3"
]


def main():
    print("=" * 60)
    print("  HVAC Fan — Model Validation & Threshold Calibration")
    print("=" * 60)

    # ─── Load Everything ─────────────────────────────────────────
    for path, name in [
        (FEATURES_FILE, "features_all.csv"),
        (MODEL_FILE, "kmeans_model.joblib"),
        (SCALER_FILE, "scaler_params.json"),
    ]:
        if not os.path.exists(path):
            print(f"\n[ERROR] {name} not found at {path}")
            return

    df = pd.read_csv(FEATURES_FILE)
    kmeans = joblib.load(MODEL_FILE)
    with open(SCALER_FILE) as f:
        scaler_params = json.load(f)

    print(f"\nLoaded {len(df):,} feature vectors")
    print(f"Labels: {dict(df['label'].value_counts())}")

    # ─── Apply Scaler ────────────────────────────────────────────
    X_all = df[FEATURE_COLS].values
    mean = np.array(scaler_params["mean_"])
    scale = np.array(scaler_params["scale_"])
    X_scaled = (X_all - mean) / (scale + 1e-9)

    labels = df["label"].values

    # ─── Compute Anomaly Scores ──────────────────────────────────
    print("\n[STEP 1] Computing anomaly scores for ALL data...")

    # Distance to each centroid
    distances = kmeans.transform(X_scaled)       # shape (N, K)
    min_distances = distances.min(axis=1)        # distance to nearest cluster
    nearest_cluster = distances.argmin(axis=1)   # which cluster

    # Normalize to 0-1 range
    max_dist = min_distances.max()
    anomaly_scores = min_distances / max_dist

    # Print per-label stats
    print(f"\n  Anomaly Score Statistics:")
    print(f"  {'Label':>15s}  {'Mean':>8s}  {'Std':>8s}  {'Min':>8s}  {'Max':>8s}")
    print(f"  {'-'*15}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}")
    for label in sorted(df["label"].unique()):
        mask = labels == label
        scores = anomaly_scores[mask]
        print(
            f"  {label:>15s}  {scores.mean():8.4f}  {scores.std():8.4f}  "
            f"{scores.min():8.4f}  {scores.max():8.4f}"
        )

    # ─── Score Distribution Plot ─────────────────────────────────
    print("\n[STEP 2] Generating score distribution plot...")

    plt.figure(figsize=(12, 6))
    label_colors = {
        "normal": "#2ecc71", "normal_low": "#27ae60",
        "warning": "#f39c12", "critical": "#e74c3c"
    }
    for label in sorted(df["label"].unique()):
        mask = labels == label
        plt.hist(
            anomaly_scores[mask], bins=50, alpha=0.5,
            label=f"{label} (n={mask.sum()})",
            color=label_colors.get(label, "#95a5a6")
        )
    plt.xlabel("Anomaly Score", fontsize=12)
    plt.ylabel("Count", fontsize=12)
    plt.title("Anomaly Score Distribution by Fan State", fontsize=14)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)

    dist_path = os.path.join(DATA_DIR, "score_distribution.png")
    plt.savefig(dist_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {dist_path}")

    # ─── Threshold Optimization ──────────────────────────────────
    print("\n[STEP 3] Optimizing detection thresholds...")

    # Binary labels: normal=0, anomaly=1
    y_binary = np.array([
        0 if l in ["normal", "normal_low"] else 1 for l in labels
    ])

    # Sweep thresholds to find best F1
    best_f1 = 0
    best_threshold = 0.5
    thresholds_tested = np.arange(0.05, 0.95, 0.01)
    f1_scores = []

    for thr in thresholds_tested:
        y_pred = (anomaly_scores >= thr).astype(int)
        f1 = f1_score(y_binary, y_pred, zero_division=0)
        f1_scores.append(f1)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = thr

    print(f"\n  Optimal threshold: {best_threshold:.2f} (F1 = {best_f1:.4f})")

    # Also find a good warning threshold (using the 95th percentile of normal scores)
    normal_scores = anomaly_scores[y_binary == 0]
    warn_threshold = np.percentile(normal_scores, 95)
    crit_threshold = best_threshold

    # Ensure warn < crit
    if warn_threshold >= crit_threshold:
        warn_threshold = crit_threshold * 0.65

    print(f"  WARNING  threshold: {warn_threshold:.2f}")
    print(f"  CRITICAL threshold: {crit_threshold:.2f}")

    # ─── Final Classification Report ────────────────────────────
    print("\n[STEP 4] Final classification report...")
    y_pred_final = (anomaly_scores >= crit_threshold).astype(int)

    print("\n" + classification_report(
        y_binary, y_pred_final,
        target_names=["normal", "anomaly"],
        digits=4
    ))

    # ─── ROC Curve ───────────────────────────────────────────────
    roc_auc = roc_auc_score(y_binary, anomaly_scores)
    fpr, tpr, _ = roc_curve(y_binary, anomaly_scores)

    plt.figure(figsize=(8, 8))
    plt.plot(fpr, tpr, "b-", linewidth=2, label=f"K-Means (AUC = {roc_auc:.4f})")
    plt.plot([0, 1], [0, 1], "k--", alpha=0.5)
    plt.xlabel("False Positive Rate", fontsize=12)
    plt.ylabel("True Positive Rate", fontsize=12)
    plt.title("ROC Curve — K-Means Anomaly Detection", fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)

    roc_path = os.path.join(DATA_DIR, "roc_curve.png")
    plt.savefig(roc_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ROC AUC: {roc_auc:.4f}")
    print(f"  Saved → {roc_path}")

    # ─── Confusion Matrix ────────────────────────────────────────
    cm = confusion_matrix(y_binary, y_pred_final)
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=["Normal", "Anomaly"],
        yticklabels=["Normal", "Anomaly"],
        annot_kws={"size": 16}
    )
    plt.xlabel("Predicted", fontsize=12)
    plt.ylabel("Actual", fontsize=12)
    plt.title(
        f"Confusion Matrix (threshold = {crit_threshold:.2f})", fontsize=14
    )

    cm_path = os.path.join(DATA_DIR, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved → {cm_path}")

    # ─── Save Threshold Results ──────────────────────────────────
    results = {
        "warning_threshold": round(float(warn_threshold), 4),
        "critical_threshold": round(float(crit_threshold), 4),
        "max_distance": round(float(max_dist), 4),
        "f1_score": round(float(best_f1), 4),
        "roc_auc": round(float(roc_auc), 4),
        "n_samples_normal": int((y_binary == 0).sum()),
        "n_samples_anomaly": int((y_binary == 1).sum()),
    }
    results_path = os.path.join(DATA_DIR, "threshold_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"  Saved → {results_path}")

    # ─── Summary ─────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  Validation Complete!")
    print(f"{'='*60}")
    print(f"  WARNING  threshold = {warn_threshold:.4f}")
    print(f"  CRITICAL threshold = {crit_threshold:.4f}")
    print(f"  Max distance       = {max_dist:.4f}")
    print(f"  F1 Score           = {best_f1:.4f}")
    print(f"  ROC AUC            = {roc_auc:.4f}")
    print(f"{'='*60}\n")
    print("  Next step: python export_to_c_header.py")


if __name__ == "__main__":
    main()
