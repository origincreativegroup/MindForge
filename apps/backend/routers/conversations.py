from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from fastapi.responses import StreamingResponse, JSONResponse, RedirectResponse, HTMLResponse
from ..db import get_db, Base, engine
from .. import models, schemas
from ..services.scoring import score_emotion
from ..services.extractor import extract_process
from ..services.interviewer import next_questions
from ..services.mirror import mirror_understanding
from ..services.uploads import parse_uploaded
from ..services.simulate import simulate

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="templates")

router = APIRouter()

Base.metadata.create_all(bind=engine)

@router.post("/conversations", response_model=schemas.ConversationOut)
def create_conversation(payload: schemas.ConversationCreate, db: Session = Depends(get_db)):
    conv = models.Conversation(title=payload.title or "Untitled")
    db.add(conv); db.commit(); db.refresh(conv)
    greet = models.Message(conversation_id=conv.id, role="assistant",
                           content="Hi, I'm Casey. Let's map how your work *actually* happens.")
    db.add(greet); db.commit()
    return conv

@router.get("/conversations", response_model=List[schemas.ConversationOut])
def list_conversations(db: Session = Depends(get_db)):
    rows = db.query(models.Conversation).order_by(models.Conversation.created_at.desc()).all()
    return rows

@router.get("/conversations/{conversation_id}/latest_process")
def latest_process(conversation_id: int, db: Session = Depends(get_db)):
    conv = db.query(models.Conversation).get(conversation_id)
    if not conv: raise HTTPException(404, "Conversation not found")
    latest = db.query(models.ProcessMap).filter_by(conversation_id=conversation_id).order_by(models.ProcessMap.created_at.desc()).first()
    if not latest:
        return {"steps": [], "actors": [], "tools": [], "decisions": []}
    return {
        "steps": latest.steps or [],
        "actors": latest.actors or [],
        "tools": latest.tools or [],
        "decisions": latest.decisions or [],
        "raw_chunks": latest.raw_chunks or [],
        "created_at": latest.created_at.isoformat()
    }

@router.post("/conversations/{conversation_id}/message")
def send_message(conversation_id: int, payload: schemas.ChatTurn, db: Session = Depends(get_db)):
    conv = db.query(models.Conversation).get(conversation_id)
    if not conv: raise HTTPException(404, "Conversation not found")
    emo = score_emotion(payload.user_text)
    um = models.Message(conversation_id=conversation_id, role="user", content=payload.user_text, emotion=emo)
    db.add(um); db.commit()
    user_texts = [m.content for m in conv.messages if m.role == "user"] + [payload.user_text]
    extraction = extract_process(user_texts)
    pm = models.ProcessMap(conversation_id=conversation_id, **extraction)
    db.add(pm); db.commit()
    history = [m.content for m in conv.messages] + [payload.user_text]
    question = next_questions(history, str(conversation_id))[0]
    am = models.Message(conversation_id=conversation_id, role="assistant", content=question)
    db.add(am); db.commit()
    return {"assistant": question, "emotion": emo, "extraction_snapshot": extraction}

@router.get("/conversations/{conversation_id}/message_stream")
def send_message_stream(
    conversation_id: int,
    content: str,
    db: Session = Depends(get_db),
):
    conv = db.query(models.Conversation).get(conversation_id)
    if not conv: raise HTTPException(404, "Conversation not found")
    emo = score_emotion(content)
    um = models.Message(conversation_id=conversation_id, role="user", content=content, emotion=emo)
    db.add(um); db.commit()

    user_texts = [m.content for m in conv.messages if m.role == "user"] + [content]
    extraction = extract_process(user_texts)
    pm = models.ProcessMap(conversation_id=conversation_id, **extraction)
    db.add(pm); db.commit()

    history = [m.content for m in conv.messages] + [content]
    question = next_questions(history, str(conversation_id))[0]

    def gen():
        yield f"data: {question}\n\n"
        am = models.Message(conversation_id=conversation_id, role="assistant", content=question)
        db.add(am); db.commit()
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")

@router.post("/conversations/{conversation_id}/upload")
async def upload(conversation_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    conv = db.query(models.Conversation).get(conversation_id)
    if not conv: raise HTTPException(404, "Conversation not found")
    content = await file.read()
    kind, summary = parse_uploaded(file.filename, content)
    text = f"[Uploaded {kind} {file.filename}]\n{summary}"
    emo = score_emotion(text)
    um = models.Message(conversation_id=conversation_id, role="user", content=text, emotion=emo)
    db.add(um); db.commit()
    user_texts = [m.content for m in conv.messages if m.role == "user"] + [text]
    extraction = extract_process(user_texts)
    pm = models.ProcessMap(conversation_id=conversation_id, **extraction)
    db.add(pm); db.commit()
    return {"status": "ok", "kind": kind, "preview_len": len(summary)}

@router.get("/conversations/{conversation_id}/mirror")
def mirror(conversation_id: int, db: Session = Depends(get_db)):
    conv = db.query(models.Conversation).get(conversation_id)
    if not conv: raise HTTPException(404, "Conversation not found")
    history_texts = [m.content for m in conv.messages]
    text = mirror_understanding(history_texts)
    return {"mirror": text}

@router.get("/conversations/{conversation_id}/simulate")
def simulate_route(conversation_id: int, scale: float = 1.0, db: Session = Depends(get_db)):
    conv = db.query(models.Conversation).get(conversation_id)
    if not conv: raise HTTPException(404, "Conversation not found")
    latest = db.query(models.ProcessMap).filter_by(conversation_id=conversation_id).order_by(models.ProcessMap.created_at.desc()).first()
    if not latest:
        return {"summary": "No process extracted yet."}
    recent_emotions = [m.emotion for m in conv.messages if m.role == "user"]
    result = simulate({
        "steps": latest.steps or [],
        "actors": latest.actors or [],
        "tools": latest.tools or [],
        "decisions": latest.decisions or [],
    }, recent_emotions=recent_emotions, scale=scale)
    return result

@router.get("/export")
def export_data(db: Session = Depends(get_db)):
    convs = db.query(models.Conversation).all()
    procs = db.query(models.ProcessMap).all()
    out = {
        "conversations": [
            {
                "id": c.id,
                "title": c.title,
                "created_at": c.created_at.isoformat(),
                "messages": [
                    {"role": m.role, "content": m.content, "emotion": m.emotion, "created_at": m.created_at.isoformat()}
                    for m in c.messages
                ],
            }
            for c in convs
        ],
        "processes": [
            {
                "conversation_id": p.conversation_id,
                "steps": p.steps, "actors": p.actors, "tools": p.tools, "decisions": p.decisions,
                "raw_chunks": p.raw_chunks, "created_at": p.created_at.isoformat()
            }
            for p in procs
        ],
    }
    return out
