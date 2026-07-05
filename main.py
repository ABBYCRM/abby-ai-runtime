"""
ABBY - Autonomous Business Bot Yielder
Unified API Gateway Server (NVIDIA NIM Edition)
"""

import os
import sys
import time
import json
import asyncio
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# =============================================================================
# CONDITIONAL IMPORTS - Graceful fallback if heavy frameworks fail
# =============================================================================

METAGPT_AVAILABLE = False
CREWAI_AVAILABLE = False

# Try to load MetaGPT
try:
    import src.config
    from src.metagpt_pipeline import run_metagpt_pipeline
    METAGPT_AVAILABLE = True
    print("[INIT] MetaGPT loaded")
except Exception as e:
    print(f"[INIT] MetaGPT unavailable: {e}")

# Try to load CrewAI
try:
    from src.crew_swarm import execute_crew_swarm
    CREWAI_AVAILABLE = True
    print("[INIT] CrewAI loaded")
except Exception as e:
    print(f"[INIT] CrewAI unavailable: {e}")

# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(
    title="ABBY - Autonomous Business Bot Yielder",
    description="Production multi-agent AI runtime integrating MetaGPT + CrewAI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# =============================================================================
# DATA MODELS
# =============================================================================

class WebhookPayload(BaseModel):
    raw_payload: str
    request_id: Optional[str] = None

class MetaGPTOnlyRequest(BaseModel):
    raw_payload: str

class CrewOnlyRequest(BaseModel):
    sop_context: str

# =============================================================================
# REQUEST TRACKING
# =============================================================================

_request_log: Dict[str, Dict[str, Any]] = {}
_start_time = time.time()

def _generate_request_id() -> str:
    return f"abby-{uuid.uuid4().hex[:12]}-{int(time.time())}"

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "ABBY - Autonomous Business Bot Yielder",
        "version": "1.0.0",
        "metagpt_available": METAGPT_AVAILABLE,
        "crewai_available": CREWAI_AVAILABLE,
        "endpoints": {
            "pipeline": "POST /v1/execute-pipeline",
            "metagpt": "POST /v1/metagpt/run",
            "crew": "POST /v1/crew/run",
            "health": "GET /health",
            "status": "GET /status",
            "docs": "GET /docs"
        }
    }

@app.get("/health")
async def health_check():
    """Service health check endpoint for Render monitoring."""
    return {
        "status": "healthy",
        "service": "ABBY",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime_seconds": round(time.time() - _start_time, 2),
        "metagpt_available": METAGPT_AVAILABLE,
        "crewai_available": CREWAI_AVAILABLE
    }

@app.get("/status")
async def system_status():
    """Full system status with request statistics."""
    return {
        "service": "ABBY",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime_seconds": round(time.time() - _start_time, 2),
        "total_requests_processed": len(_request_log),
        "metagpt_available": METAGPT_AVAILABLE,
        "crewai_available": CREWAI_AVAILABLE,
        "configuration": {
            "llm_provider": "nvidia_nim",
            "model": os.getenv("ABBY_MODEL", "nvidia/llama-3.1-nemotron-70b-instruct"),
            "nim_endpoint": os.getenv("NIM_BASE_URL", "https://integrate.api.nvidia.com/v1"),
            "port": os.getenv("PORT", "10000"),
            "max_tokens": int(os.getenv("ABBY_MAX_TOKENS", "8192")),
            "crewai_temp": float(os.getenv("ABBY_CREW_TEMP", "0.2")),
            "metagpt_temp": float(os.getenv("ABBY_METAGPT_TEMP", "0.1"))
        }
    }

@app.post("/v1/execute-pipeline")
async def handle_incoming_request(payload: WebhookPayload):
    """
    Full E2E pipeline execution:
    1. MetaGPT deterministic SOP
    2. CrewAI dynamic swarm
    """
    request_id = payload.request_id or _generate_request_id()
    start_ts = time.time()

    if not METAGPT_AVAILABLE or not CREWAI_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="MetaGPT or CrewAI not available. Framework installation pending."
        )

    try:
        print(f"[{request_id}] [1/3] Initializing MetaGPT Assembly SOP...")
        sop_blueprint = await run_metagpt_pipeline(payload.raw_payload)

        print(f"[{request_id}] [2/3] Launching CrewAI Functional Swarm...")
        final_execution_token = execute_crew_swarm(sop_blueprint)

        exec_time_ms = round((time.time() - start_ts) * 1000, 2)
        timestamp = datetime.utcnow().isoformat() + "Z"

        _request_log[request_id] = {
            "status": "success",
            "timestamp": timestamp,
            "execution_time_ms": exec_time_ms
        }

        return {
            "status": "Success",
            "request_id": request_id,
            "execution_time_ms": exec_time_ms,
            "meta_gpt_sop": sop_blueprint,
            "crew_ai_execution_token": str(final_execution_token),
            "timestamp": timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/metagpt/run")
async def run_metagpt_only(request: MetaGPTOnlyRequest):
    """Run only the MetaGPT deterministic SOP pipeline."""
    if not METAGPT_AVAILABLE:
        raise HTTPException(status_code=503, detail="MetaGPT not available")
    try:
        sop_result = await run_metagpt_pipeline(request.raw_payload)
        return {"status": "Success", "sop_blueprint": sop_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/crew/run")
async def run_crew_only(request: CrewOnlyRequest):
    """Run only the CrewAI swarm against a provided SOP context."""
    if not CREWAI_AVAILABLE:
        raise HTTPException(status_code=503, detail="CrewAI not available")
    try:
        token = execute_crew_swarm(request.sop_context)
        return {"status": "Success", "execution_token": str(token)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    print(f"[START] ABBY on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
