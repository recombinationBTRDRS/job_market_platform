# src/etl/aggregators.py
import logging
from datetime import date

from sqlalchemy import func, select, text

from src.db.session import AsyncSessionFactory
from src.models.operational.company import Company
from src.models.operational.provider import Provider
from src.models.operational.skill import Skill
from src.models.operational.vacancy import Vacancy
from src.models.operational.vacancy_skill import VacancySkill

logger = logging.getLogger(__name__)


async def aggregate_fact_vacancies(target_date: date) -> int:
    async with AsyncSessionFactory() as session:
        result = await session.execute(
            select(
                Vacancy.id,
                Vacancy.external_id,
                Vacancy.title,
                Vacancy.description,
                Vacancy.salary_min,
                Vacancy.salary_max,
                Vacancy.salary_currency,
                Vacancy.remote_type,
                Vacancy.employment_type,
                Vacancy.is_active,
                Vacancy.published_at,
                Company.name.label("company_name"),
                Provider.name.label("provider_name"),
            )
            .outerjoin(Company, Vacancy.company_id == Company.id)
            .outerjoin(Provider, Vacancy.provider_id == Provider.id)
            .where(Vacancy.is_active == True)  # noqa: E712
        )
        vacancies = result.all()

        await session.execute(
            text("DELETE FROM analytics.fact_vacancies WHERE collected_date = :d"),
            {"d": target_date},
        )

        for v in vacancies:
            await session.execute(
                text("""
                    INSERT INTO analytics.fact_vacancies
                    (vacancy_id, external_id, title, company_name, provider_name,
                     description, salary_min, salary_max, salary_currency,
                     remote_type, employment_type, is_active, published_at, collected_date)
                    VALUES (:vid, :ext, :title, :company, :provider,
                            :desc, :smin, :smax, :scur,
                            :remote, :employ, :active, :pub, :cdate)
                """),
                {
                    "vid": v.id,
                    "ext": v.external_id,
                    "title": v.title,
                    "company": v.company_name,
                    "provider": v.provider_name,
                    "desc": v.description,
                    "smin": v.salary_min,
                    "smax": v.salary_max,
                    "scur": v.salary_currency,
                    "remote": v.remote_type,
                    "employ": v.employment_type,
                    "active": v.is_active,
                    "pub": v.published_at,
                    "cdate": target_date,
                },
            )

        await session.commit()
        logger.info("Aggregated %d vacancies for %s", len(vacancies), target_date)
        return len(vacancies)


async def aggregate_skills_daily(target_date: date) -> int:
    async with AsyncSessionFactory() as session:
        result = await session.execute(
            select(
                Skill.id.label("skill_id"),
                Skill.name.label("skill_name"),
                func.count(VacancySkill.vacancy_id).label("vacancy_count"),
            )
            .join(VacancySkill, Skill.id == VacancySkill.skill_id)
            .join(Vacancy, VacancySkill.vacancy_id == Vacancy.id)
            .where(Vacancy.is_active == True)  # noqa: E712
            .group_by(Skill.id, Skill.name)
        )
        skills = result.all()

        await session.execute(
            text("DELETE FROM analytics.agg_skills_daily WHERE aggregation_date = :d"),
            {"d": target_date},
        )

        for s in skills:
            await session.execute(
                text("""
                    INSERT INTO analytics.agg_skills_daily
                    (skill_id, skill_name, aggregation_date, vacancy_count)
                    VALUES (:sid, :sname, :adate, :count)
                """),
                {
                    "sid": s.skill_id,
                    "sname": s.skill_name,
                    "adate": target_date,
                    "count": s.vacancy_count,
                },
            )

        await session.commit()
        logger.info("Aggregated %d skills for %s", len(skills), target_date)
        return len(skills)


async def aggregate_salary_by_skill() -> int:
    async with AsyncSessionFactory() as session:
        result = await session.execute(
            select(
                Skill.id.label("skill_id"),
                Skill.name.label("skill_name"),
                func.avg(Vacancy.salary_min).label("avg_salary_min"),
                func.avg(Vacancy.salary_max).label("avg_salary_max"),
                func.count(Vacancy.id).label("sample_count"),
            )
            .join(VacancySkill, Skill.id == VacancySkill.skill_id)
            .join(Vacancy, VacancySkill.vacancy_id == Vacancy.id)
            .where(Vacancy.is_active == True, Vacancy.salary_min.isnot(None))  # noqa: E712
            .group_by(Skill.id, Skill.name)
            .having(func.count(Vacancy.id) >= 3)
        )
        skills = result.all()

        await session.execute(text("DELETE FROM analytics.agg_salary_by_skill"))

        for s in skills:
            await session.execute(
                text("""
                    INSERT INTO analytics.agg_salary_by_skill
                    (skill_id, skill_name, avg_salary_min, avg_salary_max, sample_count)
                    VALUES (:sid, :sname, :amin, :amax, :count)
                """),
                {
                    "sid": s.skill_id,
                    "sname": s.skill_name,
                    "amin": float(s.avg_salary_min)
                    if s.avg_salary_min is not None
                    else None,
                    "amax": float(s.avg_salary_max)
                    if s.avg_salary_max is not None
                    else None,
                    "count": s.sample_count,
                },
            )

        await session.commit()
        logger.info("Aggregated salary data for %d skills", len(skills))
        return len(skills)
