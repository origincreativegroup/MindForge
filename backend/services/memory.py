from typing import List, Dict

def summarize_context(last_n_msgs: List[str], max_len: int = 300) -> str:
    blob = " ".join(s.strip() for s in last_n_msgs if s.strip())
    return (blob[: max_len - 3] + "...") if len(blob) > max_len else blob

def window_messages(messages: List[Dict[str, str]], max_chars: int = 6000) -> List[Dict[str, str]]:
    """Trim a list of {role, content} dicts from the front to fit roughly under max_chars."""
    total = 0
    kept: List[Dict[str, str]] = []
    # iterate from the end (most recent) backwards, then reverse at the end
    for m in reversed(messages):
        c = m.get("content", "") or ""
        total += len(c)
        kept.append(m)
        if total >= max_chars:
            break
    kept.reverse()
    return kept
