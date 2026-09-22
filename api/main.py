"""FastAPI application entrypoint for CodeQual.

Configures middleware, routes, and database initialization.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.db.models import Base
from api.db.session import engine
from api.models import HealthResponse
from api.routes.analyze import router as analyze_router
from api.routes.runs import router as runs_router
from api.routes.validation import router as validation_router

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CodeQual API",
    description="Cross-language code quality and correctness analyzer API",
    version="0.1.0",
)

# CORS configuration for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include endpoint routers matching ARCHITECTURE.md §2
app.include_router(analyze_router)
app.include_router(runs_router)
app.include_router(validation_router)


@app.get("/api/health", response_model=HealthResponse, tags=["health"])
def health():
    """Liveness check returning operational status and loaded language grammars."""
    return {"status": "ok", "grammars_loaded": ["python", "java"]}
