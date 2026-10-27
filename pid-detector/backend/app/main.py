from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import audit, detect, generate, plc
from app.auth_routes import router as auth_router

app = FastAPI(
    title="P&ID Symbol Detection API",
    description="Detects piping/instrumentation symbols and reads their tags from P&ID drawings.",
    version="1.0.0",
)
app.include_router(auth_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict to your frontend's origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(detect.router)
app.include_router(plc.router)
app.include_router(generate.router)
app.include_router(audit.router)


@app.get("/")
def root():
    return {"service": "pid-symbol-detection", "docs": "/docs"}