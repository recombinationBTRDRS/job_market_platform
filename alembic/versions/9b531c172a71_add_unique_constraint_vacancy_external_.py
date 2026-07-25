"""add unique constraint vacancy external provider

Revision ID: 9b531c172a71
Revises: d941e392ced0
Create Date: 2026-07-21 21:16:35.822840

"""

from collections.abc import Sequence

from alembic import op

revision: str = "9b531c172a71"
down_revision: str | Sequence[str] | None = "d941e392ced0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_vacancy_external_provider",
        "vacancies",
        ["external_id", "provider_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_vacancy_external_provider",
        "vacancies",
        type_="unique",
    )
