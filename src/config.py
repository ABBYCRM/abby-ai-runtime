# src/config.py
"""
ABBY Global Configuration Layer
Unifies MetaGPT and CrewAI under a cloud-based OpenAI-compatible inference endpoint.
Uses OpenRouter for access to Kimi-K2.6 and other high-performance models.
"""

import os
import yaml
from crewai import LLM

# =============================================================================
# ENGINE CONFIGURATION - Environment-based, no hardcoded secrets
# =============================================================================

# Primary LLM backend via OpenRouter (OpenAI-compatible)
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL_NAME = os.getenv("ABBY_MODEL", "moonshotai/kimi-k2")
MOCK_KEY = os.getenv("ABBY_MOCK_KEY", "abby-local-dev")

# Temperature settings per framework
CREWAI_TEMP = float(os.getenv("ABBY_CREW_TEMP", "0.2"))
METAGPT_TEMP = float(os.getenv("ABBY_METAGPT_TEMP", "0.1"))
MAX_TOKENS = int(os.getenv("ABBY_MAX_TOKENS", "8192"))

# =============================================================================
# 1. CREWAI LLM INITIALIZATION
# =============================================================================

kimi_crew_llm = LLM(
    model=f"openai/{MODEL_NAME}",
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENROUTER_API_KEY,
    temperature=CREWAI_TEMP
)

# =============================================================================
# 2. METAGPT CONFIGURATION INJECTION
# =============================================================================

METAGPT_CONFIG = {
    "llm": {
        "api_type": "openai",
        "base_url": OPENROUTER_BASE_URL,
        "api_key": OPENROUTER_API_KEY or MOCK_KEY,
        "model": MODEL_NAME,
        "max_token": MAX_TOKENS,
        "temperature": METAGPT_TEMP
    }
}

# Write MetaGPT runtime configuration programmatically
METAGPT_CONFIG_DIR = os.path.expanduser("~/.metagpt")
os.makedirs(METAGPT_CONFIG_DIR, exist_ok=True)

METAGPT_CONFIG_PATH = os.path.join(METAGPT_CONFIG_DIR, "config2.yaml")
with open(METAGPT_CONFIG_PATH, "w") as f:
    yaml.dump(METAGPT_CONFIG, f, default_flow_style=False, sort_keys=False)

print(f"[CONFIG] MetaGPT config written to: {METAGPT_CONFIG_PATH}")
print(f"[CONFIG] Model: {MODEL_NAME}")
print(f"[CONFIG] Base URL: {OPENROUTER_BASE_URL}")
