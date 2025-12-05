"""
Enumeraciones para validación de schemas de la API
"""
from enum import Enum
from ...core.cognitive_engine import AgentMode

# DEPRECATED: Use AgentMode from cognitive_engine instead
# Mantener por compatibilidad temporal, pero usar AgentMode en código nuevo
SessionMode = AgentMode  # Alias for backward compatibility


class SessionStatus(str, Enum):
    """Estados de sesión válidos"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ABORTED = "aborted"
    PAUSED = "paused"


class CognitiveIntent(str, Enum):
    """Intenciones cognitivas del estudiante"""
    UNDERSTANDING = "UNDERSTANDING"  # Busca entender conceptos
    EXPLORATION = "EXPLORATION"  # Explora posibilidades
    PLANNING = "PLANNING"  # Planifica solución
    IMPLEMENTATION = "IMPLEMENTATION"  # Implementa código
    DEBUGGING = "DEBUGGING"  # Depura errores
    VALIDATION = "VALIDATION"  # Valida solución
    REFLECTION = "REFLECTION"  # Reflexiona sobre proceso
    UNKNOWN = "UNKNOWN"  # No determinado