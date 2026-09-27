from abc import ABC, abstractmethod
from typing import Any, Dict


class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""
    pass


class LLMTimeoutError(LLMProviderError):
    """Raised when an LLM completion request times out."""
    pass


class LLMResponseFormatError(LLMProviderError):
    """Raised when LLM output fails schema/JSON format requirements."""
    pass


class LLMProvider(ABC):
    """Abstract Base Class for LLM Providers (Mock, Gemini, OpenAI)."""

    @abstractmethod
    async def generate_completion(
        self,
        prompt: str,
        system_instruction: str,
        schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Executes completion request against LLM provider and returns parsed JSON dictionary.
        Must raise LLMProviderError, LLMTimeoutError, or LLMResponseFormatError on failure.
        """
        pass
