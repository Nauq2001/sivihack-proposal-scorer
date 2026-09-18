# Scoring Agent ↔ Scoring RAG

The benchmark is indexed offline from Markdown response files. The Scoring Agent calls the RAG endpoint once per criterion; RAG returns reference cases only and never produces the final score.

## Endpoint

```http
POST /rag/retrieve
Content-Type: application/json
```

```json
{
  "criterion": {
    "id": "timeline_clarity",
    "name": "Timeline Clarity",
    "description": "Milestones, dependencies and dates are explicit",
    "levels": {"1": "...", "2": "...", "3": "...", "4": "...", "5": "..."}
  },
  "proposal_context": "The relevant section from the new proposal",
  "requirement_context": "The relevant requirement from the new RFP",
  "top_k_per_type": 1,
  "relevance_threshold": 2
}
```

The response contains up to one reference per `weak`, `medium`, `strong`, and `overpromise` type, but only when at least two meaningful query terms overlap by default. Use `text`, `score_range`, and `reasoning` only as calibration context. A query with no sufficiently relevant match returns `{"matches": []}`.

## Agent prompt insertion

Insert the response under `BENCHMARK REFERENCES` and add these rules:

- The final criteria supplied by the RFP Analyst are authoritative.
- Benchmark references explain score levels; they are not evidence for the current documents.
- Cite only exact quotes from the current RFP or proposal.
- If the proposal does not support a requirement, use `missing` or `found: false`.
- Use `contradicted` for an explicit conflict and `unsubstantiated` for an unsupported promise.

## Local run

From `backend/`:

```bash
uvicorn main:app --reload --port 8000
```

The AI team can then call `http://localhost:8000/rag/retrieve`. The current frontend still calls `POST /api/review`; the team’s scoring endpoint should use the RAG endpoint internally before returning that existing response shape.

## Rebuild the index

```bash
py -3 -m backend.rag.ingest <benchmark-root>/cases backend/rag/data/records.jsonl
```

The supplied ZIP has 24 responses and produces 168 records (24 × 7 criteria).
