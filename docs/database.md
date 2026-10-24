# DataPulse — Relational Database Architecture & Integration Guide

This document details the relational database design, schema validation, migration workflow, analytical SQL views, connection pooling, security, and cloud deployment procedures for the **DataPulse — Smart Campus Analytics & Predictive Intelligence Platform**.

---

## 1. Entity-Relationship (ER) Architecture

The DataPulse database implements a normalized Third Normal Form (3NF) relational architecture separating individual student demographics from multi-course academic enrollments, pipeline execution audits, inference telemetry, and data ingestion provenance.

```mermaid
erDiagram
    STUDENTS ||--o{ ACADEMIC_RECORDS : "enrolls in (1:N)"
    COURSES ||--o{ ACADEMIC_RECORDS : "contains (1:N)"
    PIPELINE_EXECUTIONS ||--o{ DATA_IMPORTS : "audits"

    STUDENTS {
        int id PK
        string student_id UK "STU-0001 to STU-0674"
        string school "GP or MS"
        string sex "F or M"
        int age "15-22"
        string address "U or R"
        string famsize "LE3 or GT3"
        string pstatus "T or A"
        int medu "0-4 (Mother Education)"
        int fedu "0-4 (Father Education)"
        string mjob "Mother Job"
        string fjob "Father Job"
        string reason "School choice reason"
        string guardian "mother, father, other"
        string nursery "yes or no"
        string internet "yes or no"
        datetime created_at
    }

    COURSES {
        int id PK
        string course_code UK "MAT or POR"
        string course_name "Mathematics or Portuguese"
        string department "STEM or Humanities"
        int credits "6"
        string semester "Full Year"
    }

    ACADEMIC_RECORDS {
        int id PK
        string record_id UK "REC-00001 to REC-01044"
        string student_id FK "References students.student_id"
        int course_id FK "References courses.id"
        string course_code "MAT or POR"
        int traveltime "1-4"
        int studytime "1-4"
        int failures "0-4 past class failures"
        string schoolsup "yes or no"
        string famsup "yes or no"
        string paid "yes or no"
        string activities "yes or no"
        string higher "yes or no"
        string romantic "yes or no"
        int famrel "1-5 family relationship quality"
        int freetime "1-5 free time after school"
        int goout "1-5 going out with friends"
        int dalc "1-5 workday alcohol consumption"
        int walc "1-5 weekend alcohol consumption"
        int health "1-5 current health status"
        int absences "0-93 class absences"
        int g1 "0-20 First period grade"
        int g2 "0-20 Second period grade"
        int g3 "0-20 Final grade (Target)"
        float parent_edu_avg "Engineered: (Medu + Fedu) / 2"
        float alcohol_index "Engineered: (Dalc * 5 + Walc * 2) / 7"
        float study_to_social_ratio "Engineered: studytime / (goout + freetime)"
        int grade_delta "Engineered: G2 - G1"
        int academic_risk "1 if G3 < 10 else 0"
        bool passing_status "True if G3 >= 10"
        string performance_tier "Needs Support, Satisfactory, Good, Excellent"
        datetime created_at
    }

    PIPELINE_EXECUTIONS {
        int id PK
        datetime run_timestamp
        int records_processed
        float duration_seconds
        string status "SUCCESS or FAILED"
        float quality_score "0.0 - 100.0"
        text details_json
    }

    PREDICTION_LOGS {
        int id PK
        datetime timestamp
        string course "MAT or POR"
        text features_json
        float predicted_grade "0.0 - 20.0"
        int predicted_risk "0 or 1"
        float risk_probability "0.0 - 1.0"
        string model_name
        string model_version
    }

    DATA_IMPORTS {
        int id PK
        string source_name
        string file_name
        int row_count
        string checksum "SHA-256 integrity hash"
        datetime imported_at
        bool is_synthetic
        string status
    }
```

---

## 2. Table Specifications & Constraints

### 2.1 Core Relational Schema

| Table Name | Primary Key | Foreign Keys | Unique Constraints | Primary Indexes | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `students` | `id` (SERIAL / INTEGER) | None | `student_id` | `ix_students_student_id` | Student demographic entity registry (674 derived cross-course student keys based on demographic matching and occurrence ordering). |
| `courses` | `id` (SERIAL / INTEGER) | None | `course_code` | `ix_courses_course_code` | Academic catalog registry (`MAT`, `POR`). |
| `academic_records` | `id` (SERIAL / INTEGER) | `student_id` $\rightarrow$ `students.student_id`<br>`course_id` $\rightarrow$ `courses.id` | `record_id`<br>`uq_student_course (student_id, course_id)` | `ix_academic_records_record_id`<br>`ix_academic_records_student_id`<br>`ix_academic_records_course_id`<br>`ix_academic_records_academic_risk`<br>`ix_student_course` | Individual course enrollments (1,044 records) with academic marks and engineered risk factors. |
| `pipeline_executions` | `id` (SERIAL / INTEGER) | None | None | `ix_pipeline_executions_run_timestamp` | Audit log for ETL execution cycles, durations, and multi-pillar quality scores. |
| `prediction_logs` | `id` (SERIAL / INTEGER) | None | None | `ix_prediction_logs_timestamp` | In-flight telemetry for inference requests, tracking model inputs and drift. |
| `data_imports` | `id` (SERIAL / INTEGER) | None | None | `ix_data_imports_source_name` | Provenance tracking for raw dataset ingestion and SHA-256 verification. |

