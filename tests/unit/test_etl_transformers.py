# tests/unit/test_etl_transformers.py

from src.etl.providers.base import NormalizedVacancy
from src.etl.transformers.deduplicator import deduplicate_in_memory
from src.etl.transformers.normalizer import (
    normalize_remote_type,
    normalize_salary_to_usd,
    normalize_skill,
    normalize_skills,
    normalize_vacancy,
)


def make_vacancy(**kwargs) -> NormalizedVacancy:
    return NormalizedVacancy(
        external_id=kwargs.get("external_id", "test-001"),
        title=kwargs.get("title", "Python Developer"),
        url=kwargs.get("url", "https://test.com/jobs/001"),
        skills=kwargs.get("skills", []),
        salary_min=kwargs.get("salary_min", None),
        salary_max=kwargs.get("salary_max", None),
        salary_currency=kwargs.get("salary_currency", None),
        remote_type=kwargs.get("remote_type", None),
    )


class TestNormalizer:
    def test_normalize_skill_python3(self):
        assert normalize_skill("python3") == "Python"

    def test_normalize_skill_js(self):
        assert normalize_skill("JS") == "JavaScript"

    def test_normalize_skill_k8s(self):
        assert normalize_skill("k8s") == "Kubernetes"

    def test_normalize_skill_unknown(self):
        assert normalize_skill("SomeNewTech") == "Somenewtech"

    def test_normalize_skills_deduplication(self):
        skills = ["python3", "Python", "JS", "javascript"]
        result = normalize_skills(skills)
        assert result.count("Python") == 1
        assert result.count("JavaScript") == 1

    def test_normalize_skills_empty(self):
        assert normalize_skills([]) == []

    def test_normalize_skills_preserves_order(self):
        skills = ["python3", "JS", "Docker"]
        result = normalize_skills(skills)
        assert result[0] == "Python"
        assert result[1] == "JavaScript"
        assert result[2] == "Docker"

    def test_normalize_salary_usd(self):
        min_s, max_s, currency = normalize_salary_to_usd(2000, 4000, "USD")
        assert min_s == 2000
        assert max_s == 4000
        assert currency == "USD"

    def test_normalize_salary_uah(self):
        min_s, max_s, currency = normalize_salary_to_usd(50000, 80000, "UAH")
        assert currency == "USD"
        assert min_s == 1200
        assert max_s == 1920

    def test_normalize_salary_none(self):
        min_s, max_s, currency = normalize_salary_to_usd(None, None, None)
        assert min_s is None
        assert max_s is None
        assert currency is None

    def test_normalize_salary_unknown_currency(self):
        min_s, max_s, currency = normalize_salary_to_usd(1000, 2000, "JPY")
        assert min_s == 1000
        assert max_s == 2000
        assert currency == "JPY"

    def test_normalize_remote_type_remote(self):
        assert normalize_remote_type("remote") == "remote"

    def test_normalize_remote_type_ukrainian(self):
        assert normalize_remote_type("віддалено") == "remote"

    def test_normalize_remote_type_hybrid(self):
        assert normalize_remote_type("гібрид") == "hybrid"

    def test_normalize_remote_type_none(self):
        assert normalize_remote_type(None) is None

    def test_normalize_vacancy_full(self):
        vacancy = make_vacancy(
            skills=["python3", "JS", "pg"],
            salary_min=50000,
            salary_max=80000,
            salary_currency="UAH",
            remote_type="віддалено",
        )
        result = normalize_vacancy(vacancy)
        assert "Python" in result.skills
        assert "JavaScript" in result.skills
        assert "PostgreSQL" in result.skills
        assert result.salary_currency == "USD"
        assert result.remote_type == "remote"


class TestDeduplicator:
    def test_deduplicate_removes_duplicates(self):
        vacancies = [
            make_vacancy(external_id="001"),
            make_vacancy(external_id="002"),
            make_vacancy(external_id="001"),
            make_vacancy(external_id="003"),
        ]
        result = deduplicate_in_memory(vacancies)
        assert len(result) == 3

    def test_deduplicate_preserves_first(self):
        vacancies = [
            make_vacancy(external_id="001", title="First"),
            make_vacancy(external_id="001", title="Second"),
        ]
        result = deduplicate_in_memory(vacancies)
        assert result[0].title == "First"

    def test_deduplicate_empty_list(self):
        assert deduplicate_in_memory([]) == []

    def test_deduplicate_no_duplicates(self):
        vacancies = [make_vacancy(external_id=str(i)) for i in range(5)]
        result = deduplicate_in_memory(vacancies)
        assert len(result) == 5
