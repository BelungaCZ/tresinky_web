from typing import Optional, Dict, Any
import logging
import httpx
from app.core.test_config import test_settings

logger = logging.getLogger(__name__)

class IdentitaError(Exception):
    """Base exception for Identita client errors"""
    pass

class IdentitaConnectionError(IdentitaError):
    """Raised when there are connection issues with Identita service"""
    pass

class IdentitaTimeoutError(IdentitaError):
    """Raised when request to Identita service times out"""
    pass

class IdentitaValidationError(IdentitaError):
    """Raised when response from Identita service is invalid"""
    pass

class IdentitaClient:
    def __init__(self) -> None:
        # MojeID OIDC endpoints
        self.base_url = "https://mojeid.cz"
        self.authorization_endpoint = f"{self.base_url}/oidc/authorize"
        self.token_endpoint = f"{self.base_url}/oidc/token"
        self.userinfo_endpoint = f"{self.base_url}/oidc/userinfo"
        self.client_id = test_settings.IDENTITA_CLIENT_ID
        self.client_secret = test_settings.IDENTITA_CLIENT_SECRET
        self.timeout = 10.0  # seconds

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify MojeID token and return user data
        
        Args:
            token: The MojeID token to verify
            
        Returns:
            Dict containing user data if token is valid, None otherwise
            
        Raises:
            IdentitaConnectionError: If there are connection issues
            IdentitaTimeoutError: If request times out
            IdentitaValidationError: If response is invalid
            IdentitaError: For other errors
        """
        if not token:
            raise IdentitaValidationError("Token cannot be empty")

        try:
            async with httpx.AsyncClient() as client:
                # Get user info using the token
                response = await client.get(
                    self.userinfo_endpoint,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    },
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
                
                # Validate required fields
                required_fields = ["sub", "name"]
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    raise IdentitaValidationError(f"Missing required fields: {', '.join(missing_fields)}")
                
                return {
                    "identita_id": data["sub"],
                    "full_name": data["name"],
                    "email": data.get("email"),
                    "phone": data.get("phone_number"),
                    "birth_date": data.get("birthdate"),
                    "address": {
                        "street": data.get("street_address"),
                        "city": data.get("locality"),
                        "zip_code": data.get("postal_code")
                    }
                }
        except httpx.TimeoutException:
            logger.error("Timeout while verifying MojeID token")
            raise IdentitaTimeoutError("Request to MojeID service timed out")
        except httpx.ConnectError:
            logger.error("Connection error while verifying MojeID token")
            raise IdentitaConnectionError("Failed to connect to MojeID service")
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while verifying MojeID token: {str(e)}")
            raise IdentitaError(f"Failed to verify token: {str(e)}")
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid response from MojeID service: {str(e)}")
            raise IdentitaValidationError(f"Invalid response from MojeID service: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in MojeID verification: {str(e)}")
            raise IdentitaError(f"Unexpected error: {str(e)}")

    async def get_auth_url(self) -> str:
        """
        Get MojeID authorization URL
        
        Returns:
            The authorization URL
            
        Raises:
            IdentitaError: If client_id is not configured
        """
        if not self.client_id:
            raise IdentitaError("MojeID client_id is not configured")
            
        # OIDC authorization request parameters
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": "openid profile email phone address",
            "redirect_uri": test_settings.IDENTITA_REDIRECT_URI,
            "state": "random_state",  # Should be generated and validated
            "nonce": "random_nonce"   # Should be generated and validated
        }
        
        # Build query string
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.authorization_endpoint}?{query_string}"

identita_client = IdentitaClient() 