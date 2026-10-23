from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import detect, plc

app = FastAPI(
    title="P&ID Symbol Detection API",
    description="Detects piping/instrumentation symbols and reads their tags from P&ID drawings.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict to your frontend's origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(detect.router)
app.include_router(plc.router)


@app.get("/")
def root():
    return {"service": "pid-symbol-detection", "docs": "/docs"}