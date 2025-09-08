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

from typing import Any, Dict, List, Tuple, Union

# ``yaml`` is an optional dependency.  The test environment used for these
# exercises does not always provide external packages, so we gracefully fall
# back to a tiny YAML parser that supports just the subset of syntax required
# by the unit tests.
try:  # pragma: no cover - exercised indirectly in tests
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback for offline envs
    import json

    def _parse_value(text: str) -> Any:
        """Parse a scalar YAML value into an appropriate Python object."""

        if text.isdigit():
            return int(text)
        lowered = text.lower()
        if lowered in {"true", "false"}:
            return lowered == "true"
        if (text.startswith("\"") and text.endswith("\"")) or (
            text.startswith("'") and text.endswith("'")
        ):
            return text[1:-1]
        return text

    def _simple_safe_load(data: str) -> Dict[str, Any]:
        """Very small YAML loader supporting mappings and lists."""

        lines = [ln.rstrip() for ln in data.splitlines() if ln.strip()]
        result: Dict[str, Any] = {}
        stack: List[Tuple[int, Any]] = [(0, result)]
        i = 0
        while i < len(lines):
            line = lines[i]
            indent = len(line) - len(line.lstrip())
            stripped = line.lstrip()
            while stack and indent < stack[-1][0]:
                stack.pop()
            container = stack[-1][1]

            if stripped.startswith("- "):
                if not isinstance(container, list):
                    raise PDLParseError("Invalid YAML structure")
                item: Dict[str, Any] = {}
                after = stripped[2:]
                if after:
                    if ":" in after:
                        k, v = after.split(":", 1)
                        item[k.strip()] = _parse_value(v.strip())
                container.append(item)
                stack.append((indent + 2, item))
                i += 1
                continue

            if ":" in stripped:
                k, v = stripped.split(":", 1)
                k = k.strip()
                v = v.strip()
                if v == "":
                    # Decide whether the upcoming block is a list or mapping
                    next_line = lines[i + 1] if i + 1 < len(lines) else ""
                    next_indent = len(next_line) - len(next_line.lstrip())
                    next_stripped = next_line.lstrip()
                    if next_stripped.startswith("- ") and next_indent > indent:
                        new_val: Any = []
                    else:
                        new_val = {}
                    if isinstance(container, list):
                        container.append({k: new_val})
                    else:
                        container[k] = new_val
                    stack.append((indent + 2, new_val))
                else:
                    val = _parse_value(v)
                    if isinstance(container, list):
                        container.append({k: val})
                    else:
                        container[k] = val
            else:
                raise PDLParseError("Invalid YAML structure")
            i += 1
        return result

    class _YamlModule:
        @staticmethod
        def safe_load(data: str) -> Dict[str, Any]:
            return _simple_safe_load(data)

    yaml = _YamlModule()

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

