from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str
    ENV: str

    # LLM
    GROQ_API_KEY: str
    LLM_MODEL: str

    # Gmail
    GOOGLE_CLIENT_SECRET_FILE: str
    GOOGLE_TOKEN_FILE: str
    GMAIL_SCOPES: str

    # Database
    DATABASE_URL: str

    def gmail_scopes_list(self) -> List[str]:
        return [scope.strip() for scope in self.GMAIL_SCOPES.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
