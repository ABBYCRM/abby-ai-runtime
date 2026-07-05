"""
ABBY - Autonomous Business Bot Yielder
Unified API Gateway Server (NVIDIA NIM Edition)

This FastAPI application ties together:
  - MetaGPT deterministic SOP pipeline
  - CrewAI dynamic agent swarm
  - NVIDIA NIM cloud LLM inference (multi-key rotation)
  - Health checks and monitoring

Routes:
  POST /v1/execute-pipeline   - Execute full E2E pipeline (MetaGPT + CrewAI)
  POST /v1/metagpt/run        - Run MetaGPT pipeline only
  POST /v1/crew/run           - Run CrewAI swarm only
  GET  /health                - Service health check
  GET  /status                - Full system status
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

# Force configuration initialization
import src.config

# Import pipeline modules
from src.metagpt_pipeline import run_metagpt_pipeline
from src.crew_swarm import execute_crew_swarm

# =============================================================================
# FASTAPI APPLICATION SETUP
# =============================================================================

app = FastAPI(
    title="ABBY - Autonomous Business Bot Yielder",
    description=(
        "Production multi-agent AI runtime integrating MetaGPT deterministic SOP "
        "pipeline with CrewAI dynamic collaboration swarm."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
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


class PipelineResponse(BaseModel):
    status: str
    request_id: str
    execution_time_ms: float
    meta_gpt_sop: str
    crew_ai_execution_token: str
    timestamp: str


class MetaGPTOnlyRequest(BaseModel):
    raw_payload: str


class CrewOnlyRequest(BaseModel):
    sop_context: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str
    uptime_seconds: float


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

@app.post("/v1/execute-pipeline", response_model=PipelineResponse)
async def handle_incoming_request(payload: WebhookPayload):
    """
    Full E2E pipeline execution:
    1. MetaGPT deterministic assembly SOP generation
    2. CrewAI dynamic swarm execution with tool-use
    """
    request_id = payload.request_id or _generate_request_id()
    start_ts = time.time()

    try:
        # Phase 1: MetaGPT deterministic SOP
        print(f"[{request_id}] [1/3] Initializing MetaGPT Assembly SOP...")
        sop_blueprint = await run_metagpt_pipeline(payload.raw_payload)
        print(f"[{request_id}] [1/3] SOP generated successfully")

        # Phase 2: CrewAI dynamic swarm
        print(f"[{request_id}] [2/3] Launching CrewAI Functional Swarm...")
        final_execution_token = execute_crew_swarm(sop_blueprint)
        print(f"[{request_id}] [2/3] Swarm execution complete")

        # Calculate execution time
        exec_time_ms = round((time.time() - start_ts) * 1000, 2)
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Log request
        _request_log[request_id] = {
            "status": "success",
            "timestamp": timestamp,
            "execution_time_ms": exec_time_ms,
            "sop_length": len(sop_blueprint),
            "token_length": len(str(final_execution_token))
        }

        print(f"[{request_id}] [3/3] Pipeline complete in {exec_time_ms}ms")

        return {
            "status": "Success",
            "request_id": request_id,
            "execution_time_ms": exec_time_ms,
            "meta_gpt_sop": sop_blueprint,
            "crew_ai_execution_token": str(final_execution_token),
            "timestamp": timestamp
        }

    except Exception as e:
        exec_time_ms = round((time.time() - start_ts) * 1000, 2)
        error_msg = f"Pipeline execution failed: {str(e)}"
        print(f"[{request_id}] ERROR: {error_msg}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/v1/metagpt/run")
async def run_metagpt_only(request: MetaGPTOnlyRequest):
    """Run only the MetaGPT deterministic SOP pipeline."""
    request_id = _generate_request_id()
    start_ts = time.time()

    try:
        print(f"[{request_id}] Running MetaGPT pipeline...")
        sop_result = await run_metagpt_pipeline(request.raw_payload)
        exec_time_ms = round((time.time() - start_ts) * 1000, 2)

        return {
            "status": "Success",
            "request_id": request_id,
            "execution_time_ms": exec_time_ms,
            "sop_blueprint": sop_result,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MetaGPT pipeline failed: {str(e)}")


@app.post("/v1/crew/run")
async def run_crew_only(request: CrewOnlyRequest):
    """Run only the CrewAI swarm against a provided SOP context."""
    request_id = _generate_request_id()
    start_ts = time.time()

    try:
        print(f"[{request_id}] Running CrewAI swarm...")
        token = execute_crew_swarm(request.sop_context)
        exec_time_ms = round((time.time() - start_ts) * 1000, 2)

        return {
            "status": "Success",
            "request_id": request_id,
            "execution_time_ms": exec_time_ms,
            "execution_token": str(token),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CrewAI swarm failed: {str(e)}")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Service health check endpoint for Render monitoring."""
    return {
        "status": "healthy",
        "service": "ABBY",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime_seconds": round(time.time() - _start_time, 2)
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
        "recent_requests": list(_request_log.keys())[-10:] if _request_log else [],
        "configuration": {
            "llm_provider": "nvidia_nim",
            "model": os.getenv("ABBY_MODEL", "nvidia/llama-3.1-nemotron-70b-instruct"),
            "nim_endpoint": os.getenv("NIM_BASE_URL", "https://integrate.api.nvidia.com/v1"),
            "max_tokens": int(os.getenv("ABBY_MAX_TOKENS", "8192")),
            "crewai_temp": float(os.getenv("ABBY_CREW_TEMP", "0.2")),
            "metagpt_temp": float(os.getenv("ABBY_METAGPT_TEMP", "0.1"))
        }
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "ABBY - Autonomous Business Bot Yielder",
        "version": "1.0.0",
        "description": "Multi-agent AI runtime: MetaGPT + CrewAI",
        "endpoints": {
            "pipeline": "POST /v1/execute-pipeline",
            "metagpt": "POST /v1/metagpt/run",
            "crew": "POST /v1/crew/run",
            "health": "GET /health",
            "status": "GET /status",
            "docs": "GET /docs"
        }
    }


# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", "9000"))
    host = os.getenv("HOST", "0.0.0.0")

    print("=" * 60)
    print("  ABBY - Autonomous Business Bot Yielder v1.0.0")
    print("  Multi-Agent AI Runtime: MetaGPT + CrewAI")
    print("  LLM Backend: NVIDIA NIM Cloud Inference")
    print("=" * 60)
    print(f"  Starting server on {host}:{port}")
    print(f"  Model: {os.getenv('ABBY_MODEL', 'nvidia/llama-3.1-nemotron-70b-instruct')}")
    print(f"  NIM Endpoint: {os.getenv('NIM_BASE_URL', 'https://integrate.api.nvidia.com/v1')}")
    print(f"  Docs: http://{host}:{port}/docs")
    print("=" * 60)

    uvicorn.run(app, host=host, port=port)
