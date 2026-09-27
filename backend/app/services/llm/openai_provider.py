import asyncio
import json
import logging
from typing import Any, Dict, Optional
from app.core.config import settings
from app.services.llm.base_provider import (
    LLMProvider,
    LLMProviderError,
    LLMResponseFormatError,
    LLMTimeoutError,
)

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model_name = model_name or "gpt-4o-mini"

        if not self.api_key:
            logger.warning("OpenAIProvider initialized without API key.")

    async def generate_completion(
        self,
        prompt: str,
        system_instruction: str,
        schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise LLMProviderError("OPENAI_API_KEY is missing or not configured.")

        try:
            import openai

            client = openai.AsyncOpenAI(api_key=self.api_key)

            task = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
            )

            response = await asyncio.wait_for(task, timeout=float(settings.LLM_TIMEOUT_SECONDS))
            text = response.choices[0].message.content.strip()

            parsed = json.loads(text)
            if not isinstance(parsed, dict):
                raise LLMResponseFormatError("OpenAI output is not a JSON object dictionary.")
            return parsed

        except asyncio.TimeoutError:
            logger.error("OpenAI API call timed out.")
            raise LLMTimeoutError(f"OpenAI API timed out after {settings.LLM_TIMEOUT_SECONDS}s.")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI JSON output: {e}")
            raise LLMResponseFormatError(f"Malformed JSON output from OpenAI: {e}")
        except Exception as e:
            logger.error(f"OpenAI provider error: {e}")
            raise LLMProviderError(f"OpenAI completion failed: {e}")
