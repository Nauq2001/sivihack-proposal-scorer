"""Small, dependency-free retrieval layer for scoring examples."""

from collections import Counter
import json
import re
import unicodedata


_WORD_RE = re.compile(r"[\w€]+", re.UNICODE)
_STOP = {"the", "and", "for", "with", "from", "that", "this", "are", "will", "proposal", "rfp"}


def _tokens(text):
    text = unicodedata.normalize("NFKC", text or "").lower()
    return {w for w in _WORD_RE.findall(text) if len(w) > 2 and w not in _STOP}


class BenchmarkStore:
    def __init__(self, records):
        self.records = records

    @classmethod
    def from_file(cls, path):
        with open(path, encoding="utf-8") as fh:
            return cls([json.loads(line) for line in fh if line.strip()])

    def retrieve(self, criterion_id, query, top_k_per_type=1):
        candidates = [r for r in self.records if r.get("criterion_id") == criterion_id]
        wanted = _tokens(query)
        ranked = []
        for record in candidates:
            terms = _tokens(" ".join(str(record.get(k, "")) for k in ("text", "reasoning", "section")))
            overlap = len(wanted & terms)
            ranked.append((overlap, record))

        result = []
        for sample_type in ("weak", "medium", "strong", "overpromise"):
            group = sorted(
                (item for item in ranked if item[1].get("sample_type") == sample_type),
                key=lambda item: item[0],
                reverse=True,
            )
            result.extend(record for _, record in group[:max(0, top_k_per_type)])
        return result
