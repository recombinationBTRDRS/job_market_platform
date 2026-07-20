# src/repositories/company.py
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from src.models.operational.company import Company
from src.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    """Repository для роботи з компаніями."""

    async def get_by_name(self, name: str) -> Company | None:
        """Отримати компанію по назві."""
        result = await self.session.execute(select(Company).where(Company.name == name))
        return result.scalar_one_or_none()

    async def get_or_create(self, name: str, website: str | None = None) -> Company:
        """Отримати або створити компанію. Безпечно при паралельних запитах."""
        stmt = (
            insert(Company)
            .values(name=name, website=website)
            .on_conflict_do_nothing(index_elements=["name"])
            .returning(Company)
        )
        result = await self.session.execute(stmt)
        company = result.scalar_one_or_none()

        if company is None:
            company = await self.get_by_name(name)

        return company  # type: ignore[return-value]
