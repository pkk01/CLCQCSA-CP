import json

from engine.validation import run_validation


def test_validation_harness_returns_accuracy_report(tmp_path) -> None:
    fixtures = tmp_path / "fixtures"
    (fixtures / "python" / "good").mkdir(parents=True)
    (fixtures / "python" / "bad").mkdir(parents=True)
    (fixtures / "python" / "good" / "good.py").write_text("def ok():\n    return 1\n", encoding="utf-8")
    (fixtures / "python" / "bad" / "bad.py").write_text("def broken(:\n    return 1\n", encoding="utf-8")
    (fixtures / "labels.json").write_text(json.dumps({
        "python_good_001": {"language": "python", "expected_label": "good", "filename": "good.py"},
        "python_bad_001": {"language": "python", "expected_label": "bad", "filename": "bad.py"},
    }), encoding="utf-8")

    report = run_validation(fixtures)

    assert report.fixture_count == 2
    assert 0.0 <= report.overall_accuracy <= 1.0
    assert report.language_breakdown == {"python": 1.0}
    assert all(result.correct for result in report.results)
