"""Analysis route handlers: POST /api/analyze, GET /api/analyze/{run_id}."""

from __future__ import annotations

import json
import logging
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.db.models import AnalysisRun
from api.db.session import get_db
from api.models import AnalysisResponse, ErrorResponse
from api.services.analyze_service import analyze_uploads
from api.services.validation_service import execute_validation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


def format_run_response(run: AnalysisRun) -> dict:
    """Format an AnalysisRun database record into the API response dictionary."""
    files = []
    for analyzed_file in run.files:
        functions = [
            {
                "name": item.name,
                "start_line": item.start_line,
                "end_line": item.end_line,
                "cyclomatic_complexity": item.cyclomatic_complexity,
                "nesting_depth": item.nesting_depth,
                "length_lines": item.length_lines,
                "flags": json.loads(item.flags_json),
            }
            for item in analyzed_file.functions
        ]
        files.append(
            {
                "file_id": analyzed_file.id,
                "filename": analyzed_file.filename,
                "language": analyzed_file.language,
                "loc": analyzed_file.loc,
                "composite_score": analyzed_file.composite_score,
                "functions": functions,
            }
        )
    return {
        "run_id": run.id,
        "status": run.status,
        "composite_score": run.composite_score,
        "language_summary": json.loads(run.language_summary),
        "files": files,
    }


@router.post("", response_model=AnalysisResponse, responses={400: {"model": ErrorResponse}})
def analyze(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """Upload and analyze one or more source files.
    
    Also automatically updates the validation harness so the validation benchmark
    records stay freshly updated after analysis.
    """
    try:
        result = analyze_uploads(db, files)
        try:
            execute_validation(db)
        except Exception as val_err:
            logger.warning("Validation update after analysis failed: %s", val_err)
        return result
    except ValueError as error:
        code = "unsupported_language" if "supported language" in str(error) else "invalid_source"
        return JSONResponse(status_code=400, content={"error": code, "detail": str(error)})


@router.get("/{run_id}", response_model=AnalysisResponse, responses={404: {"model": ErrorResponse}})
def get_analysis(
    run_id: int,
    db: Session = Depends(get_db),
):
    """Fetch stored results of a previously computed run without recomputing."""
    run = db.get(AnalysisRun, run_id)
    if run is None:
        return JSONResponse(
            status_code=404,
            content={"error": "not_found", "detail": f"No analysis run with id {run_id}"},
        )
    return format_run_response(run)
