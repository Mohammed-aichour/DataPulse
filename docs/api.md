# DataPulse — REST API Specification

DataPulse exposes high-performance RESTful endpoints built with FastAPI. All endpoints are interactive and self-documenting via Swagger UI at `/api/docs` and ReDoc at `/api/redoc`.

Base URL: `http://localhost:8000/api`

---

## 1. System & Health Endpoints

### `GET /health`
Returns the operational health of the database and machine learning inference services.
```bash
curl -X GET http://localhost:8000/api/health
```
**Response:**
```json
{
  "status": "UP",
  "timestamp": "2026-10-23T13:00:00Z",
  "database": "HEALTHY",
  "ml_models": "READY",
  "version": "1.0.0"
}
```

### `GET /info`
Institutional project attribution and dataset summary.

---

## 2. Analytics Endpoints

### `GET /analytics/overview`
Computes executive institutional KPIs directly from live database tables.
```bash
curl -X GET http://localhost:8000/api/analytics/overview
```
**Response:**
```json
{
  "total_students": 674,
  "total_enrollments": 1044,
  "avg_final_grade": 11.34,
  "pass_rate_pct": 78.0,
  "risk_count": 230,
  "risk_rate_pct": 22.0,
  "avg_absences": 4.9,
  "data_quality_score": 91.2,
  "courses_count": 2,
  "last_pipeline_run": "2026-10-23T13:30:00.000000+00:00"
}
```

### `GET /analytics/courses`
Comparative breakdown between Mathematics (`MAT`) and Portuguese (`POR`).

### `GET /analytics/distribution`
Multi-period grade distribution across standard evaluation score bands.

### `GET /analytics/performance?factor={factor_name}`
Grouped analysis by `studytime`, `failures`, `parent_edu`, `absences`, `school`, `sex`, or `internet`.

### `GET /analytics/correlations`
Pearson correlation coefficients ranking student attributes with final academic grade (G3).

---

## 3. Student Directory Endpoints

### `GET /students`
Searchable, filterable, and paginated student list.
- Query Parameters: `page`, `page_size`, `search`, `school`, `course`, `risk_only`.

### `GET /students/{student_id}`
Returns full demographic and multi-course enrollment history for a specific student (e.g. `STU-0001`).

---

## 4. Machine Learning & Prediction Endpoints

DataPulse employs a **3-Horizon Multi-Horizon Architecture** to prevent target leakage:
- **Scenario A (`scenario=a`)**: Intake / Pre-Exam Warning (Week 0-4, excludes $G1, G2$).
- **Scenario B (`scenario=b`)**: Mid-Term Progress Check (Month 3, incorporates $G1$).
- **Scenario C (`scenario=c`)**: Late-Stage Final Projections (Month 7, incorporates $G1 + G2$).

### `GET /ml/model-info`
Returns active model architectures, feature lists per scenario, and training timestamps.

### `GET /ml/evaluation?scenario={a|b|c}`
Returns cross-validated benchmark metrics (accuracy, precision, recall, F1, ROC-AUC, MAE, R²) and top feature importance weights for the chosen horizon (defaults to `a`).

### `POST /ml/predict`
Executes real-time student performance inference using scenario routing.
```bash
curl -X POST http://localhost:8000/api/ml/predict \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "a",
    "course_code": "MAT",
    "studytime": 3,
    "failures": 0,
    "absences": 2,
    "school": "GP",
    "sex": "F",
    "age": 16,
    "Medu": 3,
    "Fedu": 3
  }'
```
**Response:**
```json
{
  "scenario": "a",
  "scenario_description": "Scenario A: Intake / Pre-Exam Warning (Weeks 0-4, zero grades)",
  "predicted_grade_g3": 11.85,
  "is_at_risk": false,
  "risk_probability": 0.184,
  "risk_tier": "Low Academic Risk",
  "confidence_pct": 81.6,
  "recommendation": "Student demonstrates sound foundational engagement with zero prior academic failures.",
  "contributing_factors": [
    "No recorded prior course failures (protective factor).",
    "Good weekly study commitment (studytime >= 3)."
  ],
  "model_used": {
    "classifier": "Gradient Boosting Classifier",
    "regressor": "Random Forest Regressor"
  },
  "timestamp": "2026-10-23T13:30:00.000000+00:00"
}
```

---

## 5. Pipeline Orchestration Endpoints

### `POST /pipeline/run`
Executes the full master ETL and ML retraining pipeline synchronously.

### `GET /pipeline/status`
Returns database table row counts, execution duration, and data freshness indicators.

### `GET /pipeline/history`
Audit log of past pipeline execution runs.

---

## 6. Export & Power BI Endpoints

### `GET /export/csv/{dataset_name}`
Downloads clean CSV data (`students`, `academic_records`, or `courses`).

### `GET /export/powerbi-spec`
Returns star-schema architecture, DAX formulas, and connection guides for Power BI desktop integration.
