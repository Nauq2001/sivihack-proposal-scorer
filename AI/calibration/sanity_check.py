"""Pure-logic checks that need zero LLM API calls / zero Gemini budget (the
real backend/rag/ index is a local JSONL file, so exercising it here is free
and network-free too).

Verifies: the fixture parses against contracts.py, RAG example routing goes
to the right criteria (v2 hardened contract — exclusion enforced by Backend,
matches pre-trimmed to text/sample_type/reasoning), the hard-constraint
severity override works, and the weighted overall-score math is correct.
Run with:

    python3 -m AI.calibration.sanity_check

from the repo root (needed so `AI` and `backend` resolve as packages).
"""

from __future__ import annotations

import json
from pathlib import Path

from AI.contracts import CriterionScore, CriterionWeight, RequirementFinding, RFPAnalysis
from AI.rag_client import retrieve_examples
from AI.scoring import (
    _enforce_criterion_score_rules,
    _enforce_hard_constraint_severity,
    _priority_adjusted_score,
    compute_overall_score,
)
from AI.contracts import ProposalAnalystOutput, ScoringInput

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "nordframe_rfp_analysis.json"


def check(label: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        raise SystemExit(1)


def main() -> None:
    raw = json.loads(FIXTURE_PATH.read_text())
    rfp_analysis = RFPAnalysis.model_validate(raw)
    check("fixture parses against RFPAnalysis (incl. related_criterion validator)", True)
    check("19 requirements loaded", len(rfp_analysis.requirements) == 19)
    check(
        "client_name/project_name present",
        bool(rfp_analysis.client_name) and bool(rfp_analysis.project_name),
    )

    # Excluded criteria: Backend's retrieve_payload() raises ValueError for
    # these (v2 hardened contract); our client must not let that bubble up.
    for name in ("Problem Understanding", "Scope & Deliverables Clarity", "Completeness vs RFP Requirements"):
        result = retrieve_examples(
            CriterionWeight(name=name, description="x", weight=1),
            proposal_context="anything",
            requirement_context="anything",
        )
        check(f'retrieve_examples("{name}") is always empty (excluded)', result == [])

    pricing_matches = retrieve_examples(
        CriterionWeight(name="Pricing Clarity", description="Makes pricing clear", weight=1),
        proposal_context="Total project cost 102000 EUR, itemized breakdown by phase including first year support.",
        requirement_context="Budget 80000 to 120000 total including first year of support.",
    )
    check(
        "retrieve_examples(Pricing Clarity) returns matches pre-trimmed to text/sample_type/reasoning",
        len(pricing_matches) > 0 and all(set(m.keys()) == {"text", "sample_type", "reasoning"} for m in pricing_matches),
    )

    custom = CriterionWeight(
        name="Đào tạo nhân viên kho",
        description="Proposal cần có kế hoạch đào tạo cho nhân viên kho.",
        weight=1,
    )
    custom_matches = retrieve_examples(
        custom,
        proposal_context="training plan for warehouse staff onboarding sessions",
        requirement_context="",
    )
    check("custom criterion searches the whole corpus (non-empty)", len(custom_matches) > 0)

    scoring_input = ScoringInput(
        rfp_analysis=rfp_analysis,
        raw_rfp_text="placeholder",
        raw_proposal_text="placeholder",
        confirmed_criteria=rfp_analysis.suggested_criteria_weights,
    )

    findings = [
        RequirementFinding(
            requirement_id="REQ-007",
            status="contradicted",
            severity="low",  # deliberately wrong, to prove the override fires
            reason="Proposal migrates off Postgres despite the RFP's no-migration constraint.",
            citation="we recommend migrating away from your current PostgreSQL database",
        ),
        RequirementFinding(
            requirement_id="REQ-012",
            status="missing",
            severity="medium",
            reason="No support/maintenance section present.",
            citation="(model hallucinated this quote)",
        ),
    ]
    _enforce_hard_constraint_severity(findings, scoring_input)
    check(
        "hard-constraint contradiction forces severity=high regardless of model output",
        findings[0].severity == "high",
    )
    check(
        'status="missing" clears any citation the model invented',
        findings[1].citation == "",
    )

    # Deterministic criterion-score rules (v2): Completeness score computed
    # from findings, and a hard-constraint cap applied to any criterion.
    all_ids = [r.id for r in rfp_analysis.requirements]
    almost_all_met_findings = [
        RequirementFinding(requirement_id=rid, status="met", severity="low", reason="x")
        for rid in all_ids
    ]
    almost_all_met_findings[-1].status = "missing"  # 18/19 met, 1 missing -> 94.7% credit
    output = ProposalAnalystOutput(
        findings=almost_all_met_findings,
        criteria=[
            CriterionScore(name=c.name, score=1, comment="x")  # deliberately low, to prove override
            for c in rfp_analysis.suggested_criteria_weights
        ],
        verdict="x",
    )
    _enforce_criterion_score_rules(output, scoring_input)
    completeness = next(c for c in output.criteria if c.name == "Completeness vs RFP Requirements")
    check(
        "Completeness score computed from findings (18/19 met -> 4), not left at LLM's guess",
        completeness.score == 4,
    )

    hard_cap_findings = [
        RequirementFinding(requirement_id=rid, status="met", severity="low", reason="x")
        for rid in all_ids
    ]
    hard_cap_findings_by_id = {f.requirement_id: f for f in hard_cap_findings}
    hard_cap_findings_by_id["REQ-007"].status = "contradicted"  # a hard constraint under Scope
    output2 = ProposalAnalystOutput(
        findings=hard_cap_findings,
        criteria=[
            CriterionScore(name=c.name, score=5, comment="x")  # deliberately high, to prove the cap fires
            for c in rfp_analysis.suggested_criteria_weights
        ],
        verdict="x",
    )
    _enforce_criterion_score_rules(output2, scoring_input)
    scope = next(c for c in output2.criteria if c.name == "Scope & Deliverables Clarity")
    check(
        "hard-constraint contradiction caps Scope & Deliverables Clarity at 2 despite LLM giving 5",
        scope.score == 2,
    )
    unrelated = next(c for c in output2.criteria if c.name == "Pricing Clarity")
    check(
        "criteria not linked to the contradicted hard constraint are left uncapped",
        unrelated.score == 5,
    )

    # Priority as a strictness dial: "low" is more lenient (+1), "high" is
    # stricter (-1), "medium" is unchanged — but never outside 1-5.
    check("priority nudge: low +1", _priority_adjusted_score(3, "low") == 4)
    check("priority nudge: low clamps at 5", _priority_adjusted_score(5, "low") == 5)
    check("priority nudge: high -1", _priority_adjusted_score(3, "high") == 2)
    check("priority nudge: high clamps at 1", _priority_adjusted_score(1, "high") == 1)
    check("priority nudge: medium unchanged", _priority_adjusted_score(3, "medium") == 3)

    low_priority_input = scoring_input.model_copy(
        update={
            "confirmed_criteria": [
                CriterionWeight(
                    name=c.name, description="x", weight=1,
                    recommended_priority="low" if c.name == "Scope & Deliverables Clarity" else "medium",
                )
                for c in rfp_analysis.suggested_criteria_weights
            ]
        }
    )
    lenient_findings = [
        RequirementFinding(requirement_id=rid, status="met", severity="low", reason="x")
        for rid in all_ids
    ]
    output3 = ProposalAnalystOutput(
        findings=lenient_findings,
        criteria=[
            CriterionScore(name=c.name, score=3, comment="x")
            for c in rfp_analysis.suggested_criteria_weights
        ],
        verdict="x",
    )
    _enforce_criterion_score_rules(output3, low_priority_input)
    scope3 = next(c for c in output3.criteria if c.name == "Scope & Deliverables Clarity")
    check(
        "criterion set to 'low' priority gets its score nudged up by 1 (3 -> 4)",
        scope3.score == 4,
    )

    # But the hard-constraint cap still wins even when the user set that same
    # criterion to "low" — a contradicted hard constraint cannot be graded
    # away just by lowering the criterion's priority.
    hard_cap_low_findings_by_id = {f.requirement_id: f for f in lenient_findings}
    hard_cap_low_findings_by_id["REQ-007"].status = "contradicted"
    output4 = ProposalAnalystOutput(
        findings=list(hard_cap_low_findings_by_id.values()),
        criteria=[
            CriterionScore(name=c.name, score=3, comment="x")
            for c in rfp_analysis.suggested_criteria_weights
        ],
        verdict="x",
    )
    _enforce_criterion_score_rules(output4, low_priority_input)
    scope4 = next(c for c in output4.criteria if c.name == "Scope & Deliverables Clarity")
    check(
        "hard-constraint cap overrides the 'low' priority nudge (still capped at 2)",
        scope4.score == 2,
    )

    criteria = [
        CriterionScore(name=c.name, score=3, comment="x")
        for c in rfp_analysis.suggested_criteria_weights
    ]
    overall = compute_overall_score(scoring_input, criteria)
    check("equal weights + all score=3 -> overall_score == 3.0", overall == 3.0)

    weighted_input = scoring_input.model_copy(
        update={
            "confirmed_criteria": [
                CriterionWeight(name="Pricing Clarity", description="x", weight=3),
                CriterionWeight(name="Tone & Persuasiveness", description="x", weight=1),
            ]
        }
    )
    weighted_criteria = [
        CriterionScore(name="Pricing Clarity", score=5, comment="x"),
        CriterionScore(name="Tone & Persuasiveness", score=1, comment="x"),
    ]
    weighted_overall = compute_overall_score(weighted_input, weighted_criteria)
    # (5*3 + 1*1) / 4 = 4.0
    check("weighted average math (5*3 + 1*1)/4 == 4.0", weighted_overall == 4.0)

    print("\nAll sanity checks passed — no LLM calls made, no budget spent.")


if __name__ == "__main__":
    main()
