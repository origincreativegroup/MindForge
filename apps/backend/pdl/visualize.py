from __future__ import annotations

from .ast import Process


def to_flowchart(proc: Process) -> dict[str, list[dict[str, str]]]:
    nodes = [{"id": s.id, "type": s.type, "actor": s.actor or ""} for s in proc.steps]
    edges: list[dict[str, str]] = []
    for s in proc.steps:
        if s.next:
            edges.append({"from": s.id, "to": s.next, "label": ""})
        for label, dest in s.branches.items():
            edges.append({"from": s.id, "to": dest, "label": label})
    return {"nodes": nodes, "edges": edges}


def to_mermaid(proc: Process) -> str:
    lines = ["flowchart TD"]
    for s in proc.steps:
        label = f"{s.id}[{s.type}]"
        lines.append(label)
    for s in proc.steps:
        if s.next:
            lines.append(f"{s.id} --> {s.next}")
        for label, dest in s.branches.items():
            lines.append(f"{s.id} --|{label}| {dest}")
    return "\n".join(lines)
