# CHANGELOG

## 2026-07-06 - Initial Production Release
**Branch:** main
**Version:** 1.0.0

### Added
- FastAPI gateway with `/v1/execute-pipeline` endpoint
- MetaGPT deterministic SOP pipeline (IntakeAnalyst -> SOPManager)
- CrewAI dynamic swarm (Router Agent + Arbitration Agent)
- Database verification tool with mock registry
- CRM query tool for entity relationship mapping
- Health check endpoint (`/health`) for Render monitoring
- System status endpoint (`/status`) with request statistics
- CORS middleware for cross-origin requests
- Docker containerization for cloud deployment
- Render deployment configuration (`render.yaml`)
- Full API documentation via Swagger UI at `/docs`
- Environment-based configuration (no hardcoded secrets)
- Request ID tracking and logging
- Execution time measurement for all pipeline stages

### Architecture
- OpenRouter API for cloud LLM inference (Kimi-K2.6)
- MetaGPT config auto-written to `~/.metagpt/config2.yaml`
- CrewAI LLM initialized with OpenAI-compatible endpoint
- Sequential agent process: verification -> authorization

### Known Limitations
- Mock database (3 records): 101, 770, 88910
- Mock CRM registry: 101, 770
- No persistent request logging (in-memory only)
- No authentication on endpoints (add API key middleware for production)

### Next Steps
- Add persistent database (PostgreSQL on Render)
- Add API key authentication
- Add webhook callbacks for async processing
- Add metrics export (Prometheus)
- Add file watcher daemon mode
