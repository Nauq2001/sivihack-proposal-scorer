from __future__ import annotations


def test_removing_criterion_does_not_remove_requirements(rfp_text, base_criteria):
    from rfp_analyst.models import CriterionPacket, Requirement, RFPAnalysis
    from rfp_analyst.service import CriteriaState

    requirements = [
        Requirement(
            id="REQ-001",
            text="No database migration.",
            related_criterion="Scope & Deliverables Clarity",
            is_hard_constraint=True,
            source_section="Requirements",
            source_quote="Integration with our existing PostgreSQL database — no migration to a new database.",
        )
    ]
    analysis = RFPAnalysis(
        client_name="NordFrame Logistics GmbH",
        project_name="Warehouse Inventory Dashboard",
        detected_priority_note=None,
        requirements=requirements,
        suggested_criteria_weights=base_criteria,
        criterion_packets=[
            CriterionPacket(
                criterion_name=c.name,
                origin="base",
                evaluation_guidance=[],
                requirement_ids=[],
                source_refs=[],
                notes=[],
            )
            for c in base_criteria
        ],
    )
    state = CriteriaState.from_analysis(analysis, rfp_text)
    state.remove("Scope & Deliverables Clarity")
    scoring_input = state.package("Proposal text")
    assert scoring_input.rfp_analysis.requirements == requirements
    assert all(
        c.name != "Scope & Deliverables Clarity"
        for c in scoring_input.confirmed_criteria
    )


def test_package_rejects_empty_criteria(rfp_text, base_criteria):
    import pytest
    from rfp_analyst.models import CriterionPacket, RFPAnalysis
    from rfp_analyst.service import CriteriaState, StateError

    analysis = RFPAnalysis(
        client_name="NordFrame Logistics GmbH",
        project_name="Warehouse Inventory Dashboard",
        detected_priority_note=None,
        requirements=[],
        suggested_criteria_weights=base_criteria,
        criterion_packets=[
            CriterionPacket(
                criterion_name=c.name,
                origin="base",
                evaluation_guidance=[],
                requirement_ids=[],
                source_refs=[],
                notes=[],
            )
            for c in base_criteria
        ],
    )
    state = CriteriaState.from_analysis(analysis, rfp_text)
    for criterion in list(state.criteria):
        state.remove(criterion.name)
    with pytest.raises(StateError, match="NO_CONFIRMED_CRITERIA"):
        state.package("Proposal")


def test_state_snapshot_roundtrip_and_edit_preserve_user_change(rfp_text, base_criteria):
    from rfp_analyst.models import CriterionPacket, RFPAnalysis, UserCriterionInput
    from rfp_analyst.service import CriteriaState

    analysis = RFPAnalysis(
        client_name="NordFrame Logistics GmbH",
        project_name="Warehouse Inventory Dashboard",
        detected_priority_note=None,
        requirements=[],
        suggested_criteria_weights=base_criteria,
        criterion_packets=[
            CriterionPacket(
                criterion_name=c.name,
                origin="base",
                evaluation_guidance=[],
                requirement_ids=[],
                source_refs=[],
                notes=[],
            )
            for c in base_criteria
        ],
    )
    state = CriteriaState.from_analysis(analysis, rfp_text)
    state.add_or_merge(
        UserCriterionInput(name="Training", description="Train staff.", weight=2),
        resolver=None,
    )
    state.edit(
        "Training",
        UserCriterionInput(name="Training quality", description="Explain staff training quality.", weight=4),
        resolver=None,
    )
    restored = CriteriaState.from_snapshot(state.to_snapshot())
    custom = next(x for x in restored.criteria if x.name == "Training quality")
    assert custom.description == "Explain staff training quality."
    assert custom.weight == 4
    assert restored.revision == state.revision
