"""
Loads a CSV in the expected format, validates it, encodes features, and
splits into train/validation/test sets.
"""
import os
import sys

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

sys.path.append(os.path.dirname(__file__))
from config import (  # noqa: E402
    ALL_FEATURE_COLUMNS,
    NUMERIC_COLUMNS,
    SYMPTOM_COLUMNS,
    SEVERITY_TO_ORDINAL,
    TARGET_COLUMN,
)


def load_dataset(csv_path: str) -> pd.DataFrame:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Dataset not found at {csv_path}. See ml/data/README.md for the "
            f"expected format, or run generate_dummy_data.py to create a "
            f"synthetic dataset for pipeline testing."
        )
    df = pd.read_csv(csv_path)

    required_columns = ALL_FEATURE_COLUMNS + [TARGET_COLUMN]
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")

    return df


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df = df.dropna(subset=[TARGET_COLUMN])

    for col in NUMERIC_COLUMNS:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())

    for col in SYMPTOM_COLUMNS:
        df[col] = df[col].fillna("NOT_PRESENT")

    return df


def encode_features(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Returns (X, y) as numpy arrays, in ALL_FEATURE_COLUMNS order."""
    df = df.copy()

    for col in SYMPTOM_COLUMNS:
        df[col] = df[col].map(SEVERITY_TO_ORDINAL)
        if df[col].isnull().any():
            raise ValueError(
                f"Column '{col}' contains values outside "
                f"{list(SEVERITY_TO_ORDINAL.keys())}: check your CSV."
            )

    X = df[ALL_FEATURE_COLUMNS].to_numpy(dtype=np.float32)
    y = df[TARGET_COLUMN].to_numpy(dtype=np.float32)
    return X, y


def split_dataset(X: np.ndarray, y: np.ndarray, test_size=0.15, val_size=0.15, seed=42):
    """Returns X_train, X_val, X_test, y_train, y_val, y_test"""
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=test_size, random_state=seed, stratify=y
    )
    val_ratio_of_temp = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_ratio_of_temp, random_state=seed, stratify=y_temp
    )
    return X_train, X_val, X_test, y_train, y_val, y_test


def compute_normalization_stats(X_train: np.ndarray) -> dict:
    age_idx = ALL_FEATURE_COLUMNS.index("age")
    mean = float(X_train[:, age_idx].mean())
    std = float(X_train[:, age_idx].std()) or 1.0
    return {"age_mean": mean, "age_std": std, "age_index": age_idx}


def apply_normalization(X: np.ndarray, stats: dict) -> np.ndarray:
    X = X.copy()
    idx = stats["age_index"]
    X[:, idx] = (X[:, idx] - stats["age_mean"]) / stats["age_std"]
    return X


if __name__ == "__main__":
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "dataset.csv")
    df = load_dataset(csv_path)
    df = clean_dataset(df)
    X, y = encode_features(df)
    X_train, X_val, X_test, y_train, y_val, y_test = split_dataset(X, y)
    stats = compute_normalization_stats(X_train)

    print(f"Loaded {len(df)} rows.")
    print(f"Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
    print(f"Normalization stats: {stats}")
    print(f"Positive rate — train: {y_train.mean():.2f}, val: {y_val.mean():.2f}, test: {y_test.mean():.2f}")