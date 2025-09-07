import os
import json
import httpx
from typing import List, Dict, Any, Generator, Optional

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
BASE_URL = os.getenv("OPENAI_BASE_URL", "").rstrip("/")
TIMEOUT = float(os.getenv("LLM_REQUEST_TIMEOUT", "45"))
MODEL = os.getenv("LLM_MODEL", "gpt-5.1")
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))

OPENAI_URL = f"{BASE_URL or 'https://api.openai.com'}/v1/chat/completions"

def _auth_headers() -> Dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if OPENAI_API_KEY:
        headers["Authorization"] = f"Bearer {OPENAI_API_KEY}"
    return headers

def chat(messages: List[Dict[str, str]], model: str = MODEL, temperature: float = TEMPERATURE) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": False,
    }
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.post(OPENAI_URL, headers=_auth_headers(), json=payload)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]

def chat_stream(messages: List[Dict[str, str]], model: str = MODEL, temperature: float = TEMPERATURE) -> Generator[str, None, None]:
    """Yield content tokens from an OpenAI-compatible streaming response."""
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": True,
    }
    with httpx.Client(timeout=None) as client:
        with client.stream("POST", OPENAI_URL, headers=_auth_headers(), json=payload) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                # OpenAI-compatible servers send Server-Sent Events lines prefixed with 'data: '
                if isinstance(line, bytes):
                    line = line.decode("utf-8", errors="ignore")
                if line.startswith("data: "):
                    data = line[len("data: "):].strip()
                    if data == "[DONE]":
                        break
                    try:
                        obj = json.loads(data)
                        delta = obj.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if delta:
                            yield delta
                    except Exception:
                        # Best effort: ignore malformed chunks
                        continue
