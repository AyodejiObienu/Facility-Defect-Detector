# 🏗️ Facility Visual Anomaly Detection

AI-powered web application for detecting anomalies in facility equipment (bunk beds, fans, tables, chairs) using computer vision.

![Stack](https://img.shields.io/badge/Next.js-black?logo=next.js) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![YOLOv8](https://img.shields.io/badge/YOLOv8-purple) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)

## Features

- 📷 **Image Inspection** — Upload facility photos for instant anomaly detection with bounding box overlays
- 🎥 **Video Analysis** — Process footage frame-by-frame to catch every defect
- 📹 **Live Camera** — Real-time detection using your webcam with a scanning overlay
- 📊 **Dashboard** — Stats overview, recent inspections, and anomaly rates
- 🗂️ **Results History** — Browse, filter, and inspect past detection results

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌────────────┐
│  Next.js    │────▶│  FastAPI Backend  │────▶│ PostgreSQL │
│  Frontend   │     │  + YOLOv8 Model   │     │            │
│  (Port 3000)│◀────│  (Port 8000)      │     │ (Port 5432)│
└─────────────┘     └──────────────────┘     └────────────┘
```

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Start all services
docker-compose up --build

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

### Option 2: Local Development

**Prerequisites**: Python 3.11+, Node.js 18+, PostgreSQL (or use Docker just for the DB)

#### Database (Docker)
```bash
docker-compose up postgres
```

#### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** in your browser.

## Configuration

Create a `backend/.env` file to override defaults:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/facility_anomaly

# ML Model
USE_MOCK_DETECTION=true          # Set to false when you have a trained model
MODEL_PATH=models/facility_model.pt
DETECTION_CONFIDENCE=0.35

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

## Training a Custom Model

See [`ml_training/README.md`](./ml_training/README.md) for detailed instructions on:
1. Preparing and labeling your dataset
2. Training a YOLOv8 model
3. Exporting for production
4. Deploying to the backend

## API Endpoints

| Method | Endpoint                       | Description                    |
|--------|--------------------------------|--------------------------------|
| POST   | `/api/upload/image`            | Upload an image                |
| POST   | `/api/upload/video`            | Upload a video                 |
| POST   | `/api/detect/image/{id}`       | Run detection on image         |
| POST   | `/api/detect/video/{id}`       | Run detection on video         |
| POST   | `/api/detect/frame`            | Detect from webcam frame       |
| GET    | `/api/results`                 | List all inspections           |
| GET    | `/api/results/stats`           | Dashboard statistics           |
| GET    | `/api/results/{id}`            | Inspection detail              |
| GET    | `/api/health`                  | Health check                   |

## Project Structure

```
├── backend/                 # FastAPI + YOLOv8
│   ├── app/
│   │   ├── main.py          # App entry point
│   │   ├── config.py        # Settings & env vars
│   │   ├── database.py      # Async SQLAlchemy
│   │   ├── models.py        # ORM models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── routers/         # API routes
│   │   └── services/        # Inference, storage, video processing
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # Next.js + TailwindCSS
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   ├── components/      # React components
│   │   └── lib/             # API client & types
│   └── Dockerfile
├── ml_training/             # Model training scripts
├── infrastructure/          # Nginx, PostgreSQL configs
├── docker-compose.yml
└── README.md
```

## License

MIT
