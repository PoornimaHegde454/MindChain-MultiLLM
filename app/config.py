"""
Configuration settings for MultiLLM Router
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "MultiLLM Router"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # API Keys
    GROQ_API_KEY: Optional[str] = None
    GROQ_KEY: Optional[str] = None  # Alternative name for GROQ_API_KEY
    HUGGINGFACE_API_KEY: Optional[str] = None
    GITHUB_MODELS_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "sqlite:///./multillm.db"
    
    # Redis (optional)
    REDIS_URL: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_BURST: int = 200
    
    # Caching
    CACHE_TTL_SECONDS: int = 3600
    CACHE_MAX_SIZE: int = 1000
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
