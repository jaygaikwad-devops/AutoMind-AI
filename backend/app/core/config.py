from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://automind:automind@postgres:5432/automind"
    SYNC_DATABASE_URL: str = "postgresql://automind:automind@postgres:5432/automind"
    REDIS_URL: str = "redis://redis:6379/0"
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173","https://automindai.info"]

    OPENAI_API_KEY: str = ""
    REPLICATE_API_TOKEN: str = ""
    PEXELS_API_KEY: str = ""
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_CONTAINER_NAME: str = "automind-videos"
    JWT_SECRET: str = "your-super-secret-key-change-in-production"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    JWT_ALGORITHM: str = "HS256"

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Razorpay
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""


settings = Settings()
