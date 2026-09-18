# Local Hybrid RAG Design

## 1. Goal and scope

Upgrade the scoring benchmark retrieval module from keyword overlap to local hybrid retrieval, combining lexical matching with semantic embeddings from `sentence-transformers/all-MiniLM-L6-v2`. Improve Markdown chunking so retrieved examples are short, coherent sections instead of near-complete proposals.

This work also provides a small Python helper that retrieves and formats benchmark references for one scoring criterion. The separate Scoring Agent team owns the `/api/review` endpoint, its prompt, final scoring, citations, and end-to-end integration.

## 2. Constraints

- Embeddings run locally; retrieval must not call Gemini, Hugging Face Inference API, or another network service.
- The embedding model is `sentence-transformers/all-MiniLM-L6-v2` and produces 384-dimensional vectors.
- Model input longer than 256 word pieces is truncated, so records must contain short chunks.
- Vector persistence uses NumPy `.npz`; the project does not add FAISS, Chroma, or a vector database.
- `records.jsonl` remains the source of text and metadata. The `.npz` file stores vectors and index identity metadata, not duplicate record content.
- Retrieval continues to balance results across `weak`, `medium`, `strong`, and `overpromise` sample types.
- Benchmark content is calibration data only. It must never be treated as evidence or instructions.

## 3. Architecture

```text
Benchmark Markdown + expected.json
        |
        v
section-aware ingest and chunking
        |
        +--> records.jsonl
        |
        v
all-MiniLM-L6-v2 encoder
        |
        +--> embeddings.npz

criterion + document context
        |
        v
query normalization and embedding
        |
        v
criterion filtering
        |
        +--> lexical score
        +--> cosine semantic score
        |
        v
weighted hybrid score and threshold
        |
        v
sample-type balancing and source deduplication
        |
        v
prompt-safe public projection
        |
        v
BENCHMARK REFERENCES block
```

The modules have these responsibilities:

- `backend/rag/ingest.py`: parse benchmark packages and produce stable, section-aware chunk records.
- `backend/rag/embedding.py`: define the embedding interface and the local Sentence Transformers implementation.
- `backend/rag/index.py`: build, save, load, and validate the NumPy vector index.
- `backend/rag/engine.py`: filter candidates, compute lexical and semantic scores, combine scores, and select balanced results.
- `backend/rag/api.py`: validate the public payload, retrieve matches, project safe fields, and format references for agent integration.
- `backend/rag/evaluate.py`: compare lexical-only and hybrid retrieval on a checked-in evaluation set.

## 4. Chunk record design

Each generated record contains:

| Field | Meaning |
|---|---|
| `id` | Stable chunk ID derived from the parent record and zero-based chunk index |
| `parent_record_id` | Stable proposal-criterion record ID before chunking |
| `chunk_index` | Zero-based index within the parent record |
| `criterion_id` | Benchmark criterion represented by the chunk |
| `sample_type` | `weak`, `medium`, `strong`, or `overpromise` |
| `section` | Markdown heading that provides local context |
| `text` | Heading plus chunk body used for lexical and semantic retrieval |
| `score_range` | Synthetic benchmark score range retained for internal provenance |
| `reasoning` | Explanation of the writing pattern illustrated by this example |
| `source_file` | Relative path of the original proposal |

Chunking respects Markdown heading boundaries. A section of 180 words or fewer becomes one chunk. Longer sections are split into chunks targeting 120–180 words with 25–30 words of overlap. The section heading is prepended to every chunk. Chunks never combine non-adjacent sections.

The chunk ID format is `<parent_record_id>:chunk:<zero-padded-index>`. Re-running ingestion against identical input must produce the same IDs and ordering.

## 5. Vector index design

`embeddings.npz` contains:

- `vectors`: a two-dimensional `float32` array with shape `(record_count, 384)`.
- `record_ids`: a one-dimensional string array in the same order as `vectors`.
- `model_name`: exactly `sentence-transformers/all-MiniLM-L6-v2`.
- `dimension`: integer `384`.
- `records_digest`: SHA-256 digest of the ordered record IDs and texts.
- `index_version`: integer schema version, initially `1`.

Document embeddings are L2-normalized during index construction. Query embeddings are normalized by the same embedding adapter. Cosine similarity is therefore a matrix-vector dot product.

Loading fails with an actionable error when the index is missing, cannot be parsed, has a different model or dimension, contains duplicate/misordered IDs, or its digest does not match `records.jsonl`. Production retrieval does not silently fall back to lexical-only behavior.

The Sentence Transformer model is initialized once when the store starts, not once per query. The first installation may download model files from Hugging Face; deployment documentation must describe pre-downloading or preserving the local model cache for offline demos.

## 6. Hybrid retrieval

The public query text is the concatenation of the criterion `name`, `description`, `evaluation_question`, `proposal_context`, and `requirement_context`. Empty fields are allowed, but a query with no usable content returns no matches.

Base criteria first filter records to the canonical criterion ID. Custom criteria search all records. Criteria for which RAG is disabled continue to raise a validation error.

