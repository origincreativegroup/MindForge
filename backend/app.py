import os
from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .routers import workforce
import asyncio, re, time

BASE = Path(__file__).parent

# Initialize FastAPI app
app = FastAPI(title="Casey · MindForge", debug=True)

# Setup static files and templates
(BASE/"static").mkdir(exist_ok=True)
(BASE/"templates").mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(BASE/"static")), name="static")
templates = Jinja2Templates(directory=str(BASE/"templates"))
app.include_router(workforce.router, prefix="/api")
# Add this line near the top of your app.py file, right after the import statements
# and before the USE_DATABASE check:

WEBSOCKET_ENABLED = False  # Simple fix - disable WebSocket for now

# Alternatively, if you want to keep the WebSocket logic,
# replace all instances of:
# if WEBSOCKET_ENABLED:

# with:
# try:
# Check if we should use database mode or simple mode
USE_DATABASE = os.getenv("USE_DATABASE", "false").lower() == "true"

if USE_DATABASE:
    # Import and setup database routers
    try:
        from .routers import conversations, nextq
        app.include_router(conversations.router, prefix="/api")
        app.include_router(nextq.router, prefix="/api")
        print("Database mode enabled - full functionality available")
    except ImportError as e:
        print(f"Database imports failed: {e}")
        print("Falling back to simple mode")
        USE_DATABASE = False

# Add this to replace the simple mode API endpoints in your backend/app.py

# Replace the simple mode section in your backend/app.py with this enhanced version

