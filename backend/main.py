"""
SiviHack Backend — Proposal Scorer

Gop tu cac nhanh:
- feat/ai         : hai agent trong AI/ va agent/, kho tham chieu backend/rag
- be-init         : chuyen file (PDF/PPTX/DOCX) sang Markdown, /v1/markitdown
- rag-enterprise  : kho tri thuc doanh nghiep, /api/evidence/*

Chay:
    pip install -r requirements.txt
    cp .env.example .env   # dien API key vao
    uvicorn main:app --reload --port 8000
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv(Path(__file__).with_name(".env"))
logging.basicConfig(format="%(asctime)s:%(levelname)s:%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SiviHack Backend — Proposal Scorer")

# Frontend chay o 5173 (vite dev) va 4173 (vite preview).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # thu gon lai domain that khi deploy
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("AI_MODEL", "claude-sonnet-4-6")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


# --------------------------------------------------------------------------
# Module phu: hong mot cai khong duoc lam chet ca app
# --------------------------------------------------------------------------

try:  # chuyen doi file sang Markdown (tieu chi bonus: PDF, PPTX)
    from app.v1.endpoints.MarkitDown.router import router as markitdown_router

    app.include_router(markitdown_router, prefix="/v1/markitdown", tags=["markitdown"])
except Exception as exc:  # pragma: no cover
    logger.warning("[markitdown] khong nap duoc: %s", exc)

try:  # kho tri thuc doanh nghiep
    from enterprise.router import router as evidence_router

    app.include_router(evidence_router)
except Exception as exc:  # pragma: no cover
    logger.warning("[enterprise] khong nap duoc: %s", exc)

RAG_STORE = None
try:  # kho tham chieu cham diem theo tieu chi
    from rag.api import load_store, retrieve_payload

    RAG_STORE = load_store()
except Exception as exc:  # pragma: no cover
    logger.warning("[rag] khong nap duoc kho tham chieu: %s", exc)


# --------------------------------------------------------------------------
# API
# --------------------------------------------------------------------------

class AskRequest(BaseModel):
    prompt: str


class AskResponse(BaseModel):
    answer: str


class RagRequest(BaseModel):
    criterion: dict
    proposal_context: str = ""
    requirement_context: str = ""
    top_k_per_type: int = 1
    relevance_threshold: int = 2


def call_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Thieu GEMINI_API_KEY trong file .env")

    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    return model.generate_content(prompt).text


def call_anthropic(prompt: str) -> str:
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="Thieu ANTHROPIC_API_KEY trong file .env")

    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=ANTHROPIC_MODEL, max_tokens=1024, messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


def call_ai(prompt: str) -> str:
    """Doi provider chi can sua AI_PROVIDER trong .env."""
    return call_anthropic(prompt) if AI_PROVIDER == "anthropic" else call_gemini(prompt)


@app.get("/api/health")
def health():
    """Trang thai tung module — kiem tra truoc luc demo."""
    paths = {r.path for r in app.routes}
    return {
        "status": "ok",
        "modules": {
            "markitdown": any(p.startswith("/v1/markitdown") for p in paths),
            "enterprise_evidence": any(p.startswith("/api/evidence") for p in paths),
            "scoring_rag": RAG_STORE is not None,
            "analyze_rfp": "/api/analyze-rfp" in paths,
            "score": "/api/score" in paths,
        },
    }


@app.post("/api/ask", response_model=AskResponse)
def ask(req: AskRequest):
    return AskResponse(answer=call_ai(req.prompt))


@app.post("/rag/retrieve")
def retrieve_rag(req: RagRequest):
    if RAG_STORE is None:
        raise HTTPException(status_code=503, detail="Kho tham chieu chua nap duoc")
    try:
        return retrieve_payload(RAG_STORE, req.model_dump())
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# /api/analyze-rfp va /api/score do team AI noi vao, xem CLAUDE.md muc
# "Interface contract". Frontend da san sang goi hai endpoint nay.

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
