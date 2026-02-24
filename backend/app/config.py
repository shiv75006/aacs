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
    API_TITLE: str = "AACS Backend API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Academic Article Collaboration System REST API"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # CORS Configuration - includes wildcard subdomains for production
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "https://aacsjournals.com",
        "https://www.aacsjournals.com",
        "https://dev.aacsjournals.com",
        "https://aacs-woad.vercel.app",
    ]
    
    # Base domain for subdomain detection
    BASE_DOMAIN: str = "aacsjournals.com"
    
    # Allow all subdomains via regex pattern (handled in middleware)
    CORS_ORIGIN_REGEX: str = r"https?://(.*\.aacsjournals\.com|.*\.up\.railway\.app|.*\.railway\.app|.*\.vercel\.app|localhost:\d+)"
    
    # Crossref DOI Configuration
    CROSSREF_USERNAME: str = ""  # Your Crossref username
    CROSSREF_PASSWORD: str = ""  # Your Crossref password
    CROSSREF_DOI_PREFIX: str = "10.58517"  # AACS DOI prefix
    CROSSREF_DEPOSITOR_NAME: str = "AACS Journals"
    CROSSREF_DEPOSITOR_EMAIL: str = "info@aacsjournals.com"
    CROSSREF_API_URL: str = "https://doi.crossref.org/servlet/deposit"
    CROSSREF_TEST_URL: str = "https://test.crossref.org/servlet/deposit"
    CROSSREF_TEST_MODE: bool = True  # Set to False for production
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def DATABASE_URL(self) -> str:
        """Generate database URL for SQLAlchemy"""
        return f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


# Create settings instance
settings = Settings()
