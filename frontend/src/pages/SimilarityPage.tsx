import React, { useState } from "react";
import { checkSimilarity, extractErrorMessage } from "../api/client";
import type { SimilarityResponse } from "../api/types";

// ---------------------------------------------------------------------------
// Built-in sample pair for quick demo
// ---------------------------------------------------------------------------
const SAMPLE_A = {
  language: "python" as const,
  code: `def find_max(numbers):
    maximum = numbers[0]
    for number in numbers:
        if number > maximum:
            maximum = number
    return maximum
`,
};

const SAMPLE_B = {
  language: "java" as const,
  code: `public class ArrayUtils {
    public int findMax(int[] numbers) {
        int maximum = numbers[0];
        for (int number : numbers) {
            if (number > maximum) {
                maximum = number;
            }
        }
        return maximum;
    }
}
`,
};

// ---------------------------------------------------------------------------
// Verdict badge colours
// ---------------------------------------------------------------------------
function VerdictBadge({ verdict }: { verdict: string }) {
  const styles: Record<string, string> = {
    plagiarized: "bg-red-100 text-red-800 border border-red-300",
    suspicious: "bg-amber-100 text-amber-800 border border-amber-300",
    not_plagiarized: "bg-green-100 text-green-800 border border-green-300",
  };
  const labels: Record<string, string> = {
    plagiarized: "Plagiarized",
    suspicious: "Suspicious",
    not_plagiarized: "Not Plagiarized",
  };
  return (
    <span
      className={`px-3 py-1 rounded-full text-sm font-semibold ${styles[verdict] ?? "bg-gray-100 text-gray-700"}`}
    >
      {labels[verdict] ?? verdict}
    </span>
  );
}

