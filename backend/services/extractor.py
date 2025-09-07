import json
from typing import Dict, List
import orjson

from .llm_client import chat
from .memory import summarize_context
from .prompts import EXTRACTOR_SYSTEM, extractor_user

# Fallback baseline from the preserved regex module
from . import extractor_regex as regex_extractor_baseline

def _try_json(s: str) -> Dict[str, List[str]]:
    s = s.strip()
    if s.startswith("```"):
        s = s.strip("`")
        s = s.split("\n", 1)[1] if "\n" in s else s
        s = s.strip()
        if s.lower().startswith("json"):
            s = s[4:].strip()
    try:
        data = orjson.loads(s)
    except Exception:
        try:
            data = json.loads(s)
        except Exception:
            return {}
    out = {
        "steps": [str(x).strip() for x in data.get("steps", []) if str(x).strip()],
        "actors": [str(x).strip() for x in data.get("actors", []) if str(x).strip()],
        "tools": [str(x).strip() for x in data.get("tools", []) if str(x).strip()],
        "decisions": [str(x).strip() for x in data.get("decisions", []) if str(x).strip()],
    }
    return out

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
            parsed["raw_chunks"] = [t for t in texts if t.strip()][-20:]
            for k in ("steps", "actors", "tools", "decisions"):
                parsed[k] = parsed[k][:25]
            return parsed
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
