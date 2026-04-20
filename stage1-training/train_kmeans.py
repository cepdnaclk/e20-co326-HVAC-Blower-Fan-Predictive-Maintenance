"""
HVAC Fan — K-Means Anomaly Detection Model Training
=====================================================
Trains a K-Means clustering model on NORMAL fan data only.
The model learns what "normal" looks like so it can detect anomalies
by measuring distance from normal clusters.

Usage:
    python train_kmeans.py

Inputs:
    data/features_all.csv

Outputs:
    data/kmeans_model.joblib     — Saved sklearn model
    data/centroids.json          — Centroid arrays for C++ export
    data/scaler_params.json      — Mean/scale for C++ normalization
    data/elbow_plot.png          — Elbow method plot for choosing K
    data/cluster_scatter.png     — 2D PCA scatter of clusters
"""

import os
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import joblib

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
FEATURES_FILE = os.path.join(DATA_DIR, "features_all.csv")

# Labels considered as "normal" for training
NORMAL_LABELS = ["normal", "normal_low"]

# Feature columns (exclude label)
FEATURE_COLS = [
    "vib_rms", "vib_peak", "vib_crest", "vib_kurt",
    "cur_rms", "cur_std",
    "dom_freq", "spec_rms", "spec_cent",
    "band1", "band2", "band3"
]


