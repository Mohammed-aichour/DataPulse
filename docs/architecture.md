# DataPulse — Architecture & System Design Documentation

DataPulse is an enterprise-grade university analytics and predictive intelligence platform designed to ingest educational datasets, validate schema conformance, store normalized entities in relational storage, compute descriptive KPIs, and execute real-time machine learning predictions for academic student risk.

---

## 1. System Architecture Diagram

```mermaid
flowchart TD
    subgraph DataSources["Data Sources & Ingestion"]
        UCI["UCI ML Repository (Dataset #320)"] --> DL["DatasetLoader (SHA-256 Verified)"]
        DL --> RAW["Raw Storage (student-mat.csv, student-por.csv)"]
    end

    subgraph DataEngineering["Data Engineering Pipeline"]
        RAW --> VAL["DataValidator (Multi-Pillar QA & Outlier Engine)"]
        VAL --> REP["Quality Report (JSON / Markdown)"]
        VAL --> TR["EducationalTransformer (1-to-1 Linkage: 674 Students / 1,044 Records)"]
        TR --> PROCESSED["Clean Relational Datasets (Students, Courses, Records)"]
        PROCESSED --> DBL["DatabaseLoader (SQLAlchemy Session & Atomic Transactions)"]
    end

    subgraph Storage["Storage & Analytics Layer"]
        DBL --> DB[(PostgreSQL 16 / SQLite)]
        DB --> VIEWS["Analytical SQL Views (v_student_overview, v_course_perf, v_absence_impact)"]
        VIEWS --> POWERBI["Power BI / CSV Direct Query Stream"]
    end

    subgraph MachineLearning["3-Horizon Machine Learning Engine"]
        PROCESSED --> TRAIN["ModelTrainer (Scikit-Learn Multi-Scenario Pipeline)"]
        TRAIN --> BEST_M["Model Artifacts (.joblib & model_metadata.json)"]
        BEST_M --> PRED["PredictorService (Multi-Scenario Inference & Explainability)"]
    end

    subgraph BackendAPI["FastAPI REST API"]
        DB --> API["FastAPI Application"]
        PRED --> API
        API --> EP1["GET /api/analytics/*"]
        API --> EP2["GET /api/students/*"]
        API --> EP3["POST /api/ml/predict (Multi-Scenario)"]
        API --> EP4["POST /api/pipeline/run"]
        API --> EP5["GET /api/export/*"]
    end

    subgraph FrontendApp["Frontend User Interface"]
        API --> REACT["React 19 + TypeScript + Vite"]
        REACT --> DASH["Executive Dashboard"]
        REACT --> STU["Student Directory & Profiles"]
        REACT --> AN["Factor Analytics & Correlation"]
        REACT --> ML_UI["Multi-Horizon Risk Simulation"]
        REACT --> ETL_UI["ETL Orchestration & Quality Logs"]
    end
```

---

## 2. Component Architecture

### 2.1 Ingestion & Extraction Layer (`src/ingestion/`)
- Downloads authentic educational data directly from the UCI Machine Learning repository.
- Computes cryptographic SHA-256 hashes to guarantee data provenance.
- Provides a reproducible synthetic generation fallback when external networks are unavailable.

### 2.2 Preprocessing & Multi-Pillar Validation Layer (`src/preprocessing/validator.py`)
- Enforces strict Pydantic v2 schemas across 33 academic and demographic variables.
- Detects domain mismatches, missing values, duplicates, and statistical outliers using the Interquartile Range (IQR).
- Calculates institutional Data Quality Scores across 5 pillars: Completeness, Validity, Key Integrity, Outlier Regularity, and Granularity (Overall score: **91.2 / 100**).

### 2.3 Feature Engineering Layer (`src/preprocessing/transformer.py`)
- Resolves student entities across multi-course enrollments via **1-to-1 occurrence-ranked linkage (`cumcount()`)**, completely eliminating intra-course duplicate collisions.
- Resolves **674 unique students** and preserves **1,044 enrollment records** as first-class entities.
- Computes composite features: `parent_edu_avg`, `study_to_social_ratio`, `alcohol_index`, `grade_delta`, and `academic_risk`.

### 2.4 3-Horizon Machine Learning Pipeline (`src/ml/`)
- Eliminates target leakage by training and benchmarking models across three distinct time horizons:
  - **Scenario A**: Early Intake Warning (Pre-Grades) — uses only intake demographics and behavioral factors (ROC-AUC: 0.818).
  - **Scenario B**: Mid-Term Evaluation (Post-Period 1 with G1) (ROC-AUC: 0.931).
  - **Scenario C**: Late-Stage Forecasting (Post-Period 2 with G1 and G2) (ROC-AUC: 0.971, MAE: 0.76 pts).
- Evaluates models using Stratified 5-Fold Cross Validation.
- Persists serialised artifacts using `joblib`.

### 2.5 REST API Backend (`backend/app/`)
- High-throughput asynchronous FastAPI framework.
- CORS middleware with strict allowed origins, automatic OpenAPI / Swagger specifications, structured exception handling, and database session lifecycles.

### 2.6 Frontend Platform (`frontend/`)
- Modern enterprise SaaS aesthetic built with React 19, Vite, TypeScript, Tailwind CSS, and Recharts.
- Multi-horizon risk simulation engine, live analytics charts, and student directory with filtering and pagination.
