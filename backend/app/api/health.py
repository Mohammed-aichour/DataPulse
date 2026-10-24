"""
Health & System Information Endpoints
Sanitizes error responses to avoid leaking database hosts, usernames, or internal topologies.
"""

from datetime import datetime, timezone
import logging
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.schemas.schemas import HealthResponse, InfoResponse
from database.connection import get_db
from database.models import AcademicRecordModel, StudentModel
from src.ml.predictor import PredictorService

logger = logging.getLogger("datapulse.health")
router = APIRouter(tags=["System"])


@router.get("/health", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)):
    db_status = "HEALTHY"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"[HealthCheck] Database connection error: {e}")
        # Return sanitized non-leaking error status
        db_status = f"UNHEALTHY: {type(e).__name__}"

    predictor = PredictorService()
    ml_status = "READY" if predictor.is_ready() else "NOT_TRAINED"

    return HealthResponse(
        status="UP" if "HEALTHY" in db_status else "DEGRADED",
        timestamp=datetime.now(timezone.utc).isoformat(),
        database=db_status,
        ml_models=ml_status,
        version=settings.VERSION
    )


@router.get("/info", response_model=InfoResponse)
def get_info(db: Session = Depends(get_db)):
    students_count = db.query(StudentModel).count()
    records_count = db.query(AcademicRecordModel).count()

    return InfoResponse(
        project_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        institution=settings.INSTITUTION,
        author_role="Computer Engineering Student (UIA Agadir)",
        dataset_source="UCI Machine Learning Repository (Student Performance, ID: 320)",
        total_records=records_count,
        unique_students=students_count
    )
