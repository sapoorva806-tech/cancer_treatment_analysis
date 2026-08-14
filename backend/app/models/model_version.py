import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID

from app.database.session import Base


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version = Column(String(50), unique=True, nullable=False)
    model_name = Column(String(255), nullable=False)
    training_date = Column(DateTime, nullable=True)
    metrics = Column(JSON, nullable=True)   # {"accuracy": ..., "precision": ..., "recall": ..., "f1": ..., "roc_auc": ...}
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)