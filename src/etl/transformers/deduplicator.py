# src/etl/transformers/deduplicator.py
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.etl.providers.base import NormalizedVacancy
from src.models.operational.vacancy import Vacancy
from src.repositories.vacancy import VacancyRepository

logger = logging.getLogger(__name__)


def deduplicate_in_memory(
    vacancies: list[NormalizedVacancy],
) -> list[NormalizedVacancy]:
    """Прибрати дублікати всередині одного батчу по external_id."""
    seen: set[str] = set()
    unique = []
    for vacancy in vacancies:
        if vacancy.external_id not in seen:
            seen.add(vacancy.external_id)
            unique.append(vacancy)
        else:
            logger.debug("In-memory duplicate skipped: %s", vacancy.external_id)

    duplicates_count = len(vacancies) - len(unique)
    if duplicates_count > 0:
        logger.info("Removed %d in-memory duplicates", duplicates_count)

    return unique


async def filter_existing_vacancies(
    vacancies: list[NormalizedVacancy],
    provider_id: int,
    session: AsyncSession,
) -> tuple[list[NormalizedVacancy], int]:
    """
    Відфільтрувати вакансії які вже є в БД.
    Повертає (нові вакансії, кількість дублікатів).
    """
    repo = VacancyRepository(model=Vacancy, session=session)
    new_vacancies = []
    duplicates_count = 0

    for vacancy in vacancies:
        existing = await repo.get_by_external_id(
            external_id=vacancy.external_id,
            provider_id=provider_id,
        )
        if existing is None:
            new_vacancies.append(vacancy)
        else:
            duplicates_count += 1
            logger.debug(
                "DB duplicate skipped: %s (provider_id=%d)",
                vacancy.external_id,
                provider_id,
            )

    logger.info(
        "DB deduplication: %d new, %d duplicates (provider_id=%d)",
        len(new_vacancies),
        duplicates_count,
        provider_id,
    )
    return new_vacancies, duplicates_count
