# src/services/vacancy.py
from src.core.exceptions import NotFoundError
from src.models.operational.vacancy import Vacancy
from src.repositories.vacancy import VacancyFilter, VacancyRepository


class VacancyService:
    """Сервіс для роботи з вакансіями."""

    def __init__(self, repository: VacancyRepository) -> None:
        self.repository = repository

    async def get_vacancy(self, id: int) -> Vacancy:
        """Отримати вакансію по ID або кинути NotFoundError."""
        vacancy = await self.repository.get_by_id(id)
        if vacancy is None:
            raise NotFoundError(detail=f"Vacancy with id={id} not found")
        return vacancy

    async def get_vacancy_with_skills(self, id: int) -> Vacancy:
        """Отримати вакансію зі скілами або кинути NotFoundError."""
        vacancy = await self.repository.get_with_skills(id)
        if vacancy is None:
            raise NotFoundError(detail=f"Vacancy with id={id} not found")
        return vacancy

    async def get_vacancies(
        self,
        filters: VacancyFilter,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Vacancy], int]:
        """Отримати список вакансій з фільтрами і пагінацією."""
        if limit > 100:
            limit = 100
        return await self.repository.get_with_filters(
            filters=filters,
            skip=skip,
            limit=limit,
        )

    async def deactivate_vacancy(self, id: int) -> Vacancy:
        """Деактивувати вакансію."""
        await self.get_vacancy(id)  # перевірка що існує
        updated = await self.repository.update(id, is_active=False)
        if updated is None:
            raise NotFoundError(detail=f"Vacancy with id={id} not found")
        return updated
