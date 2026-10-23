"""
DataPulse Backend Configuration
Loads settings using Pydantic Settings with support for environment variables.
"""

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "DataPulse — Smart Campus Analytics & Predictive Intelligence"
    VERSION: str = "2.0.0"
    API_PREFIX: str = "/api"
    DEBUG: bool = False
    INSTITUTION: str = "Universiapolis International University of Agadir (UIA)"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'datapulse.db'}")

    # Security & CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:80",
    ]

    JWT_SECRET: str = os.getenv("JWT_SECRET", "datapulse-production-secret-key-uia-agadir-2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
