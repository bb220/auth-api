import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, FastAPI, Depends, HTTPException, status, Body, Request, Security
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from app import models, schemas, crud, database, auth
from app.auth import verify_password, hash_password
from app.cors import add_cors_middleware
from app.cooldown_manager import resend_verification_cache, reset_password_cache, check_and_update_cooldown
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.email_sender import send_verification_email, send_reset_email
from app.jwt_handler import create_access_token, create_refresh_token, verify_token
from app.models import User
from app.reset_token_handler import create_password_reset_token, verify_password_reset_token
from app.schemas import UserLogin
from app.verification_token_handler import create_email_verification_token, verify_email_verification_token


# --------------------------------------------------
# Lifespan Setup
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    models.Base.metadata.create_all(bind=database.engine)
    yield
    # (Optional shutdown logic later if you need it)

# --------------------------------------------------
# App Setup
# --------------------------------------------------

app = FastAPI(lifespan=lifespan)
add_cors_middleware(app)

API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="Authorization")
router = APIRouter()

# --------------------------------------------------
# Middleware
# --------------------------------------------------

@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    if request.url.path in ["/openapi.json", "/docs"]:
        return await call_next(request)

    api_key = request.headers.get("x-api-key")
    if api_key != API_KEY:
        return JSONResponse(status_code=403, content={"detail": "Forbidden. Invalid or missing API Key."})

    return await call_next(request)

# --------------------------------------------------
# Utility
# --------------------------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------------------------------------
# Authentication and User Management Routes
# --------------------------------------------------

@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = crud.create_user(db, user)

    token = create_email_verification_token(new_user.email)
    send_verification_email(new_user.email, token)

    return new_user

@app.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
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

    return {"message": "Email verified successfully. You can now log in."}

@app.post("/resend-verification-email")
def resend_verification_email(email: str, db: Session = Depends(get_db)):
    cooldown_period = timedelta(minutes=5)

    # Apply cooldown
    check_and_update_cooldown(
        cache=resend_verification_cache,
        email=email,
        cooldown_period=cooldown_period,
        error_message="Please wait before requesting another verification email."
    )

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"message": "If an account with that email exists, a verification email has been resent."}
    
    if user.is_verified:
        return {"message": "Account already verified. Please log in."}

    token = create_email_verification_token(user.email)
    send_verification_email(user.email, token)

    return {"message": "Verification email resent. Please check your inbox."}

@app.post("/login")
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(models.User.email == user_credentials.email).first()

    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please verify your email before logging in.")

    token_data = {
        "user_id": user.id,
        "last_password_reset": str(user.last_password_reset)
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/refresh")
def refresh_token(refresh_token: str = Body(...), db: Session = Depends(get_db)):
    payload = verify_token(refresh_token, db)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("user_id")

    # Re-fetch the user from the database
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

# --------------------------------------------------
# Password Reset Routes
# --------------------------------------------------

@router.post("/request-password-reset")
def request_password_reset(email: str, db: Session = Depends(get_db)):
    cooldown_period = timedelta(minutes=1)

    # Apply cooldown
    check_and_update_cooldown(
        cache=reset_password_cache,
        email=email,
        cooldown_period=cooldown_period,
        error_message="Please wait before requesting another password reset email."
    )

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"message": "If the email is associated with an account, a reset link has been sent."}

    reset_token = create_password_reset_token(user.email)
    reset_link = f"https://yourfrontend.com/reset-password?token={reset_token}"
    send_reset_email(user.email, reset_link)

    return {"message": "If the email is associated with an account, a reset link has been sent."}

@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    email = verify_password_reset_token(token)
    if email is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired password reset token.")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.hashed_password = hash_password(new_password)
    user.last_password_reset = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Password reset successful."}

# --------------------------------------------------
# Protected Route Example
# --------------------------------------------------

@app.get("/protected")
def protected_route(token: str = Security(api_key_header), db: Session = Depends(get_db)):
    if not token.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Invalid authorization header format")

    real_token = token.split("Bearer ")[1]
    payload = verify_token(real_token, db)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("user_id")
    return {"message": f"Welcome user {user_id}!"}

# --------------------------------------------------
# Include Router
# --------------------------------------------------

app.include_router(router)
