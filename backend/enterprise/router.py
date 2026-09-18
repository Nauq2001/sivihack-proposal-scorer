"""FastAPI routes over the enterprise corpus. Mounted from main.py."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .evidence import benchmark_section, check_commitments, free_search
from .store import Corpus, load_corpus, sanitized_text

router = APIRouter(prefix="/api/evidence", tags=["evidence"])


@lru_cache(maxsize=1)
def corpus() -> Corpus:
    """Loaded once; the corpus is small and read-only at runtime."""
    return load_corpus()


class SearchRequest(BaseModel):
    query: str
    section_role: str | None = None
    industry: str | None = None
    country: str | None = None
    service_type: str | None = None
    outcome: str | None = None
    min_quality: float | None = None
    limit: int = Field(default=5, ge=1, le=20)


class BenchmarkRequest(BaseModel):
    section_role: str
    query: str = ""
    industry: str | None = None
    country: str | None = None
    service_type: str | None = None
    limit: int = Field(default=3, ge=1, le=10)


class CommitmentRequest(BaseModel):
    text: str


@router.get("/corpus")
def corpus_report() -> dict[str, Any]:
    """What was admitted, what was refused and why."""
    return corpus().report()


@router.post("/search")
def search_corpus(req: SearchRequest) -> dict[str, Any]:
    return free_search(
        corpus(), req.query, limit=req.limit,
        section_role=req.section_role, industry=req.industry, country=req.country,
        service_type=req.service_type, outcome=req.outcome, min_quality=req.min_quality,
    )


@router.post("/benchmark")
def benchmark(req: BenchmarkRequest) -> dict[str, Any]:
    """How comparable won proposals wrote a given section."""
    return benchmark_section(
        corpus(), req.section_role, query=req.query, limit=req.limit,
        industry=req.industry, country=req.country, service_type=req.service_type,
    )


@router.post("/commitments")
def commitments(req: CommitmentRequest) -> dict[str, Any]:
    """Promises in the draft the company cannot currently back."""
    return check_commitments(corpus(), req.text)


@router.get("/document/{record_id}")
def document(record_id: str) -> dict[str, Any]:
    """The redacted full text, for records cleared for use across deals."""
    text = sanitized_text(corpus(), record_id)
    if text is None:
        return {"record_id": record_id, "text": None, "reason": "not_cleared_for_cross_deal_use"}
    return {"record_id": record_id, "text": text}
