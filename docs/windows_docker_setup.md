# DataPulse — Windows 11 Docker Desktop Setup & Verification Guide

This guide provides step-by-step instructions to install Docker Desktop on Windows 11, configure WSL 2, start the containerized DataPulse architecture (PostgreSQL 16, FastAPI backend, React Nginx frontend), and verify PostgreSQL persistence and health.

---

## 1. Prerequisites for Windows 11

Ensure your machine meets the hardware and operating system requirements:
- **Operating System**: Windows 11 64-bit (Home, Pro, Enterprise, or Education).
- **CPU Virtualization**: Enabled in your motherboard BIOS/UEFI (Intel VT-x or AMD-V).
- **RAM**: Minimum 8 GB (16 GB recommended).

To verify CPU virtualization in Windows:
1. Press `Ctrl + Shift + Esc` to open **Task Manager**.
2. Click the **Performance** tab, then select **CPU**.
3. Verify that **Virtualization: Enabled** is displayed at the bottom right.

---

## 2. Step 1: Install WSL 2 (Windows Subsystem for Linux)

Docker Desktop on Windows 11 achieves optimal performance using the WSL 2 backend.

1. Open **PowerShell as Administrator** (Right-click Start menu $\rightarrow$ *Terminal (Admin)* or *PowerShell (Admin)*).
2. Run the WSL installation command:
   ```powershell
   wsl --install
   ```
3. If WSL is already partially installed, update the WSL kernel:
   ```powershell
   wsl --update
   ```
4. **Restart your computer** when prompted by Windows to finalize hypervisor feature activation.

---

## 3. Step 2: Install Docker Desktop for Windows

1. Download the official installer from Docker:
   - [https://docs.docker.com/desktop/setup/install/windows-install/](https://docs.docker.com/desktop/setup/install/windows-install/)
2. Run `Docker Desktop Installer.exe`.
3. In the configuration dialog, ensure the **Use WSL 2 instead of Hyper-V (recommended)** checkbox is selected.
4. Complete the installation and click **Close and restart** if prompted.
5. Launch **Docker Desktop** from the Windows Start menu.
6. Accept the Docker Service Agreement. Wait until the whale icon in the bottom-left turns green with **Engine running**.

---

## 4. Step 3: Verify Docker CLI in PowerShell

Open a new PowerShell terminal and verify that both `docker` and `docker compose` are recognized:

```powershell
docker --version
# Expected output: Docker version 26.x or newer

docker compose version
# Expected output: Docker Compose version v2.27 or newer
```

---

## 5. Step 4: Configure Strong Secrets in DataPulse

Before launching containers, DataPulse requires strong secrets to be configured in your `.env` file.

1. Navigate to your project folder:
   ```powershell
   cd "D:\Desktop\Downloads\Project linked in\DataPulse"
   ```
2. Copy the environment template:
   ```powershell
   Copy-Item .env.example .env
   ```
3. Open `.env` in an editor and replace placeholder credentials:
   ```ini
   # Set a strong, unique PostgreSQL password:
   POSTGRES_USER=datapulse_user
   POSTGRES_PASSWORD=CreateYourStrongPassword2026!
   POSTGRES_DB=datapulse_db

   # Set a cryptographically secure JWT secret:
   JWT_SECRET=f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8
   ```

> [!CAUTION]
> If `POSTGRES_PASSWORD` or `JWT_SECRET` is left unset in `.env`, `docker compose up` will intentionally halt with an error to protect your environment from weak default passwords.

---

## 6. Step 5: Build & Launch the Complete Container Stack

Start all services (PostgreSQL 16, FastAPI backend, React frontend) in detached mode:

```powershell
docker compose up --build -d
```

### Expected Startup Sequence:
1. `datapulse_db`: Starts PostgreSQL 16 on `127.0.0.1:5432` with persistent volume `postgres_data`. Runs `pg_isready` healthcheck.
2. `datapulse_backend`: Waits until `datapulse_db` is healthy. Runs `alembic upgrade head`, validates ETL, and starts FastAPI on `127.0.0.1:8000`.
3. `datapulse_frontend`: Waits until `datapulse_backend` is healthy. Serves compiled React 19 UI on `127.0.0.1:3000`.

---

## 7. Step 6: Verify Service Health & Live API

Inspect running containers and health status:

```powershell
docker compose ps
```

**Expected output:**
```text
NAME                 IMAGE                STATUS                   PORTS
datapulse_db         postgres:16-alpine   Up (healthy)             127.0.0.1:5432->5432/tcp
datapulse_backend    datapulse-backend    Up (healthy)             127.0.0.1:8000->8000/tcp
datapulse_frontend   datapulse-frontend   Up                       127.0.0.1:3000->80/tcp
```

Query the backend health and analytics endpoints via PowerShell:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health"
# Expected response: status: UP, database: HEALTHY, ml_models: READY

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/analytics/overview"
# Expected response: total_students: 674, total_enrollments: 1044, pass_rate_pct: 78.0
```

Access the user interfaces in your browser:
- **Executive SaaS Web Dashboard**: [http://localhost:3000](http://localhost:3000)
- **Interactive OpenAPI Swagger Docs**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

---

## 8. Step 7: Verify Database Persistence Across Container Restarts

To verify that educational records survive container lifecycle events:

```powershell
# Restart the database container
docker compose restart db

# Verify that the container restarts and recovers to healthy status
docker compose ps

# Re-query the API to confirm data persistence
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/analytics/overview"
# Expected: All 674 students and 1,044 enrollments remain intact
```

---

## 9. Step 8: Run Tests Against PostgreSQL Inside Container

To execute the automated test suite directly against the live PostgreSQL database:

```powershell
docker compose exec backend pytest -v
```

---

## 10. Teardown Commands

```powershell
# Stop all containers while preserving database volume:
docker compose down

# View logs for a specific service:
docker compose logs -f backend
docker compose logs -f db
```
