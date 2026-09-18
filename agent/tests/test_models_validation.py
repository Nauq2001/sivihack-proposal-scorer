from __future__ import annotations

import pytest
from pydantic import ValidationError
from pathlib import Path


def test_user_criterion_requires_nonempty_name_and_description():
    from rfp_analyst.models import UserCriterionInput

    with pytest.raises(ValidationError):
        UserCriterionInput(name=" ", description="Useful", weight=1)
    with pytest.raises(ValidationError):
        UserCriterionInput(name="Useful", description=" ", weight=1)


def test_weight_must_be_positive_and_finite():
    from rfp_analyst.models import CriterionWeight

    for invalid in (0, -1, float("inf"), float("nan")):
        with pytest.raises(ValidationError):
            CriterionWeight(name="Test", description="Meaning", weight=invalid)


def test_analysis_rejects_fabricated_quote(rfp_text, base_criteria):
    from rfp_analyst.models import CriterionPacket, Requirement, RFPAnalysis
    from rfp_analyst.validation import ContractError, validate_analysis

    analysis = RFPAnalysis(
        client_name="NordFrame Logistics GmbH",
        project_name="Warehouse Inventory Dashboard",
        detected_priority_note=None,
        requirements=[
            Requirement(
                id="REQ-001",
                text="No database migration.",
                related_criterion="Scope & Deliverables Clarity",
                is_hard_constraint=True,
                source_section="Requirements",
                source_quote="not in the source",
            )
        ],
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
    with pytest.raises(ContractError, match="QUOTE_NOT_FOUND"):
        validate_analysis(analysis, rfp_text)


def test_analysis_requires_one_packet_per_criterion(rfp_text, base_criteria):
    from rfp_analyst.models import RFPAnalysis
    from rfp_analyst.validation import ContractError, validate_analysis

    analysis = RFPAnalysis(
        client_name="NordFrame Logistics GmbH",
        project_name="Warehouse Inventory Dashboard",
        detected_priority_note=None,
        requirements=[],
        suggested_criteria_weights=base_criteria,
        criterion_packets=[],
    )
    with pytest.raises(ContractError, match="PACKET_MISMATCH"):
        validate_analysis(analysis, rfp_text)


def test_bundled_scoring_fixture_matches_runtime_contract():
    from rfp_analyst.models import ScoringInput

    project = Path(__file__).resolve().parents[1]
    payload = (project / "fixtures/nordframe-scoring-input.example.json").read_text(
        encoding="utf-8"
    )
    parsed = ScoringInput.model_validate_json(payload)
    assert parsed.rfp_analysis.client_name == "NordFrame Logistics GmbH"
    assert len(parsed.rfp_analysis.requirements) == 19
    assert len(parsed.confirmed_criteria) == 8
