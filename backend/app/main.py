"""
DataPulse FastAPI Main Application
Integrates REST APIs, CORS, Database Session Management, and Documentation.
"""

from contextlib import asynccontextmanager
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

# Ensure root directory is on sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
parent_of_root = root_dir.parent
if str(parent_of_root) not in sys.path:
    sys.path.insert(0, str(parent_of_root))

from DataPulse.backend.app.api.analytics import router as analytics_router
from DataPulse.backend.app.api.export import router as export_router
from DataPulse.backend.app.api.health import router as health_router
from DataPulse.backend.app.api.ml import router as ml_router
from DataPulse.backend.app.api.pipeline import router as pipeline_router
from DataPulse.backend.app.api.students import router as students_router
from DataPulse.backend.app.core.config import settings
from DataPulse.database.connection import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist
    print(f"[DataPulse API] Initializing database schema on {settings.DATABASE_URL}...")
    init_db()
    print("[DataPulse API] Startup initialization complete.")
    yield
    print("[DataPulse API] Shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Smart Campus Analytics & Predictive Intelligence Platform for University Administration & Educational Science.",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(analytics_router, prefix=settings.API_PREFIX)
app.include_router(students_router, prefix=settings.API_PREFIX)
app.include_router(ml_router, prefix=settings.API_PREFIX)
app.include_router(pipeline_router, prefix=settings.API_PREFIX)
app.include_router(export_router, prefix=settings.API_PREFIX)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url=f"{settings.API_PREFIX}/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("DataPulse.backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
