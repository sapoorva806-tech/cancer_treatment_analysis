from typing import List, Optional
from pydantic import BaseModel


class AdminOverview(BaseModel):
    total_users: int
    total_assessments: int
    assessments_per_day: List[dict]          # [{"date": "...", "count": N}]
    top_symptoms: List[dict]                  # [{"symptom": "...", "count": N}]
    aggregate_risk_distribution: List[dict]   # [{"bucket": "...", "count": N}]
    prediction_distribution: dict             # {"mean": ..., "min": ..., "max": ...}


class ModelPerformance(BaseModel):
    model_version: Optional[str]
    test_metrics: Optional[dict]
    note: Optional[str]