from .llm_client import chat
from .memory import summarize_context, window_messages
from .prompts import MIRROR_SYSTEM, mirror_user

def mirror_understanding(history_texts, max_len=3000) -> str:
    history_plain = summarize_context(history_texts, max_len=max_len)
    messages = [
        {"role": "system", "content": MIRROR_SYSTEM},
        {"role": "user",   "content": mirror_user(history_plain)},
    ]
    messages = window_messages(messages, max_chars=6000)
    try:
        out = chat(messages, temperature=0.0).strip()
        return out or "Here's what I think I heard: (no content)"
    except Exception:
        # Fallback basic template
        return "Here's what I think I heard: steps happen in order, with some approvals. Tools and handoffs exist. Did I miss anything?"  # minimal fail-safe
