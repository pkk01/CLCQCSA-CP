import React, { useEffect, useState } from "react";
import { fetchRuns, extractErrorMessage } from "../api/client";
import type { RunSummary } from "../api/types";

interface HistoryPageProps {
  onSelectRun: (runId: number) => void;
  onNavigateToAnalyze: () => void;
}

export function HistoryPage({ onSelectRun, onNavigateToAnalyze }: HistoryPageProps) {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadRuns = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const response = await fetchRuns(50, 0);
      setRuns(response.runs);
      setTotal(response.total);
    } catch (err) {
      setErrorMessage(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadRuns();
  }, []);

  const getScoreBadgeColor = (score: number | null) => {
    if (score === null) return "bg-gray-100 text-gray-800";
    if (score >= 80) return "bg-emerald-100 text-emerald-800";
    if (score >= 60) return "bg-amber-100 text-amber-800";
    return "bg-rose-100 text-rose-800";
  };

  const formatDate = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleString();
    } catch {
      return isoString;
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Analysis History</h1>
          <p className="mt-1 text-sm text-gray-600">
            Audit log of all past code quality analysis runs persisted in SQLite.
          </p>
        </div>

        <button
          type="button"
          onClick={loadRuns}
          disabled={isLoading}
          className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none"
        >
          {isLoading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {errorMessage && (
        <div className="rounded-md bg-red-50 p-4 border border-red-200">
          <div className="text-sm font-medium text-red-800">History Error:</div>
          <div className="mt-1 text-sm text-red-700">{errorMessage}</div>
        </div>
      )}

      {isLoading && runs.length === 0 ? (
        <div className="py-12 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-600 border-t-transparent" />
          <p className="mt-3 text-sm text-gray-500">Loading analysis history...</p>
        </div>
      ) : runs.length === 0 ? (
        <div className="bg-white p-12 text-center rounded-lg border border-dashed border-gray-300">
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
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No past analysis runs</h3>
          <p className="mt-1 text-sm text-gray-500">
            Analyze your first codebase to see run history here.
          </p>
          <div className="mt-6">
            <button
              type="button"
              onClick={onNavigateToAnalyze}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Start Analysis
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
              Total Runs: {total}
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead>
                <tr className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <th className="px-6 py-3">Run ID</th>
                  <th className="px-6 py-3">Source / Files</th>
                  <th className="px-6 py-3">Composite Score</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Created At</th>
                  <th className="px-6 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {runs.map((run) => (
                  <tr key={run.run_id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap font-mono text-xs font-medium text-gray-900">
                      #{run.run_id}
                    </td>
                    <td className="px-6 py-4 text-xs font-mono text-gray-800">
                      {run.source_label}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {run.composite_score !== null ? (
                        <span
                          className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold ${getScoreBadgeColor(
                            run.composite_score
                          )}`}
                        >
                          {run.composite_score.toFixed(1)} / 100
                        </span>
                      ) : (
                        <span className="text-xs text-gray-400">N/A</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                        {run.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-xs text-gray-500">
                      {formatDate(run.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-xs font-medium">
                      <button
                        onClick={() => onSelectRun(run.run_id)}
                        className="text-indigo-600 hover:text-indigo-900 font-semibold"
                      >
                        View Report &rarr;
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
