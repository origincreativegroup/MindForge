"""Workforce Intelligence Matrix service.

This module provides lightweight scoring algorithms to evaluate tasks and
categorise them into automation quadrants.  The implementation is intentionally
simple – its goal is to act as a placeholder for a more sophisticated
Workforce Intelligence system.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

# Thresholds controlling quadrant classification.
THRESHOLDS = {
    "automate_potential": 0.7,
    "semi_potential": 0.5,
    "complexity_limit": 0.6,
    "human_value_limit": 0.5,
}


@dataclass
class TaskMetrics:
    """Container for calculated task metrics."""

    description: str
    complexity: float
    human_value: float
    automation_potential: float
    quadrant: str
    roi: float
    migration_path: str

    def to_dict(self) -> dict[str, float | str]:
        return asdict(self)


def compute_complexity(description: str) -> float:
    """Naive task complexity score based on word count.

    A longer description implies a more complex task.  The score is scaled to a
    0‑1 range.
    """

    words = len(description.split())
    return min(1.0, words / 50)


def assess_human_value(description: str) -> float:
    """Estimate the human value of a task.

    The heuristic counts how many "human centric" terms appear in the
    description.  More matches imply higher human value.
    """

    value_words = {
        "strategy",
        "strategic",
        "creative",
        "empathy",
        "leadership",
        "innovation",
        "relationship",
    }
    tokens = {t.strip(".,").lower() for t in description.split()}
    score = len(tokens & value_words) / len(value_words)
    return min(1.0, score)


def calculate_automation_potential(complexity: float, human_value: float) -> float:
    """Simple automation potential calculator.

    Tasks with low complexity and low human value have the highest automation
    potential.
    """

    return max(0.0, 1 - (0.5 * complexity + human_value))


def classify_quadrant(
    complexity: float, human_value: float, automation_potential: float
) -> str:
    """Classify the task into one of four quadrants."""

    if automation_potential > THRESHOLDS["automate_potential"] and human_value < 0.3:
        return "Automate"
    if (
        automation_potential > THRESHOLDS["semi_potential"]
        and complexity < THRESHOLDS["complexity_limit"]
    ):
        return "Semi-Automate"
    if human_value < THRESHOLDS["human_value_limit"]:
        return "AI Copilot"
    return "Human-Led"


def predict_roi(automation_potential: float, human_value: float) -> float:
    """Very rough ROI estimation.

    ROI increases with automation potential and decreases with human value.
    The numbers do not represent any real currency; they simply provide a
    relative comparison between tasks.
    """

    return round(automation_potential * 100 - human_value * 50, 2)


def migration_path(quadrant: str) -> str:
    """Suggest next steps to move a task towards a better quadrant."""

    paths = {
        "Automate": "Deploy RPA or scripting solutions",
        "Semi-Automate": "Combine automation with human oversight",
        "AI Copilot": "Use assistant tools to augment workers",
        "Human-Led": "Invest in human training and expertise",
    }
    return paths.get(quadrant, "Review task details")


def rebalance_capabilities(growth: float) -> None:
    """Dynamically adjust classification thresholds as capabilities evolve."""

    THRESHOLDS["automate_potential"] = max(
        0.5, THRESHOLDS["automate_potential"] - growth
    )
    THRESHOLDS["semi_potential"] = max(0.3, THRESHOLDS["semi_potential"] - growth / 2)


def evaluate_task(description: str) -> TaskMetrics:
    """Evaluate a task and return metrics."""

    complexity = compute_complexity(description)
    human_value = assess_human_value(description)
    automation_potential = calculate_automation_potential(complexity, human_value)
    quadrant = classify_quadrant(complexity, human_value, automation_potential)
    roi = predict_roi(automation_potential, human_value)
    path = migration_path(quadrant)
    return TaskMetrics(
        description=description,
        complexity=complexity,
        human_value=human_value,
        automation_potential=automation_potential,
        quadrant=quadrant,
        roi=roi,
        migration_path=path,
    )


def evaluate_scenario(
    description: str, complexity_delta: float = 0.0, human_value_delta: float = 0.0
) -> TaskMetrics:
    """Model a what-if scenario by adjusting scores before classification."""

    metrics = evaluate_task(description)
    metrics.complexity = max(0.0, min(1.0, metrics.complexity + complexity_delta))
    metrics.human_value = max(0.0, min(1.0, metrics.human_value + human_value_delta))
    metrics.automation_potential = calculate_automation_potential(
        metrics.complexity, metrics.human_value
    )
    metrics.quadrant = classify_quadrant(
        metrics.complexity, metrics.human_value, metrics.automation_potential
    )
    metrics.roi = predict_roi(metrics.automation_potential, metrics.human_value)
    metrics.migration_path = migration_path(metrics.quadrant)
    return metrics
