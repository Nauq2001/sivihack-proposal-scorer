"""
Cac route noi hai agent lai voi nhau, theo CLAUDE.md muc "Interface contract".

    POST /api/analyze-rfp   RFP Analyst  -> rfp_analysis + confirmed_criteria
    POST /api/score         Proposal Analyst -> scoring
    POST /api/create-ticket Nguoi dung bam "Send to Work" -> n8n (Jira + Slack)

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


REVISE_FLOOR = 2.0


def _recommendation(result: Any, requirements: list[Any]) -> tuple[str, str]:
    """Khuyen nghi cuoi cung — tinh bang code, khong hoi LLM.

    Theo `rubric.json` cua benchmark: vi pham mot rang buoc cung thi khong the
    khuyen nghi gui di, du diem trung binh co cao.

    Duoi REVISE_FLOOR cung khong the goi la "sua duoc": ban 1.4/5 ma AI ta la
    "non-responsive" van hien "Revise — the gaps are fixable" thi badge dang
    noi nguoc lai chinh nhan xet ngay ben canh no.
    """
    hard = {r.id for r in requirements if getattr(r, "is_hard_constraint", False)}
    for finding in result.findings:
        if finding.status == "contradicted" and finding.requirement_id in hard:
            return "do_not_accept_as_written", "A hard constraint in the RFP is contradicted."
    if any(f.status == "contradicted" for f in result.findings):
        return "do_not_accept_as_written", "The draft contradicts something the RFP states."
    if result.overall_score < REVISE_FLOOR:
        return "do_not_accept_as_written", "Too little of the RFP is answered to edit this into shape."
    if result.overall_score >= 4:
        return "ready", "Minor edits at most."
    return "revise", "The gaps are fixable."


def _dump(model: Any) -> dict[str, Any]:
    return model.model_dump() if hasattr(model, "model_dump") else dict(model)


def _company_checks(raw_proposal_text: str) -> dict[str, Any]:
    """Loi hua trong ban thao ma cong ty chua chac giu duoc.

    Doi chieu voi rate card va chuan SLA noi bo (backend/enterprise/): khong goi
    model, khong truy xuat — chi so chuoi, nen lan nao chay cung ra ket qua nhu
    nhau va moi phat hien deu keo theo mot cau nguyen van. Day la phan RFP
    khong the bat duoc: RFP khong biet gia san hay gio truc cua ben minh.

    Khong co kho thi bo qua; mot ban danh gia thieu phan nay van dung.
    """
    try:
        from enterprise.evidence import check_commitments
        from enterprise.router import corpus

        result = check_commitments(corpus(), raw_proposal_text)
    except Exception as exc:  # pragma: no cover
        logger.warning("enterprise commitment check unavailable: %s", exc)
        return {"findings": [], "available": False}

    # Trich dan phai co that trong ban thao, y nhu moi trich dan khac.
    findings = [f for f in result.get("findings", []) if _find_verbatim(f.get("quote", ""), raw_proposal_text)]
    return {
        "findings": findings,
        "available": True,
        "standards_checked": result.get("standards_checked", []),
        "stale_standards": result.get("stale_standards", []),
    }


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


# Model cua agent dat extra="forbid". Frontend nhan lai ban phan tich da co
# them truong hien thi (`short_label`, `origin`, `requirement_ids`...), nen phai
# go ra truoc khi dung lai state.
_ANALYSIS_FIELDS = {"client_name", "project_name", "detected_priority_note",
                    "requirements", "suggested_criteria_weights", "criterion_packets"}
_REQUIREMENT_FIELDS = {"id", "text", "source_section", "source_quote",
                       "related_criterion", "is_hard_constraint"}
_CRITERION_FIELDS = {"name", "description", "weight", "recommended_priority", "priority_reason"}
_PACKET_FIELDS = {"criterion_name", "origin", "evaluation_guidance", "requirement_ids",
                  "source_refs", "notes"}


def _only(data: dict[str, Any], fields: set[str]) -> dict[str, Any]:
    return {k: v for k, v in data.items() if k in fields}


def _strip_extra_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    out = _only(analysis, _ANALYSIS_FIELDS)
    out["requirements"] = [_only(r, _REQUIREMENT_FIELDS) for r in analysis.get("requirements", [])]
    out["suggested_criteria_weights"] = [
        _only(c, _CRITERION_FIELDS) for c in analysis.get("suggested_criteria_weights", [])
    ]
    out["criterion_packets"] = [_only(p, _PACKET_FIELDS) for p in analysis.get("criterion_packets", [])]
    out.setdefault("detected_priority_note", None)
    return out


class ConfirmRequest(BaseModel):
    rfp_analysis: dict[str, Any]
    raw_rfp_text: str
    criteria: list[dict[str, Any]]


@router.post("/api/confirm-criteria")
def confirm_criteria_route(req: ConfirmRequest) -> dict[str, Any]:
    """Chot danh sach tieu chi — chay resolver dung mot lan, o day.

    Nguoi dung them/xoa/keo tha thoai mai o man 2 ma khong ton mot lan goi model
    nao. Bam "Score the proposal" moi la luc chot, va chi luc do resolver cua
    agent (agent/src/rfp_analyst/criteria.py) moi lam hai viec no sinh ra de lam:

      - bat trung y nghia: "Price transparency" khi da co "Pricing Clarity" thi
        gop lai, thay vi cham hai lan cung mot thu;
      - noi tieu chi tu them vao requirement/quote co that trong RFP, de no
        khong bi cham mu.

    Hong o dau cung khong chan duoc buoc cham diem: tra lai dung danh sach
    nguoi dung gui len kem mot cau canh bao.
    """
    try:
        from rfp_analyst.criteria import create_gemini_resolution_model
        from rfp_analyst.models import RFPAnalysis, UserCriterionInput
        from rfp_analyst.service import CriteriaState
    except ImportError as exc:  # pragma: no cover
        raise HTTPException(status_code=503, detail=f"RFP Analyst is not installed: {exc}") from exc

    import os

    warnings: list[str] = []
    try:
        analysis = RFPAnalysis.model_validate(_strip_extra_analysis(req.rfp_analysis))
        state = CriteriaState.from_analysis(analysis, req.raw_rfp_text)
    except Exception as exc:
        logger.warning("confirm-criteria could not rebuild the state: %s", exc)
        return {"confirmed_criteria": req.criteria, "rfp_analysis": req.rfp_analysis,
                "warnings": [f"Criteria were used exactly as you set them ({exc})."], "merges": []}

    wanted = {c["name"] for c in req.criteria}
    for existing in [c.name for c in state.criteria]:
        if existing not in wanted:
            state.remove(existing)

    resolver = None
    added = [c for c in req.criteria if c.get("origin") == "user"]
    if added:
        try:
            model_name = os.getenv("RFP_ANALYST_MODEL") or os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
            resolver = create_gemini_resolution_model(model_name)
        except Exception as exc:
            logger.warning("resolver unavailable, using the offline fallback: %s", exc)
            warnings.append("Your own criteria were kept as written; they could not be checked against the RFP.")

    merges: list[dict[str, str]] = []
    for item in added:
        try:
            resolved = state.add_or_merge(
                UserCriterionInput(
                    name=item["name"],
                    description=item.get("description", ""),
                    weight=item.get("weight") or 1.0,
                ),
                resolver,
            )
        except Exception as exc:
            logger.warning("could not resolve %r: %s", item.get("name"), exc)
            warnings.append(f"“{item.get('name')}” was kept as you wrote it ({exc}).")
            continue
        if resolved.is_duplicate and resolved.criterion.name != item["name"]:
            merges.append({"added": item["name"], "merged_into": resolved.criterion.name})

    # add_or_merge goi lai apply_priority_recommendations, de xuat cua AI ghi de
    # len cot nguoi dung vua chon. Lua chon cua nguoi dung la cuoi cung, nen dat
    # lai sau cung.
    chosen = {c["name"]: c for c in req.criteria}
    for merge in merges:
        chosen[merge["merged_into"]] = chosen.pop(merge["added"])
    for criterion in state.criteria:
        pick = chosen.get(criterion.name)
        if pick:
            criterion.recommended_priority = pick.get("recommended_priority", criterion.recommended_priority)
            criterion.weight = pick.get("weight") or criterion.weight

    packet_by_name = {p.criterion_name: p for p in state.packets}
    confirmed = []
    for criterion in state.criteria:
        packet = packet_by_name.get(criterion.name)
        item = _dump(criterion)
        item["origin"] = packet.origin if packet else "base"
        item["requirement_ids"] = list(packet.requirement_ids) if packet else []
        item["source_refs"] = [_dump(r) for r in packet.source_refs] if packet else []
        confirmed.append(item)

    analysis_payload = _dump(state.analysis)
    analysis_payload["criterion_packets"] = [_dump(p) for p in state.packets]
    labels = _short_labels(state.analysis.requirements, req.raw_rfp_text)
    analysis_payload["requirements"] = [
        dict(_dump(r), short_label=label) for r, label in zip(state.analysis.requirements, labels)
    ]

    return {
        "confirmed_criteria": confirmed,
        "rfp_analysis": analysis_payload,
        "merges": merges,
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
    scoring["recommendation"], scoring["recommendation_reason"] = _recommendation(result, requirements)
    scoring["company_checks"] = _company_checks(proposal_text)
    scoring["warnings"] = (
        [f"{len(unverified)} citation(s) were dropped because the quote is not in the proposal "
         f"word for word: {', '.join(unverified)}."]
        if unverified else []
    )
    return scoring


@router.post("/api/create-ticket")
def create_ticket_route(payload: dict[str, Any]) -> dict[str, Any]:
    """Nguoi dung bam "Send to Work" tren man ket qua — khong tu dong chay
    theo /api/score. `payload` la chinh object `scoring` frontend da co san."""
    import os

    webhook_url = os.getenv("N8N_TICKET_WEBHOOK_URL")
    if not webhook_url:
        raise HTTPException(status_code=503, detail="N8N_TICKET_WEBHOOK_URL is not configured")

    try:
        from AI.n8n_client import N8nWorkflowError, send_to_jira_slack_workflow
    except ImportError as exc:  # pragma: no cover
        raise HTTPException(status_code=503, detail=f"n8n client is not installed: {exc}") from exc

    try:
        return send_to_jira_slack_workflow(payload, webhook_url)
    except N8nWorkflowError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
