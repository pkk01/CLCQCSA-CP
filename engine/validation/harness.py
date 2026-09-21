from dataclasses import dataclass
from pathlib import Path

from engine.parsing import normalize_tree, parse_source
from engine.quality import score_file
from engine.validation.fixtures_loader import load_fixtures

THRESHOLD = 60.0


@dataclass(frozen=True)
class FixtureResult:
    fixture_id: str
    language: str
    expected_label: str
    predicted_label: str
    predicted_score: float
    correct: bool


@dataclass(frozen=True)
class ValidationReport:
    overall_accuracy: float
    fixture_count: int
    language_breakdown: dict[str, float]
    threshold_used: float
    results: list[FixtureResult]


def run_validation(fixtures_dir: Path, threshold: float = THRESHOLD) -> ValidationReport:
    """Run parsing and scoring over labelled fixtures and calculate accuracy."""
    results = []
    for fixture in load_fixtures(fixtures_dir):
        source = fixture.path.read_text(encoding="utf-8")
        file_ir = normalize_tree(parse_source(source, fixture.language), source, fixture.language)
        score = float(score_file(file_ir)["composite_score"])
        predicted_label = "good" if score >= threshold else "bad"
        results.append(FixtureResult(
            fixture.fixture_id,
            fixture.language,
            fixture.expected_label,
            predicted_label,
            score,
            predicted_label == fixture.expected_label,
        ))
    language_breakdown = {}
    for language in {result.language for result in results}:
        language_results = [result for result in results if result.language == language]
        language_breakdown[language] = sum(result.correct for result in language_results) / len(language_results)
    return ValidationReport(
        overall_accuracy=sum(result.correct for result in results) / len(results) if results else 0.0,
        fixture_count=len(results),
        language_breakdown=language_breakdown,
        threshold_used=threshold,
        results=results,
    )
