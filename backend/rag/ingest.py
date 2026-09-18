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


def _sections_for(criterion_id, sections):
    needles = SECTION_BY_CRITERION[criterion_id]
    if not needles:
        return sections
    selected = [(heading, text) for heading, text in sections if any(n in heading.lower() for n in needles)]
    return selected or sections


def chunk_sections(sections, min_words=120, max_words=180, overlap_words=25):
    if not 0 <= overlap_words < max_words:
        raise ValueError("overlap_words must be between 0 and max_words")
    if not 0 < min_words <= max_words:
        raise ValueError("min_words must be between 1 and max_words")
    chunks = []
    step = max_words - overlap_words
    for heading, body in sections:
        words = body.split()
        if len(words) <= max_words:
            chunks.append((heading, f"## {heading}\n{body}"))
            continue
        for start in range(0, len(words), step):
            piece = words[start:start + max_words]
            if not piece:
                break
            chunks.append((heading, f"## {heading}\n{' '.join(piece)}"))
            if start + max_words >= len(words):
                break
    return chunks


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
                parent_id = f"{expected['case_id']}:{response['file']}:{criterion_id}"
                chunks = chunk_sections(_sections_for(criterion_id, sections))
                for chunk_index, (heading, chunk_text) in enumerate(chunks):
                    records.append({
                        "id": f"{parent_id}:chunk:{chunk_index:03d}",
                        "parent_record_id": parent_id,
                        "chunk_index": chunk_index,
                        "sample_type": "overpromise" if response["variant"] == "overpromised" else response["variant"],
                        "criterion_id": criterion_id,
                        "section": heading,
                        "text": chunk_text,
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
