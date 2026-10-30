"""App settings loaded from environment variables (or .env file)."""

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Basic app environment: "development" or "production"
    APP_ENV: str = "development"

    # Development-only default. Set a strong secret through the environment in production.
    JWT_SECRET_KEY: str = "dev-only-change-this-secret-key-32"
    JWT_ALGORITHM: str = "HS256"

    # How long an access token stays valid, in minutes
    ACCESS_TOKEN_MINUTES: int = 60

    # Uses libpq password-file/trust configuration unless overridden in .env.
    DATABASE_URL: str = "postgresql+psycopg://postgres@localhost:5432/student_query_manager"

    # Required in development to create seeded faculty accounts; never commit a real value.
    DEV_FACULTY_PASSWORD: str = ""

    # Gemini is configured separately so the backend can run without an API key.
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.8-flash"

    # Chroma uses cosine distance (0 is identical; lower values are more relevant).
    RAG_TOP_K: int = 5
    RAG_MAX_COSINE_DISTANCE: float = 1.0

    @model_validator(mode="after")
    def require_production_jwt_secret(self):
        if self.APP_ENV.strip().casefold() == "production":
            if self.JWT_SECRET_KEY == "dev-only-change-this-secret-key-32" or len(self.JWT_SECRET_KEY) < 32:
                raise ValueError("Set JWT_SECRET_KEY to a unique secret of at least 32 characters in production")
        return self

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Single shared settings instance used across the app
settings = Settings()
