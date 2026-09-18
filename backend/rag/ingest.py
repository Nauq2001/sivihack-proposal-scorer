"""Build criterion-level records from the supplied benchmark package."""

import argparse
import json
import re
from pathlib import Path


SECTION_BY_CRITERION = {
    "problem_understanding": ("understanding", "background", "approach"),
    "scope_deliverables_clarity": ("scope", "delivery", "solution", "deliverables"),
    "pricing_clarity": ("price", "pricing", "commercial", "cost"),
    "timeline_clarity": ("timeline", "schedule", "milestone", "delivery"),
    "completeness_vs_rfp": (),
    "tone_persuasiveness": (),
    "risk_assumptions_transparency": ("risk", "assumption", "dependency"),
}


def _sections(markdown):
    chunks = []
    current = "Document"
    body = []
    for line in markdown.splitlines():
        match = re.match(r"^#{1,3}\s+(.+?)\s*$", line)
        if match:
            if body:
                chunks.append((current, "\n".join(body).strip()))
            current, body = match.group(1), []
        else:
            body.append(line)
    if body:
        chunks.append((current, "\n".join(body).strip()))
    return [(heading, text) for heading, text in chunks if text]


def _text_for(criterion_id, sections):
    needles = SECTION_BY_CRITERION[criterion_id]
    if not needles:
        return "\n\n".join(f"## {heading}\n{text}" for heading, text in sections)
    selected = [(heading, text) for heading, text in sections if any(n in heading.lower() for n in needles)]
    return "\n\n".join(f"## {heading}\n{text}" for heading, text in selected) or _text_for("completeness_vs_rfp", sections)


def build_records(root):
    root = Path(root)
    records = []
    for case_dir in sorted((root / "cases").iterdir()):
        if not case_dir.is_dir():
            continue
        expected = json.loads((case_dir / "expected.json").read_text(encoding="utf-8"))
        for response in expected["responses"]:
            response_path = case_dir / response["file"]
            text = response_path.read_text(encoding="utf-8")
            sections = _sections(text)
            for criterion_id, score_range in response["score_ranges"].items():
                records.append({
                    "id": f"{expected['case_id']}:{response['file']}:{criterion_id}",
                    "sample_type": "overpromise" if response["variant"] == "overpromised" else response["variant"],
                    "criterion_id": criterion_id,
                    "section": ", ".join(h for h, _ in sections),
                    "text": _text_for(criterion_id, sections),
                    "score_range": score_range,
                    "reasoning": "Reference case from the benchmark; compare evidence, do not copy its score.",
                    "source_file": str(response_path.relative_to(root)).replace("\\", "/"),
                })
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    records = build_records(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"wrote {len(records)} records to {args.output}")


if __name__ == "__main__":
    main()
