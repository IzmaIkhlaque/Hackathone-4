from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str

    # Cloudflare R2
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = "course-companion-bucket"
    R2_PUBLIC_URL: str = ""

    # App Config
    APP_ENV: str = "development"
    APP_VERSION: str = "1.0"
    APP_PHASE: str = "1"

    # Phase 2 keys — optional in Phase 1, NOT used anywhere in Phase 1 code
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # Security
    API_SECRET_KEY: str = "change-me-in-production"


settings = Settings()
