"""Pydantic response schemas matching API.md exactly."""

from __future__ import annotations

from pydantic import BaseModel


class FunctionReport(BaseModel):
    name: str
    start_line: int
    end_line: int
    cyclomatic_complexity: int
    nesting_depth: int
    length_lines: int
    flags: list[str]


class FileReport(BaseModel):
    file_id: int
    filename: str
    language: str
    loc: int
    composite_score: float
    functions: list[FunctionReport]


class AnalysisResponse(BaseModel):
    run_id: int
    status: str
    composite_score: float | None
    language_summary: dict[str, int]
    files: list[FileReport]


class RunSummary(BaseModel):
    run_id: int
    created_at: str
    source_label: str
    composite_score: float | None
    status: str


class RunsListResponse(BaseModel):
    total: int
    runs: list[RunSummary]


class FixtureResultResponse(BaseModel):
    fixture_id: str
    language: str
    expected_label: str
    predicted_label: str
    predicted_score: float
    correct: bool


class ValidationResponse(BaseModel):
    validation_run_id: int | None
    overall_accuracy: float | None = None
    fixture_count: int | None = None
    language_breakdown: dict[str, float] | None = None
    threshold_used: float | None = None
    results: list[FixtureResultResponse] | None = None


class ErrorResponse(BaseModel):
    error: str
    detail: str


class HealthResponse(BaseModel):
    status: str
    grammars_loaded: list[str]
