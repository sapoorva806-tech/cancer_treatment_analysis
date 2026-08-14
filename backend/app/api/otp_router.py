import random
import string
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.models.otp import OTPCode
from app.schemas.otp import OTPRequestPayload, OTPVerifyPayload
from app.schemas.token import Token
from app.auth.security import create_access_token
from app.services.sms import send_otp
from app.core.limiter import limiter

router = APIRouter(prefix="/auth/otp", tags=["auth"])

OTP_EXPIRY_MINUTES = 5


def generate_code() -> str:
    return "".join(random.choices(string.digits, k=6))


@router.post("/request", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
def request_otp(request: Request, payload: OTPRequestPayload, db: Session = Depends(get_db)):
    code = generate_code()
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)

    otp = OTPCode(phone_number=payload.phone_number, code=code, expires_at=expires_at)
    db.add(otp)
    db.commit()

    send_otp(payload.phone_number, code)

    return {"message": "OTP sent. Check the backend console (mock SMS) for the code."}


@router.post("/verify", response_model=Token)
@limiter.limit("10/minute")
def verify_otp(request: Request, payload: OTPVerifyPayload, db: Session = Depends(get_db)):
    otp = (
        db.query(OTPCode)
        .filter(
            OTPCode.phone_number == payload.phone_number,
            OTPCode.code == payload.code,
            OTPCode.is_used == False,  # noqa: E712
        )
        .order_by(OTPCode.created_at.desc())
        .first()
    )

    if not otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP code")

    if otp.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP code has expired")

    otp.is_used = True
    db.commit()

    user = db.query(User).filter(User.phone_number == payload.phone_number).first()

    if not user:
        if not payload.full_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="full_name is required to register a new account via phone",
            )
        user = User(full_name=payload.full_name, phone_number=payload.phone_number)
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token)