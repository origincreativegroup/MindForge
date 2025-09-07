import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from backend.services.process_intelligence import ProcessIntelligenceEngine


def build_engine():
    engine = ProcessIntelligenceEngine()
    # three typical successful executions
    engine.record_execution(["start", "review", "approve", "end"])
    engine.record_execution(["start", "review", "approve", "end"])
    engine.record_execution(["start", "review", "revise", "review", "approve", "end"])
    return engine


def test_prediction_engine():
    engine = build_engine()
    step, conf = engine.predict_next_action(["start", "review"])
    assert step == "approve"
    assert conf > 0.5


def test_anomaly_detection_and_suggestions():
    engine = build_engine()
    anomalies = engine.detect_anomalies(["start", "review", "hack", "end"])
    assert "hack" in anomalies
    suggestions = engine.self_improvement_suggestions(["start", "review", "hack"])
    assert any("unusual" in s for s in suggestions)


def test_reinforcement_learning():
    engine = build_engine()
    engine.update_q("review", "approve", reward=1.0)
    engine.update_q("review", "revise", reward=0.0)
    assert engine.next_best_action("review") == "approve"


def test_consciousness_levels():
    engine = ProcessIntelligenceEngine()
    assert engine.consciousness_level() == 1
    engine.record_execution(["start", "end"])
    assert engine.consciousness_level() >= 2
    engine.record_execution(["start", "review", "end"])
    engine.record_execution(["start", "review", "approve", "end"])
    assert engine.consciousness_level() >= 3
