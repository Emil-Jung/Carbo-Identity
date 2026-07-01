"""Health/info endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "service": "carbo-identity"}


@router.get("/schema_version")
def schema_version():
    return {"schema_version": "1.0"}
