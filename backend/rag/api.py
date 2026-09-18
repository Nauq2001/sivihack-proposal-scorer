from .engine import BenchmarkStore


def retrieve_payload(store, payload):
    criterion = payload.get("criterion") or {}
    criterion_id = criterion.get("id")
    query = " ".join(
        str(payload.get(key, "")) for key in ("proposal_context", "requirement_context")
    )
    if not criterion_id or not query.strip():
        raise ValueError("criterion.id, proposal_context and requirement_context are required")
    return {"matches": store.retrieve(criterion_id, query, int(payload.get("top_k_per_type", 1)))}


def load_store(path):
    return BenchmarkStore.from_file(path)
