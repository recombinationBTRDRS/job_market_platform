-- Створення аналітичної схеми
CREATE SCHEMA IF NOT EXISTS analytics;

-- Права для користувача
GRANT ALL PRIVILEGES ON SCHEMA analytics TO job_market_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO job_market_user;
