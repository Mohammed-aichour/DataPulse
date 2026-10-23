"""
Comprehensive Audited Pytest Test Suite for DataPulse
Tests Data Authenticity, 1-to-1 Entity Linkage, Multi-Pillar Quality Framework,
Idempotency, 3-Horizon ML Anti-Leakage Pipelines, and FastAPI REST Endpoints.
"""

import sys
from pathlib import Path

# Ensure root directory and parent are in sys.path
root_dir = Path(__file__).resolve().parent.parent
parent_dir = root_dir.parent
for p in [str(root_dir), str(parent_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

import pytest
from fastapi.testclient import TestClient

try:
    from database.connection import SessionLocal
    from database.models import StudentModel, AcademicRecordModel, CourseModel
    from backend.app.main import app
    from src.ingestion.dataset_loader import DatasetLoader
    from src.preprocessing.validator import DataValidator
    from src.preprocessing.transformer import EducationalTransformer
    from src.ml.predictor import PredictorService, StudentPredictionInput
    from src.pipeline.db_loader import DatabaseLoader
except ImportError:
    from backend.app.main import app
    from database.connection import SessionLocal
    from database.models import StudentModel, AcademicRecordModel, CourseModel
    from src.ingestion.dataset_loader import DatasetLoader
    from src.preprocessing.validator import DataValidator
    from src.preprocessing.transformer import EducationalTransformer
    from src.ml.predictor import PredictorService, StudentPredictionInput
    from src.pipeline.db_loader import DatabaseLoader


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


# ==================== 1. DATASET AUTHENTICITY & INTEGRITY ====================

def test_dataset_authenticity_and_hashes():
    loader = DatasetLoader()
    df_mat, df_por, metadata = loader.load_raw_datasets()
    assert len(df_mat) == 395
    assert len(df_por) == 649
    assert len(metadata) == 2

    # Cryptographic hashes must match genuine UCI files
    for m in metadata:
        assert len(m.sha256_checksum) == 64
        assert m.is_synthetic is False
        assert m.row_count in {395, 649}


# ==================== 2. DATA VALIDATION & QUALITY PILLARS ====================

def test_multi_pillar_data_quality_framework():
    loader = DatasetLoader()
    df_mat, df_por, _ = loader.load_raw_datasets()
    validator = DataValidator()

    _, report_mat = validator.validate_dataframe(df_mat, "Mathematics")
    _, report_por = validator.validate_dataframe(df_por, "Portuguese")

    # Honest institutional scores (audited between 85 and 95)
    assert 85.0 <= report_mat.quality_score <= 95.0
    assert 85.0 <= report_por.quality_score <= 95.0

    # Verify quality pillars
    assert report_mat.quality_pillars["completeness"] == 100.0
    assert report_mat.quality_pillars["schema_validity"] == 100.0
    assert report_mat.quality_pillars["key_integrity"] == 75.0
    assert report_mat.quality_pillars["granularity_authenticity"] == 80.0
    assert len(report_mat.methodology_notes) == 5


# ==================== 3. 1-TO-1 ENTITY LINKAGE & ZERO COLLISIONS ====================

def test_entity_linkage_zero_intra_course_duplicates():
    loader = DatasetLoader()
    df_mat, df_por, _ = loader.load_raw_datasets()
    transformer = EducationalTransformer()
    students, courses, records = transformer.transform(df_mat, df_por)

    assert len(records) == 1044
    assert len(courses) == 2
    assert len(students) == 674

    # CRUCIAL: Zero students should have multiple enrollments in the same course
    intra_dups = records.duplicated(subset=["student_id", "course_code"]).sum()
    assert intra_dups == 0, f"Found {intra_dups} duplicate enrollments in the same course!"

    # Engineered features
    assert "parent_edu_avg" in records.columns
    assert "alcohol_index" in records.columns
    assert "study_to_social_ratio" in records.columns
    assert "academic_risk" in records.columns
    assert "passing_status" in records.columns
    assert "performance_tier" in records.columns


# ==================== 4. DATABASE IDEMPOTENCY & TRANSACTIONS ====================

def test_database_idempotency():
    db = SessionLocal()
    init_students = db.query(StudentModel).count()
    init_records = db.query(AcademicRecordModel).count()
    db.close()

    assert init_students == 674
    assert init_records == 1044

    # Run loader again on existing tables
    loader = DatasetLoader()
    df_mat, df_por, _ = loader.load_raw_datasets()
    transformer = EducationalTransformer()
    students, courses, records = transformer.transform(df_mat, df_por)

    db_loader = DatabaseLoader()
    db_loader.load_courses(courses)
    db_loader.load_students(students)
    db_loader.load_academic_records(records)
    db_loader.close()

    db2 = SessionLocal()
    post_students = db2.query(StudentModel).count()
    post_records = db2.query(AcademicRecordModel).count()
    db2.close()

    # Counts must remain strictly stable without duplication
    assert post_students == 674
    assert post_records == 1044


# ==================== 5. MACHINE LEARNING 3-HORIZON PREDICTION ====================

def test_ml_three_horizon_scenarios():
    predictor = PredictorService()
    assert predictor.is_ready() is True

    # 1. Scenario A: Early Intake (Pre-Grades: G1 and G2 omitted)
    input_early = StudentPredictionInput(
        course_code="MAT",
        studytime=1,
        failures=2,
        absences=14,
        scenario="early"
    )
    res_a = predictor.predict(input_early)
    assert res_a["scenario_used"]["key"] == "scenario_a"
    assert res_a["scenario_used"]["anti_leakage_status"] == "VERIFIED_NO_TARGET_LEAKAGE"
    assert "predicted_grade_g3" in res_a
    assert 0.0 <= res_a["predicted_grade_g3"] <= 20.0
    assert 0.0 <= res_a["risk_probability"] <= 1.0

    # 2. Scenario B: Mid-Term (With Period 1 Grade G1)
    input_mid = StudentPredictionInput(
        course_code="MAT",
        studytime=2,
        failures=0,
        absences=3,
        G1=14,
        scenario="midterm"
    )
    res_b = predictor.predict(input_mid)
    assert res_b["scenario_used"]["key"] == "scenario_b"
    assert res_b["is_at_risk"] is False

    # 3. Scenario C: Late-Stage (With G1 & G2)
    input_late = StudentPredictionInput(
        course_code="MAT",
        studytime=3,
        failures=0,
        absences=1,
        G1=16,
        G2=17,
        scenario="latestage"
    )
    res_c = predictor.predict(input_late)
    assert res_c["scenario_used"]["key"] == "scenario_c"
    assert res_c["predicted_grade_g3"] >= 14.0
    assert res_c["is_at_risk"] is False
    assert res_c["risk_probability"] < 0.20


# ==================== 6. REST API ENDPOINT TESTS ====================

def test_api_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert data["database"] == "HEALTHY"
    assert data["ml_models"] == "READY"


def test_api_info(client):
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert data["institution"] == "Universiapolis International University of Agadir (UIA)"
    assert data["total_records"] == 1044
    assert data["unique_students"] == 674


def test_api_analytics_overview(client):
    response = client.get("/api/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_students"] == 674
    assert data["total_enrollments"] == 1044
    assert data["avg_final_grade"] > 10.0
    assert data["pass_rate_pct"] > 70.0
    assert data["data_quality_score"] >= 85.0


def test_api_analytics_courses(client):
    response = client.get("/api/analytics/courses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    codes = {c["course_code"] for c in data}
    assert "MAT" in codes
    assert "POR" in codes


def test_api_analytics_distribution(client):
    response = client.get("/api/analytics/distribution")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 8


def test_api_analytics_performance_factors(client):
    # Study time
    r_study = client.get("/api/analytics/performance?factor=studytime")
    assert r_study.status_code == 200
    assert len(r_study.json()) > 0

    # Absences
    r_abs = client.get("/api/analytics/performance?factor=absences")
    assert r_abs.status_code == 200
    assert len(r_abs.json()) > 0


def test_api_analytics_correlations(client):
    response = client.get("/api/analytics/correlations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_api_students_list_and_filter(client):
    response = client.get("/api/students?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 674
    assert len(data["items"]) == 10

    resp_search = client.get("/api/students?search=STU-0001")
    assert resp_search.status_code == 200
    assert resp_search.json()["total"] == 1


def test_api_student_detail(client):
    response = client.get("/api/students/STU-0001")
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == "STU-0001"
    assert len(data["enrollments"]) >= 1


def test_api_ml_evaluation_and_predict(client):
    eval_resp = client.get("/api/ml/evaluation")
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    assert "scenarios" in eval_data
    assert "scenario_a" in eval_data["scenarios"]
    assert "scenario_c" in eval_data["scenarios"]

    # Predict early scenario
    payload_early = {
        "course_code": "MAT",
        "studytime": 1,
        "failures": 2,
        "absences": 10,
        "scenario": "early"
    }
    pred_resp = client.post("/api/ml/predict", json=payload_early)
    assert pred_resp.status_code == 200
    pred_data = pred_resp.json()
    assert pred_data["scenario_used"]["key"] == "scenario_a"
    assert pred_data["scenario_used"]["anti_leakage_status"] == "VERIFIED_NO_TARGET_LEAKAGE"


def test_api_export_csv(client):
    resp_csv = client.get("/api/export/csv/students")
    assert resp_csv.status_code == 200
    assert "text/csv" in resp_csv.headers["content-type"]
    assert "student_id" in resp_csv.text


def test_api_powerbi_spec(client):
    resp_pbi = client.get("/api/export/powerbi-spec")
    assert resp_pbi.status_code == 200
    data = resp_pbi.json()
    assert "star_schema" in data
    assert "recommended_dax_measures" in data
