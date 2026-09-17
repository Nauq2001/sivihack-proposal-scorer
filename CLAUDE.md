# Proposal Scorer — working notes for Claude

SiviHack 2026, Track 1, sponsor FPT Software Europe. Full brief:
`docs/challenge/track-1-proposal-scorer.pdf`. Sample data:
`docs/challenge/sample_data/`.

## What we are building

A **reviewer**, not a writer. The user pastes or uploads a client RFP and a draft
proposal; the tool returns fast, specific, structured feedback before the
proposal goes out. Never generate a proposal from scratch.

Output the judges look for, in priority order:

1. **Specific, actionable feedback** pointing at an exact section/issue — never
   "could be clearer".
2. **RFP-grounded checks**: each explicit RFP requirement marked addressed /
   vague / missing / contradicted, with a suggested fix.
3. Score per criterion (Appendix A: Problem Understanding, Scope & Deliverables,
   Pricing, Timeline, Completeness vs RFP, Tone, Risk/Assumptions) + comment.
4. **Citations** back to RFP section and proposal section for every claim.
5. Configurable criteria (weights, add/remove), optionally AI-suggested from the
   RFP.
6. Bonus: PDF input (RFPs as PDF, proposals exported from PowerPoint).

`scoring_example.md` is the reference for the level of specificity expected.
Sanity check on the sample set: weak < medium < strong, and
`response_4_overpromise.md` must be flagged for contradicting the "no database
migration" constraint and an unrealistic 8-week timeline.

Judges test live with an **unseen** RFP/proposal pair — nothing may be tuned to
NordFrame specifically.

## Repository layout

```text
backend/    FastAPI (main.py) — call_ai() switches Gemini/Anthropic via .env
frontend/   React 18 + Vite (src/App.jsx is still the starter demo)
docs/challenge/   brief PDF + sample RFP/proposals
.claude/    shared plugins + project skill ui-build-verify
.mcp.json   shared MCP servers (chrome-devtools, playwright, context7, figma-talk)
```

Run: see `README.md`. Backend on :8000, frontend on :5173 (Vite proxies `/api`).

## UI work

Load the `ui-build-verify` skill for any change under `frontend/`. It covers the
Figma → code → Chrome screenshot loop and the screens the challenge needs.

## Conventions

- Branches: `feature/<short-name>`, `fix/<short-name>`; merge via Merge Request.
- Commit prefixes: `feat:` `fix:` `docs:` `refactor:` `test:` `chore:`.
- Never commit `backend/.env` or any API key. New config goes in
  `backend/.env.example`.
- Gemini key has a $100 team budget — develop on `gemini-2.0-flash`.
