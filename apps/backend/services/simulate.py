from typing import Dict, List
import re

RISK_KEYWORDS = ['approve', 'approval', 'handoff', 'wait', 'waiting', 'manual', 'review', 'escalate', 'queue']

def score_step(step: str, frustration_bias: float = 0.0) -> float:
    s = step.lower()
    score = 1.0
    for k in RISK_KEYWORDS:
        if k in s:
            score += 1.0
    # slightly boost longer, vaguer steps
    if len(s) > 60:
        score += 0.5
    # incorporate frustration signal
    score += frustration_bias
    return score

def simulate(process: Dict[str, List[str]], recent_emotions: List[str], scale: float = 1.0) -> Dict[str, any]:
    steps = process.get('steps', []) or []
    # compute frustration bias from recent emotions
    fbias = 0.3 if any(e in ('frustrated','concerned') for e in recent_emotions[-5:]) else 0.0
    scores = [(i, st, score_step(st, fbias)) for i, st in enumerate(steps)]
    # scale inflates risk
    scores = [(i, st, sc * max(1.0, scale)) for (i, st, sc) in scores]
    # find top
    top = max(scores, key=lambda x: x[2]) if scores else None
    summary = "Not enough structure to simulate." if not steps else f"Projected bottleneck under scale x{scale:.1f}: step {top[0]+1} — “{top[1]}”"
    return {
        "scale": scale,
        "scores": [{"index": i, "step": st, "risk": sc} for (i, st, sc) in scores],
        "bottleneck_index": top[0] if top else None,
        "bottleneck_step": top[1] if top else None,
        "summary": summary,
    }
