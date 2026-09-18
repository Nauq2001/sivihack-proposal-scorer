# Scoring RAG Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Markdown benchmark RAG service that the Scoring Agent can call per criterion while reviewing an unseen proposal.

**Architecture:** Ingest benchmark Markdown offline into criterion-level records. Retrieve filtered and balanced examples through `POST /rag/retrieve`; the Scoring Agent uses them for calibration, while citations still come only from the live RFP and proposal.

**Tech Stack:** Python, FastAPI, SQLite FTS5 for lexical fallback, the existing Gemini embedding dependency when semantic embeddings are enabled, JSON over HTTP.

---

## Task 1: Define the benchmark corpus format

**Files:**
- Create: `backend/rag/schema.py`
- Create: `backend/rag/README.md`
- Test: `backend/tests/test_rag_schema.py`

- [ ] **Step 1: Write a failing test** asserting a record requires `criterion_id`, `sample_type`, `score`, `text`, and `source_file`, and rejects an unknown sample type.
- [ ] **Step 2: Run** `python -m pytest backend/tests/test_rag_schema.py -v`; expect failure because the schema module does not exist.
- [ ] **Step 3: Implement** one Pydantic model for `BenchmarkRecord` and one model for the retrieval request/response. Allow sample types `weak`, `medium`, `strong`, `overpromise`.
- [ ] **Step 4: Run** the same test; expect PASS.
- [ ] **Step 5: Commit** `feat: define scoring rag records`.

## Task 2: Add Markdown ingestion

**Files:**
- Create: `backend/rag/ingest.py`
- Create: `backend/rag/data/records.jsonl`
- Test: `backend/tests/test_rag_ingest.py`

- [ ] **Step 1: Write a failing test** using a small Markdown fixture with headings and assert that ingestion preserves the heading, source file, and sample type.
- [ ] **Step 2: Run** `python -m pytest backend/tests/test_rag_ingest.py -v`; expect failure because ingestion does not exist.
- [ ] **Step 3: Implement** a standard-library Markdown splitter that starts a new chunk at `#`, `##`, or `###`, keeps the heading with its text, and emits JSONL records. Do not split a table or bullet list away from its heading.
- [ ] **Step 4: Add a mapping file** for the 100 samples so each source file maps to `weak`, `medium`, `strong`, or `overpromise`; do not infer the label from text.
- [ ] **Step 5: Run** the test and ingest the real sample directory; expect valid JSONL with no empty records.
- [ ] **Step 6: Commit** `feat: ingest markdown benchmark cases`.

## Task 3: Implement retrieval

**Files:**
- Create: `backend/rag/store.py`
- Create: `backend/rag/retrieve.py`
- Test: `backend/tests/test_rag_retrieve.py`

- [ ] **Step 1: Write a failing test** that queries `timeline` and returns only timeline records, with at most one result per sample type when `top_k_per_type=1`.
- [ ] **Step 2: Run** `python -m pytest backend/tests/test_rag_retrieve.py -v`; expect failure.
- [ ] **Step 3: Implement** SQLite FTS5 indexing over `text`, `section`, and `reasoning`, with metadata columns for criterion and sample type.
- [ ] **Step 4: Implement** filtered retrieval followed by per-type ranking. Return fewer than four matches when a type has no relevant record.
- [ ] **Step 5: Add semantic ranking using the existing Gemini embedding provider only if the API key is configured; retain FTS5 as the deterministic fallback.
- [ ] **Step 6: Run** the retrieval test and a four-query smoke test for timeline, pricing, completeness, and contradiction; expect PASS.
- [ ] **Step 7: Commit** `feat: add benchmark retrieval`.

## Task 4: Expose the team integration endpoint

**Files:**
- Modify: `backend/main.py`
- Create: `backend/rag/api.py`
- Test: `backend/tests/test_rag_api.py`
- Modify: `docs/api/review-contract.md`

- [ ] **Step 1: Write a failing API test** for `POST /rag/retrieve` with the request in the design document and assert a JSON response containing `matches`.
- [ ] **Step 2: Run** `python -m pytest backend/tests/test_rag_api.py -v`; expect failure because the route is absent.
- [ ] **Step 3: Implement** the route using the Pydantic request model and the local store. Return `400` for missing criterion id or proposal context, and `200` with an empty list when no match exists.
- [ ] **Step 4: Add the endpoint request/response to the API docs and tell the AI team to call `http://<backend-host>:8000/rag/retrieve` once per criterion.
- [ ] **Step 5: Run** the API test and `python -m py_compile backend/main.py backend/rag/*.py`; expect PASS.
- [ ] **Step 6: Commit** `feat: expose scoring rag api`.

## Task 5: Connect Scoring Agent and verify end to end

**Files:**
- Modify: the Scoring Agent repository's prompt/client module
- Create: `docs/api/scoring-agent-rag-integration.md`

- [ ] **Step 1: Add a client call** that sends `criterion`, `proposal_context`, and `requirement_context` to `/rag/retrieve`.
- [ ] **Step 2: Insert returned matches under a clearly labeled `BENCHMARK REFERENCES` prompt section.
- [ ] **Step 3: Add prompt rules** that `final_criteria` is authoritative, benchmark text is not citation evidence, and missing evidence must remain missing.
- [ ] **Step 4: Run the agent on the four existing sample proposals and record score ordering plus detected overpromise conflicts.
- [ ] **Step 5: Run the agent on one unseen RFP/proposal pair and verify every citation quote exists in the live input.
- [ ] **Step 6: Commit the client and integration note** in the AI team's repository.

## Handoff contract

The AI team only needs:

```text
POST http://<rag-host>:8000/rag/retrieve
Content-Type: application/json
```

The response is reference context, not the final score. Their agent still returns the existing `POST /api/review` response shape.

