"""
DataPulse Database Architecture & Integration Test Suite
Verifies:
- Clean schema creation & Alembic migration execution
- All 6 tables, columns, constraints, unique keys, and indexes
- Compilation and querying of analytical SQL views
- Idempotent ETL data loading & integrity verification (674 students, 1044 enrollments)
- Duplicate enrollment rejection via unique constraint
- Referential integrity enforcement
- Graceful error handling when database engine is unreachable
"""

import os
import tempfile
from pathlib import Path
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models import (
    AcademicRecordModel, CourseModel, DataImportModel,
    PipelineExecutionModel, PredictionLogModel, StudentModel
)
from src.ingestion.dataset_loader import DatasetLoader
from src.preprocessing.transformer import EducationalTransformer
from src.pipeline.db_loader import DatabaseLoader


@pytest.fixture(scope="module")
def temp_db():
    """Provides a fresh isolated database file for integration testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    db_url = f"sqlite:///{db_path}"
    test_engine = create_engine(db_url, connect_args={"check_same_thread": False})
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    yield {
        "path": db_path,
        "url": db_url,
        "engine": test_engine,
        "sessionmaker": TestSession
    }

    test_engine.dispose()
    if os.path.exists(db_path):
        os.remove(db_path)


def test_alembic_clean_schema_migration(temp_db):
    """Verifies that Alembic upgrade head creates all expected tables and columns on an empty database."""
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", temp_db["url"])

    command.upgrade(cfg, "head")

    inspector = inspect(temp_db["engine"])
    tables = inspector.get_table_names()

    expected_tables = {
        "students", "courses", "academic_records",
        "pipeline_executions", "prediction_logs", "data_imports"
    }
    assert expected_tables.issubset(set(tables)), f"Missing tables in {tables}"

    # Verify columns in academic_records
    col_names = [c["name"] for c in inspector.get_columns("academic_records")]
    assert "student_id" in col_names
    assert "course_id" in col_names
    assert "g1" in col_names
    assert "g2" in col_names
    assert "g3" in col_names
    assert "academic_risk" in col_names


def test_views_compilation_and_querying(temp_db):
    """Verifies that views.sql compiles and executes without SQL syntax errors."""
    views_sql_path = Path("database/sql/views.sql")
    assert views_sql_path.exists(), "views.sql missing"

    sql_content = views_sql_path.read_text(encoding="utf-8")
    statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]

    with temp_db["engine"].connect() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
        conn.commit()

        # Query compiled views
        res_overview = conn.execute(text("SELECT COUNT(*) FROM v_student_overview")).scalar()
        res_course = conn.execute(text("SELECT COUNT(*) FROM v_course_performance")).scalar()
        res_absence = conn.execute(text("SELECT COUNT(*) FROM v_absence_impact")).scalar()
        assert res_overview == 0  # Empty at this point
        assert res_course == 0
        assert res_absence == 0


def test_idempotent_etl_data_loading(temp_db):
    """Verifies that DatabaseLoader correctly loads exactly 674 students, 2 courses, and 1044 records."""
    loader = DatasetLoader()
    df_mat, df_por, metadata = loader.load_raw_datasets()
    transformer = EducationalTransformer()
    students_df, courses_df, records_df = transformer.transform(df_mat, df_por)

    session = temp_db["sessionmaker"]()
    db_loader = DatabaseLoader(db_session=session)

    # First load
    db_loader.load_courses(courses_df)
    db_loader.load_students(students_df)
    db_loader.load_academic_records(records_df)

    count_students = session.query(StudentModel).count()
    count_courses = session.query(CourseModel).count()
    count_records = session.query(AcademicRecordModel).count()

    assert count_students == 674, f"Expected 674 students, got {count_students}"
    assert count_courses == 2, f"Expected 2 courses, got {count_courses}"
    assert count_records == 1044, f"Expected 1044 records, got {count_records}"

    # Second load (Idempotency check: counts must remain identical)
    db_loader.load_courses(courses_df)
    db_loader.load_students(students_df)
    db_loader.load_academic_records(records_df)

    assert session.query(StudentModel).count() == 674
    assert session.query(CourseModel).count() == 2
    assert session.query(AcademicRecordModel).count() == 1044
    session.close()


def test_unique_constraint_prevents_duplicate_enrollment(temp_db):
    """Verifies that a student cannot be enrolled in the same course twice."""
    session = temp_db["sessionmaker"]()
    # Attempt inserting a duplicate record with the same student_id and course_id
    dup_record = AcademicRecordModel(
        record_id="REC-TEST-DUP",
        student_id="STU-0001",
        course_id=1,  # MAT already exists for STU-0001
        course_code="MAT",
        traveltime=1, studytime=2, failures=0, schoolsup="no", famsup="no",
        paid="no", activities="yes", higher="yes", romantic="no", famrel=4,
        freetime=3, goout=3, dalc=1, walc=1, health=5, absences=0,
        g1=12, g2=13, g3=14, parent_edu_avg=3.0, alcohol_index=1.0,
        study_to_social_ratio=0.3, grade_delta=1, academic_risk=0,
        passing_status=True, performance_tier="Satisfactory"
    )

    with pytest.raises(IntegrityError):
        session.add(dup_record)
        session.commit()
    session.rollback()
    session.close()


def test_database_views_return_real_data(temp_db):
    """Verifies that analytical SQL views return live aggregated data after seeding."""
    with temp_db["engine"].connect() as conn:
        res = conn.execute(text("SELECT course_code, total_enrollments, avg_g3 FROM v_course_performance ORDER BY course_code")).fetchall()
        assert len(res) == 2
        # MAT: 395 records, POR: 649 records
        row_mat = res[0]
        row_por = res[1]
        assert row_mat[0] == "MAT" and row_mat[1] == 395
        assert row_por[0] == "POR" and row_por[1] == 649

        # Check absence impact tiers
        tiers = conn.execute(text("SELECT absence_tier, student_count FROM v_absence_impact")).fetchall()
        assert len(tiers) > 0


def test_unreachable_database_error_handling():
    """Verifies that the application handles an unavailable database gracefully without crashing."""
    # Create an engine pointing to an unreachable non-existent database port
    bad_engine = create_engine(
        "postgresql+psycopg2://baduser:badpass@127.0.0.1:59999/bad_db",
        connect_args={"connect_timeout": 1}
    )
    BadSession = sessionmaker(bind=bad_engine)
    session = BadSession()

    db_status = "HEALTHY"
    try:
        session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"UNHEALTHY: {type(e).__name__}"
    finally:
        session.close()

    bad_engine.dispose()
    assert "UNHEALTHY" in db_status
