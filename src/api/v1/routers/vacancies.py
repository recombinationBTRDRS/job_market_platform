# src/api/v1/routers/vacancies.py
from fastapi import APIRouter, Depends

from src.api.v1.dependencies import get_vacancy_service
from src.repositories.vacancy import VacancyFilter
from src.schemas.vacancy import VacancyFilterParams, VacancyListRead, VacancyRead
from src.services.vacancy import VacancyService

router = APIRouter(prefix="/vacancies", tags=["vacancies"])


@router.get("", response_model=VacancyListRead)
async def get_vacancies(
    params: VacancyFilterParams = Depends(),
    service: VacancyService = Depends(get_vacancy_service),
) -> VacancyListRead:
    """Отримати список вакансій з фільтрами і пагінацією."""
    filters = VacancyFilter(
        skill_ids=params.skill_ids,
        remote_type=params.remote_type,
        salary_min=params.salary_min,
        salary_max=params.salary_max,
        salary_currency=params.salary_currency,
        company_id=params.company_id,
        provider_id=params.provider_id,
    )
    skip = (params.page - 1) * params.per_page
    vacancies, total = await service.get_vacancies(
        filters=filters,
        skip=skip,
        limit=params.per_page,
    )
    pages = (total + params.per_page - 1) // params.per_page
    return VacancyListRead(
        items=[VacancyRead.model_validate(v) for v in vacancies],
        total=total,
        page=params.page,
        per_page=params.per_page,
        pages=pages,
    )


@router.get("/{vacancy_id}", response_model=VacancyRead)
async def get_vacancy(
    vacancy_id: int,
    service: VacancyService = Depends(get_vacancy_service),
) -> VacancyRead:
    """Отримати вакансію по ID."""
    vacancy = await service.get_vacancy(vacancy_id)
    return VacancyRead.model_validate(vacancy)
