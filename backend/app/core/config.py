from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Base
    SECRET_KEY: str = "changeme-secret-key-for-development-only"
    ENCRYPTION_KEY: str = ""  # Fernet key base64
    FRONTEND_URL: str = "http://localhost:5173"
    ENVIRONMENT: str = "development"

    # Base de datos
    DATABASE_URL: str = "postgresql://repubot:repubot@localhost:5432/repubot"

    # Anthropic
    ANTHROPIC_API_KEY: str = ""

    # Meta (Facebook / Instagram)
    META_APP_ID: str = ""
    META_APP_SECRET: str = ""
    META_REDIRECT_URI: str = "http://localhost:8000/api/auth/meta/callback"

    # Google
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"

    # Culqi
    CULQI_PUBLIC_KEY: str = ""
    CULQI_PRIVATE_KEY: str = ""
    CULQI_WEBHOOK_SECRET: str = ""

    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 día
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
