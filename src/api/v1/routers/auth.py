# src/api/v1/routers/auth.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.dependencies import get_current_user, get_db
from src.models.operational.user import User
from src.repositories.user import UserRepository
from src.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserRead,
)
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    repo = UserRepository(model=User, session=session)
    return AuthService(repository=repo)


@router.post("/register", status_code=201, response_model=UserRead)
async def register(
    body: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> UserRead:
    user = await service.register(
        email=body.email,
        password=body.password,
        full_name=body.full_name,
    )
    return UserRead.model_validate(user)


@router.get("/me", response_model=UserRead)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserRead:
    return UserRead.model_validate(current_user)


@router.post("/login")
async def login(
    body: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Автентифікація і отримання токенів."""
    tokens = await service.login(
        email=body.email,
        password=body.password,
    )
    return TokenResponse(**tokens)


@router.post("/refresh")
async def refresh(
    body: RefreshRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Оновлення access token."""
    tokens = await service.refresh(refresh_token=body.refresh_token)
    return TokenResponse(**tokens)
