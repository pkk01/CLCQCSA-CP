import React, { useState } from "react";
import { Header, PageName } from "./components/Header";
import { AnalyzePage } from "./pages/AnalyzePage";
import { ReportPage } from "./pages/ReportPage";
import { ValidationPage } from "./pages/ValidationPage";
import { HistoryPage } from "./pages/HistoryPage";
import { SimilarityPage } from "./pages/SimilarityPage";
import { triggerValidation } from "./api/client";
import type { AnalysisResponse } from "./api/types";

export function App() {
  const [currentPage, setCurrentPage] = useState<PageName>("Analyze");
  const [currentReport, setCurrentReport] = useState<AnalysisResponse | null>(null);
  const [runIdToLoad, setRunIdToLoad] = useState<number | null>(null);
  const [validationRefreshKey, setValidationRefreshKey] = useState<number>(0);

  const handleAnalysisComplete = (report: AnalysisResponse) => {
    setCurrentReport(report);
    setRunIdToLoad(report.run_id);
    setCurrentPage("Report");

    // Automatically trigger validation run after analysis so validation benchmarks update immediately
    setValidationRefreshKey((prev) => prev + 1);
    triggerValidation()
      .then(() => {
        setValidationRefreshKey((prev) => prev + 1);
      })
      .catch((err) => {
        console.warn("Background validation sync after analysis:", err);
      });
  };

  const handleSelectRunFromHistory = (runId: number) => {
    setRunIdToLoad(runId);
    setCurrentReport(null);
    setCurrentPage("Report");
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      <Header currentPage={currentPage} onNavigate={setCurrentPage} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentPage === "Analyze" && (
          <AnalyzePage onAnalysisComplete={handleAnalysisComplete} />
        )}

        {currentPage === "Report" && (
          <ReportPage
            initialReport={currentReport}
            runIdToLoad={runIdToLoad}
            onNavigateToAnalyze={() => setCurrentPage("Analyze")}
            onNavigateToValidation={() => setCurrentPage("Validation")}
          />
        )}

        {currentPage === "Validation" && (
          <ValidationPage refreshTrigger={validationRefreshKey} />
        )}

        {currentPage === "History" && (
          <HistoryPage
            onSelectRun={handleSelectRunFromHistory}
            onNavigateToAnalyze={() => setCurrentPage("Analyze")}
          />
        )}

        {currentPage === "Similarity" && <SimilarityPage />}
      </main>

      <footer className="bg-white border-t border-gray-200 py-4 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-xs text-gray-500">
          CodeQual Capstone &middot; Review 1 (O1 Cross-Language Parsing + O2 Quality Scoring) &middot; Python &amp; Java Support
        </div>
      </footer>
    </div>
  );
}

export default App;