if not USE_DATABASE:
    # Advanced AI-powered simple mode
    print("🧠 Advanced AI mode enabled - using intelligent in-memory processing")

    # Import the advanced AI engine
    try:
        from .services.casey_ai import AdvancedCaseyAI, ProcessInsight
        casey_ai = AdvancedCaseyAI()
        AI_ENABLED = True
        print("✨ Advanced Casey AI engine loaded")
    except ImportError:
        print("⚠️  Advanced AI not available, using basic mode")
        AI_ENABLED = False

    # Enhanced state management
    STATE = {
        "messages": [],
        "process": {"steps": [], "actors": [], "tools": [], "decisions": []},
        "conversation_count": 0,
        "insights": [],
        "user_profile": {},
        "learning_history": [],
        "session_analytics": {
            "start_time": time.time(),
            "total_interactions": 0,
            "process_complexity_score": 0,
            "optimization_opportunities": 0,
            "ai_confidence_avg": 0.0
        }
    }

    def process_with_ai(user_input: str, conversation_id: str = "default") -> Dict:
        """Process user input with advanced AI analysis"""
        if not AI_ENABLED:
            return {"ai_response": "AI analysis not available", "insights": []}

        try:
            # Run comprehensive AI analysis
            ai_result = casey_ai.analyze_conversation_turn(user_input, conversation_id)

            # Update session analytics
            STATE["session_analytics"]["total_interactions"] += 1
            STATE["session_analytics"]["ai_confidence_avg"] = (
                STATE["session_analytics"]["ai_confidence_avg"] * 0.8 +
                ai_result.get("analysis", {}).get("confidence", 0.5) * 0.2
            )

            # Store insights
            if ai_result.get("insights"):
                STATE["insights"].extend(ai_result["insights"])
                STATE["session_analytics"]["optimization_opportunities"] += len(ai_result["insights"])

            # Update user profile
            if ai_result.get("context"):
                STATE["user_profile"] = ai_result["context"].__dict__

            return ai_result

        except Exception as e:
            print(f"AI processing error: {e}")
            return {"ai_response": "AI analysis temporarily unavailable", "insights": []}

    def generate_process_intelligence_summary() -> Dict:
        """Generate intelligent summary of the current process"""
        if not AI_ENABLED or not STATE["process"]["steps"]:
            return {}

        steps = STATE["process"]["steps"]
        actors = STATE["process"]["actors"]
        tools = STATE["process"]["tools"]

        # Calculate process complexity
        complexity_score = (
            len(steps) * 1.0 +
            len(actors) * 1.5 +  # More actors = more coordination complexity
            len(tools) * 0.5 +   # Tools can reduce or increase complexity
            len(STATE["insights"]) * 2.0  # Issues add complexity
        )

        STATE["session_analytics"]["process_complexity_score"] = complexity_score

        # Generate smart insights
        insights_summary = []
        if STATE["insights"]:
            high_impact_insights = [i for i in STATE["insights"] if hasattr(i, 'impact') and i.impact in ['high', 'critical']]
            insights_summary = [
                {
                    "title": insight.title,
                    "type": insight.type,
                    "impact": insight.impact,
                    "confidence": insight.confidence,
                    "quick_win": insight.actionable_steps[0] if insight.actionable_steps else "Review process"
                }
                for insight in high_impact_insights[:3]  # Top 3 insights
            ]

        return {
            "complexity_assessment": {
                "score": complexity_score,
                "level": "low" if complexity_score < 5 else "medium" if complexity_score < 15 else "high",
                "factors": {
                    "step_count": len(steps),
                    "stakeholder_count": len(actors),
                    "tool_count": len(tools),
                    "identified_issues": len(STATE["insights"])
                }
            },
            "top_insights": insights_summary,
            "recommendations": generate_smart_recommendations(),
            "metrics": {
                "estimated_cycle_time": calculate_intelligent_cycle_time(),
                "automation_potential": assess_automation_potential(),
                "risk_factors": identify_risk_factors()
            }
        }

    def generate_smart_recommendations() -> List[str]:
        """Generate AI-powered recommendations"""
        recommendations = []

        if len(STATE["process"]["steps"]) > 8:
            recommendations.append("🔄 Consider breaking this into sub-processes - complexity is high")

        if len(STATE["process"]["actors"]) > 5:
            recommendations.append("👥 Multiple stakeholders detected - ensure clear communication protocols")

        manual_indicators = ["manual", "by hand", "copy", "enter", "type"]
        process_text = " ".join(STATE["process"]["steps"]).lower()
        if any(indicator in process_text for indicator in manual_indicators):
            recommendations.append("🤖 Automation opportunities detected - prioritize high-volume manual tasks")

        approval_indicators = ["approve", "review", "sign off", "authorize"]
        if any(indicator in process_text for indicator in approval_indicators):
            recommendations.append("⚡ Approval bottlenecks possible - consider parallel or delegated approvals")

        if STATE["insights"]:
            critical_insights = [i for i in STATE["insights"] if hasattr(i, 'impact') and i.impact == 'critical']
            if critical_insights:
                recommendations.append(f"🚨 {len(critical_insights)} critical issues require immediate attention")

        return recommendations[:5]  # Top 5 recommendations

    def calculate_intelligent_cycle_time() -> Dict:
        """Calculate intelligent cycle time estimates"""
        steps = STATE["process"]["steps"]
        if not steps:
            return {"estimated_hours": 0, "confidence": "low"}

        # AI-powered cycle time calculation
        base_time_per_step = 0.5  # 30 minutes base
        complexity_multiplier = 1.0

        process_text = " ".join(steps).lower()

        # Adjust based on process characteristics
        if any(word in process_text for word in ["approve", "review", "authorize"]):
            complexity_multiplier += 0.8  # Approvals add delay

        if any(word in process_text for word in ["manual", "by hand", "copy"]):
            complexity_multiplier += 0.5  # Manual work is slower

        if any(word in process_text for word in ["automated", "system", "automatic"]):
            complexity_multiplier -= 0.3  # Automation is faster

        if len(STATE["process"]["actors"]) > 3:
            complexity_multiplier += 0.2 * (len(STATE["process"]["actors"]) - 3)  # More people = more coordination

        estimated_time = len(steps) * base_time_per_step * max(complexity_multiplier, 0.1)

        # Confidence based on information completeness
        confidence_score = min(
            (len(STATE["process"]["actors"]) / max(len(steps), 1)) * 0.4 +
            (len(STATE["process"]["tools"]) / max(len(steps), 1)) * 0.3 +
            (len(STATE["messages"]) / 10) * 0.3,
            1.0
        )

        confidence_level = "high" if confidence_score > 0.7 else "medium" if confidence_score > 0.4 else "low"

        return {
            "estimated_hours": round(estimated_time, 1),
            "confidence": confidence_level,
            "factors": {
                "base_steps": len(steps),
                "complexity_multiplier": round(complexity_multiplier, 2),
                "coordination_overhead": len(STATE["process"]["actors"])
            }
        }

    def assess_automation_potential() -> Dict:
        """Assess automation potential using AI"""
        if not STATE["process"]["steps"]:
            return {"score": 0, "opportunities": []}

        process_text = " ".join(STATE["process"]["steps"]).lower()

        # AI-powered automation scoring
        automation_indicators = {
            "data_entry": ["enter", "input", "type", "fill", "copy"],
            "calculations": ["calculate", "compute", "add", "sum", "total"],
            "notifications": ["send", "notify", "email", "alert"],
            "approvals": ["approve", "review", "check", "verify"],
            "reporting": ["report", "generate", "create report", "dashboard"]
        }

        opportunities = []
        total_score = 0

        for category, indicators in automation_indicators.items():
            category_score = sum(1 for indicator in indicators if indicator in process_text)
            if category_score > 0:
                opportunities.append({
                    "category": category.replace("_", " ").title(),
                    "score": category_score,
                    "priority": "high" if category_score >= 2 else "medium"
                })
                total_score += category_score

        return {
            "score": min(total_score * 10, 100),  # 0-100 scale
            "level": "high" if total_score >= 5 else "medium" if total_score >= 2 else "low",
            "opportunities": opportunities
        }

    def identify_risk_factors() -> List[Dict]:
        """Identify process risk factors"""
        risks = []

        # Single point of failure
        if len(set(STATE["process"]["actors"])) == 1 and len(STATE["process"]["actors"]) > 0:
            risks.append({
                "type": "Single Point of Failure",
                "severity": "high",
                "description": "Process depends on single person"
            })

        # Manual steps
        process_text = " ".join(STATE["process"]["steps"]).lower()
        if any(word in process_text for word in ["manual", "by hand", "copy"]):
            risks.append({
                "type": "Manual Process Risk",
                "severity": "medium",
                "description": "Manual steps prone to errors and delays"
            })

        # Approval bottlenecks
        approval_count = sum(1 for step in STATE["process"]["steps"] if any(word in step.lower() for word in ["approve", "review", "authorize"]))
        if approval_count > 2:
            risks.append({
                "type": "Approval Bottleneck",
                "severity": "medium",
                "description": f"{approval_count} approval steps may cause delays"
            })

        return risks

    # Enhanced API endpoints with AI
    @app.post("/api/conversations/1/message_stream")
    async def message_stream(content: str = Form(...)):
        # Store user message
        user_msg = {"role": "user", "content": content, "created_at": time.time()}
        STATE["messages"].append(user_msg)

        # AI-powered analysis
        ai_result = process_with_ai(content)

        # Extract and update process elements using AI
        if ai_result.get("analysis"):
            analysis = ai_result["analysis"]

            # Update process elements from AI analysis
            if analysis.get("entities"):
                entities = analysis["entities"]

                # Merge AI-extracted entities with existing state
                for actor in entities.get("actors", []):
                    if actor not in STATE["process"]["actors"]:
                        STATE["process"]["actors"].append(actor)

                for tool in entities.get("tools", []):
                    if tool not in STATE["process"]["tools"]:
                        STATE["process"]["tools"].append(tool)

            if analysis.get("process_elements"):
                elements = analysis["process_elements"]

                for step in elements.get("steps", []):
                    if step not in STATE["process"]["steps"]:
                        STATE["process"]["steps"].append(step)

                for decision in elements.get("decisions", []):
                    if decision not in STATE["process"]["decisions"]:
                        STATE["process"]["decisions"].append(decision)

        # Get AI-generated response
        response_text = ai_result.get("recommended_response", "Tell me more about that process step.")

        # Add contextual intelligence to response
        if STATE["insights"]:
            latest_insight = STATE["insights"][-1]
            if hasattr(latest_insight, 'impact') and latest_insight.impact in ['high', 'critical']:
                response_text += f" 💡 I'm noticing {latest_insight.title.lower()} - this could be a key optimization opportunity."

        # Broadcast update via WebSocket if available
        try:
            from .websocket import broadcast_process_update
            await broadcast_process_update(STATE["process"])
        except:
            pass

        # Stream the intelligent response
        async def gen():
            for char in response_text:
                yield char
                await asyncio.sleep(0.015)  # Slightly faster for better UX

            # Store assistant message
            STATE["messages"].append({
                "role": "assistant",
                "content": response_text,
                "created_at": time.time(),
                "ai_metadata": {
                    "confidence": ai_result.get("analysis", {}).get("confidence", 0.5),
                    "insights_count": len(ai_result.get("insights", [])),
                    "primary_intent": ai_result.get("analysis", {}).get("intent", {})
                }
            })

        return StreamingResponse(gen(), media_type="text/plain")

    @app.get("/api/conversations/1/latest_process")
    def latest_proc():
        base_process = STATE["process"]
        if not any(base_process.values()):
            return {"steps": [], "actors": [], "tools": [], "decisions": []}

        # Add AI intelligence to response
        intelligence_summary = generate_process_intelligence_summary()

        return {
            **base_process,
            "ai_insights": {
                "complexity": intelligence_summary.get("complexity_assessment", {}),
                "recommendations": intelligence_summary.get("recommendations", []),
                "metrics": intelligence_summary.get("metrics", {}),
                "session_stats": STATE["session_analytics"]
            }
        }

    @app.get("/api/conversations/1/simulate")
    def simulate(scale: float = 1.5):
        steps = STATE["process"]["steps"]
        n = max(1, len(steps))

        # AI-enhanced simulation
        cycle_time_data = calculate_intelligent_cycle_time()
        base_time = cycle_time_data["estimated_hours"]
        cycle = round(base_time * scale, 1)

        # AI-powered risk scoring
        scores = []
        for i, step in enumerate(steps):
            # Base risk calculation
            base_risk = 1.0

            # AI risk factors
            step_lower = step.lower()
            if any(word in step_lower for word in ["approve", "manual", "review"]):
                base_risk += 1.0
            if any(word in step_lower for word in ["urgent", "critical", "important"]):
                base_risk += 0.5
            if any(word in step_lower for word in ["automated", "system"]):
                base_risk -= 0.3

            # Scale affects risk
            final_risk = base_risk * max(1.0, scale)

            scores.append({
                "index": i,
                "step": step,
                "risk": round(final_risk, 2),
                "ai_assessment": {
                    "automation_potential": "high" if any(word in step_lower for word in ["manual", "copy", "enter"]) else "low",
                    "bottleneck_likelihood": "high" if any(word in step_lower for word in ["approve", "review", "wait"]) else "low"
                }
            })

        # Generate AI insights for simulation
        automation_assessment = assess_automation_potential()
        risk_factors = identify_risk_factors()

        result = {
            "cycle_time_hours": cycle,
            "scores": scores,
            "scale": scale,
            "ai_analysis": {
                "confidence": cycle_time_data["confidence"],
                "automation_potential": automation_assessment,
                "risk_factors": risk_factors,
                "optimization_score": min(100 - len(risk_factors) * 20 + automation_assessment["score"] * 0.3, 100)
            }
        }

        # Broadcast enhanced simulation
        try:
            from .websocket import broadcast_simulation_result
            asyncio.create_task(broadcast_simulation_result(result))
        except:
            pass

        return result

    @app.post("/api/conversations/1/upload")
    async def upload(file: UploadFile = File(...)):
        try:
            data = await file.read()
            file_info = {"filename": file.filename, "size": len(data)}

            # AI-powered file analysis
            if file.filename.endswith('.txt'):
                content = data.decode('utf-8', errors='ignore')[:2000]

                # Use AI to extract process elements from file
                ai_result = process_with_ai(f"Analyzing uploaded document: {content}")

                if ai_result.get("analysis", {}).get("entities"):
                    entities = ai_result["analysis"]["entities"]

                    # Add extracted entities to process
                    STATE["process"]["actors"].extend(entities.get("actors", []))
                    STATE["process"]["tools"].extend(entities.get("tools", []))

                    # Remove duplicates
                    STATE["process"]["actors"] = list(set(STATE["process"]["actors"]))
                    STATE["process"]["tools"] = list(set(STATE["process"]["tools"]))

            # Add AI-generated analysis step
            analysis_step = f"AI analysis of {file.filename}: Extract insights and validate process elements"
            if analysis_step not in STATE["process"]["steps"]:
                STATE["process"]["steps"].append(analysis_step)

            # Broadcast update
            try:
                from .websocket import broadcast_process_update
                await broadcast_process_update(STATE["process"])
            except:
                pass

            return JSONResponse({
                "ok": True,
                "file": file_info,
                "ai_extracted": len(ai_result.get("analysis", {}).get("entities", {}).get("actors", [])) + len(ai_result.get("analysis", {}).get("entities", {}).get("tools", []))
            })

        except Exception as e:
            return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

    # New AI-specific endpoints
    @app.get("/api/conversations/1/intelligence")
    def get_intelligence_summary():
        """Get AI-powered intelligence summary"""
        return generate_process_intelligence_summary()

    @app.get("/api/conversations/1/insights")
    def get_insights():
        """Get AI-generated insights"""
        return {
            "insights": [
                {
                    "title": insight.title,
                    "type": insight.type,
                    "confidence": insight.confidence,
                    "description": insight.description,
                    "impact": insight.impact,
                    "actionable_steps": insight.actionable_steps,
                    "metrics": insight.metrics
                }
                for insight in STATE["insights"]
            ],
            "total_count": len(STATE["insights"]),
            "high_impact_count": len([i for i in STATE["insights"] if hasattr(i, 'impact') and i.impact in ['high', 'critical']])
        }

    @app.post("/api/conversations/1/ask_ai")
    async def ask_ai_direct(question: str = Form(...)):
        """Direct AI question endpoint"""
        ai_result = process_with_ai(f"Direct question: {question}")
        return {
            "ai_response": ai_result.get("recommended_response", "I'd be happy to help with that question."),
            "confidence": ai_result.get("analysis", {}).get("confidence", 0.5),
            "insights": ai_result.get("insights", [])
        }
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
        # simple "next best question" that nudges structure
        if "?" in text:
            ask = "What's the very next concrete action, and who does it?"
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

    # Simple mode API endpoints
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
        q = f"For {focus_text or 'that step'}, what's the input, who owns it, and what marks it done?"
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

# Common routes for both modes
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    # Create a mock conversation object for the template
    Conv = type("Conv", (), {})
    conv = Conv()
    conv.id = 1
    if USE_DATABASE:
        # In database mode, we'd fetch real data here
        conv.messages = []
        conv.processes = []
    else:
        # Simple mode uses in-memory state
        conv.messages = STATE["messages"]
        conv.processes = [STATE["process"]] if STATE["process"]["steps"] else []

    return templates.TemplateResponse("chat.html", {"request": request, "title": "Casey", "conv": conv})

@app.get("/healthz")
def healthz():
    return {"ok": True, "mode": "database" if USE_DATABASE else "simple"}

# Add a route to check current mode
@app.get("/api/status")
def status():
    return {
        "mode": "database" if USE_DATABASE else "simple",
        "database_available": USE_DATABASE,
        "message": "Database mode provides full functionality" if USE_DATABASE else "Simple mode for quick demo"
    }
