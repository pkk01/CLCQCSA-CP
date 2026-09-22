import { describe, it, expect, vi } from "vitest";
import React from "react";
import { render, screen, fireEvent, act } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";
import { Header } from "../../frontend/src/components/Header";
import { ReportPage } from "../../frontend/src/pages/ReportPage";
import { AnalyzePage } from "../../frontend/src/pages/AnalyzePage";
import { ValidationPage } from "../../frontend/src/pages/ValidationPage";
import { HistoryPage } from "../../frontend/src/pages/HistoryPage";
import type { AnalysisResponse } from "../../frontend/src/api/types";

// Mock API client functions so jsdom does not initiate real HTTP requests
vi.mock("../../frontend/src/api/client", () => ({
  uploadAndAnalyze: vi.fn(),
  fetchAnalysisRun: vi.fn().mockResolvedValue({
    run_id: 42,
    status: "complete",
    composite_score: 85.0,
    language_summary: { python: 1 },
    files: [],
  }),
  fetchRuns: vi.fn().mockResolvedValue({ total: 0, runs: [] }),
  triggerValidation: vi.fn().mockResolvedValue({
    validation_run_id: 1,
    overall_accuracy: 0.9,
    fixture_count: 10,
    language_breakdown: { python: 0.9 },
    threshold_used: 60.0,
    results: [],
  }),
  fetchLatestValidation: vi.fn().mockResolvedValue({ validation_run_id: null }),
  extractErrorMessage: vi.fn().mockReturnValue("Error occurred"),
}));

describe("Header navigation", () => {
  it("renders CodeQual brand and 4 navigation tabs", () => {
    const handleNavigate = vi.fn();
    render(<Header currentPage="Analyze" onNavigate={handleNavigate} />);

    expect(screen.getByText("CodeQual")).toBeInTheDocument();
    expect(screen.getByText("Analyze")).toBeInTheDocument();
    expect(screen.getByText("Report")).toBeInTheDocument();
    expect(screen.getByText("Validation")).toBeInTheDocument();
    expect(screen.getByText("History")).toBeInTheDocument();

    fireEvent.click(screen.getByText("Validation"));
    expect(handleNavigate).toHaveBeenCalledWith("Validation");
  });
});

describe("AnalyzePage component", () => {
  it("renders file upload and snippet inputs", () => {
    render(<AnalyzePage onAnalysisComplete={vi.fn()} />);

    expect(screen.getByText("Analyze Source Code")).toBeInTheDocument();
    expect(screen.getByText(/Upload Source Files/)).toBeInTheDocument();
    expect(screen.getByText(/Paste Code Snippet/)).toBeInTheDocument();
    expect(screen.getByText("Run Quality Analysis")).toBeInTheDocument();
  });
});

describe("ReportPage component", () => {
  const mockReport: AnalysisResponse = {
    run_id: 42,
    status: "complete",
    composite_score: 84.5,
    language_summary: { python: 1 },
    files: [
      {
        file_id: 101,
        filename: "test.py",
        language: "python",
        loc: 15,
        composite_score: 84.5,
        functions: [
          {
            name: "calculate_total",
            start_line: 1,
            end_line: 10,
            cyclomatic_complexity: 2,
            nesting_depth: 1,
            length_lines: 10,
            flags: [],
          },
        ],
      },
    ],
  };

  it("renders composite score and function table from report data", () => {
    render(
      <ReportPage
        initialReport={mockReport}
        onNavigateToAnalyze={vi.fn()}
      />
    );

    expect(screen.getByText("Analysis Report")).toBeInTheDocument();
    expect(screen.getByText("Run #42")).toBeInTheDocument();
    expect(screen.getByText("84.5")).toBeInTheDocument();
    expect(screen.getByText("test.py")).toBeInTheDocument();
    expect(screen.getByText("calculate_total")).toBeInTheDocument();
  });

  it("renders empty state when no report is provided", () => {
    render(
      <ReportPage
        initialReport={null}
        onNavigateToAnalyze={vi.fn()}
      />
    );

    expect(screen.getByText("No analysis report loaded")).toBeInTheDocument();
    expect(screen.getByText("Go to Analyze")).toBeInTheDocument();
  });
});

describe("ValidationPage component", () => {
  it("renders validation harness interface", async () => {
    await act(async () => {
      render(<ValidationPage />);
    });
    expect(screen.getByText("Validation Harness & Accuracy")).toBeInTheDocument();
    expect(screen.getByText("Run Full Validation Harness")).toBeInTheDocument();
  });
});

describe("HistoryPage component", () => {
  it("renders history interface with title and refresh action", async () => {
    await act(async () => {
      render(<HistoryPage onSelectRun={vi.fn()} onNavigateToAnalyze={vi.fn()} />);
    });
    expect(screen.getByText("Analysis History")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /refresh/i })).toBeInTheDocument();
  });
});
