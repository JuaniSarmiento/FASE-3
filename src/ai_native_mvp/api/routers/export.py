"""
Export Router - REST API endpoints for research data export

Endpoints:
- POST /api/v1/export/research-data - Export anonymized data for research
- GET /api/v1/export/history - View previous exports (admin only)
- GET /api/v1/export/{export_id} - Download specific export
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import (
    get_db_session,
    CognitiveTraceDB,
    EvaluationDB,
    RiskDB,
    SessionDB,
)
from ...export import (
    DataAnonymizer,
    AnonymizationConfig,
    ResearchDataExporter,
    ExportConfig,
    PrivacyValidator,
    GDPRCompliance,
)
from ..schemas.export import (
    ExportRequest,
    ExportResponse,
    ExportMetadata,
    ValidationReport,
    PrivacyMetrics,
)
from ..exceptions import AINativeAPIException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/export", tags=["Data Export"])


def fetch_data_from_db(
    db: Session, request: ExportRequest
) -> Dict[str, List[Dict]]:
    """
    Fetch data from database based on export request filters

    Args:
        db: Database session
        request: Export request with filters

    Returns:
        Dictionary mapping data types to lists of records
    """
    data = {}

    # Build base query filters
    filters = []
    if request.start_date:
        filters.append(SessionDB.start_time >= request.start_date)
    if request.end_date:
        filters.append(SessionDB.start_time <= request.end_date)
    if request.activity_ids:
        filters.append(SessionDB.activity_id.in_(request.activity_ids))

    # Fetch sessions
    if request.include_sessions:
        sessions = db.query(SessionDB).filter(*filters).all()
        data["sessions"] = [
            {
                "id": s.id,
                "student_id": s.student_id,
                "activity_id": s.activity_id,
                "mode": s.mode,
                "status": s.status,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "created_at": s.created_at,
            }
            for s in sessions
        ]
        session_ids = [s.id for s in sessions]
    else:
        session_ids = [s.id for s in db.query(SessionDB.id).filter(*filters).all()]

    # Fetch traces
    if request.include_traces and session_ids:
        traces = (
            db.query(CognitiveTraceDB)
            .filter(CognitiveTraceDB.session_id.in_(session_ids))
            .all()
        )
        data["traces"] = [
            {
                "id": t.id,
                "session_id": t.session_id,
                "student_id": t.student_id,
                "activity_id": t.activity_id,
                "trace_level": t.trace_level,
                "interaction_type": t.interaction_type,
                "cognitive_state": t.cognitive_state,
                "cognitive_intent": t.cognitive_intent,
                "ai_involvement": t.ai_involvement,
                "content": t.content,
                "response": t.response,
                "created_at": t.created_at,
                "trace_metadata": t.trace_metadata,
            }
            for t in traces
        ]

    # Fetch evaluations
    if request.include_evaluations and session_ids:
        evaluations = (
            db.query(EvaluationDB)
            .filter(EvaluationDB.session_id.in_(session_ids))
            .all()
        )
        data["evaluations"] = [
            {
                "id": e.id,
                "session_id": e.session_id,
                "student_id": e.student_id,
                "activity_id": e.activity_id,
                "overall_competency_level": e.overall_competency_level,
                "overall_score": e.overall_score,
                "dimensions": e.dimensions,
                "key_strengths": e.key_strengths,
                "improvement_areas": e.improvement_areas,
                "created_at": e.created_at,
            }
            for e in evaluations
        ]

    # Fetch risks
    if request.include_risks and session_ids:
        risks = (
            db.query(RiskDB).filter(RiskDB.session_id.in_(session_ids)).all()
        )
        data["risks"] = [
            {
                "id": r.id,
                "session_id": r.session_id,
                "student_id": r.student_id,
                "activity_id": r.activity_id,
                "risk_type": r.risk_type,
                "risk_level": r.risk_level,
                "dimension": r.dimension,
                "description": r.description,
                "evidence": r.evidence,
                "recommendations": r.recommendations,
                "resolved": r.resolved,
                "created_at": r.created_at,
            }
            for r in risks
        ]

    return data


@router.post("/research-data", response_model=ExportResponse)
async def export_research_data(
    request: ExportRequest,
    db: Session = Depends(get_db_session),
) -> ExportResponse:
    """
    Export anonymized research data with privacy guarantees

    This endpoint implements HU-ADM-005: Exportación de datos para investigación institucional

    **Privacy Safeguards**:
    - k-anonymity (configurable, default k=5)
    - ID hashing (irreversible pseudonymization)
    - PII suppression (emails, names removed)
    - Timestamp generalization (week level)
    - Optional differential privacy noise
    - GDPR Article 89 compliance

    **Use Cases**:
    - Educational research
    - Learning analytics
    - Institutional improvement
    - Academic publications

    **Example Request**:
    ```json
    {
        "start_date": "2025-01-01T00:00:00Z",
        "end_date": "2025-12-31T23:59:59Z",
        "activity_ids": ["prog2_tp1", "prog2_tp2"],
        "include_traces": true,
        "include_evaluations": true,
        "format": "json",
        "k_anonymity": 5
    }
    ```

    **Response**:
    - Returns export metadata and validation report
    - For large exports, provides download URL
    - For small exports (<10MB), includes data inline

    **Permissions**: Requires admin role (future implementation)
    """
    export_id = str(uuid.uuid4())[:8]

    logger.info(
        "Starting research data export",
        extra={
            "export_id": export_id,
            "format": request.format,
            "k_anonymity": request.k_anonymity,
            "start_date": request.start_date,
            "end_date": request.end_date,
        },
    )

    try:
        # Step 1: Fetch data from database
        raw_data = fetch_data_from_db(db, request)

        total_records = sum(len(v) for v in raw_data.values())
        if total_records == 0:
            raise HTTPException(
                status_code=404,
                detail="No data found matching the specified filters",
            )

        logger.info(
            "Data fetched from database",
            extra={"total_records": total_records, "data_types": list(raw_data.keys())},
        )

        # Step 2: Anonymize data
        anon_config = AnonymizationConfig(
            k_anonymity=request.k_anonymity,
            suppress_pii=True,
            generalize_timestamps=True,
            add_noise_to_scores=request.add_noise,
            noise_epsilon=request.noise_epsilon,
        )
        anonymizer = DataAnonymizer(anon_config)

        anonymized_data = {}
        for data_type, records in raw_data.items():
            if data_type == "traces":
                anonymized_data[data_type] = [
                    anonymizer.anonymize_trace(r) for r in records
                ]
            elif data_type == "evaluations":
                anonymized_data[data_type] = [
                    anonymizer.anonymize_evaluation(r) for r in records
                ]
            elif data_type == "risks":
                anonymized_data[data_type] = [
                    anonymizer.anonymize_risk(r) for r in records
                ]
            elif data_type == "sessions":
                anonymized_data[data_type] = [
                    anonymizer.anonymize_session(r) for r in records
                ]

        logger.info("Data anonymization completed")

        # Step 3: Validate privacy
        validator = PrivacyValidator(min_k=request.k_anonymity)

        # Validate all records together for k-anonymity
        all_records = []
        for records in anonymized_data.values():
            all_records.extend(records)

        # Quasi-identifiers: fields that combined could identify someone
        quasi_identifiers = ["activity_id", "week"]

        validation_result = validator.validate(all_records, quasi_identifiers)

        # Check GDPR compliance
        gdpr_result = GDPRCompliance.check_article_89_compliance(
            anonymization_config=anon_config.model_dump(),
            validation_result=validation_result,
        )

        # Combine validation results
        validation_result.metrics.update(gdpr_result.metrics)
        validation_result.is_valid &= gdpr_result.is_valid
        validation_result.errors.extend(gdpr_result.errors)

        if not validation_result.is_valid:
            logger.error(
                "Privacy validation failed",
                extra={
                    "errors": validation_result.errors,
                    "metrics": validation_result.metrics,
                },
            )
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Privacy validation failed",
                    "errors": validation_result.errors,
                    "metrics": validation_result.metrics,
                },
            )

        logger.info("Privacy validation passed", extra=validation_result.metrics)

        # Step 4: Export to requested format
        export_config = ExportConfig(
            format=request.format,
            compress=request.compress,
            include_metadata=True,
        )
        exporter = ResearchDataExporter(export_config)

        # Export (returns string or bytes depending on format)
        exported_data = exporter.export(anonymized_data)

        # Calculate file size
        if isinstance(exported_data, str):
            file_size = len(exported_data.encode("utf-8"))
        else:
            file_size = len(exported_data)

        logger.info(
            "Export completed successfully",
            extra={
                "export_id": export_id,
                "format": request.format,
                "file_size_bytes": file_size,
                "total_records": total_records,
            },
        )

        # Build response
        metadata = ExportMetadata(
            export_timestamp=datetime.utcnow(),
            export_format=request.format,
            total_records=total_records,
            data_types=list(anonymized_data.keys()),
            anonymization_applied=True,
            privacy_standard="k-anonymity",
            date_range={
                "start": request.start_date,
                "end": request.end_date,
            }
            if request.start_date or request.end_date
            else None,
        )

        privacy_metrics = PrivacyMetrics(**validation_result.metrics)

        validation_report = ValidationReport(
            is_valid=validation_result.is_valid,
            errors=validation_result.errors,
            warnings=validation_result.warnings,
            metrics=privacy_metrics,
            gdpr_article_89_compliant=validation_result.metrics.get(
                "gdpr_article_89_compliance", False
            ),
        )

        # For now, return data inline (future: upload to S3 and provide download URL)
        # TODO: For production, save to file storage and provide download URL
        download_url = None  # f"/api/v1/export/download/{export_id}"

        return ExportResponse(
            success=True,
            message=f"Export completed successfully. {total_records} records anonymized with k={request.k_anonymity}.",
            metadata=metadata,
            validation_report=validation_report,
            download_url=download_url,
            file_size_bytes=file_size,
            export_id=export_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Export failed with exception",
            exc_info=True,
            extra={"export_id": export_id},
        )
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {str(e)}",
        )
