from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Step:
    """Represents a single process step."""

    id: str
    type: str
    actor: Optional[str] = None
    next: Optional[str] = None
    condition: Optional[str] = None
    branches: Dict[str, str] = field(default_factory=dict)


@dataclass
class Process:
    """Top level process definition."""

    name: str
    steps: List[Step]

    def step_map(self) -> Dict[str, Step]:
        return {s.id: s for s in self.steps}
