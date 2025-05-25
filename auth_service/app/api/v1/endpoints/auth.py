from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.identita import identita_client, IdentitaError
from app.core.security import create_access_token, get_password_hash
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, Token, UserInDB, IdentitaToken
from app.core.validators import validate_password, validate_phone

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/login/identita", response_model=Token)
async def login_identita(
    token_data: IdentitaToken,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Login with Identita občana
    
    Args:
        token_data: Identita token data
        db: Database session
        
    Returns:
        Dict containing access token
        
    Raises:
        HTTPException: If token is invalid or user creation fails
    """
    try:
        user_data = await identita_client.verify_token(token_data.token)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Identita token"
            )
        
        user = db.query(User).filter(User.identita_id == user_data["identita_id"]).first()
        if not user:
            # Create new user from Identita data
            user = User(
                identita_id=user_data["identita_id"],
                email=user_data.get("email"),
                phone=user_data.get("phone"),
                full_name=user_data["full_name"],
                identita_data=user_data,
                email_verified=True,  # Email is verified by Identita
                phone_verified=True   # Phone is verified by Identita
            )
            try:
                db.add(user)
                db.commit()
                db.refresh(user)
            except Exception as e:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user"
                )
        
        return {
            "access_token": create_access_token(user.id),
            "token_type": "bearer"
        }
    except IdentitaError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.get("/identita/auth-url", response_model=Dict[str, str])
async def get_identita_auth_url() -> Dict[str, str]:
    """
    Get Identita občana authorization URL
    
    Returns:
        Dict containing the authorization URL
        
    Raises:
        HTTPException: If Identita client is not configured
    """
    try:
        return {"url": await identita_client.get_auth_url()}
    except IdentitaError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/register/identita", response_model=Token)
async def register_identita(
    token_data: IdentitaToken,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Register with Identita občana
    
    Args:
        token_data: Identita token data
        db: Database session
        
    Returns:
        Dict containing access token
        
    Raises:
        HTTPException: If token is invalid or user already exists
    """
    try:
        user_data = await identita_client.verify_token(token_data.token)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Identita token"
            )
        
        # Check if user already exists
        if db.query(User).filter(User.identita_id == user_data["identita_id"]).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already registered"
            )
        
        # Create new user
        user = User(
            identita_id=user_data["identita_id"],
            email=user_data.get("email"),
            phone=user_data.get("phone"),
            full_name=user_data["full_name"],
            identita_data=user_data,
            email_verified=True,
            phone_verified=True
        )
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        return {
            "access_token": create_access_token(user.id),
            "token_type": "bearer"
        }
    except IdentitaError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        ) 