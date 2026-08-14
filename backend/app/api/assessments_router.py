from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database.session import get_db
from app.models.assessment import Assessment
from app.models.symptom import Symptom
from app.models.prediction import Prediction
from app.models.user import User
from app.schemas.assessment import AssessmentCreate, AssessmentOut, AssessmentListItem
from app.auth.dependencies import get_current_user
from app.services.ml_inference import predict_risk

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("", response_model=AssessmentOut, status_code=status.HTTP_201_CREATED)
def create_assessment(
        payload: AssessmentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    assessment = Assessment(user_id=current_user.id)
    db.add(assessment)
    db.flush()  # get assessment.id before creating child rows

    symptom_data = payload.symptoms.model_dump()
    symptom = Symptom(assessment_id=assessment.id, **symptom_data)
    db.add(symptom)
    db.flush()

    try:
        result = predict_risk(symptom_data)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Prediction model is not available: {e}",
        )

    prediction = Prediction(
        assessment_id=assessment.id,
        risk_score=result["risk_score"],
        risk_percentage=result["risk_percentage"],
        model_version=result["model_version"],
    )
    db.add(prediction)

    db.commit()
    db.refresh(assessment)

    return assessment


@router.get("", response_model=List[AssessmentListItem])
def list_assessments(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    assessments = (
        db.query(Assessment)
        .filter(Assessment.user_id == current_user.id)
        .options(joinedload(Assessment.prediction))
        .order_by(Assessment.assessment_date.desc())
        .all()
    )

    return [
        AssessmentListItem(
            id=a.id,
            assessment_date=a.assessment_date,
            risk_percentage=a.prediction.risk_percentage if a.prediction else None,
            model_version=a.prediction.model_version if a.prediction else None,
        )
        for a in assessments
    ]


@router.get("/{assessment_id}", response_model=AssessmentOut)
def get_assessment(
        assessment_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    assessment = (
        db.query(Assessment)
        .options(joinedload(Assessment.symptoms), joinedload(Assessment.prediction))
        .filter(Assessment.id == assessment_id, Assessment.user_id == current_user.id)
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    return assessment