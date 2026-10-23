# Model weights

Place your trained YOLO weights here as `best.pt`.

This repo doesn't ship a trained model. Train one with:

```bash
cd backend
python training/train.py --data training/data.yaml --epochs 100 --imgsz 1280
```

Then copy the resulting `runs/detect/train/weights/best.pt` into this folder,
or point the backend at it directly with:

```bash
export YOLO_MODEL_PATH=/path/to/best.pt
```

Until `best.pt` exists here, `/detect` returns `503 Model weights not found`.
