from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # -> backend/
PROJECT_ROOT = BASE_DIR.parent                              # -> project/ (local dev only)
ENV_PATH = BASE_DIR / ".env"

_ml_override = os.environ.get("ML_MODELS_DIR_OVERRIDE")
ML_MODELS_DIR = Path(_ml_override) if _ml_override else (PROJECT_ROOT / "ml" / "models")


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "http://localhost:5500"
    API_PREFIX: str = "/api"
    MODEL_PATH: str = "ml/models/hodgkin_model.pth"
    MODEL_VERSION: str = "1.0.0"

    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()