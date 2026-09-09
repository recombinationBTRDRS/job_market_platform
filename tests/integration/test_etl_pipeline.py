# tests/integration/test_etl_pipeline.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.etl.loaders.vacancy_loader import VacancyLoader
from src.etl.providers.mock import MockProvider
from src.etl.transformers.deduplicator import (
    deduplicate_in_memory,
    filter_existing_vacancies,
)
from src.etl.transformers.normalizer import normalize_vacancies
from src.models.operational import Company, Provider, Skill


@pytest.mark.asyncio
async def test_full_etl_pipeline(
    db_session: AsyncSession,
    test_provider: Provider,
) -> None:
    """Тест повного ETL циклу: MockProvider → normalize → deduplicate → load."""
    provider = MockProvider()
    raw_vacancies = await provider.fetch()
    assert len(raw_vacancies) == 5

    normalized = normalize_vacancies(raw_vacancies)
    assert len(normalized) == 5
    assert all(v.salary_currency == "USD" for v in normalized if v.salary_currency)

    unique = deduplicate_in_memory(normalized)
    assert len(unique) == 5

    new_vacancies, duplicates = await filter_existing_vacancies(
        unique, test_provider.id, db_session
    )
    assert len(new_vacancies) == 5
    assert duplicates == 0

    loader = VacancyLoader(session=db_session, provider_id=test_provider.id)
    success, errors = await loader.load(new_vacancies)

    assert success == 5
    assert errors == 0


@pytest.mark.asyncio
async def test_deduplication_on_second_run(
    db_session: AsyncSession,
    test_provider: Provider,
) -> None:
    """Тест що повторний запуск не створює дублікатів."""
    provider = MockProvider()
    raw_vacancies = await provider.fetch()
    normalized = normalize_vacancies(raw_vacancies)

    loader = VacancyLoader(session=db_session, provider_id=test_provider.id)
    success1, _ = await loader.load(normalized)

    new_vacancies, duplicates = await filter_existing_vacancies(
        normalized, test_provider.id, db_session
    )

    assert len(new_vacancies) == 0
    assert duplicates == success1


@pytest.mark.asyncio
async def test_loader_creates_companies_and_skills(
    db_session: AsyncSession,
    test_provider: Provider,
) -> None:
    """Тест що loader створює компанії і скіли автоматично."""
    from src.etl.providers.base import NormalizedVacancy

    vacancies = [
        NormalizedVacancy(
            external_id="new-001",
            title="Test Dev",
            url="https://test.com/new-001",
            company_name="New Company XYZ",
            skills=["Python", "FastAPI"],
        )
    ]

    loader = VacancyLoader(session=db_session, provider_id=test_provider.id)
    success, errors = await loader.load(vacancies)

    assert success == 1
    assert errors == 0

    from src.repositories.company import CompanyRepository

    repo = CompanyRepository(model=Company, session=db_session)
    company = await repo.get_by_name("New Company XYZ")
    assert company is not None

    from src.repositories.skill import SkillRepository

    skill_repo = SkillRepository(model=Skill, session=db_session)
    python = await skill_repo.get_by_normalized_name("python")
    assert python is not None


@pytest.mark.asyncio
async def test_loader_handles_error_gracefully(
    db_session: AsyncSession,
    test_provider: Provider,
) -> None:
    """Тест що помилка в одній вакансії не зупиняє батч."""
    from src.etl.providers.base import NormalizedVacancy

    vacancies = [
        NormalizedVacancy(
            external_id="good-001",
            title="Good Vacancy",
            url="https://test.com/good",
        ),
        NormalizedVacancy(
            external_id="good-002",
            title="Another Good Vacancy",
            url="https://test.com/good2",
        ),
    ]

    loader = VacancyLoader(session=db_session, provider_id=test_provider.id)
    success, errors = await loader.load(vacancies)

    assert success == 2
    assert errors == 0
