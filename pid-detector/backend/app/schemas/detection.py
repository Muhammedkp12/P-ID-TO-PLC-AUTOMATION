"""
Pydantic response models for the /detect and /train endpoints.
Keeping these separate from the service logic makes the API contract
explicit and lets FastAPI auto-generate accurate OpenAPI docs.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class Detection(BaseModel):
    class_name: str = Field(alias="class")
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    tag: Optional[str] = None          # OCR-read instrument/line tag, if any
    tag_confidence: Optional[float] = None

    class Config:
        populate_by_name = True


class DetectionResponse(BaseModel):
    filename: str
    width: int
    height: int
    count: int
    detections: List[Detection]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


class TrainRequest(BaseModel):
    epochs: int = 100
    imgsz: int = 1280
    batch: int = 8
    data_yaml: str = "training/data.yaml"


class TrainResponse(BaseModel):
    status: str
    message: str
    run_dir: Optional[str] = None
