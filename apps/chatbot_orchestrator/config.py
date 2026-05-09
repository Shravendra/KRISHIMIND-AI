from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.local", extra="ignore")
    orchestrator_name: str = "KrishiMind Chatbot Orchestrator"
    default_language: str = "en"
    redis_url: str = "redis://localhost:6379/1"

settings = Settings()
