# src/api/v1/routers/providers.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.dependencies import get_current_admin, get_db
from src.core.exceptions import NotFoundError
from src.models.operational.provider import Provider
from src.models.operational.user import User
from src.repositories.base import BaseRepository

router = APIRouter(prefix="/providers", tags=["admin", "providers"])


class ProviderCreate(BaseModel):
    name: str
    type: str
    url: str | None = None
    is_active: bool = True


class ProviderUpdate(BaseModel):
    url: str | None = None
    is_active: bool | None = None


class ProviderRead(BaseModel):
    id: int
    name: str
    type: str
    url: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


@router.get("", response_model=list[ProviderRead])
async def get_providers(
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> list[ProviderRead]:
    """Отримати всі провайдери."""
    repo = BaseRepository(model=Provider, session=session)
    providers = await repo.get_all()
    return [ProviderRead.model_validate(p) for p in providers]


@router.post("", response_model=ProviderRead, status_code=201)
async def create_provider(
    body: ProviderCreate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> ProviderRead:
    """Створити нового провайдера."""
    repo = BaseRepository(model=Provider, session=session)
    provider = await repo.create(
        name=body.name,
        type=body.type,
        url=body.url,
        is_active=body.is_active,
    )
    return ProviderRead.model_validate(provider)


@router.patch("/{provider_id}", response_model=ProviderRead)
async def update_provider(
    provider_id: int,
    body: ProviderUpdate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> ProviderRead:
    """Оновити провайдера."""
    repo = BaseRepository(model=Provider, session=session)
    update_data = body.model_dump(exclude_none=True)
    provider = await repo.update(provider_id, **update_data)
    if provider is None:
        raise NotFoundError(detail=f"Provider with id={provider_id} not found")
    return ProviderRead.model_validate(provider)


@router.delete("/{provider_id}", status_code=204)
async def delete_provider(
    provider_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> None:
    """Видалити провайдера."""
    repo = BaseRepository(model=Provider, session=session)
    deleted = await repo.delete(provider_id)
    if not deleted:
        raise NotFoundError(detail=f"Provider with id={provider_id} not found")
