from __future__ import annotations

import math
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


CanonicalCriterionName = Literal[
    "Problem Understanding",
    "Scope & Deliverables Clarity",
    "Pricing Clarity",
    "Timeline Clarity",
    "Completeness vs RFP Requirements",
    "Tone & Persuasiveness",
    "Risk/Assumptions Transparency",
]
Origin = Literal["base", "rfp_explicit", "ai_inferred", "user"]
NonEmpty = Annotated[str, Field(min_length=1)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CriterionWeight(StrictModel):
    name: NonEmpty
    description: NonEmpty
    weight: float = 1.0

    @field_validator("name", "description")
    @classmethod
    def nonblank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("weight")
    @classmethod
    def positive_finite(cls, value: float) -> float:
        if not math.isfinite(value) or value <= 0:
            raise ValueError("weight must be finite and greater than zero")
        return value


class UserCriterionInput(StrictModel):
    name: NonEmpty
    description: NonEmpty
    weight: float | None = None

    @field_validator("name", "description")
    @classmethod
    def nonblank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("weight")
    @classmethod
    def positive_finite(cls, value: float | None) -> float | None:
        if value is not None and (not math.isfinite(value) or value <= 0):
            raise ValueError("weight must be finite and greater than zero")
        return value


class SourceRef(StrictModel):
    source_section: NonEmpty
    quote: NonEmpty


class Requirement(StrictModel):
    id: str = Field(pattern=r"^REQ-[0-9]{3,}$")
    text: NonEmpty
    related_criterion: CanonicalCriterionName
    is_hard_constraint: bool
    source_section: NonEmpty
    source_quote: NonEmpty


class ExtractedRequirement(StrictModel):
    text: NonEmpty
    related_criterion: CanonicalCriterionName
    is_hard_constraint: bool
    source_section: NonEmpty
    source_quote: NonEmpty


class WeightSuggestion(StrictModel):
    criterion_name: CanonicalCriterionName
    weight: float

    @field_validator("weight")
    @classmethod
    def positive_finite(cls, value: float) -> float:
        if not math.isfinite(value) or value <= 0:
            raise ValueError("weight must be finite and greater than zero")
        return value


class CriterionPacket(StrictModel):
    criterion_name: NonEmpty
    origin: Origin
    evaluation_guidance: list[str] = Field(default_factory=list)
    requirement_ids: list[str] = Field(default_factory=list)
    source_refs: list[SourceRef] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class RFPAnalysis(StrictModel):
    client_name: str
    project_name: str
    detected_priority_note: str | None
    requirements: list[Requirement]
    suggested_criteria_weights: list[CriterionWeight]
    criterion_packets: list[CriterionPacket]


class AnalysisDraft(StrictModel):
    client_name: str
    project_name: str
    detected_priority_note: str | None
    requirements: list[ExtractedRequirement]
    suggested_weights: list[WeightSuggestion] = Field(default_factory=list)
    custom_criteria: list[CriterionWeight] = Field(default_factory=list)
    criterion_packets: list[CriterionPacket] = Field(default_factory=list)


class CriterionResolutionDraft(StrictModel):
    duplicate_criterion_name: str | None = None
    evaluation_guidance: list[str] = Field(default_factory=list)
    requirement_ids: list[str] = Field(default_factory=list)
    source_refs: list[SourceRef] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ResolvedCriterion(StrictModel):
    criterion: CriterionWeight
    packet: CriterionPacket
    is_duplicate: bool


class ScoringInput(StrictModel):
    rfp_analysis: RFPAnalysis
    raw_rfp_text: NonEmpty
    raw_proposal_text: NonEmpty
    confirmed_criteria: list[CriterionWeight] = Field(min_length=1)


class CriteriaStateSnapshot(StrictModel):
    revision: int = Field(ge=1)
    raw_rfp_text: NonEmpty
    analysis: RFPAnalysis
    confirmed_criteria: list[CriterionWeight]
    criterion_packets: list[CriterionPacket]
