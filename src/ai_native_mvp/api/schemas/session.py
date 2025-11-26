"""
Schemas para sesiones de aprendizaje
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from .enums import SessionMode, SessionStatus


class SessionCreate(BaseModel):
    """Request para crear una nueva sesión"""

    student_id: str = Field(..., min_length=1, max_length=255, description="ID del estudiante")
    activity_id: str = Field(..., min_length=1, max_length=255, description="ID de la actividad")
    mode: SessionMode = Field(..., description="Modo de interacción: TUTOR, EVALUATOR, SIMULATOR, etc.")

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "student_001",
                "activity_id": "prog2_tp1_colas",
                "mode": "TUTOR"
            }
        }


class SessionUpdate(BaseModel):
    """Request para actualizar una sesión"""

    mode: Optional[SessionMode] = Field(None, description="Nuevo modo de interacción")
    status: Optional[SessionStatus] = Field(None, description="Nuevo estado: active, completed, aborted, paused")

    class Config:
        json_schema_extra = {
            "example": {
                "mode": "EVALUATOR",
                "status": "COMPLETED"
            }
        }


class SessionResponse(BaseModel):
    """Response con información de una sesión"""

    id: str = Field(..., description="ID de la sesión")
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: str = Field(..., description="ID de la actividad")
    mode: str = Field(..., description="Modo de interacción")
    status: str = Field(..., description="Estado de la sesión")
    start_time: datetime = Field(..., description="Timestamp de inicio")
    end_time: Optional[datetime] = Field(None, description="Timestamp de finalización")
    trace_count: int = Field(0, description="Número de trazas capturadas")
    risk_count: int = Field(0, description="Número de riesgos detectados")
    created_at: datetime = Field(..., description="Timestamp de creación")
    updated_at: datetime = Field(..., description="Timestamp de última actualización")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "session_abc123",
                "student_id": "student_001",
                "activity_id": "prog2_tp1_colas",
                "mode": "TUTOR",
                "status": "ACTIVE",
                "start_time": "2025-11-18T10:00:00Z",
                "end_time": None,
                "trace_count": 5,
                "risk_count": 1,
                "created_at": "2025-11-18T10:00:00Z",
                "updated_at": "2025-11-18T10:30:00Z"
            }
        }


class SessionListResponse(BaseModel):
    """Response con lista de sesiones"""

    sessions: List[SessionResponse] = Field(..., description="Lista de sesiones")
    total: int = Field(..., description="Total de sesiones")


class SessionDetailResponse(SessionResponse):
    """Response con detalles completos de una sesión"""

    traces_summary: dict = Field(..., description="Resumen de trazas por nivel")
    risks_summary: dict = Field(..., description="Resumen de riesgos por tipo")
    ai_dependency_score: Optional[float] = Field(None, description="Score de dependencia de IA (0-1)")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "session_abc123",
                "student_id": "student_001",
                "activity_id": "prog2_tp1_colas",
                "mode": "TUTOR",
                "status": "ACTIVE",
                "start_time": "2025-11-18T10:00:00Z",
                "end_time": None,
                "trace_count": 5,
                "risk_count": 1,
                "created_at": "2025-11-18T10:00:00Z",
                "updated_at": "2025-11-18T10:30:00Z",
                "traces_summary": {
                    "N1_SUPERFICIAL": 0,
                    "N2_TECNICO": 1,
                    "N3_INTERACCIONAL": 2,
                    "N4_COGNITIVO": 2
                },
                "risks_summary": {
                    "COGNITIVE_DELEGATION": 1,
                    "UNCRITICAL_ACCEPTANCE": 0
                },
                "ai_dependency_score": 0.35
            }
        }


# ============================================================================
# SCHEMAS PARA HISTORIAL DE SESIONES (HU-EST-008) - Sprint 6
# ============================================================================


class SessionHistoryFilters(BaseModel):
    """Filtros para consultar historial de sesiones"""

    start_date: Optional[date] = Field(None, description="Fecha de inicio del rango")
    end_date: Optional[date] = Field(None, description="Fecha de fin del rango")
    activity_id: Optional[str] = Field(None, description="Filtrar por actividad específica")
    mode: Optional[SessionMode] = Field(None, description="Filtrar por modo de interacción")
    status: Optional[SessionStatus] = Field(None, description="Filtrar por estado")
    min_competency: Optional[str] = Field(None, description="Competencia mínima: INICIAL, INTERMEDIO, AVANZADO, EXPERTO")

    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2025-11-01",
                "end_date": "2025-11-30",
                "activity_id": "prog2_tp1_colas",
                "mode": "TUTOR",
                "status": "COMPLETED",
                "min_competency": "INTERMEDIO"
            }
        }


class SessionSummary(BaseModel):
    """Resumen de una sesión para el historial"""

    session_id: str = Field(..., description="ID de la sesión")
    activity_id: str = Field(..., description="ID de la actividad")
    mode: str = Field(..., description="Modo de interacción")
    status: str = Field(..., description="Estado")
    start_time: datetime = Field(..., description="Inicio")
    end_time: Optional[datetime] = Field(None, description="Fin")
    duration_minutes: Optional[int] = Field(None, description="Duración en minutos")
    interactions_count: int = Field(0, description="Número de interacciones")
    ai_dependency_score: Optional[float] = Field(None, description="Score de dependencia de IA")
    competency_level: Optional[str] = Field(None, description="Nivel de competencia alcanzado")
    overall_score: Optional[float] = Field(None, description="Puntaje general (0-1)")
    risks_detected: int = Field(0, description="Riesgos detectados")
    critical_risks: int = Field(0, description="Riesgos críticos")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123",
                "activity_id": "prog2_tp1_colas",
                "mode": "TUTOR",
                "status": "COMPLETED",
                "start_time": "2025-11-18T10:00:00Z",
                "end_time": "2025-11-18T11:30:00Z",
                "duration_minutes": 90,
                "interactions_count": 12,
                "ai_dependency_score": 0.35,
                "competency_level": "INTERMEDIO",
                "overall_score": 0.75,
                "risks_detected": 2,
                "critical_risks": 0
            }
        }


class ProgressAggregation(BaseModel):
    """Agregaciones de progreso temporal"""

    total_sessions: int = Field(..., description="Total de sesiones")
    completed_sessions: int = Field(..., description="Sesiones completadas")
    total_interactions: int = Field(..., description="Total de interacciones")
    average_ai_dependency: float = Field(..., description="Dependencia promedio de IA (0-1)")
    competency_evolution: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Evolución de competencia por fecha"
    )
    activity_breakdown: Dict[str, int] = Field(
        default_factory=dict,
        description="Sesiones por actividad"
    )
    mode_breakdown: Dict[str, int] = Field(
        default_factory=dict,
        description="Sesiones por modo"
    )
    risk_summary: Dict[str, int] = Field(
        default_factory=dict,
        description="Resumen de riesgos"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_sessions": 15,
                "completed_sessions": 12,
                "total_interactions": 180,
                "average_ai_dependency": 0.42,
                "competency_evolution": [
                    {"date": "2025-11-01", "level": "INICIAL", "score": 0.5},
                    {"date": "2025-11-15", "level": "INTERMEDIO", "score": 0.7},
                    {"date": "2025-11-30", "level": "AVANZADO", "score": 0.85}
                ],
                "activity_breakdown": {
                    "prog2_tp1_colas": 5,
                    "prog2_tp2_arboles": 4,
                    "prog2_tp3_grafos": 6
                },
                "mode_breakdown": {
                    "TUTOR": 10,
                    "EVALUATOR": 3,
                    "SIMULATOR": 2
                },
                "risk_summary": {
                    "total_risks": 8,
                    "critical_risks": 1,
                    "high_risks": 3,
                    "resolved_risks": 6
                }
            }
        }


class SessionHistoryResponse(BaseModel):
    """Response completo del historial de sesiones"""

    student_id: str = Field(..., description="ID del estudiante")
    sessions: List[SessionSummary] = Field(..., description="Lista de sesiones")
    aggregations: ProgressAggregation = Field(..., description="Agregaciones y métricas")
    filters_applied: Optional[Dict[str, Any]] = Field(None, description="Filtros aplicados")

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "student_001",
                "sessions": [
                    {
                        "session_id": "session_abc123",
                        "activity_id": "prog2_tp1_colas",
                        "mode": "TUTOR",
                        "status": "COMPLETED",
                        "start_time": "2025-11-18T10:00:00Z",
                        "end_time": "2025-11-18T11:30:00Z",
                        "duration_minutes": 90,
                        "interactions_count": 12,
                        "ai_dependency_score": 0.35,
                        "competency_level": "INTERMEDIO",
                        "overall_score": 0.75,
                        "risks_detected": 2,
                        "critical_risks": 0
                    }
                ],
                "aggregations": {
                    "total_sessions": 15,
                    "completed_sessions": 12,
                    "total_interactions": 180,
                    "average_ai_dependency": 0.42,
                    "competency_evolution": [],
                    "activity_breakdown": {},
                    "mode_breakdown": {},
                    "risk_summary": {}
                },
                "filters_applied": {
                    "start_date": "2025-11-01",
                    "end_date": "2025-11-30"
                }
            }
        }