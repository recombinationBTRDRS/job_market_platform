# src/repositories/parse_run.py
from sqlalchemy import select

from src.models.operational.parse_run import ParseRun
from src.repositories.base import BaseRepository


class ParseRunRepository(BaseRepository[ParseRun]):
    """Repository для роботи з логами ETL запусків."""

    async def get_by_provider(
        self,
        provider_id: int,
        limit: int = 10,
    ) -> list[ParseRun]:
        """Отримати останні запуски для провайдера."""
        result = await self.session.execute(
            select(ParseRun)
            .where(ParseRun.provider_id == provider_id)
            .order_by(ParseRun.started_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_recent(self, limit: int = 20) -> list[ParseRun]:
        """Отримати останні запуски всіх провайдерів."""
        result = await self.session.execute(
            select(ParseRun).order_by(ParseRun.started_at.desc()).limit(limit)
        )
        return list(result.scalars().all())
