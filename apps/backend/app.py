import os
import time
import asyncio
import re
import random
from pathlib import Path
from typing import Dict, List
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .middleware import AssetAccessMiddleware

try:
    from .routers import workforce
    WORKFORCE_ROUTER_AVAILABLE = True
except ImportError:
    print("⚠️  Workforce router not available")
    WORKFORCE_ROUTER_AVAILABLE = False

BASE = Path(__file__).parent

# Initialize FastAPI app
app = FastAPI(title="Casey · MindForge", debug=True)

# Setup static files and templates
(BASE/"static").mkdir(exist_ok=True)
(BASE/"templates").mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(BASE/"static")), name="static")
templates = Jinja2Templates(directory=str(BASE/"templates"))

# Include routers if available
if WORKFORCE_ROUTER_AVAILABLE:
    app.include_router(workforce.router, prefix="/api")

# Configuration
USE_DATABASE = os.getenv("USE_DATABASE", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print(f"🔧 Configuration:")
print(f"   📊 Database Mode: {'Enabled' if USE_DATABASE else 'Disabled (Simple Mode)'}")
print(f"   🔑 API Key: {'Set' if OPENAI_API_KEY else 'Not set (LLM features disabled)'}")

        print("✅ Database mode enabled - full functionality available")
    except ImportError as e:
        print(f"⚠️  Database imports failed: {e}")
        print("🔄 Falling back to simple mode")
        USE_DATABASE = False

if not USE_DATABASE:
    print("🧠 Simple mode enabled - using in-memory processing")

    def infer_tone(text: str) -> str:
        """Analyze text tone for adaptive responses"""
        if not text:
            return "warm"

        t = text.lower()
        negative_indicators = ["angry", "frustrated", "blocked", "confused", "tired", "annoyed", "overwhelmed"]
        expert_indicators = ["sla", "throughput", "kpi", "slo", "sprint", "backlog", "okrs", "latency"]

        is_negative = any(w in t for w in negative_indicators)
        is_expert = any(w in t for w in expert_indicators)
        is_terse = len(t) < 40 and not t.endswith("?")

        if is_expert:
            return "expert"
        elif is_negative:
            return "gentle"
        elif is_terse:
            return "direct"
        else:
            return "warm"

    def generate_adaptive_reply(text: str) -> str:
        """Generate contextually appropriate responses"""
        tone = infer_tone(text)

        responses = {
            "gentle": "I understand this can be challenging. Let's break it down step by step. ",
            "expert": "Got it - diving into the technical details. ",
            "direct": "Quick question: ",
            "warm": "Thanks for sharing that! "
        }

        prefix = responses.get(tone, "")

        # Generate follow-up questions based on content
        if "?" in text:
            question = "What's the very next concrete action, and who handles it?"
        elif any(word in text.lower() for word in ["step", "process", "workflow"]):
            question = "Who owns the first step and what tools do they use?"
        elif any(word in text.lower() for word in ["problem", "issue", "challenge"]):
            question = "What's the root cause, and what would resolution look like?"
        else:
            question = "What happens next in this process?"

        return prefix + question

    def generate_smart_chips(text: str) -> List[str]:
        """
        Generate contextual suggestion chips based on the assistant's reply.
        """
        t = text.lower() if text else ""
        chips: List[str] = []

        if any(word in t for word in ["step", "process", "workflow"]):
            chips.append("What is the next step?")
        if any(word in t for word in ["who", "actor", "owner", "responsible"]):
            chips.append("Who is responsible?")
        if any(word in t for word in ["tool", "system", "application"]):
            chips.append("What tools are used?")

        if not chips:
            chips = [
                "What is the next step?",
                "Who is responsible?",
                "What tools are used?",
            ]

        return chips[:5]

    def extract_process_elements(text: str) -> Dict[str, List[str]]:
        """Extract process steps, actors, and tools from text"""
        elements = {"steps": [], "actors": [], "tools": [], "decisions": [], "inputs": [], "outputs": []}

        # Extract steps (look for action words and sequences)
        step_patterns = [
            r"(?:then|next|after that)\s+([^.]+)",
            r"(\w+ing[^.]+)",
            r"(create|submit|review|approve|send|validate|process|generate)\s+([^.]+)"
        ]

        for pattern in step_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                step = match if isinstance(match, str) else " ".join(match)
                step = step.strip().rstrip(".")
                if step and len(step) > 3:
                    elements["steps"].append(step)

        # Extract actors (people, roles, departments)
        actor_patterns = [
            r"\b(manager|admin|user|team|department|analyst|developer|designer|reviewer)\b",
            r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b",  # Names
            r"\b(IT|HR|Finance|Sales|Marketing|Operations)\b"
        ]

        for pattern in actor_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.lower() not in ["the", "and", "or", "but"]:
                    elements["actors"].append(match)

        # Extract tools (systems, applications, platforms)
        tool_patterns = [
            r"\b(system|platform|application|tool|software|database|CRM|ERP)\b",
            r"\b(Excel|Slack|Email|Jira|Salesforce|SharePoint|Teams)\b",
            r"\b(\w+\.com|\w+\.io|\w+\.net)\b"
        ]

        for pattern in tool_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            elements["tools"].extend(matches)

        # Remove duplicates and clean up
        for key in elements:
            elements[key] = list(set([item.strip() for item in elements[key] if item.strip()]))
            elements[key] = elements[key][:10]  # Limit to 10 items per category

        return elements

    def calculate_process_metrics() -> Dict:
        """Calculate intelligent process metrics"""
        steps = STATE["process"]["steps"]
        actors = STATE["process"]["actors"]
        tools = STATE["process"]["tools"]

        if not steps:
            return {"complexity": "low", "estimated_time": 0, "risk_score": 0}

        # Complexity calculation
        complexity_score = len(steps) + len(actors) * 1.5 + len(tools) * 0.5
        complexity_level = "low" if complexity_score < 5 else "medium" if complexity_score < 15 else "high"

        # Time estimation (hours)
        base_time_per_step = 0.5
        coordination_overhead = len(actors) * 0.2
        estimated_time = len(steps) * base_time_per_step + coordination_overhead

        # Risk assessment
        process_text = " ".join(steps).lower()
        risk_factors = 0
        if any(word in process_text for word in ["manual", "by hand"]):
            risk_factors += 2
        if any(word in process_text for word in ["approve", "review"]):
            risk_factors += 1
        if len(actors) == 1:
            risk_factors += 2  # Single point of failure

        risk_score = min(risk_factors * 20, 100)

        return {
            "complexity": complexity_level,
            "complexity_score": complexity_score,
            "estimated_time": round(estimated_time, 1),
            "risk_score": risk_score,
            "automation_potential": 100 - risk_score if "automated" in process_text else risk_score
        }

    @app.get("/api/conversations/1/message_stream")
    async def message_stream(content: str):
        """Handle chat messages with intelligent processing"""
        # Store user message
        user_msg = {
            "role": "user",
            "content": content,
            "created_at": time.time()
        }
        STATE["messages"].append(user_msg)
        STATE["session_analytics"]["total_interactions"] += 1


        # Stream response
        async def generate_response():
            for char in response_text:
                yield f"data: {char}\n\n"
                await asyncio.sleep(0.02)

            STATE["messages"].append({
                "role": "assistant",
                "content": response_text,
                "created_at": time.time(),
                "metadata": {

                }
            })
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate_response(), media_type="text/event-stream")

    @app.get("/api/conversations/1/latest_process")
    def get_latest_process():
        """Get current process with intelligence metrics"""
        base_process = STATE["process"]

        if not any(base_process.values()):
            return {"steps": [], "actors": [], "tools": [], "decisions": [], "inputs": [], "outputs": []}

        metrics = calculate_process_metrics()

        return {
            **base_process,
            "metrics": metrics,
            "session_stats": STATE["session_analytics"]
        }

    @app.get("/api/conversations/1/followup")
    def get_followup(focus_type: str = "", focus_text: str = ""):
        """Generate intelligent follow-up questions"""
        base_questions = [
            f"For {focus_text or 'that step'}, what's the input and who owns it?",
            f"What happens if {focus_text or 'this step'} fails or gets delayed?",
            f"How do you currently measure success for {focus_text or 'this process'}?",
            f"What tools or systems support {focus_text or 'this activity'}?"
        ]

        # Select question based on current process state
        if len(STATE["process"]["steps"]) < 3:
            question = base_questions[0]
        elif len(STATE["process"]["actors"]) < 2:
            question = base_questions[1]
        else:
            question = base_questions[2]

        return {"question": question}

    @app.get("/api/conversations/1/simulate")
    def simulate_process(scale: float = 1.5):
        """Run intelligent process simulation"""
        steps = STATE["process"]["steps"]

        if not steps:
            return {"cycle_time_hours": 0, "scores": [], "scale": scale}

        metrics = calculate_process_metrics()
        base_time = metrics["estimated_time"]

        # Calculate scaled cycle time
        cycle_time = round(base_time * scale, 1)

        # Generate risk scores for each step
        scores = []
        for i, step in enumerate(steps):
            step_lower = step.lower()

            # Base risk calculation
            base_risk = 1.0

            # Risk factors
            if any(word in step_lower for word in ["approve", "manual", "review"]):
                base_risk += 1.0
            if any(word in step_lower for word in ["urgent", "critical"]):
                base_risk += 0.5
            if any(word in step_lower for word in ["automated", "system"]):
                base_risk -= 0.3

            # Scale affects risk
            final_risk = base_risk * max(1.0, scale * 0.8)

            scores.append({
                "index": i,
                "step": step,
                "risk": round(final_risk, 2),
                "bottleneck_potential": "high" if base_risk > 1.5 else "medium" if base_risk > 1.0 else "low"
            })

        return {
            "cycle_time_hours": cycle_time,
            "scores": scores,
            "scale": scale,
            "metrics": metrics,
            "recommendations": [
                "Consider automation for manual steps",
                "Add parallel processing where possible",
                "Implement monitoring for bottlenecks"
            ] if metrics["risk_score"] > 50 else ["Process looks efficient!"]
        }

    @app.post("/api/conversations/1/upload")
    async def upload_file(file: UploadFile = File(...)):
        """Handle file uploads with intelligent analysis"""
        try:
            data = await file.read()
            file_info = {"filename": file.filename, "size": len(data)}

            extracted_elements = 0

            # Process text files
            if file.filename.endswith(('.txt', '.md')):
                try:
                    content = data.decode('utf-8', errors='ignore')[:2000]  # First 2000 chars
                    extracted = extract_process_elements(content)

                    # Add to process
                    for key in extracted:
                        for item in extracted[key]:
                            if item not in STATE["process"][key]:
                                STATE["process"][key].append(item)
                                extracted_elements += 1

                except UnicodeDecodeError:
                    pass

            # Add analysis step
            analysis_step = f"Analyze uploaded file: {file.filename}"
            if analysis_step not in STATE["process"]["steps"]:
                STATE["process"]["steps"].append(analysis_step)

            return JSONResponse({
                "ok": True,
                "file": file_info,
                "extracted_elements": extracted_elements,
                "message": f"Successfully processed {file.filename}"
            })

        except Exception as e:
            return JSONResponse(
                {"ok": False, "error": str(e)},
                status_code=500
            )



