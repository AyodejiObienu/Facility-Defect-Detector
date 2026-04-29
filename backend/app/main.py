"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import init_db
from .routers import upload, detect, results
from .services.inference import load_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown events."""
    # ── Startup ──────────────────────────────────────────────
    print(f"🚀 Starting {settings.APP_NAME}")

    # Create upload directories
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.RESULTS_DIR).mkdir(parents=True, exist_ok=True)

    # Initialize database tables
    try:
        await init_db()
        print("✅ Database tables created")
    except Exception as e:
        print(f"⚠️  Database init skipped (use Docker for PostgreSQL): {e}")

    # Load ML model
    load_model()

    yield

    # ── Shutdown ─────────────────────────────────────────────
    print("👋 Shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Detect anomalies in facility equipment using computer vision.",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files (serve uploaded images) ─────────────────────────────
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ── Routers ──────────────────────────────────────────────────────────
app.include_router(upload.router)
app.include_router(detect.router)
app.include_router(results.router)


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "mock_mode": settings.USE_MOCK_DETECTION,
        "version": "1.0.0",
    }
