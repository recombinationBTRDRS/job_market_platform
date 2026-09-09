# tests/integration/test_api.py
import pytest
from httpx import AsyncClient

from src.core.security import create_access_token
from src.models.operational import User, Vacancy


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    """Тест health check ендпоінту."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_login_success(
    client: AsyncClient,
    test_user: User,
) -> None:
    """Тест успішного логіну."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(
    client: AsyncClient,
    test_user: User,
) -> None:
    """Тест помилки при неправильному паролі."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_wrong_email(client: AsyncClient) -> None:
    """Тест помилки при неіснуючому email."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "password123"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_vacancies_empty(client: AsyncClient) -> None:
    """Тест GET /vacancies повертає порожній список."""
    response = await client.get("/api/v1/vacancies")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_get_vacancies_with_data(
    client: AsyncClient,
    test_vacancy: Vacancy,
) -> None:
    """Тест GET /vacancies повертає вакансії."""
    response = await client.get("/api/v1/vacancies")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_vacancies_filter_remote(
    client: AsyncClient,
    test_vacancy: Vacancy,
) -> None:
    """Тест фільтрації по remote_type."""
    response = await client.get("/api/v1/vacancies?remote_type=remote")
    assert response.status_code == 200
    data = response.json()
    assert all(v["remote_type"] == "remote" for v in data["items"])


@pytest.mark.asyncio
async def test_get_vacancy_by_id(
    client: AsyncClient,
    test_vacancy: Vacancy,
) -> None:
    """Тест GET /vacancies/{id} — існуюча вакансія."""
    response = await client.get(f"/api/v1/vacancies/{test_vacancy.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_vacancy.id
    assert data["title"] == test_vacancy.title


@pytest.mark.asyncio
async def test_get_vacancy_not_found(client: AsyncClient) -> None:
    """Тест GET /vacancies/{id} — 404 для неіснуючої."""
    response = await client.get("/api/v1/vacancies/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_admin_endpoint_without_token(client: AsyncClient) -> None:
    """Тест admin ендпоінту без токена — 401."""
    response = await client.get("/api/v1/providers")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_endpoint_with_user_token(
    client: AsyncClient,
    test_user: User,
) -> None:
    """Тест admin ендпоінту з user токеном — 403."""
    token = create_access_token(
        subject=test_user.id,
        extra_data={"is_admin": False},
    )
    response = await client.get(
        "/api/v1/providers",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_endpoint_with_admin_token(
    client: AsyncClient,
    admin_user: User,
) -> None:
    """Тест admin ендпоінту з admin токеном — 200."""
    token = create_access_token(
        subject=admin_user.id,
        extra_data={"is_admin": True},
    )
    response = await client.get(
        "/api/v1/providers",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_analytics_top_skills(client: AsyncClient) -> None:
    """Тест GET /analytics/skills/top."""
    response = await client.get("/api/v1/analytics/skills/top")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_analytics_market_overview(client: AsyncClient) -> None:
    """Тест GET /analytics/market-overview."""
    response = await client.get("/api/v1/analytics/market-overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_vacancies" in data
    assert "active_vacancies" in data
    assert "total_companies" in data
    assert "total_skills" in data


@pytest.mark.asyncio
async def test_get_me_with_token(
    client: AsyncClient,
    test_user: User,
) -> None:
    """Тест GET /auth/me з валідним токеном."""
    token = create_access_token(subject=test_user.id)
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_me_without_token(client: AsyncClient) -> None:
    """Тест GET /auth/me без токена — 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
