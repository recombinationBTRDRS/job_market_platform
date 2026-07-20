# src/services/parse_run.py
from datetime import UTC, datetime

from src.models.operational.parse_run import ParseRun
from src.repositories.parse_run import ParseRunRepository


class ParseRunService:
    """Сервіс для логування ETL pipeline запусків."""

    def __init__(self, repository: ParseRunRepository) -> None:
        self.repository = repository

    async def start_run(self, provider_id: int) -> ParseRun:
        """Створити запис про початок ETL запуску."""
        return await self.repository.create(
            provider_id=provider_id,
            started_at=datetime.now(UTC),
            status="running",
            vacancies_found=0,
            vacancies_new=0,
            vacancies_failed=0,
        )

    async def finish_run(
        self,
        run_id: int,
        vacancies_found: int,
        vacancies_new: int,
        vacancies_failed: int = 0,
    ) -> ParseRun | None:
        """Оновити запис після успішного завершення."""
        return await self.repository.update(
            run_id,
            finished_at=datetime.now(UTC),
            status="success",
            vacancies_found=vacancies_found,
            vacancies_new=vacancies_new,
            vacancies_failed=vacancies_failed,
        )

    async def fail_run(
        self,
        run_id: int,
        error_message: str,
        vacancies_found: int = 0,
        vacancies_new: int = 0,
    ) -> ParseRun | None:
        """Оновити запис після помилки."""
        return await self.repository.update(
            run_id,
            finished_at=datetime.now(UTC),
            status="failed",
            error_message=error_message[:1000],
            vacancies_found=vacancies_found,
            vacancies_new=vacancies_new,
        )

    async def get_history(
        self,
        provider_id: int | None = None,
        limit: int = 20,
    ) -> list[ParseRun]:
        """Отримати історію запусків."""
        if provider_id is not None:
            return await self.repository.get_by_provider(
                provider_id=provider_id,
                limit=limit,
            )
        return await self.repository.get_recent(limit=limit)
