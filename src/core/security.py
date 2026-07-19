# src/core/security.py
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from src.core.config import get_settings
from src.core.exceptions import AuthenticationError

settings = get_settings()


def hash_password(password: str) -> str:
    """Хешування паролю через bcrypt."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Перевірка паролю проти хешу."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_access_token(
    subject: str | int,
    extra_data: dict[str, Any] | None = None,
) -> str:
    """Створення access JWT токена."""
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": "access",
    }
    if extra_data:
        payload.update(extra_data)

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(subject: str | int) -> str:
    """Створення refresh JWT токена."""
    expire = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_token_expire_days)
    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def verify_token(token: str, token_type: str = "access") -> dict[str, Any]:
    """Верифікація JWT токена. Повертає payload або кидає AuthenticationError."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("type") != token_type:
            raise AuthenticationError(
                detail=f"Invalid token type. Expected {token_type}"
            )
        return payload
    except JWTError as e:
        raise AuthenticationError(detail=f"Invalid token: {e}") from e


def get_subject_from_token(token: str, token_type: str = "access") -> str:
    """Отримання subject (user_id) з токена."""
    payload = verify_token(token, token_type)
    subject = payload.get("sub")
    if subject is None:
        raise AuthenticationError(detail="Token missing subject")
    return subject
