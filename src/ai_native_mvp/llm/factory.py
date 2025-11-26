"""
LLM Provider Factory

Centraliza la creación y configuración de proveedores LLM.
Implementa Factory Pattern para bajo acoplamiento y extensibilidad.

Soporta múltiples proveedores:
- mock: Provider simulado para testing/desarrollo (sin API calls)
- openai: GPT-4, GPT-3.5 Turbo (requiere OPENAI_API_KEY)
- gemini: Google Gemini 1.5 Flash (requiere GEMINI_API_KEY)
- anthropic: Claude Sonnet (futuro, requiere ANTHROPIC_API_KEY)

Usage:
    >>> from src.ai_native_mvp.llm import LLMProviderFactory
    >>>
    >>> # Método 1: Desde variables de entorno (recomendado)
    >>> provider = LLMProviderFactory.create_from_env()
    >>>
    >>> # Método 2: Configuración manual
    >>> provider = LLMProviderFactory.create("openai", {
    ...     "api_key": "sk-...",
    ...     "model": "gpt-4"
    ... })
    >>>
    >>> # Generar respuesta
    >>> response = provider.generate(messages, temperature=0.7)
"""
from typing import Optional, Dict, Any

from .base import LLMProvider
from .mock import MockLLMProvider


class LLMProviderFactory:
    """
    Factory for creating LLM providers

    Supports:
    - mock: Mock provider for testing/development
    - openai: OpenAI provider (GPT-4, GPT-3.5)
    - anthropic: Anthropic provider (Claude)
    - ollama: Ollama provider (local models)

    Usage:
        >>> factory = LLMProviderFactory()
        >>> provider = factory.create("mock")
        >>> provider = factory.create("openai", {"api_key": "sk-..."})
    """

    # Registry of available providers
    _providers = {
        "mock": MockLLMProvider,
    }

    @classmethod
    def register_provider(cls, name: str, provider_class):
        """
        Register a new provider type

        Args:
            name: Provider identifier
            provider_class: Provider class (must inherit from LLMProvider)
        """
        if not issubclass(provider_class, LLMProvider):
            raise ValueError(f"{provider_class} must inherit from LLMProvider")

        cls._providers[name] = provider_class

    @classmethod
    def create(
        cls,
        provider_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> LLMProvider:
        """
        Create LLM provider instance

        Args:
            provider_type: Type of provider ("mock", "openai", etc.)
            config: Provider-specific configuration

        Returns:
            Configured LLM provider instance

        Raises:
            ValueError: If provider type is not registered
        """
        if provider_type not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unknown provider type: {provider_type}. "
                f"Available providers: {available}"
            )

        provider_class = cls._providers[provider_type]
        return provider_class(config)

    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of registered provider types"""
        return list(cls._providers.keys())

    @classmethod
    def _build_provider_config(
        cls,
        provider_type: str,
        env_prefix: str,
        default_model: str,
        api_key_url: str,
        optional_fields: Optional[Dict[str, tuple]] = None
    ) -> Dict[str, Any]:
        """
        ✅ REFACTORED (2025-11-22): Construcción genérica de config (H2 - DRY)

        Elimina duplicación de 80+ líneas en create_from_env().

        Args:
            provider_type: Tipo de proveedor (para mensajes de error)
            env_prefix: Prefijo de variables de entorno (ej: "OPENAI", "GEMINI")
            default_model: Modelo por defecto si no se especifica
            api_key_url: URL donde obtener API key (para mensaje de error)
            optional_fields: Dict de campos opcionales
                Formato: {config_key: (env_var, parser_func, default_value)}
                Ejemplo: {"temperature": ("OPENAI_TEMPERATURE", float, None)}

        Returns:
            Dict de configuración para el provider

        Raises:
            ValueError: Si falta API key requerida

        Example:
            >>> cls._build_provider_config(
            ...     "openai", "OPENAI", "gpt-4",
            ...     "https://platform.openai.com/api-keys",
            ...     {"temperature": ("OPENAI_TEMPERATURE", float, None)}
            ... )
            {'api_key': 'sk-...', 'model': 'gpt-4', 'temperature': 0.7}
        """
        import os

        config = {}

        # API Key (requerida para todos excepto mock/ollama)
        api_key_var = f"{env_prefix}_API_KEY"
        api_key = os.getenv(api_key_var)
        if not api_key:
            raise ValueError(
                f"{api_key_var} environment variable is required. "
                f"Get your API key from: {api_key_url}"
            )
        config["api_key"] = api_key

        # Model (requerido, con default)
        model_var = f"{env_prefix}_MODEL"
        config["model"] = os.getenv(model_var, default_model)

        # Campos opcionales (temperature, max_tokens, organization, etc.)
        if optional_fields:
            for config_key, (env_var, parser_func, default_value) in optional_fields.items():
                env_value = os.getenv(env_var)
                if env_value:
                    try:
                        config[config_key] = parser_func(env_value)
                    except (ValueError, TypeError):
                        # Si falla el parsing, usar default o ignorar
                        if default_value is not None:
                            config[config_key] = default_value

        return config

    @classmethod
    def create_from_env(cls, provider_type: str = None) -> LLMProvider:
        """
        Create provider using environment variables

        Looks for:
        - LLM_PROVIDER to determine which provider to use (if provider_type not specified)
        - OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS for OpenAI
        - ANTHROPIC_API_KEY, ANTHROPIC_MODEL for Anthropic
        - GEMINI_API_KEY, GEMINI_MODEL for Google Gemini
        - etc.

        Args:
            provider_type: Type of provider (optional, reads from LLM_PROVIDER env var if not provided)

        Returns:
            Configured provider instance

        Example:
            >>> # Set LLM_PROVIDER=gemini in .env
            >>> provider = LLMProviderFactory.create_from_env()  # Uses Gemini
            >>>
            >>> # Or specify explicitly
            >>> provider = LLMProviderFactory.create_from_env("gemini")
        """
        import os

        # If provider_type not specified, read from environment
        if provider_type is None:
            provider_type = os.getenv("LLM_PROVIDER", "mock")

        config = {}

        # ✅ REFACTORED (2025-11-22): Uso de builder genérico (H2 - DRY)
        # Elimina 80+ líneas de código duplicado

        if provider_type == "openai":
            config = cls._build_provider_config(
                provider_type="openai",
                env_prefix="OPENAI",
                default_model="gpt-4",
                api_key_url="https://platform.openai.com/api-keys",
                optional_fields={
                    "organization": ("OPENAI_ORGANIZATION", str, None),
                    "temperature": ("OPENAI_TEMPERATURE", float, None),
                    "max_tokens": ("OPENAI_MAX_TOKENS", int, None),
                }
            )

        elif provider_type == "anthropic":
            config = cls._build_provider_config(
                provider_type="anthropic",
                env_prefix="ANTHROPIC",
                default_model="claude-3-sonnet-20240229",
                api_key_url="https://console.anthropic.com/settings/keys",
                optional_fields=None  # Anthropic solo usa api_key y model
            )

        elif provider_type == "gemini":
            config = cls._build_provider_config(
                provider_type="gemini",
                env_prefix="GEMINI",
                default_model="gemini-1.5-flash",
                api_key_url="https://makersuite.google.com/app/apikey",
                optional_fields={
                    "temperature": ("GEMINI_TEMPERATURE", float, None),
                    "max_tokens": ("GEMINI_MAX_TOKENS", int, None),
                }
            )

        elif provider_type == "ollama":
            # Ollama no requiere API key, solo base_url y model
            config["base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            config["model"] = os.getenv("OLLAMA_MODEL", "llama2")

        elif provider_type == "mock":
            # Mock provider doesn't need configuration
            pass

        return cls.create(provider_type, config)


# Register OpenAI provider (lazy loading)
def _register_openai():
    """Register OpenAI provider if available"""
    try:
        from .openai_provider import OpenAIProvider
        LLMProviderFactory.register_provider("openai", OpenAIProvider)
    except ImportError:
        pass  # OpenAI not available


# Register Gemini provider (lazy loading)
def _register_gemini():
    """Register Google Gemini provider if available"""
    try:
        from .gemini_provider import GeminiProvider
        LLMProviderFactory.register_provider("gemini", GeminiProvider)
    except ImportError:
        pass  # Gemini not available


# Auto-register available providers
_register_openai()
_register_gemini()