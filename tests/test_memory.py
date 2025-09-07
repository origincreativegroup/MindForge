import sys
from pathlib import Path

# Ensure project root on path for module imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.services.memory import ContextMemory, ShortTermMemory


def test_buffer_rollover():
    mem = ShortTermMemory(max_turns=3)
    for i in range(5):
        mem.add("user", f"u{i}")
    tx = mem.transcript()
    assert "u0" not in tx and "u4" in tx


def test_context_memory_tracks_data():
    mem = ContextMemory(max_turns=2)
    mem.add_turn("user", "hello")
    mem.add_process_elements({"steps": ["s1"]})
    mem.add_emotions({"pride": 1.0})
    mem.add_turn("assistant", "hi")

    assert "hello" in mem.transcript()
    assert mem.process[-1]["steps"] == ["s1"]
    assert mem.latest_emotion()["pride"] == 1.0
