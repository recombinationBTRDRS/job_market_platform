# src/repositories/skill.py
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from src.models.operational.skill import Skill
from src.repositories.base import BaseRepository


class SkillRepository(BaseRepository[Skill]):
    """Repository для роботи зі скілами."""

    async def get_by_normalized_name(self, normalized_name: str) -> Skill | None:
        """Отримати скіл по нормалізованій назві."""
        result = await self.session.execute(
            select(Skill).where(Skill.normalized_name == normalized_name)
        )
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        name: str,
        normalized_name: str,
    ) -> Skill:
        """Отримати або створити скіл. Безпечно при паралельних запитах."""
        stmt = (
            insert(Skill)
            .values(name=name, normalized_name=normalized_name)
            .on_conflict_do_nothing(index_elements=["normalized_name"])
            .returning(Skill)
        )
        result = await self.session.execute(stmt)
        skill = result.scalar_one_or_none()

        if skill is None:
            skill = await self.get_by_normalized_name(normalized_name)

        return skill  # type: ignore[return-value]

    async def get_all_with_vacancy_count(self) -> list[dict]:
        """Отримати всі скіли з кількістю вакансій."""
        from sqlalchemy import func

        from src.models.operational.vacancy_skill import VacancySkill

        result = await self.session.execute(
            select(
                Skill.id,
                Skill.name,
                Skill.normalized_name,
                func.count(VacancySkill.vacancy_id).label("vacancy_count"),
            )
            .outerjoin(VacancySkill, Skill.id == VacancySkill.skill_id)
            .group_by(Skill.id)
            .order_by(func.count(VacancySkill.vacancy_id).desc())
        )
        return [row._asdict() for row in result.all()]
