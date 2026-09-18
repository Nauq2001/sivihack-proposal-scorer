"""Generate one consistently-named scoring_<label>.md report per calibration
sample, using the real RFP Analyst output already packaged in agent/work/
(see run_e2e_with_rfp_analyst.py's docstring for the prerequisite steps).

    python3 -m AI.calibration.generate_reports
"""

from __future__ import annotations

import json
from pathlib import Path

from AI.contracts import ScoringInput
from AI.report import render_markdown
from AI.scoring import score_proposal

REPO_ROOT = Path(__file__).parent.parent.parent
WORK_DIR = REPO_ROOT / "agent" / "work"
OUTPUT_DIR = Path(__file__).parent / "output"

LABELS = ["weak", "medium", "strong", "overpromise"]


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    for label in LABELS:
        input_path = WORK_DIR / f"scoring-input-{label}.json"
        scoring_input = ScoringInput.model_validate(json.loads(input_path.read_text()))
        result = score_proposal(scoring_input)
        markdown = render_markdown(scoring_input, result)
        output_path = OUTPUT_DIR / f"scoring_{label}.md"
        output_path.write_text(markdown + "\n")
        print(f"{label}: overall_score={result.overall_score} -> {output_path}")


if __name__ == "__main__":
    main()
