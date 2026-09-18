"""Compare collected scorer outputs; never calls a model. Python stdlib only."""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, pstdev

ROOT = Path(__file__).resolve().parent


def schema_errors(value, schema, root, location="$"):
    if "$ref" in schema:
        target = root
        for part in schema["$ref"].split("/")[1:]:
            target = target[part]
        return schema_errors(value, target, root, location)
    errors = []
    tests = {"object": lambda x: isinstance(x, dict), "array": lambda x: isinstance(x, list),
             "string": lambda x: isinstance(x, str), "null": lambda x: x is None,
             "integer": lambda x: isinstance(x, int) and not isinstance(x, bool),
             "number": lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)}
    types = schema.get("type", [])
    types = [types] if isinstance(types, str) else types
    if types and not any(tests[t](value) for t in types):
        return [f"{location}: invalid type"]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{location}: invalid enum")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{location}: missing {key}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            errors += [f"{location}: unknown {key}" for key in value if key not in props]
        for key, sub in props.items():
            if key in value:
                errors += schema_errors(value[key], sub, root, f"{location}.{key}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", float("inf")):
            errors.append(f"{location}: invalid item count")
        if schema.get("uniqueItems") and len({json.dumps(x, sort_keys=True) for x in value}) != len(value):
            errors.append(f"{location}: duplicate items")
        for index, item in enumerate(value):
            errors += schema_errors(item, schema.get("items", {}), root, f"{location}[{index}]")
    if isinstance(value, str) and len(value) < schema.get("minLength", 0):
        errors.append(f"{location}: empty string")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if not schema.get("minimum", float("-inf")) <= value <= schema.get("maximum", float("inf")):
            errors.append(f"{location}: number outside range")
    return errors


