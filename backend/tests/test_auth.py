import pytest
from app.core.security.password import PasswordHasher
from app.core.security.jwt import JWTHandler


def test_password_hashing_and_verification():
    password = "SuperSecretPassword123!"
    hashed = PasswordHasher.hash_password(password)
    assert hashed != password
    assert PasswordHasher.verify_password(password, hashed) is True
    assert PasswordHasher.verify_password("WrongPassword123!", hashed) is False


def test_jwt_token_generation_and_decoding():
    subject = "123e4567-e89b-12d3-a456-426614174000"
    token = JWTHandler.create_access_token(subject=subject)
    decoded = JWTHandler.decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == subject


def test_jwt_token_invalid_decoding():
    invalid_token = "invalid.token.payload"
    assert JWTHandler.decode_token(invalid_token) is None


