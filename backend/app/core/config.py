from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class _Settings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    PROJECT_NAME: str = "DocuChat AI"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str
    SECRET_KEY: str
    
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10485760
    
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_data"
    COLLECTION_NAME: str = "documents"
    
    GROQ_API_KEY: str
    MODEL_NAME: str = "llama-3.3-70b-versatile"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 1024


settings = _Settings()
