# DataPulse — Production Deployment Guide

DataPulse is built for cloud and containerized production environments.

---

## 1. Local Container Deployment (Docker Compose)

The easiest way to run the full production stack locally with PostgreSQL, FastAPI backend, and React Nginx frontend:

```bash
cd DataPulse
docker compose up --build
```

### Services Started:
- **PostgreSQL 16**: Port `5432` with persistent data volume `postgres_data`.
- **FastAPI Backend**: Port `8000` (auto-initializes schema, runs pipeline, and serves REST API).
- **React Frontend (Nginx)**: Port `3000` (serves compiled static assets and proxies `/api/` to backend).

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
