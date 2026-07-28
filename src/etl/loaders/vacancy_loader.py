# src/etl/loaders/vacancy_loader.py
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.etl.providers.base import NormalizedVacancy
from src.models.operational.company import Company
from src.models.operational.skill import Skill
from src.models.operational.vacancy import Vacancy
from src.models.operational.vacancy_skill import VacancySkill
from src.repositories.company import CompanyRepository
from src.repositories.skill import SkillRepository
from src.repositories.vacancy import VacancyRepository

logger = logging.getLogger(__name__)


class VacancyLoader:
    """Завантаження нормалізованих вакансій в операційну БД."""

    def __init__(self, session: AsyncSession, provider_id: int) -> None:
        self.session = session
        self.provider_id = provider_id
        self.vacancy_repo = VacancyRepository(model=Vacancy, session=session)
        self.company_repo = CompanyRepository(model=Company, session=session)
        self.skill_repo = SkillRepository(model=Skill, session=session)

    async def _get_or_create_company(self, company_name: str | None) -> int | None:
        """Отримати або створити компанію. Повертає company_id."""
        if not company_name:
            return None
        company = await self.company_repo.get_or_create(name=company_name)
        return company.id

    async def _get_or_create_skills(self, skill_names: list[str]) -> list[int]:
        """Отримати або створити скіли. Повертає список skill_id."""
        skill_ids = []
        for name in skill_names:
            normalized_name = name.lower().strip()
            skill = await self.skill_repo.get_or_create(
                name=name,
                normalized_name=normalized_name,
            )
            skill_ids.append(skill.id)
        return skill_ids

    async def _load_single_vacancy(
        self, normalized: NormalizedVacancy
    ) -> Vacancy | None:
        """Завантажити одну вакансію з компанією і скілами."""
        try:
            company_id = await self._get_or_create_company(normalized.company_name)
            skill_ids = await self._get_or_create_skills(normalized.skills)

            vacancy = await self.vacancy_repo.create(
                external_id=normalized.external_id,
                provider_id=self.provider_id,
                company_id=company_id,
                url=normalized.url,
                title=normalized.title,
                description=normalized.description,
                salary_min=normalized.salary_min,
                salary_max=normalized.salary_max,
                salary_currency=normalized.salary_currency,
                employment_type=normalized.employment_type,
                remote_type=normalized.remote_type,
                published_at=normalized.published_at,
                is_active=True,
            )

            for skill_id in skill_ids:
                vacancy_skill = VacancySkill(
                    vacancy_id=vacancy.id,
                    skill_id=skill_id,
                )
                self.session.add(vacancy_skill)

            await self.session.flush()
            return vacancy

        except Exception as e:
            logger.error(
                "Failed to load vacancy %s: %s",
                normalized.external_id,
                e,
            )
            return None

    async def load(
        self,
        vacancies: list[NormalizedVacancy],
        batch_size: int = 50,
    ) -> tuple[int, int]:
        """
        Завантажити список вакансій батчами.
        Повертає (успішно завантажено, помилок).
        """
        success_count = 0
        error_count = 0

        for i in range(0, len(vacancies), batch_size):
            batch = vacancies[i : i + batch_size]
            logger.info(
                "Loading batch %d-%d of %d vacancies",
                i + 1,
                min(i + batch_size, len(vacancies)),
                len(vacancies),
            )

            for normalized in batch:
                result = await self._load_single_vacancy(normalized)
                if result is not None:
                    success_count += 1
                else:
                    error_count += 1

        logger.info(
            "Load complete: %d success, %d errors (provider_id=%d)",
            success_count,
            error_count,
            self.provider_id,
        )
        return success_count, error_count
