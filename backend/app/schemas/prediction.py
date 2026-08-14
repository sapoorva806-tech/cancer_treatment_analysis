import uuid
from datetime import datetime

from pydantic import BaseModel


class PredictionOut(BaseModel):
    id: uuid.UUID
    risk_score: float
    risk_percentage: float
    model_version: str
    created_at: datetime

    model_config = {"from_attributes": True}