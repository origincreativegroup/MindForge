# MindForge Casey — MVP

An interactive process-extraction MVP with:
- Live Mermaid **swimlane** graph (steps, actors, tools, decisions)
- **Clickable nodes** → targeted follow-ups
- **Edit mode** with inline **modal** editor (owner/SLA/inputs/outputs/notes/parallel group)
- **Scenario overlays** colored by simulated load with real-time **Scale** slider
- **Predicted cycle time**
- **Drag-to-reorder** steps
- **Export** SVG/PNG
- **Snapshot diffs**
- **Actor-level** SLA & capacity controls
- **Discovery Mode** chips + **Ask next best question**
- **Polished UI**: command palette, toasts, tour, tooltips, friendly empty states

## Quick start
```bash
./run.sh
# open http://localhost:8000
```
If you prefer manual:
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

## Notable endpoints
- `POST /api/conversations/{id}/message_stream`
- `GET  /api/conversations/{id}/latest_process`
- `GET  /api/conversations/{id}/simulate?scale=1.5`
- `POST /api/conversations/{id}/edit` (**edit|delete|insert_after**)
- `POST /api/conversations/{id}/reorder`
- `POST /api/conversations/{id}/meta` (structured fields)
- `GET  /api/conversations/{id}/diff`
- `GET  /api/conversations/{id}/next_question` (**Discovery Mode**)

> This is an offline MVP (no vendor keys needed). If you want to connect a real LLM or vector store later, stub points already exist in `services/llm_client.py` and `services/extract.py` (if present in your local build).
