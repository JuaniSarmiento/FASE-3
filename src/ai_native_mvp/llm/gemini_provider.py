"""
Google Gemini LLM provider implementation

Provides integration with Google's Gemini API (Gemini 1.5 Pro/Flash, etc.)

Note: Requires 'google-generativeai' package to be installed:
    pip install google-generativeai
"""
from typing import Optional, Dict, Any, List
import logging

from .base import LLMProvider, LLMMessage, LLMResponse, LLMRole

# Prometheus metrics instrumentation (HIGH-01)
# Lazy import to avoid circular dependency with api.monitoring
_metrics_module = None

def _get_metrics():
    """Lazy load metrics module to avoid circular imports."""
    global _metrics_module
    if _metrics_module is None:
        try:
            from ..api.monitoring import metrics as m
            _metrics_module = m
        except ImportError:
            _metrics_module = False  # Mark as unavailable
    return _metrics_module if _metrics_module else None

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """
    Google Gemini LLM provider

    Supports:
    - Gemini 1.5 Pro (gemini-1.5-pro)
    - Gemini 1.5 Flash (gemini-1.5-flash)
    - Gemini Pro (gemini-pro)

    Configuration:
        api_key: Google API key (required) - Get from https://makersuite.google.com/app/apikey
        model: Model name (default: gemini-1.5-flash)

    Features:
    - Large context window (2M tokens for Gemini 1.5 Pro)
    - Multimodal capabilities (text, images, video)
    - Free tier available with generous limits
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

        self.api_key = self.config.get("api_key")
        if not self.api_key:
            raise ValueError("Google API key is required. Set 'api_key' in config.")

        self.model_name = self.config.get("model", "gemini-1.5-flash")

        # Initialize Gemini client (lazy import to avoid dependency issues)
        self._genai = None
        self._model = None

    def _get_genai(self):
        """Lazy initialization of Google Generative AI"""
        if self._genai is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._genai = genai
            except ImportError:
                raise ImportError(
                    "google-generativeai package not installed. "
                    "Install with: pip install google-generativeai"
                )
        return self._genai

    def _get_model(self):
        """Lazy initialization of Gemini model"""
        if self._model is None:
            genai = self._get_genai()
            self._model = genai.GenerativeModel(self.model_name)
        return self._model

    def _convert_messages_to_gemini_format(self, messages: List[LLMMessage]) -> tuple:
        """
        Convert LLMMessage list to Gemini format

        Returns:
            (system_instruction, conversation_history)
        """
        system_instruction = None
        history = []

        for msg in messages:
            if msg.role == LLMRole.SYSTEM:
                # Gemini uses system_instruction separately
                system_instruction = msg.content
            elif msg.role == LLMRole.USER:
                history.append({
                    "role": "user",
                    "parts": [msg.content]
                })
            elif msg.role == LLMRole.ASSISTANT:
                history.append({
                    "role": "model",  # Gemini uses "model" instead of "assistant"
                    "parts": [msg.content]
                })

        return system_instruction, history

    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion using Google Gemini API"""
        # ✅ HIGH-01: Use context manager to track LLM call duration
        metrics = _get_metrics()
        if metrics:
            with metrics.record_llm_call("gemini", self.model_name):
                return self._execute_gemini_call(messages, temperature, max_tokens, **kwargs)
        else:
            return self._execute_gemini_call(messages, temperature, max_tokens, **kwargs)

    def _execute_gemini_call(
        self,
        messages: List[LLMMessage],
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    ) -> LLMResponse:
        """Execute the actual Gemini API call (extracted for metrics instrumentation)"""
        model = self._get_model()
        genai = self._get_genai()

        # Convert messages
        system_instruction, history = self._convert_messages_to_gemini_format(messages)

        # Configure generation
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            **kwargs
        )

        # If we have system instruction, recreate model with it
        if system_instruction:
            model = genai.GenerativeModel(
                self.model_name,
                system_instruction=system_instruction
            )

        # Generate response
        if len(history) > 1:
            # Multi-turn conversation
            chat = model.start_chat(history=history[:-1])
            response = chat.send_message(
                history[-1]["parts"][0],
                generation_config=generation_config
            )
        else:
            # Single prompt
            prompt = history[0]["parts"][0] if history else ""
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )

        # Extract token usage (if available)
        usage = {
            "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
            "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
            "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0
        }

        return LLMResponse(
            content=response.text,
            model=self.model_name,
            usage=usage,
            metadata={
                "temperature": temperature,
                "max_tokens": max_tokens,
                "finish_reason": response.candidates[0].finish_reason.name if response.candidates else "UNKNOWN"
            }
        )

    def generate_stream(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Generate streaming completion using Google Gemini API"""
        model = self._get_model()
        genai = self._get_genai()

        # Convert messages
        system_instruction, history = self._convert_messages_to_gemini_format(messages)

        # Configure generation
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            **kwargs
        )

        # If we have system instruction, recreate model with it
        if system_instruction:
            model = genai.GenerativeModel(
                self.model_name,
                system_instruction=system_instruction
            )

        # Generate streaming response
        if len(history) > 1:
            # Multi-turn conversation
            chat = model.start_chat(history=history[:-1])
            response_stream = chat.send_message(
                history[-1]["parts"][0],
                generation_config=generation_config,
                stream=True
            )
        else:
            # Single prompt
            prompt = history[0]["parts"][0] if history else ""
            response_stream = model.generate_content(
                prompt,
                generation_config=generation_config,
                stream=True
            )

        # Yield chunks
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text

    def count_tokens(self, text: str) -> int:
        """
        Count tokens using Gemini's token counter
        """
        try:
            model = self._get_model()
            result = model.count_tokens(text)
            return result.total_tokens
        except ImportError as e:
            logger.warning(f"Gemini package not installed: {e}")
            # Fallback: approximate with character count
            return len(text) // 4
        except Exception as e:
            # Fallback for API errors or unsupported operations
            logger.warning(f"Token counting failed: {type(e).__name__}: {e}")
            # Gemini uses similar tokenization to GPT (roughly 4 chars per token)
            return len(text) // 4

    def validate_config(self) -> bool:
        """Validate Gemini configuration"""
        if not self.api_key:
            return False

        # Try a simple API call to validate
        try:
            genai = self._get_genai()
            # List available models to validate API key
            list(genai.list_models())
            return True
        except ImportError as e:
            logger.warning(f"Gemini package not installed: {e}")
            return False
        except ValueError as e:
            logger.warning(f"Invalid Gemini configuration: {e}")
            return False
        except Exception as e:
            # Catch Gemini API errors (authentication, quota, etc.)
            logger.error(f"Gemini validation failed: {type(e).__name__}: {e}", exc_info=True)
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get Gemini model information"""
        capabilities = ["text_generation", "streaming"]

        # Add multimodal capability for supported models
        if "pro" in self.model_name or "flash" in self.model_name:
            capabilities.extend(["vision", "multimodal"])

        # Add large context for 1.5 models
        context_window = "2M tokens" if "1.5" in self.model_name else "32K tokens"

        return {
            "provider": "GeminiProvider",
            "model": self.model_name,
            "context_window": context_window,
            "capabilities": capabilities,
            "pricing": "Free tier: 60 requests/min, 1M tokens/day" if "flash" in self.model_name else "Check Google AI Studio"
        }