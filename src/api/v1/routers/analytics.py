# src/api/v1/routers/analytics.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.dependencies import get_db
from src.repositories.analytics import AnalyticsRepository
from src.schemas.analytics import MarketOverview, TopSkill

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/skills/top", response_model=list[TopSkill])
async def get_top_skills(
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> list[TopSkill]:
    repo = AnalyticsRepository(session=session)
    rows = await repo.get_top_skills(limit=limit)
    return [TopSkill(**row) for row in rows]


@router.get("/market-overview", response_model=MarketOverview)
async def get_market_overview(
    session: AsyncSession = Depends(get_db),
) -> MarketOverview:
    repo = AnalyticsRepository(session=session)
    data = await repo.get_market_overview()
    return MarketOverview(**data, last_updated="operational_db")
