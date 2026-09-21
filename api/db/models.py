from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    status: Mapped[str] = mapped_column(String, default="complete")
    source_label: Mapped[str] = mapped_column(String)
    language_summary: Mapped[str] = mapped_column(Text)
    composite_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    files: Mapped[list["AnalyzedFile"]] = relationship(cascade="all, delete-orphan")

class AnalyzedFile(Base):
    __tablename__ = "analyzed_files"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("analysis_runs.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String)
    language: Mapped[str] = mapped_column(String)
    loc: Mapped[int] = mapped_column(Integer)
    composite_score: Mapped[float] = mapped_column(Float)
    ir_json: Mapped[str] = mapped_column(Text)
    functions: Mapped[list["FunctionScore"]] = relationship(cascade="all, delete-orphan")

class FunctionScore(Base):
    __tablename__ = "function_scores"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("analyzed_files.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String)
    start_line: Mapped[int] = mapped_column(Integer)
    end_line: Mapped[int] = mapped_column(Integer)
    cyclomatic_complexity: Mapped[int] = mapped_column(Integer)
    nesting_depth: Mapped[int] = mapped_column(Integer)
    length_lines: Mapped[int] = mapped_column(Integer)
    flags_json: Mapped[str] = mapped_column(Text)

class ValidationRun(Base):
    __tablename__ = "validation_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    overall_accuracy: Mapped[float] = mapped_column(Float)
    fixture_count: Mapped[int] = mapped_column(Integer)
    language_breakdown_json: Mapped[str] = mapped_column(Text)
    threshold_used: Mapped[float] = mapped_column(Float)
    results: Mapped[list["FixtureResult"]] = relationship(cascade="all, delete-orphan")

class FixtureResult(Base):
    __tablename__ = "fixture_results"
    __table_args__ = (UniqueConstraint("validation_run_id", "fixture_id"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    validation_run_id: Mapped[int] = mapped_column(ForeignKey("validation_runs.id", ondelete="CASCADE"), index=True)
    fixture_id: Mapped[str] = mapped_column(String)
    language: Mapped[str] = mapped_column(String)
    expected_label: Mapped[str] = mapped_column(String)
    predicted_label: Mapped[str] = mapped_column(String)
    predicted_score: Mapped[float] = mapped_column(Float)
    correct: Mapped[bool] = mapped_column(Boolean)
