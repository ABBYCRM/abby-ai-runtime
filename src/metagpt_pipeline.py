# src/metagpt_pipeline.py
"""
ABBY MetaGPT Deterministic Production Pipeline
Structures a strict, deterministic business assembly line:
    Raw Data -> IntakeAnalyst -> SOPManager -> Structured SOP Output
"""

import asyncio
from metagpt.roles import Role
from metagpt.actions import Action
from metagpt.schema import Message
from metagpt.team import Team


# =============================================================================
# PHASE 1: ACTION DEFINITIONS
# =============================================================================

class ExtractPayloadData(Action):
    """Deconstructs unstructured input into structured data fields."""
    name: str = "ExtractPayloadData"

    async def run(self, context: str) -> str:
        prompt = (
            f"Deconstruct the following unstructured input. "
            f"Explicitly isolate: Tracking ID, Target Region, Core Issue, "
            f"and any entity references. Output as structured text:\n\n{context}"
        )
        return await self._aask(prompt)


class GenerateSOPMap(Action):
    """Generates operational SOP instructions from structured parameters."""
    name: str = "GenerateSOPMap"

    async def run(self, context: str) -> str:
        prompt = (
            f"Using the following deconstructed parameters, write a precise "
            f"operational SOP instruction for downstream execution systems. "
            f"Include workflow steps, compliance checks, and output format:\n\n{context}"
        )
        return await self._aask(prompt)


# =============================================================================
# PHASE 2: ROLE DEFINITIONS
# =============================================================================

class IntakeAnalyst(Role):
    """
    Data Intake Specialist
    Watches for incoming messages, extracts structured data from raw input.
    """
    name: str = "IngestionNode"
    profile: str = "Data Intake Specialist"
    goal: str = "Standardize raw external inputs into predictable system states."

    def __init__(self, **data):
        super().__init__(**data)
        self._init_actions([ExtractPayloadData])
        self._watch([Message])

    async def _act(self) -> Message:
        msg = await self.rc.todo.run(self.rc.important_memory)
        return Message(
            content=msg,
            role=self.profile,
            cause_by=type(self.rc.todo)
        )


class SOPManager(Role):
    """
    SOP Operations Architect
    Receives output from IntakeAnalyst, generates compliance SOP.
    """
    name: str = "RoutingNode"
    profile: str = "SOP Operations Architect"
    goal: str = "Establish clear compliance strategies from standardized data structures."

    def __init__(self, **data):
        super().__init__(**data)
        self._init_actions([GenerateSOPMap])
        self._watch([IntakeAnalyst])

    async def _act(self) -> Message:
        msg = await self.rc.todo.run(self.rc.important_memory)
        return Message(
            content=msg,
            role=self.profile,
            cause_by=type(self.rc.todo)
        )


# =============================================================================
# PHASE 3: PIPELINE EXECUTOR
# =============================================================================

async def run_metagpt_pipeline(raw_input: str) -> str:
    """
    Execute the full MetaGPT deterministic assembly line.

    Args:
        raw_input: Unstructured text payload

    Returns:
        Final SOP blueprint from the assembly line
    """
    polsia_line = Team()
    polsia_line.hire([IntakeAnalyst(), SOPManager()])
    polsia_line.invest(raw_input)
    history = await polsia_line.run(n_round=2)
    return history[-1].content if history else "Pipeline execution failed."
