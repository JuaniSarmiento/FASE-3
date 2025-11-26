"""
OpenAI LLM provider implementation

Provides integration with OpenAI's API (GPT-4, GPT-3.5, etc.)

Note: Requires 'openai' package to be installed:
    pip install openai
"""
from typing import Optional, Dict, Any, List
import logging
import threading
import time

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


def _sanitize_api_key(api_key: str) -> str:
    """
    Sanitiza API key para logging seguro.
    Muestra solo los primeros 10 caracteres seguidos de asteriscos.

    Args:
        api_key: API key completa

    Returns:
        API key sanitizada (ej: "sk-proj-Ab***")
    """
    if not api_key or len(api_key) < 10:
        return "***"
    return f"{api_key[:10]}***"


class OpenAIProvider(LLMProvider):
    """
    OpenAI LLM provider

    Supports:
    - GPT-4 (gpt-4, gpt-4-turbo)
    - GPT-3.5 (gpt-3.5-turbo)
    - Legacy models (text-davinci-003, etc.)

    Configuration:
        api_key: OpenAI API key (required)
        model: Model name (default: gpt-4)
        organization: Organization ID (optional)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

        self.api_key = self.config.get("api_key")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set 'api_key' in config.")

        self.model = self.config.get("model", "gpt-4")
        self.organization = self.config.get("organization")

        # Log configuration with sanitized API key
        logger.info(
            "OpenAI provider initialized",
            extra={
                "model": self.model,
                "api_key": _sanitize_api_key(self.api_key),
                "organization": self.organization or "default"
            }
        )

        # Initialize OpenAI client (lazy import to avoid dependency issues)
        self._client = None
        self._client_lock = threading.Lock()  # Thread-safety for lazy init

    def _get_client(self):
        """Lazy initialization of OpenAI client. Thread-safe."""
        # Double-checked locking pattern for thread-safety
        if self._client is None:
            with self._client_lock:
                if self._client is None:
                    try:
                        import openai
                        self._client = openai.OpenAI(
                            api_key=self.api_key,
                            organization=self.organization
                        )
                    except ImportError:
                        raise ImportError(
                            "OpenAI package not installed. Install with: pip install openai"
                        )
        return self._client

    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion using OpenAI API"""
        client = self._get_client()

        # Convert messages to OpenAI format
        openai_messages = [
            {"role": m.role.value, "content": m.content}
            for m in messages
        ]

        # ✅ HIGH-01: Use context manager to track LLM call duration
        metrics = _get_metrics()
        if metrics:
            with metrics.record_llm_call("openai", self.model):
                return self._execute_openai_call(
                    client, openai_messages, temperature, max_tokens, **kwargs
                )
        else:
            return self._execute_openai_call(
                client, openai_messages, temperature, max_tokens, **kwargs
            )

    def _execute_openai_call(
        self,
        client,
        openai_messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    ) -> LLMResponse:
        """Execute the actual OpenAI API call (extracted for metrics instrumentation)"""
        # Call OpenAI API
        response = client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        # Extract response
        content = response.choices[0].message.content

        return LLMResponse(
            content=content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            metadata={
                "temperature": temperature,
                "max_tokens": max_tokens,
                "finish_reason": response.choices[0].finish_reason
            }
        )

    def generate_stream(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Generate streaming completion using OpenAI API"""
        client = self._get_client()

        # Convert messages to OpenAI format
        openai_messages = [
            {"role": m.role.value, "content": m.content}
            for m in messages
        ]

        # Call OpenAI API with streaming
        stream = client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )

        # Yield chunks
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def count_tokens(self, text: str) -> int:
        """
        Count tokens using tiktoken

        Note: Requires 'tiktoken' package:
            pip install tiktoken
        """
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model)
            return len(encoding.encode(text))
        except ImportError:
            # Fallback: approximate with character count
            return len(text) // 4

    def validate_config(self) -> bool:
        """Validate OpenAI configuration"""
        if not self.api_key:
            logger.warning("OpenAI API key not configured")
            return False

        # Try a simple API call to validate
        try:
            client = self._get_client()
            client.models.list()
            logger.info(
                "OpenAI configuration validated successfully",
                extra={"api_key": _sanitize_api_key(self.api_key)}
            )
            return True
        except ImportError as e:
            logger.warning(f"OpenAI package not installed: {e}")
            return False
        except ValueError as e:
            logger.warning(
                f"Invalid OpenAI configuration: {e}",
                extra={"api_key": _sanitize_api_key(self.api_key)}
            )
            return False
        except Exception as e:
            # Catch OpenAI API errors (AuthenticationError, RateLimitError, etc.)
            logger.error(
                f"OpenAI validation failed: {type(e).__name__}: {str(e)}",
                exc_info=True,
                extra={"api_key": _sanitize_api_key(self.api_key)}
            )
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get OpenAI model information"""
        return {
            "provider": "OpenAIProvider",
            "model": self.model,
            "organization": self.organization,
            "capabilities": [
                "text_generation",
                "streaming",
                "function_calling",
                "vision" if "vision" in self.model or "gpt-4" in self.model else None
            ]
        }