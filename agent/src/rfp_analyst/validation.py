from __future__ import annotations

import re

from .models import RFPAnalysis


class ContractError(ValueError):
    pass


def reconcile_quote(candidate: str, source_text: str) -> str:
    """Return the exact source span for a quote differing only in whitespace."""
    if candidate in source_text:
        return candidate
    tokens = re.findall(r"\S+", candidate)
    if not tokens:
        return candidate
    pattern = r"\s+".join(re.escape(token) for token in tokens)
    match = re.search(pattern, source_text)
    if match:
        return match.group(0)

    def clean(token: str) -> str:
        return re.sub(r"[*_`]+", "", token)

    candidate_tokens = [clean(token) for token in tokens]
    source_matches = list(re.finditer(r"\S+", source_text))
    source_tokens = [clean(match.group(0)) for match in source_matches]
    size = len(candidate_tokens)
    for start in range(len(source_tokens) - size + 1):
        if source_tokens[start : start + size] == candidate_tokens:
            return source_text[source_matches[start].start() : source_matches[start + size - 1].end()]
    return candidate


def _unique(values: list[str], code: str) -> None:
    if len(values) != len(set(values)):
        raise ContractError(code)


def validate_analysis(analysis: RFPAnalysis, raw_rfp_text: str) -> None:
    requirement_ids = [requirement.id for requirement in analysis.requirements]
    criterion_names = [criterion.name for criterion in analysis.suggested_criteria_weights]
    packet_names = [packet.criterion_name for packet in analysis.criterion_packets]
    _unique(requirement_ids, "DUPLICATE_REQUIREMENT_ID")
    _unique(criterion_names, "DUPLICATE_CRITERION_NAME")
    _unique(packet_names, "DUPLICATE_PACKET")

    if set(criterion_names) != set(packet_names):
        raise ContractError("PACKET_MISMATCH")

    requirement_id_set = set(requirement_ids)
    for requirement in analysis.requirements:
        if requirement.source_quote not in raw_rfp_text:
            raise ContractError(f"QUOTE_NOT_FOUND: {requirement.id}")
    for packet in analysis.criterion_packets:
        unknown = set(packet.requirement_ids) - requirement_id_set
        if unknown:
            raise ContractError(f"UNKNOWN_REQUIREMENT: {sorted(unknown)}")
        for source in packet.source_refs:
            if source.quote not in raw_rfp_text:
                raise ContractError(f"QUOTE_NOT_FOUND: packet {packet.criterion_name}")
