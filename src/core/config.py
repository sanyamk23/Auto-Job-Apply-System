"""
Database and application configuration using Pydantic settings.
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    # Database type (postgresql or sqlite)
    type: str = Field(default="sqlite", env="DB_TYPE")  # Use sqlite for development/testing

    # PostgreSQL connection settings
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    name: str = Field(default="job_recommendation", env="DB_NAME")
    user: str = Field(default="postgres", env="DB_USER")
    password: str = Field(default="", env="DB_PASSWORD")

    # SQLite settings
    sqlite_path: str = Field(default="data/job_recommendation.db", env="DB_SQLITE_PATH")

    # Connection pool settings
    pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    pool_recycle: int = Field(default=3600, env="DB_POOL_RECYCLE")

    # SQLAlchemy settings
    echo: bool = Field(default=False, env="DB_ECHO")  # Set to True for SQL logging

    @property
    def database_url(self) -> str:
        """Generate database URL from settings."""
        if self.type == "sqlite":
            return f"sqlite:///{self.sqlite_path}"
        else:
            return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class AppSettings(BaseSettings):
    """Application-wide settings."""

    # Application settings
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # API settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")

    # Email settings (for job applications)
    smtp_server: Optional[str] = Field(default=None, env="SMTP_SERVER")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")

    # AI/Model settings
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")

    # LinkedIn API settings
    linkedin_email: Optional[str] = Field(default=None, env="LINKEDIN_EMAIL")
    linkedin_password: Optional[str] = Field(default=None, env="LINKEDIN_PASSWORD")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instances
db_settings = DatabaseSettings()
app_settings = AppSettings()


def get_database_url() -> str:
    """Get the database URL for SQLAlchemy."""
    return db_settings.database_url


def is_production() -> bool:
    """Check if running in production environment."""
    return os.getenv("ENVIRONMENT", "development").lower() == "production"


def is_development() -> bool:
    """Check if running in development environment."""
    return os.getenv("ENVIRONMENT", "development").lower() == "development"
