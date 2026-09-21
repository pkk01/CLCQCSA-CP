# API.md
## CodeQual — Review 1 API Contract (O1 + O2 endpoints only)

Base URL: `/api`
Format: JSON over HTTP. FastAPI auto-generates OpenAPI docs at `/docs` —
this file is the human-readable source of truth the frontend and backend
must both match.

---

## 1. Authentication

**None in Review 1.** No login, no tokens, no API keys. All endpoints are
open on localhost/demo deployment. (Do not scaffold auth middleware — see
AGENTS.md boundaries.)

---

## 2. Endpoints

### `POST /api/analyze`
Upload and analyze one or more source files.

**Request:** `multipart/form-data`
- `files`: one or more files (`.py`, `.java`, optionally `.js`)

**Response `200`:**
```json
{
  "run_id": 42,
  "status": "complete",
  "composite_score": 78.4,
  "language_summary": { "python": 2, "java": 1 },
  "files": [
    {
      "file_id": 101,
      "filename": "app.py",
      "language": "python",
      "loc": 214,
      "composite_score": 82.1,
      "functions": [
        {
          "name": "process_data",
          "start_line": 12,
          "end_line": 40,
          "cyclomatic_complexity": 7,
          "nesting_depth": 3,
          "length_lines": 28,
          "flags": ["deep_nesting"]
        }
      ]
    }
  ]
}
```

**Response `400`** — unsupported language / unparseable file:
```json
{ "error": "unsupported_language", "detail": "'.rb' is not a supported language in this review (supported: python, java)" }
```

**Response `422`** — no files provided (FastAPI validation default).

---

### `GET /api/analyze/{run_id}`
Fetch a previously computed run (Report page load / History page click-through).
Returns stored data — **must not re-parse or recompute**.

**Response `200`:** same shape as `POST /api/analyze` response body.

**Response `404`:**
```json
{ "error": "not_found", "detail": "No analysis run with id 42" }
```

---

### `GET /api/runs`
List past analysis runs (History page).

**Query params:** `limit` (default 20), `offset` (default 0)

**Response `200`:**
```json
{
  "total": 5,
  "runs": [
    {
      "run_id": 42,
      "created_at": "2026-09-20T10:15:00Z",
      "source_label": "app.py + 2 more",
      "composite_score": 78.4,
      "status": "complete"
    }
  ]
}
```

---

### `POST /api/validation/run`
Trigger the fixture validation harness (engine/validation/harness.py) end
to end and persist the result.

**Request:** empty body (uses the checked-in `fixtures/` directory).

**Response `200`:**
```json
{
  "validation_run_id": 7,
  "overall_accuracy": 0.89,
  "fixture_count": 40,
  "language_breakdown": { "python": 0.91, "java": 0.87 },
  "threshold_used": 60.0,
  "results": [
    {
      "fixture_id": "python_bad_012",
      "language": "python",
      "expected_label": "bad",
      "predicted_label": "bad",
      "predicted_score": 34.2,
      "correct": true
    }
  ]
}
```

**Response `500`** — harness crashed (e.g. malformed fixture):
```json
{ "error": "validation_failed", "detail": "Fixture 'java_good_004' failed to parse: <tree-sitter error>" }
```

---

### `GET /api/validation/{validation_run_id}`
Fetch a previously computed validation run (Validation page load).

**Response `200`:** same shape as `POST /api/validation/run` response body.

**Response `404`:** same shape as analyze 404.

---

### `GET /api/validation/latest`
Convenience endpoint — returns the most recent validation run, or `null` if
none has been run yet (Validation page default view).

**Response `200`:**
```json
{ "validation_run_id": 7, "overall_accuracy": 0.89, "...": "..." }
```
or
```json
{ "validation_run_id": null }
```

---

### `GET /api/health`
Liveness check.

**Response `200`:**
```json
{ "status": "ok", "grammars_loaded": ["python", "java"] }
```

---

## 3. Error Handling Convention

All error responses follow one shape:
```json
{ "error": "<machine_readable_code>", "detail": "<human readable message>" }
```

| HTTP status | Meaning |
|---|---|
| 400 | Bad input (unsupported language, empty file) |
| 404 | Run/validation ID not found |
| 422 | Request shape invalid (FastAPI/Pydantic validation) |
| 500 | Engine crashed unexpectedly — must still return this shape, never a raw stack trace |

Frontend must render `detail` directly to the user for 400/404; for 500,
show a generic "analysis failed" message and log `detail` to console.

---

## 4. Explicitly Not in Review 1 API Surface

- No `/api/similarity/*` endpoints — O3 not implemented.
- No `/api/auth/*` — no auth this review.
- No pagination beyond simple limit/offset on `/api/runs` — no complex
  filtering/search required yet.
