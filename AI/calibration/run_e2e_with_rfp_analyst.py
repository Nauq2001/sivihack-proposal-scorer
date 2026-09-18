"""True two-agent end-to-end test: real RFP Analyst output (agent/) piped
into the real Scoring Agent (AI/). Unlike run_regression.py (which scores
against a hand-authored fixture), this reads the actual ScoringInput JSON
files produced by `rfp-analyst package` in agent/work/ — i.e. it validates
the real wire contract between the two packages, not just AI/'s own logic.

Prerequisite (see agent/README.md), from agent/:
    export GOOGLE_API_KEY=... GEMINI_MODEL=gemini-3.8-flash
    uv run --no-sync rfp-analyst analyze --rfp fixtures/rfp_nordframe.md \
        --output work/live-analysis.json --overwrite
    uv run --no-sync rfp-analyst start-review --analysis work/live-analysis.json \
        --rfp fixtures/rfp_nordframe.md --output work/review.json --overwrite
    uv run --no-sync rfp-analyst package --state work/review.json \
        --proposal <sample proposal path> --output work/scoring-input-<label>.json --overwrite
    (repeat package for each of the 4 sample proposals, one analysis reused for all)

Then, from the repo root:
    python3 -m AI.calibration.run_e2e_with_rfp_analyst
"""

from __future__ import annotations

import json
from pathlib import Path

from AI.contracts import ScoringInput
from AI.scoring import score_proposal

REPO_ROOT = Path(__file__).parent.parent.parent
WORK_DIR = REPO_ROOT / "agent" / "work"

LABELS = ["weak", "medium", "strong", "overpromise"]


def main() -> None:
    results = {}
    for label in LABELS:
        path = WORK_DIR / f"scoring-input-{label}.json"
        scoring_input = ScoringInput.model_validate(json.loads(path.read_text()))
        print(f"\n=== {label} ({path.name}) — "
              f"{len(scoring_input.rfp_analysis.requirements)} requirements from RFP Analyst ===")
        result = score_proposal(scoring_input)
        results[label] = result
        print(f"overall_score: {result.overall_score}")
        for c in result.criteria:
            print(f"  {c.name}: {c.score}/5 — {c.comment}")
        print(f"verdict: {result.verdict}")

    print("\n=== Regression checks (real RFP Analyst + real Scoring Agent) ===")
    ordering_ok = (
        results["weak"].overall_score
        < results["medium"].overall_score
        < results["strong"].overall_score
    )
    print(
        f"[{'PASS' if ordering_ok else 'FAIL'}] weak < medium < strong "
        f"({results['weak'].overall_score} < {results['medium'].overall_score} < "
        f"{results['strong'].overall_score})"
    )

    hard_constraint_findings = [
        f
        for f in results["overpromise"].findings
        if f.status == "contradicted" and f.severity == "high"
    ]
    print(
        f"[{'PASS' if hard_constraint_findings else 'FAIL'}] response_4 has >=1 "
        f"contradicted/high finding — got: {hard_constraint_findings}"
    )


if __name__ == "__main__":
    main()
