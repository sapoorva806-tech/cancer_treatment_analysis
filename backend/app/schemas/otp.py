from pydantic import BaseModel, Field
from typing import Optional


class OTPRequestPayload(BaseModel):
    phone_number: str = Field(min_length=8, max_length=20)


class OTPVerifyPayload(BaseModel):
    phone_number: str = Field(min_length=8, max_length=20)
    code: str = Field(min_length=6, max_length=6)
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=255)