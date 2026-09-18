"""
Loads the enterprise corpus and decides what is allowed to be used.

The gate is re-run here on every load. The fixtures carry their own
`demo_gate_result`, but a self-declared flag is not proof, so this module
recomputes admission from the metadata itself and keeps its own reasons.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterable

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "enterprise_demo"

# Metadata a proposal must carry before it may be retrieved at all.
REQUIRED_FIELDS = (
    "record_id", "industry", "country", "service_type",
    "value_band", "outcome", "quality_score", "submitted_date",
)
GOOD_QUALITY = 4.0     # at or above: usable as a reference to copy from
POOR_QUALITY = 3.0     # below: an anti-pattern, never shown as a good example
STALE_AFTER_DAYS = 183  # ~6 months; a standard older than this stops being "current"


@dataclass
class Record:
    """One admitted proposal in the corpus."""
    data: dict[str, Any]
    warnings: list[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        return self.data["record_id"]

    @property
    def outcome(self) -> str:
        return self.data["outcome"]

    @property
    def quality(self) -> float:
        return float(self.data["quality_score"])

    @property
    def bucket(self) -> str:
        if self.quality >= GOOD_QUALITY:
            return "good"
        if self.quality < POOR_QUALITY:
            return "poor"
        return "intermediate"

    @property
    def role(self) -> str:
        """Which of the four won/lost x good/poor cells this record sits in.

        Only 'gold_reference' may be held up as an example to follow, and only
        'anti_pattern' as a warning. A proposal that won while badly written
        won on something else; one that lost while well written did not lose on
        the writing.
        """
        if self.outcome == "won" and self.bucket == "good":
            return "gold_reference"
        if self.outcome == "lost" and self.bucket == "poor":
            return "anti_pattern"
        return "context_only"

    @property
    def cross_deal_ok(self) -> bool:
        d = self.data
        return bool(
            d.get("cross_deal_use")
            and d.get("anonymized_customer_names")
            and d.get("anonymized_amounts")
            and d.get("sanitized_document")
        )


@dataclass
class Rejection:
    record_id: str
    errors: list[str]


def _parse_date(value: str | None) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def _gate_record(data: dict[str, Any], *, production: bool, today: date) -> tuple[list[str], list[str]]:
    """Returns (errors, warnings). A record with errors is not loaded."""
    errors: list[str] = []
    warnings: list[str] = []

    for f in REQUIRED_FIELDS:
        if data.get(f) in (None, ""):
            errors.append(f"missing_metadata:{f}")

    if data.get("status") == "draft":
        errors.append("draft_not_admitted")

    method = (data.get("quality_provenance") or {}).get("method")
    if method != "ingestion_scoring_api":
        if production:
            errors.append("quality_must_be_scored_by_ingestion_api")
        else:
            warnings.append(f"quality_score_from:{method or 'unknown'}")

    if data.get("fictional") and production:
        errors.append("fictional_document_in_production")

    submitted = _parse_date(data.get("submitted_date"))
    if submitted and (today - submitted).days > 365 * 3:
        warnings.append("older_than_three_years")

    if not data.get("cross_deal_use"):
        warnings.append("not_cleared_for_cross_deal_use")

    return errors, warnings


def _gate_standard(data: dict[str, Any], *, today: date) -> tuple[bool, list[str]]:
    """A stale rate card or SLA may still be read, but not asserted as current."""
    warnings: list[str] = []
    stamp = _parse_date(data.get("effective_from") or data.get("approved_date"))
    current = True
    if stamp is None:
        current = False
        warnings.append("no_effective_date")
    elif (today - stamp).days > STALE_AFTER_DAYS:
        current = False
        warnings.append(f"stale_since:{stamp.isoformat()}")
    return current, warnings


@dataclass
class Corpus:
    records: dict[str, Record]
    chunks: list[dict[str, Any]]
    standards: dict[str, dict[str, Any]]
    rejected: list[Rejection]
    stale_standards: list[str]
    production: bool

    @property
    def gold_ids(self) -> set[str]:
        return {r.id for r in self.records.values() if r.role == "gold_reference"}

    @property
    def anti_pattern_ids(self) -> set[str]:
        return {r.id for r in self.records.values() if r.role == "anti_pattern"}

    def standard(self, document_type: str) -> dict[str, Any] | None:
        for s in self.standards.values():
            if s["document_type"] == document_type:
                return s
        return None

    def clauses(self, section_role: str | None = None) -> list[dict[str, Any]]:
        out = [s for s in self.standards.values() if s["document_type"] == "approved_clause"]
        if section_role:
            out = [c for c in out if c.get("section_role") == section_role]
        return out

    def report(self) -> dict[str, Any]:
        """What was admitted, what was not, and why — shown in the UI and logs."""
        return {
            "corpus_dir": str(DATA_DIR),
            "mode": "production" if self.production else "demo",
            "admitted_records": len(self.records),
            "rejected_records": [{"record_id": r.record_id, "errors": r.errors} for r in self.rejected],
            "chunks": len(self.chunks),
            "roles": {
                "gold_reference": sorted(self.gold_ids),
                "anti_pattern": sorted(self.anti_pattern_ids),
                "context_only": sorted(
                    r.id for r in self.records.values() if r.role == "context_only"
                ),
            },
            "standards": sorted(self.standards),
            "stale_standards": self.stale_standards,
            "warnings": {r.id: r.warnings for r in self.records.values() if r.warnings},
        }


def load_corpus(data_dir: Path | str = DATA_DIR, *, production: bool = False,
                today: date | None = None) -> Corpus:
    data_dir = Path(data_dir)
    today = today or date.today()

    raw_records = json.loads((data_dir / "records.json").read_text())["records"]
    records: dict[str, Record] = {}
    rejected: list[Rejection] = []
    for data in raw_records:
        errors, warnings = _gate_record(data, production=production, today=today)
        if errors:
            rejected.append(Rejection(data.get("record_id", "?"), errors))
            continue
        records[data["record_id"]] = Record(data=data, warnings=warnings)

    chunks = [json.loads(line) for line in (data_dir / "chunks.jsonl").read_text().splitlines() if line.strip()]
    # A chunk of a rejected document must not be retrievable.
    chunks = [c for c in chunks if c["record_id"] in records]

    standards: dict[str, dict[str, Any]] = {}
    stale: list[str] = []
    for data in json.loads((data_dir / "standards.json").read_text())["records"]:
        current, warnings = _gate_standard(data, today=today)
        data = dict(data, is_current=current, gate_warnings=warnings)
        if not current:
            stale.append(data["record_id"])
        standards[data["record_id"]] = data

    return Corpus(
        records=records,
        chunks=chunks,
        standards=standards,
        rejected=rejected,
        stale_standards=stale,
        production=production,
    )


def sanitized_text(corpus: Corpus, record_id: str, data_dir: Path | str = DATA_DIR) -> str | None:
    """The redacted full document, for records cleared for cross-deal use."""
    record = corpus.records.get(record_id)
    if not record or not record.cross_deal_ok:
        return None
    path = Path(data_dir) / record.data["sanitized_document"]
    return path.read_text() if path.exists() else None


def iter_chunks(corpus: Corpus, **filters: Any) -> Iterable[dict[str, Any]]:
    """Metadata filtering happens before any text matching — that is what keeps
    a retrieval from quoting a lost deal as if it were a good example."""
    for chunk in corpus.chunks:
        record = corpus.records[chunk["record_id"]]
        if filters.get("section_role") and chunk["section_role"] != filters["section_role"]:
            continue
        if filters.get("outcome") and chunk["outcome"] != filters["outcome"]:
            continue
        if filters.get("industry") and chunk["industry"] != filters["industry"]:
            continue
        if filters.get("country") and chunk["country"] != filters["country"]:
            continue
        if filters.get("service_type") and chunk["service_type"] != filters["service_type"]:
            continue
        min_quality = filters.get("min_quality")
        if min_quality is not None and float(chunk["quality_score"]) < float(min_quality):
            continue
        role = filters.get("role")
        if role and record.role != role:
            continue
        if filters.get("cross_deal_only") and not record.cross_deal_ok:
            continue
        yield chunk
