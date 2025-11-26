"""
Git Traceability API Endpoints - SPRINT 5 HU-SYS-008

Endpoints:
- POST /git/sync - Sync Git commits for a session
- GET /git/session/{session_id} - Get Git traces for a session
- GET /git/session/{session_id}/evolution - Get code evolution analysis
- GET /git/session/{session_id}/correlate - Correlate Git with cognitive traces
"""

import logging
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..deps import get_db, get_session_repository, get_trace_repository
from ...database.repositories import GitTraceRepository, SessionRepository, TraceRepository
from ...agents.git_integration import GitIntegrationAgent
from ...models.git_trace import GitTrace, CodeEvolution, GitN2CorrelationResult
from ..schemas.common import APIResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/git", tags=["Git Traceability (N2)"])


# =============================================================================
# REQUEST/RESPONSE SCHEMAS
# =============================================================================


class GitSyncRequest(BaseModel):
    """Request to sync Git commits for a session"""

    session_id: str = Field(description="Session ID")
    repo_path: str = Field(description="Path to Git repository")
    since: Optional[datetime] = Field(None, description="Start datetime (optional)")
    until: Optional[datetime] = Field(None, description="End datetime (optional)")


class GitSyncResponse(BaseModel):
    """Response from Git sync operation"""

    session_id: str
    commits_synced: int
    git_traces: List[dict]


class CodeEvolutionResponse(BaseModel):
    """Response with code evolution analysis"""

    session_id: str
    total_commits: int
    total_lines_added: int
    total_lines_deleted: int
    net_lines_change: int
    unique_files_count: int
    pattern_distribution: dict
    commits_by_cognitive_state: dict
    commit_timeline: List[dict]


class CorrelationResponse(BaseModel):
    """Response with Git-Cognitive correlation"""

    session_id: str
    correlations: List[dict]
    avg_time_between_commit_and_interaction: Optional[float]
    commits_without_nearby_interactions: int
    interaction_to_commit_ratio: Optional[float]


# =============================================================================
# ENDPOINTS
# =============================================================================


