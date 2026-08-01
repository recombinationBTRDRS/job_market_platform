# src/api/v1/routers/companies.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.dependencies import get_db
from src.models.operational.company import Company
from src.repositories.company import CompanyRepository
from src.schemas.company import CompanyRead

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyRead])
async def get_companies(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db),
) -> list[CompanyRead]:
    """Отримати список компаній."""
    repo = CompanyRepository(model=Company, session=session)
    companies = await repo.get_all(skip=skip, limit=limit)
    return [CompanyRead.model_validate(c) for c in companies]


@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(
    company_id: int,
    session: AsyncSession = Depends(get_db),
) -> CompanyRead:
    """Отримати компанію по ID."""
    from src.core.exceptions import NotFoundError

    repo = CompanyRepository(model=Company, session=session)
    company = await repo.get_by_id(company_id)
    if company is None:
        raise NotFoundError(detail=f"Company with id={company_id} not found")
    return CompanyRead.model_validate(company)
