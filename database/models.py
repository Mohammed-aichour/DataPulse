"""
DataPulse Relational Models
Defines normalized entities: Student, Course, AcademicRecord,
PipelineExecution, PredictionLog, and DataImport.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, Text, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from database.connection import Base


def utc_now():
    return datetime.now(timezone.utc)


class StudentModel(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(32), unique=True, index=True, nullable=False)
    school = Column(String(16), nullable=False)  # GP or MS
    sex = Column(String(8), nullable=False)     # F or M
    age = Column(Integer, nullable=False)
    address = Column(String(8), nullable=False) # U or R
    famsize = Column(String(8), nullable=False) # LE3 or GT3
    pstatus = Column(String(8), nullable=False) # T or A
    medu = Column(Integer, nullable=False)      # Mother's education (0-4)
    fedu = Column(Integer, nullable=False)      # Father's education (0-4)
    mjob = Column(String(32), nullable=False)   # teacher, health, services, at_home, other
    fjob = Column(String(32), nullable=False)   # teacher, health, services, at_home, other
    reason = Column(String(32), nullable=False) # home, reputation, course, other
    guardian = Column(String(16), nullable=False) # mother, father, other
    nursery = Column(String(8), nullable=False) # yes/no
    internet = Column(String(8), nullable=False)# yes/no
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    records = relationship("AcademicRecordModel", back_populates="student", cascade="all, delete-orphan")


class CourseModel(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_code = Column(String(16), unique=True, index=True, nullable=False) # MAT, POR
    course_name = Column(String(64), nullable=False)
    department = Column(String(128), nullable=True)
    credits = Column(Integer, default=6)
    semester = Column(String(64), default="Full Academic Year")

    # Relationships
    records = relationship("AcademicRecordModel", back_populates="course")


class AcademicRecordModel(Base):
    __tablename__ = "academic_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    record_id = Column(String(32), unique=True, index=True, nullable=False)
    student_id = Column(String(32), ForeignKey("students.student_id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    course_code = Column(String(16), nullable=False)

    # Behavioral & context attributes
    traveltime = Column(Integer, nullable=False)
    studytime = Column(Integer, nullable=False)
    failures = Column(Integer, nullable=False)
    schoolsup = Column(String(8), nullable=False)
    famsup = Column(String(8), nullable=False)
    paid = Column(String(8), nullable=False)
    activities = Column(String(8), nullable=False)
    higher = Column(String(8), nullable=False)
    romantic = Column(String(8), nullable=False)
    famrel = Column(Integer, nullable=False)
    freetime = Column(Integer, nullable=False)
    goout = Column(Integer, nullable=False)
    dalc = Column(Integer, nullable=False)
    walc = Column(Integer, nullable=False)
    health = Column(Integer, nullable=False)
    absences = Column(Integer, nullable=False)

    # Grades
    g1 = Column(Integer, nullable=False)
    g2 = Column(Integer, nullable=False)
    g3 = Column(Integer, nullable=False)

    # Engineered metrics
    parent_edu_avg = Column(Float, nullable=False)
    alcohol_index = Column(Float, nullable=False)
    study_to_social_ratio = Column(Float, nullable=False)
    grade_delta = Column(Integer, nullable=False)
    academic_risk = Column(Integer, nullable=False, index=True) # 1 if at risk, 0 otherwise
    passing_status = Column(Boolean, nullable=False)
    performance_tier = Column(String(32), nullable=False)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    student = relationship("StudentModel", back_populates="records")
    course = relationship("CourseModel", back_populates="records")

    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_student_course"),
        Index("idx_student_course", "student_id", "course_id"),
    )


class PipelineExecutionModel(Base):
    __tablename__ = "pipeline_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_timestamp = Column(DateTime, default=utc_now, nullable=False)
    records_processed = Column(Integer, nullable=False)
    duration_seconds = Column(Float, nullable=False)
    status = Column(String(32), nullable=False) # SUCCESS, FAILED, WARNING
    quality_score = Column(Float, nullable=False)
    details_json = Column(Text, nullable=True)


class PredictionLogModel(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=utc_now, nullable=False)
    course = Column(String(16), nullable=False)
    features_json = Column(Text, nullable=False)
    predicted_grade = Column(Float, nullable=False)
    predicted_risk = Column(Integer, nullable=False)
    risk_probability = Column(Float, nullable=False)
    model_name = Column(String(64), nullable=False)
    model_version = Column(String(32), default="v1.0")


class DataImportModel(Base):
    __tablename__ = "data_imports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_name = Column(String(128), nullable=False)
    file_name = Column(String(128), nullable=False)
    row_count = Column(Integer, nullable=False)
    checksum = Column(String(128), nullable=False)
    imported_at = Column(DateTime, default=utc_now, nullable=False)
    is_synthetic = Column(Boolean, default=False)
    status = Column(String(32), default="IMPORTED")
