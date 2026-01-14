from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- DB ---
    DATABASE_URL: str = "sqlite:///./autogram.db"
    DB_ECHO: bool = False

    # --- Telegram (Telethon) ---
    TG_API_ID: int | None = None
    TG_API_HASH: str | None = None
    TG_SESSION_NAME: str = "autogram"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
