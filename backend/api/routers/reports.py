"""
Institutional Reports API Endpoints - SPRINT 5 HU-DOC-009

Endpoints:
- POST /reports/cohort - Generate cohort summary report
- POST /reports/risk-dashboard - Generate risk dashboard
- GET /reports/{report_id} - Get report by ID
- GET /reports/{report_id}/download - Download report file
- GET /reports/teacher/{teacher_id} - Get reports by teacher
"""

import logging
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..deps import get_db
from ...database.repositories import CourseReportRepository
from ...services.course_report_generator import CourseReportGenerator
from ..schemas.common import APIResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Institutional Reports"])


# =============================================================================
# REQUEST/RESPONSE SCHEMAS
# =============================================================================


class CohortReportRequest(BaseModel):
    """Request to generate cohort summary report"""

    course_id: str = Field(description="Course identifier (e.g., PROG2_2025_1C)")
    teacher_id: str = Field(description="Teacher generating the report")
    student_ids: List[str] = Field(description="List of student IDs in cohort")
    period_start: datetime = Field(description="Start of reporting period")
    period_end: datetime = Field(description="End of reporting period")
    export_format: str = Field(default="json", description="Export format (json, pdf, xlsx)")


class RiskDashboardRequest(BaseModel):
    """Request to generate risk dashboard"""

    course_id: str = Field(description="Course identifier")
    teacher_id: str = Field(description="Teacher generating the report")
    student_ids: List[str] = Field(description="List of student IDs")
    period_start: datetime = Field(description="Start of period")
    period_end: datetime = Field(description="End of period")


class ReportResponse(BaseModel):
    """Response with report summary"""

    report_id: str
    course_id: str
    teacher_id: str
    report_type: str
    period_start: str
    period_end: str
    generated_at: str
    summary_stats: dict
    at_risk_students: List[str]


# =============================================================================
# ENDPOINTS
# =============================================================================


@router.post(
    "/cohort",
    response_model=APIResponse[dict],
    summary="Generate cohort summary report",
    description="Generate aggregate report for a cohort of students",
    status_code=status.HTTP_201_CREATED,
)
async def generate_cohort_report(
    request: CohortReportRequest,
    db: Session = Depends(get_db),
) -> APIResponse[dict]:
    """
    Generate cohort summary report

    Aggregates data from multiple students to provide institutional insights.
    """
    if not request.student_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="student_ids cannot be empty",
        )

    if request.period_end <= request.period_start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="period_end must be after period_start",
        )

    try:
        generator = CourseReportGenerator(db)
        report_data = generator.generate_cohort_summary(
            course_id=request.course_id,
            teacher_id=request.teacher_id,
            student_ids=request.student_ids,
            period_start=request.period_start,
            period_end=request.period_end,
            export_format=request.export_format,
        )

        logger.info(
            "Cohort report generated",
            extra={
                "report_id": report_data["report_id"],
                "course_id": request.course_id,
                "student_count": len(request.student_ids),
            },
        )

        return APIResponse(
            success=True,
            data=report_data,
            message=f"Cohort report generated for {len(request.student_ids)} students",
        )

    except Exception as e:
        logger.error(
            "Error generating cohort report",
            exc_info=True,
            extra={"course_id": request.course_id, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating report: {str(e)}",
        )


@router.post(
    "/risk-dashboard",
    response_model=APIResponse[dict],
    summary="Generate risk dashboard",
    description="Generate risk-focused dashboard for proactive intervention",
    status_code=status.HTTP_201_CREATED,
)
async def generate_risk_dashboard(
    request: RiskDashboardRequest,
    db: Session = Depends(get_db),
) -> APIResponse[dict]:
    """
    Generate risk dashboard

    Provides detailed risk analysis for a cohort.
    """
    if not request.student_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="student_ids cannot be empty",
        )

    try:
        generator = CourseReportGenerator(db)
        dashboard_data = generator.generate_risk_dashboard(
            course_id=request.course_id,
            teacher_id=request.teacher_id,
            student_ids=request.student_ids,
            period_start=request.period_start,
            period_end=request.period_end,
        )

        logger.info(
            "Risk dashboard generated",
            extra={
                "report_id": dashboard_data["report_id"],
                "course_id": request.course_id,
                "critical_students": len(dashboard_data["critical_students"]),
            },
        )

        return APIResponse(
            success=True,
            data=dashboard_data,
            message=f"Risk dashboard generated for {len(request.student_ids)} students",
        )

    except Exception as e:
        logger.error(
            "Error generating risk dashboard",
            exc_info=True,
            extra={"course_id": request.course_id, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating dashboard: {str(e)}",
        )


@router.get(
    "/{report_id}",
    response_model=APIResponse[dict],
    summary="Get report by ID",
    description="Retrieve a previously generated report",
)
async def get_report(
    report_id: str,
    db: Session = Depends(get_db),
) -> APIResponse[dict]:
    """
    Get report by ID

    Returns complete report data.
    """
    report_repo = CourseReportRepository(db)
    report = report_repo.get_by_id(report_id)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{report_id}' not found",
        )

    report_data = {
        "report_id": report.id,
        "course_id": report.course_id,
        "teacher_id": report.teacher_id,
        "report_type": report.report_type,
        "period_start": report.period_start.isoformat(),
        "period_end": report.period_end.isoformat(),
        "generated_at": report.created_at.isoformat(),
        "summary_stats": report.summary_stats,
        "competency_distribution": report.competency_distribution,
        "risk_distribution": report.risk_distribution,
        "top_risks": report.top_risks,
        "student_summaries": report.student_summaries,
        "institutional_recommendations": report.institutional_recommendations,
        "at_risk_students": report.at_risk_students,
        "format": report.format,
        "file_path": report.file_path,
        "exported_at": report.exported_at.isoformat() if report.exported_at else None,
    }

    logger.info("Report retrieved", extra={"report_id": report_id})

    return APIResponse(
        success=True,
        data=report_data,
        message="Report retrieved successfully",
    )


