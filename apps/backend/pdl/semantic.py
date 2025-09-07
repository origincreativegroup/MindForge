from __future__ import annotations

from .ast import Process
from .errors import PDLSemanticError


def validate(proc: Process) -> None:
    """Validate semantic correctness of a process."""

    ids: set[str] = set()
    for step in proc.steps:
        if step.id in ids:
            raise PDLSemanticError(f"Duplicate step id '{step.id}'")
        ids.add(step.id)
        if step.type == "task" and not step.actor:
            raise PDLSemanticError(f"Task '{step.id}' requires an actor")

    id_set = set(ids)
    for step in proc.steps:
        if step.next and step.next not in id_set:
            raise PDLSemanticError(
                f"Step '{step.id}' references unknown next step '{step.next}'"
            )
        for label, dest in step.branches.items():
            if dest not in id_set:
                raise PDLSemanticError(
                    f"Step '{step.id}' branch '{label}' references unknown step '{dest}'"
                )

    if proc.steps and proc.steps[-1].type != "end":
        raise PDLSemanticError("Last step must be of type 'end'")
