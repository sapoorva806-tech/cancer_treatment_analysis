from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.analytics import UserAnalytics
from app.analytics.queries import (
    get_user_total_assessments,
    get_user_average_risk,
    get_user_risk_history,
    get_user_symptom_frequency,
    get_user_risk_distribution,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=UserAnalytics)
def get_my_analytics(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    return UserAnalytics(
        total_assessments=get_user_total_assessments(db, current_user.id),
        average_risk_percentage=get_user_average_risk(db, current_user.id),
        risk_history=get_user_risk_history(db, current_user.id),
        symptom_frequency=get_user_symptom_frequency(db, current_user.id),
        risk_distribution=get_user_risk_distribution(db, current_user.id),
    )