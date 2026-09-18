"""Client for the n8n "Jira ticket + Slack" automation workflow.

Not part of scoring — a separate, user-triggered action fired from the
Frontend's "Send to Work" button (see docs/api/review-contract.md), never
called automatically from score_proposal(). n8n owns the actual Jira/Slack
steps; this module only POSTs a trimmed ScoringResult to n8n's Webhook node
and returns whatever the workflow answers with.
"""

from __future__ import annotations

import requests

# Keeps the Jira ticket readable — only material issues matter for a review ticket.
_MAX_FINDINGS = 20


class N8nWorkflowError(RuntimeError):
    """The n8n workflow could not be reached, or answered with an error."""


def _flagged_findings(findings: list[dict]) -> list[dict]:
    return [
        {
            "requirement_id": f.get("requirement_id"),
            "status": f.get("status"),
            "severity": f.get("severity"),
            "reason": f.get("reason"),
            "suggested_patch": f.get("suggested_patch"),
        }
        for f in findings
        if f.get("severity") != "low"
    ][:_MAX_FINDINGS]


def send_to_jira_slack_workflow(scoring: dict, webhook_url: str, timeout: float = 15.0) -> dict:
    """POST a trimmed ScoringResult to n8n's webhook; n8n creates a Jira issue
    and posts to Slack. Returns the workflow's JSON response — expected shape
    {"ticket_key": "...", "ticket_url": "..."}, but this is n8n's contract to
    define, not validated here.
    """
    payload = {
        "client_name": scoring.get("client_name", ""),
        "project_name": scoring.get("project_name", ""),
        "overall_score": scoring.get("overall_score"),
        "verdict": scoring.get("verdict", ""),
        "criteria": [
            {"name": c.get("name"), "score": c.get("score"), "comment": c.get("comment")}
            for c in scoring.get("criteria", [])
        ],
        "flagged_findings": _flagged_findings(scoring.get("findings", [])),
    }
    try:
        response = requests.post(webhook_url, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        raise N8nWorkflowError(f"Could not reach the n8n workflow: {exc}") from exc
    if not response.ok:
        raise N8nWorkflowError(f"n8n workflow returned {response.status_code}: {response.text[:500]}")
    try:
        return response.json()
    except ValueError as exc:
        raise N8nWorkflowError(f"n8n workflow did not return JSON: {response.text[:500]}") from exc
