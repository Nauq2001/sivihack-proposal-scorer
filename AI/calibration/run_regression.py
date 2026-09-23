"""The real regression check docs/architecture.md requires before every hand-off: run all
4 sample proposals through score_proposal() against the one RFP.

Needs a real key in backend/.env (GEMINI_API_KEY, or ANTHROPIC_API_KEY with
AI_PROVIDER=anthropic) — this makes real LLM calls and spends budget. Run
deliberately, not in a loop. From the repo root:

    python3 -m AI.calibration.run_regression
"""

from __future__ import annotations

import json
from pathlib import Path

from AI.contracts import RFPAnalysis, ScoringInput
from AI.scoring import score_proposal

REPO_ROOT = Path(__file__).parent.parent.parent
SAMPLE_DIR = REPO_ROOT / "docs" / "challenge" / "sample_data"
FIXTURE_PATH = Path(__file__).parent / "fixtures" / "nordframe_rfp_analysis.json"

RESPONSES = [
    ("weak", "response_1_weak.md"),
    ("medium", "response_2_medium.md"),
    ("strong", "response_3_strong.md"),
    ("overpromise", "response_4_overpromise.md"),
]


def main() -> None:
    rfp_analysis = RFPAnalysis.model_validate(json.loads(FIXTURE_PATH.read_text()))
    raw_rfp_text = (SAMPLE_DIR / "rfp_nordframe.md").read_text()
    # Default regression set: the 7 base criteria only (no custom criterion),
    # matching docs/architecture.md's stated default.
    confirmed_criteria = [c for c in rfp_analysis.suggested_criteria_weights]

    results = {}
    for label, filename in RESPONSES:
        raw_proposal_text = (SAMPLE_DIR / filename).read_text()
        scoring_input = ScoringInput(
            rfp_analysis=rfp_analysis,
            raw_rfp_text=raw_rfp_text,
            raw_proposal_text=raw_proposal_text,
            confirmed_criteria=confirmed_criteria,
        )
        print(f"\n=== {label} ({filename}) ===")
        result = score_proposal(scoring_input)
        results[label] = result
        print(f"overall_score: {result.overall_score}")
        for c in result.criteria:
            print(f"  {c.name}: {c.score}/5 — {c.comment}")
        print(f"verdict: {result.verdict}")

    print("\n=== Regression checks ===")
    ordering_ok = results["weak"].overall_score < results["medium"].overall_score < results["strong"].overall_score
    print(f"[{'PASS' if ordering_ok else 'FAIL'}] weak < medium < strong "
          f"({results['weak'].overall_score} < {results['medium'].overall_score} < {results['strong'].overall_score})")

    req007 = next(
        (f for f in results["overpromise"].findings if f.requirement_id == "REQ-007"), None
    )
    contradiction_ok = bool(req007) and req007.status == "contradicted" and req007.severity == "high"
    print(f"[{'PASS' if contradiction_ok else 'FAIL'}] response_4 REQ-007 (no-migration) "
          f"surfaces as contradicted/high — got: {req007}")


if __name__ == "__main__":
    main()
