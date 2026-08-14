import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.symptom import SymptomCreate, SymptomOut
from app.schemas.prediction import PredictionOut


class AssessmentCreate(BaseModel):
    symptoms: SymptomCreate


class AssessmentOut(BaseModel):
    id: uuid.UUID
    assessment_date: datetime
    created_at: datetime
    symptoms: Optional[SymptomOut] = None
    prediction: Optional[PredictionOut] = None

    model_config = {"from_attributes": True}


class AssessmentListItem(BaseModel):
    """Lighter-weight shape used for the history list."""
    id: uuid.UUID
    assessment_date: datetime
    risk_percentage: Optional[float] = None
    model_version: Optional[str] = None