# 🏢 Job Market Analytics Platform

> Production-style Data Platform для моніторингу ринку вакансій Python розробників в Україні.

[![CI](https://github.com/recombinationBTRDRS/job_market_platform/actions/workflows/ci.yml/badge.svg)](https://github.com/recombinationBTRDRS/job_market_platform/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.139-green)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)](https://www.postgresql.org/)

## 🎯 Що це і навіщо

Система збирає вакансії для Python розробників з популярних українських job платформ (DOU, Work.ua, Robota.ua, Djinni), нормалізує та агрегує їх для аналітики.

**Головна мета** — не скрапінг, а демонстрація production-підходів до побудови Data Platform:

- ✅ ETL Pipeline з Provider Pattern
- ✅ REST API з JWT автентифікацією
- ✅ Операційна + Аналітична схеми БД (OLTP/OLAP)
- ✅ Оркестрація через Apache Airflow
- ✅ Дашборди через Apache Superset
- ✅ CI/CD через GitHub Actions
- ✅ 57 автотестів

## 🖥️ Демо

### API — список вакансій з фільтрацією

GET /api/v1/vacancies?remote_type=remote&salary_min=2000


### Топ скілів на ринку
```json
[
  {"name": "Python", "vacancy_count": 5},
  {"name": "Docker", "vacancy_count": 3},
  {"name": "PostgreSQL", "vacancy_count": 3},
  {"name": "FastAPI", "vacancy_count": 2}
]
```

### Огляд ринку
```json
{
  "total_vacancies": 5,
  "active_vacancies": 5,
  "total_companies": 4,
  "total_skills": 10
}
```

## 🏗️ Архітектура

┌─────────────────────────────────────────────────────┐
│ Data Sources │
│ DOU.ua │ Work.ua │ Robota.ua │ Djinni.co │
└────────────────────┬────────────────────────────────┘
│ RSS Feeds
▼
┌─────────────────────────────────────────────────────┐
│ ETL Pipeline (Airflow) │
│ Extract → Normalize → Deduplicate → Load │
└────────────────────┬────────────────────────────────┘
│
┌──────────┴──────────┐
▼ ▼
┌─────────────────┐ ┌──────────────────┐
│ Operational DB │ │ Analytical DB │
│ (PostgreSQL) │──▶│ (PostgreSQL) │
│ OLTP схема │ │ analytics.* │
└─────────────────┘ └────────┬─────────┘
│ │
▼ ▼
┌─────────────────┐ ┌──────────────────┐
│ FastAPI │ │ Superset │
│ REST API │ │ Дашборди │
└─────────────────┘ └──────────────────┘


## 🛠️ Стек технологій

| Категорія | Технологія |
|-----------|-----------|
| **Backend** | Python 3.11, FastAPI |
| **Database** | PostgreSQL 15, SQLAlchemy 2.0 async |
| **Migrations** | Alembic |
| **Cache** | Redis 7 |
| **ETL** | Apache Airflow 2.9 |
| **Analytics** | Apache Superset 3.1 |
| **Auth** | JWT (access + refresh tokens) |
| **Validation** | Pydantic v2 |
| **Testing** | Pytest, pytest-asyncio, httpx |
| **Code Quality** | Ruff, MyPy, pre-commit |
| **CI/CD** | GitHub Actions |
| **Container** | Docker, Docker Compose |

## 🚀 Швидкий старт

### Вимоги
- Docker та Docker Compose
- Python 3.11+ (для локальної розробки)
- Poetry

### 1. Клонування та налаштування

```bash
git clone https://github.com/recombinationBTRDRS/job_market_platform.git
cd job_market_platform
cp .env.example .env
```

Відредагуй `.env` — змінити секретні ключі:
```bash
SECRET_KEY=your-super-secret-key-min-32-characters
JWT_SECRET_KEY=your-jwt-secret-key-min-32-characters
SUPERSET_SECRET_KEY=your-superset-secret-key
```

### 2. Запуск основних сервісів

```bash
docker compose up postgres redis api -d
docker compose run --rm api alembic upgrade head
```

### 3. Відкрий API документацію

http://localhost:8000/docs


### 4. Реєстрація адміна та запуск ETL

```bash
# Реєстрація через API
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "Admin123456", "full_name": "Admin"}'

# Зробити адміном через БД
docker exec job_market_postgres psql -U job_market_user -d job_market_db \
  -c "UPDATE users SET is_admin = true WHERE email = 'admin@example.com';"

# Логін та отримання токена
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "Admin123456"}'

# Запуск ETL pipeline (MockProvider для демо)
curl -X POST http://localhost:8000/api/v1/parse-runs/trigger \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"provider_name": "mock"}'
```

### 5. Запуск Airflow (опціонально)

```bash
docker compose up airflow-init
docker compose up airflow-webserver airflow-scheduler -d
```

Airflow UI: `http://localhost:8080` (admin/admin)

### 6. Запуск Superset (опціонально)

```bash
docker compose up superset -d
```

Superset UI: `http://localhost:8088` (admin/admin)

## 📡 API Ендпоінти

### Публічні
| Метод | Ендпоінт | Опис |
|-------|----------|------|
| GET | `/health` | Статус сервісів |
| GET | `/api/v1/vacancies` | Список вакансій з фільтрами |
| GET | `/api/v1/vacancies/{id}` | Вакансія по ID |
| GET | `/api/v1/skills` | Всі скіли |
| GET | `/api/v1/companies` | Всі компанії |
| GET | `/api/v1/analytics/skills/top` | Топ скілів |
| GET | `/api/v1/analytics/market-overview` | Огляд ринку |

### Автентифікація
| Метод | Ендпоінт | Опис |
|-------|----------|------|
| POST | `/api/v1/auth/register` | Реєстрація |
| POST | `/api/v1/auth/login` | Логін → токени |
| POST | `/api/v1/auth/refresh` | Оновлення токена |
| GET | `/api/v1/auth/me` | Профіль користувача |

### Адмін (JWT required)
| Метод | Ендпоінт | Опис |
|-------|----------|------|
| GET/POST | `/api/v1/providers` | Управління провайдерами |
| GET | `/api/v1/parse-runs` | Історія ETL запусків |
| POST | `/api/v1/parse-runs/trigger` | Запуск ETL вручну |

### Фільтри для `/api/v1/vacancies`

?remote_type=remote # remote | hybrid | office
&salary_min=2000 # мінімальна зарплата USD
&salary_max=5000 # максимальна зарплата USD
&skill_ids=1&skill_ids=2 # фільтр по скілах
&company_id=1 # фільтр по компанії
&page=1&per_page=20 # пагінація


## 🔄 ETL Pipeline

Provider.fetch()
↓
[NormalizedVacancy список]
↓
Normalizer (скіли, зарплата, remote_type)
↓
Deduplicator (external_id + provider_id)
↓
VacancyLoader (batch insert)
↓
PostgreSQL (operational schema)
↓
Airflow Analytics DAG (щоночі о 2:00)
↓
PostgreSQL (analytics schema)
↓
Superset Дашборди


### Провайдери та rate limits

| Провайдер | Тип | Rate Limit | robots.txt |
|-----------|-----|-----------|------------|
| MockProvider | mock | 0s | — |
| Djinni.co | RSS | 2s | ✅ Дозволено |
| Work.ua | RSS | 3s | ✅ Дозволено |
| Robota.ua | RSS | 3s | ✅ Дозволено |
| DOU.ua | RSS | 5s | ⚠️ RSS дозволено |

## 🧪 Тести

```bash
# Локально (потребує Docker PostgreSQL)
docker compose up postgres -d
docker compose run --rm api pytest tests/ -v

# Результат
# 57 passed in 8.59s
```

| Тип | Файл | Тестів |
|-----|------|--------|
| Unit — ETL | test_etl_transformers.py | 20 |
| Unit — Service | test_services.py | 10 |
| Unit — Repository | test_repositories.py | 7 |
| Integration — API | test_api.py | 16 |
| Integration — ETL | test_etl_pipeline.py | 4 |

## 📁 Структура проєкту

job_market_platform/
├── src/
│ ├── api/v1/routers/ # FastAPI роутери
│ ├── core/ # Config, Security, Logging
│ ├── db/ # SQLAlchemy engine, session
│ ├── models/ # ORM моделі (operational + analytical)
│ ├── repositories/ # Repository Pattern
│ ├── services/ # Business logic
│ ├── etl/ # ETL Pipeline
│ │ ├── providers/ # Provider Pattern (RSS, Mock)
│ │ ├── transformers/ # Normalizer, Deduplicator
│ │ └── loaders/ # VacancyLoader
│ └── dags/ # Airflow DAGs
├── tests/
│ ├── unit/ # Unit тести
│ └── integration/ # Integration тести
├── alembic/ # Міграції БД
├── docker/ # Dockerfile, init.sql
├── .github/workflows/ # CI/CD
└── docker-compose.yml


## 🗺️ Roadmap

### v2 (планується)
- [ ] WebSocket — realtime нотифікації про нові вакансії
- [ ] Prometheus + Grafana — метрики
- [ ] Повнотекстовий пошук через PostgreSQL tsvector
- [ ] Додаткові провайдери — LinkedIn (якщо дозволить TOS)
- [ ] User-агент ротація для production скрапінгу

## 👨‍💻 Автор

**Vitalii** — Junior Data Platform Engineer
[GitHub](https://github.com/recombinationBTRDRS)

---

*Проєкт розроблений як pet project для демонстрації навичок Data Engineering та Python Backend розробки.*
