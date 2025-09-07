"""Lightweight memory utilities used across the Casey application.

This module previously only exposed helper functions for summarising context and
windowing message history.  The project blueprint also calls for a small
in-memory buffer that keeps track of recent conversation turns.  To better
support that design we add a :class:`ShortTermMemory` implementation which
stores the last *N* messages and can output a transcript.  The class is simple
and dependency free which makes it easy to test and reuse.
"""

from collections import deque


class ShortTermMemory:
    """Store a rolling window of the most recent conversation turns.

    Parameters
    ----------
    max_turns:
        Maximum number of messages to retain.  Older messages are discarded as
        new ones are added.
    """

    def __init__(self, max_turns: int = 12) -> None:
        self.buffer: deque[dict[str, str]] = deque(maxlen=max_turns)

    def add(self, role: str, content: str) -> None:
        """Append a turn to the memory buffer."""
        self.buffer.append({"role": role, "content": content})

    def transcript(self) -> str:
        """Return the buffered conversation as a simple transcript string."""
        return "\n".join(f"{m['role'].upper()}: {m['content']}" for m in self.buffer)


def summarize_context(last_n_msgs: list[str], max_len: int = 300) -> str:
    blob = " ".join(s.strip() for s in last_n_msgs if s.strip())
    return (blob[: max_len - 3] + "...") if len(blob) > max_len else blob


def window_messages(
    messages: list[dict[str, str]], max_chars: int = 6000
) -> list[dict[str, str]]:
    """Trim a list of {role, content} dicts from the front to fit roughly under
    ``max_chars``.

    Messages are consumed from the end (most recent) backwards so the newest
    content is preserved.  The resulting list retains chronological order.
    """

    total = 0
    kept: list[dict[str, str]] = []
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
        self.active: dict[str, object] | None = None

    def update(self, process_doc: dict[str, object]) -> None:
        self.active = process_doc

    def clear(self) -> None:
        self.active = None


class ContextMemory:
    """Track conversational turns, extracted process elements and emotions.

    The class combines three simple stores:

    * ``session`` – rolling window of the dialogue using :class:`ShortTermMemory`
    * ``process`` – list of structured process element dictionaries
    * ``emotions`` – history of detected emotional scores

    It provides tiny helper methods for updating each store and for retrieving
    common views such as the current transcript or the most recent emotion
    scores.  No external dependencies are required which keeps this component
    lightweight and easy to test.
    """

    def __init__(self, max_turns: int = 12) -> None:
        self.session = ShortTermMemory(max_turns=max_turns)
        self.process: list[dict[str, object]] = []
        self.emotions: list[dict[str, float]] = []

    # session memory -----------------------------------------------------
    def add_turn(self, role: str, content: str) -> None:
        """Record a new conversation turn."""
        self.session.add(role, content)

    def transcript(self) -> str:
        """Return the recent conversation transcript."""
        return self.session.transcript()

    # process memory -----------------------------------------------------
    def add_process_elements(self, elements: dict[str, object]) -> None:
        """Append extracted process elements to the history."""
        self.process.append(elements)

    # emotional memory ---------------------------------------------------
    def add_emotions(self, scores: dict[str, float]) -> None:
        """Store detected emotional scores for the latest turn."""
        self.emotions.append(scores)

    def latest_emotion(self) -> dict[str, float]:
        """Return the most recent emotional score dictionary."""
        return self.emotions[-1] if self.emotions else {}
