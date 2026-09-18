"""
Hai route noi hai agent lai voi nhau, theo CLAUDE.md muc "Interface contract".

    POST /api/analyze-rfp   RFP Analyst  -> rfp_analysis + confirmed_criteria
    POST /api/score         Proposal Analyst -> scoring

Lop nay khong chua logic cham diem. No chi:
  - nap duoc package AI/ va agent/src tu thu muc backend/
  - goi ham co san, doi loi thanh HTTP cho nguoi dung doc duoc
  - them hai thu frontend can ma contract chua co: `short_label` cho tung yeu cau
    va `recommendation` cho ket qua (xem ghi chu o duoi)
"""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(tags=["review"])

# AI/ va agent/src nam ngoai thu muc backend, them vao duong dan import.
ROOT = Path(__file__).resolve().parent.parent
for path in (ROOT, ROOT / "agent" / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


class AnalyzeRequest(BaseModel):
    raw_rfp_text: str


def _short_labels(requirements: list[Any]) -> list[str]:
    """Nhan ngan cho dai phu yeu cau, toi da ~14 ky tu.

    `source_section` khac nhau tuy model: co ban tra "Requirements / 3", co ban
    chi tra "Requirements". Nen danh so trong tung muc de khong bi trung nhan.
    """
    counts: dict[str, int] = {}
    for r in requirements:
        section = (getattr(r, "source_section", "") or "Requirement").strip()
        counts[section] = counts.get(section, 0) + 1

    seen: dict[str, int] = {}
    labels: list[str] = []
    for r in requirements:
        section = (getattr(r, "source_section", "") or "Requirement").strip()
        numbered = re.search(r"(\d+)\s*$", section)
        base = re.sub(r"\s*/?\s*\d+\s*$", "", section) or "Requirement"
        short = "Req" if base.lower().startswith("requirement") else base[:9]
        if numbered:
            labels.append(f"{short} {numbered.group(1)}")
        elif counts[section] == 1:
            labels.append(base[:14])
        else:
            seen[section] = seen.get(section, 0) + 1
            labels.append(f"{short} {seen[section]}")
    return labels


def _origin_by_criterion(packets: list[Any]) -> dict[str, str]:
    return {p.criterion_name: p.origin for p in packets}


def _recommendation(result: Any, requirements: list[Any]) -> str:
    """Khuyen nghi cuoi cung — tinh bang code, khong hoi LLM.

    Theo `rubric.json` cua benchmark: vi pham mot rang buoc cung thi khong the
    khuyen nghi gui di, du diem trung binh co cao.
    """
    hard = {r.id for r in requirements if getattr(r, "is_hard_constraint", False)}
    for finding in result.findings:
        if finding.status == "contradicted" and finding.requirement_id in hard:
            return "do_not_accept_as_written"
    if any(f.status == "contradicted" for f in result.findings):
        return "do_not_accept_as_written"
    return "ready" if result.overall_score >= 4 else "revise"


def _dump(model: Any) -> dict[str, Any]:
    return model.model_dump() if hasattr(model, "model_dump") else dict(model)


@router.post("/api/analyze-rfp")
def analyze_rfp_route(req: AnalyzeRequest) -> dict[str, Any]:
    if len(req.raw_rfp_text.strip()) < 40:
        raise HTTPException(status_code=400, detail="RFP text is too short to analyse.")

    try:
        from rfp_analyst.analyst import AnalystError, analyze_rfp, create_gemini_analysis_model
        from rfp_analyst.service import CriteriaState
    except ImportError as exc:  # pragma: no cover
        raise HTTPException(status_code=503, detail=f"RFP Analyst is not installed: {exc}") from exc

    import os

    model_name = os.getenv("RFP_ANALYST_MODEL") or os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    attempts = int(os.getenv("RFP_ANALYST_ATTEMPTS", "3"))

    # analyze_rfp goi model dung mot lan roi validate_analysis bac bo neu co mot
    # trich dan khong khop nguyen van (QUOTE_NOT_FOUND). Do la dao dong cua model
    # chu khong phai loi co dinh, nen thu lai vai lan truoc khi bao hong.
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            model = create_gemini_analysis_model(model_name)
            analysis = analyze_rfp(req.raw_rfp_text, model)
            break
        except AnalystError as exc:
            last = exc
            logger.warning("analyze-rfp attempt %s/%s failed: %s", attempt, attempts, exc)
        except Exception as exc:  # loi mang, het quota
            logger.exception("analyze-rfp failed")
            raise HTTPException(status_code=502, detail=f"Reading the RFP failed: {exc}") from exc
    else:
        raise HTTPException(
            status_code=502,
            detail=f"Reading the RFP failed after {attempts} attempts: {last}",
        )

    # Buoc nay gan recommended_priority/priority_reason cho tung tieu chi.
    state = CriteriaState.from_analysis(analysis, req.raw_rfp_text)
    origins = _origin_by_criterion(state.packets)

    analysis_payload = _dump(analysis)
    labels = _short_labels(analysis.requirements)
    analysis_payload["requirements"] = [
        dict(_dump(r), short_label=label) for r, label in zip(analysis.requirements, labels)
    ]

    criteria_payload = []
    for criterion in state.criteria:
        item = _dump(criterion)
        item["origin"] = origins.get(criterion.name, "base")
        packet = next((p for p in state.packets if p.criterion_name == criterion.name), None)
        item["source_refs"] = [_dump(ref) for ref in getattr(packet, "source_refs", [])] if packet else []
        criteria_payload.append(item)

    analysis_payload["suggested_criteria_weights"] = criteria_payload

    return {
        "schema_version": "3.0",
        "rfp_analysis": analysis_payload,
        "confirmed_criteria": criteria_payload,
    }


@router.post("/api/score")
def score_route(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        from AI.contracts import ScoringInput
        from AI.scoring import score_proposal
    except ImportError as exc:  # pragma: no cover
        raise HTTPException(status_code=503, detail=f"Scoring agent is not installed: {exc}") from exc

    try:
        scoring_input = ScoringInput.model_validate(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Bad scoring input: {exc}") from exc

    try:
        result = score_proposal(scoring_input)
    except Exception as exc:
        logger.exception("score failed")
        raise HTTPException(status_code=502, detail=f"Scoring failed: {exc}") from exc

    scoring = _dump(result)
    scoring["recommendation"] = _recommendation(result, scoring_input.rfp_analysis.requirements)
    return scoring
