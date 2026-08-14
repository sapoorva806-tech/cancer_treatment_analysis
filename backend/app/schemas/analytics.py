from typing import List, Optional
from pydantic import BaseModel


class RiskHistoryPoint(BaseModel):
    date: str
    risk_percentage: float


class SymptomFrequencyItem(BaseModel):
    symptom: str
    count: int  # number of assessments where this symptom was MILD/MODERATE/SEVERE


class RiskDistributionBucket(BaseModel):
    bucket: str  # e.g. "0-25", "25-50"
    count: int


class UserAnalytics(BaseModel):
    total_assessments: int
    average_risk_percentage: Optional[float]
    risk_history: List[RiskHistoryPoint]
    symptom_frequency: List[SymptomFrequencyItem]
    risk_distribution: List[RiskDistributionBucket]