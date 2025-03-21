import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
import database.models as models
from database.database import get_session_local
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "KROWAJETRAWE"  # TODO Change this to a strong secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

roles_values = {
    "": 0,
    "shifter": 1,
    "coordinator": 2,
    "admin": 4
}

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, required_role: str = "", db: Session = Depends(get_session_local)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_data: int = payload.get("user")
        user = db.query(models.User).filter(
            models.User.name == user_data["name"],
            models.User.email == user_data["email"],
            models.User.role == user_data["role"]
        ).first()
        if not user:
            raise credentials_exception
        if roles_values[required_role] > roles_values[user_data["role"]]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not authorized to perform the action.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except jwt.PyJWTError:
        raise credentials_exception
