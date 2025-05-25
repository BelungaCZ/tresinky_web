import re
import phonenumbers
from typing import Optional

def validate_password(password: str) -> bool:
    """
    Validate password strength
    
    Args:
        password: Password to validate
        
    Returns:
        bool: True if password is valid
    """
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

def validate_phone(phone: Optional[str]) -> Optional[str]:
    """
    Validate and format phone number
    
    Args:
        phone: Phone number to validate
        
    Returns:
        str: Formatted phone number or None if invalid
    """
    if not phone:
        return None
        
    try:
        # Parse phone number
        parsed = phonenumbers.parse(phone)
        # Check if valid
        if not phonenumbers.is_valid_number(parsed):
            return None
        # Format to E.164 format
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        return None 