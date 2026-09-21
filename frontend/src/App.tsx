import { useEffect, useState } from "react";

type FileReport = { filename: string; language: string; loc: number; composite_score: number; functions: { name: string; cyclomatic_complexity: number; nesting_depth: number; length_lines: number; flags: string[] }[] };
type Run = { run_id: number; status: string; composite_score: number; files: FileReport[] };
type HistoryRun = { run_id: number; source_label: string; composite_score: number; status: string; created_at: string };
type Validation = { validation_run_id: number | null; overall_accuracy?: number; fixture_count?: number; language_breakdown?: Record<string, number>; threshold_used?: number; results?: { fixture_id: string; language: string; expected_label: string; predicted_label: string; predicted_score: number; correct: boolean }[] };

const API = `${window.location.protocol}//${window.location.hostname}:8000/api`;

export function App() {
  const [page, setPage] = useState("Analyze");
  const [language, setLanguage] = useState("python");
  const [code, setCode] = useState("");
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [report, setReport] = useState<Run | null>(null);
  const [history, setHistory] = useState<HistoryRun[]>([]);
  const [validation, setValidation] = useState<Validation>({ validation_run_id: null });
  const [message, setMessage] = useState("");
  const [validationLoading, setValidationLoading] = useState(false);

  async function analyze() {
    setMessage("");
    const extension = language === "python" ? "py" : "java";
    const body = new FormData();
    if (selectedFiles.length) selectedFiles.forEach(file => body.append("files", file));
    else body.append("files", new File([code], `pasted.${extension}`, { type: "text/plain" }));
    try {
      const response = await fetch(`${API}/analyze`, { method: "POST", body });
      const payload = await response.json();
      if (!response.ok) { setMessage(payload.detail?.detail ?? payload.detail ?? "Analysis failed"); return; }
      setReport(payload);
      setPage("Report");
    } catch {
      setMessage("Cannot connect to the backend. Start FastAPI on port 8000.");
    }
  }

  async function runValidation() {
    setMessage("");
    setValidationLoading(true);
    try {
      const response = await fetch(`${API}/validation/run`, { method: "POST" });
      const payload = await response.json();
      if (response.ok) setValidation(payload);
      else setMessage(payload.detail?.detail ?? payload.detail ?? "Validation failed");
    } catch {
      setMessage("Cannot connect to the backend. Start FastAPI on port 8000.");
    } finally {
      setValidationLoading(false);
    }
  }

  async function openRun(runId: number) {
    setMessage("");
    try {
      const response = await fetch(`${API}/analyze/${runId}`);
      const payload = await response.json();
      if (!response.ok) { setMessage(payload.detail ?? "Could not load the saved report."); return; }
      setReport(payload);
      setPage("Report");
    } catch {
      setMessage("Cannot connect to the backend. Start FastAPI on port 8000.");
    }
  }

  useEffect(() => {
    if (page === "History") fetch(`${API}/runs`).then(response => response.json()).then(payload => setHistory(payload.runs ?? [])).catch(() => setMessage("Cannot load history from the backend."));
    if (page === "Validation") fetch(`${API}/validation/latest`).then(response => response.json()).then(setValidation).catch(() => setMessage("Cannot load validation from the backend."));
  }, [page]);

  return <div className="app"><header><strong>CodeQual</strong><nav>{["Analyze", "Report", "Validation", "History"].map(item => <button key={item} onClick={() => setPage(item)}>{item}</button>)}</nav></header><main>
    {page === "Analyze" && <section><h1>Analyze code</h1><p>Paste Python or Java source, or select source files.</p><select value={language} onChange={event => setLanguage(event.target.value)}><option value="python">Python</option><option value="java">Java</option></select><input type="file" accept=".py,.java" multiple onChange={event => setSelectedFiles(Array.from(event.target.files ?? []))} /><textarea value={code} onChange={event => setCode(event.target.value)} placeholder="Paste source code here..." rows={18} /><button className="primary" onClick={analyze} disabled={!code.trim() && !selectedFiles.length}>Analyze code</button>{message && <p className="error">{message}</p>}</section>}
    {page === "Report" && <section><h1>Analysis report</h1>{report ? <><div className="score">{report.composite_score.toFixed(1)}<small>/100</small></div>{report.files.map(file => <article key={file.filename}><h2>{file.filename} <span>{file.language} · {file.loc} LOC</span></h2><table><thead><tr><th>Function</th><th>Complexity</th><th>Nesting</th><th>Length</th><th>Flags</th></tr></thead><tbody>{file.functions.map(fn => <tr key={fn.name}><td>{fn.name}</td><td>{fn.cyclomatic_complexity}</td><td>{fn.nesting_depth}</td><td>{fn.length_lines}</td><td>{fn.flags.join(", ") || "None"}</td></tr>)}</tbody></table></article>)}</> : <p>No analysis loaded yet.</p>}</section>}
    {page === "Validation" && <section><h1>Validation</h1><button className="primary" onClick={runValidation} disabled={validationLoading}>{validationLoading ? "Running..." : "Run validation"}</button>{message && <p className="error">{message}</p>}{validation.validation_run_id ? <><p>Run #{validation.validation_run_id} · threshold {validation.threshold_used?.toFixed(1)} · {((validation.overall_accuracy ?? 0) * 100).toFixed(1)}% across {validation.fixture_count ?? 0} fixtures.</p><p>{Object.entries(validation.language_breakdown ?? {}).map(([name, accuracy]) => `${name}: ${(accuracy * 100).toFixed(1)}%`).join(" | ")}</p><table><thead><tr><th>Fixture</th><th>Language</th><th>Expected</th><th>Predicted</th><th>Score</th><th>Result</th></tr></thead><tbody>{(validation.results ?? []).map(result => <tr key={result.fixture_id}><td>{result.fixture_id}</td><td>{result.language}</td><td>{result.expected_label}</td><td>{result.predicted_label}</td><td>{result.predicted_score.toFixed(1)}</td><td>{result.correct ? "Pass" : "Failed"}</td></tr>)}</tbody></table></> : <p>No validation run has been recorded yet.</p>}</section>}
    {page === "History" && <section><h1>History</h1>{message && <p className="error">{message}</p>}{history.length ? <table><thead><tr><th>Source</th><th>Score</th><th>Status</th><th>Created</th><th>Report</th></tr></thead><tbody>{history.map(run => <tr key={run.run_id}><td>{run.source_label}</td><td>{run.composite_score?.toFixed(1)}</td><td>{run.status}</td><td>{run.created_at}</td><td><button onClick={() => openRun(run.run_id)}>Open</button></td></tr>)}</tbody></table> : <p>No saved analysis runs yet.</p>}</section>}
  </main></div>;
}
