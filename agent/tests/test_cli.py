from __future__ import annotations

import json


def test_validate_command_accepts_fixture(tmp_path, capsys, rfp_text, base_criteria):
    from rfp_analyst.cli import main
    from rfp_analyst.models import CriterionPacket, RFPAnalysis

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
    analysis_path = tmp_path / "analysis.json"
    rfp_path = tmp_path / "rfp.md"
    analysis_path.write_text(analysis.model_dump_json(indent=2), encoding="utf-8")
    rfp_path.write_text(rfp_text, encoding="utf-8")
    assert main(["validate", "--analysis", str(analysis_path), "--rfp", str(rfp_path)]) == 0
    assert "VALID" in capsys.readouterr().out


def test_package_command_writes_scoring_contract(tmp_path, rfp_text, base_criteria):
    from rfp_analyst.cli import main
    from rfp_analyst.models import CriterionPacket, RFPAnalysis
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
    state_path = tmp_path / "state.json"
    proposal_path = tmp_path / "proposal.md"
    output_path = tmp_path / "scoring.json"
    state_path.write_text(state.to_snapshot().model_dump_json(indent=2), encoding="utf-8")
    proposal_path.write_text("A concrete proposal.", encoding="utf-8")
    assert main([
        "package", "--state", str(state_path), "--proposal", str(proposal_path),
        "--output", str(output_path),
    ]) == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["rfp_analysis"]["client_name"] == "NordFrame Logistics GmbH"
    assert len(payload["confirmed_criteria"]) == 7


def test_schema_command_exports_scoring_input_schema(tmp_path):
    from rfp_analyst.cli import main

    output = tmp_path / "schema.json"
    assert main(["schema", "--output", str(output)]) == 0
    schema = json.loads(output.read_text(encoding="utf-8"))
    assert schema["title"] == "ScoringInput"
    assert "rfp_analysis" in schema["properties"]
