"""
Security utilities for password hashing and validation.
Centralizes bcrypt operations and password strength rules.
"""
import re
import bcrypt
import logging

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with generated salt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password as a string (UTF-8 decoded)
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def check_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against a bcrypt hash.
    
    Args:
        password: Plain text password to check
        password_hash: Previously hashed password
        
    Returns:
        True if password matches hash, False otherwise
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except (ValueError, AttributeError) as e:
        logger.error(f"Password check failed: {e}")
        return False


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password meets minimum strength requirements.
    
    Requirements:
    - At least 8 characters long
    - Contains at least one letter (a-z, A-Z)
    - Contains at least one number (0-9)
    
    Args:
        password: Plain text password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        If password is valid, error_message is empty string.
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[a-zA-Z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, ""