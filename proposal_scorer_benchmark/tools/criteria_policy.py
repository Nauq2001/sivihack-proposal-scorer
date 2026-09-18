"""Three-source criterion policy. Python stdlib only; no model calls."""
import re
import unicodedata

BASE = (
    ("problem_understanding", "Problem Understanding"),
    ("scope_deliverables_clarity", "Scope & Deliverables Clarity"),
    ("pricing_clarity", "Pricing Clarity"),
    ("timeline_clarity", "Timeline Clarity"),
    ("completeness_vs_rfp", "Completeness vs. RFP Requirements"),
    ("tone_persuasiveness", "Tone & Persuasiveness"),
    ("risk_assumptions_transparency", "Risk/Assumptions Transparency"),
)
PRIORITIES = {"minor", "major", "critical"}


def normalized_name(value):
    text = unicodedata.normalize("NFKD", str(value)).casefold()
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.replace("&", " and ")
    words = re.findall(r"[a-z0-9]+", text)
    return " ".join(w for w in words if w not in {"and", "vs", "versus"})


def _priority(row):
    return row.get("priority") if row.get("priority") in PRIORITIES else "minor"


def _evidence(row, rfp_text):
    quote = row.get("rfp_quote")
    return quote if isinstance(quote, str) and quote.strip() and quote in rfp_text else None


def normalize_criteria(agent_rows, custom_rows, rfp_text):
    """Return a proposal only; user confirmation belongs to the Criteria table.

    Agent may vary base priority, never base identity/count. Custom rows come
    exclusively from the user. History is deliberately not accepted here.
    """
    base_lookup = {}
    for key, name in BASE:
        base_lookup[normalized_name(name)] = key
        base_lookup[normalized_name(key)] = key
    base_updates, ai_rows, discarded = {}, [], []
    for row in agent_rows:
        if not isinstance(row, dict):
            discarded.append({"reason": "invalid_row"})
            continue
        key = base_lookup.get(normalized_name(row.get("name", "")))
        if row.get("source") == "base":
            supplied_id = row.get("id")
            if supplied_id in dict(BASE):
                key = supplied_id
            if key and key not in base_updates:
                base_updates[key] = row
            else:
                discarded.append({"name": row.get("name"), "reason": "unknown_or_duplicate_base"})
        elif row.get("source") == "ai":
            if key:
                discarded.append({"name": row.get("name"), "reason": "duplicates_base"})
            else:
                ai_rows.append(row)
        else:
            discarded.append({"name": row.get("name"), "reason": "agent_source_not_allowed"})
    output = []
    for key, name in BASE:
        row = base_updates.get(key, {})
        output.append({"id": key, "name": name, "source": "base",
                       "priority": _priority(row), "rfp_quote": _evidence(row, rfp_text)})
    seen = set(base_lookup)
    count = 0
    for row in ai_rows:
        name = row.get("name")
        normal = normalized_name(name or "")
        quote = _evidence(row, rfp_text)
        reason = None
        if not isinstance(name, str) or not normal:
            reason = "empty_name"
        elif normal in seen:
            reason = "duplicates_normalized_name"
        elif quote is None:
            reason = "missing_or_invalid_rfp_quote"
        elif count >= 3:
            reason = "ai_limit_3"
        if reason:
            discarded.append({"name": name, "reason": reason})
            continue
        count += 1
        seen.add(normal)
        output.append({"id": f"ai_{count}", "name": name, "source": "ai",
                       "priority": _priority(row), "rfp_quote": quote})
    for index, row in enumerate(custom_rows, 1):
        if not isinstance(row, dict) or not isinstance(row.get("name"), str) or not row["name"].strip():
            discarded.append({"reason": "empty_custom_name"})
            continue
        output.append({"id": f"custom_{index}", "name": row["name"].strip(),
                       "source": "custom", "priority": _priority(row),
                       "rfp_quote": _evidence(row, rfp_text)})
    return {"criteria": output, "discarded": discarded, "requires_user_confirmation": True,
            "table_columns": ["Criterion", "Source", "Priority", "RFP evidence"]}
