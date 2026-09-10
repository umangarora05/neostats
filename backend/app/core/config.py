from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Document Intelligence API"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "sqlite:///./documents.db"
    GEMINI_API_KEY: str = ""
    FRONTEND_URL: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
