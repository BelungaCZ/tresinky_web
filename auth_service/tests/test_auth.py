from typing import Dict, Any
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.user import IdentitaToken

def test_login_email_password(client: TestClient, test_user: User) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

def test_login_email_password_wrong_credentials(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "detail" in response.json()

def test_login_phone_sms(client: TestClient) -> None:
    with patch("app.core.sms.send_verification_code") as mock_send:
        mock_send.return_value = "123456"
        response = client.post(
            "/api/v1/auth/login/phone",
            json={
                "phone": "+420123456789"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "verification_id" in data
        mock_send.assert_called_once_with("+420123456789")

@patch("app.core.identita.identita_client.verify_token")
def test_login_identita_obcana(
    mock_verify: MagicMock,
    client: TestClient
) -> None:
    mock_verify.return_value = {
        "identita_id": "test_id",
        "full_name": "Test User",
        "email": "test@example.com"
    }
    
    response = client.post(
        "/api/v1/auth/login/identita",
        json={
            "token": "test_token"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    mock_verify.assert_called_once_with("test_token")

@patch("app.core.identita.identita_client.verify_token")
def test_login_identita_obcana_invalid_token(
    mock_verify: MagicMock,
    client: TestClient
) -> None:
    mock_verify.return_value = None
    
    response = client.post(
        "/api/v1/auth/login/identita",
        json={
            "token": "invalid_token"
        }
    )
    assert response.status_code == 401
    assert "detail" in response.json()

@patch("app.core.oauth.verify_oauth_token")
def test_oauth_login(
    mock_verify: MagicMock,
    client: TestClient
) -> None:
    mock_verify.return_value = {
        "email": "test@example.com",
        "name": "Test User"
    }
    
    response = client.post(
        "/api/v1/auth/login/oauth",
        json={
            "provider": "google",
            "token": "test_oauth_token"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    mock_verify.assert_called_once_with("google", "test_oauth_token")

def test_register_email(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@example.com",
            "password": "newpassword",
            "full_name": "New User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == "new@example.com"

def test_register_email_duplicate(client: TestClient, test_user: User) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "newpassword",
            "full_name": "New User"
        }
    )
    assert response.status_code == 400
    assert "detail" in response.json()

def test_register_phone(client: TestClient) -> None:
    with patch("app.core.sms.send_verification_code") as mock_send:
        mock_send.return_value = "123456"
        response = client.post(
            "/api/v1/auth/register/phone",
            json={
                "phone": "+420987654321",
                "full_name": "Phone User"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["phone"] == "+420987654321"

@patch("app.core.identita.identita_client.verify_token")
def test_register_identita(
    mock_verify: MagicMock,
    client: TestClient
) -> None:
    mock_verify.return_value = {
        "identita_id": "test_id",
        "full_name": "Test User",
        "email": "test@example.com"
    }
    
    response = client.post(
        "/api/v1/auth/register/identita",
        json={
            "token": "test_token"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    mock_verify.assert_called_once_with("test_token")

def test_refresh_token(client: TestClient, test_user: User) -> None:
    access_token = create_access_token(test_user.id)
    response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_refresh_token_invalid(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()

def test_logout(client: TestClient, test_user: User) -> None:
    access_token = create_access_token(test_user.id)
    response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200

def test_logout_no_token(client: TestClient) -> None:
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 401
    assert "detail" in response.json() 