"""
Loads the trained model once at startup and runs inference on symptom data.

IMPORTANT: This service returns a MODEL-ESTIMATED PROBABILITY, not a
diagnosis. If the underlying model was trained on synthetic demo data
(see ml/data/README.md), the output has no medical validity.
"""
import json
import threading
from typing import Optional

import torch

from app.core.config import ML_MODELS_DIR
from app.services.ml_config import ALL_FEATURE_COLUMNS, SEVERITY_TO_ORDINAL
from app.services.ml_model import HodgkinRiskModel

_lock = threading.Lock()
_model: Optional[HodgkinRiskModel] = None
_stats: Optional[dict] = None
_model_version: str = "unknown"


def _load_artifacts():
    global _model, _stats, _model_version

    model_path = ML_MODELS_DIR / "hodgkin_model.pth"
    stats_path = ML_MODELS_DIR / "preprocessing_stats.json"
    metrics_path = ML_MODELS_DIR / "metrics.json"

    if not model_path.exists():
        raise FileNotFoundError(
            f"No trained model found at {model_path}. Run ml/training/train.py first."
        )
    if not stats_path.exists():
        raise FileNotFoundError(
            f"No preprocessing stats found at {stats_path}. Run ml/training/train.py first."
        )

    model = HodgkinRiskModel()
    model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model.eval()

    with open(stats_path) as f:
        stats = json.load(f)

    version = "unknown"
    if metrics_path.exists():
        with open(metrics_path) as f:
            version = json.load(f).get("model_version", "unknown")

    return model, stats, version


def get_model():
    """Lazily loads the model on first use (thread-safe), then reuses it."""
    global _model, _stats, _model_version
    if _model is None:
        with _lock:
            if _model is None:  # double-checked locking
                _model, _stats, _model_version = _load_artifacts()
    return _model, _stats, _model_version


def _encode_symptoms(symptom_data: dict) -> list[float]:
    row = []
    for col in ALL_FEATURE_COLUMNS:
        value = symptom_data[col]
        if col == "age":
            row.append(float(value))
        else:
            # symptom_data values may be SeverityEnum members or plain strings
            key = value.value if hasattr(value, "value") else value
            if key not in SEVERITY_TO_ORDINAL:
                raise ValueError(f"Unknown severity value '{key}' for column '{col}'")
            row.append(float(SEVERITY_TO_ORDINAL[key]))
    return row


def predict_risk(symptom_data: dict) -> dict:
    """
    symptom_data: dict with keys matching ALL_FEATURE_COLUMNS
                  (age as int, symptom fields as SeverityEnum or string)
    Returns: {"risk_score": float, "risk_percentage": float, "model_version": str}
    """
    model, stats, version = get_model()

    row = _encode_symptoms(symptom_data)

    age_idx = stats["age_index"]
    row[age_idx] = (row[age_idx] - stats["age_mean"]) / stats["age_std"]

    x = torch.tensor([row], dtype=torch.float32)
    with torch.no_grad():
        logit = model(x)
        probability = torch.sigmoid(logit).item()

    return {
        "risk_score": round(probability, 4),
        "risk_percentage": round(probability * 100, 2),
        "model_version": version,
    }