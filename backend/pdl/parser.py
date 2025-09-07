from __future__ import annotations

import yaml
from typing import Any, Dict, List

from .ast import Process, Step
from .errors import PDLParseError


def _parse_step(raw: Dict[str, Any]) -> Step:
    if "id" not in raw or "type" not in raw:
        raise PDLParseError("Each step requires 'id' and 'type'")
    branches = {}
    if "then" in raw:
        branches["then"] = raw["then"]
    if "else" in raw:
        branches["else"] = raw["else"]
    return Step(
        id=raw["id"],
        type=raw["type"],
        actor=raw.get("actor"),
        next=raw.get("next"),
        condition=raw.get("condition"),
        branches=branches,
    )


def parse(text: str) -> Process:
    """Parse a YAML PDL definition into an AST."""

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:  # pragma: no cover - represents yaml failure
        raise PDLParseError(str(exc)) from exc

    if not isinstance(data, dict) or "process" not in data:
        raise PDLParseError("Root must contain 'process')")
    pdata = data["process"]
    name = pdata.get("name", "")
    raw_steps: List[Dict[str, Any]] = pdata.get("steps", [])
    steps = [_parse_step(s) for s in raw_steps]
    return Process(name=name, steps=steps)
