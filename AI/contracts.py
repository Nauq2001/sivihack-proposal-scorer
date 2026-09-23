"""Shared Pydantic contract between RFP Analyst and Proposal Analyst (Scoring Agent).

Locked v1.1 — see docs/architecture.md "Output schemas". Both agents should import
these models directly instead of redefining them, so schema drift (field
renames, criterion-name typos) fails fast at parse time instead of silently
at runtime.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

# Character-for-character canonical — used as RAG static-lookup dict keys.
# NOTE: #5 has no period after "vs" — this deliberately matches the RFP
# Analyst package's models.py/config.py/prompts.py (agent/src/rfp_analyst/),
# not the Appendix A brief text ("vs."). The agent-side spelling is baked
# into a Literal type, base criteria list, prompt text, its JSON schema, and
# two fixtures — changing it there would ripple through tested code, so this
# side conforms instead. If you ever see "Completeness vs. RFP Requirements"
# (with period) coming from RFP Analyst output, that's the bug to fix there.
BASE_CRITERIA: tuple[str, ...] = (
    "Problem Understanding",
    "Scope & Deliverables Clarity",
    "Pricing Clarity",
    "Timeline Clarity",
    "Completeness vs RFP Requirements",
    "Tone & Persuasiveness",
    "Risk/Assumptions Transparency",
)

STATUS_VALUES = ("met", "missing", "vague", "contradicted")
SEVERITY_VALUES = ("high", "medium", "low")
ORIGIN_VALUES = ("base", "rfp_explicit", "ai_inferred", "user")
RECOMMENDED_PRIORITY_VALUES = ("high", "medium", "low")


class CriterionWeight(BaseModel):
    name: str
    description: str
    weight: float = Field(gt=0)
    # FE-only display hint from RFP Analyst (agent/src/rfp_analyst/priority.py)
    # — high: linked to a hard-constraint requirement, medium: linked to any
    # requirement, low: no direct link. Never used by Scoring Agent to adjust
    # a score; kept here only so it round-trips instead of being dropped.
    recommended_priority: str = "medium"
    priority_reason: str = "No direct RFP requirement is linked."

    @field_validator("recommended_priority")
    @classmethod
    def _check_recommended_priority(cls, v: str) -> str:
        if v not in RECOMMENDED_PRIORITY_VALUES:
            raise ValueError(
                f"recommended_priority must be one of {RECOMMENDED_PRIORITY_VALUES}, got {v!r}"
            )
        return v


class SourceRef(BaseModel):
    source_section: str
    quote: str


class CriterionPacket(BaseModel):
    criterion_name: str
    origin: str
    evaluation_guidance: list[str] = Field(default_factory=list)
    # Authoritative grouping for scoring — Proposal Analyst joins findings to a
    # criterion via this list, not by filtering Requirement.related_criterion.
    requirement_ids: list[str] = Field(default_factory=list)
    source_refs: list[SourceRef] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @field_validator("origin")
    @classmethod
    def _check_origin(cls, v: str) -> str:
        if v not in ORIGIN_VALUES:
            raise ValueError(f"origin must be one of {ORIGIN_VALUES}, got {v!r}")
        return v


class Requirement(BaseModel):
    id: str
    text: str
    source_section: str
    source_quote: str
    related_criterion: str
    is_hard_constraint: bool

    @field_validator("related_criterion")
    @classmethod
    def _check_related_criterion(cls, v: str) -> str:
        if v not in BASE_CRITERIA:
            raise ValueError(
                f"related_criterion must match one of {BASE_CRITERIA!r} "
                f"character-for-character, got {v!r}"
            )
        return v


class RFPAnalysis(BaseModel):
    client_name: str
    project_name: str
    requirements: list[Requirement]
    suggested_criteria_weights: list[CriterionWeight] | None = None
    criterion_packets: list[CriterionPacket] = Field(default_factory=list)
    detected_priority_note: str | None = None


class ScoringInput(BaseModel):
    rfp_analysis: RFPAnalysis
    raw_rfp_text: str
    raw_proposal_text: str
    confirmed_criteria: list[CriterionWeight]


class RequirementFinding(BaseModel):
    requirement_id: str
    status: str
    severity: str
    reason: str
    citation: str = ""
    suggested_patch: str = ""

    @field_validator("status")
    @classmethod
    def _check_status(cls, v: str) -> str:
        if v not in STATUS_VALUES:
            raise ValueError(f"status must be one of {STATUS_VALUES}, got {v!r}")
        return v

    @field_validator("severity")
    @classmethod
    def _check_severity(cls, v: str) -> str:
        if v not in SEVERITY_VALUES:
            raise ValueError(f"severity must be one of {SEVERITY_VALUES}, got {v!r}")
        return v


class CriterionScore(BaseModel):
    name: str
    score: int = Field(ge=1, le=5)
    comment: str
    citations: list[str] = Field(default_factory=list)


class ProposalAnalystOutput(BaseModel):
    """Raw shape the LLM must return. overall_score/client_name/project_name
    are filled in by score_proposal() afterwards, never by the model."""

    findings: list[RequirementFinding]
    criteria: list[CriterionScore]
    verdict: str


class ScoringResult(BaseModel):
    client_name: str
    project_name: str
    findings: list[RequirementFinding]
    criteria: list[CriterionScore]
    overall_score: float
    verdict: str
