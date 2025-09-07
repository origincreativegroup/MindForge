"""Lightweight memory utilities used across the Casey application.

This module previously only exposed helper functions for summarising context and
windowing message history.  The project blueprint also calls for a small
in-memory buffer that keeps track of recent conversation turns.  To better
support that design we add a :class:`ShortTermMemory` implementation which
stores the last *N* messages and can output a transcript.  The class is simple
and dependency free which makes it easy to test and reuse.
"""

from collections import deque
from typing import Deque, Dict, List


class ShortTermMemory:
    """Store a rolling window of the most recent conversation turns.

    Parameters
    ----------
    max_turns:
        Maximum number of messages to retain.  Older messages are discarded as
        new ones are added.
    """

    def __init__(self, max_turns: int = 12) -> None:
        self.buffer: Deque[Dict[str, str]] = deque(maxlen=max_turns)

    def add(self, role: str, content: str) -> None:
        """Append a turn to the memory buffer."""
        self.buffer.append({"role": role, "content": content})

    def transcript(self) -> str:
        """Return the buffered conversation as a simple transcript string."""
        return "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in self.buffer
        )


def summarize_context(last_n_msgs: List[str], max_len: int = 300) -> str:
    blob = " ".join(s.strip() for s in last_n_msgs if s.strip())
    return (blob[: max_len - 3] + "...") if len(blob) > max_len else blob


def window_messages(
    messages: List[Dict[str, str]], max_chars: int = 6000
) -> List[Dict[str, str]]:
    """Trim a list of {role, content} dicts from the front to fit roughly under
    ``max_chars``.

    Messages are consumed from the end (most recent) backwards so the newest
    content is preserved.  The resulting list retains chronological order.
    """

    total = 0
    kept: List[Dict[str, str]] = []
    for m in reversed(messages):
        c = m.get("content", "") or ""
        total += len(c)
        kept.append(m)
        if total >= max_chars:
            break
    kept.reverse()
    return kept


class WorkingProcessSlate:
    """Convenience container for the currently discussed process map."""

    def __init__(self) -> None:
        self.active: Dict[str, object] | None = None

    def update(self, process_doc: Dict[str, object]) -> None:
        self.active = process_doc

    def clear(self) -> None:
        self.active = None
