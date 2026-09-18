"""Minimal Gemini connectivity check — run this BEFORE the full regression to
confirm GEMINI_API_KEY / model name / network all work, spending only a
couple of trivial-prompt tokens instead of a full scoring call.

    python3 -m AI.calibration.test_gemini_connection
"""

from __future__ import annotations

from pydantic import BaseModel

from AI.llm_client import AI_PROVIDER, GEMINI_API_KEY, GEMINI_MODEL, _call_gemini, call_ai_json


class _PingReply(BaseModel):
    message: str


def main() -> None:
    print(f"AI_PROVIDER = {AI_PROVIDER!r}")
    print(f"GEMINI_MODEL = {GEMINI_MODEL!r}")
    print(f"GEMINI_API_KEY set = {bool(GEMINI_API_KEY) and GEMINI_API_KEY != 'your_key_here'}")
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_key_here":
        raise SystemExit(
            "GEMINI_API_KEY chưa được điền thật trong backend/.env — mở file đó và "
            "dán key vào (đừng paste key vào chat/terminal log)."
        )

    print("\n--- Tier 1: raw text call (no JSON mode) ---")
    raw = _call_gemini("Reply with exactly one word: pong")
    print("raw response:", raw.strip())

    print("\n--- Tier 2: JSON-mode structured call (what score_proposal() relies on) ---")
    result = call_ai_json('Return JSON exactly: {"message": "pong"}', _PingReply)
    print("parsed:", result)

    print("\nGemini OK — both raw text and JSON-mode structured output work.")


if __name__ == "__main__":
    main()
