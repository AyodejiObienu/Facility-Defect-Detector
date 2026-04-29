"""Application configuration via environment variables."""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────────────
    APP_NAME: str = "Facility Anomaly Detection API"
    DEBUG: bool = True

    # ── Database ─────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/facility_anomaly"

    # ── File Storage ─────────────────────────────────────────────────
    UPLOAD_DIR: str = str(Path(__file__).resolve().parent.parent / "uploads")
    RESULTS_DIR: str = str(Path(__file__).resolve().parent.parent / "results")

    # ── ML Model ─────────────────────────────────────────────────────
    MODEL_PATH: str = str(Path(__file__).resolve().parent.parent / "models" / "yolov8n.pt")
    USE_MOCK_DETECTION: bool = True  # Use mock detections when True
    DETECTION_CONFIDENCE: float = 0.35
    VIDEO_FRAME_INTERVAL: int = 10  # Process every Nth frame

    # ── CORS ─────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
