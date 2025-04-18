from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, crud, database, auth
from .jwt_handler import create_access_token, verify_access_token
from fastapi.security import APIKeyHeader
from fastapi import Security

api_key_header = APIKeyHeader(name="Authorization")

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

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
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Create JWT token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    return {"access_token": access_token, "token_type": "bearer"}

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
    payload = verify_access_token(real_token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    return {"message": f"Welcome user {user_id}!"}
    