"""API endpoints for the Workforce Intelligence Matrix."""

from fastapi import APIRouter
from pydantic import BaseModel

from ..services import workforce_matrix


class TaskRequest(BaseModel):
    description: str


class ScenarioRequest(BaseModel):
    description: str
    complexity_delta: float = 0.0
    human_value_delta: float = 0.0


class RebalanceRequest(BaseModel):
    growth: float


router = APIRouter(prefix="/workforce", tags=["workforce"])


@router.post("/classify")
def classify_task(req: TaskRequest):
    """Return quadrant classification and metrics for a task."""

    metrics = workforce_matrix.evaluate_task(req.description)
    return metrics.to_dict()


@router.post("/scenario")
def scenario(req: ScenarioRequest):
    """Evaluate a what-if scenario for a task."""

    metrics = workforce_matrix.evaluate_scenario(
        req.description, req.complexity_delta, req.human_value_delta
    )
    return metrics.to_dict()


@router.post("/rebalance")
def rebalance(req: RebalanceRequest):
    """Update thresholds to reflect capability growth."""

    workforce_matrix.rebalance_capabilities(req.growth)
    return {"thresholds": workforce_matrix.THRESHOLDS}
