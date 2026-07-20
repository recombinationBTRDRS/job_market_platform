# src/models/operational/skill.py
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.operational.vacancy_skill import VacancySkill


class Skill(Base, TimestampMixin):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    normalized_name: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True
    )

    vacancy_skills: Mapped[list["VacancySkill"]] = relationship(
        back_populates="skill",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Skill id={self.id} name={self.name}>"
