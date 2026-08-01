# src/api/v1/routers/analytics.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.dependencies import get_db
from src.models.operational.skill import Skill
from src.models.operational.vacancy import Vacancy
from src.models.operational.vacancy_skill import VacancySkill
from src.schemas.analytics import MarketOverview, TopSkill

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/skills/top", response_model=list[TopSkill])
async def get_top_skills(
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> list[TopSkill]:
    """Топ скілів по кількості вакансій."""
    result = await session.execute(
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
    return [
        TopSkill(
            id=row.id,
            name=row.name,
            normalized_name=row.normalized_name,
            vacancy_count=row.vacancy_count,
        )
        for row in result.all()
    ]


@router.get("/market-overview", response_model=MarketOverview)
async def get_market_overview(
    session: AsyncSession = Depends(get_db),
) -> MarketOverview:
    """Загальний огляд ринку вакансій."""
    from src.models.operational.company import Company

    total_result = await session.execute(select(func.count()).select_from(Vacancy))
    total_vacancies = total_result.scalar_one()

    active_result = await session.execute(
        select(func.count()).select_from(Vacancy).where(Vacancy.is_active == True)  # noqa: E712
    )
    active_vacancies = active_result.scalar_one()

    companies_result = await session.execute(select(func.count()).select_from(Company))
    total_companies = companies_result.scalar_one()

    skills_result = await session.execute(select(func.count()).select_from(Skill))
    total_skills = skills_result.scalar_one()

    return MarketOverview(
        total_vacancies=total_vacancies,
        active_vacancies=active_vacancies,
        total_companies=total_companies,
        total_skills=total_skills,
        last_updated="operational_db",
    )
