"""API-level tests for POST /api/similarity."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


PYTHON_FIND_MAX = """\
def find_max(numbers):
    maximum = numbers[0]
    for number in numbers:
        if number > maximum:
            maximum = number
    return maximum
"""

JAVA_FIND_MAX = """\
public class ArrayUtils {
    public int findMax(int[] numbers) {
        int maximum = numbers[0];
        for (int number : numbers) {
            if (number > maximum) {
                maximum = number;
            }
        }
        return maximum;
    }
}
"""

PYTHON_FACTORIAL = """\
def factorial(n):
    result = 1
    while n > 1:
        result = result * n
        n = n - 1
    return result
"""


class TestSimilarityEndpointSuccess:
    def _post(self, payload: dict) -> dict:
        resp = client.post("/api/similarity", json=payload)
        assert resp.status_code == 200, f"Unexpected {resp.status_code}: {resp.text}"
        return resp.json()

    def test_identical_code_scores_high(self):
        data = self._post(
            {
                "code_a": PYTHON_FIND_MAX,
                "language_a": "python",
                "code_b": PYTHON_FIND_MAX,
                "language_b": "python",
            }
        )
        assert data["similarity"] >= 95.0
        assert data["verdict"] == "plagiarized"

    def test_cross_language_same_logic(self):
        data = self._post(
            {
                "code_a": PYTHON_FIND_MAX,
                "language_a": "python",
                "code_b": JAVA_FIND_MAX,
                "language_b": "java",
            }
        )
        assert data["similarity"] >= 70.0

    def test_unrelated_code_scores_low(self):
        data = self._post(
            {
                "code_a": PYTHON_FACTORIAL,
                "language_a": "python",
                "code_b": JAVA_FIND_MAX,
                "language_b": "java",
            }
        )
        assert data["similarity"] < 50.0
        assert data["verdict"] == "not_plagiarized"

    def test_response_shape(self):
        data = self._post(
            {
                "code_a": PYTHON_FIND_MAX,
                "language_a": "python",
                "code_b": JAVA_FIND_MAX,
                "language_b": "java",
            }
        )
        required_keys = {
            "similarity", "verdict", "structural_score", "shingle_score",
            "tokens_a", "tokens_b", "matching_ngrams", "reason",
        }
        assert required_keys.issubset(data.keys())
        assert isinstance(data["similarity"], float)
        assert isinstance(data["tokens_a"], int)
        assert isinstance(data["tokens_b"], int)
        assert isinstance(data["matching_ngrams"], int)
        assert isinstance(data["reason"], str)
        assert data["verdict"] in {"plagiarized", "suspicious", "not_plagiarized"}


class TestSimilarityEndpointErrors:
    def test_syntax_error_returns_400(self):
        resp = client.post(
            "/api/similarity",
            json={
                "code_a": "def broken(:\n    return 1",
                "language_a": "python",
                "code_b": PYTHON_FIND_MAX,
                "language_b": "python",
            },
        )
        assert resp.status_code == 400
        body = resp.json()
        assert body["error"] == "syntax_error"
        assert "detail" in body

    def test_too_short_returns_400(self):
        resp = client.post(
            "/api/similarity",
            json={
                "code_a": "x = 1",
                "language_a": "python",
                "code_b": PYTHON_FIND_MAX,
                "language_b": "python",
            },
        )
        assert resp.status_code == 400
        body = resp.json()
        assert body["error"] == "too_short"

    def test_unsupported_language_returns_400(self):
        resp = client.post(
            "/api/similarity",
            json={
                "code_a": PYTHON_FIND_MAX,
                "language_a": "ruby",
                "code_b": PYTHON_FIND_MAX,
                "language_b": "python",
            },
        )
        assert resp.status_code == 422  # Pydantic validation error from field_validator

    def test_missing_field_returns_422(self):
        resp = client.post(
            "/api/similarity",
            json={"code_a": PYTHON_FIND_MAX, "language_a": "python"},
        )
        assert resp.status_code == 422
