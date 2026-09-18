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


def _rfp_item_number(quote: str, raw_rfp_text: str) -> str | None:
    """So thu tu ma chinh RFP danh cho dong chua `quote`, neu co.

    Lui tu cho trich dan len tren cho den khi gap mot dong danh so. Gap tieu de
    hoac dong trong thi dung: het khoi danh sach, khong con so nao thuoc ve no.
    """
    span = _find_verbatim(quote, raw_rfp_text)
    if span is None:
        return None
    at = raw_rfp_text.find(span)
    for line in reversed(raw_rfp_text[:at].splitlines()):
        if re.match(r"^\s*#{1,6}\s", line) or not line.strip():
            return None
        found = re.match(r"^\s*(\d+)[.)]\s", line)
        if found:
            return found.group(1)
    return None


def _short_labels(requirements: list[Any], raw_rfp_text: str) -> list[str]:
    """Nhan ngan cho dai phu yeu cau, toi da ~14 ky tu.

    Uu tien so ma RFP tu danh ("3." trong danh sach): nguoi doc do lai duoc.
    Mot dong RFP co the sinh ra hai yeu cau — hai nhan trung nhau la dung, ca
    hai cung tro ve mot cho.

    Khong co so thi quay ve `source_section`, von khac nhau tuy model: co ban
    tra "Requirements / 3", co ban chi tra "Requirements".
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
        in_rfp = _rfp_item_number(getattr(r, "source_quote", "") or "", raw_rfp_text)
        if in_rfp:
            labels.append(f"{short} {in_rfp}")
        elif numbered:
            labels.append(f"{short} {numbered.group(1)}")
        elif counts[section] == 1:
            labels.append(base[:14])
        else:
            seen[section] = seen.get(section, 0) + 1
            labels.append(f"{short} {seen[section]}")
    return labels



def _normalise(text: str) -> tuple[str, list[int]]:
    """Ban thuong hoa de tim trich dan, kem ban do chi so ve van ban goc.

    Bo dau nhan Markdown, gom khoang trang, thong nhat gach ngang va dau nhay.
    Nho ban do nay, doan tim duoc van duoc cat ra tu van ban goc nguyen van.
    """
    out: list[str] = []
    index: list[int] = []
    prev_space = False
    for i, ch in enumerate(text):
        if ch in "*_`#>":
            continue
        if ch in "\u2013\u2014":
            ch = "-"
        elif ch in "\u2018\u2019":
            ch = "'"
        elif ch in "\u201c\u201d":
            ch = '"'
        if ch.isspace():
            if prev_space:
                continue
            prev_space = True
            ch = " "
        else:
            prev_space = False
        out.append(ch.lower())
        index.append(i)
    return "".join(out), index


def _find_verbatim(quote: str, source: str) -> str | None:
    """Doan nguyen van trong `source` ung voi `quote`, hoac None."""
    if quote and quote in source:
        return quote
    norm_source, index = _normalise(source)
    norm_quote, _ = _normalise(quote)
    norm_quote = norm_quote.strip()
    if not norm_quote:
        return None
    at = norm_source.find(norm_quote)
    if at == -1:
        return None
    return source[index[at]: index[at + len(norm_quote) - 1] + 1]


def _repair_analysis(analysis: Any, raw_rfp_text: str) -> list[str]:
    """Sua trich dan ve dung nguyen van; bo yeu cau nao khong tim duoc.

    Bo mot yeu cau van hon la bao hong ca lan doc RFP: nguoi dung mat mot dong
    trong bang phu, con hon man hinh trang khong co gi.
    """
    dropped: list[str] = []
    kept = []
    for requirement in analysis.requirements:
        fixed = _find_verbatim(requirement.source_quote, raw_rfp_text)
        if fixed is None:
            dropped.append(requirement.id)
            continue
        requirement.source_quote = fixed
        kept.append(requirement)
    analysis.requirements = kept

    ids = {r.id for r in kept}
    for packet in analysis.criterion_packets:
        packet.requirement_ids = [i for i in packet.requirement_ids if i in ids]
        refs = []
        for ref in packet.source_refs:
            fixed = _find_verbatim(ref.quote, raw_rfp_text)
            if fixed is not None:
                ref.quote = fixed
                refs.append(ref)
        packet.source_refs = refs
    return dropped


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
        from rfp_analyst.validation import ContractError, validate_analysis
    except ImportError as exc:  # pragma: no cover
        raise HTTPException(status_code=503, detail=f"RFP Analyst is not installed: {exc}") from exc

    import os

    model_name = os.getenv("RFP_ANALYST_MODEL") or os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    attempts = int(os.getenv("RFP_ANALYST_ATTEMPTS", "3"))

    # analyze_rfp goi model dung mot lan, roi validate_analysis bac bo CA BAN
    # PHAN TICH neu chi mot trich dan khong khop nguyen van (ContractError:
    # QUOTE_NOT_FOUND). Day la dao dong cua model, khong phai loi co dinh, nen:
    #   1. sua trich dan ve dung nguyen van, bo yeu cau nao khong tim duoc
    #   2. neu van hong thi thu lai ca lan goi model
    # Hoan buoc validate cua analyst lai: neu de no chay trong analyze_rfp thi
    # mot trich dan lech lam mat luon ca object phan tich, khong con gi de sua.
    # Tu validate lai ngay sau khi da sua, o duoi.
    import rfp_analyst.analyst as analyst_module

    original_validate = analyst_module.validate_analysis
    analysis = None
    dropped: list[str] = []
    last: Exception | None = None
    try:
        analyst_module.validate_analysis = lambda *_args, **_kwargs: None
        for attempt in range(1, attempts + 1):
            try:
                model = create_gemini_analysis_model(model_name)
                analysis = analyze_rfp(req.raw_rfp_text, model)
                break
            except (AnalystError, ContractError) as exc:
                last = exc
                logger.warning("analyze-rfp attempt %s/%s failed: %s", attempt, attempts, exc)
            except Exception as exc:  # loi mang, het quota
                logger.exception("analyze-rfp failed")
                raise HTTPException(status_code=502, detail=f"Reading the RFP failed: {exc}") from exc
    finally:
        analyst_module.validate_analysis = original_validate

    if analysis is None:
        raise HTTPException(
            status_code=502,
            detail=f"Reading the RFP failed after {attempts} attempts: {last}",
        )

    # Chot lai: sua trich dan lech va bo yeu cau khong doi chieu duoc.
    dropped = _repair_analysis(analysis, req.raw_rfp_text)
    if not analysis.requirements:
        raise HTTPException(
            status_code=502,
            detail="No requirement quote could be matched back to the RFP text.",
        )
    try:
        validate_analysis(analysis, req.raw_rfp_text)
    except ContractError as exc:
        raise HTTPException(status_code=502, detail=f"Reading the RFP failed: {exc}") from exc

    # Buoc nay gan recommended_priority/priority_reason cho tung tieu chi.
    state = CriteriaState.from_analysis(analysis, req.raw_rfp_text)
    origins = _origin_by_criterion(state.packets)

    analysis_payload = _dump(analysis)
    labels = _short_labels(analysis.requirements, req.raw_rfp_text)
    analysis_payload["requirements"] = [
        dict(_dump(r), short_label=label) for r, label in zip(analysis.requirements, labels)
    ]

    criteria_payload = []
    for criterion in state.criteria:
        item = _dump(criterion)
        item["origin"] = origins.get(criterion.name, "base")
        packet = next((p for p in state.packets if p.criterion_name == criterion.name), None)
        item["source_refs"] = [_dump(ref) for ref in getattr(packet, "source_refs", [])] if packet else []
        item["requirement_ids"] = list(getattr(packet, "requirement_ids", [])) if packet else []
        criteria_payload.append(item)

    analysis_payload["suggested_criteria_weights"] = criteria_payload

    warnings: list[str] = []
    if dropped:
        warnings.append(
            f"{len(dropped)} requirement(s) were dropped because their quote could not be "
            f"matched word for word in the RFP: {', '.join(dropped)}."
        )

    return {
        "schema_version": "3.0",
        "rfp_analysis": analysis_payload,
        "confirmed_criteria": criteria_payload,
        "warnings": warnings,
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

    # Kiem chung trich dan: moi `citation` phai co nguyen van trong proposal.
    # Sua duoc thi sua, khong thi bo trong — mot cau trich bia lam mat niem tin
    # vao ca ban danh gia, va giao dien se khong to sang duoc gi.
    proposal_text = scoring_input.raw_proposal_text
    unverified: list[str] = []
    for finding in result.findings:
        if not finding.citation:
            continue
        fixed = _find_verbatim(finding.citation, proposal_text)
        if fixed is None:
            unverified.append(finding.requirement_id)
            finding.citation = ""
        else:
            finding.citation = fixed

    for criterion in result.criteria:
        kept = []
        for quote in criterion.citations:
            fixed = _find_verbatim(quote, proposal_text)
            if fixed is not None:
                kept.append(fixed)
        criterion.citations = kept

    # Model van viet "failing REQ-009" trong loi binh. REQ-009 la so thu tu noi
    # bo; doi sang nhan cua RFP de nguoi doc do lai duoc trong tai lieu goc.
    requirements = scoring_input.rfp_analysis.requirements
    labels = dict(zip(
        (r.id for r in requirements),
        _short_labels(requirements, scoring_input.raw_rfp_text),
    ))
    def relabel(text: str) -> str:
        out = re.sub(r"REQ-\d+", lambda m: labels.get(m.group(0), m.group(0)), text or "")
        # Mot dong RFP tach ra hai yeu cau thi hai nhan trung nhau: "(Req 4, Req 4)".
        return re.sub(r"\b([A-Za-z]+ \d+)(?:,\s*\1\b)+", r"\1", out)
    for finding in result.findings:
        finding.reason = relabel(finding.reason)
        finding.suggested_patch = relabel(finding.suggested_patch)
    for criterion in result.criteria:
        criterion.comment = relabel(criterion.comment)
    result.verdict = relabel(result.verdict)

    scoring = _dump(result)
    scoring["recommendation"] = _recommendation(result, requirements)
    scoring["warnings"] = (
        [f"{len(unverified)} citation(s) were dropped because the quote is not in the proposal "
         f"word for word: {', '.join(unverified)}."]
        if unverified else []
    )
    return scoring
