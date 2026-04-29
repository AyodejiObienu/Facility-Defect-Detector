"""
ML Inference Service — supports both real YOLO and mock detection modes.

When USE_MOCK_DETECTION is True, generates realistic mock detections for demo
purposes so the app works without a trained custom model.
"""

import base64
import random
import uuid
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from ..config import settings

# ── Facility-specific class definitions ──────────────────────────────

FACILITY_CLASSES = {
    0: {"name": "bunk_normal", "is_anomaly": False},
    1: {"name": "bunk_broken", "is_anomaly": True},
    2: {"name": "fan_normal", "is_anomaly": False},
    3: {"name": "fan_broken", "is_anomaly": True},
    4: {"name": "chair_normal", "is_anomaly": False},
    5: {"name": "chair_broken", "is_anomaly": True},
    6: {"name": "table_normal", "is_anomaly": False},
    7: {"name": "table_broken", "is_anomaly": True},
}

# ── Global model reference ───────────────────────────────────────────
_model = None


def load_model():
    """Load the YOLO model at startup (if not using mock mode)."""
    global _model
    if settings.USE_MOCK_DETECTION:
        print("🔧 Using MOCK detection mode (no model loaded)")
        return

    try:
        from ultralytics import YOLO
        model_path = Path(settings.MODEL_PATH)
        if model_path.exists():
            _model = YOLO(str(model_path))
            print(f"✅ YOLO model loaded from {model_path}")
        else:
            print(f"⚠️  Model not found at {model_path}, falling back to yolov8n.pt")
            _model = YOLO("yolov8n.pt")
            print("✅ Pre-trained YOLOv8n loaded (generic classes)")
    except Exception as e:
        print(f"❌ Failed to load YOLO model: {e}")
        print("🔧 Falling back to MOCK detection mode")


def _generate_mock_detections(width: int, height: int, count: int | None = None) -> list[dict]:
    """Generate realistic mock detections for demo purposes."""
    if count is None:
        count = random.randint(1, 5)

    detections = []
    for _ in range(count):
        cls_id = random.choice(list(FACILITY_CLASSES.keys()))
        cls_info = FACILITY_CLASSES[cls_id]

        # Generate a realistic bounding box
        box_w = random.uniform(0.08, 0.35) * width
        box_h = random.uniform(0.08, 0.35) * height
        x1 = random.uniform(0.05 * width, width - box_w - 0.05 * width)
        y1 = random.uniform(0.05 * height, height - box_h - 0.05 * height)

        detections.append({
            "class_name": cls_info["name"],
            "confidence": round(random.uniform(0.55, 0.98), 4),
            "is_anomaly": cls_info["is_anomaly"],
            "bbox_x1": round(x1, 2),
            "bbox_y1": round(y1, 2),
            "bbox_x2": round(x1 + box_w, 2),
            "bbox_y2": round(y1 + box_h, 2),
        })

    return detections


def _yolo_to_detections(results) -> list[dict]:
    """Convert YOLO results to our detection format."""
    detections = []
    for result in results:
        boxes = result.boxes
        if boxes is None:
            continue
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            # Map to facility classes if custom model, else use generic YOLO names
            if cls_id in FACILITY_CLASSES:
                cls_info = FACILITY_CLASSES[cls_id]
                class_name = cls_info["name"]
                is_anomaly = cls_info["is_anomaly"]
            else:
                class_name = result.names.get(cls_id, f"class_{cls_id}")
                is_anomaly = False

            if conf >= settings.DETECTION_CONFIDENCE:
                detections.append({
                    "class_name": class_name,
                    "confidence": round(conf, 4),
                    "is_anomaly": is_anomaly,
                    "bbox_x1": round(x1, 2),
                    "bbox_y1": round(y1, 2),
                    "bbox_x2": round(x2, 2),
                    "bbox_y2": round(y2, 2),
                })
    return detections


def detect_image(image_path: str) -> list[dict]:
    """Run detection on a single image file."""
    img = Image.open(image_path)
    width, height = img.size

    if settings.USE_MOCK_DETECTION or _model is None:
        return _generate_mock_detections(width, height)

    results = _model(image_path, conf=settings.DETECTION_CONFIDENCE)
    return _yolo_to_detections(results)


def detect_frame(frame_base64: str) -> list[dict]:
    """Run detection on a base64-encoded frame (from webcam)."""
    # Decode base64 → numpy array
    if "," in frame_base64:
        frame_base64 = frame_base64.split(",")[1]

    frame_bytes = base64.b64decode(frame_base64)
    nparr = np.frombuffer(frame_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if frame is None:
        return []

    height, width = frame.shape[:2]

    if settings.USE_MOCK_DETECTION or _model is None:
        return _generate_mock_detections(width, height, count=random.randint(0, 3))

    results = _model(frame, conf=settings.DETECTION_CONFIDENCE)
    return _yolo_to_detections(results)


def detect_video(video_path: str) -> list[dict]:
    """Run detection on a video file — sample every Nth frame."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    interval = settings.VIDEO_FRAME_INTERVAL

    all_detections = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % interval == 0:
            if settings.USE_MOCK_DETECTION or _model is None:
                dets = _generate_mock_detections(width, height, count=random.randint(0, 4))
            else:
                results = _model(frame, conf=settings.DETECTION_CONFIDENCE)
                dets = _yolo_to_detections(results)

            for det in dets:
                det["frame_number"] = frame_idx
            all_detections.extend(dets)

        frame_idx += 1

    cap.release()
    return all_detections
