# Proposal Scorer — SiviHack 2026, Track 1

**Challenge sponsor:** FPT Software Europe.

## 1. What this is

FPT's sales teams write a lot of proposals for enterprise clients (DACH/EU,
cloud and AI work). Before one goes out, a senior person reads it against the
client's RFP — checking for requirements that went unanswered, pricing and
timelines that stay vague, and promises the company cannot actually keep. That
review is manual, inconsistent, and usually squeezed against a deadline.

**Proposal Scorer** stands in for that reviewer. Give it one RFP and one draft
proposal, and in about 30 seconds it returns:

- **A score across 7 criteria** (Problem Understanding, Scope & Deliverables,
  Pricing Clarity, Timeline Clarity, Completeness vs RFP, Tone &
  Persuasiveness, Risk/Assumptions Transparency) — and you can add, remove or
  re-rank any of them before scoring runs.
- **Every RFP requirement checked one by one**: addressed, vague, missing or
  contradicted, each with a verbatim quote from both documents and a concrete
  replacement sentence. Not "this is unclear" but the paragraph to write
  instead.
- **A hard stop on contradictions.** When the draft breaks something the RFP
  states outright — the RFP says "no database migration" and the proposal
  proposes one — the finding is forced to high severity in code. A confident
  writing style cannot bury it.
- **A check against the company's own knowledge base** (rate card, validated
  delivery capability, SLA standard). This catches commitments the RFP cannot:
  promising 24/7 cover the company does not staff, or quoting a day rate below
  the internal floor.
- **A handoff to the team.** "Send to Work" opens a Jira ticket with the
  findings and posts it to Slack.

This is a **reviewer, not a generator**. It never drafts a proposal from
scratch; it only evaluates and improves one that already exists.

## 2. Running the demo, from a clean machine

### 2.1. Requirements

