"""Keyword based emotional scoring used by Casey."""

from __future__ import annotations

from typing import Dict

# Mapping of emotions to indicative keywords.  The list is intentionally small
# and purely lexical; it acts as a deterministic stub for more advanced models.
EMOTION_KEYWORDS = {
    "frustration": ["frustrated", "annoyed", "irritating", "redo", "pain"],
    "pride": ["proud", "satisfied", "pleased"],
    "confusion": ["confused", "unsure", "not sure", "uncertain"],
    "eagerness": ["eager", "excited", "can't wait", "keen"],
}


def emotional_scores(text: str) -> Dict[str, float]:
    """Return rudimentary emotion scores for ``text``.

    The score for each emotion is the fraction of its keywords present in the
    lower-cased text, capped at 1.0.  Absence of keywords yields a score of 0.0.
    The function is deliberately lightweight and deterministic, making it easy
    to unit test and safe to run in offline environments.
    """

    lower = text.lower()
    scores: Dict[str, float] = {}
    for emotion, keywords in EMOTION_KEYWORDS.items():
        hits = sum(1 for k in keywords if k in lower)
        scores[emotion] = min(hits / len(keywords), 1.0)
    return scores
