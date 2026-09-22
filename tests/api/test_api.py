"""API endpoint tests covering all routes and error conditions specified in API.md."""

from io import BytesIO

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "python" in data["grammars_loaded"]
    assert "java" in data["grammars_loaded"]


def test_analyze_valid_source_returns_report() -> None:
    response = client.post(
        "/api/analyze",
        files={"files": ("valid.py", BytesIO(b"def hello():\n    return 1\n"), "text/plain")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "complete"
    assert "composite_score" in data
    assert data["files"][0]["functions"][0]["name"] == "hello"


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


def test_runs_list_and_pagination() -> None:
    # Ensure at least one run exists
    client.post(
        "/api/analyze",
        files={"files": ("test.py", BytesIO(b"def f():\n    return 42\n"), "text/plain")},
    )

    response = client.get("/api/runs?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "runs" in data
    assert isinstance(data["runs"], list)
    assert data["total"] >= 1
    run = data["runs"][0]
    assert "run_id" in run
    assert "created_at" in run
    assert "source_label" in run
    assert "composite_score" in run
    assert "status" in run


def test_validation_endpoints_full_lifecycle() -> None:
    # 1. Trigger validation run
    post_res = client.post("/api/validation/run")
    assert post_res.status_code == 200
    post_data = post_res.json()
    assert "validation_run_id" in post_data
    assert post_data["validation_run_id"] is not None
    assert "overall_accuracy" in post_data
    assert "fixture_count" in post_data
    assert "language_breakdown" in post_data
    assert "results" in post_data
    val_id = post_data["validation_run_id"]

    # 2. Get latest validation run
    latest_res = client.get("/api/validation/latest")
    assert latest_res.status_code == 200
    latest_data = latest_res.json()
    assert latest_data["validation_run_id"] is not None
    assert latest_data["overall_accuracy"] is not None

    # 3. Get validation run by ID
    id_res = client.get(f"/api/validation/{val_id}")
    assert id_res.status_code == 200
    id_data = id_res.json()
    assert id_data["validation_run_id"] == val_id
    assert id_data["overall_accuracy"] == post_data["overall_accuracy"]

    # 4. Nonexistent validation ID returns 404
    missing_res = client.get("/api/validation/999999999")
    assert missing_res.status_code == 404
    assert missing_res.json()["error"] == "not_found"
