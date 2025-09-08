import sys
from pathlib import Path

# Ensure project root on path for module imports
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root / "apps"))
sys.path.append(str(project_root / "packages"))

from backend.pdl import parser, semantic, codegen, optimizer, visualize, errors


def sample_yaml():
    return """
process:
  name: Sample
  steps:
    - id: start
      type: task
      actor: user
      next: decision1
    - id: decision1
      type: decision
      condition: "x > 0"
      then: end
      else: end
    - id: end
      type: end
"""


def test_parse_and_generate():
    proc = parser.parse(sample_yaml())
    semantic.validate(proc)
    py = codegen.generate_python(proc)
    js = codegen.generate_javascript(proc)
    flow = visualize.to_flowchart(proc)
    opts = optimizer.find_optimizations(proc)

    assert "def run" in py
    assert "function run" in js
    assert flow["nodes"][0]["id"] == "start"
    assert opts == []


def test_semantic_error():
    bad_yaml = """
process:
  name: Bad
  steps:
    - id: a
      type: task
      actor: user
      next: missing
    - id: end
      type: end
"""
    proc = parser.parse(bad_yaml)
    try:
        semantic.validate(proc)
    except errors.PDLSemanticError as exc:
        assert "unknown next step" in str(exc)
    else:
        assert False, "Expected semantic error"
