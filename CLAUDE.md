# CLAUDE.md — SiviHack 2026, Track 1: Proposal Scorer (AI team scope)

This file is project context for Claude Code working in this repo, scoped to
the **AI team member** working here (prompt design + scoring logic). The team
splits work as: AI (this scope) / Backend (API routing, file upload, deploy) /
Frontend (UI). Read "Architecture", "Your scope" and "Interface contract"
first — they define what you own and what you hand off to the rest of the
team.

## What we're building

**Proposal Scorer** — sponsor: FPT Software Europe (Track 1 of SiviHack 2026).

FPT's teams write a lot of client proposals (DACH/EU enterprise IT, cloud, AI
projects). Today a senior person manually reviews each proposal before it goes
out — checking it against the client's RFP, catching vague pricing/timelines,
missing requirements, and overpromising. That review is manual, inconsistent,
and often rushed right before a deadline.

**Goal:** a tool that gives a salesperson a fast, specific, structured second
opinion on a draft proposal — comparable to a quick review from an experienced
colleague — without waiting on a person's availability. The AI logic you build
is the actual product judges are evaluating; the API/UI around it just needs
to expose it live.

**Hard constraints (do not violate):**
- This is a **reviewer, not a generator**. Never build a "write me a proposal
  from scratch" feature — only evaluate/improve an existing draft.
