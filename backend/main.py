"""
SiviHack Starter Backend
-------------------------
FastAPI backend voi 1 endpoint mau goi AI API (Anthropic Claude mac dinh,
de doi sang OpenAI / Gemini / NVIDIA NIM bang cach sua ham call_ai()).

Chay:
    pip install -r requirements.txt
    cp .env.example .env   # dien API key vao
    uvicorn main:app --reload --port 8000

Test:
    curl -X POST http://localhost:8000/api/ask \
      -H "Content-Type: application/json" \
      -d '{"prompt": "Xin chao"}'
"""

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from rag.api import load_store, retrieve_payload

load_dotenv()

app = FastAPI(title="SiviHack Backend")

RAG_STORE = load_store(Path(__file__).parent / "rag" / "data" / "records.jsonl")

# Cho phep frontend (Vite dev server) goi sang trong luc dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # thu gon lai domain that khi deploy
    allow_methods=["*"],
    allow_headers=["*"],
)

AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")  # "gemini" hoac "anthropic"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("AI_MODEL", "claude-sonnet-4-6")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")  # ban nhe, tiet kiem quota $100


class AskRequest(BaseModel):
    prompt: str


class AskResponse(BaseModel):
    answer: str


class RagRequest(BaseModel):
    criterion: dict
    proposal_context: str
    requirement_context: str
    top_k_per_type: int = 1


def call_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Thieu GEMINI_API_KEY trong file .env")

    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text


def call_anthropic(prompt: str) -> str:
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="Thieu ANTHROPIC_API_KEY trong file .env")

    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def call_ai(prompt: str) -> str:
    """
    Goi AI API theo AI_PROVIDER trong .env ("gemini" mac dinh, hoac "anthropic").
    Doi provider luc thi dau chi can sua 1 dong trong .env, khong can sua code.
    """
    if AI_PROVIDER == "anthropic":
        return call_anthropic(prompt)
    return call_gemini(prompt)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/ask", response_model=AskResponse)
def ask(req: AskRequest):
    answer = call_ai(req.prompt)
    return AskResponse(answer=answer)


@app.post("/rag/retrieve")
def retrieve_rag(req: RagRequest):
    try:
        return retrieve_payload(RAG_STORE, req.model_dump())
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
