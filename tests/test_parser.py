import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root / "apps"))
sys.path.append(str(project_root / "packages"))

from backend.services.parser import parse_response


def test_parse_response_extracts_elements():
    text = (
        "First the manager checks the form. Then the system sends an email. "
        "If approved, the supervisor files it."
    )
    result = parse_response(text)
    assert len(result["steps"]) == 3
    assert "manager" in result["actors"]
    assert "email" in result["tools"]
    assert result["decisions"] == ["If approved, the supervisor files it"]
