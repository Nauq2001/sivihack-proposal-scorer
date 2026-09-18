"""
Offline check of the corpus and the retrieval, run with:

    cd backend && python -m rag.selftest

No network, no model, no API key. It prints the admission report, the demo
queries from the corpus README, and the commitment checks against a draft that
overpromises, so a failure is visible before anyone opens the app.
"""

from __future__ import annotations

import json

from .evidence import benchmark_section, check_commitments
from .retrieve import search
from .store import load_corpus

OVERPROMISING_DRAFT = """
## Support
We provide 24/7 support with a dedicated on-call engineer, including weekends
and public holidays. Any critical incident is resolved within 4 hours.

## Pricing
Our blended team rate is €480 per day, well below the market.
"""


def main() -> int:
    corpus = load_corpus()
    report = corpus.report()
    print("=== Admission report ===")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    failures: list[str] = []
    if report["admitted_records"] != 6:
        failures.append(f"expected 6 admitted records, got {report['admitted_records']}")
    if len(report["roles"]["gold_reference"]) != 3:
        failures.append(f"expected 3 gold references, got {report['roles']['gold_reference']}")
    if report["roles"]["anti_pattern"] != ["proposal_06"]:
        failures.append(f"unexpected anti-patterns: {report['roles']['anti_pattern']}")

    print("\n=== Production mode (fixture scores must be refused) ===")
    prod = load_corpus(production=True).report()
    print(f"admitted={prod['admitted_records']} rejected={len(prod['rejected_records'])}")
    if prod["admitted_records"] != 0:
        failures.append("production mode admitted a mock-scored record")

    print("\n=== Demo query: pricing sections of won, well-written proposals ===")
    bench = benchmark_section(corpus, "pricing", country="DE",
                              service_type="Custom software implementation")
    for hit in bench["gold_references"]:
        p = hit["provenance"]
        print(f"- {hit['record_id']} ({p['outcome']}, {p['quality_score']}, {p['industry']})")
        print(f"  {hit['text'][:110].replace(chr(10), ' ')}...")
    print(f"matched documents: {bench['matched_documents']}")
    print(f"approved clauses available: {[c['record_id'] for c in bench['approved_clauses']]}")
    if not bench["gold_references"]:
        failures.append("no gold pricing references returned")

    print("\n=== Free search: rollout and pilot ===")
    for hit in search(corpus, "pilot rollout parallel run before cutover", limit=3):
        print(f"- {hit.chunk['record_id']} [{hit.chunk['section_role']}] score={hit.score:.2f} ({hit.role})")

    print("\n=== Commitment checks against an overpromising draft ===")
    result = check_commitments(corpus, OVERPROMISING_DRAFT)
    for f in result["findings"]:
        print(f"- [{f['severity']}] {f['rule']}")
        print(f"  quote: {f['quote']}")
        print(f"  {f['message']}")
        print(f"  source: {f['standard']['record_id']}.{f['standard']['field']}")
    rules = {f["rule"] for f in result["findings"]}
    for expected in ("coverage_beyond_capability", "restoration_guarantee", "day_rate_below_floor"):
        if expected not in rules:
            failures.append(f"missed expected finding: {expected}")

    print("\n=== Every quote must appear verbatim in the draft ===")
    for f in result["findings"]:
        if f["quote"] not in OVERPROMISING_DRAFT:
            failures.append(f"quote not found verbatim: {f['quote'][:50]}")
    print("ok" if not failures else "FAILURES")

    if failures:
        print("\n".join(f"FAIL: {f}" for f in failures))
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
