# CodeQual

**Cross-Language Code Quality & Correctness Analyzer**  
*Capstone Project Review 1 Deliverable (Objectives O1 + O2)*

---

## Overview

CodeQual analyzes source code written in multiple programming languages (Python and Java for Review 1) through a unified, language-agnostic Intermediate Representation (IR). It computes deterministic quality signals—including cyclomatic complexity, maximum nesting depth, function length, and static correctness issues—and yields an auditable composite score (0–100).

CodeQual also includes an **independent validation oracle** that evaluates the scoring engine against a ground-truth labeled fixture dataset, producing quantifiable accuracy evidence (KPI-1).

---

## System Architecture

```
capstone/
├── engine/
│   ├── parsing/           # tree-sitter language loading, parsing, IR normalization (O1)
│   │   ├── grammars.py
│   │   ├── parser.py
│   │   └── normalize.py
│   ├── quality/           # pure quality signals & composite scoring (O2)
│   │   ├── complexity.py
│   │   ├── correctness.py
│   │   ├── style.py
│   │   └── scorer.py
│   ├── similarity/        # O3 interface stub reserved for Review 2
│   │   └── __init__.py
│   └── validation/        # Ground-truth test oracle harness
│       ├── harness.py
│       └── fixtures_loader.py
├── api/
│   ├── main.py            # FastAPI entrypoint
│   ├── routes/            # Route modules (analyze, runs, validation)
│   ├── models/            # Pydantic request/response schemas matching API.md
│   ├── services/          # Business logic orchestrators
│   └── db/                # SQLite + SQLAlchemy models + Alembic migrations
├── frontend/              # React 18 + TypeScript + Vite + Tailwind CSS + Axios
│   ├── src/
│   │   ├── pages/         # AnalyzePage, ReportPage, ValidationPage, HistoryPage
│   │   ├── components/    # Reusable UI components (Header, etc.)
│   │   ├── api/           # Typed Axios client matching API.md
│   │   └── App.tsx
├── fixtures/              # Labeled ground-truth benchmarks (Python & Java)
└── tests/
    ├── engine/            # Unit tests for parsing, quality, and harness
    ├── api/               # Integration tests covering all API endpoints
    └── frontend/          # Component tests for frontend pages (Vitest)
```

---

## Quick Start

### 1. Prerequisites
- Python 3.11 or 3.12
- Node.js 18+ and npm

### 2. Backend Setup
```bash
# Activate existing virtualenv (Windows)
.venv\Scripts\activate

# Run database migrations (or auto-created on startup)
alembic upgrade head

# Start FastAPI server (runs on port 8000)
uvicorn api.main:app --reload --port 8000
```
Interactive OpenAPI documentation will be available at `http://localhost:8000/docs`.

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## Running Tests

### Backend Unit & Integration Tests (pytest)
```bash
.venv\Scripts\python.exe -m pytest tests/ -v
```

### Frontend Component Tests (vitest)
```bash
cd frontend
npm test
```

### Direct Validation Harness Evaluation
To run the ground-truth validation harness and inspect engine accuracy directly:
```bash
.venv\Scripts\python.exe -c "from pathlib import Path; from engine.validation import run_validation; r = run_validation(Path('fixtures')); print(f'Accuracy: {r.overall_accuracy:.2%} across {r.fixture_count} fixtures'); print('Breakdown:', r.language_breakdown)"
```

---

## Pages & User Flows

1. **Analyze Page (`/`)**: Upload `.py` or `.java` files, or paste code snippets directly into the editor.
2. **Report Page**: Displays the composite quality score, detected functions, cyclomatic complexity, nesting depth, length, and code quality flags.
3. **Validation Page**: Executes the automated benchmark oracle across all labeled fixtures, displaying real-time accuracy and pass/fail audit logs.
4. **History Page**: Review past analysis runs stored in SQLite and click through to inspect historical reports.
