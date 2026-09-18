"""Small, dependency-free retrieval layer for scoring examples."""

import json
import re
import unicodedata
from pathlib import Path

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


def _reasoning(record):
    reasoning = record.get('reasoning', '')
    if reasoning and not reasoning.startswith('Reference case from the benchmark;'):
        return reasoning
    example = ' '.join(record.get('text', '').split())
    excerpt = example[:180].rstrip() + ('...' if len(example) > 180 else '')
    return (f"This {record.get('sample_type', 'benchmark')} example for "
            f"{record.get('criterion_id', 'the criterion')} illustrates evidence in: {excerpt}")


class BenchmarkStore:
    def __init__(self, records):
        self.records = list(records)

    @classmethod
    def from_file(cls, path=DEFAULT_INDEX):
        with open(path, encoding="utf-8") as fh:
            return cls([json.loads(line) for line in fh if line.strip()])

    def retrieve(self, criterion_id, query, top_k_per_type=1, min_overlap=2):
        if not isinstance(criterion_id, str) or not criterion_id.strip():
            raise ValueError('criterion.id must be a non-empty string')
        if not isinstance(query, str):
            raise ValueError('query must be a string')
        if type(top_k_per_type) is not int or not 1 <= top_k_per_type <= 3:
            raise ValueError('top_k_per_type must be an integer between 1 and 3')
        if type(min_overlap) is not int or not 1 <= min_overlap <= 100:
            raise ValueError('relevance_threshold must be an integer between 1 and 100')
        criterion_id = canonical_id(criterion_id.strip())
        custom = criterion_id not in BASE_CRITERIA
        candidates = [r for r in self.records if custom or r.get('criterion_id') == criterion_id]
        wanted = _tokens(query)
        ranked = []
        for record in candidates:
            terms = _tokens(record.get('text', ''))
            overlap = len(wanted & terms)
            ranked.append((overlap, record))

        result = []
        for sample_type in ("weak", "medium", "strong", "overpromise"):
            group = sorted(
                (item for item in ranked if item[1].get("sample_type") == sample_type),
                key=lambda item: item[0],
                reverse=True,
            )
            seen = set()
            for overlap, record in group:
                if overlap < min_overlap:
                    continue
                source = record.get('source_file', record.get('id'))
                if source in seen:
                    continue
                seen.add(source)
                result.append({**record, 'score_range': None if custom else record.get('score_range'),
                               'reasoning': _reasoning(record),
                               'overlap': overlap, 'matched_terms': sorted(wanted & _tokens(record['text'])),
                               'annotation_provenance': 'synthetic_benchmark',
                               'usage': 'calibration_only'})
                if len(seen) == top_k_per_type:
                    break
        return result
