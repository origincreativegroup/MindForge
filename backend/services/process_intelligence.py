from __future__ import annotations

"""Process Intelligence Engine for learning and self improvement.

This module provides a lightweight framework that allows processes to
become "self aware" by observing past executions.  The goal is not to be
state of the art but to offer a deterministic and testable reference
implementation that exposes a number of intelligent behaviours:

* Consciousness levels on a 1-5 scale based on the amount of knowledge
  gathered about the process.
* Learning from execution history by building simple transition models.
* Pattern recognition across executions via frequency analysis.
* Anomaly detection for rarely seen steps.
* Prediction of the next best action with a confidence score.
* Self‑improvement suggestions based on anomalies and prediction
  uncertainty.
* A tiny reinforcement learning loop used for optimisation.

The implementation purposely avoids heavy third‑party dependencies so it
can run in a restricted environment (e.g. the unit tests in this
repository).  All data structures are kept in memory which is sufficient
for the small simulated datasets used in tests.
"""

from collections import Counter, defaultdict
from typing import DefaultDict, Dict, Iterable, List, Sequence, Tuple

TransitionCounts = DefaultDict[str, Counter]
QTable = DefaultDict[str, Dict[str, float]]


class ProcessIntelligenceEngine:
    """Engine that captures and reasons about process executions."""

    def __init__(self) -> None:
        self.history: List[List[str]] = []
        # transition_counts[A][B] -> how often step B followed step A
        self.transition_counts: TransitionCounts = defaultdict(Counter)
        self.step_counts: Counter = Counter()
        # simple Q-learning table: state -> action -> value
        self.q_table: QTable = defaultdict(dict)

    # ------------------------------------------------------------------
    # Data ingest & learning
    # ------------------------------------------------------------------
    def record_execution(self, steps: Sequence[str]) -> None:
        """Record a single process execution.

        The execution is represented as an ordered sequence of steps.
        Recording automatically updates transition and step counts which
        act as the "learning" component of the engine.
        """

        seq = list(steps)
        if not seq:
            return
        self.history.append(seq)
        self.step_counts.update(seq)
        for a, b in zip(seq, seq[1:]):
            self.transition_counts[a][b] += 1

    # ------------------------------------------------------------------
    # Consciousness & pattern recognition
    # ------------------------------------------------------------------
    def consciousness_level(self) -> int:
        """Return a naive consciousness level from 1-5.

        The level is derived from the amount of historical information
        the engine has observed.  More executions and unique steps raise
        the level.  Presence of reinforcement learning information bumps
        it to the highest level.
        """

        executions = len(self.history)
        unique_steps = len(self.step_counts)
        if executions == 0:
            return 1
        if executions < 3 or unique_steps < 2:
            return 2
        if executions < 5:
            return 3
        if any(self.q_table.values()):
            return 5
        return 4

    def recognize_patterns(self) -> Dict[str, Tuple[str, int]]:
        """Return the most common next step for each observed step."""

        patterns: Dict[str, Tuple[str, int]] = {}
        for step, counter in self.transition_counts.items():
            if counter:
                nxt, count = counter.most_common(1)[0]
                patterns[step] = (nxt, count)
        return patterns

    # ------------------------------------------------------------------
    # Anomaly detection & prediction
    # ------------------------------------------------------------------
    def detect_anomalies(self, execution: Sequence[str]) -> List[str]:
        """Detect rarely seen steps in *execution*.

        A step is considered anomalous if its frequency is less than half
        the average step frequency observed in the history.
        """

        if not self.step_counts:
            return list(execution)
        avg = sum(self.step_counts.values()) / len(self.step_counts)
        threshold = avg * 0.5
        anomalies = [s for s in execution if self.step_counts[s] < threshold]
        return anomalies

    def predict_next_action(self, execution: Sequence[str]) -> Tuple[str | None, float]:
        """Predict the next action after the provided *execution*.

        Returns a tuple of (step, confidence).  Confidence is the
        probability of the predicted step based on transition counts.
        """

        if not execution:
            return None, 0.0
        last = execution[-1]
        counter = self.transition_counts.get(last)
        if not counter:
            return None, 0.0
        nxt, count = counter.most_common(1)[0]
        total = sum(counter.values())
        confidence = count / total if total else 0.0
        return nxt, confidence

    # ------------------------------------------------------------------
    # Reinforcement learning
    # ------------------------------------------------------------------
    def update_q(self, state: str, action: str, reward: float, *, alpha: float = 0.1, gamma: float = 0.9) -> None:
        """Update the Q-table using the Q-learning rule."""

        old = self.q_table[state].get(action, 0.0)
        future = max(self.q_table[action].values(), default=0.0)
        self.q_table[state][action] = old + alpha * (reward + gamma * future - old)

    def next_best_action(self, state: str) -> str | None:
        """Return the best known action from *state*.

        Falls back to the pattern based prediction if the Q-table has no
        information about the state.
        """

        actions = self.q_table.get(state)
        if actions:
            return max(actions, key=actions.get)
        nxt, _ = self.predict_next_action([state])
        return nxt

    # ------------------------------------------------------------------
    # Self improvement
    # ------------------------------------------------------------------
    def self_improvement_suggestions(self, execution: Sequence[str]) -> List[str]:
        """Generate simple suggestions for improving a process."""

        suggestions: List[str] = []
        anomalies = self.detect_anomalies(execution)
        if anomalies:
            suggestions.append(f"Review unusual steps: {', '.join(anomalies)}")
        nxt, conf = self.predict_next_action(execution)
        if nxt and conf < 0.5:
            suggestions.append(
                f"Prediction for next step '{nxt}' has low confidence ({conf:.2f}). Consider clarifying the process."
            )
        if not suggestions:
            suggestions.append("Process appears stable and well understood.")
        return suggestions


__all__ = ["ProcessIntelligenceEngine"]
