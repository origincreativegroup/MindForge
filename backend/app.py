from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio, re, time

BASE = Path(__file__).parent
app = FastAPI(title="Casey · MindForge", debug=True)
(BASE/"static").mkdir(exist_ok=True); (BASE/"templates").mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(BASE/"static")), name="static")
templates = Jinja2Templates(directory=str(BASE/"templates"))

# ---- tiny in-memory convo store for demo ----
STATE = {"messages": [], "process": {"steps": [], "actors": [], "tools": [], "decisions": []}}

def infer_tone(text: str) -> str:
    if not text: return "warm"
    t = text.lower()
    neg = any(w in t for w in ["angry","frustrated","blocked","confused","tired","annoyed","overwhelmed"])
    terse = len(t) < 40 and t.endswith("?") is False
    expert = any(w in t for w in ["sla","throughput","kpi","slo","sprint","backlog","okrs","latency"])
    if expert: return "expert"
    if neg: return "gentle"
    if terse: return "direct"
    return "warm"

def reply_for(text: str) -> str:
    tone = infer_tone(text)
    if tone == "gentle":
        pre = "Quick gut-check—I'll keep this light. "
    else:
        pre = ""
    # simple “next best question” that nudges structure
    if "?" in text:
        ask = "What’s the very next concrete action, and who does it?"
    else:
        ask = "Who owns the first step and what tool do they touch?"
    return pre + ask

def extract_steps_from(text: str):
    # toy extractor: split on arrows or sentences with verbs
    parts = re.split(r"\s*(?:->|→|=>)\s*", text)
    if len(parts) >= 2:
        return [p.strip().rstrip(".") for p in parts if p.strip()]
    # fallback: sentencey splits
    sents = re.split(r"[.]\s+|\n+", text)
    steps = [s.strip() for s in sents if re.search(r"\b(\w+ing|create|submit|review|approve|send|triage|validate)\b", s, re.I)]
    return steps[:8]

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    Conv = type("Conv", (), {})
    conv = Conv(); conv.id = 1; conv.messages = STATE["messages"]; conv.processes = [STATE["process"]] if STATE["process"]["steps"] else []
    return templates.TemplateResponse("chat.html", {"request": request, "title": "Casey", "conv": conv})

@app.get("/healthz")
def healthz(): return {"ok": True}

# ---------- minimal API used by the UI ----------

@app.post("/api/conversations/1/message_stream")
async def message_stream(content: str = Form(...)):
    # store user message
    STATE["messages"].append({"role":"user","content":content,"created_at":time.time()})
    # extract/update process map
    steps = extract_steps_from(content)
    if steps:
        STATE["process"]["steps"] = steps
    # stream back a short adaptive question
    async def gen():
        out = reply_for(content)
        for ch in out:
            yield ch
            await asyncio.sleep(0.01)
        STATE["messages"].append({"role":"assistant","content":out,"created_at":time.time()})
    return StreamingResponse(gen(), media_type="text/plain")

@app.get("/api/conversations/1/latest_process")
def latest_proc():
    return STATE["process"] if STATE["process"]["steps"] else {"steps":[], "actors":[], "tools":[], "decisions":[]}

@app.get("/api/conversations/1/followup")
def followup(focus_type: str = "", focus_text: str = ""):
    q = f"For {focus_text or 'that step'}, what’s the input, who owns it, and what marks it done?"
    return {"question": q}

@app.get("/api/conversations/1/simulate")
def simulate(scale: float = 1.5):
    n = max(1, len(STATE["process"]["steps"]) or 3)
    cycle = round(n * scale * 0.8, 2)
    scores = [{"index": i, "risk": round(0.3 + 0.7*(i/(n-1 or 1)), 3)} for i in range(n)]
    return {"cycle_time_hours": cycle, "scores": scores}

@app.post("/api/conversations/1/upload")
async def upload(file: UploadFile = File(...)):
    data = await file.read()
    info = {"filename": file.filename, "size": len(data)}
    # trivial: set a step mentioning the artifact
    STATE["process"]["steps"] = STATE["process"]["steps"] or [f"Review {file.filename}", "Summarize", "Decide next action"]
    return JSONResponse({"ok": True, "file": info})
