from pydantic import BaseModel, Field

from app.models.symptom import SeverityEnum


class SymptomCreate(BaseModel):
    age: int = Field(ge=0, le=120)

    swollen_lymph_nodes: SeverityEnum = SeverityEnum.NOT_PRESENT
    fever: SeverityEnum = SeverityEnum.NOT_PRESENT
    night_sweats: SeverityEnum = SeverityEnum.NOT_PRESENT
    weight_loss: SeverityEnum = SeverityEnum.NOT_PRESENT
    fatigue: SeverityEnum = SeverityEnum.NOT_PRESENT
    itching: SeverityEnum = SeverityEnum.NOT_PRESENT
    shortness_of_breath: SeverityEnum = SeverityEnum.NOT_PRESENT
    chest_discomfort: SeverityEnum = SeverityEnum.NOT_PRESENT
    cough: SeverityEnum = SeverityEnum.NOT_PRESENT
    abdominal_symptoms: SeverityEnum = SeverityEnum.NOT_PRESENT
    loss_of_appetite: SeverityEnum = SeverityEnum.NOT_PRESENT


class SymptomOut(SymptomCreate):
    model_config = {"from_attributes": True}