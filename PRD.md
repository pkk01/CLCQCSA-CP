# PRD.md — Product Requirements Document
## CodeQual — Cross-Language Code Quality & Correctness Analyzer
### (CLOUD-36 · Capstone Project I scope — Review 1)

---

## 1. What We're Building

A web application that ingests source code across multiple programming
languages, parses it into a **unified, language-agnostic representation**
using tree-sitter, and computes **code quality and correctness signals**
against that representation. The system is validated by running it against
a labelled dataset of known-good and known-bad code and reporting measured
accuracy.

This is the **O1 (cross-language parsing foundation)** and **O2 (reference
quality/correctness engine)** portion of the full CLOUD-36 capstone. It is
the reproducible baseline that the Review 2 deliverable — O3, cross-language
similarity/plagiarism detection — will later be measured against.

**This is not a demo or prototype.** Every page and endpoint described here
must be fully functional end to end: upload → parse → score → report,
backed by a real validation harness with real accuracy numbers.

---

## 2. Problem Statement

Programming-education and developer-assistance tools need a reliable way to
judge code quality and correctness that works the same way regardless of
source language. Today this is done per-language, inconsistently, with no
common representation and no measured accuracy against labelled examples.
This project builds that common reference layer.

---

## 3. Target Users (for this review)

- **Primary — capstone evaluators/reviewers**: need to see a working system
  end to end, a validation report, and evidence the accuracy claim is real
  (not eyeballed).
- **Secondary — the project team itself**: uses the same tool during
  development to sanity-check the quality engine and to prep the O3
  similarity module in Review 2 without re-touching this layer.
- **Downstream (not this review) — developers/students**: eventual users of
  the finished CLOUD-36 system once O3–O5 are complete.

---

## 4. Scope for Review 1

### In scope (must be fully working, no stubs)
1. Upload one or more source files (or a small repo as a zip) through the
   web UI.
2. Automatic language detection (by file extension) for **at minimum 2
   languages** (recommend: **Python + Java**, extendable to JavaScript).
3. Parse every file with tree-sitter into a CST, then normalize into a
   language-agnostic intermediate representation (IR): functions, branches,
   loops, nesting depth, LOC, imports, function length.
4. Compute quality/correctness signals from the IR:
   - Cyclomatic complexity (per function + aggregate)
   - Nesting depth
   - Function length / long-function flags
   - Static correctness checks (syntax validity, unreachable code,
     undefined-name style checks where feasible per language)
   - Comment density
   - Composite quality score (0–100) per file and per function
5. Render a report in the UI: composite score, per-function breakdown,
   flagged issues, and the raw signal values.
6. A **validation harness**: a labelled fixture set (known-good / known-bad
   code samples per language) that the engine is run against automatically,
   producing an accuracy report (this is the O2 evidence requirement:
   "validated against known-good/bad code").
7. A validation report page in the UI showing current measured accuracy,
   per-language breakdown, and which fixtures failed.
8. Persist every analysis run and every validation run so results are
   reproducible and reviewable later (not recomputed live for the
   reviewer).

### Explicitly out of scope for Review 1
- **O3 — Similarity/duplication/plagiarism detection.** Not implemented.
  Reserve a clean module interface (`engine/similarity/`) so it can be
  built in Review 2 without touching O1/O2 code, but write no detection
  logic there now.
- O4 (full system integration, failure-pattern surfacing across O2+O3) and
  O5 (independent acceptance, negative-test/fault-injection campaign) —
  these require O3 to exist first.
- User authentication / multi-user accounts.
- Production deployment, containerized fault-injection testbed, cloud
  hosting.
- Any language beyond the 2 (optionally 3) chosen for this review.
- Real-time/streaming analysis, IDE plugins, CI integration.

---

## 5. Features (Review 1 build list)

| # | Feature | Priority |
|---|---|---|
| F1 | File/repo upload UI | Must |
| F2 | Language auto-detection | Must |
| F3 | Tree-sitter parsing → normalized IR (O1) | Must |
| F4 | Quality/correctness signal computation (O2) | Must |
| F5 | Composite scoring | Must |
| F6 | Analysis report page (per-file, per-function) | Must |
| F7 | Fixture-based validation harness | Must |
| F8 | Validation/accuracy report page | Must |
| F9 | Persisted run history (list past analyses/validations) | Should |
| F10 | Multi-file/repo batch upload | Should |
| F11 | Export report (JSON/PDF) | Could |
| F12 | Similarity detection | **Not this review** |

---

## 6. Business / Academic Requirements

Mapped directly to the CLOUD-36 capstone charter:

- **CP1 Gate 1** — problem, scope, evidence and acceptance plan approved →
  satisfied by this PRD + ARCHITECTURE.md.
- **CP1 Gate 2** — "a reproducible reference and an integrated vertical
  slice are demonstrated" → satisfied by F1–F8 working end to end with real
  fixture data, not mocked output.
- **Deliverable D1** — problem charter, requirements, system boundary,
  architecture (this doc + ARCHITECTURE.md).
- **Deliverable D2** — "Reproducible Compute code-quality/correctness
  signals with fixtures or protocol, oracle, tests, baseline results and
  resource profile" → satisfied by F7/F8 and the fixtures directory.
- **KPI-1 (quality-signal accuracy)** — must be measured and reported, not
  asserted. This review establishes the **baseline value** that Review 2's
  O3 contribution will later be compared against.

---

## 7. User Flows

### Flow 1 — Analyze code
1. User lands on the Analyze page.
2. User uploads a file or a small zip of files.
3. System detects language per file, rejects unsupported languages with a
   clear message (does not silently skip).
4. System parses, computes signals, stores the run, redirects to the report
   page for that run.
5. Report page shows: composite score, per-function table (name, complexity,
   nesting depth, length, flags), and any correctness issues found.

### Flow 2 — Run/view validation
1. User opens the Validation page.
2. User triggers "Run validation" (executes engine against the fixture set)
   or views the most recent stored validation run.
3. System shows: overall accuracy %, per-language accuracy, a table of
   fixtures with expected label vs. predicted label, and which ones failed.

### Flow 3 — Review run history
1. User opens History page.
2. Sees a list of past analysis runs and validation runs with timestamps
   and summary scores.
3. Clicking a row opens that run's full report (Flow 1 or Flow 2 view,
   loaded from stored data, not recomputed).

---

## 8. Success Criteria for This Review

- All 3 pages (Analyze, Report, Validation/History) fully functional against
  real backend endpoints — **zero placeholder/mock data**.
- Validation harness runs against ≥15–20 labelled fixtures per language and
  produces a real, reproducible accuracy number.
- A reviewer can upload arbitrary Python/Java code live during the demo and
  get a correct, non-crashing report.
- Every run is persisted and re-viewable without recomputation.
