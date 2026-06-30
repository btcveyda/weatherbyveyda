from pydantic import BaseSettings


class Settings(BaseSettings):
    OPENWEATHER_API_KEY: str | None = None
    REDIS_URL: str | None = None
    CACHE_TTL: int = 600
    FASTAPI_HOST: str = "127.0.0.1"
    FASTAPI_PORT: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
