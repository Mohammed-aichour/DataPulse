"""
DataPulse Dedicated PostgreSQL Integration Test Suite
Explicitly targets a live PostgreSQL 16 database via TEST_DATABASE_URL.

IMPORTANT INTEGRITY RULE:
Never silently runs against SQLite. If TEST_DATABASE_URL is unset or the PostgreSQL
server is unavailable, this entire module is explicitly SKIPPED with a descriptive notice.

PRODUCTION SAFEGUARD:
Automatically inspects the target database name to prevent destructive operations
on production databases (blocks execution if database name contains 'prod', 'live', 'master',
or cannot be confidently identified as a dedicated test database).

Usage:
    export TEST_DATABASE_URL="postgresql+psycopg2://datapulse_user:YOUR_SECRET@127.0.0.1:5432/datapulse_test"
    pytest -v tests/test_postgres_integration.py
"""

import os
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import sessionmaker

# Explicitly load .env from project root if available
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

from database.models import (
    AcademicRecordModel, CourseModel, StudentModel
)
from src.ingestion.dataset_loader import DatasetLoader
from src.preprocessing.transformer import EducationalTransformer
from src.pipeline.db_loader import DatabaseLoader

# Inspect TEST_DATABASE_URL
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL or ("postgres" not in TEST_DATABASE_URL.lower()):
    pytest.skip(
        "PostgreSQL integration tests SKIPPED: TEST_DATABASE_URL is not set or not a PostgreSQL connection URI. "
        "To enable, configure TEST_DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/datapulse_test in .env",
        allow_module_level=True
    )

# Normalize URL
PG_URL = TEST_DATABASE_URL
if PG_URL.startswith("postgres://"):
    PG_URL = PG_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif PG_URL.startswith("postgresql://") and not PG_URL.startswith("postgresql+"):
    PG_URL = PG_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Task 5 Safeguard: Parse and validate target server & database name
parsed = urlparse(PG_URL)
db_name = parsed.path.lstrip("/").split("?")[0].lower() if parsed.path else ""
PROD_KEYWORDS = ["prod", "production", "live", "master"]
is_prod_named = any(keyword in db_name for keyword in PROD_KEYWORDS)
allow_unsafe = os.getenv("ALLOW_UNSAFE_TEST_DB", "false").lower() in ("true", "1", "yes")

# Refuse to run if targeted at production
if is_prod_named and not allow_unsafe:
    pytest.fail(
        f"SAFETY HALT: TEST_DATABASE_URL targets a database with production keyword (dbname='{db_name}')! "
        "PostgreSQL integration tests execute DDL migrations and load test datasets. "
        "Point TEST_DATABASE_URL to a dedicated test/staging database (e.g., 'datapulse_test'). "
        "Set ALLOW_UNSAFE_TEST_DB=true only if you have verified this is an isolated test environment."
    )

# Require test identification if default database name is used (e.g. 'postgres')
is_explicit_test_db = any(term in db_name for term in ["test", "dev", "stage", "staging", "sandbox"])
if not is_explicit_test_db and not allow_unsafe:
    pytest.fail(
        f"SAFETY HALT: Target database name is '{db_name}', which cannot be confidently identified as a test database. "
        "To protect application data, TEST_DATABASE_URL must target an explicitly identified test database "
        "(e.g., 'datapulse_test' or a database name containing 'test', 'dev', or 'sandbox'). "
        "Set ALLOW_UNSAFE_TEST_DB=true only if you have verified this database is dedicated exclusively to test executions."
    )

# Safeguard against colliding with main application DATABASE_URL
app_db_url = os.getenv("DATABASE_URL", "").lower()
if app_db_url and app_db_url == PG_URL.lower() and not is_explicit_test_db and not allow_unsafe:
    pytest.fail(
        f"SAFETY HALT: TEST_DATABASE_URL is identical to DATABASE_URL and does not contain 'test'! "
        "To protect development/application data from test operations, "
        "use a separate test database in TEST_DATABASE_URL (e.g., 'datapulse_test')."
    )

# Liveness probe to avoid hanging if server is down
try:
    _probe_engine = create_engine(PG_URL, connect_args={"connect_timeout": 3})
    with _probe_engine.connect() as _probe_conn:
        _version = _probe_conn.execute(text("SELECT version()")).scalar()
    _probe_engine.dispose()
except (OperationalError, Exception) as exc:
    pytest.skip(
        f"PostgreSQL integration tests SKIPPED: Server at {parsed.hostname or 'host'} is unreachable: {exc}",
        allow_module_level=True
    )


@pytest.fixture(scope="module")
def pg_engine():
    """Provides an active PostgreSQL SQLAlchemy engine for the test module."""
    engine = create_engine(
        PG_URL,
        pool_pre_ping=True,
        echo=False
    )
    yield engine
    engine.dispose()


@pytest.fixture(scope="module")
def pg_session(pg_engine):
    """Provides a transactional session on PostgreSQL."""
    Session = sessionmaker(autocommit=False, autoflush=False, bind=pg_engine)
    session = Session()
    yield session
    session.close()


@pytest.mark.postgres
def test_postgres_live_connection_and_dialect(pg_engine):
    """Verifies that the target engine is genuinely PostgreSQL."""
    assert pg_engine.dialect.name == "postgresql", f"Expected postgresql dialect, got {pg_engine.dialect.name}"
    with pg_engine.connect() as conn:
        version_str = conn.execute(text("SELECT version()")).scalar()
        assert "PostgreSQL" in version_str, f"Unexpected version string: {version_str}"
        print(f"\n[PostgreSQL Live Probe] Connected to: {version_str[:60]}...")


