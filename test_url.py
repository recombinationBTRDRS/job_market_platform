from src.core.config import get_settings

s = get_settings()
print(str(s.database_url))
