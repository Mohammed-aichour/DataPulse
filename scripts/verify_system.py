"""
DataPulse Full System Verification & Health Check Script
Performs an end-to-end audit check across DB, ML, and API services.

Usage:
    python scripts/verify_system.py
    python -m scripts.verify_system
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure root directory is on sys.path
root_dir = Path(__file__).resolve().parent.parent
parent_of_root = root_dir.parent
for p in [str(root_dir), str(parent_of_root)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from database.connection import SessionLocal, engine
    from database.models import AcademicRecordModel, CourseModel, StudentModel
    from src.ml.predictor import PredictorService, StudentPredictionInput
    from backend.app.main import app
except ImportError:
    from database.connection import SessionLocal, engine
    from database.models import AcademicRecordModel, CourseModel, StudentModel
    from src.ml.predictor import PredictorService, StudentPredictionInput
    from backend.app.main import app


def verify_system():
    print("=" * 80)
    print("  DATAPULSE END-TO-END SYSTEM VERIFICATION AUDIT")
    print("=" * 80)

    # 1. Database Check
    print("\n[Audit 1/4: Relational Database Integrity]")
    db = SessionLocal()
    try:
        student_count = db.query(StudentModel).count()
        record_count = db.query(AcademicRecordModel).count()
        course_count = db.query(CourseModel).count()
        print(f"  * Engine:             {engine.url}")
        print(f"  * Unique Students:    {student_count} (Expected: 674)")
        print(f"  * Academic Records:   {record_count} (Expected: 1044)")
        print(f"  * Courses Registered: {course_count} (Expected: 2)")
        assert student_count == 674, f"Student count mismatch: {student_count}"
        assert record_count == 1044, f"Record count mismatch: {record_count}"
        assert course_count == 2, f"Course count mismatch: {course_count}"
        print("  -> Database Integrity: PASSED [100%]")
    finally:
        db.close()

    # 2. ML Artifacts Check
    print("\n[Audit 2/4: Machine Learning Artifacts & Predictor]")
    predictor = PredictorService()
    is_ready = predictor.is_ready()
    print(f"  * Multi-Horizon Predictor Ready: {is_ready}")
    assert is_ready, "PredictorService models are not ready!"

    test_input = StudentPredictionInput(
        scenario="a",
        course_code="MAT",
        studytime=3,
        failures=0,
        absences=2,
        school="GP",
        sex="F",
        age=17,
        Medu=4,
        Fedu=3
    )
    res = predictor.predict(test_input)
    print(f"  * Scenario A Test Inference: Grade={res['predicted_grade_g3']:.2f}, Risk={res['is_at_risk']}, Prob={res['risk_probability']:.3f}")
    assert res["scenario"] in ["a", "scenario_a"]
    assert "predicted_grade_g3" in res
    print("  -> Machine Learning Inference: PASSED [100%]")

    # 3. API Integration Check
    print("\n[Audit 3/4: FastAPI REST Endpoints via TestClient]")
    client = TestClient(app)

    endpoints = [
        ("/api/health", 200),
        ("/api/info", 200),
        ("/api/analytics/overview", 200),
        ("/api/analytics/courses", 200),
        ("/api/analytics/distribution", 200),
        ("/api/students?page=1&page_size=5", 200),
        ("/api/ml/evaluation?scenario=a", 200),
        ("/api/ml/model-info", 200)
    ]

    for path, expected_status in endpoints:
        resp = client.get(path)
        assert resp.status_code == expected_status, f"Endpoint {path} failed with {resp.status_code}: {resp.text}"
        print(f"  * GET {path:<38} -> HTTP {resp.status_code} OK")

    # Post predict test
    post_resp = client.post("/api/ml/predict", json={
        "scenario": "a",
        "course_code": "MAT",
        "studytime": 4,
        "failures": 0,
        "absences": 1
    })
    assert post_resp.status_code == 200
    print("  * POST /api/ml/predict (Scenario A)      -> HTTP 200 OK")
    print("  -> REST API Integration: PASSED [100%]")

    # 4. Summary
    print("\n" + "=" * 80)
    print("  SYSTEM VERIFICATION COMPLETED: ALL SYSTEMS OPERATIONAL (PRODUCTION-READY)")
    print("=" * 80)
    return True


if __name__ == "__main__":
    verify_system()
