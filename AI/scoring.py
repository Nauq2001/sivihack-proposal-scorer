"""Proposal Analyst / Scoring Agent — the AI team's core deliverable.

score_proposal() is the one function Backend should import:

    from AI.scoring import score_proposal
    from AI.contracts import ScoringInput

    result = score_proposal(ScoringInput.model_validate(request_json))

Everything else in this module is an implementation detail.
"""

from __future__ import annotations

from AI.contracts import (
    ProposalAnalystOutput,
    RequirementFinding,
    ScoringInput,
    ScoringResult,
)
from AI.llm_client import call_ai_json
from AI.prompts import build_proposal_analyst_prompt
from AI.rag_client import retrieve_examples


class ScoringValidationError(ValueError):
    """The LLM's output failed a semantic invariant check (not just JSON shape)."""


def _enforce_hard_constraint_severity(
    findings: list[RequirementFinding], scoring_input: ScoringInput
) -> None:
    hard_constraint_ids = {
        r.id for r in scoring_input.rfp_analysis.requirements if r.is_hard_constraint
    }
    for finding in findings:
        if finding.requirement_id in hard_constraint_ids and finding.status == "contradicted":
            finding.severity = "high"
        if finding.status == "missing":
            finding.citation = ""


def _compute_requirement_based_score(requirement_ids: list[str], findings_by_id: dict) -> int:
    """Deterministic 1-5 score from requirement statuses: met=1.0 credit,
    vague=0.5, missing/contradicted=0.0 credit, averaged then bucketed.
    Mirrors the "requirement-linked" prompt rubric as arithmetic — used to
    override the LLM's own score for "Completeness vs RFP Requirements",
    since that criterion is cross-cutting over (near-)all requirements and
    fully derivable from findings, so it shouldn't depend on the LLM
    synthesizing the count correctly every run.
    """
    linked = [findings_by_id[rid] for rid in requirement_ids if rid in findings_by_id]
    if not linked:
        return 3
    credit = {"met": 1.0, "vague": 0.5, "missing": 0.0, "contradicted": 0.0}
    proportion = sum(credit[f.status] for f in linked) / len(linked)
    if proportion >= 1.0:
        return 5
    if proportion >= 0.8:
        return 4
    if proportion >= 0.5:
        return 3
    if proportion > 0.0:
        return 2
    return 1


def _hard_constraint_cap(
    requirement_ids: list[str], findings_by_id: dict, hard_constraint_ids: set
) -> int | None:
    """2 if a hard-constraint requirement linked to this criterion is
    contradicted, else None. Enforced the same way as severity above: the
    prompt guides the model toward this, but the cap is only guaranteed by
    applying it here, so it never depends on the LLM applying it consistently.
    """
    for rid in requirement_ids:
        if rid in hard_constraint_ids:
            finding = findings_by_id.get(rid)
            if finding and finding.status == "contradicted":
                return 2
    return None


def _priority_adjusted_score(score: int, priority: str) -> int:
    """User-chosen priority is a strictness dial, not just an aggregation
    weight: "low" means the user has decided this criterion matters less for
    this review, so gaps here are graded more leniently; "high" means graded
    more strictly. Applied as a flat +-1 nudge on top of the LLM's objective,
    rubric-based score — the rubric itself never changes per criterion (still
    consistent/comparable), only the final number shifts a bit either way.
    """
    if priority == "low":
        return min(5, score + 1)
    if priority == "high":
        return max(1, score - 1)
    return score


def _enforce_criterion_score_rules(
    output: ProposalAnalystOutput, scoring_input: ScoringInput
) -> None:
    packets_by_name = {
        p.criterion_name: p for p in scoring_input.rfp_analysis.criterion_packets
    }
    findings_by_id = {f.requirement_id: f for f in output.findings}
    hard_constraint_ids = {
        r.id for r in scoring_input.rfp_analysis.requirements if r.is_hard_constraint
    }
    priority_by_name = {c.name: c.recommended_priority for c in scoring_input.confirmed_criteria}
    for criterion in output.criteria:
        packet = packets_by_name.get(criterion.name)
        requirement_ids = packet.requirement_ids if packet else []
        if criterion.name == "Completeness vs RFP Requirements" and requirement_ids:
            criterion.score = _compute_requirement_based_score(requirement_ids, findings_by_id)

        criterion.score = _priority_adjusted_score(
            criterion.score, priority_by_name.get(criterion.name, "medium")
        )

        # Hard-constraint cap is a safety floor, not subject to the priority
        # nudge above — a proposal cannot buy its way out of a contradicted
        # hard constraint (e.g. the PostgreSQL migration case) just because
        # the user dragged that criterion to "Low". Applied last so it always
        # wins over whatever the nudge produced.
        cap = _hard_constraint_cap(requirement_ids, findings_by_id, hard_constraint_ids)
        if cap is not None:
            criterion.score = min(criterion.score, cap)


