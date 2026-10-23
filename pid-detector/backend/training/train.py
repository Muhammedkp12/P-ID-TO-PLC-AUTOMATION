"""
Trains a YOLO model on the P&ID symbol dataset.

Usage:
    python training/train.py --data training/data.yaml --epochs 100 --imgsz 1280

After training, copy runs/detect/<run_name>/weights/best.pt into
app/models/best.pt so the API can load it.
"""
import argparse

from ultralytics import YOLO


def main():
    parser = argparse.ArgumentParser(description="Train the P&ID symbol detector.")
    parser.add_argument("--data", default="training/data.yaml", help="Path to data.yaml")
    parser.add_argument("--model", default="yolov8m.pt", help="Base weights to fine-tune from")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=1280, help="P&ID sheets have small, dense symbols")
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--name", default="pid_symbols")
    args = parser.parse_args()

    model = YOLO(args.model)
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        name=args.name,
    )


if __name__ == "__main__":
    main()
