# src/repositories/vacancy.py
from dataclasses import dataclass

from sqlalchemy import and_, select
from sqlalchemy.orm import selectinload

from src.models.operational.vacancy import Vacancy
from src.repositories.base import BaseRepository


@dataclass
class VacancyFilter:
    """Фільтри для пошуку вакансій."""

    skill_ids: list[int] | None = None
    remote_type: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = None
    company_id: int | None = None
    provider_id: int | None = None
    is_active: bool | None = True


class VacancyRepository(BaseRepository[Vacancy]):
    """Repository для роботи з вакансіями."""

    async def get_by_external_id(
        self,
        external_id: str,
        provider_id: int,
    ) -> Vacancy | None:
        """Отримати вакансію по external_id і provider_id."""
        result = await self.session.execute(
            select(Vacancy).where(
                and_(
                    Vacancy.external_id == external_id,
                    Vacancy.provider_id == provider_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_with_skills(self, id: int) -> Vacancy | None:
        """Отримати вакансію зі всіма скілами через JOIN."""
        result = await self.session.execute(
            select(Vacancy)
            .options(
                selectinload(Vacancy.vacancy_skills).selectinload(
                    Vacancy.vacancy_skills.property.mapper.class_.skill
                )
            )
            .where(Vacancy.id == id)
        )
        return result.scalar_one_or_none()

    async def get_with_filters(
        self,
        filters: VacancyFilter,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Vacancy], int]:
        """Отримати вакансії з фільтрами. Повертає (список, загальна кількість)."""
        from sqlalchemy import func

        from src.models.operational.vacancy_skill import VacancySkill

        query = select(Vacancy)
        conditions = []

        if filters.is_active is not None:
            conditions.append(Vacancy.is_active == filters.is_active)
        if filters.remote_type is not None:
            conditions.append(Vacancy.remote_type == filters.remote_type)
        if filters.salary_min is not None:
            conditions.append(Vacancy.salary_min >= filters.salary_min)
        if filters.salary_max is not None:
            conditions.append(Vacancy.salary_max <= filters.salary_max)
        if filters.salary_currency is not None:
            conditions.append(Vacancy.salary_currency == filters.salary_currency)
        if filters.company_id is not None:
            conditions.append(Vacancy.company_id == filters.company_id)
        if filters.provider_id is not None:
            conditions.append(Vacancy.provider_id == filters.provider_id)
        if filters.skill_ids:
            query = query.join(
                VacancySkill,
                Vacancy.id == VacancySkill.vacancy_id,
            ).where(VacancySkill.skill_id.in_(filters.skill_ids))

        if conditions:
            query = query.where(and_(*conditions))

        count_result = await self.session.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar_one()

        result = await self.session.execute(
            query.offset(skip).limit(limit).order_by(Vacancy.published_at.desc())
        )
        return list(result.scalars().all()), total

    async def bulk_create(self, vacancies_data: list[dict]) -> list[Vacancy]:
        """Батчове створення вакансій."""
        instances = [Vacancy(**data) for data in vacancies_data]
        self.session.add_all(instances)
        await self.session.flush()
        return instances
