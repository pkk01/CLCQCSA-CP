import React, { useEffect, useState } from "react";
import {
  fetchLatestValidation,
  triggerValidation,
  extractErrorMessage,
} from "../api/client";
import type { ValidationResponse } from "../api/types";

interface ValidationPageProps {
  refreshTrigger?: number;
}

export function ValidationPage({ refreshTrigger }: ValidationPageProps = {}) {
  const [validation, setValidation] = useState<ValidationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isRunningHarness, setIsRunningHarness] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const loadLatestValidation = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await fetchLatestValidation();
      setValidation(data);
      setLastUpdated(new Date());
    } catch (err) {
      setErrorMessage(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadLatestValidation();
  }, [refreshTrigger]);

  const handleRunValidation = async () => {
    setIsRunningHarness(true);
    setErrorMessage(null);
    try {
      const data = await triggerValidation();
      setValidation(data);
      setLastUpdated(new Date());
    } catch (err) {
      setErrorMessage(extractErrorMessage(err));
    } finally {
      setIsRunningHarness(false);
    }
  };

  const hasRunData = validation && validation.validation_run_id !== null && validation.overall_accuracy !== undefined;

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            Validation Harness &amp; Accuracy
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            Runs the engine against the pre-labelled fixtures/ dataset and reports accuracy
            (PRD.md §3 KPI-1). Click "Run Full Validation Harness" to re-evaluate.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            type="button"
            onClick={loadLatestValidation}
            disabled={isLoading || isRunningHarness}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none"
          >
            {isLoading ? "Fetching..." : "Refresh"}
          </button>

          <button
            type="button"
            onClick={handleRunValidation}
            disabled={isRunningHarness || isLoading}
            className={`inline-flex items-center px-5 py-2.5 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
              isRunningHarness || isLoading
                ? "bg-indigo-400 cursor-not-allowed"
                : "bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            }`}
          >
            {isRunningHarness ? (
              <>
                <svg
                  className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v8H4z"
                  />
                </svg>
                Running Validation Harness...
              </>
            ) : (
              "Run Full Validation Harness"
            )}
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="rounded-md bg-red-50 p-4 border border-red-200">
          <div className="text-sm font-medium text-red-800">Validation Error:</div>
          <div className="mt-1 text-sm text-red-700">{errorMessage}</div>
        </div>
      )}

      {isLoading && !isRunningHarness ? (
        <div className="py-12 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-600 border-t-transparent" />
          <p className="mt-3 text-sm text-gray-500">Checking latest validation records...</p>
        </div>
      ) : !hasRunData ? (
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
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No validation runs found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Click "Run Full Validation Harness" above to evaluate the engine against all fixtures.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex items-center justify-between text-xs text-gray-500 px-1">
            <span>Synchronized with database: {lastUpdated.toLocaleTimeString()}</span>
            <span className="text-emerald-700 font-medium">Results from last harness run</span>
          </div>

          {/* Key Metrics Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-lg shadow-sm border border-gray-200">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider block">
                Overall Accuracy (KPI-1)
              </span>
              <div className="mt-2 flex items-baseline">
                <span className="text-3xl font-extrabold text-indigo-600">
                  {((validation.overall_accuracy ?? 0) * 100).toFixed(1)}%
                </span>
                <span className="ml-2 text-xs text-emerald-600 font-medium">Target: &ge;80%</span>
              </div>
            </div>

            <div className="bg-white p-5 rounded-lg shadow-sm border border-gray-200">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider block">
                Fixtures Evaluated
              </span>
              <div className="mt-2">
                <span className="text-3xl font-extrabold text-gray-900">
                  {validation.fixture_count ?? 0}
                </span>
                <span className="ml-2 text-xs text-gray-500">labeled files</span>
              </div>
            </div>

            <div className="bg-white p-5 rounded-lg shadow-sm border border-gray-200">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider block">
                Classification Cutoff
              </span>
              <div className="mt-2">
                <span className="text-3xl font-extrabold text-gray-900">
                  {validation.threshold_used?.toFixed(1) ?? "60.0"}
                </span>
                <span className="ml-2 text-xs text-gray-500">&ge; cutoff is Good</span>
              </div>
            </div>

            <div className="bg-white p-5 rounded-lg shadow-sm border border-gray-200">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider block">
                Run Identifier
              </span>
              <div className="mt-2">
                <span className="text-2xl font-bold text-gray-900">
                  #{validation.validation_run_id}
                </span>
                <span className="ml-2 text-xs text-green-600 font-medium">Active</span>
              </div>
            </div>
          </div>

          {/* Language Breakdown */}
          {validation.language_breakdown && (
            <div className="bg-white p-5 rounded-lg shadow-sm border border-gray-200">
              <h2 className="text-sm font-semibold text-gray-900 mb-3">Language Accuracy Breakdown</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {Object.entries(validation.language_breakdown).map(([lang, acc]) => (
                  <div key={lang} className="p-3 bg-gray-50 rounded border border-gray-200">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium uppercase text-gray-600">{lang}</span>
                      <span className="text-sm font-bold text-gray-900">
                        {(acc * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-indigo-600 h-2 rounded-full"
                        style={{ width: `${Math.min(100, Math.max(0, acc * 100))}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Fixture Detailed Results Table */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
              <h2 className="text-sm font-semibold text-gray-900">
                Fixture Audit Results ({validation.results?.length ?? 0} items)
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead>
                  <tr className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <th className="px-4 py-2.5">Fixture ID</th>
                    <th className="px-4 py-2.5">Language</th>
                    <th className="px-4 py-2.5">Expected</th>
                    <th className="px-4 py-2.5">Predicted</th>
                    <th className="px-4 py-2.5">Score</th>
                    <th className="px-4 py-2.5">Verdict</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {(validation.results ?? []).map((res) => (
                    <tr key={res.fixture_id} className="hover:bg-gray-50">
                      <td className="px-4 py-2.5 font-mono text-xs text-gray-900 font-medium">
                        {res.fixture_id}
                      </td>
                      <td className="px-4 py-2.5 text-xs text-gray-600 uppercase">
                        {res.language}
                      </td>
                      <td className="px-4 py-2.5 text-xs">
                        <span
                          className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${
                            res.expected_label === "good"
                              ? "bg-green-100 text-green-800"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          {res.expected_label}
                        </span>
                      </td>
                      <td className="px-4 py-2.5 text-xs">
                        <span
                          className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${
                            res.predicted_label === "good"
                              ? "bg-green-100 text-green-800"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          {res.predicted_label}
                        </span>
                      </td>
                      <td className="px-4 py-2.5 text-xs font-semibold text-gray-900">
                        {res.predicted_score.toFixed(1)}
                      </td>
                      <td className="px-4 py-2.5 text-xs">
                        {res.correct ? (
                          <span className="inline-flex items-center text-emerald-600 font-semibold">
                            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                              <path
                                fillRule="evenodd"
                                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                clipRule="evenodd"
                              />
                            </svg>
                            Pass
                          </span>
                        ) : (
                          <span className="inline-flex items-center text-rose-600 font-semibold">
                            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                              <path
                                fillRule="evenodd"
                                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                                clipRule="evenodd"
                              />
                            </svg>
                            Fail
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
