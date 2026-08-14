"""
Aggregate analytics queries — user-level (Phase 12) and admin-wide (Phase 13).
"""
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.assessment import Assessment
from app.models.symptom import Symptom, SeverityEnum
from app.models.prediction import Prediction
from app.models.user import User

SYMPTOM_FIELDS = [
    "swollen_lymph_nodes", "fever", "night_sweats", "weight_loss", "fatigue",
    "itching", "shortness_of_breath", "chest_discomfort", "cough",
    "abdominal_symptoms", "loss_of_appetite",
]


# ---------------------------------------------------------------------------
# User-level analytics (Phase 12)
# ---------------------------------------------------------------------------

def get_user_risk_history(db: Session, user_id) -> list[dict]:
    rows = (
        db.query(Assessment.assessment_date, Prediction.risk_percentage)
        .join(Prediction, Prediction.assessment_id == Assessment.id)
        .filter(Assessment.user_id == user_id)
        .order_by(Assessment.assessment_date.asc())
        .all()
    )
    return [{"date": d.isoformat(), "risk_percentage": r} for d, r in rows]


def get_user_average_risk(db: Session, user_id) -> float | None:
    avg = (
        db.query(func.avg(Prediction.risk_percentage))
        .join(Assessment, Assessment.id == Prediction.assessment_id)
        .filter(Assessment.user_id == user_id)
        .scalar()
    )
    return round(float(avg), 2) if avg is not None else None


def get_user_symptom_frequency(db: Session, user_id) -> list[dict]:
    """For each symptom field, count assessments where severity != NOT_PRESENT."""
    result = []
    for field in SYMPTOM_FIELDS:
        column = getattr(Symptom, field)
        count = (
            db.query(func.count(Symptom.id))
            .join(Assessment, Assessment.id == Symptom.assessment_id)
            .filter(Assessment.user_id == user_id, column != SeverityEnum.NOT_PRESENT)
            .scalar()
        )
        result.append({"symptom": field, "count": count or 0})
    return result


def get_user_risk_distribution(db: Session, user_id) -> list[dict]:
    buckets = [("0-25", 0, 25), ("25-50", 25, 50), ("50-75", 50, 75), ("75-100", 75, 100.01)]
    result = []
    for label, lo, hi in buckets:
        count = (
            db.query(func.count(Prediction.id))
            .join(Assessment, Assessment.id == Prediction.assessment_id)
            .filter(
                Assessment.user_id == user_id,
                Prediction.risk_percentage >= lo,
                Prediction.risk_percentage < hi,
                )
            .scalar()
        )
        result.append({"bucket": label, "count": count or 0})
    return result


def get_user_total_assessments(db: Session, user_id) -> int:
    return db.query(func.count(Assessment.id)).filter(Assessment.user_id == user_id).scalar() or 0


# ---------------------------------------------------------------------------
# Admin-wide analytics (Phase 13)
# ---------------------------------------------------------------------------

def get_total_users(db: Session) -> int:
    return db.query(func.count(User.id)).scalar() or 0


def get_total_assessments_all(db: Session) -> int:
    return db.query(func.count(Assessment.id)).scalar() or 0


def get_assessments_per_day(db: Session, limit_days: int = 30) -> list[dict]:
    rows = (
        db.query(func.date(Assessment.assessment_date).label("day"), func.count(Assessment.id))
        .group_by("day")
        .order_by("day")
        .limit(limit_days)
        .all()
    )
    return [{"date": str(day), "count": count} for day, count in rows]


def get_top_symptoms_all(db: Session) -> list[dict]:
    result = []
    for field in SYMPTOM_FIELDS:
        column = getattr(Symptom, field)
        count = (
            db.query(func.count(Symptom.id))
            .filter(column != SeverityEnum.NOT_PRESENT)
            .scalar()
        )
        result.append({"symptom": field, "count": count or 0})
    return sorted(result, key=lambda x: x["count"], reverse=True)


def get_aggregate_risk_distribution(db: Session) -> list[dict]:
    buckets = [("0-25", 0, 25), ("25-50", 25, 50), ("50-75", 50, 75), ("75-100", 75, 100.01)]
    result = []
    for label, lo, hi in buckets:
        count = (
            db.query(func.count(Prediction.id))
            .filter(Prediction.risk_percentage >= lo, Prediction.risk_percentage < hi)
            .scalar()
        )
        result.append({"bucket": label, "count": count or 0})
    return result


def get_prediction_distribution_stats(db: Session) -> dict:
    row = db.query(
        func.avg(Prediction.risk_percentage),
        func.min(Prediction.risk_percentage),
        func.max(Prediction.risk_percentage),
    ).first()
    mean, mn, mx = row
    return {
        "mean": round(float(mean), 2) if mean is not None else None,
        "min": round(float(mn), 2) if mn is not None else None,
        "max": round(float(mx), 2) if mx is not None else None,
    }