"""
Router para configuración de proveedores LLM (Administración)

Sprint 3 - HU-ADM-004
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import os

from ..schemas.common import APIResponse

router = APIRouter(prefix="/admin/llm", tags=["Admin - LLM Configuration"])


class LLMProviderConfig(BaseModel):
    """Configuración de un proveedor LLM"""
    provider: str = Field(..., description="Nombre del proveedor (openai, gemini, anthropic, mock)")
    enabled: bool = Field(..., description="Si el proveedor está habilitado")
    api_key_configured: bool = Field(..., description="Si tiene API key configurada")
    model: Optional[str] = Field(None, description="Modelo por defecto")
    temperature: Optional[float] = Field(None, description="Temperatura por defecto")
    max_tokens: Optional[int] = Field(None, description="Máximo de tokens")
    limits: Optional[Dict[str, Any]] = Field(None, description="Límites de uso")
    privacy_compliant: bool = Field(..., description="Si cumple con privacidad institucional")
    cost_per_1k_tokens: Optional[float] = Field(None, description="Costo estimado por 1K tokens (USD)")


class LLMProviderUpdate(BaseModel):
    """Actualización de configuración de proveedor"""
    enabled: Optional[bool] = Field(None, description="Habilitar/deshabilitar")
    model: Optional[str] = Field(None, description="Modelo por defecto")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Temperatura (0.0-2.0)")
    max_tokens: Optional[int] = Field(None, gt=0, description="Máximo de tokens")
    daily_request_limit: Optional[int] = Field(None, description="Límite de requests por día")
    monthly_token_limit: Optional[int] = Field(None, description="Límite de tokens por mes")


@router.get(
    "/providers",
    response_model=APIResponse[List[LLMProviderConfig]],
    summary="Listar proveedores LLM",
    description="Lista todos los proveedores LLM disponibles con su configuración (HU-ADM-004)"
)
async def list_llm_providers() -> APIResponse[List[LLMProviderConfig]]:
    """
    Lista todos los proveedores LLM disponibles en el sistema.

    **HU-ADM-004**: Permite al administrador ver qué proveedores están configurados
    y cuáles están habilitados para uso institucional.

    **Información incluida:**
    - Estado de habilitación
    - Configuración de API keys (sin exponer valores)
    - Modelos disponibles
    - Límites de uso
    - Cumplimiento de privacidad
    - Costos estimados
    """
    # Leer configuración actual del sistema
    current_provider = os.getenv("LLM_PROVIDER", "mock")

    providers = [
        LLMProviderConfig(
            provider="mock",
            enabled=current_provider == "mock",
            api_key_configured=True,  # No requiere
            model="mock-model",
            temperature=0.7,
            max_tokens=2000,
            privacy_compliant=True,
            cost_per_1k_tokens=0.0,
            limits={
                "requests_per_day": "unlimited",
                "tokens_per_month": "unlimited"
            }
        ),
        LLMProviderConfig(
            provider="openai",
            enabled=current_provider == "openai",
            api_key_configured=bool(os.getenv("OPENAI_API_KEY")),
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
            privacy_compliant=False,  # Datos enviados a OpenAI
            cost_per_1k_tokens=0.03,  # GPT-4 input
            limits={
                "requests_per_day": os.getenv("OPENAI_DAILY_LIMIT", "unlimited"),
                "tokens_per_month": os.getenv("OPENAI_MONTHLY_TOKEN_LIMIT", "unlimited")
            }
        ),
        LLMProviderConfig(
            provider="gemini",
            enabled=current_provider == "gemini",
            api_key_configured=bool(os.getenv("GEMINI_API_KEY")),
            model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "8192")),
            privacy_compliant=False,  # Datos enviados a Google
            cost_per_1k_tokens=0.0,  # Free tier
            limits={
                "requests_per_day": "1500",  # 60 req/min * 60 min * 24h / 60
                "tokens_per_month": "1000000"  # Free tier
            }
        ),
        LLMProviderConfig(
            provider="anthropic",
            enabled=current_provider == "anthropic",
            api_key_configured=bool(os.getenv("ANTHROPIC_API_KEY")),
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
            temperature=float(os.getenv("ANTHROPIC_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "4096")),
            privacy_compliant=False,  # Datos enviados a Anthropic
            cost_per_1k_tokens=0.015,  # Claude 3 Sonnet
            limits={
                "requests_per_day": os.getenv("ANTHROPIC_DAILY_LIMIT", "unlimited"),
                "tokens_per_month": os.getenv("ANTHROPIC_MONTHLY_TOKEN_LIMIT", "unlimited")
            }
        ),
    ]

    return APIResponse(
        success=True,
        data=providers,
        message=f"Se encontraron {len(providers)} proveedores LLM configurados"
    )


@router.get(
    "/providers/{provider_name}",
    response_model=APIResponse[LLMProviderConfig],
    summary="Obtener configuración de proveedor",
    description="Obtiene la configuración detallada de un proveedor LLM específico"
)
async def get_provider_config(provider_name: str) -> APIResponse[LLMProviderConfig]:
    """
    Obtiene la configuración detallada de un proveedor LLM específico.
    """
    # Obtener lista de proveedores
    providers_response = await list_llm_providers()
    providers = providers_response.data

    # Buscar proveedor específico
    provider = next((p for p in providers if p.provider == provider_name), None)

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found. Available: mock, openai, gemini, anthropic"
        )

    return APIResponse(
        success=True,
        data=provider,
        message=f"Configuración de proveedor {provider_name}"
    )


@router.patch(
    "/providers/{provider_name}",
    response_model=APIResponse[Dict[str, Any]],
    summary="Actualizar configuración de proveedor",
    description="Actualiza la configuración de un proveedor LLM (HU-ADM-004)"
)
async def update_provider_config(
    provider_name: str,
    update: LLMProviderUpdate
) -> APIResponse[Dict[str, Any]]:
    """
    Actualiza la configuración de un proveedor LLM.

    **HU-ADM-004**: Permite al administrador configurar límites de uso,
    habilitar/deshabilitar proveedores, y ajustar parámetros.

    **IMPORTANTE**: En el MVP actual, esto solo retorna una confirmación.
    En producción, esto debería:
    1. Actualizar variables de entorno o archivo de configuración
    2. Reiniciar el servicio LLM con la nueva configuración
    3. Validar que el proveedor funciona con las nuevas configuraciones
    4. Registrar el cambio en auditoría

    **Ejemplo:**
    ```bash
    PATCH /api/v1/admin/llm/providers/openai
    {
      "enabled": true,
      "model": "gpt-3.5-turbo",
      "daily_request_limit": 1000,
      "monthly_token_limit": 500000
    }
    ```
    """
    # Validar que el proveedor existe
    valid_providers = ["mock", "openai", "gemini", "anthropic"]
    if provider_name not in valid_providers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found. Available: {', '.join(valid_providers)}"
        )

    # En el MVP, solo retornamos confirmación
    # En producción, aquí se actualizaría la configuración real

    changes = {}
    if update.enabled is not None:
        changes["enabled"] = update.enabled
    if update.model is not None:
        changes["model"] = update.model
    if update.temperature is not None:
        changes["temperature"] = update.temperature
    if update.max_tokens is not None:
        changes["max_tokens"] = update.max_tokens
    if update.daily_request_limit is not None:
        changes["daily_request_limit"] = update.daily_request_limit
    if update.monthly_token_limit is not None:
        changes["monthly_token_limit"] = update.monthly_token_limit

    return APIResponse(
        success=True,
        data={
            "provider": provider_name,
            "changes_applied": changes,
            "note": "En producción, requiere reinicio del servicio para aplicar cambios",
            "next_steps": [
                f"Actualizar archivo .env con nuevos valores",
                "Reiniciar servidor: python scripts/run_api.py",
                "Verificar que el proveedor funciona correctamente"
            ]
        },
        message=f"Configuración de {provider_name} actualizada (MVP: solo confirmación)"
    )


@router.get(
    "/usage/stats",
    response_model=APIResponse[Dict[str, Any]],
    summary="Obtener estadísticas de uso de LLM",
    description="Obtiene estadísticas de uso de proveedores LLM"
)
async def get_llm_usage_stats() -> APIResponse[Dict[str, Any]]:
    """
    Obtiene estadísticas de uso de proveedores LLM.

    **Útil para:**
    - Monitorear costos
    - Identificar patrones de uso
    - Planificar capacidad
    - Justificar presupuesto

    **NOTA**: En el MVP actual, retorna datos de ejemplo.
    En producción, esto debería leer de una tabla `llm_usage_logs`.
    """
    # En el MVP, retornamos datos de ejemplo
    # En producción, esto vendría de la base de datos

    stats = {
        "current_month": "2025-11",
        "total_requests": 1248,
        "total_tokens": 345678,
        "estimated_cost_usd": 12.45,
        "by_provider": {
            "mock": {
                "requests": 856,
                "tokens": 245000,
                "cost_usd": 0.0,
                "percentage": 68.6
            },
            "openai": {
                "requests": 392,
                "tokens": 100678,
                "cost_usd": 12.45,
                "percentage": 31.4
            },
            "gemini": {
                "requests": 0,
                "tokens": 0,
                "cost_usd": 0.0,
                "percentage": 0.0
            }
        },
        "top_activities": [
            {"activity_id": "prog2_tp1_colas", "requests": 423, "cost_usd": 5.12},
            {"activity_id": "prog2_tp2_arboles", "requests": 389, "cost_usd": 4.67},
            {"activity_id": "prog2_tp3_grafos", "requests": 234, "cost_usd": 2.66}
        ],
        "limits_status": {
            "daily_limit": {"used": 48, "limit": 1000, "percentage": 4.8},
            "monthly_limit": {"used": 345678, "limit": 1000000, "percentage": 34.6}
        }
    }

    return APIResponse(
        success=True,
        data=stats,
        message="Estadísticas de uso de LLM (datos de ejemplo en MVP)"
    )