def _validate_output(scoring_input: ScoringInput, output: ProposalAnalystOutput) -> None:
    requirement_ids = {r.id for r in scoring_input.rfp_analysis.requirements}
    finding_ids = {f.requirement_id for f in output.findings}
    missing = requirement_ids - finding_ids
    unknown = finding_ids - requirement_ids
    if missing:
        raise ScoringValidationError(f"LLM omitted findings for requirement ids: {sorted(missing)}")
    if unknown:
        raise ScoringValidationError(f"LLM invented unknown requirement ids: {sorted(unknown)}")

    confirmed_names = {c.name for c in scoring_input.confirmed_criteria}
    scored_names = {c.name for c in output.criteria}
    if confirmed_names != scored_names:
        raise ScoringValidationError(
            f"Criterion mismatch — expected {sorted(confirmed_names)}, got {sorted(scored_names)}"
        )


def compute_overall_score(scoring_input: ScoringInput, criteria) -> float:
    weight_by_name = {c.name: c.weight for c in scoring_input.confirmed_criteria}
    scored = [c for c in criteria if c.name in weight_by_name]
    total_weight = sum(weight_by_name[c.name] for c in scored)
    if total_weight <= 0:
        return 0.0
    weighted_sum = sum(c.score * weight_by_name[c.name] for c in scored)
    return round(weighted_sum / total_weight, 1)


def _requirement_context_for(scoring_input: ScoringInput, criterion_name: str) -> str:
    packets_by_name = {p.criterion_name: p for p in scoring_input.rfp_analysis.criterion_packets}
    packet = packets_by_name.get(criterion_name)
    if not packet:
        return ""
    requirements_by_id = {r.id: r for r in scoring_input.rfp_analysis.requirements}
    texts = [requirements_by_id[rid].text for rid in packet.requirement_ids if rid in requirements_by_id]
    return " ".join(texts)


def score_proposal(scoring_input: ScoringInput, max_semantic_retries: int = 1) -> ScoringResult:
    examples_by_criterion = {
        c.name: retrieve_examples(
            c,
            proposal_context=scoring_input.raw_proposal_text,
            requirement_context=_requirement_context_for(scoring_input, c.name),
        )
        for c in scoring_input.confirmed_criteria
    }
    base_prompt = build_proposal_analyst_prompt(
        rfp_analysis=scoring_input.rfp_analysis,
        raw_rfp_text=scoring_input.raw_rfp_text,
        raw_proposal_text=scoring_input.raw_proposal_text,
        confirmed_criteria=scoring_input.confirmed_criteria,
        examples_by_criterion=examples_by_criterion,
    )

    prompt = base_prompt
    last_error: Exception | None = None
    for _ in range(max_semantic_retries + 1):
        output = call_ai_json(prompt, ProposalAnalystOutput)
        _enforce_hard_constraint_severity(output.findings, scoring_input)
        _enforce_criterion_score_rules(output, scoring_input)
        try:
            _validate_output(scoring_input, output)
        except ScoringValidationError as exc:
            last_error = exc
            prompt = (
                f"{base_prompt}\n\n---\nYour previous answer failed validation: {exc}\n"
                f"Fix this and return the full corrected JSON."
            )
            continue

        return ScoringResult(
            client_name=scoring_input.rfp_analysis.client_name,
            project_name=scoring_input.rfp_analysis.project_name,
            findings=output.findings,
            criteria=output.criteria,
            overall_score=compute_overall_score(scoring_input, output.criteria),
            verdict=output.verdict,
        )

    raise ScoringValidationError(f"Scoring failed semantic validation after retries: {last_error}")