@router.post(
    "/sync",
    response_model=APIResponse[GitSyncResponse],
    summary="Sync Git commits for a session",
    description="Capture Git commits from a repository and associate them with a learning session",
    status_code=status.HTTP_201_CREATED,
)
async def sync_git_commits(
    request: GitSyncRequest,
    db: Session = Depends(get_db),
    session_repo: SessionRepository = Depends(get_session_repository),
    trace_repo: TraceRepository = Depends(get_trace_repository),
) -> APIResponse[GitSyncResponse]:
    """
    Sync Git commits for a learning session

    Captures all commits in the specified time window and creates N2 traces.
    """
    # Validate session exists
    session = session_repo.get_by_id(request.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{request.session_id}' not found",
        )

    # Validate repository path
    repo_path = Path(request.repo_path)
    if not repo_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Repository path does not exist: {request.repo_path}",
        )

    # Get cognitive traces for correlation
    cognitive_traces = trace_repo.get_by_session(request.session_id)

    # Create Git integration agent
    git_trace_repo = GitTraceRepository(db)
    git_agent = GitIntegrationAgent(git_trace_repo=git_trace_repo)

    try:
        # Capture commits
        git_traces = git_agent.capture_session_commits(
            repo_path=str(repo_path),
            session_id=request.session_id,
            student_id=session.student_id,
            activity_id=session.activity_id,
            since=request.since,
            until=request.until,
            cognitive_traces=cognitive_traces,
        )

        logger.info(
            "Git commits synced",
            extra={
                "session_id": request.session_id,
                "commits_synced": len(git_traces),
            },
        )

        return APIResponse(
            success=True,
            data=GitSyncResponse(
                session_id=request.session_id,
                commits_synced=len(git_traces),
                git_traces=[
                    {
                        "commit_hash": t.commit_hash,
                        "commit_message": t.commit_message,
                        "timestamp": t.timestamp.isoformat(),
                        "files_changed": len(t.files_changed),
                        "lines_added": t.total_lines_added,
                        "lines_deleted": t.total_lines_deleted,
                        "patterns": [p.value for p in t.detected_patterns],
                    }
                    for t in git_traces
                ],
            ),
            message=f"Successfully synced {len(git_traces)} commits",
        )

    except Exception as e:
        logger.error(
            "Error syncing Git commits",
            exc_info=True,
            extra={"session_id": request.session_id, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing Git commits: {str(e)}",
        )


@router.get(
    "/session/{session_id}",
    response_model=APIResponse[List[dict]],
    summary="Get Git traces for a session",
    description="Retrieve all Git N2 traces associated with a learning session",
)
async def get_session_git_traces(
    session_id: str,
    db: Session = Depends(get_db),
) -> APIResponse[List[dict]]:
    """
    Get all Git traces for a session

    Returns list of commits with metadata and analysis.
    """
    git_trace_repo = GitTraceRepository(db)
    git_traces = git_trace_repo.get_by_session(session_id)

    if not git_traces:
        return APIResponse(
            success=True,
            data=[],
            message=f"No Git traces found for session '{session_id}'",
        )

    traces_data = [
        {
            "id": t.id,
            "commit_hash": t.commit_hash,
            "commit_message": t.commit_message,
            "author_name": t.author_name,
            "author_email": t.author_email,
            "timestamp": t.timestamp.isoformat(),
            "branch_name": t.branch_name,
            "event_type": t.event_type,
            "files_changed": len(t.files_changed),
            "total_lines_added": t.total_lines_added,
            "total_lines_deleted": t.total_lines_deleted,
            "is_merge": t.is_merge,
            "is_revert": t.is_revert,
            "detected_patterns": t.detected_patterns,
            "cognitive_state_during_commit": t.cognitive_state_during_commit,
            "time_since_last_interaction_minutes": t.time_since_last_interaction_minutes,
        }
        for t in git_traces
    ]

    logger.info(
        "Git traces retrieved",
        extra={"session_id": session_id, "count": len(traces_data)},
    )

    return APIResponse(
        success=True,
        data=traces_data,
        message=f"Retrieved {len(traces_data)} Git traces",
    )


@router.get(
    "/session/{session_id}/evolution",
    response_model=APIResponse[CodeEvolutionResponse],
    summary="Get code evolution analysis",
    description="Analyze code evolution during a session (commits, patterns, complexity)",
)
async def get_code_evolution(
    session_id: str,
    db: Session = Depends(get_db),
) -> APIResponse[CodeEvolutionResponse]:
    """
    Get code evolution analysis for a session

    Aggregates Git traces to show how code evolved during learning.
    """
    git_trace_repo = GitTraceRepository(db)
    git_traces_db = git_trace_repo.get_by_session(session_id)

    if not git_traces_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Git traces found for session '{session_id}'",
        )

    # Convert ORM to Pydantic models
    from ...models.git_trace import GitTrace, GitFileChange, CodePattern

    git_traces = []
    for t in git_traces_db:
        git_traces.append(
            GitTrace(
                id=t.id,
                session_id=t.session_id,
                student_id=t.student_id,
                activity_id=t.activity_id,
                event_type=t.event_type,
                commit_hash=t.commit_hash,
                commit_message=t.commit_message,
                author_name=t.author_name,
                author_email=t.author_email,
                timestamp=t.timestamp,
                branch_name=t.branch_name,
                parent_commits=t.parent_commits,
                files_changed=[GitFileChange(**f) for f in t.files_changed],
                total_lines_added=t.total_lines_added,
                total_lines_deleted=t.total_lines_deleted,
                diff=t.diff,
                is_merge=t.is_merge,
                is_revert=t.is_revert,
                detected_patterns=[CodePattern(p) for p in t.detected_patterns],
                complexity_delta=t.complexity_delta,
                related_cognitive_traces=t.related_cognitive_traces,
                cognitive_state_during_commit=t.cognitive_state_during_commit,
                time_since_last_interaction_minutes=t.time_since_last_interaction_minutes,
                repo_path=t.repo_path,
                remote_url=t.remote_url,
            )
        )

    # Analyze evolution
    git_agent = GitIntegrationAgent()
    evolution = git_agent.analyze_code_evolution(session_id, git_traces)

    logger.info(
        "Code evolution analyzed",
        extra={
            "session_id": session_id,
            "total_commits": evolution.total_commits,
        },
    )

    return APIResponse(
        success=True,
        data=CodeEvolutionResponse(
            session_id=evolution.session_id,
            total_commits=evolution.total_commits,
            total_lines_added=evolution.total_lines_added,
            total_lines_deleted=evolution.total_lines_deleted,
            net_lines_change=evolution.net_lines_change,
            unique_files_count=evolution.unique_files_count,
            pattern_distribution=evolution.pattern_distribution,
            commits_by_cognitive_state=evolution.commits_by_cognitive_state,
            commit_timeline=evolution.commit_timeline,
        ),
        message="Code evolution analysis completed",
    )


