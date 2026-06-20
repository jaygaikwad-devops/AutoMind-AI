from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://automind:automind@postgres:5432/automind"
    SYNC_DATABASE_URL: str = "postgresql://automind:automind@postgres:5432/automind"
    REDIS_URL: str = "redis://redis:6379/0"
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://automindai.info",
        "https://www.automindai.info",
    ]

    OPENAI_API_KEY: str = ""
    REPLICATE_API_TOKEN: str = ""
    PEXELS_API_KEY: str = ""
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_CONTAINER_NAME: str = "automind-videos"

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Razorpay
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""

    # AWS S3 / CloudFront
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = "automind-assets-prod"
    AWS_CLOUDFRONT_DOMAIN: str = "cdn.automindai.info"

    # AWS Bedrock — LLM provider
    LLM_PROVIDER: str = "bedrock"               # openai | bedrock
    BEDROCK_REGION: str = "us-east-1"
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    BEDROCK_HAIKU_MODEL_ID: str = "anthropic.claude-3-haiku-20240307-v1:0"

    # Kling AI — Video generation
    KLING_API_KEY: str = ""
    KLING_API_BASE: str = "https://api.klingai.com"

    # AWS SES (future)
    SES_FROM_EMAIL: str = ""
    SES_REGION: str = "us-east-1"

settings = Settings()
