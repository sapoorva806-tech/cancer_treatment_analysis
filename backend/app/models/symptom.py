import uuid
import enum

from sqlalchemy import Column, Integer, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.session import Base


class SeverityEnum(str, enum.Enum):
    NOT_PRESENT = "NOT_PRESENT"
    MILD = "MILD"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"


class Symptom(Base):
    __tablename__ = "symptoms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True, unique=True)

    age = Column(Integer, nullable=False)

    swollen_lymph_nodes = Column(Enum(SeverityEnum), nullable=False, default=SeverityEnum.NOT_PRESENT)
    fever = Column(Enum(SeverityEnum), nullable=False, default=SeverityEnum.NOT_PRESENT)
    night_sweats = Column(Enum(SeverityEnum), nullable=False, default=SeverityEnum.NOT_PRESENT)
    weight_loss = Column(Enum(SeverityEnum), nullable=False, default=SeverityEnum.NOT_PRESENT)
    fatigue = Column(Enum(SeverityEnum), nullable=False, default=SeverityEnum.NOT_PRESENT)
    itching = Column(Enum(SeverityEnum), nullable=False, default=SeverityEnum.NOT_PRESENT)
    shortness_of_breath = Column(Enum(SeverityEnum), nullable=False, default=SeverityEnum.NOT_PRESENT)
    chest_discomfort = Column(Enum(SeverityEnum), nullable=False, default=SeverityEnum.NOT_PRESENT)
    cough = Column(Enum(SeverityEnum), nullable=False, default=SeverityEnum.NOT_PRESENT)
    abdominal_symptoms = Column(Enum(SeverityEnum), nullable=False, default=SeverityEnum.NOT_PRESENT)
    loss_of_appetite = Column(Enum(SeverityEnum), nullable=False, default=SeverityEnum.NOT_PRESENT)

    assessment = relationship("Assessment", back_populates="symptoms")