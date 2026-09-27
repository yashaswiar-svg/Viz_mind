import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from app.core.config import settings

try:
    import jwt as pyjwt
    _HAS_PYJWT = True
except ImportError:
    _HAS_PYJWT = False


class JWTHandler:
    """JWT Token creation and verification module."""

    @staticmethod
    def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            "sub": str(subject),
            "exp": int(expire.timestamp()),
            "type": "access",
            "iat": int(datetime.now(timezone.utc).timestamp()),
        }

        if _HAS_PYJWT:
            return pyjwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        # Fallback standard JWT construction
        header = {"alg": "HS256", "typ": "JWT"}
        header_bytes = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b"=")
        payload_bytes = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=")
        to_sign = header_bytes + b"." + payload_bytes
        signature = base64.urlsafe_b64encode(
            hmac.new(settings.JWT_SECRET_KEY.encode(), to_sign, hashlib.sha256).digest()
        ).rstrip(b"=")
        return (to_sign + b"." + signature).decode()

    @staticmethod
    def create_refresh_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=7))
        payload = {
            "sub": str(subject),
            "exp": int(expire.timestamp()),
            "type": "refresh",
            "iat": int(datetime.now(timezone.utc).timestamp()),
        }

        if _HAS_PYJWT:
            return pyjwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        header = {"alg": "HS256", "typ": "JWT"}
        header_bytes = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b"=")
        payload_bytes = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=")
        to_sign = header_bytes + b"." + payload_bytes
        signature = base64.urlsafe_b64encode(
            hmac.new(settings.JWT_SECRET_KEY.encode(), to_sign, hashlib.sha256).digest()
        ).rstrip(b"=")
        return (to_sign + b"." + signature).decode()

    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        if not token:
            return None

        if _HAS_PYJWT:
            try:
                payload = pyjwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
                return payload
            except Exception:
                return None

        # Fallback verification
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None
            to_sign = (parts[0] + "." + parts[1]).encode()
            expected_sig = base64.urlsafe_b64encode(
                hmac.new(settings.JWT_SECRET_KEY.encode(), to_sign, hashlib.sha256).digest()
            ).rstrip(b"=")
            if not hmac.compare_digest(parts[2].encode(), expected_sig):
                return None
            padded_payload = parts[1] + "=" * (-len(parts[1]) % 4)
            payload_data = json.loads(base64.urlsafe_b64decode(padded_payload).decode())
            if payload_data.get("exp", 0) < time.time():
                return None
            return payload_data
        except Exception:
            return None
