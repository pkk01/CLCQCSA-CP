# AGENTS.md
## Rules for the AI IDE building CodeQual (Review 1 — O1 + O2 only)

This file governs what any AI coding agent (Cursor, Claude Code, Copilot
Workspace, etc.) is allowed to build in this repo right now. Read PRD.md,
ARCHITECTURE.md, DATABASE.md and API.md first — this file constrains *how*
those get implemented.

---

## 1. Hard Scope Boundary — Read This First

**Build only what PRD.md Section 4 marks "in scope."** Concretely:

✅ Build:
- `engine/parsing`, `engine/quality`, `engine/validation` — fully working,
  not stubbed.
- `api/` endpoints exactly as specified in API.md — no more, no fewer.
- `db/` schema exactly as specified in DATABASE.md.
- `frontend/` — exactly 4 pages: Analyze, Report, Validation, History.

🚫 Do NOT build, even if it seems natural or "nice to have":
- Authentication, login, user accounts, sessions.
- `engine/similarity/` logic — create **only** the empty interface/stub
  described in ARCHITECTURE.md §3. If asked to "finish" similarity
  detection, refuse and point to this file — it's Review 2 scope.
- A landing/marketing page, settings page, dark mode toggle, or any page
  not in the 4-page list above.
- Docker/Kubernetes/cloud deployment configs.
- Any language grammar beyond the 2 (or 3, if explicitly added) chosen in
  PRD.md.
- Background job queues, websockets, caching layers — the architecture is
  explicitly synchronous request/response for this scope.
- Mock data, placeholder API responses, or "TODO: wire this up later"
  comments in place of real implementation. **Every page must hit a real,
  working endpoint from day one of its own build.** If a page's backend
  isn't ready yet, don't build the page yet either — build backend-first
  per the module order below.

If a request from the user conflicts with this boundary, flag it rather
than silently building outside scope.

---

## 2. Build Order (do not skip ahead)

1. `engine/parsing` — tree-sitter setup + normalization, with unit tests,
   before anything else.
2. `engine/quality` — signal computation on top of the IR, with unit tests.
3. `engine/validation` — harness + fixtures, with a real accuracy number
   printed/testable before touching the API layer.
4. `db/` models + migrations.
5. `api/` routes, wired to `services/` which call `engine/`.
6. `frontend/` — Analyze page first (needs `/api/analyze` working), then
   Report page (needs `/api/analyze/{id}` working), then Validation page,
   then History page last.

Do not scaffold frontend pages before their backing endpoint is real and
tested — this produces the "boilerplate demo page" outcome the project
explicitly wants to avoid.

---

## 3. Coding Conventions

### Python (`engine/`, `api/`)
- Python 3.11, type hints on every function signature.
- Formatting: `black`, linting: `ruff`. Both must pass in CI/pre-commit.
- `engine/` must have **zero imports** from `fastapi`, `sqlalchemy`, or
  anything web/DB-related — it is pure, framework-agnostic Python, testable
  in isolation. This is not a style preference — O3 in Review 2 will import
  `engine/parsing` directly and must not drag in web dependencies.
- Use `dataclasses` for IR types (`FileIR`, `FunctionIR`) — not dicts — so
  the shape is enforced and IDE-navigable.
- Every public function in `engine/quality/*.py` needs a docstring
  explaining the signal it computes and its scoring rationale (reviewers
  will ask "why does this file get 78?").

### TypeScript (`frontend/`)
- Strict TypeScript (`strict: true` in tsconfig).
- Formatting/linting: `prettier` + `eslint`.
- API response types in `frontend/src/api/types.ts` must match API.md
  exactly — if they drift, API.md is the source of truth to fix toward.
- No `any` types on API response handling.
- Functional components + hooks only. No class components.

### General
- No commented-out code left in commits.
- No hardcoded file paths — use config/env for the SQLite path, fixtures
  path, etc.
- Commit messages describe the module touched (e.g.
  `engine/quality: add cyclomatic complexity signal`).

---

## 4. Folder Structure

Follow ARCHITECTURE.md §2 exactly. Do not introduce new top-level
directories (e.g. `src/`, `lib/`, `utils/` at repo root) without updating
ARCHITECTURE.md first — the structure is part of the reviewed deliverable.

---

## 5. What the AI Should / Shouldn't Change

**Should change freely within scope:**
- Anything inside `engine/parsing`, `engine/quality`, `engine/validation`,
  `api/`, `frontend/src/pages` for the 4 approved pages, `db/`.

**Should NOT change without explicit user confirmation:**
- `fixtures/labels.json` and the fixture files themselves — these are the
  labelled evidence set; silently "fixing" a label to make accuracy look
  better invalidates the validation (this is exactly what NT-2/NT-3 in the
  spec are guarding against — superficial signals / false confidence).
- API.md's endpoint contracts — if an endpoint needs to change shape,
  update API.md in the same change, don't let frontend/backend silently
  drift apart.
- The composite scoring formula/weights in `scorer.py` — document any
  change and why, since it's graded evidence (KPI-1 baseline).

**Never do:**
- Add `engine/similarity` detection logic (see §1).
- Delete or bypass the validation harness to "speed up" development.
- Introduce a new database engine (Postgres, Mongo, etc.) — SQLite is the
  Review 1 choice; revisit only when DATABASE.md is updated.

---

## 6. Testing Requirements

- `engine/parsing` — unit tests per supported language: known input source
  → expected IR shape (function count, nesting depth, etc.).
- `engine/quality` — unit tests per signal: hand-crafted snippets with a
  known expected complexity/nesting/score.
- `engine/validation` — an integration test that runs the harness against
  the checked-in fixtures and asserts it completes without error and
  returns a `0.0–1.0` accuracy float (not a specific accuracy — that's
  reported, not asserted, since it's the evidence itself).
- `api/` — endpoint tests (FastAPI `TestClient`) for every route in API.md,
  covering both the success shape and the documented error shapes.
- `frontend/` — component test per page verifying it renders real data from
  a mocked API response matching API.md's schema, and handles the
  documented error responses (e.g. Report page shows the 404 message
  correctly).
- **No PR/change is complete without tests for the code it adds.** This
  matches NFR-5 (maintainability: automated tests) in the project spec.

---

## 7. Definition of Done for Review 1

A feature is done only when:
1. It matches PRD.md scope exactly (nothing extra, nothing missing).
2. It's covered by the tests described in §6.
3. It uses real data end to end — no mock/placeholder in the demo path.
4. `fixtures/`-based validation accuracy is printed/visible somewhere a
   reviewer can see it without reading logs (Validation page).
5. `black`/`ruff` (Python) and `prettier`/`eslint` (TS) pass clean.
