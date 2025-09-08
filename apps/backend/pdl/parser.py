"""Simple parser for the Process Description Language (PDL).

The original project ships with a much more sophisticated ANTLR based parser
but for the unit tests in this kata we only need a very small subset of the
functionality.  The parser implemented here is intentionally lightweight: it
parses a YAML representation of a process into the dataclasses defined in
``apps.backend.pdl.ast`` and performs minimal validation.  Any structural
problems are reported via ``PDLParseError`` which mirrors the behaviour of the
real parser.
"""

from __future__ import annotations

from typing import Any, Dict, List, Union

import yaml

from .ast import Process, Step
from .errors import PDLParseError


def _parse_step(raw: Dict[str, Any]) -> Step:
    """Convert a raw mapping into a :class:`Step` instance."""

    if not isinstance(raw, dict) or "id" not in raw or "type" not in raw:
        raise PDLParseError("Each step requires 'id' and 'type'")

    branches: Dict[str, str] = {}
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


def parse(data: Union[str, Dict[str, Any]]) -> Process:
    """Parse a YAML string or pre-loaded dictionary into a ``Process``.

    Parameters
    ----------
    data:
        Either a YAML string or a dictionary representing the process.
    """

    if isinstance(data, str):
        try:
            data = yaml.safe_load(data)
        except Exception as exc:  # pragma: no cover - yaml library errors
            raise PDLParseError("Invalid YAML") from exc

    if not isinstance(data, dict) or "process" not in data:
        raise PDLParseError("Root must contain 'process'")

    pdata = data["process"]
    if not isinstance(pdata, dict):
        raise PDLParseError("'process' must be a mapping")

    name = pdata.get("name", "")
    raw_steps = pdata.get("steps", [])
    if not isinstance(raw_steps, list):
        raise PDLParseError("'steps' must be a list")

    steps: List[Step] = [_parse_step(step) for step in raw_steps]
    return Process(name=name, steps=steps)


__all__ = ["parse"]

