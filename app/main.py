import os
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, crud, database, auth
from .jwt_handler import create_access_token, create_refresh_token, verify_token
from fastapi.security import APIKeyHeader
from fastapi import Body, Request, Security
from fastapi.responses import JSONResponse
from app.schemas import UserLogin
from app.auth import verify_password
from app.cors import add_cors_middleware

api_key_header = APIKeyHeader(name="Authorization")

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

add_cors_middleware(app)

API_KEY = os.getenv("API_KEY")

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

@app.post("/reset-password")
def reset_password(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.hashed_password = auth.hash_password(user.password)
    db.commit()
    return {"message": "Password reset successful"}

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
    