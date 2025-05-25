from typing import Generator, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.main import app
from app.db.base import Base
from app.core.config import settings
from app.db.session import get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db() -> Generator[Session, Any, None]:
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        # Clean up test database file
        import os
        if os.path.exists("./test.db"):
            os.remove("./test.db")

@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, Any, None]:
    def override_get_db() -> Generator[Session, Any, None]:
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db: Session) -> Any:
    from app.models.user import User
    from app.core.security import get_password_hash
    from uuid import uuid4
    
    user = User(
        id=str(uuid4()),
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
        is_active=True,
        email_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user 