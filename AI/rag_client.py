"""Client for Backend's RAG retrieval (backend/rag/), v3 "hybrid contract".

Uses Backend's recommended integration path — a direct in-process Python
import of backend/rag/api.py — not the HTTP `/rag/retrieve` endpoint, since
both packages run in the same process once Backend wires AI/scoring.py into
main.py.

v3 change from v2: retrieval is now hybrid (keyword overlap + local
sentence-transformers embedding cosine similarity), not pure keyword
overlap. Still no per-request API call — the embedding model runs locally,
so it never touches the shared Gemini budget, only a one-time model
download/load cost. `relevance_threshold` (int, keyword-overlap count) was
removed by Backend and replaced with `min_hybrid_score` (float 0-1).

v2 change from v1: exclusion of Problem Understanding / Scope & Deliverables
Clarity / Completeness vs RFP Requirements is enforced by Backend itself
(`retrieve_payload` raises ValueError for those) rather than by this client —
so this module just needs to not call RAG for them at all, and matches are
already pre-trimmed to exactly {text, sample_type, reasoning}.
"""

from __future__ import annotations

import re
import unicodedata

from backend.rag.api import format_benchmark_references, load_store, retrieve_payload

from AI.contracts import BASE_CRITERIA, CriterionWeight

__all__ = ["retrieve_examples", "format_benchmark_references"]

# Backend's benchmark index keys criteria by snake_case canonical id, not our
# display-name strings — map ours to theirs. Character-for-character with
# backend/rag/engine.py:BASE_CRITERIA/ALIASES.
_CANONICAL_ID_BY_NAME: dict[str, str] = {
    "Problem Understanding": "problem_understanding",
    "Scope & Deliverables Clarity": "scope_deliverables_clarity",
    "Pricing Clarity": "pricing_clarity",
    "Timeline Clarity": "timeline_clarity",
    "Completeness vs RFP Requirements": "completeness_vs_rfp",
    "Tone & Persuasiveness": "tone_persuasiveness",
    "Risk/Assumptions Transparency": "risk_assumptions_transparency",
}
assert set(_CANONICAL_ID_BY_NAME) == set(BASE_CRITERIA)

# Backend's RAG_CRITERIA (backend/rag/engine.py) — the only base criteria RAG
# applies to. Mirrored here just to skip the call outright instead of
# catching Backend's ValueError; Backend's check is still the source of truth.
_RAG_ENABLED_BASE_CRITERIA = {
    "Pricing Clarity",
    "Timeline Clarity",
    "Tone & Persuasiveness",
    "Risk/Assumptions Transparency",
}
_EXCLUDED_BASE_CRITERIA = set(BASE_CRITERIA) - _RAG_ENABLED_BASE_CRITERIA

_store = None


def _get_store():
    global _store
    if _store is None:
        _store = load_store()
    return _store


def _slugify(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "_", normalized.lower()).strip("_")
    return f"custom_{slug}" if slug else "custom_criterion"


def retrieve_examples(
    criterion: CriterionWeight,
    proposal_context: str = "",
    requirement_context: str = "",
    top_k: int = 1,
    min_hybrid_score: float = 0.45,
) -> list[dict]:
    """Benchmark examples for this criterion, or [] if excluded/no match.

    Each item has exactly {"text", "sample_type", "reasoning"} — see
    backend/rag/README.md "JSON filtering contract".
    """
    if criterion.name in _EXCLUDED_BASE_CRITERIA:
        return []

    criterion_id = _CANONICAL_ID_BY_NAME.get(criterion.name) or _slugify(criterion.name)
    payload = {
        "criterion": {
            "id": criterion_id,
            "name": criterion.name,
            "description": criterion.description,
        },
        "proposal_context": proposal_context,
        "requirement_context": requirement_context,
        "top_k": top_k,
        "min_hybrid_score": min_hybrid_score,
    }
    result = retrieve_payload(_get_store(), payload)
    return result["matches"]
