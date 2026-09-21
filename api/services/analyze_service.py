import json
from dataclasses import asdict
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from api.db.models import AnalysisRun, AnalyzedFile, FunctionScore
from engine.parsing import normalize_tree, parse_source
from engine.quality import score_file

EXTENSIONS = {".py": "python", ".java": "java"}


def analyze_uploads(db: Session, uploads: list[UploadFile]) -> dict:
    parsed = []
    try:
        for upload in uploads:
            filename = upload.filename or "unnamed"
            suffix = Path(filename).suffix.lower()
            language = EXTENSIONS.get(suffix)
            if language is None:
                raise ValueError(f"'{suffix}' is not a supported language in this review (supported: python, java)")
            try:
                source = upload.file.read().decode("utf-8")
            except UnicodeDecodeError as error:
                raise ValueError(f"'{filename}' is not valid UTF-8 source") from error
            if not source.strip():
                raise ValueError(f"'{filename}' is empty")
            file_ir = normalize_tree(parse_source(source, language), source, language)
            if not file_ir.syntax_valid:
                raise ValueError(f"'{filename}' could not be parsed as valid {language} source")
            score = score_file(file_ir)
            parsed.append((filename, file_ir, score))
        if not parsed:
            raise ValueError("At least one source file is required")
        summary = {}
        for _, file_ir, _ in parsed:
            summary[file_ir.language] = summary.get(file_ir.language, 0) + 1
        run = AnalysisRun(source_label=" + ".join(item[0] for item in parsed), language_summary=json.dumps(summary), composite_score=sum(item[2]["composite_score"] for item in parsed) / len(parsed))
        db.add(run)
        db.flush()
        response_files = []
        for filename, file_ir, score in parsed:
            analyzed_file = AnalyzedFile(run_id=run.id, filename=filename, language=file_ir.language, loc=file_ir.loc, composite_score=score["composite_score"], ir_json=json.dumps(asdict(file_ir)))
            db.add(analyzed_file)
            db.flush()
            style_functions = {item["name"]: item for item in score["style"]["functions"]}
            complexity_functions = {item["name"]: item for item in score["complexity"]["functions"]}
            functions = []
            for function in file_ir.functions:
                flags = []
                if function.max_nesting_depth > 3:
                    flags.append("deep_nesting")
                if style_functions[function.name]["long_function"]:
                    flags.append("long_function")
                if function.name in score["correctness"]["undefined_variables"]:
                    flags.append("undefined_variable")
                function_score = FunctionScore(file_id=analyzed_file.id, name=function.name, start_line=function.start_line, end_line=function.end_line, cyclomatic_complexity=complexity_functions[function.name]["cyclomatic_complexity"], nesting_depth=function.max_nesting_depth, length_lines=function.end_line - function.start_line + 1, flags_json=json.dumps(flags))
                db.add(function_score)
                functions.append({"name": function.name, "start_line": function.start_line, "end_line": function.end_line, "cyclomatic_complexity": function_score.cyclomatic_complexity, "nesting_depth": function.max_nesting_depth, "length_lines": function_score.length_lines, "flags": flags})
            response_files.append({"file_id": analyzed_file.id, "filename": filename, "language": file_ir.language, "loc": file_ir.loc, "composite_score": analyzed_file.composite_score, "functions": functions})
        db.commit()
        return {"run_id": run.id, "status": run.status, "composite_score": run.composite_score, "language_summary": summary, "files": response_files}
    except Exception:
        db.rollback()
        raise