- Python 3.10+ (3.11+ recommended), Node.js 18+.
- A Gemini API key (Google AI Studio) — free, from
  [aistudio.google.com/apikey](https://aistudio.google.com/apikey).
- Disk and network for the first run: it downloads the local embedding model
  `all-MiniLM-L6-v2` (~90 MB) once, then runs entirely offline.

### 2.2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # then open .env and set GEMINI_API_KEY
uvicorn main:app --reload --port 8000
```

Check every module came up:

```bash
curl http://localhost:8000/api/health
```

```json
{
  "status": "ok",
  "modules": {
    "markitdown": true, "enterprise_evidence": true, "scoring_rag": true,
    "internal_knowledge": true, "analyze_rfp": true, "score": true
  }
}
```

A module reporting `false` does not stop the app — it disables that one
feature. With `markitdown: false` you lose PDF and Word import, and scoring
still works on pasted text. Each module is mounted inside its own `try/except`
for exactly this reason: one broken import cannot take the service down.

### 2.3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

### 2.4. One full review

1. On **Documents**, click one of the four sample chips (Weak / Medium /
   Strong / Overpromising), or paste or drop in your own RFP and proposal
   (PDF, Word, PowerPoint, Excel, an image, or `.md`/`.txt`).
2. Click **"Review this proposal"** — about 10-15 seconds while the RFP
   Analyst reads the RFP.
3. On **Criteria**, see what the AI proposed and at what priority (High /
   Medium / Low). Drag a card to another column or use its arrows; add or
   remove criteria. Click any requirement on a card to jump to that exact
   passage in the RFP.
4. Click **"Score the proposal"** — about 15-20 seconds while the Proposal
   Analyst scores it.
5. On **Result**: the overall score and a send / do-not-send recommendation,
   a score per criterion, every requirement with its quote and suggested fix,
   and any warnings from the internal knowledge base. **"Send to Work"** opens
   the Jira ticket (needs the config in section 3).

If the backend is down or fails, the frontend falls back to a stored sample
result labelled "Stored sample result", so a demo never dies mid-sentence.

## 3. Configuring `backend/.env`

Copy from `backend/.env.example`. Never commit the real `.env` — it is in
`.gitignore`.

| Variable | Required? | What it does |
|---|---|---|
| `GEMINI_API_KEY` | **Yes** | Key for both agents. The team shares one budget (see section 8). |
| `GEMINI_MODEL` | No (default `gemini-3.8-flash`) | `gemini-2.0-flash` was withdrawn from the API — do not go back to it. |
| `AI_PROVIDER` | No (default `gemini`) | Set to `anthropic` to switch to Claude if the Gemini budget runs out; also set `ANTHROPIC_API_KEY`. |
| `RFP_ANALYST_MODEL`, `RFP_ANALYST_ATTEMPTS` | No | Model and retry count for the RFP Analyst specifically, used when a quote comes back that does not match the source word for word. |
| `ANTHROPIC_API_KEY`, `AI_MODEL` | No | Only needed with `AI_PROVIDER=anthropic`. |
| `N8N_TICKET_WEBHOOK_URL` | No (optional feature) | Webhook URL of the n8n workflow (Webhook → Jira → Slack). Leave it empty and "Send to Work" reports an error; scoring is unaffected. See `docs/api/review-contract.md` section 5. |

## 4. Architecture

### 4.1. The pipeline

```
                      Frontend (React 18 + Vite)
                                │
      ┌─────────────────────────┼──────────────────────────┐
      │  POST /v1/markitdown/convert                        │
      ▼                                                     │
  Document reader                                           │
  PDF/DOCX/PPTX/XLSX read locally by MarkItDown;            │
  images go to Gemini OCR. Nothing else touches a model.    │
      │                                                     │
      └──────────────► raw_rfp_text, raw_proposal_text ─────┤
                                                            │
                          POST /api/analyze-rfp             │
                                ▼                           │
   ┌────────────────────────────────────────────────────┐   │
   │ RFP Analyst              LLM call 1 of 2           │   │
   │ agent/src/rfp_analyst/                             │   │
   │ LangChain + Gemini, native structured output       │   │
   │                                                    │   │
   │ → atomic requirements, one obligation each         │   │
   │ → hard constraints ("no migration") flagged        │   │
   │ → a verbatim source_quote per requirement          │   │
   │ → suggested criteria + priority per criterion      │   │
   │ → fail-closed validation: a quote that is not in   │   │
   │   the RFP word for word is rejected                │   │
   └────────────────────────────────────────────────────┘   │
                                ▼                           │
   ┌────────────────────────────────────────────────────┐   │
   │ Human checkpoint — no model call                   │   │
   │ The user re-ranks, adds and removes criteria as    │   │
   │ much as they like. This costs nothing.             │   │
   └────────────────────────────────────────────────────┘   │
                                ▼                           │
                     POST /api/confirm-criteria             │
   ┌────────────────────────────────────────────────────┐   │
   │ Criterion resolver — runs ONCE, at lock-in         │   │
   │ Only for criteria the user typed themselves:       │   │
   │ merges semantic duplicates, and links a custom     │   │
   │ criterion to real RFP requirements so it is not    │   │
   │ scored blind. 0 seconds when nobody added one.     │   │
   └────────────────────────────────────────────────────┘   │
                                ▼                           │
                          POST /api/score                   │
   ┌────────────────────────────────────────────────────┐   │
   │ Proposal Analyst + Scoring  LLM call 2 of 2        │   │
   │ AI/scoring.py, Gemini SDK directly                 │   │
   │                                                    │   │
   │ in:  requirements + both raw documents +           │   │
   │      confirmed criteria + retrieved style          │   │
   │      heuristics (never used to decide whether a    │   │
   │      requirement was met)                          │   │
   │ out: a finding per requirement, a 1-5 score per    │   │
   │      criterion, a verdict                          │   │
   └────────────────────────────────────────────────────┘   │
                                ▼                           │
   ┌────────────────────────────────────────────────────┐   │
   │ Deterministic layer — plain code, no model         │   │
   │ · overall_score = weighted mean of the criteria    │   │
   │ · hard constraint contradicted → severity high     │   │
   │ · Completeness scored from the findings, not from  │   │
   │   the model counting them correctly                │   │
   │ · every citation re-checked against its source;    │   │
   │   an invented quote is blanked and reported        │   │
   │ · company commitment check (string matching        │   │
   │   against the rate card and SLA standard)          │   │
   └────────────────────────────────────────────────────┘   │
                                ▼                           │
                            Result screen ◄─────────────────┘
                                │
                    POST /api/create-ticket (optional)
                                ▼
                    n8n → Jira (ticket) → Slack (team)
```

### 4.2. Why it is built this way

**Two agents, not three.** An earlier design had a separate Proposal Analyst
and Scoring Agent. They were merged because two models can disagree with each
other — one calling something a serious gap, the other scoring it well — and
because a third call costs latency and budget on a live demo. One agent means
one source of truth per score.

**The arithmetic is not the model's job.** The weighted average, the
hard-constraint severity floor, the Completeness score and the send / do-not-send
recommendation are all computed in Python. A model asked to weight seven
numbers will sometimes get it wrong, silently. This also makes live re-weighting
during a demo instant: no extra call.

**Every quote is verified against its source.** The model is asked for verbatim
citations, and then the backend checks each one actually appears in the
document, normalising only whitespace, dashes, quote marks and Markdown
emphasis. A citation that cannot be found is blanked and counted in a warning
rather than shown. On unseen documents this has caught fabricated quotes in
practice.

**The user's edit always wins.** `confirmed_criteria` is the single source of
truth for what gets scored and at what weight. The AI's suggestion is a
starting point; the scoring prompt is told the priority is applied later in
code, so it does not discount a low-priority criterion's own score and have it
discounted a second time.

**RAG is scoped narrowly.** Retrieved examples calibrate *writing quality* on
the four subjective criteria (Pricing, Timeline, Tone, Risk). They never decide
whether a requirement was met — that stays grounded in the requirements the RFP
Analyst extracted. Otherwise a fluent, confident proposal that contradicts the
RFP would score well, which is exactly the failure the sponsor's overpromise
sample is designed to expose.

**The corpus check is deterministic on purpose.** The company knowledge check
is plain string matching, no model and no retrieval, so it returns the same
answer every time and attaches a verbatim quote to every finding. It is the one
part of the review that cannot be explained by the RFP.

### 4.3. Components

| Layer | Technology | Role |
|---|---|---|
| Frontend | React 18 + Vite, no CSS framework | Three screens: Documents → Criteria → Result |
| Backend | FastAPI + Uvicorn + Pydantic v2 | HTTP routing, schema validation, glue between the two agents |
| RFP Analyst | LangChain (`langchain-google-genai`) + Gemini, structured output | Requirements, hard constraints, suggested criteria — one model call |
| Proposal Analyst | Gemini SDK directly (`google-generativeai`) | Scores 7 criteria and checks every requirement — one model call, with a repair retry on invalid JSON |
| Style-heuristic RAG | Keyword overlap + `all-MiniLM-L6-v2` running locally (hybrid) | Supports only the 4 subjective criteria; never touches completeness |
| Internal knowledge base | Pure string matching, no model | Catches promises beyond validated capability and rates below the card |
| Document reader | `markitdown` (+ Gemini OCR for images) | PDF/Word/PowerPoint/Excel/image → Markdown |
| Automation | n8n Cloud → Jira → Slack | The "Send to Work" button, optional |

### 4.4. The n8n workflow ("Send to Work")

`Webhook → Jira: Create Issue → Slack: Send a message → Respond to Webhook`.
Pressing "Send to Work" on the Result screen POSTs the scoring result to this
webhook; n8n opens a Jira ticket summarising the medium and high severity
findings, then posts the ticket link to Slack with `<!channel>`.

![n8n workflow: Webhook → Jira → Slack](docs/assets/n8n-workflow.png)

To rebuild the workflow and get a webhook URL, see
`docs/api/review-contract.md` section 5.

## 5. API

| Endpoint | What it does |
|---|---|
| `GET /api/health` | Per-module status |
| `POST /api/analyze-rfp` | RFP Analyst — RFP in, `rfp_analysis` + suggested criteria out |
| `POST /api/confirm-criteria` | Locks the criteria after the user's edits (merges duplicates, links custom criteria to the RFP) |
| `POST /api/score` | Proposal Analyst — returns `scoring` |
| `POST /api/create-ticket` | Sends the result to n8n for the Jira ticket and Slack post |
| `POST /v1/markitdown/convert` | PDF/Word/PowerPoint/Excel/image → Markdown |
| `POST /rag/retrieve` | Queries the benchmark store directly, for debugging |
| `GET/POST /api/evidence/*` | Internal knowledge base: search, commitment check, source documents |

Field-by-field schemas: `docs/api/review-contract.md`.

## 6. Data and dependencies

**Datasets:**

- `docs/challenge/sample_data/` — one RFP (NordFrame Logistics) plus four
  sample proposals (weak / medium / strong / overpromise) and one reference
  output (`scoring_example.md`), used to calibrate the prompts.
- `proposal_scorer_benchmark/` — 6 fictional RFPs across 6 different
  industries × 4 responses = 24 pairs, used to widen the good-writing /
  bad-writing heuristics. Deliberately not NordFrame, so the system does not
  learn one case by heart.
- `backend/rag/data/records.jsonl` — 557 chunks from those two sources, with
  matching vectors in `embeddings.npz`.

**Main libraries** (full lists in `backend/requirements.txt`,
`frontend/package.json`, `agent/pyproject.toml`):

| Library | Used for |
|---|---|
| `fastapi`, `uvicorn`, `pydantic` | Backend API and schema validation |
| `google-generativeai` | Calling Gemini directly (Proposal Analyst) |
| `langchain-google-genai` | Calling Gemini with structured output (RFP Analyst) |
| `anthropic` | Fallback provider via `AI_PROVIDER=anthropic` |
| `sentence-transformers`, `numpy` | Local embeddings for the hybrid RAG, no external API |
| `markitdown[pdf,docx,pptx,xlsx,xls]` | Document conversion. The extras matter: a bare install cannot read PDF or Word |
| `python-multipart` | File uploads through FastAPI |
| `react`, `vite` | Frontend |

## 7. Known limits

- **One shared Gemini budget, capped at $100.** Each review costs two model
  calls (RFP Analyst + Proposal Analyst). When it runs out, switch
  `AI_PROVIDER=anthropic` in `.env`.
- **The hybrid RAG pulls in `sentence-transformers`/`torch`** — a heavy install
  (minutes, hundreds of MB) that needs network the first time it fetches the
  model. Without them the system falls back to keyword-only matching rather
  than failing.
- **PDF and image quality depends on `markitdown` and Gemini OCR.** A blurred
  scan or a complex layout can yield the wrong passage.
- **Tested on fictional RFPs only** (NordFrame plus the 24 benchmark pairs).
  The prompts are written to generalise — nothing is hard-coded to NordFrame —
  but there are no numbers yet from a real client document.
- **"Send to Work" needs the n8n workflow built by hand first** (Webhook →
  Jira → Slack). Nothing is provisioned automatically; see
  `docs/api/review-contract.md` section 5.
- **No timeout or cancel on a model call.** If Gemini responds unusually
  slowly, the user waits or reloads (the stored sample result appears
  instead).

## 8. Security

- `backend/.env` is in `.gitignore`. **Do not commit it, and do not paste the
  key into Slack, Discord or Zalo.**
- All sample material — RFPs, proposals, company names — is fictional. There is
  no real client data in this repository.
- Credentials the organisers issue to the team (n8n Cloud vouchers, API keys)
  belong in the team's password manager, not in this README.

> **Vietnamese version:** [`../README.md`](../README.md) — the team's copy,
> and the one GitLab renders. This English file is what GitHub shows on the
> public repository. Changing one means changing the other.

## 9. Related documentation

- Field-by-field API contract: `docs/api/review-contract.md`
- Scoring logic, schemas, architecture decisions: `docs/architecture.md`
- RFP Analyst (standalone package): `agent/README.md`
- Hybrid RAG: `backend/rag/README.md`

## 10. Licence

This project is released under the **MIT Licence** — see [`LICENSE`](LICENSE)
for the full text. In short: anyone may use, copy, modify and distribute this
code, including commercially, as long as the copyright notice and the licence
text travel with it. It is provided without warranty.

Copyright is held jointly by the **SiviHack 2026 Proposal Scorer
contributors** rather than by any one person, because six people have commits
in this repository. No single contributor can license another's work, so the
notice names the group.

Two things in this repository are **not** covered by that licence:

- **The sponsor's challenge material.** The brief and the sample data under
  `docs/challenge/` were supplied by the organisers and FPT Software Europe.
  They remain theirs. The public GitHub mirror of this project omits the brief
  PDF for that reason.
- **Third-party dependencies**, which keep their own licences. The
  `all-MiniLM-L6-v2` embedding model is Apache-2.0; the Python and JavaScript
  packages listed in section 6 carry their own terms.

If you are reading this as a judge or a reviewer: the work in `AI/`, `agent/`,
`backend/` and `frontend/` is ours. The RFPs and proposals it reads are
fictional material written for the challenge.
