# src/api/v1/routers/skills.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.dependencies import get_db
from src.models.operational.skill import Skill
from src.repositories.skill import SkillRepository
from src.schemas.skill import SkillRead

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[SkillRead])
async def get_skills(
    session: AsyncSession = Depends(get_db),
) -> list[SkillRead]:
    """Отримати всі скіли з кількістю вакансій."""
    repo = SkillRepository(model=Skill, session=session)
    skills_data = await repo.get_all_with_vacancy_count()
    return [
        SkillRead(
            id=row["id"],
            name=row["name"],
            normalized_name=row["normalized_name"],
        )
        for row in skills_data
    ]
