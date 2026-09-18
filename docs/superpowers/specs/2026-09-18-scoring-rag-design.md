# Scoring RAG Design

## Goal

Build a small benchmark-retrieval service that helps the Scoring Agent evaluate an unseen proposal against criteria produced by the RFP Analyst.

## Scope

In scope:

- Ingest Markdown benchmark samples and split them into scoring cases.
- Retrieve relevant weak, medium, strong, and overpromise examples for one criterion.
- Expose retrieval through a stable HTTP contract for the AI team.
- Keep benchmark examples separate from evidence citations in the live RFP and proposal.

Out of scope:

- A separate Criteria RAG pipeline.
- Fine-tuning a model.
- Having RAG calculate the final score.
- Using benchmark text as a citation for the live proposal.

## Architecture

```text
benchmark Markdown files
        │ offline ingest
        ▼
Scoring RAG index
        │ POST /rag/retrieve
        ▼
Scoring Agent ── final_criteria + proposal ──> final.json
```

The RFP Analyst remains responsible for creating `final_criteria`. The Scoring Agent remains responsible for judgment, score, reasoning, and live-document citations. RAG only returns comparable evaluation examples and their metadata.

The index uses metadata filters plus semantic retrieval. Each query is restricted to the active criterion and returns a balanced set of examples across the four sample types when available. A lexical fallback is allowed when embeddings are unavailable.

## Benchmark record

Each indexed record represents one evaluation case, not an entire proposal:

```json
{
  "id": "response_3_strong:timeline",
  "sample_type": "strong",
  "criterion_id": "timeline",
  "requirement_ids": ["r5", "timeline"],
  "section": "Timeline",
  "text": "Phase 1 runs from 1 April to 30 April...",
  "score": 5,
  "reasoning": "Concrete milestones and dates satisfy the criterion.",
  "source_file": "response_3_strong.md"
}
```

The benchmark corpus is reference material only. The Scoring Agent must cite the current proposal/RFP, never `source_file` from a retrieved benchmark record.

## Retrieval API

`POST /rag/retrieve`

Request:

```json
{
  "criterion": {
    "id": "timeline",
    "name": "Timeline clarity",
    "description": "Concrete milestones and dates",
    "levels": {"1": "...", "2": "...", "3": "...", "4": "...", "5": "..."}
  },
  "proposal_context": "The proposal says ...",
  "requirement_context": "The RFP requires ...",
  "top_k_per_type": 1
}
```

Response:

```json
{
  "matches": [
    {
      "sample_type": "strong",
      "criterion_id": "timeline",
      "score": 5,
      "section": "Timeline",
      "text": "...",
      "reasoning": "..."
    }
  ]
}
```

The API returns an empty list rather than invented examples when no match exists. It should not return the full benchmark file.

## Scoring Agent handoff

The AI team calls `/rag/retrieve` once per criterion, inserts the returned matches into the scoring prompt, and instructs the agent:

1. Treat `final_criteria` as authoritative.
2. Use benchmark matches to calibrate the meaning of each level.
3. Find evidence in the current proposal and RFP.
4. Return `found: false` when a required claim is absent.
5. Never cite benchmark records as live evidence.

The existing frontend contract remains the output contract for `POST /api/review`; the RAG API is an internal/team integration contract.

## Validation

- Every benchmark record has a criterion, sample type, score, and source section.
- Retrieved matches are filtered by criterion.
- Results are balanced across sample types when data exists.
- Live citation quotes are validated against the current documents outside RAG.
- A small offline test checks that timeline, pricing, completeness, and overpromise queries retrieve the expected case types.