function SimilarityGauge({ value }: { value: number }) {
  const pct = Math.round(value);
  let colour = "text-green-600";
  if (pct >= 80) colour = "text-red-600";
  else if (pct >= 50) colour = "text-amber-500";
  return (
    <div className={`text-6xl font-extrabold tracking-tight ${colour}`}>
      {pct}
      <span className="text-3xl font-bold">%</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------
export function SimilarityPage() {
  const [codeA, setCodeA] = useState("");
  const [langA, setLangA] = useState<"python" | "java">("python");
  const [codeB, setCodeB] = useState("");
  const [langB, setLangB] = useState<"python" | "java">("java");

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [result, setResult] = useState<SimilarityResponse | null>(null);

  const handleLoadSample = () => {
    setCodeA(SAMPLE_A.code);
    setLangA(SAMPLE_A.language);
    setCodeB(SAMPLE_B.code);
    setLangB(SAMPLE_B.language);
    setResult(null);
    setErrorMessage(null);
  };

  const handleCompare = async () => {
    if (!codeA.trim() || !codeB.trim()) {
      setErrorMessage("Both code boxes must contain source code before comparing.");
      return;
    }
    setIsLoading(true);
    setErrorMessage(null);
    setResult(null);
    try {
      const response = await checkSimilarity({
        code_a: codeA,
        language_a: langA,
        code_b: codeB,
        language_b: langB,
      });
      setResult(response);
    } catch (err) {
      setErrorMessage(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">
          Similarity &amp; Plagiarism Detection
        </h1>
        <p className="mt-2 text-sm text-gray-600">
          Paste two snippets (Python or Java — cross-language comparison is
          supported). Comparison is based on structural token sequences derived
          from real tree-sitter parse trees, so renamed variables and language
          differences are stripped away.
        </p>
      </div>

      {/* Load sample button */}
      <div className="flex items-center gap-4">
        <button
          type="button"
          onClick={handleLoadSample}
          className="inline-flex items-center px-4 py-2 border border-indigo-300 text-sm font-medium rounded-md text-indigo-700 bg-indigo-50 hover:bg-indigo-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors"
        >
          <svg
            className="mr-2 h-4 w-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
            />
          </svg>
          Load sample pair (Python ↔ Java)
        </button>
        <span className="text-xs text-gray-400">
          Loads a Python function and its Java equivalent — a cross-language
          plagiarism example.
        </span>
      </div>

      {/* Error message */}
      {errorMessage && (
        <div className="rounded-md bg-red-50 p-4 border border-red-200">
          <div className="flex">
            <svg
              className="h-5 w-5 text-red-400 mr-2 flex-shrink-0 mt-0.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div>
              <div className="text-sm font-medium text-red-800">Error</div>
              <div className="text-sm text-red-700 mt-0.5">{errorMessage}</div>
            </div>
          </div>
        </div>
      )}

      {/* Two code panels */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Code A */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-5 space-y-3">
          <div className="flex items-center justify-between">
            <label className="block text-sm font-semibold text-gray-700">
              Code A
            </label>
            <select
              value={langA}
              onChange={(e) => setLangA(e.target.value as "python" | "java")}
              className="rounded-md border-gray-300 shadow-sm text-xs focus:border-indigo-500 focus:ring-indigo-500 py-1 px-2 border"
            >
              <option value="python">Python</option>
              <option value="java">Java</option>
            </select>
          </div>
          <textarea
            rows={14}
            value={codeA}
            onChange={(e) => {
              setCodeA(e.target.value);
              setResult(null);
              setErrorMessage(null);
            }}
            placeholder={`// Paste ${langA} code here…`}
            className="w-full font-mono text-xs p-3 rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 bg-gray-900 text-gray-100 resize-y"
          />
        </div>

        {/* Code B */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-5 space-y-3">
          <div className="flex items-center justify-between">
            <label className="block text-sm font-semibold text-gray-700">
              Code B
            </label>
            <select
              value={langB}
              onChange={(e) => setLangB(e.target.value as "python" | "java")}
              className="rounded-md border-gray-300 shadow-sm text-xs focus:border-indigo-500 focus:ring-indigo-500 py-1 px-2 border"
            >
              <option value="python">Python</option>
              <option value="java">Java</option>
            </select>
          </div>
          <textarea
            rows={14}
            value={codeB}
            onChange={(e) => {
              setCodeB(e.target.value);
              setResult(null);
              setErrorMessage(null);
            }}
            placeholder={`// Paste ${langB} code here…`}
            className="w-full font-mono text-xs p-3 rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 bg-gray-900 text-gray-100 resize-y"
          />
        </div>
      </div>

      {/* Compare button */}
      <div className="flex justify-center">
        <button
          type="button"
          onClick={handleCompare}
          disabled={isLoading || !codeA.trim() || !codeB.trim()}
          className={`inline-flex items-center px-8 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
            isLoading || !codeA.trim() || !codeB.trim()
              ? "bg-indigo-300 cursor-not-allowed"
              : "bg-indigo-600 hover:bg-indigo-700"
          }`}
        >
          {isLoading ? (
            <>
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
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
              Comparing…
            </>
          ) : (
            <>
              <svg
                className="mr-2 h-5 w-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
              Compare
            </>
          )}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-6">
          {/* Top row: score + verdict */}
          <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
            <div className="flex flex-col items-center">
              <SimilarityGauge value={result.similarity} />
              <div className="mt-1 text-xs text-gray-500 uppercase tracking-wide font-semibold">
                Similarity
              </div>
            </div>
            <div className="flex flex-col justify-center gap-3">
              <VerdictBadge verdict={result.verdict} />
              <p className="text-sm text-gray-700 max-w-xl italic">
                {result.reason}
              </p>
            </div>
          </div>

          {/* Stats grid */}
          <div className="border-t border-gray-100 pt-5 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            {[
              {
                label: "Structural",
                value: (result.structural_score * 100).toFixed(1) + "%",
                hint: "SequenceMatcher ratio",
              },
              {
                label: "Shingle",
                value: (result.shingle_score * 100).toFixed(1) + "%",
                hint: "Jaccard 3-gram score",
              },
              {
                label: "Tokens A",
                value: result.tokens_a.toString(),
                hint: "Structural tokens in snippet A",
              },
              {
                label: "Tokens B",
                value: result.tokens_b.toString(),
                hint: "Structural tokens in snippet B",
              },
              {
                label: "Matching n-grams",
                value: result.matching_ngrams.toString(),
                hint: "Shared 3-gram shingles",
              },
            ].map((stat) => (
              <div
                key={stat.label}
                className="bg-gray-50 rounded-lg p-3 text-center"
                title={stat.hint}
              >
                <div className="text-lg font-bold text-gray-800">
                  {stat.value}
                </div>
                <div className="text-xs text-gray-500 mt-0.5">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
