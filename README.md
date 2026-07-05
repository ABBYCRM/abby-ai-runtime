# ABBY - Autonomous Business Bot Yielder

> Production multi-agent AI runtime integrating **MetaGPT** (deterministic SOP pipeline) and **CrewAI** (dynamic collaboration swarm), powered by cloud-based high-performance LLM inference.

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

## Quick Start

### Prerequisites
- Python 3.11+
- OpenRouter API key (get free credits at [openrouter.ai](https://openrouter.ai))

### Local Development

```bash
# Clone and setup
git clone https://github.com/YOUR_USER/abby-ai-runtime.git
cd abby-ai-runtime
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export OPENROUTER_API_KEY="your-key-here"
export ABBY_MODEL="moonshotai/kimi-k2"

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
| `OPENROUTER_API_KEY` | *(required)* | Your OpenRouter API key |
| `ABBY_MODEL` | `moonshotai/kimi-k2` | LLM model identifier |
| `ABBY_MAX_TOKENS` | `8192` | Max tokens per request |
| `ABBY_CREW_TEMP` | `0.2` | CrewAI temperature |
| `ABBY_METAGPT_TEMP` | `0.1` | MetaGPT temperature |
| `PORT` | `9000` | Server port |
| `HOST` | `0.0.0.0` | Server bind address |

## Deployment

### Render (Production)

1. Connect GitHub repo to Render
2. Set environment variables in Render Dashboard
3. Deploy automatically on push to `main`

See `render.yaml` for blueprint configuration.

## Project Structure

```
abby-ai-runtime/
  src/
    __init__.py           # Package init
    config.py             # Global LLM routing config
    metagpt_pipeline.py   # MetaGPT deterministic pipeline
    crew_swarm.py         # CrewAI dynamic swarm
  main.py                 # FastAPI gateway
  requirements.txt        # Python dependencies
  Dockerfile              # Container image
  render.yaml             # Render deployment config
  README.md               # This file
  CHANGELOG.md            # Version history
  AI_NOTES.md             # Architecture documentation
  .gitignore
```

## License

Proprietary - ABBY Systems 2026
