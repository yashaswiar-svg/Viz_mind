import pytest
from app.core.config import Settings, settings


def test_default_config_values():
    assert settings.APP_NAME == "VizMind"
    assert settings.APP_VERSION == "0.2.0"
    assert settings.API_PREFIX == "/api"
    assert settings.API_VERSION == "v1"
    assert settings.api_v1_str == "/api/v1"


def test_custom_config_override():
    custom_settings = Settings(APP_NAME="CustomVizMind", DEBUG=False)
    assert custom_settings.APP_NAME == "CustomVizMind"
    assert custom_settings.DEBUG is False