- Feedback must be **specific and actionable** ("Section 3 doesn't mention the
  budget the client specified" beats "improve clarity").
- No real client data — everything is fictional/anonymized sample material.
- Must generalize: on demo day judges bring an **unseen** RFP+proposal pair.
  Nothing in the prompt/logic can be hardcoded to the sample NordFrame data.

## Judging criteria — your prompt/logic is what's actually being scored on

1. Is the feedback specific and actionable (points to an exact section/issue),
   not generic ("could be clearer")?
2. Does the tool meaningfully use the RFP to check whether the proposal
   addresses actual client requirements, rather than scoring it in isolation?
3. Bonus (optional): can it handle longer/messier real-world documents. (Text
   extraction from PDF is Backend's job — but if they hand you messy/OCR'd
   text, your prompt should be robust to that, e.g. noisy whitespace, page
   headers/footers bleeding into the text.)

## Architecture — 2 agents + a RAG heuristics store (not 3 agents)

Earlier design explored 3 agents (RFP Analyst / Proposal Analyst / Scoring
Agent). We merged Proposal Analyst + Scoring Agent into one, for two reasons:
a 3rd LLM call adds cost/latency against the shared Gemini budget and the live
demo, and — more importantly — two separate agents risked *disagreeing with
each other* (Proposal Analyst calling something a serious gap in its findings,
Scoring Agent then scoring it well because of how weights got applied). One
agent doing both means a single source of truth for every score.

**1. RFP Analyst** (LLM call #1) — reads the RFP, outputs structured JSON:
client/project metadata, the list of explicit requirements (each tagged with
which rubric criterion it maps to, and whether it's a hard constraint — see
schema below), and optionally a suggested criteria/weight set for this client
(the brief's "AI suggests which criteria matter most" stretch goal). See
`docs/challenge/sample_data/scoring_example.md`'s Level 3 example for the tone
of that suggestion ("RFP repeats 'no migration' and 'minimal disruption' →
continuity matters more here than technical sophistication").

**2. [Human checkpoint, not an LLM step]** — the frontend shows the suggested
criteria/weights to the user, who confirms or edits them (add/remove a
criterion, change a weight) before scoring runs. This directly implements the
brief's "configurable criteria" requirement. Implement this as two separate
API calls rather than a stateful resumable workflow: `POST /api/analyze-rfp`
returns the RFP Analyst's output; the frontend holds it and the user's edits;
`POST /api/score` is called once the user is ready, carrying the (possibly
edited) criteria along with the proposal.

**3. Proposal Analyst** (LLM call #2, merged with scoring) — takes the RFP
Analyst's structured requirements + the raw RFP text (for citation fidelity)
+ the raw proposal text (needed independently, because criteria like Tone &
Persuasiveness aren't tied to any single requirement) + the confirmed
criteria/weights + **retrieved quality heuristics for the criteria being
judged** (see RAG section below). In one call it should still reason in
explicit internal steps (even though it's a single prompt): first go
requirement-by-requirement (status/citation/severity/reason/suggested_patch),
then synthesize those findings plus a holistic read of the proposal into the
7-criterion scorecard, then write the overall verdict + improvement summary.

**4. Weighted overall score = plain code, not LLM.** Once Proposal Analyst
returns a 1-5 score per criterion, computing the weighted overall average from
the user's confirmed weights is a deterministic formula — do it in Python in
the backend/glue layer, not inside the LLM prompt. This also makes live
re-weighting during the demo cheap: recompute instantly from cached
per-criterion scores, no extra LLM call needed.

### RAG — used for generic proposal-quality heuristics, NOT domain content or a generated reference proposal

We use RAG, but scoped narrowly and deliberately, after weighing this against
an earlier, riskier version of the idea (see history below) — this is the
version we're building:

**What the corpus is:** short, generic heuristic snippets describing what a
*strong proposal structurally looks like* per rubric criterion — e.g. "a
strong pricing section breaks costs down by line item and states a total
within the client's stated budget," "a strong risk section names at least one
concrete, specific dependency, not a vague disclaimer," "a strong timeline
maps milestones explicitly onto the RFP's own stated targets." Derive these
from `docs/challenge/sample_data/response_3_strong.md` and
`docs/challenge/sample_data/scoring_example.md`. If you want a richer/more
robust corpus, it's fine to have the team generate a handful of *additional
synthetic strong/weak proposal examples in other fictional industries* (not
NordFrame) ahead of time, specifically to mine more domain-agnostic patterns
from — that's a build-time curation step done by you, not something generated
live for whatever RFP a judge brings.

**What the corpus is NOT:** not NordFrame-specific facts (no PostgreSQL, no
warehouse-specific content), and not a live-generated "ideal reference
proposal" for the specific RFP being scored at runtime — see the rejected
alternative below for why that version is risky.

**Where it plugs in:** only into the more subjective, writing-quality side of
scoring — Tone & Persuasiveness, and the "how clearly/well-structured is this"
half of Pricing Clarity / Timeline Clarity / Risk Transparency. It must NOT
replace the factual completeness check — Problem Understanding and
Completeness vs RFP Requirements stay grounded directly in RFP Analyst's
explicitly extracted requirements, not in heuristics. Heuristics answer "is
this well-written," not "was this requirement addressed."

**Retrieval mechanism — implemented by Backend, not AI (superseded plan):**
this was originally scoped as an AI-team deliverable (static dict +
embedding fallback). Backend built the real version instead, in
`backend/rag/`: a 168-record benchmark index (24 sample proposals × 7
criteria) with pure keyword-overlap ranking (no embeddings, no extra API/
budget dependency — see `backend/rag/README.md`/`docs/design.md`). AI/
consumes it through `AI/rag_client.py`, which imports `backend.rag.api`
directly in-process (Backend's own recommended integration path, not the
`/rag/retrieve` HTTP endpoint) and keeps the same exclusion policy: no
examples for Problem Understanding, Scope & Deliverables Clarity, or
Completeness vs RFP Requirements, base criteria matched by canonical
snake_case id, anything else treated as custom and searched across the
whole corpus.

**Still regression-test against `response_4_overpromise.md`:** that proposal
reads fluently and confidently, which is exactly what a writing-quality
heuristic match could reward. Make sure the RAG-assisted criteria never
override or soften the hard-constraint violation (DB migration contradiction)
that RFP Analyst/Proposal Analyst's direct requirement comparison must still
catch independently of any heuristic score.

**Rejected alternative (for context, don't rebuild this):** we first
considered building a RAG index from NordFrame-flavored mock data to have the
AI draft a full "ideal" reference proposal, then score the real proposal by
similarity to it. Rejected because a corpus built from one fictional client's
domain content doesn't transfer to the unseen validation RFP judges bring on
demo day (likely a different industry entirely), it blurs the reviewer/
generator line the brief explicitly draws, and it's failure-prone in a
specific, hard-to-debug way: a similarity-to-generated-reference approach only
catches `response_4_overpromise.md`'s DB-migration contradiction if the
generated reference happens to explicitly rule out migration too — an extra,
unverifiable point of failure. Direct comparison against RFP Analyst's
explicitly extracted requirements (one of which is literally "no migration
required") catches it deterministically. The heuristics-only version above
keeps the benefit (something concrete to compare writing quality against)
without that risk, because it never depends on a live-generated draft being
complete or correct.

## Your scope (AI team)

You own the actual "brain" of the tool:
- **Prompt design** for both LLM calls (RFP Analyst, Proposal Analyst) per the
  architecture above.
- **The rubric logic**: base 7 criteria (table below), configurable via the
  human checkpoint step — user can adjust weights or add/remove criteria
  before scoring, seeded by RFP Analyst's suggestion.
- **Wiring RAG examples into the prompt** for the right criteria only — the
  retrieval store itself is now Backend's (`backend/rag/`), consumed via
  `AI/rag_client.py`; see the RAG section above.
- **Grounding & citations**: every score and every flagged issue must point
  back to a specific requirement/quote — e.g. *"Completeness: 2/5 — RFP
  Section 4 requires a data migration plan; not mentioned anywhere in the
  proposal."* This is the single biggest differentiator per the judging
  criteria. See `docs/challenge/sample_data/scoring_example.md` for the target
  level of specificity (you don't need to match its exact format).
- **Suggested fixes**: for each significant issue, produce a concrete fix — a
  rewritten paragraph, a suggested addition covering a missing requirement, or
  clearer phrasing for pricing/timelines. Not just "this is vague."
- **Output schemas + parsing**: define strict Pydantic schemas for both LLM
  calls' output (see below) so the JSON is validated, not just hopefully
  well-formed — handle retries/repair if a call returns invalid JSON.
- **Model/provider choice**: `backend/main.py`'s `call_ai()` already switches
  between Gemini (default, `gemini-3.8-flash`) and Anthropic via `AI_PROVIDER`
  in `.env`. Keep your logic provider-agnostic — don't hardcode to one API's
  SDK/response shape, since the shared Gemini budget ($100 team-wide cap)
  could run out mid-hackathon and the team may need to flip to Anthropic.
  (RAG retrieval no longer touches this budget at all — Backend's
  `backend/rag/` is pure keyword overlap, no embedding/LLM calls.)
- **Calibration/testing**: validate both calls against all 4 sample responses
  (see below) before handing off.

**Not your scope** (owned by Backend/Frontend teammates — don't spend time
here unless coordinating on the interface): FastAPI route wiring, request
validation, file upload handling, PDF text extraction, CORS/deploy, and all
UI/UX (including the criteria-edit checkpoint UI itself — you just need to
produce and accept the right JSON shape for it). Hand them clean functions/
modules and let them wire it into the two endpoints and the screen.

## Output schemas (Pydantic — the actual interface contract, v1.1)

RFP Analyst's output (`POST /api/analyze-rfp` response body):
```python
class CriterionWeight(BaseModel):
    name: str
    description: str
    weight: float                 # > 0

class SourceRef(BaseModel):
    source_section: str
    quote: str                    # must exist verbatim in the source document

class CriterionPacket(BaseModel):
    criterion_name: str           # one of the 7 canonical names below, or a user-added name
    origin: str                   # "base" | "rfp_explicit" | "ai_inferred" | "user"
    evaluation_guidance: list[str]
    requirement_ids: list[str]    # AUTHORITATIVE grouping for scoring — Proposal Analyst
                                   # joins findings to a criterion via this list, not by
                                   # filtering Requirement.related_criterion. E.g. the
                                   # "Completeness vs RFP Requirements" packet lists every
                                   # requirement id (cross-cutting), not just ones whose
                                   # related_criterion happens to equal "Completeness...".
    source_refs: list[SourceRef]
    notes: list[str]              # free-text guardrails, e.g. prefixed
                                   # "USER_DEFINED_NOT_RFP: ...", "RFP_AMBIGUITY: ...",
                                   # "INSUFFICIENT_DETAIL: ...", "POSSIBLE_OVERLAP: ...",
                                   # "ENRICHMENT_FAILED: ..."

class Requirement(BaseModel):
    id: str                       # "REQ-001", stable within one analysis
    text: str                     # atomic, near-exact paraphrase — one obligation per requirement
    source_section: str           # e.g. "Requirement 6" or a section name
    source_quote: str             # verbatim quote from the RFP — used to verify citation fidelity
    related_criterion: str        # one of the 7 rubric criterion names below (primary/default tag)
    is_hard_constraint: bool      # e.g. "no migration required" = True

class RFPAnalysis(BaseModel):
    client_name: str              # "" if the RFP doesn't name one — never invent
    project_name: str             # "" if the RFP doesn't name one — never invent
    requirements: list[Requirement]
    suggested_criteria_weights: list[CriterionWeight] | None = None  # optional stretch; a
                                   # seed for the human checkpoint UI only — Proposal Analyst
                                   # never reads this directly, it consumes confirmed_criteria
    criterion_packets: list[CriterionPacket]
    detected_priority_note: str | None = None
    # optional stretch, Level-3 style ("RFP repeats 'no migration' → continuity matters more
    # than technical sophistication"). This is an UNCONFIRMED AI inference, shown to the user
    # for context only — it must never auto-adjust weights or add/remove requirements itself.
```

Proposal Analyst's input (`POST /api/score` request body):
```python
class ScoringInput(BaseModel):
    rfp_analysis: RFPAnalysis
    raw_rfp_text: str
    raw_proposal_text: str
    confirmed_criteria: list[CriterionWeight]  # the single source of truth for which
                                   # criteria to score and at what weight, after the human
                                   # checkpoint — may differ from suggested_criteria_weights
```

Proposal Analyst's output (`POST /api/score` response body — scoring merged in):
```python
class RequirementFinding(BaseModel):
    requirement_id: str          # matches Requirement.id from RFPAnalysis
    status: str                  # "met" | "missing" | "vague" | "contradicted"
    severity: str                # "high" | "medium" | "low"
    reason: str
    citation: str                # quote/location from the proposal; "" when status="missing"
                                  # (never fabricate a citation for something that isn't there —
                                  # the RFP-side quote is still available via
                                  # Requirement.source_quote for the same requirement_id)
    suggested_patch: str

class CriterionScore(BaseModel):
    name: str                    # one of the 7 rubric criteria (or a user-added one)
    score: int                   # 1-5
    comment: str
    citations: list[str] = []

class ScoringResult(BaseModel):
    client_name: str             # copied verbatim from RFPAnalysis.client_name — never
                                  # re-derived or guessed by the LLM
    project_name: str            # copied verbatim from RFPAnalysis.project_name
    findings: list[RequirementFinding]
    criteria: list[CriterionScore]
    overall_score: float         # computed in code from criteria + confirmed weights, not by the LLM
    verdict: str                 # short overall summary, scoring_example.md style
```

Hard rule (enforce in code after parsing, don't just trust the prompt): if
`Requirement.is_hard_constraint` is `True` and its finding's `status` is
`"contradicted"`, force `severity = "high"` regardless of what the LLM output.

The 7 canonical criterion name strings below are used as dict keys for the
RAG static-lookup heuristics store — match them **character-for-character**
everywhere: this schema, `criterion_packets`, `confirmed_criteria`, and the
heuristics dict. A silent string mismatch here just means a criterion
quietly gets no heuristics, no crash, so treat it as a merge-blocking check
between AI and RFP Analyst before wiring the two calls together.

Note criterion #5 is **"Completeness vs RFP Requirements" — no period after
"vs"**, even though the Appendix A brief text below writes "vs.". This
repo's actual source of truth is `agent/src/rfp_analyst/` (RFP Analyst's
package): the no-period spelling is baked into its `Literal` type, its base
criteria list, its prompt text, its JSON schema, and its fixtures — all
already tested. `AI/contracts.py` conforms to that spelling for this reason,
not the brief's. If you ever add a new hard-coded copy of this string
anywhere, copy it from `AI/contracts.py:BASE_CRITERIA` or
`agent/src/rfp_analyst/config.py`, not from the rubric table below.

Treat these as a draft you and Backend should agree on early — the exact
field names matter less than locking them down together so nobody's blocked.
Put your actual implementation wherever you and Backend agree (e.g. a
`backend/scoring.py` module that `main.py` imports), so it's a clean import
rather than logic tangled into the route handlers.

## Base rubric (Appendix A of the brief) — your default criteria set

| # | Criterion | What to check |
|---|---|---|
| 1 | Problem Understanding | Does the proposal correctly reflect the client's actual stated problem/goals from the RFP, not a generic pitch? |
| 2 | Scope & Deliverables Clarity | Are deliverables specific and unambiguous? Clear what is/isn't included? |
| 3 | Pricing Clarity | Is pricing clearly stated/broken down (vs. vague or "on request")? |
| 4 | Timeline Clarity | Are milestones/dates concrete, not vague ("in due course")? |
| 5 | Completeness vs. RFP Requirements | Does the proposal address every requirement the RFP explicitly asked for? |
| 6 | Tone & Persuasiveness | Confident, client-focused, professional — not generic boilerplate? Not tied to any single requirement — needs the raw proposal text, not just the findings list. |
| 7 | Risk/Assumptions Transparency | Are assumptions/dependencies/risks clearly flagged, not hidden? |

## Sample data — use these to build and calibrate your prompts

- `docs/challenge/track-1-proposal-scorer.pdf` — full organizer brief.
- `docs/challenge/sample_data/rfp_nordframe.md` — the one client RFP
  (NordFrame Logistics, warehouse inventory dashboard) used for every sample
  response below.
- `docs/challenge/sample_data/response_1_weak.md` — generic, deferred
  pricing/timeline, several requirements missing entirely. Should score low.
- `docs/challenge/sample_data/response_2_medium.md` — good functional scope
  match, but vague pricing/timeline, no risk disclosure. Should score mid,
  with those specific gaps flagged.
- `docs/challenge/sample_data/response_3_strong.md` — fully addresses the
  RFP, specific and transparent. Should score high, few/no missing
  requirements. Also your primary source for the RAG heuristics corpus.
- `docs/challenge/sample_data/response_4_overpromise.md` — scope balloons
  beyond the ask, **contradicts an explicit RFP constraint** (proposes
  migrating off the existing PostgreSQL DB when the RFP says no migration),
  unrealistic 8-week timeline/price. Your prompt must specifically catch the
  contradiction (mark that requirement `is_hard_constraint: true` and make
  sure a contradiction always surfaces as `status: "contradicted"`, `severity:
  "high"`) — not just reward its confident tone or well-structured pricing
  table with a decent score via the RAG heuristics.
- `docs/challenge/sample_data/scoring_example.md` — example of good tool
  output (Level 1/2/3 style), scored against `response_1_weak.md`. Use as your
  calibration target for specificity/citation quality, and as a second source
  for the RAG heuristics corpus.

Run all four responses through both calls against the one RFP as a regression
check before every hand-off: weak < medium < strong should be obvious, and
response_4's contradiction must surface as a flagged issue regardless of how
well the RAG heuristics score its writing quality.

## Current AI-relevant code state

- `backend/main.py` — starter kit's only endpoint today is a generic
  `POST /api/ask` (`{prompt} -> {answer}`), not the scorer. `call_ai()` is the
  existing provider-switch pattern (Gemini default via `AI_PROVIDER` in
  `.env`, Anthropic fallback) — reuse this pattern for both your LLM calls
  rather than inventing a new one.
- `backend/.env` — gitignored; copy from `.env.example` if missing. Gemini key
  has a **team-wide $100 lifetime cap** — default to `gemini-3.8-flash` while
  iterating on your prompts, only reach for a stronger model once they're
  close to final.
- `backend/requirements.txt` — fastapi, uvicorn, pydantic, python-dotenv,
  anthropic, google-generativeai, requests. No embedding/vector-store deps
  needed — RAG retrieval (`backend/rag/`) is pure stdlib keyword overlap.
- `backend/rag/` — Backend's real RAG implementation (see the RAG section
  above and `backend/rag/README.md`). AI/ consumes it via
  `AI/rag_client.py:retrieve_examples()`, not built by the AI team.
- `agent/` — RFP Analyst, a separate `uv`-managed package
  (`agent/src/rfp_analyst/`). Its `package` CLI command produces the exact
  `ScoringInput` JSON `AI/contracts.py` expects — see `agent/README.md`.

## Do NOT build

- A proposal generator. Anything that drafts a new proposal from scratch is
  out of scope — this tool only reviews and improves an existing draft.
- A RAG corpus of domain-specific content (e.g. mock NordFrame-style
  proposals), or a live-generated "ideal reference proposal" per RFP used as
  the primary basis for scoring. Considered and rejected — see the RAG
  architecture note above. The only RAG corpus in scope is the generic,
  criterion-level writing-quality heuristics described there.
