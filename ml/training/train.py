"""
Trains HodgkinRiskModel on the dataset produced by ml/preprocessing/preprocess.py.

Saves:
- ml/models/hodgkin_model.pth        (model weights)
- ml/models/preprocessing_stats.json (normalization stats, needed at inference time)
- ml/models/metrics.json             (evaluation metrics from the held-out test set)

IMPORTANT: If trained on the synthetic dataset (generate_dummy_data.py),
the resulting model and metrics have NO medical validity. This is for
pipeline testing / demo purposes only. Replace ml/data/dataset.csv with a
real, properly licensed dataset before treating any metric as meaningful.
"""
import json
import os
import sys

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "preprocessing"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "evaluation"))
sys.path.append(os.path.dirname(__file__))

from preprocess import (  # noqa: E402
    load_dataset, clean_dataset, encode_features, split_dataset,
    compute_normalization_stats, apply_normalization,
)
from model import HodgkinRiskModel  # noqa: E402
from metrics import compute_metrics, print_metrics  # noqa: E402

# ---- Hyperparameters ----
EPOCHS = 60
BATCH_SIZE = 16
LEARNING_RATE = 1e-3
WEIGHT_DECAY = 1e-4
SEED = 42

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dataset.csv")
MODEL_VERSION = "1.0.0-demo"


def set_seed(seed: int):
    torch.manual_seed(seed)
    np.random.seed(seed)


def make_loader(X: np.ndarray, y: np.ndarray, batch_size: int, shuffle: bool) -> DataLoader:
    X_t = torch.tensor(X, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32).unsqueeze(1)
    return DataLoader(TensorDataset(X_t, y_t), batch_size=batch_size, shuffle=shuffle)


def train():
    set_seed(SEED)
    os.makedirs(MODEL_DIR, exist_ok=True)

    print("Loading and preparing data...")
    df = load_dataset(DATA_PATH)
    df = clean_dataset(df)
    X, y = encode_features(df)
    X_train, X_val, X_test, y_train, y_val, y_test = split_dataset(X, y)

    stats = compute_normalization_stats(X_train)
    X_train = apply_normalization(X_train, stats)
    X_val = apply_normalization(X_val, stats)
    X_test = apply_normalization(X_test, stats)

    train_loader = make_loader(X_train, y_train, BATCH_SIZE, shuffle=True)
    val_loader = make_loader(X_val, y_val, BATCH_SIZE, shuffle=False)

    model = HodgkinRiskModel()
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)

    best_val_loss = float("inf")
    best_state = None

    print(f"Training for {EPOCHS} epochs...")
    for epoch in range(1, EPOCHS + 1):
        model.train()
        train_loss = 0.0
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            logits = model(X_batch)
            loss = criterion(logits, y_batch)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * X_batch.size(0)
        train_loss /= len(train_loader.dataset)

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                logits = model(X_batch)
                loss = criterion(logits, y_batch)
                val_loss += loss.item() * X_batch.size(0)
        val_loss /= len(val_loader.dataset)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = model.state_dict()

        if epoch % 10 == 0 or epoch == 1:
            print(f"Epoch {epoch:3d}/{EPOCHS} — train_loss: {train_loss:.4f}, val_loss: {val_loss:.4f}")

    # Restore best checkpoint (lowest validation loss)
    model.load_state_dict(best_state)

    # ---- Evaluate on held-out test set ----
    model.eval()
    with torch.no_grad():
        X_test_t = torch.tensor(X_test, dtype=torch.float32)
        test_logits = model(X_test_t)
        test_proba = torch.sigmoid(test_logits).numpy().flatten()

    test_metrics = compute_metrics(y_test, test_proba)
    print_metrics(test_metrics, label="Test Set (held-out)")

    # ---- Save model, stats, metrics ----
    model_path = os.path.join(MODEL_DIR, "hodgkin_model.pth")
    torch.save(model.state_dict(), model_path)
    print(f"\nModel saved to {model_path}")

    stats_path = os.path.join(MODEL_DIR, "preprocessing_stats.json")
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"Preprocessing stats saved to {stats_path}")

    metrics_path = os.path.join(MODEL_DIR, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump({
            "model_version": MODEL_VERSION,
            "test_metrics": test_metrics,
            "note": "Trained on ml/data/dataset.csv — verify whether this was "
                    "the synthetic demo dataset or a real one before citing these numbers.",
        }, f, indent=2)
    print(f"Metrics saved to {metrics_path}")


if __name__ == "__main__":
    train()