def summarize(numbers):
    return {"mean": round(mean(numbers), 4), "min": min(numbers), "max": max(numbers),
            "range": round(max(numbers) - min(numbers), 4), "population_sd": round(pstdev(numbers), 4)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", type=Path)
    parser.add_argument("--output", type=Path, default=Path("comparison_report.json"))
    args = parser.parse_args()
    schema = json.loads((ROOT / "evaluation_output.schema.json").read_text(encoding="utf-8"))
    records = [json.loads(line) for line in (ROOT / "inputs.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    inputs = {(r["case_id"], r["response_id"]): r for r in records}
    expected = {}
    for folder in sorted((ROOT / "cases").iterdir()):
        case = json.loads((folder / "expected.json").read_text(encoding="utf-8"))
        for response in case["responses"]:
            expected[(case["case_id"], Path(response["file"]).stem)] = response
    grouped, invalid, seen = defaultdict(list), [], set()
    line_count = 0
    for line_number, line in enumerate(args.runs.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        line_count += 1
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            invalid.append({"line": line_number, "errors": [str(exc)]})
            continue
        errors = schema_errors(row, schema, schema)
        if not errors:
            key = (row["case_id"], row["response_id"])
            identity = (*key, row["run_id"])
            if key not in inputs:
                errors.append("unknown case/response")
            if identity in seen:
                errors.append("duplicate case/response/run_id")
            if {x["id"] for x in row["requirements"]} != {f"R{i}" for i in range(1, 9)} | {"B1", "T1"}:
                errors.append("requirements must contain every ID exactly once")
            if abs(row["overall_score"] - round(mean(row["scores"].values()), 2)) > 0.005:
                errors.append("overall score is not the rounded arithmetic mean")
        if errors:
            invalid.append({"line": line_number, "errors": errors})
            continue
        seen.add(identity)
        grouped[key].append(row)
    comparisons = []
    for key, source in inputs.items():
        rows = grouped[key]
        if not rows:
            comparisons.append({"case_id": key[0], "response_id": key[1], "run_count": 0, "needs_more_runs": True})
            continue
        target = expected[key]
        quote_errors, null_errors, signals = [], [], []
        for row in rows:
            for item in row["requirements"] + row["findings"]:
                if item["rfp_quote"] not in source["rfp_text"]:
                    quote_errors.append({"run_id": row["run_id"], "document": "rfp", "quote": item["rfp_quote"]})
                quote = item["response_quote"]
                if quote is not None and quote not in source["response_text"]:
                    quote_errors.append({"run_id": row["run_id"], "document": "response", "quote": quote})
                if quote is None and item.get("status") not in {None, "missing"} and item.get("kind") != "missing":
                    null_errors.append({"run_id": row["run_id"], "item": item.get("id", item.get("requirement_ids")), "reason": "non-absence claim without response evidence"})
            critical = [f for f in target["findings"] if f["id"] in target["critical_findings"]]
            matches = []
            for required in critical:
                exact = required["response_quote"]
                if any(f["kind"] == required["kind"] and set(required["requirement_ids"]) <= set(f["requirement_ids"])
                       and exact and f["response_quote"] and (exact in f["response_quote"] or f["response_quote"] in exact)
                       and f["response_quote"] in source["response_text"] for f in row["findings"]):
                    matches.append(required["id"])
            signals.append({"run_id": row["run_id"], "required": target["critical_findings"], "quote_signal_matches": matches,
                            "unmatched": sorted(set(target["critical_findings"]) - set(matches))})
        statuses = {}
        for req_id, truth in target["coverage"].items():
            found = [next(x["status"] for x in row["requirements"] if x["id"] == req_id) for row in rows]
            counts = Counter(found)
            statuses[req_id] = {"counts": dict(counts), "modal_agreement": round(max(counts.values()) / len(rows), 4),
                                "expected_status": truth, "expected_match_rate": round(found.count(truth) / len(rows), 4)}
        score_stats = {criterion: summarize([row["scores"][criterion] for row in rows]) for criterion in rows[0]["scores"]}
        interval_matches = {criterion: round(sum(bounds[0] <= row["scores"][criterion] <= bounds[1] for row in rows) / len(rows), 4)
                            for criterion, bounds in target["score_ranges"].items()}
        comparisons.append({"case_id": key[0], "response_id": key[1], "variant_for_posthoc_comparison_only": target["variant"],
                            "run_count": len(rows), "needs_more_runs": len(rows) < 5, "scores": score_stats,
                            "overall": summarize([row["overall_score"] for row in rows]), "requirements": statuses,
                            "provisional_score_interval_match_rates": interval_matches, "quote_errors": quote_errors,
                            "null_evidence_errors": null_errors, "critical_signal_checks": signals,
                            "recommendations": dict(Counter(row["recommendation"] for row in rows))})
    rankings = []
    for case_id in sorted({key[0] for key in inputs}):
        by_run = defaultdict(dict)
        for key, rows in grouped.items():
            if key[0] == case_id:
                for row in rows:
                    by_run[row["run_id"]][expected[key]["variant"]] = row["overall_score"]
        for run_id, values in sorted(by_run.items()):
            complete = set(values) == {"weak", "medium", "strong", "overpromised"}
            rankings.append({"case_id": case_id, "run_id": run_id, "scores": values, "complete": complete,
                             "strong_strictly_first": values["strong"] > max(v for k, v in values.items() if k != "strong") if complete else None})
    report = {"notice": "No scorer was run. Quote-signal matches are heuristic, not semantic proof of critical-finding recall; review findings manually.",
              "input_lines": line_count, "valid_runs": sum(map(len, grouped.values())), "invalid_outputs": invalid,
              "pairs_expected": len(inputs), "pairs_with_five_or_more_runs": sum(len(grouped[k]) >= 5 for k in inputs),
              "comparisons": comparisons, "rankings": rankings}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(args.output.resolve()), "valid_runs": report["valid_runs"], "invalid_outputs": len(invalid),
                      "pairs_with_five_or_more_runs": report["pairs_with_five_or_more_runs"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
