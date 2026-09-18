from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from .config import base_criteria, base_packets
from .models import AnalysisDraft, Requirement, RFPAnalysis
from .prompts import build_analysis_messages
from .validation import reconcile_quote, validate_analysis


class AnalystError(RuntimeError):
    pass


def analyze_rfp(raw_rfp_text: str, structured_model: Any) -> RFPAnalysis:
    if not raw_rfp_text.strip():
        raise AnalystError("EMPTY_RFP")
    try:
        raw = structured_model.invoke(build_analysis_messages(raw_rfp_text))
        draft = raw if isinstance(raw, AnalysisDraft) else AnalysisDraft.model_validate(raw)
    except Exception as exc:
        raise AnalystError(f"MODEL_OUTPUT_INVALID: {exc}") from exc

    # The decision deadline belongs to client context, not the vendor's obligations.
    extracted_requirements = [
        item
        for item in draft.requirements
        if "decision date" not in item.source_section.casefold()
    ]
    requirements = [
        Requirement(
            id=f"REQ-{index:03d}",
            **{
                **item.model_dump(),
                "source_quote": reconcile_quote(item.source_quote, raw_rfp_text),
                "is_hard_constraint": bool(
                    re.search(
                        r"\b(no|only|must not|shall not|cannot|without)\b",
                        f"{item.text} {item.source_quote}",
                        re.IGNORECASE,
                    )
                ),
            },
        )
        for index, item in enumerate(extracted_requirements, start=1)
    ]
    criteria = base_criteria()
    suggested_weight_by_name = {
        suggestion.criterion_name: suggestion.weight for suggestion in draft.suggested_weights
    }
    for criterion in criteria:
        if criterion.name in suggested_weight_by_name:
            criterion.weight = suggested_weight_by_name[criterion.name]
    criteria.extend(deepcopy(draft.custom_criteria))

    packets = base_packets()
    by_name = {packet.criterion_name: packet for packet in packets}
    custom_names = {criterion.name for criterion in draft.custom_criteria}
    for packet in draft.criterion_packets:
        if packet.criterion_name in custom_names:
            by_name[packet.criterion_name] = deepcopy(packet)
    packets = [by_name[criterion.name] for criterion in criteria if criterion.name in by_name]
    for criterion in criteria:
        if criterion.name not in {packet.criterion_name for packet in packets}:
            packets.append(
                type(base_packets()[0])(
                    criterion_name=criterion.name,
                    origin="ai_inferred",
                    evaluation_guidance=[],
                    requirement_ids=[],
                    source_refs=[],
                    notes=["INSUFFICIENT_DETAIL: Use only the criterion description; do not invent requirements."],
                )
            )

    requirement_ids_by_criterion: dict[str, list[str]] = {}
    for requirement in requirements:
        requirement_ids_by_criterion.setdefault(requirement.related_criterion, []).append(requirement.id)
    all_requirement_ids = [item.id for item in requirements]
    for packet in packets:
        if packet.origin == "base":
            if packet.criterion_name == "Completeness vs RFP Requirements":
                packet.requirement_ids = all_requirement_ids
            else:
                packet.requirement_ids = requirement_ids_by_criterion.get(packet.criterion_name, [])

    analysis = RFPAnalysis(
        client_name=draft.client_name.strip(),
        project_name=draft.project_name.strip(),
        detected_priority_note=draft.detected_priority_note,
        requirements=requirements,
        suggested_criteria_weights=criteria,
        criterion_packets=packets,
    )
    validate_analysis(analysis, raw_rfp_text)
    return analysis


def create_gemini_analysis_model(model_name: str = "gemini-3.8-flash"):
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError as exc:
        raise AnalystError("Install project dependencies before live analysis") from exc
    model = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=1.0,
        timeout=60,
        max_retries=2,
    )
    return model.with_structured_output(
        schema=AnalysisDraft.model_json_schema(), method="json_schema"
    )
