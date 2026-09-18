"""
What the corpus can say about a draft proposal.

Two jobs, kept apart on purpose:

* `benchmark_section` — retrieval. Passages from comparable proposals, so a
  reviewer can see how a section is usually written here.
* `check_commitments` — no retrieval, no model. Deterministic checks of what the
  draft promises against what the company has actually signed off: the rate
  card and the SLA standard. This is the part that catches an overpromise, and
  it has to be reproducible, so it is plain string matching with a verbatim
  quote attached to every finding.

Neither of these replaces the RFP or the proposal when scoring. The scorer
always reads both documents in full; the corpus only adds company context.
"""

from __future__ import annotations

import re
from typing import Any

from .retrieve import Hit, anti_patterns, gold_references, search
from .store import Corpus

# Sentences may wrap across lines, so newlines do not end one. The slice is
# returned untouched, which keeps every quote verbatim in the source.
_SENTENCE = re.compile(r"[^.!?]*[.!?]|[^.!?]+")

# A promise of round-the-clock cover.
ALWAYS_ON = re.compile(r"\b24\s*[/x×]\s*7\b|\b24\s*hours\s*a\s*day\b|around[- ]the[- ]clock", re.I)
# Cover on days the standard does not include.
OFF_HOURS = re.compile(r"\bweekends?\b|\bsaturdays?\b|\bsundays?\b|public holidays?", re.I)
# A promise to *fix* inside a window, not merely to answer.
RESTORATION = re.compile(
    r"\b(restor\w+|resolv\w+|fix\w*|repair\w*)\b[^.!?\n]{0,80}?\bwithin\b[^.!?\n]{0,40}?\b(hour|hours|day|days|minutes)\b",
    re.I,
)
# Day rates, in the shapes people actually write them.
DAY_RATE = re.compile(
    r"(?:€\s*|eur\s*)(\d[\d.,]*)\s*(?:per|/|a)\s*(?:person[- ])?day|(\d[\d.,]*)\s*(?:€|eur)\s*(?:per|/|a)\s*(?:person[- ])?day",
    re.I,
)


def _trim_heading(slice_: str) -> str:
    """Drop the markdown heading a sentence may have swallowed, since a heading
    carries no full stop. What is left is still a contiguous slice of the
    source, so the quote stays verifiable."""
    lines = slice_.split("\n")
    while lines and (not lines[0].strip() or lines[0].lstrip().startswith("#")):
        lines.pop(0)
    return "\n".join(lines).strip()


def _sentence_around(text: str, start: int) -> str:
    """The sentence a match sits in, returned verbatim so it can be verified."""
    for m in _SENTENCE.finditer(text):
        if m.start() <= start < m.end():
            return _trim_heading(m.group())
    return text[max(0, start - 80): start + 80].strip()


def _finding(rule: str, severity: str, quote: str, message: str, standard: dict[str, Any],
             field: str) -> dict[str, Any]:
    current = standard.get("is_current", True)
    return {
        "rule": rule,
        # A standard that is out of date can still raise the question, but it
        # must not be presented as the current rule.
        "severity": severity if current else "check",
        "quote": quote,
        "message": message if current else f"{message} (the standard on file is out of date, confirm before relying on it)",
        "standard": {
            "record_id": standard["record_id"],
            "document_type": standard["document_type"],
            "field": field,
            "is_current": current,
            "effective_from": standard.get("effective_from") or standard.get("approved_date"),
            "fictional": standard.get("fictional", False),
        },
    }


def check_commitments(corpus: Corpus, text: str) -> dict[str, Any]:
    """Promises in the draft that the company cannot currently back."""
    findings: list[dict[str, Any]] = []
    sla = corpus.standard("sla_standard")
    rate_card = corpus.standard("rate_card")

    if sla:
        capability = sla.get("delivery_capability", {})
        coverage = sla.get("coverage", "")

        flagged_coverage: set[str] = set()
        if not capability.get("24_7_on_call_available", False):
            for m in ALWAYS_ON.finditer(text):
                flagged_coverage.add(_sentence_around(text, m.start()))
                findings.append(_finding(
                    "coverage_beyond_capability", "high",
                    _sentence_around(text, m.start()),
                    f"The proposal promises round-the-clock cover. Standard support is “{coverage}” "
                    "and 24/7 on-call is not validated capacity.",
                    sla, "delivery_capability.24_7_on_call_available",
                ))
            for m in OFF_HOURS.finditer(text):
                sentence = _sentence_around(text, m.start())
                # Already covered by the stronger round-the-clock finding.
                if sentence in flagged_coverage:
                    continue
                findings.append(_finding(
                    "coverage_outside_standard_hours", "medium",
                    sentence,
                    f"The proposal implies cover outside standard support hours (“{coverage}”).",
                    sla, "coverage",
                ))

        for m in RESTORATION.finditer(text):
            findings.append(_finding(
                "restoration_guarantee", "high",
                _sentence_around(text, m.start()),
                "This guarantees a fix inside a window. The SLA standard commits to acknowledgement, "
                "not restoration, because restoration depends on diagnosis and third parties.",
                sla, "note",
            ))

    if rate_card:
        floor = min((r["floor"] for r in rate_card.get("rates", [])), default=None)
        if floor is not None:
            for m in DAY_RATE.finditer(text):
                raw = m.group(1) or m.group(2)
                try:
                    value = float(raw.replace(".", "").replace(",", "."))
                except ValueError:
                    continue
                if value < floor:
                    findings.append(_finding(
                        "day_rate_below_floor", "high",
                        _sentence_around(text, m.start()),
                        f"A day rate of {value:,.0f} {rate_card.get('currency', 'EUR')} is below the "
                        f"lowest rate on the current card ({floor:,.0f}).",
                        rate_card, "rates.floor",
                    ))

    # Deduplicate: the same sentence can trip two patterns.
    seen: set[tuple[str, str]] = set()
    unique = []
    for f in findings:
        key = (f["rule"], f["quote"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(f)

    return {
        "findings": unique,
        "standards_checked": [s["record_id"] for s in (sla, rate_card) if s],
        "stale_standards": corpus.stale_standards,
    }


def benchmark_section(corpus: Corpus, section_role: str, *, query: str = "", limit: int = 3,
                      **filters: Any) -> dict[str, Any]:
    """How comparable proposals wrote this section, with provenance for each."""
    gold = gold_references(corpus, section_role, query=query, limit=limit, **filters)
    return {
        "section_role": section_role,
        "filters": {k: v for k, v in filters.items() if v is not None},
        "gold_references": [h.to_dict() for h in gold],
        "anti_patterns": [h.to_dict() for h in anti_patterns(corpus, section_role, limit=2)],
        "approved_clauses": [
            {
                "record_id": c["record_id"],
                "text": c["text"],
                "approved_by": c.get("approved_by"),
                "approved_date": c.get("approved_date"),
                "language": c.get("language"),
            }
            for c in corpus.clauses(section_role)
        ],
        # Say plainly how many documents actually backed this answer, so nobody
        # reads "3 of 3" into a corpus that only held one match.
        "matched_documents": sorted({h.chunk["record_id"] for h in gold}),
    }


def free_search(corpus: Corpus, query: str, *, limit: int = 5, **filters: Any) -> dict[str, Any]:
    hits = search(corpus, query, limit=limit, **filters)
    return {"query": query, "hits": [h.to_dict() for h in hits], "matched": len(hits)}
