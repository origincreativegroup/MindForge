from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Step:
    """Represents a single process step."""

    id: str
    type: str
    actor: str | None = None
    next: str | None = None
    condition: str | None = None
    branches: dict[str, str] = field(default_factory=dict)


@dataclass
class Process:
    """Top level process definition."""

    name: str
    steps: list[Step]

    def step_map(self) -> dict[str, Step]:
        return {s.id: s for s in self.steps}
