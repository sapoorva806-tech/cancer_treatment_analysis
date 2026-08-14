import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_admin
from app.models.user import User
from app.core.config import ML_MODELS_DIR
from app.schemas.admin import AdminOverview, ModelPerformance
from app.analytics.queries import (
    get_total_users,
    get_total_assessments_all,
    get_assessments_per_day,
    get_top_symptoms_all,
    get_aggregate_risk_distribution,
    get_prediction_distribution_stats,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/analytics", response_model=AdminOverview)
def admin_analytics(
        db: Session = Depends(get_db),
        _admin: User = Depends(get_current_admin),
):
    return AdminOverview(
        total_users=get_total_users(db),
        total_assessments=get_total_assessments_all(db),
        assessments_per_day=get_assessments_per_day(db),
        top_symptoms=get_top_symptoms_all(db),
        aggregate_risk_distribution=get_aggregate_risk_distribution(db),
        prediction_distribution=get_prediction_distribution_stats(db),
    )


@router.get("/model-performance", response_model=ModelPerformance)
def admin_model_performance(_admin: User = Depends(get_current_admin)):
    metrics_path = ML_MODELS_DIR / "metrics.json"
    if not metrics_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No trained model metrics found.",
        )
    with open(metrics_path) as f:
        data = json.load(f)

    return ModelPerformance(
        model_version=data.get("model_version"),
        test_metrics=data.get("test_metrics"),
        note=data.get("note"),
    )