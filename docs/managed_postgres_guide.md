# DataPulse — Managed PostgreSQL Setup & Verification Guide

This guide details how to provision, configure, migrate, and test DataPulse against a cloud-managed PostgreSQL 16 database (such as **Neon.tech**, **Supabase**, **Render PostgreSQL**, or **AWS RDS**).

---

## 1. Supported Managed PostgreSQL Providers

DataPulse requires standard PostgreSQL wire protocol compatibility (PostgreSQL 14, 15, or 16):

| Managed Cloud Provider | Recommended Use Case | Connection Protocol | Free Tier Available? |
| :--- | :--- | :--- | :--- |
| **Neon.tech** | Fast serverless branching, auto-suspend | `postgresql+psycopg2://...` with `sslmode=require` | Yes (0.5 GB, instant setup) |
| **Supabase** | Integrated Auth, real-time dashboard | `postgresql+psycopg2://...` with `sslmode=require` | Yes (500 MB database) |
| **Render PostgreSQL** | Simple containerized pairing | `postgresql+psycopg2://...` with `sslmode=require` | Yes (90-day free trial) |
| **AWS RDS / Aurora** | High-availability enterprise production | `postgresql+psycopg2://...` with `sslmode=require` | 12 months free tier (t3.micro) |

---

## 2. Step 1: Provision a Managed PostgreSQL Database

### Example: Neon.tech (Recommended for Instant Setup)
1. Sign up at [https://neon.tech](https://neon.tech).
2. Create a new project (e.g., `datapulse-production`).
3. Select PostgreSQL version **16** and your preferred cloud region (e.g., `eu-central-1` Frankfurt or `us-east-2` Ohio).
4. In the Neon Dashboard, copy the **Connection details** URI string. Ensure the **Pooled connection** or direct connection string includes `?sslmode=require`.

### Example: Supabase
1. Sign up at [https://supabase.com](https://supabase.com).
2. Create a new project (e.g., `datapulse-db`).
3. Set a strong database password and note it down.
4. Go to **Project Settings** $\rightarrow$ **Database** $\rightarrow$ **Connection Pooling** or **URI**.
5. Copy the connection URI:
   ```text
   postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?sslmode=require
   ```

---

## 3. Step 2: Configure Environment Variables in DataPulse

1. In the project root, open `.env` (or copy `.env.example` to `.env`).
2. Set `DATABASE_URL` and `TEST_DATABASE_URL` using the normalized driver prefix `postgresql+psycopg2://`:

```ini
# Main application connection string:
DATABASE_URL=postgresql+psycopg2://username:your_secure_cloud_password@ep-sample-12345.eu-central-1.aws.neon.tech/datapulse_db?sslmode=require

# Dedicated test connection string (enables live PostgreSQL tests):
TEST_DATABASE_URL=postgresql+psycopg2://username:your_secure_cloud_password@ep-sample-12345.eu-central-1.aws.neon.tech/datapulse_db?sslmode=require
```

> [!IMPORTANT]
> Always append `?sslmode=require` to enforce TLS encryption in transit across public internet connections.

---

## 4. Step 3: Run Alembic Schema Migrations

Apply deterministic schema migrations to create all 6 normalized tables, foreign keys, unique constraints, and indexes on your managed PostgreSQL database:

```powershell
# Activate local virtual environment
.\.venv\Scripts\Activate.ps1

# Run migrations up to latest head
alembic upgrade head
```

### Verification:
Inspect the current migration status:
```powershell
alembic current
# Output should display: 2c77fe5a8cf5 (head)
```

---

## 5. Step 4: Compile Analytical SQL Views

Compile the 5 production-grade SQL views directly on the cloud database:

```powershell
python scripts/init_db.py
```

**Expected output:**
```text
======================================================================
  DATAPULSE DATABASE INITIALIZATION
  Target Engine: postgresql+psycopg2://...
  Dialect:       postgresql
======================================================================
[Step 1/2] Creating relational tables registered with SQLAlchemy Base...
  * Relational tables created/verified successfully.

[Step 2/2] Compiling analytical SQL views...
  * Compiled 6 analytical SQL views successfully (postgresql dialect).
```

---

## 6. Step 5: Safe & Idempotent ETL Data Loading

Run the ETL pipeline to ingest the authentic UCI benchmark dataset:

```powershell
python -m etl.run
```

**Output:**
```text
[Phase 1/4: EXTRACT]
  * Extracted Mathematics: 395 records | Portuguese: 649 records
[Phase 2/4: VALIDATE (Multi-Pillar Institutional Scorecard)]
  * Audited Overall Score: 91.2/100 (PASSED)
[Phase 3/4: TRANSFORM (Entity Linkage & Feature Engineering)]
  * Resolved Unique Students:  674 individuals
  * Academic Enrollments:      1044 records
  * Intra-Course Collisions:   0 (Zero intra-course duplication verified)
[Phase 4/4: LOAD (Atomic & Idempotent Database Persistence)]
  * Relational tables populated & SQL views created successfully.
```

> [!NOTE]
> If `python -m etl.run` is run again, the **Production State Guard** automatically detects that 674 students and 1,044 enrollments exist and skips data re-ingestion, preserving all existing production modifications.

---

## 7. Step 6: Execute Dedicated PostgreSQL Integration Tests

Execute the dedicated PostgreSQL test suite to verify that schema, views, constraints, and data aggregations perform accurately on real PostgreSQL:

```powershell
pytest -v tests/test_postgres_integration.py
```

### Expected Output:
```text
tests/test_postgres_integration.py::test_postgres_live_connection_and_dialect PASSED [ 16%]
tests/test_postgres_integration.py::test_postgres_alembic_migrations PASSED          [ 33%]
tests/test_postgres_integration.py::test_postgres_views_compilation PASSED          [ 50%]
tests/test_postgres_integration.py::test_postgres_idempotent_etl_loading PASSED    [ 66%]
tests/test_postgres_integration.py::test_postgres_unique_constraint_enforcement PASSED [ 83%]
tests/test_postgres_integration.py::test_postgres_analytical_views_query PASSED    [100%]
============================== 6 passed in 4.25s ==============================
```

---

## 8. Step 7: Launch FastAPI Backend Against Managed PostgreSQL

Start the live backend server:

```powershell
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Verify backend health in a separate PowerShell window:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health"
# Status: UP, Database: HEALTHY, Dialect: postgresql
```

---

## 9. Security Best Practices Checklist

- [x] **SSL/TLS Encryption**: `sslmode=require` is present in connection strings.
- [x] **Connection Pooling**: Configured with `pool_size=10`, `max_overflow=20`, `pool_recycle=1800`, `pool_pre_ping=True` in `database/connection.py`.
- [x] **No Secrets in Git**: `.env` is excluded in `.gitignore`.
- [x] **Least Privilege Roles**: Create a dedicated runtime application user (`datapulse_app`) with `SELECT`, `INSERT`, `UPDATE`, `DELETE` grants only, reserving administrative owner credentials for migrations.
