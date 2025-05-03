import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, FastAPI, Depends, HTTPException, status, Body, Request, Security, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app import models, schemas, crud, database, auth
from app.auth import verify_password, hash_password
from app.utils.event_logger import mask_email, record_event
from app.cors import add_cors_middleware
from app.cooldown_manager import resend_verification_cache, reset_password_cache, check_and_update_cooldown
from app.database import SessionLocal
from app.email_sender import send_verification_email, send_reset_email
from app.jwt_handler import create_access_token, create_refresh_token, verify_token
from app.models import User
from app.reset_token_handler import create_password_reset_token, verify_password_reset_token
from app.schemas import PasswordResetRequest, ResetPassword, UserLogin, EmailRequest
from app.verification_token_handler import create_email_verification_token, verify_email_verification_token

@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=database.engine)
    yield

app = FastAPI(lifespan=lifespan)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
add_cors_middleware(app)

api_key_header = APIKeyHeader(name="Authorization")
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@limiter.limit("15/hour")
@app.post("/register", response_model=schemas.UserResponse)
def register(request: Request, user: schemas.UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = crud.create_user(db, user)

    token = create_email_verification_token(new_user.email)
    send_verification_email(new_user.email, token)
    print(f"Verification token for {new_user.email}: {token}")

    background_tasks.add_task(
        record_event,
        "user_registered",
        new_user.id,
        {"email": mask_email(new_user.email)}
    )

    return new_user

@limiter.limit("10/minute")
@app.get("/verify-email")
def verify_email(request: Request, token: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    email = verify_email_verification_token(token)
    if email is None:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.is_verified:
        return {"message": "Account already verified."}

    user.is_verified = True
    user.verified_at = datetime.now(timezone.utc)
    db.commit()

    background_tasks.add_task(
        record_event,
        "email_verified",
        user.id,
        {"email": mask_email(user.email)}
    )

    return {"message": "Email verified successfully. You can now log in."}

@limiter.limit("3/minute")
@app.post("/resend-verification-email")
def resend_verification_email(request: Request, email_request: EmailRequest, db: Session = Depends(get_db)):
    cooldown_period = timedelta(minutes=5)

    check_and_update_cooldown(
        cache=resend_verification_cache,
        email=email_request.email,
        cooldown_period=cooldown_period,
        error_message="Please wait before requesting another verification email."
    )

    user = db.query(User).filter(User.email == email_request.email).first()

    if not user:
        return {"message": "If an account with that email exists, a verification email has been resent."}
    
    if user.is_verified:
        return {"message": "Account already verified. Please log in."}

    token = create_email_verification_token(user.email)
    send_verification_email(user.email, token)

    return {"message": "Verification email resent. Please check your inbox."}

@limiter.limit("5/minute")
@app.post("/login")
def login(request: Request, user_credentials: UserLogin, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(models.User.email == user_credentials.email).first()

    if not user or not verify_password(user_credentials.password, user.hashed_password):
        record_event(
            "user_login_failure",
            None,
            {"email": mask_email(user_credentials.email), "reason": "Invalid credentials"}
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_verified:
        record_event(
            "user_login_failure",
            None,
            {"email": mask_email(user_credentials.email), "reason": "Unverified email"}
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please verify your email before logging in.")

    token_data = {
        "user_id": user.id,
        "last_password_reset": str(user.last_password_reset)
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    background_tasks.add_task(
        record_event,
        "user_login_success",
        user.id,
        {"email": mask_email(user.email)}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@limiter.limit("30/minute")
@app.post("/refresh")
def refresh_token(request: Request, refresh_token: str = Body(...), db: Session = Depends(get_db)):
    payload = verify_token(refresh_token, db)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("user_id")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    token_data = {
        "user_id": user.id,
        "last_password_reset": str(user.last_password_reset)
    }

    new_access_token = create_access_token(data=token_data)

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@limiter.limit("3/minute")
@router.post("/request-password-reset")
def request_password_reset(
    request: Request,
    payload: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    email = payload.email
    cooldown_period = timedelta(minutes=1)

    check_and_update_cooldown(
        cache=reset_password_cache,
        email=email,
        cooldown_period=cooldown_period,
        error_message="Please wait before requesting another password reset email."
    )

    user = db.query(User).filter(User.email == email).first()

    if not user:
        record_event(
            "password_reset_requested",
            None,
            {"email": mask_email(email), "user_found": False}
        )
        return {"message": "If the email is associated with an account, a reset link has been sent."}

    reset_token = create_password_reset_token(user.email)
    reset_link = f"https://yourfrontend.com/reset-password?token={reset_token}"
    send_reset_email(user.email, reset_link)
    print(reset_token)

    background_tasks.add_task(
        record_event,
        "password_reset_requested",
        user.id,
        {"email": mask_email(user.email)}
    )

    return {"message": "If the email is associated with an account, a reset link has been sent."}

@limiter.limit("5/minute")
@router.post("/reset-password")
def reset_password(
    request: Request,
    payload: ResetPassword,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    email = verify_password_reset_token(payload.token)
    if email is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired password reset token.")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.hashed_password = hash_password(payload.new_password)
    user.last_password_reset = datetime.now(timezone.utc)
    db.commit()

    background_tasks.add_task(
        record_event,
        "password_reset_completed",
        user.id,
        {"email": mask_email(user.email)}
    )

    return {"message": "Password reset successful."}

@limiter.limit("60/minute")
@app.get("/protected")
def protected_route(request: Request, background_tasks: BackgroundTasks, token: str = Security(api_key_header), db: Session = Depends(get_db)):
    if not token.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Invalid authorization header format")

    real_token = token.split("Bearer ")[1]
    payload = verify_token(real_token, db)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("user_id")

    background_tasks.add_task(
        record_event,
        "protected_route_accessed",
        user_id,
        {"endpoint": "/protected"}
    )

    return {"message": f"Welcome user {user_id}!"}

app.include_router(router)
