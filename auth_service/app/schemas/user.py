from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, constr, Field, validator
from datetime import datetime
import re

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[constr(regex=r'^\+?[1-9]\d{1,14}$')] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            # Remove any non-digit characters except +
            phone = re.sub(r'[^\d+]', '', v)
            if not phone.startswith('+'):
                phone = '+' + phone
            if len(phone) < 10 or len(phone) > 15:
                raise ValueError('Invalid phone number length')
            return phone
        return v

class UserCreate(UserBase):
    email: EmailStr
    password: constr(min_length=8)
    full_name: constr(min_length=2, max_length=100)

    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserUpdate(UserBase):
    password: Optional[constr(min_length=8)] = None
    email_verified: Optional[bool] = None
    phone_verified: Optional[bool] = None

    @validator('password')
    def validate_password(cls, v):
        if v is not None:
            if not re.search(r'[A-Z]', v):
                raise ValueError('Password must contain at least one uppercase letter')
            if not re.search(r'[a-z]', v):
                raise ValueError('Password must contain at least one lowercase letter')
            if not re.search(r'\d', v):
                raise ValueError('Password must contain at least one number')
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
                raise ValueError('Password must contain at least one special character')
        return v

class UserInDBBase(UserBase):
    id: str
    email_verified: bool = False
    phone_verified: bool = False
    identita_id: Optional[str] = None
    identita_data: Optional[Dict[str, Any]] = None
    is_superuser: bool = False
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    account_locked_until: Optional[datetime] = None

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int = Field(default=3600)  # 1 hour in seconds

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None

class IdentitaToken(BaseModel):
    token: constr(min_length=1) 