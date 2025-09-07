from __future__ import annotations

"""Minimal PDL YAML parser.

This module originally relied on the external :mod:`yaml` package.  The
execution environment used for the kata, however, doesn't provide PyYAML and
installing new dependencies at test time isn't desirable.  The tests only need
very small YAML files describing processes, so we provide a tiny fallback parser
that understands just enough of YAML for these structures.  If PyYAML is
available we still prefer it as it's far more robust.
"""

from typing import Any, Dict, List

try:  # pragma: no cover - exercised implicitly when available
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - executed in the kata env
    yaml = None  # type: ignore

from .ast import Process, Step
from .errors import PDLParseError


def _simple_yaml_load(text: str) -> Dict[str, Any]:
    """Parse a very small subset of YAML used in the tests.

    The supported structure is a mapping containing a ``process`` key with
    ``name`` and ``steps`` fields.  ``steps`` is a list of mappings describing
    each step.  Only string scalar values are understood.  The parser is
    indentation based and assumes two space indents.

    This is **not** a general purpose YAML parser but keeps the tests
    lightweight when PyYAML isn't installed.
    """

    lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()]

    def indent_of(line: str) -> int:
        return len(line) - len(line.lstrip(" "))

    idx = 0

    def parse_block(expected_indent: int) -> Any:
        nonlocal idx
        items: Dict[str, Any] = {}
        while idx < len(lines):
            line = lines[idx]
            current_indent = indent_of(line)
            if current_indent < expected_indent:
                break

            line = line.strip()
            if line.startswith("-"):
                # parse list items
                result = []
                while idx < len(lines):
                    line = lines[idx]
                    if indent_of(line) != expected_indent or not line.strip().startswith("-"):
                        break
                    content = line.strip()[1:].strip()
                    idx += 1
                    item: Dict[str, Any] = {}
                    if content:
                        key, value = content.split(":", 1)
                        item[key.strip()] = _strip(value)
                    # parse nested fields for this list item
                    item.update(parse_block(expected_indent + 2))
                    result.append(item)
                return result

            # key/value pair
            idx += 1
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value:
                items[key] = _strip(value)
            else:
                # nested structure
                items[key] = parse_block(expected_indent + 2)
        return items

    def _strip(value: str) -> str:
        value = value.strip()
        if (value.startswith("\"") and value.endswith("\"")) or (
            value.startswith("'") and value.endswith("'")
        ):
            return value[1:-1]
        return value

    return parse_block(0)


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

    if yaml is not None:  # pragma: no branch - simple runtime check
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as exc:  # pragma: no cover - represents yaml failure
            raise PDLParseError(str(exc)) from exc
    else:
        try:
            data = _simple_yaml_load(text)
        except Exception as exc:  # pragma: no cover - defensive
            raise PDLParseError(str(exc)) from exc

    if not isinstance(data, dict) or "process" not in data:
        raise PDLParseError("Root must contain 'process'")
    pdata = data["process"]
    name = pdata.get("name", "")
    raw_steps: List[Dict[str, Any]] = pdata.get("steps", [])
    steps = [_parse_step(s) for s in raw_steps]
    return Process(name=name, steps=steps)
