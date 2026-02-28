"""Application Configuration"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application Settings"""
    
    # Database Configuration
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "aacsjour_aacs"
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    REFRESH_TOKEN_EXPIRATION_DAYS: int = 7
    
    # API Configuration
    API_TITLE: str = "Breakthrough Publishers India Backend API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Breakthrough Publishers India Academic Publishing System REST API"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # CORS Configuration - includes allowed domains for production
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "https://aacsjournals.com",
        "https://www.aacsjournals.com",
        "https://dev.aacsjournals.com",
        "https://aacs-woad.vercel.app",
    ]
    
    # Base domain for the application
    BASE_DOMAIN: str = "aacsjournals.com"
    
    # Allow domains via regex pattern for CORS
    CORS_ORIGIN_REGEX: str = r"https?://(.*\.aacsjournals\.com|.*\.up\.railway\.app|.*\.railway\.app|.*\.vercel\.app|localhost:\d+)"
    
    # Crossref DOI Configuration
    CROSSREF_USERNAME: str = ""  # Your Crossref username
    CROSSREF_PASSWORD: str = ""  # Your Crossref password
    CROSSREF_DOI_PREFIX: str = "10.58517"  # Breakthrough Publishers India DOI prefix
    CROSSREF_DEPOSITOR_NAME: str = "Breakthrough Publishers India"
    CROSSREF_DEPOSITOR_EMAIL: str = "info@breakthroughpublishers.com"
    CROSSREF_API_URL: str = "https://doi.crossref.org/servlet/deposit"
    CROSSREF_TEST_URL: str = "https://test.crossref.org/servlet/deposit"
    CROSSREF_TEST_MODE: bool = True  # Set to False for production
    
    # SMTP Email Configuration
    SMTP_SERVER: str = "mail.breakthroughpublishers.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "info@breakthroughpublishers.com"
    SMTP_PASSWORD: str = "Aacs@2020"
    EMAIL_FROM: str = "info@breakthroughpublishers.com"
    EMAIL_FROM_NAME: str = "Breakthrough Publishers India Journal Management System"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def DATABASE_URL(self) -> str:
        """Generate database URL for SQLAlchemy"""
        return f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


# Create settings instance
settings = Settings()
