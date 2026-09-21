from io import BytesIO

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_analyze_valid_source_returns_report() -> None:
    response = client.post(
        "/api/analyze",
        files={"files": ("valid.py", BytesIO(b"def hello():\n    return 1\n"), "text/plain")},
    )

    assert response.status_code == 200
    assert response.json()["files"][0]["functions"][0]["name"] == "hello"


def test_analyze_invalid_source_returns_flat_error() -> None:
    response = client.post(
        "/api/analyze",
        files={"files": ("invalid.py", BytesIO(b"def broken(:\n    return 1\n"), "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["error"] == "invalid_source"
    assert "could not be parsed" in response.json()["detail"]


def test_analyze_empty_and_unsupported_files_return_errors() -> None:
    empty = client.post("/api/analyze", files={"files": ("empty.py", BytesIO(b""), "text/plain")})
    unsupported = client.post("/api/analyze", files={"files": ("notes.rb", BytesIO(b"puts 1"), "text/plain")})

    assert empty.status_code == 400
    assert empty.json()["error"] == "invalid_source"
    assert unsupported.status_code == 400
    assert unsupported.json()["error"] == "unsupported_language"


def test_analyze_rejects_code_written_in_the_wrong_language() -> None:
    java_as_python = client.post(
        "/api/analyze",
        files={"files": ("wrong.py", BytesIO(b"class Demo { int add(int a, int b) { return a + b; } }"), "text/plain")},
    )
    python_as_java = client.post(
        "/api/analyze",
        files={"files": ("wrong.java", BytesIO(b"def add(a, b):\n    return a + b\n"), "text/plain")},
    )

    assert java_as_python.status_code == 400
    assert java_as_python.json()["error"] == "invalid_source"
    assert python_as_java.status_code == 400
    assert python_as_java.json()["error"] == "invalid_source"


def test_missing_analysis_returns_documented_error() -> None:
    response = client.get("/api/analyze/999999999")

    assert response.status_code == 404
    assert response.json()["error"] == "not_found"
