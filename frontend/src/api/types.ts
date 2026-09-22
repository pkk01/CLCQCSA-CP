/**
 * TypeScript definitions matching API.md response schemas exactly.
 */

export interface FunctionReport {
  name: string;
  start_line: number;
  end_line: number;
  cyclomatic_complexity: number;
  nesting_depth: number;
  length_lines: number;
  flags: string[];
}

export interface FileReport {
  file_id: number;
  filename: string;
  language: string;
  loc: number;
  composite_score: number;
  functions: FunctionReport[];
}

export interface AnalysisResponse {
  run_id: number;
  status: string;
  composite_score: number | null;
  language_summary: Record<string, number>;
  files: FileReport[];
}

export interface RunSummary {
  run_id: number;
  created_at: string;
  source_label: string;
  composite_score: number | null;
  status: string;
}

export interface RunsListResponse {
  total: number;
  runs: RunSummary[];
}

export interface FixtureResultResponse {
  fixture_id: string;
  language: string;
  expected_label: string;
  predicted_label: string;
  predicted_score: number;
  correct: boolean;
}

export interface ValidationResponse {
  validation_run_id: number | null;
  overall_accuracy?: number;
  fixture_count?: number;
  language_breakdown?: Record<string, number>;
  threshold_used?: number;
  results?: FixtureResultResponse[];
}

export interface ApiError {
  error: string;
  detail: string;
}

export interface HealthResponse {
  status: string;
  grammars_loaded: string[];
}
