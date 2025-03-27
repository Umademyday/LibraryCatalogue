from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/library"
    UPLOAD_DIR: str = "app/static/uploads"

    class Config:
        env_file = ".env"

settings = Settings()
