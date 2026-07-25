# src/etl/transformers/normalizer.py
import logging

from src.etl.providers.base import NormalizedVacancy

logger = logging.getLogger(__name__)

SKILL_SYNONYMS: dict[str, str] = {
    "python3": "Python",
    "python 3": "Python",
    "py": "Python",
    "python": "Python",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "java script": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "pg": "PostgreSQL",
    "mysql": "MySQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "fastapi": "FastAPI",
    "fast api": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "sqlalchemy": "SQLAlchemy",
    "celery": "Celery",
    "airflow": "Airflow",
    "apache airflow": "Airflow",
    "kafka": "Kafka",
    "apache kafka": "Kafka",
    "spark": "Spark",
    "apache spark": "Spark",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "linux": "Linux",
    "ubuntu": "Linux",
    "react": "React",
    "reactjs": "React",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "node": "Node.js",
    "graphql": "GraphQL",
    "rest api": "REST API",
    "rest": "REST API",
    "pytest": "Pytest",
    "nginx": "Nginx",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "elasticsearch": "Elasticsearch",
    "elk": "Elasticsearch",
}

CURRENCY_TO_USD: dict[str, float] = {
    "USD": 1.0,
    "EUR": 1.08,
    "UAH": 0.024,
    "PLN": 0.25,
    "GBP": 1.27,
}

REMOTE_TYPE_MAP: dict[str, str] = {
    "remote": "remote",
    "remotely": "remote",
    "віддалено": "remote",
    "дистанційно": "remote",
    "hybrid": "hybrid",
    "гібрид": "hybrid",
    "гібридний": "hybrid",
    "office": "office",
    "офіс": "office",
    "офісний": "office",
    "onsite": "office",
    "on-site": "office",
}


def normalize_skill(skill: str) -> str:
    """Нормалізувати назву скілу через словник синонімів."""
    normalized = SKILL_SYNONYMS.get(skill.lower().strip())
    if normalized:
        return normalized
    return skill.strip().capitalize()


def normalize_skills(skills: list[str]) -> list[str]:
    """Нормалізувати список скілів і прибрати дублікати."""
    normalized = [normalize_skill(s) for s in skills if s.strip()]
    return list(dict.fromkeys(normalized))


def normalize_salary_to_usd(
    salary_min: int | None,
    salary_max: int | None,
    currency: str | None,
) -> tuple[int | None, int | None, str | None]:
    """Конвертувати зарплату до USD якщо можливо."""
    if salary_min is None and salary_max is None:
        return None, None, None

    if currency is None or currency not in CURRENCY_TO_USD:
        return salary_min, salary_max, currency

    rate = CURRENCY_TO_USD[currency]
    new_min = int(salary_min * rate) if salary_min is not None else None
    new_max = int(salary_max * rate) if salary_max is not None else None
    return new_min, new_max, "USD"


def normalize_remote_type(remote_type: str | None) -> str | None:
    """Нормалізувати тип зайнятості."""
    if remote_type is None:
        return None
    return REMOTE_TYPE_MAP.get(remote_type.lower().strip(), remote_type)


def normalize_vacancy(vacancy: NormalizedVacancy) -> NormalizedVacancy:
    """Нормалізувати одну вакансію."""
    salary_min, salary_max, currency = normalize_salary_to_usd(
        vacancy.salary_min,
        vacancy.salary_max,
        vacancy.salary_currency,
    )
    return vacancy.model_copy(
        update={
            "skills": normalize_skills(vacancy.skills),
            "salary_min": salary_min,
            "salary_max": salary_max,
            "salary_currency": currency,
            "remote_type": normalize_remote_type(vacancy.remote_type),
            "title": vacancy.title.strip(),
            "company_name": (
                vacancy.company_name.strip() if vacancy.company_name else None
            ),
        }
    )


def normalize_vacancies(vacancies: list[NormalizedVacancy]) -> list[NormalizedVacancy]:
    """Нормалізувати список вакансій."""
    result = []
    for vacancy in vacancies:
        try:
            result.append(normalize_vacancy(vacancy))
        except Exception as e:
            logger.warning("Failed to normalize vacancy %s: %s", vacancy.external_id, e)
    logger.info("Normalized %d/%d vacancies", len(result), len(vacancies))
    return result
