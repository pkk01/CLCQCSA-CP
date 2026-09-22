import React, { useEffect, useState } from "react";
import { fetchAnalysisRun, extractErrorMessage } from "../api/client";
import type { AnalysisResponse } from "../api/types";

interface ReportPageProps {
  initialReport: AnalysisResponse | null;
  runIdToLoad?: number | null;
  onNavigateToAnalyze: () => void;
  onNavigateToValidation?: () => void;
}

export function ReportPage({
  initialReport,
  runIdToLoad,
  onNavigateToAnalyze,
  onNavigateToValidation,
}: ReportPageProps) {
  const [report, setReport] = useState<AnalysisResponse | null>(initialReport);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (runIdToLoad && (!report || report.run_id !== runIdToLoad)) {
      setIsLoading(true);
      setErrorMessage(null);
      fetchAnalysisRun(runIdToLoad)
        .then((data) => {
          setReport(data);
        })
        .catch((err) => {
          setErrorMessage(extractErrorMessage(err));
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else if (initialReport && (!report || report.run_id !== initialReport.run_id)) {
      setReport(initialReport);
    }
  }, [runIdToLoad, initialReport]);

  const getScoreBadgeColor = (score: number | null) => {
    if (score === null) return "bg-gray-100 text-gray-800 border-gray-300";
    if (score >= 80) return "bg-emerald-100 text-emerald-800 border-emerald-300";
    if (score >= 60) return "bg-amber-100 text-amber-800 border-amber-300";
    return "bg-rose-100 text-rose-800 border-rose-300";
  };

  const getFlagBadge = (flag: string) => {
    switch (flag) {
      case "deep_nesting":
        return (
          <span
            key={flag}
            className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800"
          >
            deep nesting (&gt;3)
          </span>
        );
      case "long_function":
        return (
          <span
            key={flag}
            className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800"
          >
            long function
          </span>
        );
      case "undefined_variable":
        return (
          <span
            key={flag}
            className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-rose-100 text-rose-800"
          >
            undefined var
          </span>
        );
      default:
        return (
          <span
            key={flag}
            className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800"
          >
            {flag}
          </span>
        );
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto py-12 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-600 border-t-transparent" />
        <p className="mt-3 text-sm text-gray-500">Loading analysis run #{runIdToLoad}...</p>
      </div>
    );
  }

  if (errorMessage) {
    return (
      <div className="max-w-4xl mx-auto space-y-4">
        <div className="rounded-md bg-red-50 p-4 border border-red-200">
          <h3 className="text-sm font-medium text-red-800">Could not load report</h3>
          <div className="mt-2 text-sm text-red-700">{errorMessage}</div>
        </div>
        <button
          onClick={onNavigateToAnalyze}
          className="text-sm text-indigo-600 hover:text-indigo-800 underline"
        >
          &larr; Return to Analyze
        </button>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="max-w-3xl mx-auto text-center py-16 px-4 bg-white rounded-lg border border-dashed border-gray-300">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="1.5"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No analysis report loaded</h3>
        <p className="mt-1 text-sm text-gray-500">
          Analyze code from the Analyze page or select a prior run from History.
        </p>
        <div className="mt-6">
          <button
            type="button"
            onClick={onNavigateToAnalyze}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none"
          >
            Go to Analyze
          </button>
        </div>
      </div>
    );
  }

  const isValidationPassing = report.composite_score !== null && report.composite_score >= 60.0;

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Header Summary */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold text-gray-900">Analysis Report</h1>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                Run #{report.run_id}
              </span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                {report.status}
              </span>
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Languages analyzed:{" "}
              {Object.entries(report.language_summary)
                .map(([lang, count]) => `${lang} (${count})`)
                .join(", ") || "None"}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <span className="text-xs uppercase tracking-wider text-gray-500 font-semibold block">
                Composite Quality Score
              </span>
              <span className="text-3xl font-extrabold text-gray-900">
                {report.composite_score !== null ? report.composite_score.toFixed(1) : "N/A"}
              </span>
              <span className="text-xs text-gray-500 ml-1">/ 100</span>
            </div>
            <div
              className={`w-14 h-14 rounded-full flex items-center justify-center font-bold text-lg border-2 ${getScoreBadgeColor(
                report.composite_score
              )}`}
            >
              {report.composite_score !== null ? Math.round(report.composite_score) : "-"}
            </div>
          </div>
        </div>

        {/* Validation Verdict Banner */}
        <div className="mt-6 pt-5 border-t border-gray-100 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-gray-50 -mx-6 -mb-6 p-4 rounded-b-lg">
          <div className="flex items-center space-x-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-600">
              Quality Validation Verdict:
            </span>
            {isValidationPassing ? (
              <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                ✓ VALIDATED (PASS &ge; 60.0 Cutoff)
              </span>
            ) : (
              <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-300">
                ✗ FAILED (&lt; 60.0 Cutoff)
              </span>
            )}
            <span className="text-xs text-gray-500">
              Evaluated against 60.0 quality acceptance threshold
            </span>
          </div>

          {onNavigateToValidation && (
            <button
              type="button"
              onClick={onNavigateToValidation}
              className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 underline inline-flex items-center"
            >
              Inspect Validation Oracle &rarr;
            </button>
          )}
        </div>
      </div>

      {/* Files and Functions list */}
      <div className="space-y-6">
        <h2 className="text-lg font-semibold text-gray-900">Analyzed Files ({report.files.length})</h2>

        {report.files.map((file) => (
          <div
            key={file.file_id || file.filename}
            className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden"
          >
            {/* File Header */}
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200 flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center space-x-3">
                <span className="font-mono text-sm font-semibold text-gray-900">
                  {file.filename}
                </span>
                <span className="px-2 py-0.5 rounded text-xs font-medium bg-gray-200 text-gray-700 uppercase">
                  {file.language}
                </span>
                <span className="text-xs text-gray-500">{file.loc} LOC</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-xs text-gray-500">File Score:</span>
                <span
                  className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getScoreBadgeColor(
                    file.composite_score
                  )}`}
                >
                  {file.composite_score.toFixed(1)} / 100
                </span>
              </div>
            </div>

            {/* Functions Table */}
            <div className="p-6">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
                Functions / Methods Detected ({file.functions.length})
              </h3>
              {file.functions.length === 0 ? (
                <p className="text-xs text-gray-400 italic">No top-level functions or methods detected.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 text-sm">
                    <thead>
                      <tr className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-gray-50">
                        <th className="px-4 py-2">Function Name</th>
                        <th className="px-4 py-2">Lines</th>
                        <th className="px-4 py-2">Complexity</th>
                        <th className="px-4 py-2">Nesting Depth</th>
                        <th className="px-4 py-2">Length</th>
                        <th className="px-4 py-2">Quality Flags</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 bg-white">
                      {file.functions.map((fn) => (
                        <tr key={fn.name} className="hover:bg-gray-50">
                          <td className="px-4 py-2.5 font-mono text-xs font-semibold text-gray-900">
                            {fn.name}
                          </td>
                          <td className="px-4 py-2.5 text-xs text-gray-500">
                            {fn.start_line} – {fn.end_line}
                          </td>
                          <td className="px-4 py-2.5 text-xs">
                            <span
                              className={`font-semibold ${
                                fn.cyclomatic_complexity > 5 ? "text-amber-600" : "text-gray-700"
                              }`}
                            >
                              {fn.cyclomatic_complexity}
                            </span>
                          </td>
                          <td className="px-4 py-2.5 text-xs">
                            <span
                              className={`font-semibold ${
                                fn.nesting_depth > 3 ? "text-rose-600" : "text-gray-700"
                              }`}
                            >
                              {fn.nesting_depth}
                            </span>
                          </td>
                          <td className="px-4 py-2.5 text-xs text-gray-700">
                            {fn.length_lines} LOC
                          </td>
                          <td className="px-4 py-2.5 text-xs">
                            {fn.flags.length > 0 ? (
                              <div className="flex flex-wrap gap-1">
                                {fn.flags.map((flag) => getFlagBadge(flag))}
                              </div>
                            ) : (
                              <span className="text-gray-400 text-xs">None</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
