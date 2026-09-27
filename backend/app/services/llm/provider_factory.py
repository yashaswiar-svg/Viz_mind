import logging
from typing import Optional
from app.core.config import settings
from app.services.llm.base_provider import LLMProvider
from app.services.llm.mock_provider import MockProvider
from app.services.llm.gemini_provider import GeminiProvider
from app.services.llm.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


def get_llm_provider(provider_name: Optional[str] = None) -> LLMProvider:
    """
    Factory function returning active LLMProvider instance.
    Defaults to MockProvider if LLM_ENABLED is False or provider is 'mock'.
    """
    if not settings.LLM_ENABLED:
        logger.info("LLM_ENABLED is False. Instantiating MockProvider.")
        return MockProvider()

    p_name = (provider_name or settings.LLM_PROVIDER or "mock").lower().strip()

    if p_name == "gemini":
        logger.info("Instantiating GeminiProvider.")
        return GeminiProvider()
    elif p_name == "openai":
        logger.info("Instantiating OpenAIProvider.")
        return OpenAIProvider()
    else:
        logger.info(f"Provider '{p_name}' requested. Returning MockProvider.")
        return MockProvider()
