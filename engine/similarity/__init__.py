"""Similarity detection module — STUB ONLY for Review 1.

This module reserves the interface for O3 (cross-language similarity /
plagiarism detection) which will be implemented in Review 2.  The stub
proves the architecture anticipates O3 without building it — a Gate 1
evidence point per ARCHITECTURE.md §3.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from engine.parsing.normalize import FileIR


@dataclass(frozen=True)
class SimilarityReport:
    """Result of a similarity/plagiarism analysis across multiple files."""

    pairs: list[dict[str, object]] = field(default_factory=list)


def detect_similarity(file_irs: list[FileIR]) -> SimilarityReport:
    """Detect similarity/plagiarism across a set of parsed file IRs.

    This is a stub reserved for Review 2 (O3).  It accepts the same
    ``FileIR`` dataclass that the quality engine consumes, so O3 can be
    added without touching O1/O2 code.

    Raises:
        NotImplementedError: Always — O3 is not implemented in this review.
    """
    raise NotImplementedError(
        "Similarity detection is not implemented in Review 1.  "
        "This interface is reserved for the O3 deliverable in Review 2."
    )
