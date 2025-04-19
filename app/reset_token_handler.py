from datetime import datetime, timedelta
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

load_dotenv()

# Existing secret key for your app
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Password reset token expiration time (e.g., 15 minutes)
RESET_TOKEN_EXPIRE_MINUTES = 15

def create_password_reset_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password_reset_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None
