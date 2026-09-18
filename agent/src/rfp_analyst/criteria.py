from __future__ import annotations

from copy import deepcopy
from typing import Any

from .models import (
    CriterionPacket,
    CriterionResolutionDraft,
    CriterionWeight,
    Requirement,
    ResolvedCriterion,
    UserCriterionInput,
)
from .prompts import build_resolution_messages


def _normalize(value: str) -> str:
    return " ".join(value.casefold().split())


def _existing_duplicate(
    name: str, criteria: list[CriterionWeight]
) -> CriterionWeight | None:
    normalized = _normalize(name)
    return next((item for item in criteria if _normalize(item.name) == normalized), None)


def _duplicate_result(
    existing: CriterionWeight,
    packets: list[CriterionPacket],
    requested_weight: float | None,
) -> ResolvedCriterion:
    criterion = deepcopy(existing)
    if requested_weight is not None:
        criterion.weight = requested_weight
    packet = deepcopy(next(item for item in packets if item.criterion_name == existing.name))
    return ResolvedCriterion(criterion=criterion, packet=packet, is_duplicate=True)


def resolve_user_criterion(
    user_input: UserCriterionInput,
    criteria: list[CriterionWeight],
    packets: list[CriterionPacket],
    requirements: list[Requirement],
    raw_rfp_text: str,
    resolver: Any | None,
) -> ResolvedCriterion:
    exact = _existing_duplicate(user_input.name, criteria)
    if exact is not None:
        return _duplicate_result(exact, packets, user_input.weight)

    draft: CriterionResolutionDraft | None = None
    if resolver is not None:
        try:
            raw = resolver.invoke(
                build_resolution_messages(user_input, criteria, packets, requirements, raw_rfp_text)
            )
            draft = raw if isinstance(raw, CriterionResolutionDraft) else CriterionResolutionDraft.model_validate(raw)
            if draft.duplicate_criterion_name:
                duplicate = next(
                    (item for item in criteria if item.name == draft.duplicate_criterion_name),
                    None,
                )
                if duplicate is not None:
                    return _duplicate_result(duplicate, packets, user_input.weight)
            valid_ids = {item.id for item in requirements}
            draft.requirement_ids = [item for item in draft.requirement_ids if item in valid_ids]
            draft.source_refs = [item for item in draft.source_refs if item.quote in raw_rfp_text]
        except Exception:
            draft = None

    weight = user_input.weight if user_input.weight is not None else 1.0
    criterion = CriterionWeight(
        name=user_input.name,
        description=user_input.description,
        weight=weight,
    )
    if draft is None:
        guidance = [f"Evaluate only this user-defined expectation: {user_input.description}"]
        requirement_ids: list[str] = []
        source_refs = []
        notes = [
            "USER_DEFINED_NOT_RFP: Score against the user's description; do not report it as a missing RFP requirement.",
            "ENRICHMENT_FAILED: No verified RFP links were added; do not invent thresholds or obligations.",
        ]
    else:
        guidance = draft.evaluation_guidance
        requirement_ids = draft.requirement_ids
        source_refs = draft.source_refs
        notes = draft.notes
        if not source_refs and not any(note.startswith("USER_DEFINED_NOT_RFP") for note in notes):
            notes.append(
                "USER_DEFINED_NOT_RFP: No direct RFP source was verified; score against the user's description."
            )
    packet = CriterionPacket(
        criterion_name=criterion.name,
        origin="user",
        evaluation_guidance=guidance,
        requirement_ids=requirement_ids,
        source_refs=source_refs,
        notes=notes,
    )
    return ResolvedCriterion(criterion=criterion, packet=packet, is_duplicate=False)


def create_gemini_resolution_model(model_name: str = "gemini-3.8-flash"):
    from langchain_google_genai import ChatGoogleGenerativeAI

    model = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=1.0,
        timeout=60,
        max_retries=2,
    )
    return model.with_structured_output(
        schema=CriterionResolutionDraft.model_json_schema(), method="json_schema"
    )

