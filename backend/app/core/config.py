from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    # Base
    SECRET_KEY: str = Field(...)
    ENCRYPTION_KEY: str = Field(...)  # Fernet key base64
    FRONTEND_URL: str = "http://localhost:5173"
    ENVIRONMENT: str = "development"

    # Base de datos
    DATABASE_URL: str = Field(...)

    # Anthropic
    ANTHROPIC_API_KEY: str = Field(default="")

    # Meta (Facebook / Instagram)
    META_APP_ID: str = Field(default="")
    META_APP_SECRET: str = Field(default="")
    META_REDIRECT_URI: str = "http://localhost:8000/api/auth/meta/callback"
    META_WEBHOOK_VERIFY_TOKEN: str = Field(default="")

    # Google
    GOOGLE_CLIENT_ID: str = Field(default="")
    GOOGLE_CLIENT_SECRET: str = Field(default="")
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"

    # Culqi
    CULQI_PUBLIC_KEY: str = Field(default="")
    CULQI_PRIVATE_KEY: str = Field(default="")
    CULQI_WEBHOOK_SECRET: str = Field(default="")

    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 día
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
