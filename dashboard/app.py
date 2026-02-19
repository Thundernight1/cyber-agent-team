#!/usr/bin/env python3
"""
Cyber Agent Team - Web Dashboard
FastAPI backend + real-time agent orchestration.
"""
import asyncio
import json
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, List, Optional

from orchestrator.purple_lead import PurpleLeadOrchestrator
from config.settings import TEAM_ROSTER

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cyber-agent.dashboard")

app = FastAPI(title="Cyber Agent Team", version="1.0.0")

# Global orchestrator
orchestrator = PurpleLeadOrchestrator()
ws_clients: List[WebSocket] = []


class ScanRequest(BaseModel):
    target: str
    scan_type: str = "full"  # full | recon | vuln
    scope: Optional[Dict] = None


class ToolRequest(BaseModel):
    tool_name: str
    target: str
    options: Optional[Dict] = None


class AgentRequest(BaseModel):
    agent_id: str
    task: str
    context: Optional[Dict] = None


# ============================================================
# WebSocket broadcast
# ============================================================
async def broadcast(event: str, data: dict):
    message = json.dumps({"event": event, "data": data, "timestamp": datetime.now().isoformat()}, default=str)
    dead = []
    for ws in ws_clients:
        try:
            await ws.send_text(message)
        except Exception:
            dead.append(ws)
    for ws in dead:
        ws_clients.remove(ws)


# ============================================================
# API ENDPOINTS
# ============================================================

@app.on_event("startup")
async def startup():
    await orchestrator.initialize()


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    html_path = Path(__file__).parent / "templates" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/api/status")
async def get_status():
    return {
        "session_id": orchestrator.session_id,
        "agents": orchestrator.get_team_status(),
        "tools": orchestrator.get_tool_status(),
    }


@app.get("/api/team")
async def get_team():
    return orchestrator.get_team_status()


@app.get("/api/tools")
async def get_tools():
    return orchestrator.get_tool_status()


@app.get("/api/state")
async def get_state():
    return orchestrator.get_state()


@app.post("/api/scan")
async def start_scan(req: ScanRequest):
    await broadcast("scan_started", {"target": req.target, "type": req.scan_type})

    if req.scan_type == "full":
        result = await orchestrator.run_full_assessment(req.target, scope=req.scope)
    elif req.scan_type == "recon":
        result = await orchestrator.run_recon_only(req.target)
    elif req.scan_type == "vuln":
        result = await orchestrator.run_vuln_assessment(req.target)
    else:
        result = {"error": "Invalid scan_type"}

    await broadcast("scan_completed", {"target": req.target, "summary": result.get("summary", {})})
    return result


@app.post("/api/tool")
async def run_tool(req: ToolRequest):
    options = req.options or {}
    result = await orchestrator.run_tool_scan(req.tool_name, target=req.target, **options)
    return result


@app.post("/api/agent")
async def run_agent(req: AgentRequest):
    result = await orchestrator.run_single_agent(req.agent_id, req.task, context=req.context)
    return result.to_dict()


@app.post("/api/export")
async def export_report():
    state = orchestrator.get_state()
    filename = f"pentest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_dir = Path(__file__).parent.parent / "reports"
    report_dir.mkdir(exist_ok=True)
    filepath = report_dir / filename
    filepath.write_text(json.dumps(state, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return {"filename": filename, "path": str(filepath)}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    ws_clients.append(ws)
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            # İstemciden gelen komutları işle
            if msg.get("action") == "ping":
                await ws.send_text(json.dumps({"event": "pong"}))
    except WebSocketDisconnect:
        ws_clients.remove(ws)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8443)
