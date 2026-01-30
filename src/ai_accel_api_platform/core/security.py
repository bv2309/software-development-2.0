from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from ai_accel_api_platform.settings import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bool(pwd_context.verify(plain_password, hashed_password))


def get_password_hash(password: str) -> str:
    return str(pwd_context.hash(password))


def create_access_token(subject: str, expires_minutes: int = 60) -> str:
    settings = get_settings()
    expire = datetime.now(tz=UTC) + timedelta(minutes=expires_minutes)
    to_encode = {"sub": subject, "exp": expire}
    token: str = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_alg)
    return token


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    payload: dict[str, Any] = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
    return payload


def credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def decode_subject_from_token(token: str) -> str:
    try:
        payload = decode_access_token(token)
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception()
    except JWTError as exc:
        raise credentials_exception() from exc
    return username
