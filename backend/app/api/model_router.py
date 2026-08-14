from fastapi import APIRouter, HTTPException, status

from app.core.config import ML_MODELS_DIR
import json

router = APIRouter(prefix="/model", tags=["model"])


@router.get("/info")
def model_info():
    metrics_path = ML_MODELS_DIR / "metrics.json"
    if not metrics_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No trained model metrics found. Train a model first.",
        )
    with open(metrics_path) as f:
        data = json.load(f)

    return {
        "model_version": data.get("model_version"),
        "test_metrics": data.get("test_metrics"),
        "note": data.get("note"),
        "disclaimer": (
            "These are real evaluation metrics from the model's held-out test "
            "set, not fabricated figures. If the model was trained on synthetic "
            "demo data, these numbers have no medical validity."
        ),
    }