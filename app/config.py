"""Configuration settings for CASM application."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "postgresql://casm_user:casm_password@localhost:5432/casm_db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    api_key: str = "test-api-key-change-in-production"
    
    # Application
    debug: bool = True
    log_level: str = "INFO"
    
    # Embedding Model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # API Settings
    api_v1_prefix: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

