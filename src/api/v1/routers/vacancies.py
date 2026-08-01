# src/api/v1/routers/vacancies.py
from fastapi import APIRouter, Depends, Query

from src.api.v1.dependencies import get_vacancy_service
from src.repositories.vacancy import VacancyFilter
from src.schemas.vacancy import VacancyListRead, VacancyRead
from src.services.vacancy import VacancyService

router = APIRouter(prefix="/vacancies", tags=["vacancies"])


@router.get("", response_model=VacancyListRead)
async def get_vacancies(
    skill_ids: list[int] | None = Query(default=None),
    remote_type: str | None = None,
    salary_min: int | None = Query(default=None, ge=0),
    salary_max: int | None = Query(default=None, ge=0),
    salary_currency: str | None = None,
    company_id: int | None = None,
    provider_id: int | None = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    service: VacancyService = Depends(get_vacancy_service),
) -> VacancyListRead:
    """Отримати список вакансій з фільтрами і пагінацією."""
    filters = VacancyFilter(
        skill_ids=skill_ids,
        remote_type=remote_type,
        salary_min=salary_min,
        salary_max=salary_max,
        salary_currency=salary_currency,
        company_id=company_id,
        provider_id=provider_id,
    )
    skip = (page - 1) * per_page
    vacancies, total = await service.get_vacancies(
        filters=filters,
        skip=skip,
        limit=per_page,
    )
    pages = (total + per_page - 1) // per_page
    return VacancyListRead(
        items=[VacancyRead.model_validate(v) for v in vacancies],
        total=total,
        page=page,
        per_page=per_page,
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
