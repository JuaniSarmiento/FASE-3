"""
Schemas (DTOs) para la API REST
"""
from .common import (
    APIResponse,
    ErrorDetail,
    ErrorResponse,
    HealthStatus,
    PaginatedResponse,
    PaginationMeta,
    PaginationParams,
)
from .interaction import (
    InteractionHistory,
    InteractionRequest,
    InteractionResponse,
    InteractionSummary,
)
from .session import (
    SessionCreate,
    SessionDetailResponse,
    SessionListResponse,
    SessionResponse,
    SessionUpdate,
)
from .activity import (
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse,
    ActivityListResponse,
    ActivityPublishRequest,
    ActivityArchiveRequest,
    PolicyConfig,
)

__all__ = [
    # Common
    "APIResponse",
    "ErrorDetail",
    "ErrorResponse",
    "HealthStatus",
    "PaginatedResponse",
    "PaginationMeta",
    "PaginationParams",
    # Session
    "SessionCreate",
    "SessionUpdate",
    "SessionResponse",
    "SessionListResponse",
    "SessionDetailResponse",
    # Interaction
    "InteractionRequest",
    "InteractionResponse",
    "InteractionHistory",
    "InteractionSummary",
    # Activity
    "ActivityCreate",
    "ActivityUpdate",
    "ActivityResponse",
    "ActivityListResponse",
    "ActivityPublishRequest",
    "ActivityArchiveRequest",
    "PolicyConfig",
]