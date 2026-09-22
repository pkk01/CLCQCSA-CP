import React, { useState } from "react";
import { uploadAndAnalyze, extractErrorMessage } from "../api/client";
import type { AnalysisResponse } from "../api/types";

interface AnalyzePageProps {
  onAnalysisComplete: (report: AnalysisResponse) => void;
}

export function AnalyzePage({ onAnalysisComplete }: AnalyzePageProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [pastedCode, setPastedCode] = useState("");
  const [language, setLanguage] = useState<"python" | "java">("python");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files));
      setErrorMessage(null);
    }
  };

  const handleAnalyze = async () => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      let filesToUpload: File[] = [];

      if (selectedFiles.length > 0) {
        filesToUpload = selectedFiles;
      } else if (pastedCode.trim()) {
        const ext = language === "python" ? "py" : "java";
        const blob = new Blob([pastedCode], { type: "text/plain" });
        const file = new File([blob], `snippet.${ext}`, { type: "text/plain" });
        filesToUpload = [file];
      } else {
        setErrorMessage("Please select one or more files or paste source code to analyze.");
        setIsLoading(false);
        return;
      }

      const result = await uploadAndAnalyze(filesToUpload);
      onAnalysisComplete(result);
    } catch (err) {
      setErrorMessage(extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const samplePython = `def calculate_metrics(items, threshold):\n    total = 0\n    for item in items:\n        if item > threshold:\n            total += item\n    return total\n`;
  const sampleJava = `public class Calculator {\n    public int addNumbers(int a, int b) {\n        return a + b;\n    }\n}\n`;

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">Analyze Source Code</h1>
        <p className="mt-2 text-sm text-gray-600">
          Upload Python or Java source files for cross-language AST parsing, cyclomatic complexity,
          nesting depth analysis, and quality scoring.
        </p>
      </div>

      {errorMessage && (
        <div className="rounded-md bg-red-50 p-4 border border-red-200">
          <div className="flex">
            <div className="text-sm font-medium text-red-800">Analysis Error:</div>
            <div className="ml-2 text-sm text-red-700">{errorMessage}</div>
          </div>
        </div>
      )}

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 space-y-6">
        {/* File Upload section */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Option 1: Upload Source Files (.py, .java)
          </label>
          <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md hover:border-indigo-400 transition-colors">
            <div className="space-y-1 text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
                aria-hidden="true"
              >
                <path
                  d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                  strokeWidth={2}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <div className="flex text-sm text-gray-600 justify-center">
                <label
                  htmlFor="file-upload"
                  className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none"
                >
                  <span>Select files</span>
                  <input
                    id="file-upload"
                    name="file-upload"
                    type="file"
                    multiple
                    accept=".py,.java"
                    className="sr-only"
                    onChange={handleFileChange}
                  />
                </label>
                <p className="pl-1">or drag and drop</p>
              </div>
              <p className="text-xs text-gray-500">Supports .py and .java files</p>
            </div>
          </div>
          {selectedFiles.length > 0 && (
            <div className="mt-3">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                Selected Files ({selectedFiles.length}):
              </span>
              <ul className="mt-1 divide-y divide-gray-200 border border-gray-200 rounded-md bg-gray-50 text-sm">
                {selectedFiles.map((f) => (
                  <li key={f.name} className="py-2 px-3 flex items-center justify-between">
                    <span className="font-mono text-xs text-gray-800">{f.name}</span>
                    <span className="text-xs text-gray-500">{(f.size / 1024).toFixed(1)} KB</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="relative">
          <div className="absolute inset-0 flex items-center" aria-hidden="true">
            <div className="w-full border-t border-gray-200" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">OR</span>
          </div>
        </div>

        {/* Paste Code section */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-700">
              Option 2: Paste Code Snippet
            </label>
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                <span className="text-xs text-gray-500">Language:</span>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value as "python" | "java")}
                  className="block rounded-md border-gray-300 shadow-sm text-xs focus:border-indigo-500 focus:ring-indigo-500 py-1 px-2 border"
                >
                  <option value="python">Python (.py)</option>
                  <option value="java">Java (.java)</option>
                </select>
              </div>
              <button
                type="button"
                onClick={() => setPastedCode(language === "python" ? samplePython : sampleJava)}
                className="text-xs text-indigo-600 hover:text-indigo-800 underline"
              >
                Insert sample
              </button>
            </div>
          </div>
          <textarea
            rows={10}
            value={pastedCode}
            onChange={(e) => {
              setPastedCode(e.target.value);
              setErrorMessage(null);
            }}
            placeholder={`// Paste your ${language} source code here...`}
            className="w-full font-mono text-xs p-3 rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 bg-gray-900 text-gray-100"
          />
        </div>

        {/* Action button */}
        <div className="flex justify-end pt-2">
          <button
            type="button"
            onClick={handleAnalyze}
            disabled={isLoading || (!pastedCode.trim() && selectedFiles.length === 0)}
            className={`inline-flex items-center px-6 py-2.5 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
              isLoading || (!pastedCode.trim() && selectedFiles.length === 0)
                ? "bg-indigo-300 cursor-not-allowed"
                : "bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            }`}
          >
            {isLoading ? (
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
                Analyzing code...
              </>
            ) : (
              "Run Quality Analysis"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
