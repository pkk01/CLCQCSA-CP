"""Validation route handlers: POST /api/validation/run, GET /api/validation/latest, GET /api/validation/{validation_run_id}."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.db.models import ValidationRun
from api.db.session import get_db
from api.models import ErrorResponse, ValidationResponse
from api.services.validation_service import execute_validation, format_validation_response

router = APIRouter(prefix="/api/validation", tags=["validation"])


@router.get("/latest", response_model=ValidationResponse)
def latest_validation(db: Session = Depends(get_db)):
    """Fetch the most recent validation run, or execute one automatically if none exists yet."""
    validation = db.scalar(select(ValidationRun).order_by(ValidationRun.id.desc()))
    if validation is None:
        try:
            return execute_validation(db)
        except Exception:
            return {"validation_run_id": None}
    return format_validation_response(validation)


@router.get(
    "/{validation_run_id}",
    response_model=ValidationResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_validation(validation_run_id: int, db: Session = Depends(get_db)):
    """Fetch stored results of a previously computed validation run."""
    validation = db.get(ValidationRun, validation_run_id)
    if validation is None:
        return JSONResponse(
            status_code=404,
            content={"error": "not_found", "detail": f"No validation run with id {validation_run_id}"},
        )
    return format_validation_response(validation)


@router.post(
    "/run",
    response_model=ValidationResponse,
    responses={500: {"model": ErrorResponse}},
)
def run_validation_endpoint(db: Session = Depends(get_db)):
    """Trigger the fixture validation harness end to end and persist the result."""
    try:
        return execute_validation(db)
    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={"error": "validation_failed", "detail": str(error)},
        )
