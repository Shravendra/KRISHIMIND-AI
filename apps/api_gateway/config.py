from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.local", extra="ignore")
    app_name: str = "KrishiMind API Gateway"
    app_env: str = "dev"
    api_prefix: str = ""
    cors_origins: str = "*"
    redis_url: str = "redis://localhost:6379/0"
    request_timeout_s: float = 30.0

settings = Settings()
