# src/repositories/analytics.py
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.operational.company import Company
from src.models.operational.skill import Skill
from src.models.operational.vacancy import Vacancy
from src.models.operational.vacancy_skill import VacancySkill


class AnalyticsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_top_skills(self, limit: int = 20) -> list[dict]:
        result = await self.session.execute(
            select(
                Skill.id,
                Skill.name,
                Skill.normalized_name,
                func.count(VacancySkill.vacancy_id).label("vacancy_count"),
            )
            .join(VacancySkill, Skill.id == VacancySkill.skill_id)
            .join(Vacancy, VacancySkill.vacancy_id == Vacancy.id)
            .where(Vacancy.is_active == True)  # noqa: E712
            .group_by(Skill.id)
            .order_by(func.count(VacancySkill.vacancy_id).desc())
            .limit(limit)
        )
        return [row._asdict() for row in result.all()]

    async def get_market_overview(self) -> dict:
        total = (
            await self.session.execute(select(func.count()).select_from(Vacancy))
        ).scalar_one()

        active = (
            await self.session.execute(
                select(func.count())
                .select_from(Vacancy)
                .where(Vacancy.is_active == True)  # noqa: E712
            )
        ).scalar_one()

        companies = (
            await self.session.execute(select(func.count()).select_from(Company))
        ).scalar_one()

        skills = (
            await self.session.execute(select(func.count()).select_from(Skill))
        ).scalar_one()

        return {
            "total_vacancies": total,
            "active_vacancies": active,
            "total_companies": companies,
            "total_skills": skills,
        }
