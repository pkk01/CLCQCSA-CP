# ARCHITECTURE.md
## CodeQual — Cross-Language Code Quality & Correctness Analyzer
### Review 1 scope (O1 + O2)

---

## 1. Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Backend | **Python 3.11 + FastAPI** | tree-sitter's Python bindings are the most mature; FastAPI gives typed request/response models and free OpenAPI docs, useful for API.md validation |
| Parsing | **tree-sitter** + `tree-sitter-python`, `tree-sitter-java` (optionally `tree-sitter-javascript`) | Cross-language CST parsing — the O1 requirement |
| DB | **SQLite** (file-based, via SQLAlchemy) | Zero-infra for a capstone review; schema is portable to Postgres later without code changes (SQLAlchemy ORM) |
| Frontend | **React 18 + TypeScript + Vite** | Fast dev loop, typed API contracts shared conceptually with API.md |
| Styling | **Tailwind CSS** | Fast to build real (non-boilerplate) working pages without a design system overhead |
| HTTP client | **axios** | Simple typed API calls from frontend |
| Testing (backend) | **pytest** | Required for the validation harness and engine unit tests |
| Testing (frontend) | **Vitest + React Testing Library** | Component-level tests for the 3 real pages |

No auth library, no message queue, no container orchestration — out of
scope for this review (see AGENTS.md for hard boundaries).

---

## 2. High-Level Structure

```
capstone/
├── engine/                    # Pure Python, no web framework dependency
│   ├── parsing/
│   │   ├── grammars.py        # tree-sitter language loading (Python, Java, ...)
│   │   ├── parser.py          # file -> CST
│   │   └── normalize.py       # CST -> language-agnostic IR (O1 deliverable)
│   ├── quality/
│   │   ├── complexity.py      # cyclomatic complexity, nesting depth
│   │   ├── correctness.py     # static correctness checks
│   │   ├── style.py           # comment density, function length, naming
│   │   └── scorer.py          # combines signals -> composite score (O2 deliverable)
│   ├── similarity/            # STUB ONLY — interface reserved for Review 2 (O3)
│   │   └── __init__.py        # do not implement detection logic here yet
│   └── validation/
│       ├── harness.py         # runs engine against fixtures, computes accuracy
│       └── fixtures_loader.py
├── fixtures/
│   ├── python/good/ ...  bad/ ...
│   ├── java/good/ ...    bad/ ...
│   └── labels.json        # fixture_id -> {language, expected_label}
├── api/
│   ├── main.py             # FastAPI app entrypoint
│   ├── routes/
│   │   ├── analyze.py
│   │   ├── validation.py
│   │   └── runs.py
│   ├── models/              # Pydantic request/response schemas
│   ├── db/
│   │   ├── models.py         # SQLAlchemy ORM models
│   │   ├── session.py
│   │   └── migrations/       # Alembic
│   └── services/             # glue between routes and engine/
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── AnalyzePage.tsx
│   │   │   ├── ReportPage.tsx
│   │   │   ├── ValidationPage.tsx
│   │   │   └── HistoryPage.tsx
│   │   ├── components/
│   │   ├── api/               # typed axios client, matches API.md exactly
│   │   └── App.tsx
│   └── vite.config.ts
├── tests/
│   ├── engine/
│   ├── api/
│   └── frontend/
├── PRD.md / ARCHITECTURE.md / DATABASE.md / API.md / AGENTS.md
└── README.md
```

---

## 3. Module Responsibilities

### `engine/parsing`
- Loads tree-sitter grammars once at startup.
- `parser.py`: takes raw source + language, returns a tree-sitter tree.
- `normalize.py`: walks the tree via tree-sitter queries and emits a
  **language-agnostic IR** — a plain Python dataclass structure like:
  ```
  FileIR(
    language, loc, functions=[FunctionIR(name, start_line, end_line,
    branch_count, loop_count, max_nesting_depth, param_count, ...)],
    imports=[...], comment_lines=int
  )
  ```
  This IR is the single contract every quality signal and, later, O3's
  similarity module consumes. **No quality logic lives here.**

### `engine/quality`
- Each file (`complexity.py`, `correctness.py`, `style.py`) takes a
  `FileIR` and returns a signal dict. Pure functions, fully unit-testable
  without any web/DB dependency.
- `scorer.py` combines signal dicts into one composite score. The weighting
  formula must be documented in-code (docstring) since reviewers will ask
  how the composite score is derived.

### `engine/similarity` (stub only)
- Contains only a documented interface (e.g. an abstract function signature
  `def detect_similarity(file_irs: list[FileIR]) -> SimilarityReport`) and a
  `NotImplementedError` body. This proves the architecture already
  anticipates O3 without building it — a strong Gate 1 evidence point.

### `engine/validation`
- `fixtures_loader.py` reads `fixtures/labels.json` + the fixture files.
- `harness.py` runs every fixture through parsing → quality → scorer,
  compares predicted label (e.g. score above/below a documented threshold)
  against the expected label, and outputs an accuracy report structure —
  this is what KPI-1 is measured from.

### `api/`
- Thin layer only. Routes call `services/` which call `engine/` and persist
  results via `db/`. **No business logic in route handlers.**
- `services/analyze_service.py`: orchestrates parse → score → persist →
  return run ID.
- `services/validation_service.py`: orchestrates harness run → persist →
  return summary.

### `frontend/`
- 4 real pages only, each backed by real endpoints (see API.md):
  `AnalyzePage` (upload + trigger), `ReportPage` (view one run),
  `ValidationPage` (trigger/view validation), `HistoryPage` (list all runs).
- No landing/marketing page, no auth screens, no settings page — not in
  scope.

---

## 4. How Components Communicate

```
Browser (React)
   │  fetch/axios, JSON over HTTP
   ▼
FastAPI (api/)
   │  Python function calls (in-process, no queue for this scope)
   ▼
services/  ──calls──▶  engine/ (pure Python, framework-agnostic)
   │
   ▼
db/ (SQLAlchemy → SQLite file)
```

- All communication is synchronous REST + JSON. No websockets, no async job
  queue — analysis and validation runs are fast enough (single files /
  small fixture sets) to return in-request. If a real repo upload proves
  slow in testing, add a simple polling status field on the run record
  (`status: pending|complete|failed`) rather than introducing new infra.
- The engine package has **zero imports from `api/` or `frontend/`** — it
  must be independently testable and reusable when O3 is added in Review 2.

---

## 5. Non-Goals for This Architecture (Review 1)

- No microservices — single FastAPI process.
- No containerization/orchestration required to run or demo this review
  (the spec's containerized testbed is for the later fault-injection
  campaign in O4/O5).
- No caching layer, no background workers, no cloud deployment.
