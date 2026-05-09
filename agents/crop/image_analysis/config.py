from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.local", extra="ignore")
    service_name: str = "image_analysis"
    min_confidence: float = 0.65

settings = Settings()
