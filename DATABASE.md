# DATABASE.md
## CodeQual — Review 1 Schema (O1 + O2 persistence only)

Engine: **SQLite** via SQLAlchemy (file: `capstone.db`), Alembic for
migrations. Schema is intentionally minimal — only what's needed to persist
and re-view analysis and validation runs. No user/auth tables this review.

---

## 1. Tables

### `analysis_runs`
One row per upload/analyze action.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | INTEGER | PK, autoincrement | |
| created_at | DATETIME | NOT NULL, default now | |
| status | TEXT | NOT NULL, default 'complete' | `pending` \| `complete` \| `failed` |
| source_label | TEXT | NOT NULL | filename or repo/zip name shown in UI |
| language_summary | TEXT | NOT NULL | JSON: `{"python": 3, "java": 1}` file counts |
| composite_score | FLOAT | NULL | overall run score, null if failed |
| error_message | TEXT | NULL | populated if status = failed |

### `analyzed_files`
One row per file within a run.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | INTEGER | PK, autoincrement | |
| run_id | INTEGER | FK → analysis_runs.id, NOT NULL | |
| filename | TEXT | NOT NULL | |
| language | TEXT | NOT NULL | detected language |
| loc | INTEGER | NOT NULL | |
| composite_score | FLOAT | NOT NULL | per-file score |
| ir_json | TEXT | NOT NULL | serialized normalized IR (for report re-render without re-parsing) |

### `function_scores`
One row per function found in a file — powers the per-function report table.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | INTEGER | PK, autoincrement | |
| file_id | INTEGER | FK → analyzed_files.id, NOT NULL | |
| name | TEXT | NOT NULL | |
| start_line | INTEGER | NOT NULL | |
| end_line | INTEGER | NOT NULL | |
| cyclomatic_complexity | INTEGER | NOT NULL | |
| nesting_depth | INTEGER | NOT NULL | |
| length_lines | INTEGER | NOT NULL | |
| flags_json | TEXT | NOT NULL | JSON list, e.g. `["long_function", "deep_nesting"]` |

### `validation_runs`
One row per execution of the fixture validation harness.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | INTEGER | PK, autoincrement | |
| created_at | DATETIME | NOT NULL, default now | |
| overall_accuracy | FLOAT | NOT NULL | KPI-1 evidence value |
| fixture_count | INTEGER | NOT NULL | |
| language_breakdown_json | TEXT | NOT NULL | `{"python": 0.91, "java": 0.87}` |
| threshold_used | FLOAT | NOT NULL | documented score cutoff used to predict good/bad |

### `fixture_results`
One row per fixture per validation run — the auditable evidence trail
required by the spec's "independent oracle" language.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | INTEGER | PK, autoincrement | |
| validation_run_id | INTEGER | FK → validation_runs.id, NOT NULL | |
| fixture_id | TEXT | NOT NULL | matches `fixtures/labels.json` key |
| language | TEXT | NOT NULL | |
| expected_label | TEXT | NOT NULL | `good` \| `bad` |
| predicted_label | TEXT | NOT NULL | `good` \| `bad` |
| predicted_score | FLOAT | NOT NULL | |
| correct | BOOLEAN | NOT NULL | expected_label == predicted_label |

---

## 2. Relationships

```
analysis_runs (1) ──< (many) analyzed_files (1) ──< (many) function_scores
validation_runs (1) ──< (many) fixture_results
```

No relationship between `analysis_runs` and `validation_runs` — they are
independent flows (Flow 1 vs Flow 2 in the PRD).

---

## 3. Indexes / Constraints

- `analyzed_files.run_id` — indexed (FK lookup for report page).
- `function_scores.file_id` — indexed (FK lookup for report page).
- `fixture_results.validation_run_id` — indexed.
- `fixture_results(validation_run_id, fixture_id)` — unique composite index
  (a fixture should appear once per validation run).
- `analysis_runs.created_at` and `validation_runs.created_at` — indexed
  (History page sorts/filters by recency).
- Foreign keys enforced with `ON DELETE CASCADE` (deleting a run deletes its
  files/functions; deleting a validation run deletes its fixture results).

---

## 4. Explicitly Not Modeled This Review

- No `users` table — no auth in scope.
- No `similarity_results` table — O3 is not implemented; this table is
  added in Review 2 alongside the real `engine/similarity` logic.
- No soft-deletes/versioning — not required for a capstone review demo.
