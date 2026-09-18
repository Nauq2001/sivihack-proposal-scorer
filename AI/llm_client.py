"""Provider-agnostic, JSON-validating LLM client for the AI team's calls.

Mirrors backend/main.py's call_ai() provider-switch pattern (same env var
names) but purpose-built for strict structured output: the caller passes a
Pydantic schema, and this module retries with a repair prompt until the
response parses and validates, or gives up.

Kept standalone (does not import backend/) so AI/ has no dependency on
backend/ — Backend imports AI/, not the other way around.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import TypeVar

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv(Path(__file__).resolve().parent.parent / "backend" / ".env")

AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("AI_MODEL", "claude-sonnet-4-6")

T = TypeVar("T", bound=BaseModel)


class LLMOutputError(RuntimeError):
    """Raised when the LLM never returns JSON matching the expected schema."""


def _call_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise LLMOutputError("Missing GEMINI_API_KEY in backend/.env")

    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        GEMINI_MODEL,
        generation_config={"response_mime_type": "application/json"},
    )
    response = model.generate_content(prompt)
    return response.text


def _call_anthropic(prompt: str) -> str:
    if not ANTHROPIC_API_KEY:
        raise LLMOutputError("Missing ANTHROPIC_API_KEY in backend/.env")

    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def _call_raw(prompt: str) -> str:
    if AI_PROVIDER == "anthropic":
        return _call_anthropic(prompt)
    return _call_gemini(prompt)


def _extract_json(raw: str) -> str:
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw, re.DOTALL)
    if fenced:
        return fenced.group(1)
    first, last = raw.find("{"), raw.rfind("}")
    if first != -1 and last != -1 and last > first:
        return raw[first : last + 1]
    return raw


def call_ai_json(prompt: str, schema: type[T], max_retries: int = 2) -> T:
    last_error: Exception | None = None
    current_prompt = prompt
    for _ in range(max_retries + 1):
        raw = _call_raw(current_prompt)
        try:
            data = json.loads(_extract_json(raw))
            return schema.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as exc:
            last_error = exc
            current_prompt = (
                f"{prompt}\n\n---\nYour previous response was not valid JSON for the "
                f"required schema.\nYour previous response:\n{raw}\n\nValidation error:\n"
                f"{exc}\n\nReturn ONLY corrected JSON matching the schema. No prose, no "
                f"markdown fences."
            )
    raise LLMOutputError(
        f"LLM did not return valid JSON matching {schema.__name__} after "
        f"{max_retries + 1} attempts: {last_error}"
    )
