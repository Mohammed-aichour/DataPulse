"""
DataPulse API Pydantic Schemas
Defines request and response data contracts for all API endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# Health & Info
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    database: str
    ml_models: str
    version: str


class InfoResponse(BaseModel):
    project_name: str
    version: str
    institution: str
    author_role: str
    dataset_source: str
    total_records: int
    unique_students: int


# Analytics Schemas
class OverviewKPIs(BaseModel):
    total_students: int
    total_enrollments: int
    avg_final_grade: float
    pass_rate_pct: float
    risk_count: int
    risk_rate_pct: float
    avg_absences: float
    data_quality_score: float
    courses_count: int
    last_pipeline_run: Optional[str]


class CoursePerformance(BaseModel):
    course_code: str
    course_name: str
    department: Optional[str]
    enrollments: int
    avg_g1: float
    avg_g2: float
    avg_g3: float
    avg_absences: float
    avg_studytime: float
    avg_failures: float
    pass_rate_pct: float


class GradeDistributionBin(BaseModel):
    grade_range: str
    period_1: int
    period_2: int
    final_g3: int


class FactorPerformance(BaseModel):
    factor_group: str
    student_count: int
    avg_grade: float
    pass_rate_pct: float
    risk_rate_pct: float


class CorrelationItem(BaseModel):
    feature: str
    label: str
    correlation: float
    impact: str
    magnitude: str


# Student Schemas
class StudentRecordSummary(BaseModel):
    record_id: str
    course_code: str
    g1: int
    g2: int
    g3: int
    studytime: int
    failures: int
    absences: int
    academic_risk: int
    passing_status: bool
    performance_tier: str


class StudentDetail(BaseModel):
    id: int
    student_id: str
    school: str
    sex: str
    age: int
    address: str
    famsize: str
    pstatus: str
    medu: int
    fedu: int
    mjob: str
    fjob: str
    reason: str
    guardian: str
    nursery: str
    internet: str
    enrollments: List[StudentRecordSummary]


class StudentListItem(BaseModel):
    id: int
    student_id: str
    school: str
    sex: str
    age: int
    address: str
    courses: List[str]
    final_grades: Dict[str, int]
    is_at_risk: bool
    performance_tier: str


class PaginatedStudents(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[StudentListItem]


# ML Schemas
class PredictionRequest(BaseModel):
    course_code: str = "MAT"
    school: str = "GP"
    sex: str = "F"
    age: int = Field(default=17, ge=15, le=22)
    address: str = "U"
    famsize: str = "GT3"
    Pstatus: str = "T"
    Medu: int = Field(default=3, ge=0, le=4)
    Fedu: int = Field(default=3, ge=0, le=4)
    Mjob: str = "services"
    Fjob: str = "services"
    reason: str = "course"
    guardian: str = "mother"
    traveltime: int = Field(default=1, ge=1, le=4)
    studytime: int = Field(default=2, ge=1, le=4)
    failures: int = Field(default=0, ge=0, le=4)
    schoolsup: str = "no"
    famsup: str = "yes"
    paid: str = "no"
    activities: str = "yes"
    nursery: str = "yes"
    higher: str = "yes"
    internet: str = "yes"
    romantic: str = "no"
    famrel: int = Field(default=4, ge=1, le=5)
    freetime: int = Field(default=3, ge=1, le=5)
    goout: int = Field(default=3, ge=1, le=5)
    Dalc: int = Field(default=1, ge=1, le=5)
    Walc: int = Field(default=1, ge=1, le=5)
    health: int = Field(default=4, ge=1, le=5)
    absences: int = Field(default=2, ge=0, le=93)
    G1: Optional[int] = Field(default=None, ge=0, le=20, description="Period 1 Grade (optional for Scenario A)")
    G2: Optional[int] = Field(default=None, ge=0, le=20, description="Period 2 Grade (optional for Scenarios A & B)")
    scenario: Optional[str] = Field(default="auto", description="Scenario: auto, early, midterm, latestage")


class PredictionResponse(BaseModel):
    predicted_grade_g3: float
    is_at_risk: bool
    risk_probability: float
    risk_tier: str
    confidence_pct: float
    recommendation: str
    contributing_factors: List[str]
    scenario_used: Dict[str, str]
    model_used: Dict[str, str]
    timestamp: str


# Pipeline Schemas
class PipelineRunResponse(BaseModel):
    status: str
    duration_seconds: float
    records_processed: int
    quality_score: float
    details: Dict[str, Any]
