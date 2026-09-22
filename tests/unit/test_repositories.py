# tests/unit/test_repositories.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.operational import Company, Provider, Skill, Vacancy
from src.repositories.skill import SkillRepository
from src.repositories.vacancy import VacancyFilter, VacancyRepository


@pytest.mark.asyncio
async def test_vacancy_get_by_external_id(
    db_session: AsyncSession,
    test_vacancy: Vacancy,
    test_provider: Provider,
) -> None:
    """Тест отримання вакансії по external_id."""
    repo = VacancyRepository(model=Vacancy, session=db_session)

    found = await repo.get_by_external_id(
        external_id=test_vacancy.external_id,
        provider_id=test_provider.id,
    )

    assert found is not None
    assert found.id == test_vacancy.id
    assert found.external_id == test_vacancy.external_id


@pytest.mark.asyncio
async def test_vacancy_get_by_external_id_not_found(
    db_session: AsyncSession,
    test_provider: Provider,
) -> None:
    """Тест що повертає None якщо не знайдено."""
    repo = VacancyRepository(model=Vacancy, session=db_session)

    found = await repo.get_by_external_id(
        external_id="non-existent-id",
        provider_id=test_provider.id,
    )

    assert found is None


@pytest.mark.asyncio
async def test_vacancy_get_with_filters_remote_type(
    db_session: AsyncSession,
    test_vacancy: Vacancy,
) -> None:
    """Тест фільтрації по remote_type."""
    repo = VacancyRepository(model=Vacancy, session=db_session)

    vacancies, total = await repo.get_with_filters(
        filters=VacancyFilter(remote_type="remote"),
        skip=0,
        limit=10,
    )

    assert total >= 1
    assert all(v.remote_type == "remote" for v in vacancies)


@pytest.mark.asyncio
async def test_vacancy_get_with_filters_salary(
    db_session: AsyncSession,
    test_vacancy: Vacancy,
) -> None:
    """Тест фільтрації по зарплаті."""
    repo = VacancyRepository(model=Vacancy, session=db_session)

    vacancies, total = await repo.get_with_filters(
        filters=VacancyFilter(salary_min=2000),
        skip=0,
        limit=10,
    )

    assert total >= 1
    assert all(v.salary_min >= 2000 for v in vacancies)


@pytest.mark.asyncio
async def test_vacancy_bulk_create(
    db_session: AsyncSession,
    test_provider: Provider,
    test_company: Company,
) -> None:
    """Тест батчового створення вакансій."""
    repo = VacancyRepository(model=Vacancy, session=db_session)

    vacancies_data = [
        {
            "external_id": f"bulk-{i}",
            "provider_id": test_provider.id,
            "company_id": test_company.id,
            "url": f"https://test.com/jobs/{i}",
            "title": f"Developer {i}",
            "is_active": True,
        }
        for i in range(5)
    ]

    created = await repo.bulk_create(vacancies_data)

    assert len(created) == 5
    assert all(v.external_id.startswith("bulk-") for v in created)


@pytest.mark.asyncio
async def test_skill_get_or_create_new(
    db_session: AsyncSession,
) -> None:
    """Тест get_or_create створює новий скіл."""
    repo = SkillRepository(model=Skill, session=db_session)

    skill = await repo.get_or_create(
        name="FastAPI",
        normalized_name="fastapi",
    )

    assert skill is not None
    assert skill.name == "FastAPI"
    assert skill.normalized_name == "fastapi"


@pytest.mark.asyncio
async def test_skill_get_or_create_existing(
    db_session: AsyncSession,
    test_skill: Skill,
) -> None:
    """Тест get_or_create повертає існуючий скіл без дублікату."""
    repo = SkillRepository(model=Skill, session=db_session)

    skill1 = await repo.get_or_create(
        name=test_skill.name,
        normalized_name=test_skill.normalized_name,
    )
    skill2 = await repo.get_or_create(
        name=test_skill.name,
        normalized_name=test_skill.normalized_name,
    )

    assert skill1.id == skill2.id
    assert skill1.id == test_skill.id
