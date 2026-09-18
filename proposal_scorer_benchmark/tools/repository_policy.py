"""Repository admission and cross-deal use gates. No network calls."""
from calendar import monthrange
from datetime import date, datetime
import re


def six_month_cutoff(today):
    index = today.year * 12 + today.month - 1 - 6
    year, month_zero = divmod(index, 12)
    month = month_zero + 1
    return date(year, month, min(today.day, monthrange(year, month)[1]))


def _parsed(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except (ValueError, TypeError, AttributeError):
        return None


def admission(record, today=None, demo=False):
    today = today or date.today()
    kind = record.get("document_type")
    errors, warnings = [], []
    required = {
        "proposal": ["industry", "country", "value_band", "service_type", "submitted_date", "outcome", "quality_score", "quality_provenance"],
        "rate_card": ["effective_from", "currency"],
        "sla_standard": ["version", "approved_date"],
        "delivery_capability": ["version", "approved_date"],
        "approved_clause": ["approved_by", "approved_date", "language"],
        "review_history": ["quality_score", "gaps", "reviewer"],
    }
    if kind not in required:
        errors.append("unknown_document_type")
    for field in required.get(kind, []):
        if field not in record or record[field] is None or record[field] == "":
            errors.append(f"missing:{field}")
    if kind == "proposal":
        if record.get("status") != "submitted":
            errors.append("proposal_is_not_submitted")
        if record.get("outcome") not in {"won", "lost", "pending"}:
            errors.append("invalid_outcome")
        score = record.get("quality_score")
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not 1 <= score <= 5:
            errors.append("invalid_quality_score")
        provenance = record.get("quality_provenance", {})
        if not isinstance(provenance, dict):
            errors.append("invalid_quality_provenance")
            provenance = {}
        if any(not provenance.get(key) for key in ("scorer_version", "rubric_version", "scored_at", "input_sha256")):
            errors.append("quality_provenance_incomplete")
        input_hash = provenance.get("input_sha256")
        if not isinstance(input_hash, str) or re.fullmatch(r"[0-9a-f]{64}", input_hash) is None:
            errors.append("invalid_input_hash")
        scored = _parsed(provenance.get("scored_at"))
        if scored is None or scored > today:
            errors.append("invalid_scored_at")
        if provenance.get("method") != "scoring_api":
            if demo and provenance.get("method") == "mock_scoring_api" and record.get("fictional") is True:
                warnings.append("synthetic_score_not_an_actual_api_evaluation")
            else:
                errors.append("quality_must_be_scored_by_ingestion_api")
        submitted = _parsed(record.get("submitted_date"))
        if submitted is None or submitted > today:
            errors.append("invalid_submitted_date")
        if record.get("cross_deal_use") is True:
            if record.get("anonymized_customer_names") is not True:
                errors.append("customer_names_not_anonymized")
            if record.get("anonymized_amounts") is not True:
                errors.append("amounts_not_anonymized")
            if not record.get("sanitized_document"):
                errors.append("sanitized_document_missing")
    freshness_field = "effective_from" if kind == "rate_card" else "approved_date"
    if kind == "approved_clause":
        approved = _parsed(record.get("approved_date"))
        if approved is None or approved > today:
            errors.append("invalid_clause_approval_date")
    authoritative = kind in {"rate_card", "sla_standard", "delivery_capability"}
    fresh = True
    if authoritative:
        approved = _parsed(record.get(freshness_field))
        if approved is None or approved > today:
            errors.append("invalid_authority_date")
            fresh = False
        elif approved < six_month_cutoff(today):
            warnings.append("needs_reverification_older_than_six_months")
            fresh = False
    admitted = not errors
    return {"admitted": admitted, "errors": errors, "warnings": warnings,
            "may_assert_as_current_standard": admitted and authoritative and fresh,
            "may_use_cross_deal": admitted and kind == "proposal" and record.get("cross_deal_use") is True}


def quality_bucket(score):
    if score >= 4:
        return "good"
    if score < 3:
        return "poor"
    return "intermediate"


def repository_role(record):
    bucket = quality_bucket(record["quality_score"])
    if record["outcome"] == "won" and bucket == "good":
        return "gold_reference"
    if record["outcome"] == "lost" and bucket == "poor":
        return "negative_reference"
    return "context_only"
