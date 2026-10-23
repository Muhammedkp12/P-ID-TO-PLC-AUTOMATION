# Lineweight — P&ID Symbol Detection

Upload a P&ID (piping & instrumentation diagram) drawing, get every valve,
instrument, pump and line symbol detected and tagged automatically.

- **Backend** — FastAPI + Ultralytics YOLO for symbol detection, Tesseract
  OCR for reading tag text next to each symbol, tiling so large A0/A1 scans
  don't lose small symbols.
- **Frontend** — React (Vite), a drafting-table-styled UI: drag-and-drop
  upload, an annotated drawing viewer with bounding-box overlays, and a
  sortable parts-list table of everything found.

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              FastAPI entrypoint
│   │   ├── routers/detect.py    /detect, /health, /train
│   │   ├── models/best.pt       ← put your trained weights here
│   │   ├── services/
│   │   │   ├── yolo_service.py     tiled YOLO inference
│   │   │   ├── ocr_service.py      tag text reading (Tesseract)
│   │   │   └── postprocess.py      NMS de-dupe + merge symbol+tag
│   │   ├── schemas/detection.py Pydantic response models
│   │   └── utils/image_utils.py Tiling / resizing helpers
│   ├── training/
│   │   ├── dataset/              your labeled YOLO dataset
│   │   ├── data.yaml
│   │   └── train.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/  UploadPanel, ResultViewer, DetectionTable, Loader
│   │   ├── api/detectApi.js
│   │   └── App.jsx
│   └── Dockerfile
└── docker-compose.yml
```

## 1. Get a trained model

This repo doesn't ship weights. Label a symbol dataset (Roboflow, CVAT, or
similar work fine — export in YOLO format into `backend/training/dataset/`),
update the class list in `backend/training/data.yaml`, then:

```bash
cd backend
pip install -r requirements.txt
python training/train.py --data training/data.yaml --epochs 100 --imgsz 1280
cp runs/detect/pid_symbols/weights/best.pt app/models/best.pt
```

Until `best.pt` exists in `backend/app/models/`, `/detect` responds with a
`503` explaining the model isn't loaded — the rest of the app still runs.

## 2. Run it

**With Docker (recommended):**

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs

> Note: Vite bakes `VITE_API_URL` in at *build* time, not container start
> time. If you change the backend URL, rebuild the frontend image
> (`docker compose build frontend`) rather than only restarting it.

**Without Docker, for local dev:**

```bash
# backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# frontend, in a second terminal
cd frontend
npm install
npm run dev
```

Frontend dev server runs on http://localhost:5173 and talks to the backend
at http://localhost:8000 by default (override with a `.env` file setting
`VITE_API_URL`).

## API

`POST /detect` — multipart form, field `file` (image). Returns:

```json
{
  "filename": "unit12.jpg",
  "width": 4096,
  "height": 2894,
  "count": 3,
  "detections": [
    { "class": "gate_valve", "confidence": 0.91, "bbox": [120, 340, 168, 388], "tag": "GV-1021", "tag_confidence": 0.86 }
  ]
}
```

`GET /health` — `{ "status": "ok", "model_loaded": true }`

`POST /train` — kicks off `training/train.py` as a background process
(dev/internal use only — protect or remove this endpoint before deploying
publicly).

## Extending

- **Add symbol classes**: update `backend/training/data.yaml`, re-label,
  retrain.
- **Tune tiling**: `YOLO_TILE_SIZE` / `YOLO_TILE_OVERLAP` env vars on the
  backend control how large sheets are split before inference.
- **Tag matching heuristic**: `ocr_service.py`'s `PAD_RATIO` controls how
  far around a symbol the OCR crop looks for its tag — widen it if tags
  sit further from their symbol in your drawing standard.
