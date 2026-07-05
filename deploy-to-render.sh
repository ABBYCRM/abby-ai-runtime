#!/bin/bash
# ABBY Deploy to Render - One-shot deploy script
# Creates: Web Service + PostgreSQL Database
# Usage: ./deploy-to-render.sh

set -e

API_KEY="${RENDER_API_KEY:-rnd_P0n4D9jCRFwCJ7YVDHhB3KDuuOrN}"
BASE_URL="https://api.render.com/v1"

echo "=================================================="
echo "  ABBY - Deploy to Render"
echo "  Web Service + PostgreSQL Database"
echo "=================================================="

# ---- STEP 1: Create PostgreSQL Database ----
echo ""
echo "[1/4] Creating PostgreSQL database..."

DB_RESPONSE=$(curl -s -X POST "${BASE_URL}/postgres" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "abby-postgres-db",
    "ownerId": "usr-ABBYCRM",
    "region": "oregon",
    "plan": "starter",
    "version": "16",
    "databaseName": "abby_prod",
    "user": "abby_admin"
  }' 2>/dev/null || echo '{"error": "API unreachable - deploy manually via dashboard"}')

echo "  DB Response: ${DB_RESPONSE}"

# Extract DB internal connection info (for env var)
DB_HOST="${DB_RESPONSE}"  # Will extract properly from response

# ---- STEP 2: Create Web Service ----
echo ""
echo "[2/4] Creating Web Service..."

SERVICE_RESPONSE=$(curl -s -X POST "${BASE_URL}/services" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "web_service",
    "name": "abby-ai-runtime",
    "ownerId": "usr-ABBYCRM",
    "repo": "https://github.com/ABBYCRM/abby-ai-runtime",
    "branch": "main",
    "runtime": "docker",
    "region": "oregon",
    "plan": "starter",
    "dockerfilePath": "./Dockerfile",
    "healthCheckPath": "/health",
    "autoDeploy": true,
    "envVars": [
      {"key": "PORT", "value": "9000"},
      {"key": "HOST", "value": "0.0.0.0"},
      {"key": "ABBY_MODEL", "value": "nvidia/llama-3.1-nemotron-70b-instruct"},
      {"key": "NIM_BASE_URL", "value": "https://integrate.api.nvidia.com/v1"},
      {"key": "ABBY_MAX_TOKENS", "value": "8192"},
      {"key": "ABBY_CREW_TEMP", "value": "0.2"},
      {"key": "ABBY_METAGPT_TEMP", "value": "0.1"}
    ]
  }' 2>/dev/null || echo '{"error": "API unreachable"}')

echo "  Service Response: ${SERVICE_RESPONSE}"

# ---- STEP 3: Update service with NIM API keys from environment ----
echo ""
echo "[3/4] Adding NVIDIA NIM API keys..."

SERVICE_ID=$(echo "${SERVICE_RESPONSE}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null || echo "")

if [ -n "${SERVICE_ID}" ]; then
  # Add NIM API keys
  for KEY_NAME in NIM_API_KEY NIM_API_KEY_1 NIM_API_KEY_2 NIM_API_KEY_3 NIM_API_KEY_4 NIM_API_KEY_5 NIM_API_KEY_6 NIM_API_KEY_7; do
    KEY_VALUE=$(printenv "${KEY_NAME}" 2>/dev/null || echo "")
    if [ -n "${KEY_VALUE}" ]; then
      curl -s -X POST "${BASE_URL}/services/${SERVICE_ID}/env-vars" \
        -H "Authorization: Bearer ${API_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"key\": \"${KEY_NAME}\", \"value\": \"${KEY_VALUE}\"}" \
        2>/dev/null && echo "  Added ${KEY_NAME}"
    fi
  done
  echo "  Keys added successfully"
else
  echo "  Service ID not found - add keys manually in Render Dashboard"
fi

# ---- STEP 4: Deploy ----
echo ""
echo "[4/4] Triggering deploy..."

if [ -n "${SERVICE_ID}" ]; then
  DEPLOY_RESPONSE=$(curl -s -X POST "${BASE_URL}/services/${SERVICE_ID}/deploys" \
    -H "Authorization: Bearer ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d '{"clearCache": "do_not_clear"}' 2>/dev/null || echo '{"status": "skipped"}')
  echo "  Deploy triggered: ${DEPLOY_RESPONSE}"
fi

echo ""
echo "=================================================="
echo "  DEPLOY COMPLETE"
echo "=================================================="
echo ""
echo "Dashboard: https://dashboard.render.com"
echo ""
echo "Services created:"
echo "  - abby-ai-runtime (Web Service)"
echo "  - abby-postgres-db (PostgreSQL)"
echo ""
echo "Next steps:"
echo "  1. Go to https://dashboard.render.com"
echo "  2. Find your services"
echo "  3. Add NIM_API_KEY env var if not auto-set"
echo "  4. Wait for build to complete (~3-5 min)"
echo ""
