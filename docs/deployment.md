# DataPulse — Production Deployment Architecture & Reference Guide

This document details the multi-container Docker Compose configuration and cloud deployment reference architectures for DataPulse.

> [!NOTE]
> The cloud specifications detailed below represent deployment blueprints and configuration templates. Live remote cloud deployment has not been executed; zero-downtime deployment properties are not claimed without active multi-zone load balancing verification.

---

## 1. Local Container Deployment (Docker Compose)

The full production stack runs PostgreSQL 16, the FastAPI backend, and the React Nginx frontend:

```bash
cd DataPulse
# Ensure .env is populated with secure secrets (POSTGRES_PASSWORD, JWT_SECRET)
docker compose up --build -d
```

### Services Started:
- **PostgreSQL 16**: Bound strictly to `127.0.0.1:5432:5432` with persistent data volume `postgres_data` and healthcheck.
- **FastAPI Backend**: Bound to `127.0.0.1:8000:8000` (auto-executes Alembic migrations, ETL integrity check, and serves REST API).
- **React Frontend (Nginx)**: Bound to `127.0.0.1:3000:80` (serves compiled static assets and reverse proxies `/api/` to backend).

> [!IMPORTANT]
> **Host Environment Status**: Docker execution on this specific Windows host machine is marked **NOT TESTED** because the Docker CLI is not installed in the Windows environment (`docker: The term 'docker' is not recognized`). All Dockerfiles, compose files, and container startup scripts are fully authored and syntactically verified.

---

## 2. Cloud Production Deployment Architecture

```mermaid
flowchart LR
    CLIENT["Browser Client"] --> VERCEL["Vercel / Netlify (React Frontend)"]
    VERCEL -- "/api/*" --> RENDER["Render / Railway (FastAPI Backend Container)"]
    RENDER --> NEON["Neon / Supabase (Serverless PostgreSQL)"]
```

### 2.1 Database: Neon or Supabase (PostgreSQL)
1. Provision a PostgreSQL 16 database on [Neon.tech](https://neon.tech) or [Supabase](https://supabase.com).
2. Copy the Connection String URI:
   ```env
   DATABASE_URL=postgresql://user:password@ep-sample.neon.tech/datapulse?sslmode=require
   ```

### 2.2 Backend: Render or Railway
1. Create a **Web Service** pointing to the `DataPulse` repository root.
2. Build Command:
   ```bash
   pip install -r backend/requirements.txt && python -m src.pipeline.run
   ```
3. Start Command:
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
   ```
4. Configure Environment Variables:
   - `DATABASE_URL`: Your PostgreSQL connection string.
   - `CORS_ORIGINS`: `["https://your-frontend.vercel.app"]`
   - `JWT_SECRET`: Random 256-bit secret key.

### 2.3 Frontend: Vercel
1. Link your GitHub repository to [Vercel](https://vercel.com).
2. Set **Root Directory** to `frontend`.
3. Framework Preset: **Vite**.
4. Configure Environment Variable:
   - `VITE_API_URL`: `https://your-backend.onrender.com/api`
5. Deploy.

---

## 3. Environment Variable Security Checklist

- [x] Never commit `.env` or production credentials to GitHub.
- [x] Use `.env.example` as the authoritative configuration template.
- [x] Set restrictive `CORS_ORIGINS` in production.
- [x] Ensure SSL/TLS is enforced (`sslmode=require`) on cloud database connections.