### 2.2 Cross-Course Entity Linkage Assumption & Limitations

The student entities stored in the `students` table (`STU-0001` through `STU-0674`) were derived by joining the Mathematics (`395` rows) and Portuguese (`649` rows) files using demographic matching and occurrence ordering (`cumcount()`):
- **Absence of Ground-Truth Identifiers**: The raw benchmark dataset from the UCI Machine Learning Repository does not contain authoritative student IDs or civil registration numbers.
- **Linkage Heuristic**: 13 demographic variables (`school`, `sex`, `age`, `address`, `famsize`, `Pstatus`, `Medu`, `Fedu`, `Mjob`, `Fjob`, `reason`, `nursery`, `internet`) were matched across courses. Because 16 pairs of students share identical demographic profiles within the same class, an occurrence-ranked linkage assumption was applied to eliminate cartesian product expansion.
- **Data Integrity Reality**: These 674 records represent **derived cross-course entity keys under the stated linkage assumptions**, NOT 674 independently verified physical human identities. True individual identity cannot be established without administrative institutional data.

### 2.3 Relational Integrity & The Unique Enrollment Constraint

To guarantee that a student cannot be inadvertently enrolled multiple times in the same course, `academic_records` enforces a strict compound unique constraint:

```sql
CONSTRAINT uq_student_course UNIQUE (student_id, course_id);
```

- In SQLAlchemy: `UniqueConstraint("student_id", "course_id", name="uq_student_course")` in `database/models.py`.
- Enforced at both the database engine level (PostgreSQL / SQLite) and application level (idempotent upsert in `src/pipeline/db_loader.py`).

---

## 3. Analytical SQL Views

DataPulse pre-compiles 5 production-grade SQL views directly into the database engine. These views decouple complex business aggregations from the application tier, enabling sub-millisecond API response times and direct compatibility with Business Intelligence tools (e.g., Power BI, Metabase).

### 3.1 `v_student_overview`
Denormalized analytical view joining demographics, course information, and academic performance metrics.

```sql
CREATE VIEW v_student_overview AS
SELECT 
    s.student_id,
    s.school,
    s.sex,
    s.age,
    s.address,
    s.famsize,
    s.pstatus,
    s.medu,
    s.fedu,
    s.mjob,
    s.fjob,
    s.reason,
    s.guardian,
    s.internet,
    ar.record_id,
    c.course_code,
    c.course_name,
    ar.studytime,
    ar.failures,
    ar.schoolsup,
    ar.famsup,
    ar.paid,
    ar.activities,
    ar.higher,
    ar.romantic,
    ar.famrel,
    ar.freetime,
    ar.goout,
    ar.dalc,
    ar.walc,
    ar.health,
    ar.absences,
    ar.g1,
    ar.g2,
    ar.g3,
    ar.parent_edu_avg,
    ar.alcohol_index,
    ar.study_to_social_ratio,
    ar.grade_delta,
    ar.academic_risk,
    ar.passing_status,
    ar.performance_tier
FROM students s
JOIN academic_records ar ON s.student_id = ar.student_id
JOIN courses c ON ar.course_id = c.id;
```

### 3.2 `v_course_performance`
Cross-departmental performance comparison aggregating enrollment count, grade metrics, pass rate, and average absenteeism.

```sql
CREATE VIEW v_course_performance AS
SELECT 
    c.course_code,
    c.course_name,
    COUNT(ar.id) AS total_enrolled,
    ROUND(AVG(ar.g1), 2) AS avg_g1,
    ROUND(AVG(ar.g2), 2) AS avg_g2,
    ROUND(AVG(ar.g3), 2) AS avg_g3,
    ROUND(AVG(ar.absences), 2) AS avg_absences,
    SUM(CASE WHEN ar.passing_status = 1 THEN 1 ELSE 0 END) AS passing_students,
    ROUND(CAST(SUM(CASE WHEN ar.passing_status = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(ar.id) * 100, 2) AS pass_rate,
    SUM(ar.academic_risk) AS at_risk_count
FROM courses c
JOIN academic_records ar ON c.id = ar.course_id
GROUP BY c.course_code, c.course_name;
```

