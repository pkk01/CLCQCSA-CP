"""Validation service — orchestrates harness run → persist → return summary."""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from api.db.models import FixtureResult, ValidationRun
from engine.validation import run_validation


FIXTURES_DIR = Path(__file__).resolve().parents[2] / "fixtures"


def execute_validation(db: Session) -> dict:
    """Run the fixture validation harness and persist results.

    Returns the response dict matching API.md's ``POST /api/validation/run``
    shape.
    """
    report = run_validation(FIXTURES_DIR)
    validation = ValidationRun(
        overall_accuracy=report.overall_accuracy,
        fixture_count=report.fixture_count,
        language_breakdown_json=json.dumps(report.language_breakdown),
        threshold_used=report.threshold_used,
    )
    db.add(validation)
    db.flush()
    for result in report.results:
        db.add(
            FixtureResult(
                validation_run_id=validation.id,
                fixture_id=result.fixture_id,
                language=result.language,
                expected_label=result.expected_label,
                predicted_label=result.predicted_label,
                predicted_score=result.predicted_score,
                correct=result.correct,
            )
        )
    db.commit()
    return format_validation_response(validation)


def format_validation_response(validation: ValidationRun) -> dict:
    """Convert a ValidationRun ORM instance to the API.md response shape."""
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
