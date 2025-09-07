import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root / "apps"))
sys.path.append(str(project_root / "packages"))

from backend.services.emotions import emotional_scores


def test_emotional_scores_keywords():
    text = (
        "I'm proud of the team but a bit confused by the new tool and it's "
        "frustrating to redo steps."
    )
    scores = emotional_scores(text)
    assert scores["pride"] > 0
    assert scores["confusion"] > 0
    assert scores["frustration"] > 0
    assert scores["eagerness"] == 0
