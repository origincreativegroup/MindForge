from __future__ import annotations

from .ast import Process


def generate_python(proc: Process) -> str:
    lines = ["def run(context):"]
    indent = "    "
    for step in proc.steps:
        lines.append(f"{indent}# {step.id} ({step.type})")
        if step.type == "task":
            lines.append(f"{indent}# actor: {step.actor}")
            if step.next:
                lines.append(f"{indent}next_step = '{step.next}'")
        elif step.type == "decision":
            cond = step.condition or "False"
            then = step.branches.get("then")
            other = step.branches.get("else")
            lines.append(f"{indent}if eval(\"{cond}\", {{}}, context):")
            lines.append(f"{indent*2}next_step = '{then}'")
            lines.append(f"{indent}else:")
            lines.append(f"{indent*2}next_step = '{other}'")
        elif step.type == "end":
            lines.append(f"{indent}next_step = None")
        lines.append(f"{indent}yield '{step.id}', next_step")
    return "\n".join(lines)


def generate_javascript(proc: Process) -> str:
    lines = ["function run(context) {"]
    indent = "    "
    for step in proc.steps:
        lines.append(f"{indent}// {step.id} ({step.type})")
        if step.type == "task":
            lines.append(f"{indent}// actor: {step.actor}")
            if step.next:
                lines.append(f"{indent}let next_step = '{step.next}';")
        elif step.type == "decision":
            cond = step.condition or "false"
            then = step.branches.get("then")
            other = step.branches.get("else")
            lines.append(f'{indent}if (eval("{cond}")) {{')
            lines.append(f"{indent*2}next_step = '{then}';")
            lines.append(f'{indent}}} else {{')
            lines.append(f"{indent*2}next_step = '{other}';")
            lines.append(f'{indent}}}')
        elif step.type == "end":
            lines.append(f"{indent}next_step = null;")
        lines.append(f"{indent}yield ['{step.id}', next_step];")
    lines.append("}")
    return "\n".join(lines)
