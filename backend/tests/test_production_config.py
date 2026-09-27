import pytest
from pydantic import ValidationError
from app.core.config import Settings


def test_production_config_validation_pass():
    s = Settings(
        APP_ENV="production",
        DEBUG=False,
        SECRET_KEY="super_secret_production_key_1234567890_strong_and_unique",
        JWT_SECRET_KEY="super_secret_production_key_1234567890_strong_and_unique",
    )
    s.validate_production_config()  # Should not raise


def test_production_config_validation_fail_default_secret():
    s = Settings(
        APP_ENV="production",
        DEBUG=False,
        SECRET_KEY="super_secret_production_key_1234567890_strong_and_unique",
        JWT_SECRET_KEY="dev-jwt-secret-key-change-in-production-987654321",
    )
    with pytest.raises(ValueError, match="JWT_SECRET_KEY must be configured securely"):
        s.validate_production_config()


def test_production_config_validation_fail_debug_true():
    s = Settings(
        APP_ENV="production",
        DEBUG=True,
        SECRET_KEY="super_secret_production_key_1234567890_strong_and_unique",
        JWT_SECRET_KEY="super_secret_production_key_1234567890_strong_and_unique",
    )
    with pytest.raises(ValueError, match="DEBUG must be False in production"):
        s.validate_production_config()