@pytest.mark.postgres
def test_postgres_alembic_migrations(pg_engine):
    """Verifies that Alembic upgrade head runs cleanly on PostgreSQL creating all 6 tables."""
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", PG_URL)

    # Run upgrade head
    command.upgrade(cfg, "head")

    inspector = inspect(pg_engine)
    tables = inspector.get_table_names()

    expected_tables = {
        "students", "courses", "academic_records",
        "pipeline_executions", "prediction_logs", "data_imports"
    }
    assert expected_tables.issubset(set(tables)), f"Missing PostgreSQL tables in {tables}"

    # Verify native PostgreSQL column types
    columns = {c["name"]: str(c["type"]) for c in inspector.get_columns("academic_records")}
    assert "passing_status" in columns
    assert "BOOLEAN" in columns["passing_status"].upper()


@pytest.mark.postgres
def test_postgres_views_compilation(pg_engine):
    """Verifies that views.sql compiles cleanly with PostgreSQL syntax (CREATE OR REPLACE VIEW)."""
    views_sql_path = Path("database/sql/views.sql")
    assert views_sql_path.exists(), "views.sql missing"

    sql_content = views_sql_path.read_text(encoding="utf-8")
    statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]

    with pg_engine.connect() as conn:
        for stmt in statements:
            # PostgreSQL requires CREATE OR REPLACE VIEW instead of CREATE VIEW IF NOT EXISTS
            pg_stmt = stmt.replace("CREATE VIEW IF NOT EXISTS", "CREATE OR REPLACE VIEW")
            conn.execute(text(pg_stmt))
        conn.commit()

        # Query all compiled analytical views
        res_overview = conn.execute(text("SELECT COUNT(*) FROM v_student_overview")).scalar()
        res_course = conn.execute(text("SELECT COUNT(*) FROM v_course_performance")).scalar()
        res_risk = conn.execute(text("SELECT COUNT(*) FROM v_risk_analysis")).scalar()
        res_absence = conn.execute(text("SELECT COUNT(*) FROM v_absence_impact")).scalar()
        res_tier = conn.execute(text("SELECT COUNT(*) FROM v_performance_distribution")).scalar()
        assert res_overview is not None
        assert res_course is not None
        assert res_risk is not None
        assert res_absence is not None
        assert res_tier is not None


@pytest.mark.postgres
def test_postgres_idempotent_etl_loading(pg_session):
    """Verifies that DatabaseLoader correctly populates PostgreSQL and is strictly idempotent."""
    loader = DatasetLoader()
    df_mat, df_por, metadata = loader.load_raw_datasets()
    transformer = EducationalTransformer()
    students_df, courses_df, records_df = transformer.transform(df_mat, df_por)

    db_loader = DatabaseLoader(db_session=pg_session)

    # First load
    db_loader.load_courses(courses_df)
    db_loader.load_students(students_df)
    db_loader.load_academic_records(records_df)

    count_students = pg_session.query(StudentModel).count()
    count_courses = pg_session.query(CourseModel).count()
    count_records = pg_session.query(AcademicRecordModel).count()

    assert count_students == 674, f"Expected 674 students, got {count_students}"
    assert count_courses == 2, f"Expected 2 courses, got {count_courses}"
    assert count_records == 1044, f"Expected 1044 records, got {count_records}"

    # Second load (Idempotency check: counts must remain invariant)
    db_loader.load_courses(courses_df)
    db_loader.load_students(students_df)
    db_loader.load_academic_records(records_df)

    assert pg_session.query(StudentModel).count() == 674
    assert pg_session.query(CourseModel).count() == 2
    assert pg_session.query(AcademicRecordModel).count() == 1044


@pytest.mark.postgres
def test_postgres_unique_constraint_enforcement(pg_session):
    """Verifies that PostgreSQL enforces uq_student_course composite unique constraint."""
    dup_record = AcademicRecordModel(
        record_id="REC-PG-TEST-DUP",
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
        pg_session.add(dup_record)
        pg_session.commit()
    pg_session.rollback()


@pytest.mark.postgres
def test_postgres_analytical_views_query(pg_engine):
    """Verifies that PostgreSQL analytical views return accurate aggregations on loaded data."""
    with pg_engine.connect() as conn:
        res = conn.execute(text("SELECT course_code, total_enrollments, pass_rate_pct FROM v_course_performance ORDER BY course_code")).fetchall()
        assert len(res) == 2
        # MAT: 395 records, POR: 649 records
        row_mat = res[0]
        row_por = res[1]
        assert row_mat[0] == "MAT" and row_mat[1] == 395
        assert row_por[0] == "POR" and row_por[1] == 649

        # Verify absence tier binning
        tiers = conn.execute(text("SELECT absence_tier, student_count FROM v_absence_impact")).fetchall()
        assert len(tiers) > 0

        # Verify performance tier distribution
        perf_tiers = conn.execute(text("SELECT performance_tier, student_count FROM v_performance_distribution")).fetchall()
        assert len(perf_tiers) > 0


@pytest.mark.postgres
def test_postgres_fastapi_endpoints(pg_session):
    """Verifies that FastAPI endpoints return accurate data when querying PostgreSQL."""
    from backend.app.main import app
    from database.connection import get_db
    from fastapi.testclient import TestClient

    def override_get_db():
        try:
            yield pg_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    try:
        resp = client.get("/api/analytics/overview")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_students"] == 674
        assert data["total_enrollments"] == 1044
        assert data["pass_rate_pct"] == 78.0

        resp_health = client.get("/api/health")
        assert resp_health.status_code == 200
        assert resp_health.json()["status"] == "UP"
        assert resp_health.json()["database"] == "HEALTHY"
    finally:
        app.dependency_overrides.clear()
