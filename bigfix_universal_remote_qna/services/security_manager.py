import base64
import hashlib
from cryptography.fernet import Fernet

class SecurityManager:
    """Handles password encryption and security operations"""
    
    @staticmethod
    def generate_key(seed: str) -> bytes:
        """Generate encryption key from seed"""
        return base64.urlsafe_b64encode(
            hashlib.pbkdf2_hmac('sha256', seed.encode(), b'salt_', 100000)
        )
    
    @staticmethod
    def encrypt_password(password: str, key: bytes) -> str:
        """Encrypt password using key"""
        if not password:
            return ""
        try:
            fernet = Fernet(key)
            encrypted = fernet.encrypt(password.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception:
            return ""
    
    @staticmethod
    def decrypt_password(encrypted_password: str, key: bytes) -> str:
        """Decrypt password using key"""
        if not encrypted_password:
            return ""
        try:
            fernet = Fernet(key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_password.encode())
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception:
            return ""
