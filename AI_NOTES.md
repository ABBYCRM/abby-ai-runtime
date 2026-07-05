# AI Notes - ABBY System Architecture

## Model Configuration
- **Primary Model:** Kimi-K2.6 (via OpenRouter)
- **API Format:** OpenAI-compatible
- **Max Tokens:** 8192
- **Temperature:** 0.1 (MetaGPT), 0.2 (CrewAI)
- **Backend:** Cloud inference (OpenRouter) - no local GPU required

## Architecture Overview

### MetaGPT Pipeline (Deterministic)
1. **IntakeAnalyst** - Extracts structured data from unstructured input
   - Isolates: Tracking ID, Region, Core Issue, Entity refs
   - Uses `_aask()` for LLM-powered extraction
2. **SOPManager** - Generates operational SOP from structured data
   - Creates workflow steps, compliance checks, output formats
   - Watches IntakeAnalyst output as trigger

### CrewAI Swarm (Dynamic)
1. **Router Agent** - System Operations Router
   - Tools: DB verification, CRM query
   - Verifies operational viability against datastores
2. **Arbitration Agent** - Compliance Auditor
   - No tools (pure reasoning)
   - Issues final authorization tokens with risk scores

### Data Flow
```
POST /v1/execute-pipeline
  -> raw_payload
    -> MetaGPT: IntakeAnalyst -> SOPManager
      -> sop_blueprint
        -> CrewAI: Router -> Arbitration
          -> execution_token (JSON)
```

## Design Decisions
1. **OpenRouter over local vLLM:** Render has no GPU support; OpenRouter provides Kimi-K2.6 access via API
2. **Separate endpoints:** `/v1/metagpt/run` and `/v1/crew/run` allow independent testing
3. **Mock databases:** Real DB connections can be swapped in via environment variables
4. **Docker deployment:** Containerized for consistent Render deployment

## Risks
- **Rate limiting:** OpenRouter may throttle; implement retry logic
- **Token costs:** Long agent conversations use significant tokens
- **Framework compatibility:** MetaGPT + CrewAI version conflicts possible
- **Cold starts:** Render free tier has spin-up delays

## Security Considerations
- API keys via environment variables only
- No secrets in code or Docker layers
- CORS enabled for all origins (restrict in production)
- No authentication middleware yet (add before public exposure)
