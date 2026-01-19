from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- DB ---
    DATABASE_URL: str = "sqlite:///./data/autogram.db"
    DB_ECHO: bool = False

    # --- Telegram (Telethon) ---
    TG_API_ID: int | None = None
    TG_API_HASH: str | None = None
    TG_SESSION_NAME: str = "data/autogram"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"


settings = Settings()
