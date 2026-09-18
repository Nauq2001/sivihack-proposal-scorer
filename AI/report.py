"""Render a ScoringResult as scoring_example.md-style markdown.

Not consumed by Backend/Frontend — a convenience for demos and human review,
so raw JSON output can be eyeballed against the target format/tone described
in docs/challenge/sample_data/scoring_example.md.
"""

from __future__ import annotations

from AI.contracts import ScoringInput, ScoringResult

_STATUS_LABEL = {
    "missing": "❌ Missing",
    "vague": "⚠️ Vague",
    "contradicted": "🚫 Contradicted",
}


def _verdict_label(score: float) -> str:
    if score < 2:
        return "Needs significant revision before sending."
    if score < 3.5:
        return "Needs revision before sending."
    if score < 4.5:
        return "Good — minor revisions suggested."
    return "Ready to send."


def render_markdown(scoring_input: ScoringInput, result: ScoringResult) -> str:
    requirements_by_id = {r.id: r for r in scoring_input.rfp_analysis.requirements}

    lines = [f"# Scoring: {result.project_name} — {result.client_name}", ""]

    lines.append("## Level 1 — Rubric scores")
    lines.append("")
    lines.append("| Criterion | Score (1-5) | Comment |")
    lines.append("|---|---|---|")
    for c in result.criteria:
        lines.append(f"| {c.name} | {c.score} | {c.comment} |")
    lines.append("")
    lines.append(f"**Overall: {result.overall_score} / 5 — {_verdict_label(result.overall_score)}**")
    lines.append("")

    lines.append("## Level 2 — RFP comparison + suggested fixes")
    lines.append("")
    issues = [f for f in result.findings if f.status != "met"]
    if not issues:
        lines.append("No gaps found against the RFP.")
    for f in issues:
        req = requirements_by_id.get(f.requirement_id)
        label = _STATUS_LABEL.get(f.status, f.status)
        title = req.text if req else f.requirement_id
        lines.append(f"> {label}: **{title}**")
        lines.append(f"> {f.reason}")
        if f.citation:
            lines.append(f'> Proposal: "{f.citation}"')
        if f.suggested_patch:
            lines.append(f"> **Suggested fix:** {f.suggested_patch}")
        lines.append(">")
        lines.append("")

    if scoring_input.rfp_analysis.detected_priority_note:
        lines.append("## Level 3 — Detected client priority")
        lines.append("")
        lines.append(f"> {scoring_input.rfp_analysis.detected_priority_note}")
        lines.append("> *(User confirms/adjusts this before scoring proceeds.)*")
        lines.append("")

    lines.append("## Verdict")
    lines.append("")
    lines.append(result.verdict)

    return "\n".join(lines)
