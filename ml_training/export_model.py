"""
Export trained YOLO model to ONNX or TorchScript for production.

Usage:
    python export_model.py --weights runs/detect/facility_anomaly/weights/best.pt --format onnx
"""

import argparse


def export(args):
    from ultralytics import YOLO

    model = YOLO(args.weights)
    print(f"📦 Exporting {args.weights} to {args.format}...")

    model.export(
        format=args.format,
        imgsz=args.imgsz,
        half=args.half,
        simplify=args.simplify,
    )

    print(f"\n✅ Export complete! Format: {args.format}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export YOLO model for production")
    parser.add_argument("--weights", type=str, required=True, help="Path to trained weights (.pt)")
    parser.add_argument("--format", type=str, default="onnx", choices=["onnx", "torchscript", "tflite", "engine"], help="Export format")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--half", action="store_true", help="FP16 quantization")
    parser.add_argument("--simplify", action="store_true", help="Simplify ONNX model")
    args = parser.parse_args()

    export(args)
