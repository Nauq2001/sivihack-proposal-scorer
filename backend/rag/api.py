from .engine import BASE_CRITERIA, BenchmarkStore, canonical_id


def retrieve_payload(store, payload):
    if not isinstance(payload, dict) or not isinstance(payload.get('criterion'), dict):
        raise ValueError('criterion must be an object')
    criterion = payload['criterion']
    criterion_id = criterion.get("id")
    if not isinstance(criterion_id, str) or not criterion_id.strip():
        raise ValueError('criterion.id must be a non-empty string')
    criterion_id = criterion_id.strip()
    parts = [criterion.get(key, '') for key in ('name', 'description', 'evaluation_question')]
    parts += [payload.get(key, '') for key in ('proposal_context', 'requirement_context')]
    if any(not isinstance(part, str) for part in parts):
        raise ValueError('criterion text and document contexts must be strings')
    if sum(map(len, parts)) > 100_000:
        raise ValueError('retrieval context exceeds 100000 characters; send relevant sections')
    query = ' '.join(parts)
    return {'criterion_id': criterion_id,
            'retrieval_mode': 'base' if canonical_id(criterion_id) in BASE_CRITERIA else 'custom',
            'matches': store.retrieve(
        criterion_id,
        query,
        payload.get("top_k_per_type", 1),
        payload.get("relevance_threshold", 2),
    )}


def load_store(path=None):
    return BenchmarkStore.from_file() if path is None else BenchmarkStore.from_file(path)
