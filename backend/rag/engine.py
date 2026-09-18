"""Small, dependency-free retrieval layer for scoring examples."""

import json
import re
import unicodedata
from pathlib import Path

import numpy as np

BASE_CRITERIA = frozenset((
    'problem_understanding', 'scope_deliverables_clarity', 'pricing_clarity',
    'timeline_clarity', 'completeness_vs_rfp', 'tone_persuasiveness',
    'risk_assumptions_transparency',
))
RAG_CRITERIA = frozenset((
    'pricing_clarity', 'timeline_clarity', 'tone_persuasiveness',
    'risk_assumptions_transparency',
))
ALIASES = dict(zip(('pu', 'scope', 'price', 'time', 'comp', 'tone', 'risk'), (
    'problem_understanding', 'scope_deliverables_clarity', 'pricing_clarity',
    'timeline_clarity', 'completeness_vs_rfp', 'tone_persuasiveness',
    'risk_assumptions_transparency',
)))
DEFAULT_INDEX = Path(__file__).parent / 'data' / 'records.jsonl'


def canonical_id(criterion_id):
    return ALIASES.get(criterion_id, criterion_id)


_WORD_RE = re.compile(r"[\w€]+", re.UNICODE)
_STOP = {"the", "and", "for", "with", "from", "that", "this", "are", "will", "proposal", "rfp"}


def _tokens(text):
    text = unicodedata.normalize("NFKC", text or "").lower()
    return {w for w in _WORD_RE.findall(text) if len(w) > 2 and w not in _STOP}


def hybrid_score(keyword_score, cosine_similarity):
    semantic_score = float(np.clip((cosine_similarity + 1.0) / 2.0, 0.0, 1.0))
    return 0.35 * keyword_score + 0.65 * semantic_score


def _reasoning(record):
    reasoning = record.get('reasoning', '')
    if reasoning and not reasoning.startswith('Reference case from the benchmark;'):
        return reasoning
    example = ' '.join(record.get('text', '').split())
    excerpt = example[:180].rstrip() + ('...' if len(example) > 180 else '')
    return (f"This {record.get('sample_type', 'benchmark')} example for "
            f"{record.get('criterion_id', 'the criterion')} illustrates evidence in: {excerpt}")


class BenchmarkStore:
    def __init__(self, records, vectors=None, embedder=None):
        self.records = list(records)
        self.vectors = None if vectors is None else np.asarray(vectors, dtype=np.float32)
        self.embedder = embedder
        if self.vectors is not None and (
            self.vectors.ndim != 2 or self.vectors.shape[0] != len(self.records)
        ):
            raise ValueError('vectors must contain one row per record')
        if (self.vectors is None) != (self.embedder is None):
            raise ValueError('vectors and embedder must be provided together')

    @classmethod
    def from_file(cls, path=DEFAULT_INDEX, vectors=None, embedder=None):
        with open(path, encoding="utf-8") as fh:
            return cls([json.loads(line) for line in fh if line.strip()], vectors, embedder)

    def retrieve(self, criterion_id, query, top_k_per_type=1, min_overlap=2,
                 *, min_hybrid_score=None):
        if not isinstance(criterion_id, str) or not criterion_id.strip():
            raise ValueError('criterion.id must be a non-empty string')
        if not isinstance(query, str):
            raise ValueError('query must be a string')
        if type(top_k_per_type) is not int or not 1 <= top_k_per_type <= 3:
            raise ValueError('top_k_per_type must be an integer between 1 and 3')
        if type(min_overlap) is not int or not 1 <= min_overlap <= 100:
            raise ValueError('relevance_threshold must be an integer between 1 and 100')
        if min_hybrid_score is not None and (
            isinstance(min_hybrid_score, bool)
            or not isinstance(min_hybrid_score, (int, float))
            or not 0 <= min_hybrid_score <= 1
        ):
            raise ValueError('min_hybrid_score must be a number between 0 and 1')
        criterion_id = canonical_id(criterion_id.strip())
        custom = criterion_id not in BASE_CRITERIA
        candidates = [
            (index, record) for index, record in enumerate(self.records)
            if custom or record.get('criterion_id') == criterion_id
        ]
        wanted = _tokens(query)
        if not wanted:
            return []
        query_vector = None
        if self.vectors is not None:
            query_vectors = np.asarray(self.embedder.encode([query]), dtype=np.float32)
            if query_vectors.ndim != 2 or query_vectors.shape != (1, self.vectors.shape[1]):
                raise ValueError('embedder returned an invalid query vector')
            query_vector = query_vectors[0]
            if min_hybrid_score is None:
                min_hybrid_score = 0.45
        ranked = []
        for index, record in candidates:
            terms = _tokens(record.get('text', ''))
            overlap = len(wanted & terms)
            if query_vector is None:
                ranked.append((overlap, 0.0, index, record))
                continue
            keyword_score = overlap / len(wanted)
            cosine_similarity = float(self.vectors[index] @ query_vector)
            semantic_score = float(np.clip((cosine_similarity + 1.0) / 2.0, 0.0, 1.0))
            combined_score = hybrid_score(keyword_score, cosine_similarity)
            ranked.append((combined_score, semantic_score, index, record))

        result = []
        for sample_type in ("weak", "medium", "strong", "overpromise"):
            group = sorted(
                (item for item in ranked if item[3].get("sample_type") == sample_type),
                key=lambda item: (-item[0], -item[1], item[2]),
            )
            seen = set()
            for score, semantic_score, _, record in group:
                if query_vector is None and score < min_overlap:
                    continue
                if query_vector is not None and score < min_hybrid_score:
                    continue
                source = record.get('source_file', record.get('id'))
                if source in seen:
                    continue
                seen.add(source)
                result.append({**record, 'score_range': None if custom else record.get('score_range'),
                               'reasoning': _reasoning(record),
                               'overlap': len(wanted & _tokens(record['text'])),
                               'matched_terms': sorted(wanted & _tokens(record['text'])),
                               'keyword_score': len(wanted & _tokens(record['text'])) / len(wanted),
                               'semantic_score': semantic_score if query_vector is not None else None,
                               'hybrid_score': score if query_vector is not None else None,
                               'annotation_provenance': 'synthetic_benchmark',
                               'usage': 'calibration_only'})
                if len(seen) == top_k_per_type:
                    break
        return result
