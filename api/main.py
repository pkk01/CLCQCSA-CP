import json
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.db.models import AnalysisRun, AnalyzedFile, Base, FixtureResult, FunctionScore, ValidationRun
from api.db.session import engine, get_db
from api.services.analyze_service import analyze_uploads
from engine.validation import run_validation

Base.metadata.create_all(bind=engine)
app = FastAPI(title="CodeQual API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def error_response(code: str, detail: str) -> dict[str, str]:
    return {"error": code, "detail": detail}


def api_error(status_code: int, code: str, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=error_response(code, detail))


def run_response(db: Session, run: AnalysisRun) -> dict:
    files = []
    for analyzed_file in run.files:
        functions = [{"name": item.name, "start_line": item.start_line, "end_line": item.end_line, "cyclomatic_complexity": item.cyclomatic_complexity, "nesting_depth": item.nesting_depth, "length_lines": item.length_lines, "flags": json.loads(item.flags_json)} for item in analyzed_file.functions]
        files.append({"file_id": analyzed_file.id, "filename": analyzed_file.filename, "language": analyzed_file.language, "loc": analyzed_file.loc, "composite_score": analyzed_file.composite_score, "functions": functions})
    return {"run_id": run.id, "status": run.status, "composite_score": run.composite_score, "language_summary": json.loads(run.language_summary), "files": files}

@app.post("/api/analyze")
def analyze(files: list[UploadFile] = File(...), db: Session = Depends(get_db)) -> dict:
    try:
        return analyze_uploads(db, files)
    except ValueError as error:
        code = "unsupported_language" if "supported language" in str(error) else "invalid_source"
        return api_error(400, code, str(error))

@app.get("/api/analyze/{run_id}")
def get_analysis(run_id: int, db: Session = Depends(get_db)) -> dict:
    run = db.get(AnalysisRun, run_id)
    if run is None:
        return api_error(404, "not_found", f"No analysis run with id {run_id}")
    return run_response(db, run)

@app.get("/api/runs")
def list_runs(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)) -> dict:
    total = db.scalar(select(func.count()).select_from(AnalysisRun)) or 0
    runs = db.scalars(select(AnalysisRun).order_by(AnalysisRun.created_at.desc()).limit(limit).offset(offset)).all()
    return {"total": total, "runs": [{"run_id": run.id, "created_at": run.created_at.isoformat() + "Z", "source_label": run.source_label, "composite_score": run.composite_score, "status": run.status} for run in runs]}

@app.get("/api/health")
def health() -> dict[str, object]:
    return {"status": "ok", "grammars_loaded": ["python", "java"]}

@app.get("/api/validation/latest")
def latest_validation(db: Session = Depends(get_db)) -> dict[str, object]:
    validation = db.scalar(select(ValidationRun).order_by(ValidationRun.created_at.desc()))
    if validation is None:
        return {"validation_run_id": None}
    return validation_response(validation)

def validation_response(validation: ValidationRun) -> dict:
    return {
        "validation_run_id": validation.id,
        "overall_accuracy": validation.overall_accuracy,
        "fixture_count": validation.fixture_count,
        "language_breakdown": json.loads(validation.language_breakdown_json),
        "threshold_used": validation.threshold_used,
        "results": [
            {
                "fixture_id": result.fixture_id,
                "language": result.language,
                "expected_label": result.expected_label,
                "predicted_label": result.predicted_label,
                "predicted_score": result.predicted_score,
                "correct": result.correct,
            }
            for result in validation.results
        ],
    }

@app.get("/api/validation/{validation_run_id}")
def get_validation(validation_run_id: int, db: Session = Depends(get_db)) -> dict:
    validation = db.get(ValidationRun, validation_run_id)
    if validation is None:
        return api_error(404, "not_found", f"No validation run with id {validation_run_id}")
    return validation_response(validation)

@app.post("/api/validation/run")
def run_validation_endpoint(db: Session = Depends(get_db)) -> dict:
    try:
        report = run_validation(Path(__file__).resolve().parents[1] / "fixtures")
    except Exception as error:
        return api_error(500, "validation_failed", str(error))
    validation = ValidationRun(overall_accuracy=report.overall_accuracy, fixture_count=report.fixture_count, language_breakdown_json=json.dumps(report.language_breakdown), threshold_used=report.threshold_used)
    db.add(validation)
    db.flush()
    for result in report.results:
        db.add(FixtureResult(validation_run_id=validation.id, fixture_id=result.fixture_id, language=result.language, expected_label=result.expected_label, predicted_label=result.predicted_label, predicted_score=result.predicted_score, correct=result.correct))
    db.commit()
    return validation_response(validation)
