# src/etl/providers/mock.py
from datetime import UTC, datetime

from src.etl.providers.base import BaseProvider, NormalizedVacancy


class MockProvider(BaseProvider):
    """Mock провайдер для тестів і розробки."""

    name = "mock"
    provider_type = "mock"

    MOCK_VACANCIES = [
        {
            "external_id": "mock-001",
            "title": "Senior Python Developer",
            "url": "https://mock.example.com/jobs/001",
            "company_name": "TechCorp UA",
            "description": "We need a Senior Python Developer with FastAPI experience.",
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "salary_min": 3000,
            "salary_max": 5000,
            "salary_currency": "USD",
            "employment_type": "full-time",
            "remote_type": "remote",
        },
        {
            "external_id": "mock-002",
            "title": "Middle Python Developer",
            "url": "https://mock.example.com/jobs/002",
            "company_name": "DataFlow Inc",
            "description": "Looking for Middle Python Developer for data platform.",
            "skills": ["Python", "SQLAlchemy", "Redis", "Airflow"],
            "salary_min": 2000,
            "salary_max": 3500,
            "salary_currency": "USD",
            "employment_type": "full-time",
            "remote_type": "hybrid",
        },
        {
            "external_id": "mock-003",
            "title": "Junior Python Developer",
            "url": "https://mock.example.com/jobs/003",
            "company_name": "StartupXYZ",
            "description": "Junior Python Developer for web development.",
            "skills": ["Python", "Django", "PostgreSQL"],
            "salary_min": 800,
            "salary_max": 1500,
            "salary_currency": "USD",
            "employment_type": "full-time",
            "remote_type": "office",
        },
        {
            "external_id": "mock-004",
            "title": "Python Data Engineer",
            "url": "https://mock.example.com/jobs/004",
            "company_name": "Analytics Pro",
            "description": "Data Engineer with Python and Spark experience.",
            "skills": ["Python", "Spark", "Airflow", "PostgreSQL", "Docker"],
            "salary_min": 3500,
            "salary_max": 6000,
            "salary_currency": "USD",
            "employment_type": "full-time",
            "remote_type": "remote",
        },
        {
            "external_id": "mock-005",
            "title": "Python Backend Developer",
            "url": "https://mock.example.com/jobs/005",
            "company_name": "TechCorp UA",
            "description": "Backend developer for microservices architecture.",
            "skills": ["Python", "FastAPI", "Redis", "Docker", "Kubernetes"],
            "salary_min": 2500,
            "salary_max": 4000,
            "salary_currency": "USD",
            "employment_type": "contract",
            "remote_type": "remote",
        },
    ]

    async def fetch(self) -> list[NormalizedVacancy]:
        """Повернути детерміновані тестові вакансії."""
        result = []
        for vacancy in self.MOCK_VACANCIES:
            result.append(
                NormalizedVacancy(
                    external_id=str(vacancy["external_id"]),
                    title=str(vacancy["title"]),
                    url=str(vacancy["url"]),
                    company_name=str(vacancy["company_name"])
                    if vacancy.get("company_name")
                    else None,
                    description=str(vacancy["description"])
                    if vacancy.get("description")
                    else None,
                    skills=list(str(s) for s in vacancy.get("skills", [])),  # type: ignore[attr-defined]
                    salary_min=int(vacancy["salary_min"])
                    if vacancy.get("salary_min") is not None
                    else None,  # type: ignore[call-overload]
                    salary_max=int(vacancy["salary_max"])
                    if vacancy.get("salary_max") is not None
                    else None,  # type: ignore[call-overload]
                    salary_currency=str(vacancy["salary_currency"])
                    if vacancy.get("salary_currency")
                    else None,
                    employment_type=str(vacancy["employment_type"])
                    if vacancy.get("employment_type")
                    else None,
                    remote_type=str(vacancy["remote_type"])
                    if vacancy.get("remote_type")
                    else None,
                    published_at=datetime(2024, 1, 15, tzinfo=UTC),
                )
            )
        return result
