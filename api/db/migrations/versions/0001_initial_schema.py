"""Initial schema matching DATABASE.md

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-09-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "analysis_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("source_label", sa.Text(), nullable=False),
        sa.Column("language_summary", sa.Text(), nullable=False),
        sa.Column("composite_score", sa.Float(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analysis_runs_created_at", "analysis_runs", ["created_at"])

    op.create_table(
        "analyzed_files",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.Text(), nullable=False),
        sa.Column("language", sa.Text(), nullable=False),
        sa.Column("loc", sa.Integer(), nullable=False),
        sa.Column("composite_score", sa.Float(), nullable=False),
        sa.Column("ir_json", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["analysis_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analyzed_files_run_id", "analyzed_files", ["run_id"])

    op.create_table(
        "function_scores",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("file_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("start_line", sa.Integer(), nullable=False),
        sa.Column("end_line", sa.Integer(), nullable=False),
        sa.Column("cyclomatic_complexity", sa.Integer(), nullable=False),
        sa.Column("nesting_depth", sa.Integer(), nullable=False),
        sa.Column("length_lines", sa.Integer(), nullable=False),
        sa.Column("flags_json", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["analyzed_files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_function_scores_file_id", "function_scores", ["file_id"])

    op.create_table(
        "validation_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("overall_accuracy", sa.Float(), nullable=False),
        sa.Column("fixture_count", sa.Integer(), nullable=False),
        sa.Column("language_breakdown_json", sa.Text(), nullable=False),
        sa.Column("threshold_used", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_validation_runs_created_at", "validation_runs", ["created_at"])

    op.create_table(
        "fixture_results",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("validation_run_id", sa.Integer(), nullable=False),
        sa.Column("fixture_id", sa.Text(), nullable=False),
        sa.Column("language", sa.Text(), nullable=False),
        sa.Column("expected_label", sa.Text(), nullable=False),
        sa.Column("predicted_label", sa.Text(), nullable=False),
        sa.Column("predicted_score", sa.Float(), nullable=False),
        sa.Column("correct", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["validation_run_id"], ["validation_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("validation_run_id", "fixture_id", name="uq_fixture_result_per_run"),
    )
    op.create_index("ix_fixture_results_validation_run_id", "fixture_results", ["validation_run_id"])


def downgrade() -> None:
    op.drop_table("fixture_results")
    op.drop_table("validation_runs")
    op.drop_table("function_scores")
    op.drop_table("analyzed_files")
    op.drop_table("analysis_runs")
