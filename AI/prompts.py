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


_REQUIREMENT_LINKED_RUBRIC = """
Score anchors for criteria that DO have "Relevant requirement IDs" listed
above (apply the same meaning to every such criterion):
1: Fundamentally non-compliant: no material requirement is met, or a critical
   hard constraint related to this criterion is contradicted. (Note: if a
   hard constraint here is contradicted, the scoring pipeline will cap this
   criterion's final score at 2 regardless of what you write — write 1 or 2
   as your honest read, don't strain to justify exactly "1".)
2: Some relevant content exists, but most material requirements are missing,
   vague, or contradicted.
3: Most material requirements are met, but at least one significant gap,
   omission, or ambiguity remains.
4: All material requirements are met; only minor ambiguity or detail is missing.
5: All related requirements are met with specific, internally consistent,
   evidence-backed commitments.
Note: "Completeness vs RFP Requirements" specifically will have its score
recomputed deterministically from your findings afterward — still give your
own honest score here, it's used as a sanity cross-check.
"""

_HOLISTIC_RUBRIC = """
Score anchors for criteria that do NOT have any "Relevant requirement IDs"
listed above (e.g. Problem Understanding, Tone & Persuasiveness, or a custom
criterion with no requirement IDs) — judged directly from the description
and the proposal/RFP text, not from a requirement checklist:
1: Ignores, misunderstands, or contradicts the client's actual stated
   problem/goal — or is boilerplate so generic it could apply to any client
   (no reference to this client's specific situation at all).
2: Correctly identifies the client's actual problem/goal, but only restates
   it thinly — no elaboration on their specific situation beyond the ask.
3: Correct and client-relevant, but underspecified or weakly evidenced.
4: Specific and credible with only minor weaknesses.
5: Comprehensive, client-specific, credible, and supported by precise evidence.
"""

_COMMENT_RULE = """
Every criterion's "comment" must: state the concrete strength or gap, cite
at least one requirement ID or an exact proposal quote, and explain what
separates this score from the next higher score. Generic remarks like
"could be clearer" without a citation are not acceptable.
"""

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
            "score": "integer 1-5 — follow the score anchors given in the instructions",
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
{_REQUIREMENT_LINKED_RUBRIC}
{_HOLISTIC_RUBRIC}
{_COMMENT_RULE}
3. Write the overall verdict.

Return ONLY JSON matching this exact shape, no markdown fences, no extra prose:
{json.dumps(_SCHEMA_HINT, indent=2)}
"""
