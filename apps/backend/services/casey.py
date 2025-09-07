"""High level orchestration for the Casey interviewer."""

from __future__ import annotations

from typing import Dict

from .parser import parse_response
from .emotions import emotional_scores
from .memory import ContextMemory


class Casey:
    """Minimal interviewer implementation tying together core components.

    The class records conversation turns, extracts process elements and emotional
    signals and keeps everything in a :class:`ContextMemory` instance.  It does
    not handle language model interaction directly; instead it focuses on the
    bookkeeping logic that can be tested offline.
    """

    def __init__(self, memory: ContextMemory | None = None) -> None:
        self.memory = memory or ContextMemory()

    def ingest(self, role: str, text: str) -> Dict[str, Dict[str, object]]:
        """Ingest a new utterance and update memory stores.

        Parameters
        ----------
        role:
            The speaker role, e.g. ``"user"`` or ``"assistant"``.
        text:
            Raw natural language text for the turn.

        Returns
        -------
        dict
            Dictionary with ``elements`` and ``emotions`` entries containing the
            parsed process elements and emotion scores respectively.
        """

        self.memory.add_turn(role, text)
        elements = parse_response(text)
        self.memory.add_process_elements(elements)
        emotions = emotional_scores(text)
        self.memory.add_emotions(emotions)
        return {"elements": elements, "emotions": emotions}

    # Convenience accessors -------------------------------------------------
    def transcript(self) -> str:
        return self.memory.transcript()

    def latest_emotion(self) -> Dict[str, float]:
        return self.memory.latest_emotion()
