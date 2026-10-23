from fastapi import APIRouter
from app.services.codegen_service import generate_st

router = APIRouter()


@router.post("/plc")
def plc(body: dict):
    code, warnings = generate_st(body.get("detections", []))
    return {"code": code, "warnings": warnings}