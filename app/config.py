from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_db"
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 30  # Cache TTL in seconds

    class Config:
        env_file = ".env"


settings = Settings()
