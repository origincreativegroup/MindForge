import json
from typing import Dict, List
import orjson

from .llm_client import chat
from .memory import summarize_context
from .prompts import EXTRACTOR_SYSTEM, extractor_user

# Import regex baseline (original extractor saved separately if needed)
from . import extractor as regex_extractor_baseline

def _try_json(s: str) -> Dict[str, List[str]]:
    s = s.strip()
    if s.startswith("```"):
        s = s.strip("`")
        if "\n" in s:
            s = s.split("\n", 1)[1]
        if s.lower().startswith("json"):
            s = s[4:].strip()
    try:
        return orjson.loads(s)
    except Exception:
        try:
            return json.loads(s)
        except Exception:
            return {}

def extract_process(texts: List[str]) -> Dict[str, List[str]]:
    history_plain = summarize_context(texts, max_len=4000)
    messages = [
        {"role": "system", "content": EXTRACTOR_SYSTEM},
        {"role": "user",   "content": extractor_user(history_plain)},
    ]
    try:
        raw = chat(messages, temperature=0.0)
        parsed = _try_json(raw)
        if parsed and any(parsed.values()):
            out = {
                "steps": [str(x).strip() for x in parsed.get("steps", []) if str(x).strip()][:25],
                "actors": [str(x).strip() for x in parsed.get("actors", []) if str(x).strip()][:25],
                "tools": [str(x).strip() for x in parsed.get("tools", []) if str(x).strip()][:25],
                "decisions": [str(x).strip() for x in parsed.get("decisions", []) if str(x).strip()][:25],
                "raw_chunks": [t for t in texts if t.strip()][-20:],
            }
            return out
    except Exception:
        pass
    baseline = regex_extractor_baseline.extract_process(texts)
    return {
        "steps": baseline.get("steps", [])[:25],
        "actors": baseline.get("actors", [])[:25],
        "tools": baseline.get("tools", [])[:25],
        "decisions": baseline.get("decisions", [])[:25],
        "raw_chunks": baseline.get("raw_chunks", [])[-20:],
    }
