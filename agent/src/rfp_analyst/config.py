from __future__ import annotations

from .models import CriterionPacket, CriterionWeight


_BASE = [
    (
        "Problem Understanding",
        "Shows understanding of the client's operational problem and intended outcome.",
        "Connect the proposed approach to the client's operational problem and outcomes in the RFP context.",
    ),
    (
        "Scope & Deliverables Clarity",
        "Explains what will be delivered, its boundaries, and how it will work.",
        "Check whether deliverables and their scope are specific enough to understand what is included.",
    ),
    (
        "Pricing Clarity",
        "Makes pricing, inclusions, and commercial assumptions understandable.",
        "Check whether costs, inclusions, and pricing assumptions are clear.",
    ),
    (
        "Timeline Clarity",
        "Explains delivery milestones and their timing.",
        "Check whether milestones and their timing are explicit and distinguishable.",
    ),
    (
        "Completeness vs RFP Requirements",
        "Evaluates whether the proposal addresses the RFP requirements and constraints.",
        "Use all requirement findings when judging completeness, regardless of each requirement's primary criterion.",
    ),
    (
        "Tone & Persuasiveness",
        "Evaluates clear, credible, and client-specific communication.",
        "Read the proposal directly for client specificity, credibility, and unsupported claims.",
    ),
    (
        "Risk/Assumptions Transparency",
        "Explains relevant dependencies, limitations, assumptions, and delivery risks.",
        "Check whether meaningful assumptions, limitations, dependencies, and risks are disclosed.",
    ),
]


def base_criteria() -> list[CriterionWeight]:
    return [CriterionWeight(name=name, description=description, weight=1) for name, description, _ in _BASE]


def base_packets() -> list[CriterionPacket]:
    return [
        CriterionPacket(
            criterion_name=name,
            origin="base",
            evaluation_guidance=[guidance],
            requirement_ids=[],
            source_refs=[],
            notes=[],
        )
        for name, _, guidance in _BASE
    ]

