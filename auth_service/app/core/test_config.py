from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator

class TestSettings(BaseSettings):
    PROJECT_NAME: str = "Tresinky Auth Service"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Security
    SECRET_KEY: str = "test-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "tresinky_auth"
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./test.db"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # OAuth2
    GOOGLE_CLIENT_ID: str = "test-google-client-id"
    GOOGLE_CLIENT_SECRET: str = "test-google-client-secret"
    FACEBOOK_CLIENT_ID: str = "test-facebook-client-id"
    FACEBOOK_CLIENT_SECRET: str = "test-facebook-client-secret"
    
    # Identita občana
    IDENTITA_CLIENT_ID: str = "test-identita-client-id"
    IDENTITA_CLIENT_SECRET: str = "test-identita-client-secret"
    
    # SMS
    SMS_PROVIDER_API_KEY: str = "test-sms-api-key"
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_USER: str = "test@gmail.com"
    SMTP_PASSWORD: str = "test-smtp-password"
    EMAILS_FROM_EMAIL: str = "test@gmail.com"
    EMAILS_FROM_NAME: str = "Tresinky Auth Service"

test_settings = TestSettings() 