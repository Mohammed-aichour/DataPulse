"""
Educational Analytics API Endpoints
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from DataPulse.backend.app.schemas.schemas import (
    CorrelationItem, CoursePerformance, FactorPerformance,
    GradeDistributionBin, OverviewKPIs
)
from DataPulse.database.connection import get_db
from DataPulse.src.analytics.metrics import CampusAnalyticsEngine

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=OverviewKPIs)
def get_overview(db: Session = Depends(get_db)):
    engine = CampusAnalyticsEngine(db)
    return engine.get_overview_kpis()


@router.get("/courses", response_model=List[CoursePerformance])
def get_courses(db: Session = Depends(get_db)):
    engine = CampusAnalyticsEngine(db)
    return engine.get_course_performance()


@router.get("/distribution", response_model=List[GradeDistributionBin])
def get_grade_distribution(db: Session = Depends(get_db)):
    engine = CampusAnalyticsEngine(db)
    return engine.get_grade_distribution()


@router.get("/performance", response_model=List[FactorPerformance])
def get_performance_by_factor(
    factor: str = Query("studytime", description="Factor to group by: studytime, failures, parent_edu, school, sex, internet"),
    db: Session = Depends(get_db)
):
    engine = CampusAnalyticsEngine(db)
    return engine.get_performance_by_factor(factor)


@router.get("/correlations", response_model=List[CorrelationItem])
def get_correlations(db: Session = Depends(get_db)):
    engine = CampusAnalyticsEngine(db)
    return engine.get_correlations()


@router.get("/data-quality")
def get_data_quality(db: Session = Depends(get_db)):
    engine = CampusAnalyticsEngine(db)
    return engine.get_data_quality_summary()
