"""add analytics schema tables

Revision ID: 353ff6fa33cf
Revises: d820bb53fde1
Create Date: 2026-08-03 22:06:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "353ff6fa33cf"
down_revision: str | Sequence[str] | None = "d820bb53fde1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS analytics")

    op.create_table(
        "fact_vacancies",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("vacancy_id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=True),
        sa.Column("provider_name", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("salary_min", sa.Integer(), nullable=True),
        sa.Column("salary_max", sa.Integer(), nullable=True),
        sa.Column("salary_currency", sa.String(10), nullable=True),
        sa.Column("remote_type", sa.String(50), nullable=True),
        sa.Column("employment_type", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("collected_date", sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="analytics",
    )
    op.create_index(
        "ix_fact_vacancies_vacancy_id",
        "fact_vacancies",
        ["vacancy_id"],
        schema="analytics",
    )
    op.create_index(
        "ix_fact_vacancies_collected_date",
        "fact_vacancies",
        ["collected_date"],
        schema="analytics",
    )

    op.create_table(
        "agg_skills_daily",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("skill_name", sa.String(100), nullable=False),
        sa.Column("aggregation_date", sa.Date(), nullable=False),
        sa.Column("vacancy_count", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        schema="analytics",
    )
    op.create_index(
        "ix_agg_skills_daily_skill_id",
        "agg_skills_daily",
        ["skill_id"],
        schema="analytics",
    )
    op.create_index(
        "ix_agg_skills_daily_date",
        "agg_skills_daily",
        ["aggregation_date"],
        schema="analytics",
    )

    op.create_table(
        "agg_salary_by_skill",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("skill_name", sa.String(100), nullable=False),
        sa.Column("avg_salary_min", sa.Float(), nullable=True),
        sa.Column("avg_salary_max", sa.Float(), nullable=True),
        sa.Column("sample_count", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        schema="analytics",
    )
    op.create_index(
        "ix_agg_salary_skill_id",
        "agg_salary_by_skill",
        ["skill_id"],
        schema="analytics",
    )


def downgrade() -> None:
    op.drop_table("agg_salary_by_skill", schema="analytics")
    op.drop_table("agg_skills_daily", schema="analytics")
    op.drop_table("fact_vacancies", schema="analytics")
    op.execute("DROP SCHEMA IF EXISTS analytics CASCADE")
