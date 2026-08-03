from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    app_name: str
    env: str
    debug: bool
    api_key: str
    anthropic_api_key: str
    openai_api_key: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()


