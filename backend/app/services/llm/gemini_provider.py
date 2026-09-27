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


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider implementation."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or settings.LLM_API_KEY
        self.model_name = model_name or settings.LLM_MODEL or "gemini-1.5-flash"

        if not self.api_key:
            logger.warning("GeminiProvider initialized without API key.")

    async def generate_completion(
        self,
        prompt: str,
        system_instruction: str,
        schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise LLMProviderError("GEMINI_API_KEY is missing or not configured.")

        try:
            # Import google.generativeai if installed
            import google.generativeai as genai

            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction,
                generation_config={
                    "temperature": settings.LLM_TEMPERATURE,
                    "max_output_tokens": settings.LLM_MAX_TOKENS,
                    "response_mime_type": "application/json",
                },
            )

            loop = asyncio.get_running_loop()
            task = loop.run_in_executor(
                None,
                lambda: model.generate_content(prompt),
            )

            response = await asyncio.wait_for(task, timeout=float(settings.LLM_TIMEOUT_SECONDS))
            text = response.text.strip()

            # Clean markdown JSON formatting if present
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            parsed = json.loads(text)
            if not isinstance(parsed, dict):
                raise LLMResponseFormatError("Gemini output is not a JSON object dictionary.")
            return parsed

        except asyncio.TimeoutError:
            logger.error("Gemini API call timed out.")
            raise LLMTimeoutError(f"Gemini API timed out after {settings.LLM_TIMEOUT_SECONDS}s.")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON output: {e}")
            raise LLMResponseFormatError(f"Malformed JSON output from Gemini: {e}")
        except Exception as e:
            logger.error(f"Gemini provider error: {e}")
            raise LLMProviderError(f"Gemini completion failed: {e}")
