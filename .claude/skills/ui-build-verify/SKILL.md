---
name: ui-build-verify
description: Build or change a screen of the Proposal Scorer frontend and verify it in a real browser. Use for any UI work in frontend/ — new screens, restyling, implementing a Figma frame, or checking that a UI change actually renders and works with the sample RFP/proposals.
---

# Build and verify a Proposal Scorer UI change

The same loop the team used on TeachOnce: design reference → code → look at it in
Chrome → fix → repeat. Never report a UI change as done without having seen it
render.

## 1. Get the design reference

- **Figma link given** → `get_design_context`, `get_screenshot` and
  `get_variable_defs` (claude.ai Figma connector) on the node. Use the variables
  as CSS custom properties, not hard-coded hex values.
- **No Figma** → load the `frontend-design:frontend-design` skill and pick an
  aesthetic direction before writing CSS. The audience is sales / pre-sales staff
  at FPT Software Europe: calm, professional, dense information that stays
  scannable.
- **Library API questions** (React, Vite, a chart lib) → query `context7`, do not
  answer from memory.

## 2. Build

- Stack: React 18 + Vite in `frontend/`. Keep it framework-free unless the team
  agrees otherwise; put design tokens in one CSS file as `:root` variables.
- Screens the challenge needs (see `docs/challenge/`):
  1. **Input** — paste or upload RFP + proposal (Markdown; PDF is the bonus).
  2. **Criteria config** — base rubric from Appendix A, adjustable weights,
     add/remove, optional "AI-suggested priorities" from the RFP.
  3. **Results** — overall score, per-criterion score + comment, requirement
     coverage list (addressed / vague / missing), suggested fix per issue, and a
     citation to the RFP section and proposal section for every claim.
- Loading state must stream or show progress: judges watch it run live.
- Design every state: empty, loading, error (backend down, AI quota), result.

## 3. Verify in the browser

1. Start backend (`uvicorn main:app --reload --port 8000` in `backend/`) and
   frontend (`npm run dev` in `frontend/`) in the background.
2. `chrome-devtools`: `new_page` → `http://localhost:5173`.
3. Run the real flow with `docs/challenge/sample_data/rfp_nordframe.md` and at
   least `response_1_weak.md` and `response_3_strong.md` — the weak one must
   score clearly lower than the strong one.
4. `take_screenshot` at desktop width, then `resize_page` to 390px wide and
   screenshot again. No horizontal scroll.
5. `list_console_messages` — zero errors.
6. Compare against the Figma screenshot if there is one; fix and repeat.

Use `playwright` instead when a repeatable scripted check is more useful than an
interactive look (e.g. upload flow regression).

## 4. Hand off

Report what changed, attach the screenshot(s), and list anything not verified.
