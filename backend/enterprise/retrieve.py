"""
Retrieval over the enterprise corpus.

Metadata filter first, text ranking second. With a corpus this size (tens of
chunks) BM25 over the filtered set is enough, it needs no service to run and it
gives the same answer every time — which matters when a reviewer is checking
what the tool told them. Embeddings become worth their weight somewhere in the
low thousands of chunks; the function signature below does not have to change
when that day comes.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any

from .store import Corpus, iter_chunks

K1 = 1.5
B = 0.75
_WORD = re.compile(r"[a-z0-9€%]+")

# Words that appear in every proposal and only add noise to the ranking.
STOP = {
    "the", "a", "an", "and", "or", "of", "to", "for", "in", "on", "with", "by",
    "is", "are", "be", "will", "we", "our", "your", "you", "that", "this", "as",
    "at", "it", "from", "per", "all", "each", "not", "no", "within",
}


def tokenize(text: str) -> list[str]:
    return [w for w in _WORD.findall(text.lower()) if w not in STOP and len(w) > 1]


@dataclass
class Hit:
    chunk: dict[str, Any]
    score: float
    role: str

    def to_dict(self) -> dict[str, Any]:
        c = self.chunk
        return {
            "chunk_id": c["chunk_id"],
            "record_id": c["record_id"],
            "section_role": c["section_role"],
            "section_path": c.get("section_path", []),
            "text": c["text"],
            "score": round(self.score, 3),
            "provenance": {
                "role": self.role,
                "outcome": c["outcome"],
                "quality_score": c["quality_score"],
                "quality_method": c.get("quality_provenance_method"),
                "industry": c["industry"],
                "country": c["country"],
                "service_type": c["service_type"],
                "fictional": c.get("fictional", False),
            },
        }


def search(corpus: Corpus, query: str, *, limit: int = 5, **filters: Any) -> list[Hit]:
    """Rank the chunks that survive the metadata filter against `query`."""
    pool = list(iter_chunks(corpus, **filters))
    if not pool:
        return []

    docs = [tokenize(c["text"]) for c in pool]
    lengths = [len(d) for d in docs]
    avg_len = sum(lengths) / len(lengths) or 1.0

    df: Counter[str] = Counter()
    for doc in docs:
        df.update(set(doc))

    terms = tokenize(query)
    n = len(pool)
    scored: list[Hit] = []
    for chunk, doc, length in zip(pool, docs, lengths):
        counts = Counter(doc)
        score = 0.0
        for term in terms:
            tf = counts.get(term, 0)
            if not tf:
                continue
            idf = math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
            score += idf * (tf * (K1 + 1)) / (tf + K1 * (1 - B + B * length / avg_len))
        if score > 0:
            scored.append(Hit(chunk=chunk, score=score, role=corpus.records[chunk["record_id"]].role))

    scored.sort(key=lambda h: (-h.score, h.chunk["chunk_id"]))
    return scored[:limit]


def gold_references(corpus: Corpus, section_role: str, *, query: str = "", limit: int = 3,
                    **filters: Any) -> list[Hit]:
    """Passages from proposals that both won and were written well.

    A won-but-weak proposal is deliberately excluded: it won on price or
    relationship, and holding its wording up as a model would teach the wrong
    lesson.
    """
    filters = {**filters, "section_role": section_role, "role": "gold_reference", "cross_deal_only": True}
    if query:
        return search(corpus, query, limit=limit, **filters)
    hits = [
        Hit(chunk=c, score=float(c["quality_score"]), role="gold_reference")
        for c in iter_chunks(corpus, **filters)
    ]
    hits.sort(key=lambda h: (-h.score, h.chunk["chunk_id"]))
    return hits[:limit]


def anti_patterns(corpus: Corpus, section_role: str, *, limit: int = 3) -> list[Hit]:
    """Passages from proposals that lost and were written poorly."""
    hits = [
        Hit(chunk=c, score=float(c["quality_score"]), role="anti_pattern")
        for c in iter_chunks(corpus, section_role=section_role, role="anti_pattern")
    ]
    hits.sort(key=lambda h: (h.score, h.chunk["chunk_id"]))
    return hits[:limit]
