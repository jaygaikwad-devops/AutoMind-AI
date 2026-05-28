from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://automind:automind@postgres:5432/automind"
    REDIS_URL: str = "redis://redis:6379/0"
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    OPENAI_API_KEY: str = ""
    REPLICATE_API_TOKEN: str = ""


settings = Settings()
