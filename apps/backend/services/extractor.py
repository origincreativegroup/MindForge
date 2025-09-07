import json
import re

try:
    import orjson

    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False

from .llm_client import chat
from .memory import summarize_context
from .prompts import EXTRACTOR_SYSTEM, extractor_user


def _regex_fallback_extract(texts: list[str]) -> dict[str, list[str]]:
    """Fallback regex-based extraction when LLM is unavailable."""
    combined = " ".join(texts)

    # Simple patterns for extraction
    step_pattern = (
        r"(?:then|next|after|first|second|third|finally|step \d+)[:\s]+([^.!?]+)"
    )
    actor_pattern = r"\b(manager|supervisor|system|user|staff|employee|customer|receptionist|admin|team|developer|engineer)\b"
    tool_pattern = r"\b(spreadsheet|software|portal|email|form|tool|system|database|app|platform|dashboard)\b"
    decision_pattern = (
        r"\b(if|otherwise|decision|approve|reject|check|verify|validate)\b[^.!?]*"
    )

    steps = list(set(re.findall(step_pattern, combined, re.I)))[:10]
    actors = list(set(re.findall(actor_pattern, combined, re.I)))[:10]
    tools = list(set(re.findall(tool_pattern, combined, re.I)))[:10]
    decisions = list(set(re.findall(decision_pattern, combined, re.I)))[:10]

    return {
        "steps": [s.strip() for s in steps if s.strip()],
        "actors": [a.lower() for a in actors],
        "tools": [t.lower() for t in tools],
        "decisions": [d.strip() for d in decisions if d.strip()],
        "inputs": [],
        "outputs": [],
        "raw_chunks": texts[-20:] if texts else [],
    }


def _try_json(s: str) -> dict[str, list[str]]:
    """Try to parse JSON response from LLM."""
    s = s.strip()
    if s.startswith("```"):
        s = s.strip("`")
        s = s.split("\n", 1)[1] if "\n" in s else s
        s = s.strip()
        if s.lower().startswith("json"):
            s = s[4:].strip()

    # Try orjson first if available, then standard json
    try:
        if HAS_ORJSON:
            data = orjson.loads(s)
        else:
            data = json.loads(s)
    except Exception:
        return {}

    # Ensure proper structure
    out = {
        "steps": [str(x).strip() for x in data.get("steps", []) if str(x).strip()],
        "actors": [str(x).strip() for x in data.get("actors", []) if str(x).strip()],
        "tools": [str(x).strip() for x in data.get("tools", []) if str(x).strip()],
        "decisions": [
            str(x).strip() for x in data.get("decisions", []) if str(x).strip()
        ],
        "inputs": [str(x).strip() for x in data.get("inputs", []) if str(x).strip()],
        "outputs": [str(x).strip() for x in data.get("outputs", []) if str(x).strip()],
    }
    return out


def extract_process(texts: list[str]) -> dict[str, list[str]]:
    """Extract process elements from conversation texts.

    Falls back to regex extraction if LLM is unavailable.
    """
    if not texts:
        return {
            "steps": [],
            "actors": [],
            "tools": [],
            "decisions": [],
            "inputs": [],
            "outputs": [],
            "raw_chunks": [],
        }

    # Try LLM extraction first
    try:
        history_plain = summarize_context(texts, max_len=4000)
        messages = [
            {"role": "system", "content": EXTRACTOR_SYSTEM},
            {"role": "user", "content": extractor_user(history_plain)},
        ]

        raw = chat(messages, temperature=0.0)
        parsed = _try_json(raw)

        if parsed and any(parsed.values()):
            parsed["raw_chunks"] = [t for t in texts if t.strip()][-20:]
            # Limit sizes
            for k in ("steps", "actors", "tools", "decisions", "inputs", "outputs"):
                parsed[k] = parsed[k][:25]
            return parsed
    except Exception as e:
        print(f"LLM extraction failed: {e}, falling back to regex")

    # Fallback to regex extraction
    baseline = _regex_fallback_extract(texts)
    return {
        "steps": baseline.get("steps", [])[:25],
        "actors": baseline.get("actors", [])[:25],
        "tools": baseline.get("tools", [])[:25],
        "decisions": baseline.get("decisions", [])[:25],
        "inputs": baseline.get("inputs", [])[:25],
        "outputs": baseline.get("outputs", [])[:25],
        "raw_chunks": baseline.get("raw_chunks", [])[-20:],
    }
