# ML Training Pipeline

This directory contains scripts for training a custom YOLOv8 model to detect facility equipment anomalies.

## Classes

| ID | Class Name     | Type    |
|----|----------------|---------|
| 0  | bunk_normal    | Normal  |
| 1  | bunk_broken    | Anomaly |
| 2  | fan_normal     | Normal  |
| 3  | fan_broken     | Anomaly |
| 4  | chair_normal   | Normal  |
| 5  | chair_broken   | Anomaly |
| 6  | table_normal   | Normal  |
| 7  | table_broken   | Anomaly |

## Dataset Preparation

1. **Collect images** of facility equipment (bunk beds, fans, chairs, tables) in both normal and damaged states.

2. **Label images** using one of these tools:
   - [Roboflow](https://roboflow.com) (recommended — free tier available)
   - [CVAT](https://cvat.org) (open source)
   - [LabelImg](https://github.com/heartexlabs/labelImg)

3. **Organize** the dataset:
   ```
   ml_training/
   └── dataset/
       └── images/
           ├── train/    # 80% of images
           └── val/      # 20% of images
       └── labels/
           ├── train/    # Corresponding YOLO-format .txt files
           └── val/
   ```

4. Each `.txt` label file should have one line per object:
   ```
   <class_id> <x_center> <y_center> <width> <height>
   ```

## Training

```bash
pip install -r requirements.txt

# Train with YOLOv8 nano (fastest)
python train.py --data dataset.yaml --model yolov8n.pt --epochs 100

# Train with YOLOv8 small (more accurate)
python train.py --data dataset.yaml --model yolov8s.pt --epochs 150

# Train on GPU
python train.py --data dataset.yaml --model yolov8n.pt --epochs 100 --device cuda:0
```

## Export for Production

```bash
# Export to ONNX
python export_model.py --weights runs/detect/facility_anomaly/weights/best.pt --format onnx

# Export with FP16
python export_model.py --weights runs/detect/facility_anomaly/weights/best.pt --format onnx --half
```

## Using the Trained Model

Copy the exported model to the backend:
```bash
cp runs/detect/facility_anomaly/weights/best.pt ../backend/models/facility_model.pt
```

Then update `backend/.env`:
```
MODEL_PATH=models/facility_model.pt
USE_MOCK_DETECTION=false
```

## Tips

- **Minimum images**: Aim for 100+ images per class for decent results, 500+ for production quality.
- **Augmentation**: YOLOv8 applies augmentation automatically during training.
- **Transfer learning**: Starting from `yolov8n.pt` (pre-trained on COCO) gives much better results than training from scratch.
