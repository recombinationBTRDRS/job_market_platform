# src/services/auth.py
from src.core.exceptions import AuthenticationError, DuplicateError
from src.core.security import (
    create_access_token,
    create_refresh_token,
    get_subject_from_token,
    hash_password,
    verify_password,
)
from src.models.operational.user import User
from src.repositories.user import UserRepository


class AuthService:
    """Сервіс автентифікації і авторизації."""

    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def register(
        self,
        email: str,
        password: str,
        full_name: str,
    ) -> User:
        """Зареєструвати нового користувача."""
        existing = await self.repository.get_by_email(email)
        if existing is not None:
            raise DuplicateError(detail=f"User with email {email} already exists")

        hashed = hash_password(password)
        return await self.repository.create(
            email=email,
            hashed_password=hashed,
            full_name=full_name,
            is_active=True,
            is_admin=False,
        )

    async def login(self, email: str, password: str) -> dict:
        """Автентифікувати користувача і повернути токени."""
        user = await self.repository.get_by_email(email)
        if user is None:
            raise AuthenticationError(detail="Invalid email or password")

        if not verify_password(password, user.hashed_password):
            raise AuthenticationError(detail="Invalid email or password")

        if not user.is_active:
            raise AuthenticationError(detail="User is inactive")

        access_token = create_access_token(
            subject=user.id,
            extra_data={"email": user.email, "is_admin": user.is_admin},
        )
        refresh_token = create_refresh_token(subject=user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh(self, refresh_token: str) -> dict:
        """Оновити access token через refresh token."""
        user_id = get_subject_from_token(refresh_token, token_type="refresh")

        user = await self.repository.get_by_id(int(user_id))
        if user is None or not user.is_active:
            raise AuthenticationError(detail="Invalid refresh token")

        access_token = create_access_token(
            subject=user.id,
            extra_data={"email": user.email, "is_admin": user.is_admin},
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
