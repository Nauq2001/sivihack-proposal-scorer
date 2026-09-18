from __future__ import annotations


def test_duplicate_reuses_canonical_packet_and_replaces_weight(base_criteria):
    from rfp_analyst.criteria import resolve_user_criterion
    from rfp_analyst.models import CriterionPacket, UserCriterionInput

    existing = base_criteria
    packets = [
        CriterionPacket(
            criterion_name=c.name,
            origin="base",
            evaluation_guidance=["canonical guidance"],
            requirement_ids=[],
            source_refs=[],
            notes=[],
        )
        for c in existing
    ]
    result = resolve_user_criterion(
        UserCriterionInput(
            name="pricing clarity",
            description="Explain the price.",
            weight=3,
        ),
        existing,
        packets,
        requirements=[],
        raw_rfp_text="RFP",
        resolver=None,
    )
    assert result.is_duplicate is True
    assert result.criterion.name == "Pricing Clarity"
    assert result.criterion.description == next(
        x.description for x in existing if x.name == "Pricing Clarity"
    )
    assert result.criterion.weight == 3
    assert result.packet.evaluation_guidance == ["canonical guidance"]


def test_duplicate_without_weight_keeps_existing_weight(base_criteria):
    from rfp_analyst.criteria import resolve_user_criterion
    from rfp_analyst.models import CriterionPacket, UserCriterionInput

    pricing = next(x for x in base_criteria if x.name == "Pricing Clarity")
    pricing.weight = 4
    packet = CriterionPacket(
        criterion_name=pricing.name,
        origin="base",
        evaluation_guidance=[],
        requirement_ids=[],
        source_refs=[],
        notes=[],
    )
    result = resolve_user_criterion(
        UserCriterionInput(name="PRICING CLARITY", description="Price"),
        [pricing],
        [packet],
        [],
        "RFP",
        resolver=None,
    )
    assert result.criterion.weight == 4


def test_custom_outside_rfp_keeps_user_text_and_empty_links(base_criteria):
    from rfp_analyst.criteria import resolve_user_criterion
    from rfp_analyst.models import CriterionPacket, UserCriterionInput

    packets = [
        CriterionPacket(
            criterion_name=c.name,
            origin="base",
            evaluation_guidance=[],
            requirement_ids=[],
            source_refs=[],
            notes=[],
        )
        for c in base_criteria
    ]
    entered = UserCriterionInput(
        name="Training plan",
        description="Proposal includes warehouse staff training.",
        weight=2,
    )
    result = resolve_user_criterion(
        entered,
        base_criteria,
        packets,
        [],
        "RFP has no training requirement.",
        resolver=None,
    )
    assert result.is_duplicate is False
    assert result.criterion.name == entered.name
    assert result.criterion.description == entered.description
    assert result.packet.requirement_ids == []
    assert result.packet.source_refs == []
    assert result.packet.notes[0].startswith("USER_DEFINED_NOT_RFP")


def test_semantic_duplicate_uses_existing_content_and_user_weight(base_criteria):
    from rfp_analyst.criteria import resolve_user_criterion
    from rfp_analyst.models import CriterionPacket, UserCriterionInput
    from test_analyst import CountingRunnable

    packets = [
        CriterionPacket(
            criterion_name=c.name,
            origin="base",
            evaluation_guidance=["standard"],
            requirement_ids=[],
            source_refs=[],
            notes=[],
        )
        for c in base_criteria
    ]
    resolver = CountingRunnable(
        {
            "duplicate_criterion_name": "Pricing Clarity",
            "evaluation_guidance": [],
            "requirement_ids": [],
            "source_refs": [],
            "notes": [],
        }
    )
    result = resolve_user_criterion(
        UserCriterionInput(
            name="Commercial price transparency",
            description="Make all pricing clear.",
            weight=5,
        ),
        base_criteria,
        packets,
        [],
        "RFP",
        resolver,
    )
    assert resolver.calls == 1
    assert result.is_duplicate is True
    assert result.criterion.name == "Pricing Clarity"
    assert result.criterion.weight == 5


def test_invalid_enrichment_links_are_removed(base_criteria):
    from rfp_analyst.criteria import resolve_user_criterion
    from rfp_analyst.models import CriterionPacket, Requirement, UserCriterionInput
    from test_analyst import CountingRunnable

    packets = [
        CriterionPacket(
            criterion_name=c.name,
            origin="base",
            evaluation_guidance=[],
            requirement_ids=[],
            source_refs=[],
            notes=[],
        )
        for c in base_criteria
    ]
    requirements = [
        Requirement(
            id="REQ-001",
            text="Support terms.",
            related_criterion="Scope & Deliverables Clarity",
            is_hard_constraint=False,
            source_section="Requirements",
            source_quote="Support terms after go-live.",
        )
    ]
    resolver = CountingRunnable(
        {
            "duplicate_criterion_name": None,
            "evaluation_guidance": ["Assess training."],
            "requirement_ids": ["REQ-999"],
            "source_refs": [{"source_section": "Fake", "quote": "fabricated"}],
            "notes": [],
        }
    )
    result = resolve_user_criterion(
        UserCriterionInput(name="Training", description="Train warehouse staff."),
        base_criteria,
        packets,
        requirements,
        "Support terms after go-live.",
        resolver,
    )
    assert result.packet.requirement_ids == []
    assert result.packet.source_refs == []
    assert result.packet.notes[0].startswith("USER_DEFINED_NOT_RFP")