@app.get("/", response_class=HTMLResponse)
def casey_chat(request: Request):
    """Render the Casey chat interface with stored messages."""
    return templates.TemplateResponse(
        "casey.html",
        {"request": request, "messages": STATE["messages"]},
    )


@app.post("/chat", response_class=HTMLResponse)
async def chat(request: Request, message: str = Form("")):
    """Simple chat handler that echoes back adaptive replies."""
    text = message.strip()
    if text:
        STATE["messages"].append(
            {
                "role": "user",
                "html": text,

            }
        )

        if "generate_adaptive_reply" in globals():
            reply = generate_adaptive_reply(text)
        else:
            reply = f"You said: {text}"

        # Clear chips from previous messages so only the newest assistant
        # message shows suggestions.
        for m in STATE["messages"]:
            m.pop("chips", None)


        STATE["messages"].append(
            {
                "role": "assistant",
                "html": reply,

            }
        )

    return templates.TemplateResponse(
        "casey.html", {"request": request, "messages": STATE["messages"]}
    )

@app.get("/healthz")
def health_check():
    """Health check endpoint"""
    return {
        "ok": True,
        "status": "healthy",
        "mode": "database" if USE_DATABASE else "simple",
        "features": {
            "database": USE_DATABASE,
            "llm": bool(OPENAI_API_KEY),
            "workforce_router": WORKFORCE_ROUTER_AVAILABLE
        }
    }

@app.get("/api/status")
def get_status():
    """API status endpoint"""
    return {
        "service": "Casey · MindForge",
        "version": "1.0.0",
        "mode": "database" if USE_DATABASE else "simple",
        "database_available": USE_DATABASE,
        "llm_available": bool(OPENAI_API_KEY),
        "message": "Database mode provides full functionality" if USE_DATABASE else "Simple mode for quick demo",
        "uptime": round(time.time() - (STATE.get("session_analytics", {}).get("start_time", time.time())), 1) if not USE_DATABASE else 0
    }

# Additional helpful endpoints
@app.get("/api/conversations/1/messages")
def get_messages():
    """Get conversation messages"""
    if USE_DATABASE:
        return {"messages": []}  # Would fetch from database
    else:
        return {"messages": STATE["messages"]}

@app.get("/api/conversations/1/reset")
def reset_conversation():
    """Reset conversation state"""
    if not USE_DATABASE:
        STATE["messages"].clear()
        STATE["process"] = {"steps": [], "actors": [], "tools": [], "decisions": [], "inputs": [], "outputs": []}
        STATE["session_analytics"]["total_interactions"] = 0
        STATE["session_analytics"]["start_time"] = time.time()

    return {"ok": True, "message": "Conversation reset successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
