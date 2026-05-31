from cryptography.fernet import Fernet
from passlib.context import CryptContext
from typing import Optional, Dict, Any
import hashlib
import hmac
import base64
import secrets
from src.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class DataEncryption:

    def __init__(self):
        raw_key = settings.encryption_key
        if hasattr(raw_key, 'get_secret_value'):
            raw_key = raw_key.get_secret_value()
        key = raw_key.encode()
        if len(key) != 44:
            key = base64.urlsafe_b64encode(
                hashlib.sha256(key).digest()
            )
        self.cipher = Fernet(key)

    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        return self.cipher.decrypt(encrypted_data.encode()).decode()

    def encrypt_dict(self, data: Dict[str, Any]) -> Dict[str, str]:
        return {
            key: self.encrypt(str(value))
            for key, value in data.items()
        }

    def decrypt_dict(self, encrypted_data: Dict[str, str]) -> Dict[str, Any]:
        return {
            key: self.decrypt(value)
            for key, value in encrypted_data.items()
        }


def _resolve_val(val):
    if hasattr(val, 'get_secret_value'):
        return val.get_secret_value()
    return str(val)


class APIKeyManager:

    def __init__(self):
        self._encryption = DataEncryption()

    def get_api_key(self, service: str) -> Optional[str]:
        key_attr = f"{service}_api_key"
        secret_attr = f"{service}_client_secret"

        if hasattr(settings, key_attr):
            val = getattr(settings, key_attr)
            if val:
                return _resolve_val(val)
        elif hasattr(settings, secret_attr):
            val = getattr(settings, secret_attr)
            if val:
                return _resolve_val(val)
        return None

    def verify_api_key(self, service: str, key_hash: str) -> bool:
        actual_key = self.get_api_key(service)
        if not actual_key:
            return False
        return hmac.compare_digest(
            hashlib.sha256(actual_key.encode()).hexdigest(),
            key_hash
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_secure_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)


data_encryption = DataEncryption()
api_key_manager = APIKeyManager()
