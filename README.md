# DataPulse — Smart Campus Analytics & Predictive Intelligence Platform

[![CI Pipeline](https://img.shields.io/badge/CI-Passing-emerald?style=flat-square&logo=github-actions)](https://github.com)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.13-blue?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.161-teal?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.3-cyan?style=flat-square&logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-6.0-blue?style=flat-square&logo=typescript)](https://www.typescriptlang.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

An enterprise-grade, end-to-end Data Engineering, Machine Learning, and Interactive Analytics platform designed for higher education administration and student retention. Developed by a 2nd-year Computer Engineering student at **Universiapolis International University of Agadir (UIA)**.

---

## 1. Problem Statement & Executive Overview

Higher education institutions face a systemic retention challenge: traditional analytics systems typically assess student vulnerability only after final examinations or post-midterm reviews, when it is often too late to deploy corrective academic support. 

Furthermore, naive machine learning implementations frequently suffer from **target leakage**—predicting end-of-year grades using late-term exam marks ($G1$ and $G2$) and falsely marketing the result as "early warning foresight."

**DataPulse** addresses this challenge through an audited, multi-horizon data lifecycle:
$$\text{Authentic Ingestion} \longrightarrow \text{Multi-Pillar QA} \longrightarrow \text{1-to-1 Entity Linkage} \longrightarrow \text{3-Horizon ML (No Leakage)} \longrightarrow \text{Executive SaaS UI}$$

---

## 2. System Architecture

```mermaid
flowchart TD
    subgraph DataSources["1. Data Ingestion & Provenance"]
        UCI["UCI ML Repository (Dataset #320)"] --> DL["DatasetLoader (SHA-256 Hash Auditing)"]
        DL --> RAW["Raw Datasets (student-mat.csv, student-por.csv)"]
    end

    subgraph DataEngineering["2. Data Engineering & ETL Pipeline"]
        RAW --> VAL["DataValidator (Multi-Pillar QA & Outlier Engine)"]
        VAL --> REP["Quality Reports (JSON & Markdown)"]
        VAL --> TR["EducationalTransformer (1-to-1 Linkage: 674 Students / 1,044 Records)"]
        TR --> DBL["DatabaseLoader (SQLAlchemy Atomic Transactions)"]
    end

    subgraph Storage["3. Relational Storage Layer"]
        DBL --> DB[(PostgreSQL 16 / SQLite)]
        DB --> VIEWS["Analytical SQL Views (v_student_overview, v_course_perf, v_absence_impact)"]
        VIEWS --> PBI["Power BI Stream & CSV Exports"]
    end

    subgraph MachineLearning["4. 3-Horizon ML Framework (Anti-Leakage)"]
        TR --> SC_A["Scenario A: Early Intake (Pre-Grades)"]
        TR --> SC_B["Scenario B: Mid-Term (Post-G1)"]
        TR --> SC_C["Scenario C: Late-Stage (Post-G1 & G2)"]
        SC_A & SC_B & SC_C --> ARTIFACTS["Model Artifacts (.joblib & model_metadata.json)"]
        ARTIFACTS --> PRED["PredictorService (Multi-Scenario Inference & Explainability)"]
    end

    subgraph BackendAPI["5. RESTful API Backend"]
        DB --> API["FastAPI Asynchronous Engine"]
        PRED --> API
        API --> REST["Documented OpenAPI Endpoints (/api/analytics, /api/students, /api/ml)"]
    end

    subgraph FrontendApp["6. Executive SaaS Web Interface"]
        REST --> UI["React 19 + TypeScript + Vite + Tailwind CSS"]
        UI --> DASH["Executive Dashboard"]
        UI --> DIR["Student Directory & Academic Profiles"]
        UI --> ADV["Factor Analysis & Correlation Explorer"]
        UI --> LIVE_ML["Multi-Horizon Risk Simulation Engine"]
        UI --> ETL_MGR["ETL Orchestration & Quality Logs"]
    end
```

---

## 3. Dataset Authenticity & The Entity Linkage Discovery

- **Source**: UCI Machine Learning Repository — [Dataset ID: 320 (Student Performance)](https://archive.ics.uci.edu/dataset/320/student+performance)
- **Authors**: Paulo Cortez and Alice Silva (University of Minho, Guimarães, Portugal)
- **Attribution & Licensing**: CC BY 4.0 International, preserved in [data/README.md](data/README.md).
- **Verified Files**:
  - `student-mat.csv`: 395 records (SHA-256: `e47f9ee225e1...`) — `is_synthetic: False`.
  - `student-por.csv`: 649 records (SHA-256: `a7594a11d777...`) — `is_synthetic: False`.
  - Total Verified Enrollments: **1,044 records**.

### Entity Linkage Modeling, Linkage Assumptions & Limitations:
Cortez & Silva (2008) provided an R script (`student-merge.R`) matching students on 13 demographic attributes, reporting 382 common students. 
During our data engineering audit, we discovered that **demographic attributes do not form a unique natural key within classes**:
- 4 pairs of students in Mathematics and 12 pairs in Portuguese share identical demographic traits while having different grades, guardians, and study times.
- Naive SQL/Pandas merging on those 13 attributes causes cartesian product expansion, falsely collapsing distinct students into duplicate enrollments within the same course.
- **DataPulse Solution**: Implemented **1-to-1 occurrence-ranked linkage (`cumcount()`)**, deriving:
  - **370 students** linked across both Mathematics and Portuguese.
  - **25 students** linked exclusively in Mathematics.
  - **279 students** linked exclusively in Portuguese.
  - **Total derived cross-course student keys: 674 entities** (`STU-0001` to `STU-0674`), with **zero intra-course collisions**.
- **Important Data Integrity & Assumption Note**: These 674 student keys are an **engineered modeling heuristic** derived via demographic matching and occurrence ordering across the two course datasets. Because the raw UCI repository does not contain authoritative student IDs or civil records, these keys represent **derived analytical entities under the stated linkage assumptions**, NOT 674 independently verified real-world human identities. If two distinct individuals share identical demographics, this heuristic cannot separate them without administrative ground-truth data.

---

## 4. Multi-Pillar Data Quality Scorecard

Instead of unscientific 100% claims, DataPulse implements a transparent 5-pillar institutional scoring framework:

| Quality Pillar | Weight | Score | Evaluation Criteria |
|---|---|---|---|
| **Completeness** | 25% | **100.0%** | Zero null cells across all 1,044 records |
| **Schema Conformance** | 25% | **100.0%** | 100% adherence to Pydantic v2 domain ranges |
| **Key Integrity** | 20% | **75.0%** | Penalized due to absence of verified natural surrogate keys (heuristic linkage) |
| **Outlier Regularity** | 15% | **96.3%** | Evaluates extreme right-skewed absences (>15 days) and dropouts ($G3=0$) |
| **Granularity Authenticity**| 15% | **80.0%** | Absences are cumulative term integer counts rather than timestamped swipe logs |
| **Combined Institutional Score** | **100%** | **91.2 / 100** | **Status: PASSED / PRODUCTION READY** |

---

## 5. Machine Learning: 3-Horizon Anti-Leakage Framework

To eliminate target leakage, DataPulse trains and benchmarks models across three distinct operational time horizons:

### Benchmark Comparison (Stratified 5-Fold Cross-Validation on Unseen Test Split)

| Horizon | Grades Available | Best Classifier | Test ROC-AUC | 5-Fold CV ROC-AUC | Best Regressor | MAE | $R^2$ Score |
|---|---|---|---|---|---|---|---|
| **Scenario A: Early Intake** *(Pre-Term)* | **Zero (Pre-Grades)** | **Random Forest** | **0.818** | **0.800 (±0.021)** | **Gradient Boosting** | **2.21 pts** | **0.329** |
| **Scenario B: Mid-Term** *(Month 3)* | **G1 (Period 1)** | **Logistic Regression** | **0.931** | **0.892 (±0.018)** | **Gradient Boosting** | **1.26 pts** | **0.765** |
| **Scenario C: Late-Stage** *(Month 7)* | **G1, G2 & Delta** | **Logistic Regression** | **0.971** | **0.954 (±0.012)** | **Random Forest** | **0.76 pts** | **0.932** |

### Key Takeaways:
1. **Scenario A (Intake)** relies purely on demographic background, parental education capital ($r = +0.22$), study time ($r = +0.16$), and past class failures ($r = -0.38$). It provides an authentic early warning before any exams are sat.
2. **Scenario B (Mid-Term)** captures the significant performance shift once first-period grades are published ($G1$ correlation $r = 0.82$).
3. **Scenario C (Late-Stage)** achieves high precision for borderline student intervention right before final examinations.

---

## 6. Project Architecture & Repository Layout

```text
DataPulse/
├── backend/
│   ├── app/
│   │   ├── api/            # REST API route handlers (analytics, export, health, ml, pipeline, students)
│   │   ├── core/           # Configuration, settings & security (Pydantic Settings)
│   │   ├── schemas/        # Pydantic v2 request & response contracts
│   │   └── main.py         # FastAPI application entrypoint with CORS & lifespan
│   ├── tests/              # Backend endpoint integration tests
│   ├── requirements.txt    # Production Python dependencies
│   └── Dockerfile          # Backend container specification
├── frontend/
│   ├── src/
│   │   ├── components/     # UI widgets, Navbar, Sidebar
│   │   ├── pages/          # Dashboard, Analytics, Students, ML (3-Horizon), Data Mgmt, Settings
│   │   ├── services/       # Centralized API HTTP client (Axios/fetch with base URL env)
│   │   └── types/          # TypeScript interface contracts
│   ├── nginx.conf          # Production web server configuration
│   ├── package.json        # Frontend dependencies (React 19, Vite, Tailwind CSS, Recharts)
│   └── Dockerfile          # Multi-stage frontend container build
├── data/
│   ├── raw/                # Authenticated UCI datasets (student-mat.csv, student-por.csv)
│   ├── processed/          # Clean 3NF CSV files (students.csv, academic_records.csv, courses.csv)
│   └── README.md           # Dataset provenance & CC-BY-4.0 license documentation
├── etl/
│   ├── __init__.py         # Package root
│   └── run.py              # Dedicated ETL runner (python -m etl.run)
├── ml/
│   ├── __init__.py         # Package root
│   ├── train.py            # Dedicated 3-Horizon ML trainer (python -m ml.train)
│   └── evaluate.py         # Dedicated ML evaluation & benchmark runner (python -m ml.evaluate)
├── database/
│   ├── migrations/         # Alembic database migration scripts & versions
│   ├── sql/                # Analytical SQL views (v_student_overview, v_course_perf, v_absence_impact)
│   ├── connection.py       # SQLAlchemy engine (PostgreSQL primary with SQLite fallback)
│   └── models.py           # 3NF ORM entities (Student, Course, AcademicRecord, etc.)
├── scripts/
│   ├── init_db.py          # Database initialization & SQL view compilation
│   ├── seed_db.py          # Idempotent development & demo data seeder
│   └── verify_system.py    # End-to-end smoke test & system health verifier
├── docs/                   # Full technical specifications (api.md, architecture.md, database.md, deployment.md)
├── models_artifacts/       # Serialized models (.joblib) and model_metadata.json
├── reports/                # Data quality and ML evaluation JSON/Markdown reports
├── docker-compose.yml      # Multi-container orchestration (PostgreSQL 16, Backend, Frontend)
├── pyproject.toml          # Standard packaging & pytest configuration
├── setup.py                # Setuptools editable installation support
├── .env.example            # Environment variables template
└── README.md
```

---

## 7. Quickstart Guide (Local Execution)

### Prerequisites
- Python 3.11+
- Node.js 20+

### Step 1: Clone & Setup Virtual Environment
```bash
git clone https://github.com/Mohammed-aichour/DataPulse.git
cd DataPulse

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r backend/requirements.txt
pip install -e .
```

### Step 2: Database Initialization, Migrations & Seeding
```bash
# Apply version-controlled Alembic migrations
alembic upgrade head

# Compile analytical SQL views
python scripts/init_db.py

# Run dedicated ETL pipeline (Extract -> Validate -> Transform -> Load)
python -m etl.run

# Or seed database idempotently
python scripts/seed_db.py
```

### Step 3: Machine Learning Training & Evaluation
```bash
# Train the 3-Horizon anti-leakage models (Scenarios A, B, C)
python -m ml.train

# Benchmark models against naive baselines with full metrics table
python -m ml.evaluate
```

### Step 4: Run Automated Verification & Pytest Suite
```bash
# Run end-to-end system smoke test
python scripts/verify_system.py

# Execute full pytest suite (29 integration, database, and API tests)
pytest -v
```

### Step 5: Start FastAPI Backend (Port 8000)
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Interactive Swagger Documentation: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)*

### Step 6: Start React Frontend (Port 3000)
```bash
cd frontend
npm install
npm run dev
```
*Web Application: [http://localhost:5173](http://localhost:5173) (or configured port)*

---

## 8. Docker Compose & PostgreSQL 16 (Multi-Container Architecture)

```bash
docker compose up --build -d
```
- **PostgreSQL 16**: Port `127.0.0.1:5432` with persistent volume `postgres_data` and automated healthcheck.
- **FastAPI Backend**: Port `127.0.0.1:8000` (auto-runs Alembic migrations, ETL pipeline check, and serves REST API).
- **React Frontend (Nginx)**: Port `127.0.0.1:3000` (serves production build with reverse proxy).

> [!IMPORTANT]
> **Host Environment Status**: Docker Compose execution on this specific Windows host machine is classified as **NOT TESTED** because the Docker CLI is not installed in the Windows environment (`docker: The term 'docker' is not recognized`). 
> All Dockerfiles, compose specifications, environment variable bindings, and migration scripts are fully authored and syntactically verified.

### How to Run and Verify PostgreSQL with Docker:
```bash
# 1. Create .env with strong secrets
cp .env.example .env
# Edit .env and set secure POSTGRES_PASSWORD and JWT_SECRET

# 2. Build and start containers
docker compose up --build -d

# 3. Check container health
docker compose ps

# 4. Verify live health endpoint
curl http://127.0.0.1:8000/api/health

# 5. Run the test suite against PostgreSQL inside the container
docker compose exec backend pytest -v
```

### How to Test Against Local/Remote PostgreSQL (Without Docker):
```bash
# Set PostgreSQL connection in .env or environment
export DATABASE_URL="postgresql+psycopg2://datapulse_user:YOUR_STRONG_PASSWORD@127.0.0.1:5432/datapulse_db"
export TEST_DATABASE_URL="postgresql+psycopg2://datapulse_user:YOUR_STRONG_PASSWORD@127.0.0.1:5432/datapulse_db"

# Apply Alembic migrations to PostgreSQL
alembic upgrade head

# Ingest dataset idempotently into PostgreSQL
python -m etl.run

# Execute test suite against PostgreSQL
pytest -v
```

---

## 9. Automated Testing & Verification Summary

### Database Engine Context:
- **Default Local & CI Test Suite Engine**: **SQLite** (all 29 unit, integration, and API tests run against SQLite with 100% pass rate in 8.45s).
- **PostgreSQL Integration Capability**: The integration suite dynamically targets PostgreSQL whenever `TEST_DATABASE_URL` is set to a PostgreSQL connection URI.

Full Pytest suite execution across all 29 tests:
```text
tests/test_database_integration.py::test_alembic_clean_schema_migration PASSED [  3%]
tests/test_database_integration.py::test_views_compilation_and_querying PASSED [  6%]
tests/test_database_integration.py::test_idempotent_etl_data_loading PASSED [ 10%]
tests/test_database_integration.py::test_unique_constraint_prevents_duplicate_enrollment PASSED [ 13%]
tests/test_database_integration.py::test_database_views_return_real_data PASSED [ 17%]
tests/test_database_integration.py::test_unreachable_database_error_handling PASSED [ 20%]
tests/test_pipeline_and_api.py::test_dataset_authenticity_and_hashes PASSED [ 24%]
tests/test_pipeline_and_api.py::test_multi_pillar_data_quality_framework PASSED [ 27%]
tests/test_pipeline_and_api.py::test_entity_linkage_zero_intra_course_duplicates PASSED [ 31%]
tests/test_pipeline_and_api.py::test_database_idempotency PASSED         [ 34%]
tests/test_pipeline_and_api.py::test_ml_three_horizon_scenarios PASSED   [ 37%]
tests/test_pipeline_and_api.py::test_api_health PASSED                   [ 41%]
tests/test_pipeline_and_api.py::test_api_info PASSED                     [ 44%]
tests/test_pipeline_and_api.py::test_api_analytics_overview PASSED       [ 48%]
tests/test_pipeline_and_api.py::test_api_analytics_courses PASSED        [ 51%]
tests/test_pipeline_and_api.py::test_api_analytics_distribution PASSED   [ 55%]
tests/test_pipeline_and_api.py::test_api_analytics_performance_factors PASSED [ 58%]
tests/test_pipeline_and_api.py::test_api_analytics_correlations PASSED   [ 62%]
tests/test_pipeline_and_api.py::test_api_students_list_and_filter PASSED [ 65%]
tests/test_pipeline_and_api.py::test_api_student_detail PASSED           [ 68%]
tests/test_pipeline_and_api.py::test_api_ml_evaluation_and_predict PASSED [ 72%]
tests/test_pipeline_and_api.py::test_api_export_csv PASSED               [ 75%]
tests/test_pipeline_and_api.py::test_api_powerbi_spec PASSED             [ 79%]
backend/tests/test_api_endpoints.py::test_health_check PASSED            [ 82%]
backend/tests/test_api_endpoints.py::test_system_info PASSED             [ 86%]
backend/tests/test_api_endpoints.py::test_analytics_overview PASSED      [ 89%]
backend/tests/test_api_endpoints.py::test_students_pagination PASSED     [ 93%]
backend/tests/test_api_endpoints.py::test_predict_scenario_a PASSED      [ 96%]
backend/tests/test_api_endpoints.py::test_predict_scenario_c PASSED      [100%]
======================= 29 passed in 8.45s (100% pass rate) =======================
```

Frontend production build verification:
```text
✓ 2522 modules transformed.
✓ built in 728ms (0 TypeScript errors)
```

---

## 10. Cloud Deployment Readiness & Architectural Guide

DataPulse is architected for cloud native container environments (e.g. Render, Railway, AWS ECS, or Fly.io) paired with managed PostgreSQL (Supabase, Neon, AWS RDS):
- **Configuration**: Managed strictly via standard 12-factor environment variables (`DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS`).
- **Connection Security**: Enforces TLS (`sslmode=require`) on managed cloud database endpoints.
- **Reference Guide**: Full deployment topology and instructions are documented in [docs/deployment.md](docs/deployment.md).

> [!NOTE]
> **Deployment Scope**: The cloud deployment guidelines provided are reference specifications. Live cloud deployment was not executed on remote hosted infrastructure in this local environment; zero-downtime deployment properties are not claimed without live multi-zone cluster verification.

---

## 11. Author & Institutional Attribution

- **Author**: Mohamed
- **Role**: 2nd-Year Computer Engineering Student
- **Institution**: **Universiapolis International University of Agadir (UIA)**
- **Academic Year**: 2025 – 2026
- **License**: [MIT](LICENSE)
