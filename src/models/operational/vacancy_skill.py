# src/models/operational/vacancy_skill.py
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.models.operational.skill import Skill
    from src.models.operational.vacancy import Vacancy


class VacancySkill(Base):
    __tablename__ = "vacancy_skills"
    __table_args__ = (
        UniqueConstraint("vacancy_id", "skill_id", name="uq_vacancy_skill"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    vacancy_id: Mapped[int] = mapped_column(
        ForeignKey("vacancies.id", ondelete="CASCADE"), nullable=False
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), nullable=False
    )

    vacancy: Mapped["Vacancy"] = relationship(back_populates="vacancy_skills")
    skill: Mapped["Skill"] = relationship(back_populates="vacancy_skills")

    def __repr__(self) -> str:
        return f"<VacancySkill vacancy_id={self.vacancy_id} skill_id={self.skill_id}>"
