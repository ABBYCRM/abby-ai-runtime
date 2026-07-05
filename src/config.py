# src/config.py
"""
ABBY Global Configuration Layer
Unifies MetaGPT and CrewAI under NVIDIA NIM cloud inference.
Supports multiple API keys for rotation and load distribution.
"""

import os
import random
import yaml
from crewai import LLM

# =============================================================================
# NVIDIA NIM CONFIGURATION - Multiple API keys for resilience
# =============================================================================

# Collect all available NIM API keys from environment
def _get_nim_keys():
    """Gather all NVIDIA NIM API keys from environment variables."""
    keys = []
    # Primary key
    if os.getenv("NIM_API_KEY"):
        keys.append(os.getenv("NIM_API_KEY"))
    # Secondary keys (NIM_API_KEY_1 through NIM_API_KEY_10)
    for i in range(1, 11):
        key = os.getenv(f"NIM_API_KEY_{i}")
        if key:
            keys.append(key)
    return keys

NIM_KEYS = _get_nim_keys()
NIM_BASE_URL = os.getenv("NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")
MODEL_NAME = os.getenv("ABBY_MODEL", "nvidia/llama-3.1-nemotron-70b-instruct")
MOCK_KEY = os.getenv("ABBY_MOCK_KEY", "nvidia-nim-dev")

# Temperature settings per framework
CREWAI_TEMP = float(os.getenv("ABBY_CREW_TEMP", "0.2"))
METAGPT_TEMP = float(os.getenv("ABBY_METAGPT_TEMP", "0.1"))
MAX_TOKENS = int(os.getenv("ABBY_MAX_TOKENS", "8192"))

# Pick a random key for this instance (load distribution)
ACTIVE_KEY = random.choice(NIM_KEYS) if NIM_KEYS else MOCK_KEY

# =============================================================================
# 1. CREWAI LLM INITIALIZATION
# =============================================================================

kimi_crew_llm = LLM(
    model=f"openai/{MODEL_NAME}",
    base_url=NIM_BASE_URL,
    api_key=ACTIVE_KEY,
    temperature=CREWAI_TEMP
)

# =============================================================================
# 2. METAGPT CONFIGURATION INJECTION
# =============================================================================

METAGPT_CONFIG = {
    "llm": {
        "api_type": "openai",
        "base_url": NIM_BASE_URL,
        "api_key": ACTIVE_KEY or MOCK_KEY,
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
print(f"[CONFIG] Base URL: {NIM_BASE_URL}")
print(f"[CONFIG] API Keys loaded: {len(NIM_KEYS)}")
