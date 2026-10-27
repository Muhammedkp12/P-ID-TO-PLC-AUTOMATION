from fastapi import APIRouter

from app.services import audit_service

router = APIRouter()


@router.get("/audit")
def audit_list():
    return {"records": audit_service.read_all()}


@router.get("/audit/verify")
def audit_verify():
    return audit_service.verify_chain()
