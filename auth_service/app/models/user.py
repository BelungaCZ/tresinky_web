from sqlalchemy import Boolean, Column, String, DateTime, Integer, JSON
from sqlalchemy.sql import func
from app.db.base_class import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    identita_id = Column(String, unique=True, index=True, nullable=True)
    identita_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # OAuth2 fields
    oauth_providers = Column(JSON, default={})  # Store OAuth provider data
    oauth_id = Column(String, nullable=True)    # ID from OAuth provider
    
    # Notification preferences
    notification_preferences = Column(JSON, default={
        "email": True,
        "sms": False,
        "push": True
    })
    
    # Two-factor authentication
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String, nullable=True) 