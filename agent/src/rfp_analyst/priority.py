from __future__ import annotations

from .models import CriterionPacket, CriterionWeight, Requirement


def apply_priority_recommendations(
    criteria: list[CriterionWeight],
    packets: list[CriterionPacket],
    requirements: list[Requirement],
) -> None:
    """Add a lightweight, explainable display recommendation for each criterion."""
    requirement_by_id = {item.id: item for item in requirements}
    packet_by_name = {item.criterion_name: item for item in packets}

    for criterion in criteria:
        packet = packet_by_name.get(criterion.name)
        linked = [
            requirement_by_id[requirement_id]
            for requirement_id in (packet.requirement_ids if packet else [])
            if requirement_id in requirement_by_id
        ]
        hard = next((item for item in linked if item.is_hard_constraint), None)
        if hard:
            criterion.recommended_priority = "high"
            criterion.priority_reason = f"Contains hard RFP requirement {hard.id}."
        elif linked:
            criterion.recommended_priority = "medium"
            criterion.priority_reason = f"Addresses {len(linked)} linked RFP requirement(s)."
        else:
            criterion.recommended_priority = "low"
            criterion.priority_reason = "No direct RFP requirement is linked."
