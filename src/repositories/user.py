# src/repositories/user.py
from sqlalchemy import select

from src.models.operational.user import User
from src.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository для роботи з користувачами."""

    async def get_by_email(self, email: str) -> User | None:
        """Отримати користувача по email."""
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
