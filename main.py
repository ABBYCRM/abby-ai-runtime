import os
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="ABBY - Test")

class Payload(BaseModel):
    raw_payload: str

@app.get("/")
def root():
    return {"service": "ABBY", "status": "ok", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "ABBY"}

@app.post("/v1/execute-pipeline")
def pipeline(payload: Payload):
    return {
        "status": "Success",
        "meta_gpt_sop": "SOP_PLACEHOLDER",
        "crew_ai_execution_token": "TOKEN_PLACEHOLDER",
        "model": os.getenv("ABBY_MODEL", "unknown"),
        "port": os.getenv("PORT", "unknown")
    }

@app.post("/v1/metagpt/run")
def metagpt(payload: Payload):
    return {"status": "ok", "sop": "placeholder"}

@app.post("/v1/crew/run")
def crew(payload: Payload):
    return {"status": "ok", "token": "placeholder"}

@app.get("/status")
def status():
    return {
        "service": "ABBY",
        "version": "1.0.0",
        "model": os.getenv("ABBY_MODEL", "unknown"),
        "port": os.getenv("PORT", "unknown")
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
