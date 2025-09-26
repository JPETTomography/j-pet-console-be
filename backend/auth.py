from datetime import datetime, timedelta, timezone
from enum import Enum

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import database.models as models
from database.database import get_session_local

SECRET_KEY = "KROWAJETRAWE"  # TODO Change this to a strong secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Role(Enum):
    USER = 0
    SHIFTER = 1
    COORDINATOR = 2
    ADMIN = 4


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, required_role: Role = Role.USER):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        if exp is None:
            raise credentials_exception

        current_time = datetime.now(tz=timezone.utc)
        expiration_time = datetime.fromtimestamp(exp, tz=timezone.utc)
        if expiration_time < current_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = payload.get("user")
        if user is None:
            raise credentials_exception

        user_role_str = user.get("role")
        if not user_role_str:
            user_role = Role.USER
        else:
            try:
                user_role = Role[user_role_str.upper()]
            except KeyError:
                user_role = Role.USER

        if required_role.value > user_role.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not authorized to perform the action.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role",
        )


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = verify_access_token(token)
        return payload["user"]
    except HTTPException as e:
        raise e


def get_current_user_with_role(required_role: Role):
    def verify_user_role(token: str = Depends(oauth2_scheme)):
        try:
            payload = verify_access_token(token, required_role)
            return payload["user"]
        except HTTPException as e:
            raise e

    return verify_user_role