@router.get(
    "/session/{session_id}/correlate",
    response_model=APIResponse[CorrelationResponse],
    summary="Correlate Git with cognitive traces",
    description="Find temporal relationships between commits (N2) and AI interactions (N3/N4)",
)
async def correlate_git_cognitive(
    session_id: str,
    db: Session = Depends(get_db),
    trace_repo: TraceRepository = Depends(get_trace_repository),
) -> APIResponse[CorrelationResponse]:
    """
    Correlate Git events with cognitive traces

    Identifies patterns like:
    - Commits immediately after AI assistance
    - Commits without nearby interactions (external AI use?)
    - Cognitive state during commits
    """
    git_trace_repo = GitTraceRepository(db)
    git_traces_db = git_trace_repo.get_by_session(session_id)

    if not git_traces_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Git traces found for session '{session_id}'",
        )

    # Get cognitive traces
    cognitive_traces = trace_repo.get_by_session(session_id)

    # Convert ORM to Pydantic
    from ...models.git_trace import GitTrace, GitFileChange, CodePattern

    git_traces = []
    for t in git_traces_db:
        git_traces.append(
            GitTrace(
                id=t.id,
                session_id=t.session_id,
                student_id=t.student_id,
                activity_id=t.activity_id,
                event_type=t.event_type,
                commit_hash=t.commit_hash,
                commit_message=t.commit_message,
                author_name=t.author_name,
                author_email=t.author_email,
                timestamp=t.timestamp,
                branch_name=t.branch_name,
                parent_commits=t.parent_commits,
                files_changed=[GitFileChange(**f) for f in t.files_changed],
                total_lines_added=t.total_lines_added,
                total_lines_deleted=t.total_lines_deleted,
                diff=t.diff,
                is_merge=t.is_merge,
                is_revert=t.is_revert,
                detected_patterns=[CodePattern(p) for p in t.detected_patterns],
                complexity_delta=t.complexity_delta,
                related_cognitive_traces=t.related_cognitive_traces,
                cognitive_state_during_commit=t.cognitive_state_during_commit,
                time_since_last_interaction_minutes=t.time_since_last_interaction_minutes,
                repo_path=t.repo_path,
                remote_url=t.remote_url,
            )
        )

    # Correlate
    git_agent = GitIntegrationAgent()
    correlation = git_agent.correlate_git_with_cognitive_traces(
        git_traces, cognitive_traces
    )

    logger.info(
        "Git-Cognitive correlation completed",
        extra={
            "session_id": session_id,
            "correlations": len(correlation.correlations),
        },
    )

    return APIResponse(
        success=True,
        data=CorrelationResponse(
            session_id=correlation.session_id,
            correlations=correlation.correlations,
            avg_time_between_commit_and_interaction=correlation.avg_time_between_commit_and_interaction,
            commits_without_nearby_interactions=correlation.commits_without_nearby_interactions,
            interaction_to_commit_ratio=correlation.interaction_to_commit_ratio,
        ),
        message="Correlation analysis completed",
    )