### 3.3 `v_risk_analysis`
Correlates academic risk levels ($G3 < 10$) with behavioral risk indicators (past failures, high alcohol consumption, insufficient study time).

```sql
CREATE VIEW v_risk_analysis AS
SELECT 
    ar.academic_risk,
    CASE WHEN ar.academic_risk = 1 THEN 'At Risk (G3 < 10)' ELSE 'In Good Standing (G3 >= 10)' END AS risk_label,
    COUNT(ar.id) AS student_count,
    ROUND(AVG(ar.failures), 2) AS avg_prior_failures,
    ROUND(AVG(ar.studytime), 2) AS avg_study_time,
    ROUND(AVG(ar.absences), 2) AS avg_absences,
    ROUND(AVG(ar.alcohol_index), 2) AS avg_alcohol_index,
    ROUND(AVG(ar.study_to_social_ratio), 2) AS avg_study_social_ratio
FROM academic_records ar
GROUP BY ar.academic_risk;
```

### 3.4 `v_absence_impact`
Binned absenteeism impact analysis demonstrating the empirical relationship between missed classes and final grade deterioration.

```sql
CREATE VIEW v_absence_impact AS
SELECT 
    CASE 
        WHEN absences = 0 THEN '0 absences'
        WHEN absences BETWEEN 1 AND 4 THEN '1-4 absences'
        WHEN absences BETWEEN 5 AND 9 THEN '5-9 absences'
        WHEN absences BETWEEN 10 AND 19 THEN '10-19 absences'
        ELSE '20+ absences'
    END AS absence_tier,
    COUNT(id) AS student_count,
    ROUND(AVG(g3), 2) AS avg_final_grade,
    ROUND(AVG(academic_risk) * 100, 2) AS risk_rate_pct
FROM academic_records
GROUP BY 
    CASE 
        WHEN absences = 0 THEN '0 absences'
        WHEN absences BETWEEN 1 AND 4 THEN '1-4 absences'
        WHEN absences BETWEEN 5 AND 9 THEN '5-9 absences'
        WHEN absences BETWEEN 10 AND 19 THEN '10-19 absences'
        ELSE '20+ absences'
    END;
```

### 3.5 `v_performance_distribution`
Distributes student outcomes across the four institutional grade tiers (*Needs Support*, *Satisfactory*, *Good*, *Excellent*).

```sql
CREATE VIEW v_performance_distribution AS
SELECT 
    performance_tier,
    COUNT(id) AS student_count,
    ROUND(CAST(COUNT(id) AS FLOAT) / (SELECT COUNT(*) FROM academic_records) * 100, 2) AS percentage,
    ROUND(AVG(g3), 2) AS avg_grade
FROM academic_records
GROUP BY performance_tier;
```

---

## 4. Alembic Migration Workflow

DataPulse utilizes **Alembic** for deterministic, version-controlled database schema management.

### 4.1 Migration File Hierarchy
```text
database/
├── alembic.ini                              # Alembic configuration root
├── connection.py                            # SQLAlchemy engine & session factory
├── models.py                                # Declarative ORM models (3NF)
└── migrations/
    ├── env.py                               # Dynamic DB connection & target metadata
    ├── script.py.mako                       # Template for new revision files
    └── versions/
        └── 2c77fe5a8cf5_create_initial_tables.py  # Production migration revision
```

### 4.2 Migration Commands

```bash
# Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Check current database revision status
alembic current

# Apply all pending migrations up to latest head
alembic upgrade head

# Rollback one migration revision
alembic downgrade -1

# Rollback completely to empty schema
alembic downgrade base

# Generate a new auto-detected migration after modifying models.py
alembic revision --autogenerate -m "add_new_indicator_field"

# Inspect detailed revision history
alembic history --verbose
```

---

## 5. Database Connection & Connection Pooling

The connection layer (`database/connection.py`) dynamically adapts to both production-grade PostgreSQL engines and local SQLite environments with strict connection pooling:

```python
# PostgreSQL Production Pooling Configuration:
engine = create_engine(
    url,
    pool_size=10,          # Standard pool size of active connections
    max_overflow=20,       # Burst limit for high-concurrency requests
    pool_recycle=1800,     # Recycle connections every 30 minutes to prevent stale sockets
    pool_timeout=30,       # 30-second timeout before raising connection timeout error
    pool_pre_ping=True     # Test connection liveness before checkout to prevent dead sockets
)
```

### 5.1 Environment Configuration (`.env`)

```ini
# PostgreSQL (Docker or Managed Cloud Service):
DATABASE_URL=postgresql+psycopg2://postgres:postgres_secure_pass_2026@127.0.0.1:5432/datapulse_db

# SQLite (Local Embedded Development Fallback):
DATABASE_URL=sqlite:///./datapulse.db
```

