from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models
from ..db import get_db
from ..services.llm_client import chat
from ..services.memory import summarize_context
from ..services.prompts import ENGAGING_SYSTEM, engaging_next_user

router = APIRouter()

STAGES = {
    "scope",
    "actors",
    "steps",
    "decisions",
    "io",
    "exceptions",
    "metrics",
    "automation",
}


def guess_stage(proc) -> str:
    # Simple heuristic: pick the next empty area
    if not proc or not isinstance(proc, dict):
        return "scope"
    if not (proc.get("steps") or []):
        return "steps"
    if not (proc.get("actors") or []):
        return "actors"
    if not (proc.get("decisions") or []):
        return "decisions"
    return "metrics"


@router.get("/conversations/{conversation_id}/next_question")
def next_question(
    conversation_id: int, stage: str | None = Query(None), db: Session = Depends(get_db)
):
    conv = db.query(models.Conversation).get(conversation_id)
    if not conv:
        raise HTTPException(404, "Conversation not found")
    history_plain = summarize_context([m.content for m in conv.messages], max_len=2000)
    latest = (
        db.query(models.ProcessMap)
        .filter_by(conversation_id=conversation_id)
        .order_by(models.ProcessMap.created_at.desc())
        .first()
    )
    proc = {
        "steps": latest.steps if latest else [],
        "actors": latest.actors if latest else [],
        "decisions": latest.decisions if latest else [],
    }
    # negative tone hint
    last_user = next((m for m in conv.messages[::-1] if m.role == "user"), None)
    neg = False
    if last_user and any(
        x in (last_user.emotion or "").lower()
        for x in ["frustrated", "angry", "blocked", "confused", "tired"]
    ):
        neg = True
    if stage and stage not in STAGES:
        raise HTTPException(400, "Invalid stage")
    focus = stage or guess_stage(proc)
    messages = [
        {"role": "system", "content": ENGAGING_SYSTEM},
        {"role": "user", "content": engaging_next_user(history_plain, focus, neg)},
    ]
    q = (
        chat(messages, temperature=0.4).strip()
        or "Can you walk me through the very next concrete action and who does it?"
    )
    # persist
    am = models.Message(conversation_id=conversation_id, role="assistant", content=q)
    db.add(am)
    db.commit()
    return {"question": q, "stage": focus}
