from backend.services import workforce_matrix


def test_basic_classification():
    metrics = workforce_matrix.evaluate_task("Data entry into spreadsheet")
    assert metrics.quadrant == "Automate"
    assert metrics.roi > 0

    metrics2 = workforce_matrix.evaluate_task(
        "Creative strategic leadership meeting with empathy"
    )
    assert metrics2.quadrant == "Human-Led"


def test_scenario_modeling():
    metrics = workforce_matrix.evaluate_scenario(
        "Data entry into spreadsheet", complexity_delta=0.2
    )
    assert (
        metrics.complexity
        > workforce_matrix.evaluate_task("Data entry into spreadsheet").complexity
    )