### 5.2 Session Lifecycle & Error Handling

FastAPI endpoints consume database sessions via a dependency-injected generator pattern (`get_db()`):

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- If an unhandled exception or database unreachable condition occurs, transactions are rolled back and sessions closed immediately to prevent connection pool exhaustion.
- The API intercepts database connection errors and returns a structured JSON `503 Service Unavailable` response without leaking internal database credentials or stack traces.

---

## 6. Docker Compose Orchestration

The platform includes a containerized multi-service architecture with persistent data storage:

```yaml
services:
  db:
    image: postgres:16-alpine
    container_name: datapulse_db
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres_secure_pass_2026}
      POSTGRES_DB: ${POSTGRES_DB:-datapulse_db}
    ports:
      - "127.0.0.1:5432:5432"  # Bound to loopback only for network security
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-datapulse_db}"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
    driver: local
```

### Local Docker Commands:
```bash
# Start PostgreSQL container in background
docker compose up -d db

# Inspect container healthcheck status
docker compose ps

# Inspect PostgreSQL logs
docker compose logs db

# Run automated database migrations inside container
docker compose exec backend alembic upgrade head

# Run ETL loading inside container
docker compose exec backend python -m etl.run
```

---

## 7. Backup and Disaster Recovery

### 7.1 PostgreSQL Backup Procedure
```bash
# Create custom-format compressed backup (.dump)
pg_dump -h 127.0.0.1 -p 5432 -U postgres -d datapulse_db -F c -b -v -f "datapulse_backup_$(date +%Y%m%d_%H%M%S).dump"

# Create plain-text SQL script backup (.sql)
pg_dump -h 127.0.0.1 -p 5432 -U postgres -d datapulse_db --clean --if-exists -f "datapulse_backup.sql"
```

### 7.2 PostgreSQL Restore Procedure
```bash
# Drop and recreate database prior to restore if needed
dropdb -h 127.0.0.1 -U postgres datapulse_db
createdb -h 127.0.0.1 -U postgres datapulse_db

# Restore from compressed archive
pg_restore -h 127.0.0.1 -p 5432 -U postgres -d datapulse_db -v "datapulse_backup_20261023.dump"
```

### 7.3 SQLite Backup Procedure
```bash
# Atomic online backup using SQLite CLI
sqlite3 datapulse.db ".backup 'datapulse_backup_$(date +%Y%m%d_%H%M%S).db'"
```

---

## 8. Managed Cloud Database Architecture & Configuration Guide

DataPulse is architected for PostgreSQL wire compatibility with leading managed PostgreSQL providers. 

> [!NOTE]
> The configurations below are architectural reference specifications. DataPulse has not been provisioned on live cloud infrastructure; no zero-downtime deployment properties are claimed without active multi-region cluster testing.
> For the comprehensive provisioning and connection guide, refer to: [docs/managed_postgres_guide.md](managed_postgres_guide.md).
> For local Windows Docker Desktop setup, refer to: [docs/windows_docker_setup.md](windows_docker_setup.md).

### 8.1 Recommended Cloud Providers

| Provider | Tier | Features | Connection String Format |
| :--- | :--- | :--- | :--- |
| **Neon.tech** | Serverless PostgreSQL 16 | Instant branching, auto-suspend, connection pooling | `postgresql+psycopg2://user:pass@ep-cool-fog.us-east-2.aws.neon.tech/datapulse?sslmode=require` |
| **Supabase** | Managed PostgreSQL 15/16 | Integrated auth, pgvector, daily backups | `postgresql+psycopg2://postgres:pass@db.projectref.supabase.co:5432/postgres?sslmode=require` |
| **Render PostgreSQL** | Managed Container | Zero-setup, automated SSL, automated daily backups | `postgresql+psycopg2://user:pass@dpg-xxxx.oregon-postgres.render.com/datapulse?sslmode=require` |
| **AWS RDS / Aurora** | Enterprise Cloud | Multi-AZ replication, automated point-in-time recovery | `postgresql+psycopg2://admin:pass@datapulse.cluster-xxxx.rds.amazonaws.com:5432/datapulse?sslmode=require` |

### 8.2 Production Security Checklist
1. **Enforce SSL/TLS**: Always append `?sslmode=require` to production connection strings.
2. **Connection Pooling**: Use transaction-level connection pooling (e.g., PgBouncer or Supabase port `6543`) when scaling serverless compute or container replicas.
3. **Least Privilege Principle**: Create a dedicated runtime user for the FastAPI application with `SELECT`, `INSERT`, `UPDATE`, `DELETE` grants only, reserving superuser credentials for migrations.
4. **Credential Isolation**: Store database passwords exclusively in cloud secrets managers (e.g., AWS Secrets Manager, Doppler, or Render Secret Groups) — never commit `.env` to source control.
