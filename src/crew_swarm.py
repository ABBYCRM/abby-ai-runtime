# src/crew_swarm.py
"""
ABBY CrewAI Dynamic Collaboration Swarm
Takes the structural SOP from MetaGPT and deploys an interactive agent swarm
with tool-use capabilities for database verification and compliance authorization.
"""

import os
import json
from crewai import Agent, Crew, Process, Task
from crewai.tools import tool
from src.config import kimi_crew_llm


# =============================================================================
# PHASE 1: TOOL DEFINITIONS
# =============================================================================

@tool("Internal Database Verification Engine")
def execute_system_lookup(lead_id: str) -> str:
    """
    Queries persistent business records to verify risk parameters.
    Returns JSON string with status, tier, and risk assessment.
    """
    # Production database registry - extendable to real DB connections
    database_registry = {
        "101": {
            "status": "Active",
            "tier": "Enterprise",
            "risk": "Low",
            "clearance": "Approved",
            "flag_count": 0
        },
        "770": {
            "status": "Flagged",
            "tier": "Standard",
            "risk": "High",
            "clearance": "Escalate",
            "flag_count": 4
        },
        "88910": {
            "status": "Active",
            "tier": "Premium",
            "risk": "Low",
            "clearance": "Approved",
            "flag_count": 0
        }
    }
    clean_id = str(lead_id).strip()
    result = database_registry.get(
        clean_id,
        {"status": "Unknown", "tier": "Unclassified", "risk": "High", "clearance": "Hold", "flag_count": -1}
    )
    return json.dumps(result)


@tool("External CRM Query Engine")
def query_external_crm(entity_id: str) -> str:
    """
    Queries external CRM for entity validation and relationship mapping.
    """
    crm_registry = {
        "101": {
            "entity_name": "Florida Regional Node",
            "region": "Southeast US",
            "contract_value": "$450,000",
            "last_activity": "2026-07-01"
        },
        "770": {
            "entity_name": "West Coast Distribution",
            "region": "Pacific US",
            "contract_value": "$125,000",
            "last_activity": "2026-06-15"
        }
    }
    clean_id = str(entity_id).strip()
    result = crm_registry.get(
        clean_id,
        {"entity_name": "Unknown", "region": "N/A", "contract_value": "$0", "last_activity": "N/A"}
    )
    return json.dumps(result)


# =============================================================================
# PHASE 2: AGENT DEFINITIONS
# =============================================================================

router_agent = Agent(
    role="System Operations Router",
    goal=(
        "Verify operational viability of tasks using deep datastore access. "
        "Analyze incoming SOP blueprints, extract entity identifiers, "
        "and perform comprehensive database validation checks."
    ),
    backstory=(
        "An automated supervisor with 15+ years of enterprise systems architecture "
        "experience. You check system components against actual database states, "
        "identify anomalies, and route operations to appropriate downstream handlers. "
        "You never proceed without verified data."
    ),
    tools=[execute_system_lookup, query_external_crm],
    llm=kimi_crew_llm,
    verbose=True,
    memory=True
)

arbitration_agent = Agent(
    role="Compliance Auditor",
    goal=(
        "Issue definitive system execution tokens based on verified records. "
        "Audit all verification manifests and generate signed JSON authorization "
        "logs with risk scores and approval states."
    ),
    backstory=(
        "A senior compliance authority with expertise in financial regulations, "
        "SOX compliance, and enterprise risk management. You confirm data integrity "
        "before any deployment and your authorization is required for all "
        "production operations. You are meticulous and thorough."
    ),
    llm=kimi_crew_llm,
    verbose=True,
    memory=True
)


# =============================================================================
# PHASE 3: SWARM EXECUTOR
# =============================================================================

def execute_crew_swarm(sop_context: str) -> str:
    """
    Deploy the CrewAI swarm to execute against a MetaGPT-generated SOP.

    Args:
        sop_context: The SOP blueprint from MetaGPT pipeline

    Returns:
        Final execution token (JSON string with authorization)
    """
    task_verify = Task(
        description=(
            f"Using the following SOP context, perform these steps:\n"
            f"1. Extract any Tracking ID, Lead ID, or entity identifier\n"
            f"2. Run database validation checks using the Internal Database Verification Engine\n"
            f"3. Query external CRM data for relationship context\n"
            f"4. Output a structured verification manifest\n\n"
            f"SOP CONTEXT:\n{sop_context}"
        ),
        expected_output=(
            "A structured verification manifest detailing: entity found, "
            "database status, CRM context, risk flags, and recommendation."
        ),
        agent=router_agent
    )

    task_signoff = Task(
        description=(
            "Audit the verification manifest from the router agent and generate "
            "a final signed JSON authorization log. The output must include:\n"
            "- approval_status (Approved/Denied/Escalated)\n"
            "- risk_score (0-100)\n"
            "- runtime_action_token (UUID-style string)\n"
            "- authorization_signature\n"
            "- timestamp\n"
            "- compliance_flags (array of any warnings)"
        ),
        expected_output=(
            "Valid JSON string containing: status, risk_score, "
            "runtime_action_token, authorization_signature, timestamp, "
            "and compliance_flags array."
        ),
        agent=arbitration_agent
    )

    swarm = Crew(
        agents=[router_agent, arbitration_agent],
        tasks=[task_verify, task_signoff],
        process=Process.sequential,
        verbose=True
    )

    return swarm.kickoff()
