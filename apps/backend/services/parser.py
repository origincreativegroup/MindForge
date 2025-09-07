"""Simple heuristics for extracting process elements from text.

This module implements a light-weight parser used during conversations with
Casey.  The goal is not perfect linguistic analysis but to capture obvious
mentions of steps, actors, tools and decisions so that downstream components can
reason about the process being described.
"""

from __future__ import annotations

import re

# Regular expressions for different element types -----------------------------
ACTOR_PATTERN = re.compile(
    r"\b(manager|supervisor|system|user|staff|employee|customer|receptionist)\b",
    re.I,
)
TOOL_PATTERN = re.compile(
    r"\b(spreadsheet|software|portal|email|form|tool)\b",
    re.I,
)
DECISION_PATTERN = re.compile(
    r"\b(if|otherwise|decision|approve|reject)\b",
    re.I,
)


def parse_response(text: str) -> dict[str, list[str]]:
    """Extract rudimentary process elements from ``text``.

    Parameters
    ----------
    text:
        Natural language description of a process fragment.

    Returns
    -------
    dict
        Dictionary containing ``steps``, ``actors``, ``tools`` and
        ``decisions`` lists.  The extraction is intentionally shallow but
        deterministic which makes it suitable for unit tests and for acting as
        a placeholder until a more sophisticated NLP pipeline is added.
    """

    lowered = text.lower()

    # Steps are approximated by splitting into sentences
    sentences = [s.strip() for s in re.split(r"[.]+\s*", text) if s.strip()]

    actors = sorted({m.group(0).lower() for m in ACTOR_PATTERN.finditer(lowered)})
    tools = sorted({m.group(0).lower() for m in TOOL_PATTERN.finditer(lowered)})

    decisions = [s for s in sentences if DECISION_PATTERN.search(s)]

    return {
        "steps": sentences,
        "actors": actors,
        "tools": tools,
        "decisions": decisions,
    }
