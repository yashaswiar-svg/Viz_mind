import hashlib
import hmac
import os
from typing import Tuple

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    _HAS_PASSLIB = True
except ImportError:
    _HAS_PASSLIB = False


class PasswordHasher:
    """Secure password hashing using Passlib bcrypt or PBKDF2-HMAC-SHA256 fallback."""

    @staticmethod
    def hash_password(password: str) -> str:
        if not password:
            raise ValueError("Password cannot be empty.")
        if _HAS_PASSLIB:
            return pwd_context.hash(password)
        
        # PBKDF2 fallback if passlib is missing
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return f"pbkdf2_sha256${salt.hex()}${key.hex()}"

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        if not plain_password or not hashed_password:
            return False
        if _HAS_PASSLIB and not hashed_password.startswith("pbkdf2_sha256$"):
            try:
                return pwd_context.verify(plain_password, hashed_password)
            except Exception:
                return False

        if hashed_password.startswith("pbkdf2_sha256$"):
            parts = hashed_password.split("$")
            if len(parts) != 3:
                return False
            salt = bytes.fromhex(parts[1])
            expected_key = bytes.fromhex(parts[2])
            computed_key = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, 100_000)
            return hmac.compare_digest(computed_key, expected_key)

        return False