@router.get(
    "/{report_id}/download",
    summary="Download report file",
    description="Download exported report file (JSON, PDF, XLSX)",
)
async def download_report(
    report_id: str,
    db: Session = Depends(get_db),
) -> FileResponse:
    """
    Download report file

    Returns the exported file if available.
    """
    report_repo = CourseReportRepository(db)
    report = report_repo.get_by_id(report_id)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{report_id}' not found",
        )

    # If not yet exported, export now
    if not report.file_path:
        generator = CourseReportGenerator(db, report_repo)
        output_dir = Path("reports")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"report_{report_id}.json"

        file_path = generator.export_report_to_json(report_id, str(output_path))
    else:
        file_path = report.file_path

    # Validate file exists
    if not Path(file_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report file not found: {file_path}",
        )

    logger.info(
        "Report downloaded",
        extra={"report_id": report_id, "file_path": file_path},
    )

    # Determine media type
    media_type = "application/json"
    if file_path.endswith(".pdf"):
        media_type = "application/pdf"
    elif file_path.endswith(".xlsx"):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=Path(file_path).name,
    )


@router.get(
    "/teacher/{teacher_id}",
    response_model=APIResponse[List[dict]],
    summary="Get reports by teacher",
    description="Get all reports generated by a teacher",
)
async def get_teacher_reports(
    teacher_id: str,
    limit: int = 20,
    db: Session = Depends(get_db),
) -> APIResponse[List[dict]]:
    """
    Get reports by teacher

    Returns list of reports ordered by creation date.
    """
    report_repo = CourseReportRepository(db)
    reports = report_repo.get_by_teacher(teacher_id, limit=limit)

    reports_data = [
        {
            "report_id": r.id,
            "course_id": r.course_id,
            "report_type": r.report_type,
            "period_start": r.period_start.isoformat(),
            "period_end": r.period_end.isoformat(),
            "generated_at": r.created_at.isoformat(),
            "format": r.format,
            "exported": r.exported_at is not None,
        }
        for r in reports
    ]

    logger.info(
        "Teacher reports retrieved",
        extra={"teacher_id": teacher_id, "count": len(reports_data)},
    )

    return APIResponse(
        success=True,
        data=reports_data,
        message=f"Retrieved {len(reports_data)} reports",
    )
