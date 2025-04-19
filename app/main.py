import os
from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, crud, database, auth
from app.jwt_handler import create_access_token, create_refresh_token, verify_token
from fastapi.security import APIKeyHeader
from fastapi import Body, Request, Security
from fastapi.responses import JSONResponse
from app.schemas import UserLogin
from app.auth import verify_password, hash_password
from app.cors import add_cors_middleware
from app.database import get_db
from app.models import User
from app.reset_token_handler import create_password_reset_token, verify_password_reset_token

api_key_header = APIKeyHeader(name="Authorization")

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

add_cors_middleware(app)

API_KEY = os.getenv("API_KEY")

router = APIRouter()

@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    # Allow Swagger UI and docs to load without API key
    if request.url.path in ["/openapi.json", "/docs"]:
        return await call_next(request)

    # Read the x-api-key header
    api_key = request.headers.get("x-api-key")
    
    if api_key != API_KEY:
        return JSONResponse(status_code=403, content={"detail": "Forbidden. Invalid or missing API Key."})

    return await call_next(request)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)

@app.post("/login")
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"user_id": user.id})
    refresh_token = create_refresh_token(data={"user_id": user.id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/refresh")
def refresh_token(refresh_token: str = Body(...)):
    payload = verify_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("user_id")
    new_access_token = create_access_token(data={"user_id": user_id})

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@router.post("/request-password-reset")
def request_password_reset(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Do NOT reveal if email is invalid (security best practice)
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="If the email is associated with an account, a reset link has been sent."
        )

    # Create reset token
    reset_token = create_password_reset_token(user.email)

    # Create reset link
    reset_link = f"https://yourfrontend.com/reset-password?token={reset_token}"

    # For now, mock email sending
    print(f"Password reset link for {user.email}: {reset_link}")

    return {"message": "If the email is associated with an account, a reset link has been sent."}

@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    email = verify_password_reset_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token."
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    user.hashed_password = hash_password(new_password)
    db.commit()

    return {"message": "Password reset successful."}

@app.get("/protected")
def protected_route(token: str = Security(api_key_header)):
    if not token.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Invalid authorization header format")

    real_token = token.split("Bearer ")[1]
    payload = verify_token(real_token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("user_id")
    return {"message": f"Welcome user {user_id}!"}

app.include_router(router)