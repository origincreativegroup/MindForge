import sys
from pathlib import Path

# Ensure project root on path for module imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.services.memory import ShortTermMemory


def test_buffer_rollover():
    mem = ShortTermMemory(max_turns=3)
    for i in range(5):
        mem.add("user", f"u{i}")
    tx = mem.transcript()
    assert "u0" not in tx and "u4" in tx
