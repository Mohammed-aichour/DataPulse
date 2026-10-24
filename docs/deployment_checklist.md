# DataPulse — Production Deployment Checklist

This checklist provides a structured, verification-driven protocol for deploying the DataPulse platform to production environments (FastAPI backend + React Vite frontend + PostgreSQL database).

> [!WARNING]
> Do not trigger production deployments, migrate production databases, or expose external endpoints without explicit authorization.

---

## 1. Pre-Deployment Configuration & Security Gate

- [ ] **Secret Isolation**:
  - [ ] `POSTGRES_PASSWORD` is a 24+ character cryptographically random string (e.g. generated via `python -c "import secrets; print(secrets.token_hex(16))"`).
  - [ ] `JWT_SECRET` is a 256-bit cryptographically secure key (e.g. generated via `openssl rand -hex 32`).
  - [ ] Verified that active `.env` file is excluded from Git repository (`git status` shows clean).
  - [ ] In cloud environments, secrets are configured strictly via the cloud provider's Secret Manager (e.g., Render Environment Groups, AWS Secrets Manager, Doppler), never hardcoded.
- [ ] **Database Connection Security**:
  - [ ] Connection string explicitly enforces TLS in transit: `?sslmode=require`.
  - [ ] Standardized driver prefix used: `postgresql+psycopg2://`.
  - [ ] Dedicated test database separated from production: `TEST_DATABASE_URL` targets `datapulse_test` rather than production database.
- [ ] **CORS Configuration**:
  - [ ] In `backend/app/core/config.py`, `CORS_ORIGINS` is restricted to authorized production client domains (e.g. `["https://datapulse.vercel.app"]`), removing wildcards or unauthorized localhost ports in production.
- [ ] **Client-Side Credential Audit**:
  - [ ] Verified that `frontend/dist/` contains zero database credentials, private API secrets, or server tokens.
  - [ ] `VITE_API_URL` points to production API domain or relative `/api` behind reverse proxy.

---

## 2. Database Infrastructure Deployment Gate

- [ ] **Managed PostgreSQL Provisioning**:
  - [ ] Provisioned PostgreSQL 15/16 instance (Neon.tech, Supabase, Render, or AWS RDS).
  - [ ] Verified server connectivity with TLS: `psql "$DATABASE_URL" -c "SELECT version();"`.
- [ ] **Alembic Schema Migrations**:
  - [ ] Run migration command: `alembic upgrade head`.
  - [ ] Verify migration version: `alembic current` confirms `2c77fe5a8cf5 (head)`.
  - [ ] Verify that all 6 tables exist: `students`, `courses`, `academic_records`, `pipeline_executions`, `prediction_logs`, `data_imports`.
  - [ ] Confirm constraint: `uq_student_course` unique constraint is active on `academic_records`.
- [ ] **Analytical Views Compilation**:
  - [ ] Run compilation script: `python scripts/init_db.py`.
  - [ ] Confirm all 5 SQL views compiled: `v_student_overview`, `v_course_performance`, `v_risk_analysis`, `v_absence_impact`, `v_performance_distribution`.
- [ ] **Baseline Data Ingestion**:
  - [ ] Execute idempotent ETL pipeline: `python -m etl.run`.
  - [ ] Confirm record counts: exactly 674 derived student keys, 2 courses (`MAT`, `POR`), 1,044 academic enrollments.
  - [ ] Confirm zero intra-course duplicate collisions.

---

## 3. Backend Deployment Gate (FastAPI / Uvicorn Container)

- [ ] **Container Build**:
  - [ ] Build production image: `docker build -t datapulse-backend:latest .`.
  - [ ] Confirm healthcheck utility (`curl`) is installed in container.
- [ ] **Runtime Environment**:
  - [ ] Set `DATABASE_URL` with connection pooling parameters:
    - `DB_POOL_SIZE=10`
    - `DB_MAX_OVERFLOW=20`
    - `DB_POOL_RECYCLE=1800`
    - `DB_POOL_TIMEOUT=30`
  - [ ] Set `DEBUG=false`.
- [ ] **Health Endpoint Verification**:
  - [ ] Query `/api/health`: Verify HTTP 200 with `status: "UP"`, `database: "HEALTHY"`, `ml_models: "READY"`.
  - [ ] Confirm error responses are sanitized and never leak database hostnames or usernames.

---

## 4. Frontend Deployment Gate (React 19 / TypeScript / Vite)

- [ ] **Production Build**:
  - [ ] Execute compilation: `cd frontend && npm run build`.
  - [ ] Confirm `tsc -b` completes with 0 errors.
  - [ ] Confirm `vite build` completes with assets generated in `dist/`.
- [ ] **Routing & Nginx Proxy**:
  - [ ] Verify `nginx.conf` proxies `/api/` to backend service port.
  - [ ] Confirm SPA client-side routing fallback: `try_files $uri $uri/ /index.html;`.
- [ ] **Deployment**:
  - [ ] Deploy static assets to host (Vercel, Netlify, Cloudflare Pages, or container Nginx).
  - [ ] Verify all UI routes load correctly: `/`, `/students`, `/analytics`, `/ml`, `/data`, `/settings`.

---

## 5. Post-Deployment Smoke Test & Verification Protocol

- [ ] **Executive Dashboard**:
  - [ ] KPIs display correctly: Total Students = 674, Total Enrollments = 1,044, Pass Rate = 78.0%, Academic Risk = 22.0%.
- [ ] **Student Directory**:
  - [ ] Pagination functions smoothly (page size 10/25/50).
  - [ ] Search and risk filters return accurate filtered counts.
  - [ ] Student profile modal opens displaying period marks ($G1, G2, G3$) and calculated indicators.
- [ ] **Interactive Analytics**:
  - [ ] Grade distribution charts render accurately.
  - [ ] Factor analysis and correlation heatmaps display computed Pearson coefficients.
- [ ] **Machine Learning Simulator**:
  - [ ] Scenario A (Intake): Simulates risk probability without target leakage ($G1, G2$ excluded).
  - [ ] Scenario C (Late-Stage): Simulates final grade prediction with $G1, G2$ included.
- [ ] **Export & BI**:
  - [ ] CSV download endpoints (`/api/export/csv/{dataset}`) generate valid CSV streams.
  - [ ] Power BI JSON schema specification endpoint (`/api/export/powerbi-spec`) returns 200.

---

## 6. Rollback & Disaster Recovery Plan

- [ ] **Schema Rollback**:
  - [ ] Step back 1 migration: `alembic downgrade -1`.
  - [ ] Complete rollback to base: `alembic downgrade base`.
- [ ] **Database Restoration**:
  - [ ] Restore latest compressed backup: `pg_restore -h $DB_HOST -U $DB_USER -d $DB_NAME -v backup_latest.dump`.
- [ ] **Backend Container Rollback**:
  - [ ] Re-tag and deploy previous stable container image hash.
