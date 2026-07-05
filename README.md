# ABBY - Autonomous Business Bot Yielder

> Production multi-agent AI runtime integrating **MetaGPT** (deterministic SOP pipeline) and **CrewAI** (dynamic collaboration swarm), powered by **NVIDIA NIM** cloud inference with multi-key rotation.

## Architecture

```
Incoming Webhook
      |
      v
[FastAPI Gateway] <--- HTTP API
      |
      v
[MetaGPT Pipeline] ---- Deterministic Assembly Line
  - IntakeAnalyst (extract structured data)
  - SOPManager (generate compliance SOP)
      |
      v
[CrewAI Swarm] -------- Dynamic Agent Collaboration
  - Router Agent (DB verification + CRM lookup)
  - Arbitration Agent (compliance audit + auth token)
      |
      v
  JSON Execution Token
```

## LLM Backend: NVIDIA NIM

ABBY uses **NVIDIA NIM** (NVIDIA Inference Microservices) as its LLM engine:
- **Endpoint:** `https://integrate.api.nvidia.com/v1`
- **Model:** `nvidia/llama-3.1-nemotron-70b-instruct`
- **Multi-key rotation:** Loads multiple API keys for resilience and load distribution
- **Compatible with:** Any OpenAI-compatible endpoint ( CrewAI + MetaGPT both work natively)

## Quick Start

### Prerequisites
- Python 3.11+
- NVIDIA NIM API key(s) - get at [build.nvidia.com](https://build.nvidia.com)

### Local Development

```bash
# Clone and setup
git clone https://github.com/ABBYCRM/abby-ai-runtime.git
cd abby-ai-runtime
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Set environment variables (your NIM API keys)
export NIM_API_KEY="nvapi-YOUR-KEY-HERE"
export NIM_API_KEY_1="nvapi-SECOND-KEY-HERE"
export NIM_API_KEY_2="nvapi-THIRD-KEY-HERE"
export ABBY_MODEL="nvidia/llama-3.1-nemotron-70b-instruct"

# Run
python main.py

# Test
curl -X POST http://localhost:9000/v1/execute-pipeline \
  -H "Content-Type: application/json" \
  -d '{"raw_payload": "Lead ID: 101 - Requesting verification from Florida office."}'
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info and available endpoints |
| `/health` | GET | Service health check |
| `/status` | GET | Full system status + request stats |
| `/v1/execute-pipeline` | POST | Full E2E: MetaGPT + CrewAI |
| `/v1/metagpt/run` | POST | MetaGPT SOP pipeline only |
| `/v1/crew/run` | POST | CrewAI swarm execution only |
| `/docs` | GET | Interactive API documentation (Swagger) |

### Example: Full Pipeline

```bash
curl -X POST https://abby-ai-runtime.onrender.com/v1/execute-pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "raw_payload": "Tracking ID: 770 - Escalated priority case from West Coast Distribution."
  }'
```

**Response:**
```json
{
  "status": "Success",
  "request_id": "abby-a1b2c3d4e5f6-1750000000",
  "execution_time_ms": 8452.31,
  "meta_gpt_sop": "OPERATIONAL SOP: ...",
  "crew_ai_execution_token": "{\"status\": \"Escalated\", \"risk_score\": 85, ...}",
  "timestamp": "2026-07-06T12:00:00Z"
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NIM_API_KEY` | *(required)* | Primary NVIDIA NIM API key |
| `NIM_API_KEY_1` to `NIM_API_KEY_10` | *(optional)* | Additional keys for rotation |
| `NIM_BASE_URL` | `https://integrate.api.nvidia.com/v1` | NIM endpoint |
| `ABBY_MODEL` | `nvidia/llama-3.1-nemotron-70b-instruct` | Model identifier |
| `ABBY_MAX_TOKENS` | `8192` | Max tokens per request |
| `ABBY_CREW_TEMP` | `0.2` | CrewAI temperature |
| `ABBY_METAGPT_TEMP` | `0.1` | MetaGPT temperature |
| `PORT` | `9000` | Server port |
| `HOST` | `0.0.0.0` | Server bind address |

## Deployment

### Render (Production) - 2 Methods

#### Method 1: Blueprint (Easiest)
1. Go to [dashboard.render.com/blueprint](https://dashboard.render.com/blueprint)
2. Click **New Blueprint Instance**
3. Connect your GitHub repo: `ABBYCRM/abby-ai-runtime`
4. Render auto-reads `render.yaml`
5. Add your NIM API keys in the Render Dashboard under **Environment**
6. Click **Apply** - service deploys automatically

#### Method 2: Manual Web Service
1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **New +** -> **Web Service**
3. Connect GitHub repo `ABBYCRM/abby-ai-runtime`
4. Set:
   - **Runtime:** Docker
   - **Branch:** main
   - **Dockerfile Path:** `./Dockerfile`
   - **Plan:** Standard (or Starter to start)
5. Add environment variables (see table above)
6. Click **Create Web Service**

### Adding NIM Keys to Render

In your Render service dashboard:
```
Environment -> Add Environment Variable
```

Add each key:
- `NIM_API_KEY` = `nvapi-XXXXXXXX`
- `NIM_API_KEY_1` = `nvapi-YYYYYYYY`
- `NIM_API_KEY_2` = `nvapi-ZZZZZZZZ`
- ... (up to 10 keys supported)

ABBY automatically rotates across all available keys for load distribution.

## Project Structure

```
abby-ai-runtime/
  src/
    __init__.py           # Package init
    config.py             # Global LLM routing (NVIDIA NIM, multi-key)
    metagpt_pipeline.py   # MetaGPT deterministic pipeline
    crew_swarm.py         # CrewAI dynamic swarm
  main.py                 # FastAPI gateway
  requirements.txt        # Python dependencies
  Dockerfile              # Container image
  render.yaml             # Render Blueprint config
  README.md               # This file
  CHANGELOG.md            # Version history
  AI_NOTES.md             # Architecture documentation
  .github/workflows/
    deploy.yml            # Auto-deploy on push to main
  .gitignore
  watch_folder/
    incoming/             # File drop zone
    completed/            # Processed output
```

## Multi-Key Rotation

ABBY loads all `NIM_API_KEY*` environment variables and:
1. **Randomly selects** one key on startup for load distribution
2. **Falls back** gracefully if keys are exhausted
3. **Scales** across your key pool automatically

Add more keys anytime via Render Dashboard - no restart needed (auto-deploy on env change).

## License

Proprietary - ABBY Systems 2026
