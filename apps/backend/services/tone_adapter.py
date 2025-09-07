from __future__ import annotations
"""Tone adaptation utilities for Casey.

This module exposes :class:`ToneAdapter` which analyses a user's latest
message to detect their communication style and then rewrites Casey's
responses to mirror that tone.  No persona selection is required; the
style is inferred on the fly from the dialogue.
"""

from typing import Optional
from .llm_client import chat


class ToneAdapter:
    """Detect and mirror the user's tone in Casey's responses."""

    def __init__(self) -> None:
        self.style: Optional[str] = None

    def update(self, user_message: str) -> None:
        """Derive a short description of the user's tone.

        The description is stored and later used to rewrite Casey's
        follow‑up questions in a matching style.
        """

        prompt = [
            {"role": "system", "content": "Describe the tone and style of the user's message in a few words."},
            {"role": "user", "content": user_message},
        ]
        try:
            self.style = chat(prompt).strip()
        except Exception:
            self.style = None

    def apply(self, assistant_message: str) -> str:
        """Rewrite ``assistant_message`` in the inferred style."""
        if not self.style:
            return assistant_message
        prompt = [
            {
                "role": "system",
                "content": f"Rewrite the assistant response using this tone: {self.style}"
            },
            {"role": "user", "content": assistant_message},
        ]
        try:
            return chat(prompt).strip()
        except Exception:
            return assistant_message
