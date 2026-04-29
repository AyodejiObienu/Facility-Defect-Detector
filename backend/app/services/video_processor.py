"""Video frame extraction utilities."""

import cv2
from ..config import settings


def extract_frames(video_path: str, interval: int | None = None) -> list[tuple[int, any]]:
    """
    Extract frames from a video at the configured interval.

    Returns:
        List of (frame_number, frame_ndarray) tuples.
    """
    if interval is None:
        interval = settings.VIDEO_FRAME_INTERVAL

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    frames = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % interval == 0:
            frames.append((frame_idx, frame))

        frame_idx += 1

    cap.release()
    return frames


def get_video_info(video_path: str) -> dict:
    """Get video metadata."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {}

    info = {
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "fps": cap.get(cv2.CAP_PROP_FPS),
        "total_frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        "duration_seconds": int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / max(cap.get(cv2.CAP_PROP_FPS), 1)),
    }
    cap.release()
    return info
