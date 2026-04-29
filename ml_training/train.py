"""
YOLOv8 Training Script for Facility Anomaly Detection.

Usage:
    python train.py --data dataset.yaml --epochs 100 --model yolov8n.pt
"""

import argparse
from pathlib import Path


def train(args):
    from ultralytics import YOLO

    # Load base model
    model = YOLO(args.model)
    print(f"📦 Base model: {args.model}")
    print(f"📂 Dataset: {args.data}")
    print(f"🔄 Epochs: {args.epochs}")
    print(f"📐 Image size: {args.imgsz}")

    # Train
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        name=args.name,
        patience=args.patience,
        save=True,
        plots=True,
        device=args.device,
    )

    print("\n✅ Training complete!")
    print(f"📁 Results saved to: {results.save_dir}")

    # Validate
    print("\n🧪 Running validation...")
    metrics = model.val()
    print(f"   mAP50: {metrics.box.map50:.4f}")
    print(f"   mAP50-95: {metrics.box.map:.4f}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLOv8 for Facility Anomaly Detection")
    parser.add_argument("--data", type=str, default="dataset.yaml", help="Path to dataset YAML")
    parser.add_argument("--model", type=str, default="yolov8n.pt", help="Base model (yolov8n/s/m/l/x)")
    parser.add_argument("--epochs", type=int, default=100, help="Number of training epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--name", type=str, default="facility_anomaly", help="Run name")
    parser.add_argument("--patience", type=int, default=20, help="Early stopping patience")
    parser.add_argument("--device", type=str, default="", help="Device (cuda:0, cpu, etc.)")
    args = parser.parse_args()

    train(args)
