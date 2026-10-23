"""
DataPulse Backend API Unit & Integration Tests
Tests health, overview, courses, distribution, students, and multi-scenario prediction.
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

root_dir = Path(__file__).resolve().parent.parent.parent
parent_of_root = root_dir.parent
for p in [str(root_dir), str(parent_of_root)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from backend.app.main import app
except ImportError:
    from backend.app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert data["database"] == "HEALTHY"
    assert data["ml_models"] == "READY"


def test_system_info():
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert data["unique_students"] == 674
    assert data["total_records"] == 1044


def test_analytics_overview():
    response = client.get("/api/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_students"] == 674
    assert data["total_enrollments"] == 1044
    assert data["data_quality_score"] == 91.2
    assert 70.0 <= data["pass_rate_pct"] <= 85.0


def test_students_pagination():
    response = client.get("/api/students?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["total"] == 674


def test_predict_scenario_a():
    response = client.post("/api/ml/predict", json={
        "scenario": "a",
        "course_code": "MAT",
        "studytime": 3,
        "failures": 0,
        "absences": 2
    })
    assert response.status_code == 200
    data = response.json()
    assert data["scenario"] in ["a", "scenario_a"]
    assert 0.0 <= data["predicted_grade_g3"] <= 20.0
    assert 0.0 <= data["risk_probability"] <= 1.0


def test_predict_scenario_c():
    response = client.post("/api/ml/predict", json={
        "scenario": "c",
        "course_code": "MAT",
        "studytime": 3,
        "failures": 0,
        "absences": 2,
        "G1": 15,
        "G2": 16
    })
    assert response.status_code == 200
    data = response.json()
    assert data["scenario"] in ["c", "scenario_c"]
    assert data["is_at_risk"] is False