def main():
    print("=" * 60)
    print("  HVAC Fan — K-Means Model Training")
    print("=" * 60)

    # ─── Load Data ───────────────────────────────────────────────
    if not os.path.exists(FEATURES_FILE):
        print(f"\n[ERROR] {FEATURES_FILE} not found.")
        print("  Run feature_engineering.py first.")
        return

    df = pd.read_csv(FEATURES_FILE)
    print(f"\nLoaded {len(df):,} feature vectors from {FEATURES_FILE}")
    print(f"Labels: {dict(df['label'].value_counts())}")

    # ─── Filter Normal Data Only ─────────────────────────────────
    df_normal = df[df["label"].isin(NORMAL_LABELS)]
    X_normal = df_normal[FEATURE_COLS].values

    print(f"\nNormal data for training: {len(df_normal):,} vectors")
    print(f"  Labels used: {NORMAL_LABELS}")

    if len(df_normal) < 50:
        print("[ERROR] Not enough normal data. Need at least 50 vectors.")
        return

    # ─── Normalize Features ──────────────────────────────────────
    print("\n[STEP 1] Fitting StandardScaler on normal data...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_normal)

    # Save scaler parameters (needed for ESP32 firmware)
    scaler_params = {
        "mean_": scaler.mean_.tolist(),
        "scale_": scaler.scale_.tolist(),
        "feature_names": FEATURE_COLS
    }
    scaler_path = os.path.join(DATA_DIR, "scaler_params.json")
    with open(scaler_path, "w") as f:
        json.dump(scaler_params, f, indent=2)
    print(f"  Saved scaler params → {scaler_path}")

    # Print scaler stats
    print("\n  Feature normalization stats:")
    print(f"  {'Feature':>15s}  {'Mean':>10s}  {'StdDev':>10s}")
    print(f"  {'-'*15}  {'-'*10}  {'-'*10}")
    for i, name in enumerate(FEATURE_COLS):
        print(f"  {name:>15s}  {scaler.mean_[i]:10.4f}  {scaler.scale_[i]:10.4f}")

    # ─── Elbow Method ────────────────────────────────────────────
    print("\n[STEP 2] Running elbow method (K=2 to K=8)...")
    K_range = range(2, 9)
    inertias = []
    silhouettes = []

    for k in K_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=20, max_iter=300)
        km.fit(X_scaled)
        inertias.append(km.inertia_)
        sil = silhouette_score(X_scaled, km.labels_)
        silhouettes.append(sil)
        print(f"  K={k}: Inertia={km.inertia_:.2f}  Silhouette={sil:.4f}")

    # Plot elbow
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.plot(K_range, inertias, "bo-", linewidth=2, markersize=8)
    ax1.set_xlabel("Number of Clusters (K)", fontsize=12)
    ax1.set_ylabel("Inertia (Within-Cluster Sum of Squares)", fontsize=12)
    ax1.set_title("Elbow Method — Optimal K Selection", fontsize=14)
    ax1.grid(True, alpha=0.3)

    ax2.plot(K_range, silhouettes, "ro-", linewidth=2, markersize=8)
    ax2.set_xlabel("Number of Clusters (K)", fontsize=12)
    ax2.set_ylabel("Silhouette Score", fontsize=12)
    ax2.set_title("Silhouette Score vs K", fontsize=14)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    elbow_path = os.path.join(DATA_DIR, "elbow_plot.png")
    plt.savefig(elbow_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  Saved elbow plot → {elbow_path}")

    # ─── Train Final Model with K=3 ─────────────────────────────
    OPTIMAL_K = 3
    print(f"\n[STEP 3] Training final K-Means model with K={OPTIMAL_K}...")
    kmeans = KMeans(
        n_clusters=OPTIMAL_K,
        random_state=42,
        n_init=50,       # Run 50 times with different initializations
        max_iter=500,
        algorithm="lloyd"
    )
    kmeans.fit(X_scaled)

    final_sil = silhouette_score(X_scaled, kmeans.labels_)
    print(f"  Final Silhouette Score: {final_sil:.4f}")
    print(f"  Centroids shape: {kmeans.cluster_centers_.shape}")
    print(f"  Cluster sizes: {dict(zip(*np.unique(kmeans.labels_, return_counts=True)))}")

    # Print centroids (human-readable)
    print(f"\n  Centroid values (scaled):")
    print(f"  {'Feature':>15s}", end="")
    for k in range(OPTIMAL_K):
        print(f"  {'Cluster '+str(k):>12s}", end="")
    print()
    print(f"  {'-'*15}" + f"  {'-'*12}" * OPTIMAL_K)
    for i, name in enumerate(FEATURE_COLS):
        print(f"  {name:>15s}", end="")
        for k in range(OPTIMAL_K):
            print(f"  {kmeans.cluster_centers_[k][i]:12.4f}", end="")
        print()

    # ─── Save Model ──────────────────────────────────────────────
    model_path = os.path.join(DATA_DIR, "kmeans_model.joblib")
    joblib.dump(kmeans, model_path)
    print(f"\n  Saved model → {model_path}")

    # Save centroids as JSON (for C++ export)
    centroids_dict = {
        "n_clusters": OPTIMAL_K,
        "n_features": len(FEATURE_COLS),
        "centroids": kmeans.cluster_centers_.tolist(),
        "feature_names": FEATURE_COLS
    }
    centroids_path = os.path.join(DATA_DIR, "centroids.json")
    with open(centroids_path, "w") as f:
        json.dump(centroids_dict, f, indent=2)
    print(f"  Saved centroids → {centroids_path}")

    # ─── Cluster Scatter Plot (PCA 2D) ───────────────────────────
    print(f"\n[STEP 4] Generating cluster scatter plot (PCA projection)...")
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    centroids_pca = pca.transform(kmeans.cluster_centers_)

    plt.figure(figsize=(10, 8))
    colors = ["#2ecc71", "#3498db", "#e74c3c", "#f39c12", "#9b59b6"]
    for k in range(OPTIMAL_K):
        mask = kmeans.labels_ == k
        plt.scatter(
            X_pca[mask, 0], X_pca[mask, 1],
            c=colors[k], label=f"Cluster {k} (n={mask.sum()})",
            alpha=0.5, s=20
        )
    plt.scatter(
        centroids_pca[:, 0], centroids_pca[:, 1],
        c="black", marker="X", s=200, linewidths=2,
        edgecolors="white", label="Centroids", zorder=5
    )
    plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)")
    plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)")
    plt.title("K-Means Clusters — Normal Fan Operation (PCA Projection)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    scatter_path = os.path.join(DATA_DIR, "cluster_scatter.png")
    plt.savefig(scatter_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved scatter plot → {scatter_path}")

    # ─── Summary ─────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  K-Means Training Complete!")
    print(f"{'='*60}")
    print(f"  K = {OPTIMAL_K} clusters")
    print(f"  Silhouette = {final_sil:.4f}")
    print(f"  Model:     {model_path}")
    print(f"  Centroids: {centroids_path}")
    print(f"  Scaler:    {scaler_path}")
    print(f"{'='*60}\n")
    print("  Next step: python validate_model.py")


if __name__ == "__main__":
    main()