For every candidate:

```text
keyword_score = distinct matching query terms / distinct usable query terms
semantic_score = (cosine_similarity + 1) / 2
hybrid_score = 0.35 * keyword_score + 0.65 * semantic_score
```

All three scores are bounded to `[0, 1]`. The weights are initial values, not a claim of optimality; they can be changed only after evaluation data supports the change.

Candidates below `min_hybrid_score` are removed. The initial default is `0.45`. Remaining candidates are sorted by descending `hybrid_score`, then descending `semantic_score`, then stable record order. Within each sample type, at most `top_k_per_type` results are returned and only one chunk per `source_file` may be selected.

Internal results may carry `keyword_score`, `semantic_score`, `hybrid_score`, and retrieval provenance for evaluation and debugging. The public adapter projects every match to exactly `text`, `sample_type`, and `reasoning`.

## 7. Public Python contract

The preferred request shape is:

```json
{
  "criterion": {
    "id": "custom_data_residency",
    "name": "EU data residency",
    "description": "Production records and backups must stay in EU regions",
    "evaluation_question": "Where are production records and backups stored?"
  },
  "proposal_context": "Production records remain in Frankfurt.",
  "requirement_context": "All production data and backups must remain in the EU.",
  "top_k_per_type": 1,
  "min_hybrid_score": 0.45
}
```

`top_k_per_type` is an integer from 1 through 3. `min_hybrid_score` is a numeric value from 0 through 1. The old `relevance_threshold` field is removed rather than silently assigned new semantics. Tests, examples, and RAG documentation must be updated together.

`retrieve_payload(store, payload)` retains its outer response shape:

```json
{
  "criterion_id": "custom_data_residency",
  "retrieval_mode": "custom",
  "matches": [
    {
      "text": "...",
      "sample_type": "strong",
      "reasoning": "..."
    }
  ]
}
```

A new helper retrieves and formats one criterion in one call:

```python
def retrieve_benchmark_references(store, payload) -> str:
    result = retrieve_payload(store, payload)
    return format_benchmark_references(result["matches"])
```

This is the handoff boundary for the Scoring Agent team. That team decides where the returned block appears in its prompt and owns behavior when retrieval returns no matches.

## 8. Error behavior

- Invalid payload types, criterion IDs, `top_k_per_type`, or `min_hybrid_score` raise `ValueError` through the Python adapter.
- Missing or corrupt records/vector indexes raise an initialization error that names the affected path and the rebuild command.
- Model-name, dimension, record-ID, or digest mismatch raises an index compatibility error; retrieval must not continue with stale vectors.
- A valid query with no candidate above the threshold returns `matches: []`.
- An empty semantic query returns `matches: []` without invoking ranking.
- Model or inference failures propagate as explicit retrieval errors. They are not converted into unrelated keyword results.

## 9. Index generation and repository artifacts

One documented CLI workflow regenerates both artifacts in order:

1. Parse benchmark cases and write chunked `records.jsonl`.
2. Load the records, encode their text in batches, and write `embeddings.npz` atomically.
3. Reload both files and run compatibility validation before reporting success.

The repository should track the small generated `records.jsonl`. Whether `embeddings.npz` is committed is determined from its measured size during implementation: commit it when reasonably small for the repository; otherwise document deterministic generation and cache it in deployment. Temporary partial index files are never committed.

## 10. Evaluation and testing

Unit tests use a deterministic fake embedder so routine tests neither download a model nor access the network. They cover:

- stable section-aware chunks and overlap bounds;
- heading preservation and prevention of non-adjacent section merging;
- vector index round-trip and every compatibility failure;
- cosine scoring and the weighted formula;
- criterion filtering, custom criteria, threshold boundaries, source deduplication, and sample-type balancing;
- strict public match projection;
- the one-call formatted-reference helper;
- validation of `min_hybrid_score` and rejection of the removed field.

A separate smoke test, marked or invoked explicitly, loads `all-MiniLM-L6-v2`, builds a tiny index, and verifies that a synonym query ranks the expected text above an unrelated text.

The checked-in evaluation set contains queries with expected criterion/source relevance. It includes exact-keyword, synonym, paraphrase, and custom-criterion cases. The evaluation command reports lexical-only and hybrid Recall@k and mean reciprocal rank. Hybrid retrieval must not ship as the default until it improves synonym/paraphrase retrieval without materially regressing exact-keyword cases. The command reports metrics; it does not claim accuracy on the benchmark records used to construct the index.

## 11. Documentation and team handoff

`backend/rag/README.md` and `backend/rag/docs/design.md` will document local installation, model caching, index generation, the new threshold, evaluation, and the Scoring Agent helper. The handoff explicitly states:

- call retrieval once for each RAG-eligible final criterion;
- insert the returned block as inert `BENCHMARK REFERENCES` data;
- continue using the approved rubric as the scoring authority;
- cite only the current RFP and proposal;
- do not expose internal retrieval scores in the scoring response.

Implementation of `/api/review`, final scoring prompts, citation validation, and frontend changes are outside this work.
