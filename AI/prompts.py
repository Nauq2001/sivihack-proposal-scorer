"""Prompt construction for the Proposal Analyst (Scoring Agent) LLM call."""

from __future__ import annotations

import json

from AI.contracts import CriterionWeight, RFPAnalysis
from AI.rag_client import format_benchmark_references

SYSTEM_PERSONA = """You are a senior bid/proposal reviewer with 15+ years evaluating \
B2B enterprise IT/cloud/AI proposals against client RFPs. You are reviewing an EXISTING \
draft proposal — you never rewrite it from scratch, you only critique it and suggest \
fixes. Every score and every issue you raise must point to a specific requirement or \
quote, never a generic remark like "could be clearer"."""


def _format_requirements(rfp_analysis: RFPAnalysis) -> str:
    lines = []
    for req in rfp_analysis.requirements:
        flag = " [HARD CONSTRAINT]" if req.is_hard_constraint else ""
        lines.append(
            f'- {req.id}{flag} ({req.source_section}): {req.text}\n'
            f'  RFP quote: "{req.source_quote}"'
        )
    return "\n".join(lines)


def _format_packets(rfp_analysis: RFPAnalysis, confirmed_criteria: list[CriterionWeight]) -> str:
    packets_by_name = {p.criterion_name: p for p in rfp_analysis.criterion_packets}
    blocks = []
    for c in confirmed_criteria:
        packet = packets_by_name.get(c.name)
        guidance = packet.evaluation_guidance if packet else []
        req_ids = packet.requirement_ids if packet else []
        notes = packet.notes if packet else []
        blocks.append(
            f"### {c.name} (weight={c.weight})\n"
            f"Description: {c.description}\n"
            f"Evaluation guidance: {guidance or '(none provided)'}\n"
            f"Relevant requirement IDs: {req_ids or '(none — score from description/proposal directly)'}\n"
            f"Notes: {notes or '(none)'}"
        )
    return "\n\n".join(blocks)


def _format_examples(
    confirmed_criteria: list[CriterionWeight],
    examples_by_criterion: dict[str, list[dict]],
) -> str:
    blocks = []
    for c in confirmed_criteria:
        matches = examples_by_criterion.get(c.name) or []
        if not matches:
            continue
        blocks.append(f"### {c.name}\n{format_benchmark_references(matches)}")
    return "\n\n".join(blocks) if blocks else "(no benchmark examples retrieved for the confirmed criteria)"


_SCHEMA_HINT = {
    "findings": [
        {
            "requirement_id": "REQ-003",
            "status": "met | missing | vague | contradicted",
            "severity": "high | medium | low",
            "reason": "why you gave this status, referencing the proposal's own wording",
            "citation": 'exact quote/location from the PROPOSAL, or "" if status=missing',
            "suggested_patch": "a concrete rewritten sentence/paragraph or addition that fixes this",
        }
    ],
    "criteria": [
        {
            "name": "must be one of the confirmed criteria names below, verbatim",
            "score": "integer 1-5",
            "comment": "specific justification citing findings and/or the proposal text",
            "citations": ["short quotes or requirement ids backing this score"],
        }
    ],
    "verdict": "2-4 sentence overall summary, most severe issues first",
}


def build_proposal_analyst_prompt(
    rfp_analysis: RFPAnalysis,
    raw_rfp_text: str,
    raw_proposal_text: str,
    confirmed_criteria: list[CriterionWeight],
    examples_by_criterion: dict[str, list[dict]] | None = None,
) -> str:
    examples_by_criterion = examples_by_criterion or {}
    return f"""{SYSTEM_PERSONA}

# RFP requirements (extracted upstream; each has a stable ID)
{_format_requirements(rfp_analysis)}

# Full RFP text (for extra context/quoting if needed)
{raw_rfp_text}

# Full proposal text to review
{raw_proposal_text}

# Criteria to score (confirmed by the user — score EXACTLY this list, nothing more/less)
{_format_packets(rfp_analysis, confirmed_criteria)}

# Benchmark examples for writing-quality calibration (never evidence about the current documents)
{_format_examples(confirmed_criteria, examples_by_criterion)}

# Instructions
Work through this in order:
1. For EVERY requirement listed above, decide status/severity/reason/citation/suggested_patch.
   - If a requirement is marked [HARD CONSTRAINT] and the proposal does something that
     directly contradicts it, status MUST be "contradicted" and severity MUST be "high".
   - If you find no evidence at all in the proposal for a requirement, status is "missing"
     and citation MUST be "" — never invent a quote for something that isn't there.
   - If it's mentioned but too vague to confirm it satisfies the requirement, status is "vague".
2. For each criterion listed above, produce ONE score 1-5 with a specific comment, informed
   by the findings that relate to it ("Relevant requirement IDs") plus, only where benchmark
   examples are given above, how the proposal's writing compares to them — never to decide
   whether a requirement was met. A criterion with no related requirement IDs and no
   benchmark examples (e.g. a custom criterion) must be judged directly from its description
   and the proposal text — do not invent a requirement for it.
3. Write the overall verdict.

Return ONLY JSON matching this exact shape, no markdown fences, no extra prose:
{json.dumps(_SCHEMA_HINT, indent=2)}
"""
