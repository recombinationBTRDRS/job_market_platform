# src/models/operational/company.py
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.operational.vacancy import Vacancy


class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    vacancies: Mapped[list["Vacancy"]] = relationship(
        back_populates="company",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Company id={self.id} name={self.name}>"
