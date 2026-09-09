# tests/unit/test_services.py
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core.exceptions import AuthenticationError, DuplicateError, NotFoundError
from src.models.operational.user import User
from src.models.operational.vacancy import Vacancy
from src.repositories.vacancy import VacancyFilter
from src.services.auth import AuthService
from src.services.vacancy import VacancyService


def make_vacancy(**kwargs) -> Vacancy:
    """Фабрика тестових вакансій."""
    v = MagicMock(spec=Vacancy)
    v.id = kwargs.get("id", 1)
    v.title = kwargs.get("title", "Python Developer")
    v.is_active = kwargs.get("is_active", True)
    v.remote_type = kwargs.get("remote_type", "remote")
    v.salary_min = kwargs.get("salary_min", 3000)
    v.salary_max = kwargs.get("salary_max", 5000)
    return v


def make_user(**kwargs) -> User:
    """Фабрика тестових користувачів."""
    u = MagicMock(spec=User)
    u.id = kwargs.get("id", 1)
    u.email = kwargs.get("email", "test@example.com")
    u.is_active = kwargs.get("is_active", True)
    u.is_admin = kwargs.get("is_admin", False)
    u.hashed_password = kwargs.get("hashed_password", "hashed")
    return u


class TestVacancyService:
    def setup_method(self):
        self.repo = AsyncMock()
        self.service = VacancyService(repository=self.repo)

    async def test_get_vacancy_found(self):
        """Тест отримання вакансії що існує."""
        vacancy = make_vacancy(id=1)
        self.repo.get_by_id.return_value = vacancy

        result = await self.service.get_vacancy(1)

        assert result == vacancy
        self.repo.get_by_id.assert_called_once_with(1)

    async def test_get_vacancy_not_found(self):
        """Тест NotFoundError якщо вакансія не існує."""
        self.repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError):
            await self.service.get_vacancy(999)

    async def test_get_vacancies_with_limit(self):
        """Тест що limit не перевищує 100."""
        vacancies = [make_vacancy(id=i) for i in range(5)]
        self.repo.get_with_filters.return_value = (vacancies, 5)

        results, total = await self.service.get_vacancies(
            filters=VacancyFilter(),
            skip=0,
            limit=200,
        )

        call_args = self.repo.get_with_filters.call_args
        assert call_args.kwargs["limit"] == 100

    async def test_get_vacancies_returns_correct_total(self):
        """Тест що повертається правильна загальна кількість."""
        vacancies = [make_vacancy(id=i) for i in range(3)]
        self.repo.get_with_filters.return_value = (vacancies, 42)

        results, total = await self.service.get_vacancies(
            filters=VacancyFilter(),
            skip=0,
            limit=20,
        )

        assert total == 42
        assert len(results) == 3

    async def test_deactivate_vacancy(self):
        """Тест деактивації вакансії."""
        vacancy = make_vacancy(id=1, is_active=True)
        deactivated = make_vacancy(id=1, is_active=False)
        self.repo.get_by_id.return_value = vacancy
        self.repo.update.return_value = deactivated

        result = await self.service.deactivate_vacancy(1)

        assert result.is_active is False
        self.repo.update.assert_called_once_with(1, is_active=False)


class TestAuthService:
    def setup_method(self):
        self.repo = AsyncMock()
        self.service = AuthService(repository=self.repo)

    async def test_register_success(self):
        """Тест успішної реєстрації."""
        self.repo.get_by_email.return_value = None
        new_user = make_user(email="new@example.com")
        self.repo.create.return_value = new_user

        result = await self.service.register(
            email="new@example.com",
            password="password123",
            full_name="New User",
        )

        assert result.email == "new@example.com"
        self.repo.create.assert_called_once()

    async def test_register_duplicate_email(self):
        """Тест DuplicateError якщо email вже існує."""
        existing_user = make_user(email="existing@example.com")
        self.repo.get_by_email.return_value = existing_user

        with pytest.raises(DuplicateError):
            await self.service.register(
                email="existing@example.com",
                password="password123",
                full_name="User",
            )

    async def test_login_invalid_email(self):
        """Тест AuthenticationError якщо email не знайдено."""
        self.repo.get_by_email.return_value = None

        with pytest.raises(AuthenticationError):
            await self.service.login(
                email="wrong@example.com",
                password="password123",
            )

    async def test_login_invalid_password(self):
        """Тест AuthenticationError якщо пароль невірний."""
        from src.core.security import hash_password

        user = make_user()
        user.hashed_password = hash_password("correct_password")
        user.is_active = True
        self.repo.get_by_email.return_value = user

        with pytest.raises(AuthenticationError):
            await self.service.login(
                email="test@example.com",
                password="wrong_password",
            )

    async def test_login_success(self):
        """Тест успішного логіну повертає токени."""
        from src.core.security import hash_password

        user = make_user()
        user.hashed_password = hash_password("correct_password")
        user.is_active = True
        self.repo.get_by_email.return_value = user

        result = await self.service.login(
            email="test@example.com",
            password="correct_password",
        )

        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
