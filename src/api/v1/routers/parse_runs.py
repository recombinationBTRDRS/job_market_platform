# src/api/v1/routers/parse_runs.py
import asyncio

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.dependencies import get_current_admin, get_db
from src.models.operational.parse_run import ParseRun
from src.models.operational.user import User
from src.repositories.parse_run import ParseRunRepository
from src.schemas.parse_run import ParseRunRead

router = APIRouter(prefix="/parse-runs", tags=["admin", "parse-runs"])

_background_tasks: set = set()


class TriggerRequest(BaseModel):
    provider_name: str


@router.get("", response_model=list[ParseRunRead])
async def get_parse_runs(
    provider_id: int | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> list[ParseRunRead]:
    repo = ParseRunRepository(model=ParseRun, session=session)
    if provider_id is not None:
        runs = await repo.get_by_provider(provider_id=provider_id, limit=limit)
    else:
        runs = await repo.get_recent(limit=limit)
    return [ParseRunRead.model_validate(r) for r in runs]


@router.post("/trigger", status_code=202)
async def trigger_parse_run(
    body: TriggerRequest,
    _: User = Depends(get_current_admin),
) -> dict:
    from src.etl.pipeline import run_etl_for_provider

    task = asyncio.create_task(run_etl_for_provider(body.provider_name))
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)

    return {
        "status": "accepted",
        "provider": body.provider_name,
        "message": "ETL pipeline triggered",
    }
