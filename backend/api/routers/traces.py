"""
Router para consultas de trazabilidad N4
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status

from ...database.repositories import TraceRepository, SessionRepository
from ...models.trace import CognitiveTrace
from ..deps import get_trace_repository, get_session_repository
from ..schemas.common import APIResponse, PaginatedResponse, PaginationParams, PaginationMeta
from ..exceptions import SessionNotFoundError
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter(prefix="/traces", tags=["Traceability"])


# Schemas específicos para trazas
class TraceResponse(BaseModel):
    """Response con información de una traza N4"""

    id: str
    session_id: str
    student_id: str
    activity_id: str
    trace_level: str
    interaction_type: str
    cognitive_state: Optional[str]
    cognitive_intent: Optional[str]
    content: str
    ai_involvement: Optional[float]
    metadata: Optional[dict]
    timestamp: datetime

    class Config:
        from_attributes = True


class CognitivePath(BaseModel):
    """Representación del camino cognitivo del estudiante"""

    session_id: str
    student_id: str
    activity_id: str
    states_sequence: List[str] = Field(..., description="Secuencia de estados cognitivos")
    transitions: List[dict] = Field(..., description="Transiciones entre estados")
    total_traces: int
    n4_traces_count: int
    ai_dependency_evolution: List[float] = Field(..., description="Evolución del AI involvement")
    strategy_changes: List[dict] = Field(..., description="Cambios de estrategia detectados")


@router.get(
    "/{session_id}",
    response_model=PaginatedResponse[TraceResponse],
    summary="Get Session Traces",
    description="Obtiene todas las trazas de una sesión con filtros opcionales",
)
async def get_session_traces(
    session_id: str,
    trace_level: Optional[str] = Query(None, description="Filtrar por nivel: N1, N2, N3, N4"),
    interaction_type: Optional[str] = Query(None, description="Filtrar por tipo de interacción"),
    cognitive_state: Optional[str] = Query(None, description="Filtrar por estado cognitivo"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    session_repo: SessionRepository = Depends(get_session_repository),
    trace_repo: TraceRepository = Depends(get_trace_repository),
) -> PaginatedResponse[TraceResponse]:
    """
    Obtiene todas las trazas de una sesión.

    Permite filtrar por nivel, tipo de interacción y estado cognitivo.

    Args:
        session_id: ID de la sesión
        trace_level: Filtro por nivel (N1, N2, N3, N4)
        interaction_type: Filtro por tipo de interacción
        cognitive_state: Filtro por estado cognitivo
        page: Número de página
        page_size: Elementos por página
        session_repo: Repositorio de sesiones (inyectado)
        trace_repo: Repositorio de trazas (inyectado)

    Returns:
        PaginatedResponse con lista de trazas

    Raises:
        SessionNotFoundError: Si la sesión no existe
    """
    # Verificar que la sesión existe
    db_session = session_repo.get_by_id(session_id)
    if not db_session:
        raise SessionNotFoundError(session_id)

    # Obtener trazas de la sesión
    all_traces = trace_repo.get_by_session(session_id)

    # Aplicar filtros
    filtered_traces = all_traces

    if trace_level:
        filtered_traces = [t for t in filtered_traces if t.trace_level == trace_level]

    if interaction_type:
        filtered_traces = [t for t in filtered_traces if t.interaction_type == interaction_type]

    if cognitive_state:
        filtered_traces = [t for t in filtered_traces if t.cognitive_state == cognitive_state]

    # Calcular paginación
    total_items = len(filtered_traces)
    offset = (page - 1) * page_size
    total_pages = (total_items + page_size - 1) // page_size

    # Aplicar paginación
    paginated_traces = filtered_traces[offset : offset + page_size]

    # Convertir a schemas de respuesta
    traces_data = [
        TraceResponse(
            id=t.id,
            session_id=t.session_id,
            student_id=t.student_id,
            activity_id=t.activity_id,
            trace_level=t.trace_level,
            interaction_type=t.interaction_type,
            cognitive_state=t.cognitive_state,
            cognitive_intent=t.cognitive_intent,
            content=t.content,
            ai_involvement=t.ai_involvement,
            metadata=t.trace_metadata,  # Usar trace_metadata del ORM
            timestamp=t.created_at,  # Usar created_at en lugar de timestamp
        )
        for t in paginated_traces
    ]

    # Metadatos de paginación
    pagination_meta = PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )

    return PaginatedResponse(
        success=True,
        data=traces_data,
        pagination=pagination_meta,
    )


@router.get(
    "/{session_id}/cognitive-path",
    response_model=APIResponse[CognitivePath],
    summary="Get Cognitive Path",
    description="Reconstruye el camino cognitivo completo del estudiante en una sesión",
)
async def get_cognitive_path(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repository),
    trace_repo: TraceRepository = Depends(get_trace_repository),
) -> APIResponse[CognitivePath]:
    """
    Reconstruye el camino cognitivo completo del estudiante.

    Analiza la secuencia de trazas N4 para reconstruir:
    - Secuencia de estados cognitivos
    - Transiciones entre estados
    - Evolución de la dependencia de IA
    - Cambios de estrategia

    Args:
        session_id: ID de la sesión
        session_repo: Repositorio de sesiones (inyectado)
        trace_repo: Repositorio de trazas (inyectado)

    Returns:
        APIResponse con el camino cognitivo reconstruido

    Raises:
        SessionNotFoundError: Si la sesión no existe
    """
    # Verificar que la sesión existe
    db_session = session_repo.get_by_id(session_id)
    if not db_session:
        raise SessionNotFoundError(session_id)

    # Obtener todas las trazas ordenadas cronológicamente
    all_traces = trace_repo.get_by_session(session_id)

    # Filtrar solo trazas N4 para análisis cognitivo profundo
    n4_traces = [t for t in all_traces if t.trace_level == "n4_cognitivo"]

    # Reconstruir secuencia de estados cognitivos
    states_sequence = []
    for trace in all_traces:
        if trace.cognitive_state:
            states_sequence.append(trace.cognitive_state)

    # Detectar transiciones entre estados
    transitions = []
    for i in range(len(states_sequence) - 1):
        from_state = states_sequence[i]
        to_state = states_sequence[i + 1]
        if from_state != to_state:
            transitions.append({
                "from": from_state,
                "to": to_state,
                "index": i,
                "timestamp": all_traces[i + 1].created_at.isoformat() if i + 1 < len(all_traces) else None,
            })

    # Evolución de AI involvement
    ai_dependency_evolution = [
        t.ai_involvement if t.ai_involvement is not None else 0.5
        for t in all_traces
    ]

    # Detectar cambios de estrategia (significativos cambios en AI involvement)
    strategy_changes = []
    for i in range(len(ai_dependency_evolution) - 1):
        current = ai_dependency_evolution[i]
        next_val = ai_dependency_evolution[i + 1]
        change = abs(next_val - current)

        # Cambio significativo: > 0.3
        if change > 0.3:
            strategy_changes.append({
                "index": i,
                "from_involvement": round(current, 2),
                "to_involvement": round(next_val, 2),
                "change": round(next_val - current, 2),
                "timestamp": all_traces[i + 1].created_at.isoformat() if i + 1 < len(all_traces) else None,
                "cognitive_state": all_traces[i + 1].cognitive_state if i + 1 < len(all_traces) else None,
            })

    # Construir camino cognitivo
    cognitive_path = CognitivePath(
        session_id=session_id,
        student_id=db_session.student_id,
        activity_id=db_session.activity_id,
        states_sequence=states_sequence,
        transitions=transitions,
        total_traces=len(all_traces),
        n4_traces_count=len(n4_traces),
        ai_dependency_evolution=ai_dependency_evolution,
        strategy_changes=strategy_changes,
    )

    return APIResponse(
        success=True,
        data=cognitive_path,
        message=f"Cognitive path reconstructed with {len(all_traces)} traces",
    )


@router.get(
    "/student/{student_id}",
    response_model=PaginatedResponse[TraceResponse],
    summary="Get Student Traces",
    description="Obtiene todas las trazas de un estudiante a través de todas sus sesiones",
)
async def get_student_traces(
    student_id: str,
    activity_id: Optional[str] = Query(None, description="Filtrar por actividad"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    trace_repo: TraceRepository = Depends(get_trace_repository),
) -> PaginatedResponse[TraceResponse]:
    """
    Obtiene todas las trazas de un estudiante.

    Útil para análisis longitudinal del progreso del estudiante.

    Args:
        student_id: ID del estudiante
        activity_id: Filtro opcional por actividad
        page: Número de página
        page_size: Elementos por página
        trace_repo: Repositorio de trazas (inyectado)

    Returns:
        PaginatedResponse con lista de trazas del estudiante
    """
    # Obtener trazas del estudiante
    all_traces = trace_repo.get_by_student(student_id)

    # Filtrar por actividad si se especifica
    if activity_id:
        all_traces = [t for t in all_traces if t.activity_id == activity_id]

    # Calcular paginación
    total_items = len(all_traces)
    offset = (page - 1) * page_size
    total_pages = (total_items + page_size - 1) // page_size

    # Aplicar paginación
    paginated_traces = all_traces[offset : offset + page_size]

    # Convertir a schemas de respuesta
    traces_data = [
        TraceResponse(
            id=t.id,
            session_id=t.session_id,
            student_id=t.student_id,
            activity_id=t.activity_id,
            trace_level=t.trace_level,
            interaction_type=t.interaction_type,
            cognitive_state=t.cognitive_state,
            cognitive_intent=t.cognitive_intent,
            content=t.content,
            ai_involvement=t.ai_involvement,
            metadata=t.trace_metadata,  # Usar trace_metadata del ORM
            timestamp=t.created_at,  # Usar created_at en lugar de timestamp
        )
        for t in paginated_traces
    ]

    # Metadatos de paginación
    pagination_meta = PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )

    return PaginatedResponse(
        success=True,
        data=traces_data,
        pagination=pagination_meta,
    )