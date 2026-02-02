from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/library"
    SECRET_KEY: str = "change-me-in-production"  # Load from .env in production

    class Config:
        env_file = ".env"


settings = Settings()
