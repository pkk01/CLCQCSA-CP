"""Similarity / plagiarism detection route: POST /api/similarity.

No DB persistence — stateless computation only.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from api.models import ErrorResponse
from engine.similarity import compare_snippets

router = APIRouter(prefix="/api/similarity", tags=["similarity"])

SUPPORTED_LANGUAGES = {"python", "java"}


class SimilarityRequest(BaseModel):
    code_a: str
    language_a: str
    code_b: str
    language_b: str

    @field_validator("language_a", "language_b")
    @classmethod
    def _validate_language(cls, v: str) -> str:
        normalised = v.lower().strip()
        if normalised not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language '{v}'. Must be one of: {', '.join(sorted(SUPPORTED_LANGUAGES))}."
            )
        return normalised


class SimilarityResponse(BaseModel):
    similarity: float
    verdict: str
    structural_score: float
    shingle_score: float
    tokens_a: int
    tokens_b: int
    matching_ngrams: int
    reason: str


@router.post(
    "",
    response_model=SimilarityResponse,
    responses={
        400: {"model": ErrorResponse},
        422: {"description": "Validation error — missing or invalid fields"},
    },
)
def check_similarity(body: SimilarityRequest):
    """Compare two code snippets for structural / plagiarism similarity.

    Returns a similarity percentage and verdict based on tree-sitter parse
    trees with language-agnostic structural tokens — no hardcoded results.
    """
    try:
        result = compare_snippets(
            body.code_a,
            body.language_a,
            body.code_b,
            body.language_b,
        )
        return result
    except SyntaxError as exc:
        return JSONResponse(
            status_code=400,
            content={"error": "syntax_error", "detail": str(exc)},
        )
    except ValueError as exc:
        msg = str(exc)
        if "too short" in msg:
            code = "too_short"
        elif "supported language" in msg or "Unsupported language" in msg:
            code = "unsupported_language"
        else:
            code = "invalid_input"
        return JSONResponse(
            status_code=400,
            content={"error": code, "detail": msg},
        )
