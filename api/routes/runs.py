"""History / past runs route handlers: GET /api/runs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from api.db.models import AnalysisRun
from api.db.session import get_db
from api.models import RunsListResponse

router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.get("", response_model=RunsListResponse)
def list_runs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """List past analysis runs with pagination."""
    total = db.scalar(select(func.count()).select_from(AnalysisRun)) or 0
    runs = db.scalars(
        select(AnalysisRun)
        .order_by(AnalysisRun.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()

    return {
        "total": total,
        "runs": [
            {
                "run_id": run.id,
                "created_at": run.created_at.isoformat() + "Z",
                "source_label": run.source_label,
                "composite_score": run.composite_score,
                "status": run.status,
            }
            for run in runs
        ],
    }
