from __future__ import annotations

from .ast import Process


def find_optimizations(proc: Process) -> list[str]:
    """Find simple optimization opportunities."""

    suggestions: list[str] = []
    for s1, s2 in zip(proc.steps, proc.steps[1:], strict=False):
        if (
            s1.type == "task"
            and s2.type == "task"
            and s1.actor
            and s1.actor == s2.actor
        ):
            suggestions.append(
                f"Steps '{s1.id}' and '{s2.id}' performed by '{s1.actor}' could be merged"
            )
    return suggestions
