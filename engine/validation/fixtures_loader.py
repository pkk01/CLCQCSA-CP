import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Fixture:
    fixture_id: str
    language: str
    expected_label: str
    path: Path


def load_fixtures(fixtures_dir: Path) -> list[Fixture]:
    """Load fixture metadata and resolve each fixture file path."""
    labels = json.loads((fixtures_dir / "labels.json").read_text(encoding="utf-8"))
    fixtures = []
    for fixture_id, metadata in labels.items():
        path = fixtures_dir / metadata["language"] / metadata["expected_label"] / metadata["filename"]
        fixtures.append(Fixture(fixture_id, metadata["language"], metadata["expected_label"], path))
    return fixtures
