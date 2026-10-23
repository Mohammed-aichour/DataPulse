"""
Data Pipeline Orchestration & Execution Endpoints
"""

from typing import Any, Dict, List
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from backend.app.schemas.schemas import PipelineRunResponse
from database.connection import get_db
from database.models import (
    AcademicRecordModel, CourseModel, DataImportModel,
    PipelineExecutionModel, StudentModel
)
from src.pipeline.run import run_pipeline

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


@router.post("/run", response_model=PipelineRunResponse)
def trigger_pipeline():
    """Executes the master ETL & ML training pipeline synchronously."""
    result = run_pipeline()
    return PipelineRunResponse(
        status=result["status"],
        duration_seconds=result["duration_seconds"],
        records_processed=result["records_processed"],
        quality_score=result["quality_score"],
        details=result["details"]
    )


@router.get("/status")
def get_pipeline_status(db: Session = Depends(get_db)):
    latest_run = (
        db.query(PipelineExecutionModel)
        .order_by(PipelineExecutionModel.run_timestamp.desc())
        .first()
    )

    total_students = db.query(StudentModel).count()
    total_records = db.query(AcademicRecordModel).count()
    total_courses = db.query(CourseModel).count()
    imports = db.query(DataImportModel).all()

    return {
        "is_operational": True,
        "latest_run": {
            "id": latest_run.id if latest_run else None,
            "timestamp": latest_run.run_timestamp.isoformat() if latest_run else None,
            "status": latest_run.status if latest_run else "NEVER_RUN",
            "duration_seconds": latest_run.duration_seconds if latest_run else 0.0,
            "quality_score": latest_run.quality_score if latest_run else 100.0,
        },
        "database_counts": {
            "students": total_students,
            "academic_records": total_records,
            "courses": total_courses,
            "data_imports": len(imports)
        }
    }


@router.get("/history")
def get_pipeline_history(db: Session = Depends(get_db)):
    runs = (
        db.query(PipelineExecutionModel)
        .order_by(PipelineExecutionModel.run_timestamp.desc())
        .limit(20)
        .all()
    )

    return [
        {
            "id": r.id,
            "timestamp": r.run_timestamp.isoformat(),
            "status": r.status,
            "duration_seconds": r.duration_seconds,
            "records_processed": r.records_processed,
            "quality_score": r.quality_score,
            "details": r.details_json
        }
        for r in runs
    ]
