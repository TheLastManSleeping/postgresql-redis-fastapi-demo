# fastapi_app/app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Указываем pydantic, что переменные нужно брать из окружения
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Переменные, которые мы ожидаем получить.
    # Pydantic автоматически прочитает их из окружения.
    # Можно задать значения по умолчанию.
    DATABASE_URL: str = "postgresql://user:password@postgres_db/mydatabase"
    REDIS_HOST: str = "redis_cache"
    REDIS_PORT: int = 6379

# Создаем единый экземпляр настроек, который будем импортировать
settings = Settings()