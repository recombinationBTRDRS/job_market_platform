# src/api/v1/dependencies.py
from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AuthenticationError, AuthorizationError
from src.core.security import get_subject_from_token
from src.db.session import AsyncSessionFactory
from src.models.operational.user import User
from src.models.operational.vacancy import Vacancy
from src.repositories.base import BaseRepository
from src.repositories.vacancy import VacancyRepository
from src.services.vacancy import VacancyService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — AsyncSession на один запит."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    """Отримати поточного авторизованого користувача."""
    if credentials is None:
        raise AuthenticationError(detail="Authorization header missing")

    user_id = get_subject_from_token(credentials.credentials, token_type="access")

    repo = BaseRepository(model=User, session=session)
    user = await repo.get_by_id(int(user_id))

    if user is None:
        raise AuthenticationError(detail="User not found")

    if not user.is_active:
        raise AuthenticationError(detail="User is inactive")

    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Перевірити що поточний користувач є адміністратором."""
    if not current_user.is_admin:
        raise AuthorizationError(detail="Admin access required")
    return current_user


def get_vacancy_service(
    session: AsyncSession = Depends(get_db),
) -> VacancyService:
    """Dependency для VacancyService."""
    repo = VacancyRepository(model=Vacancy, session=session)
    return VacancyService(repository=repo)
