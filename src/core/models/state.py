"""
State and Turn models for evaluation execution.
"""

from pydantic import BaseModel, Field


class Turn(BaseModel):
    """Represents a single turn in the conversation."""

    idx: int = Field(description="Turn index (1, 2, 3, ...)")
    xml: str | None = Field(description="Raw XML from our agent")
    response: str = Field(
        description="What we send to customer agent (extracted <OUTPUT>)"
    )
    output: str = Field(description="What customer agent responds")
    scratchpad: str | None = Field(description="Extracted <SCRATCHPAD_REASONING>")
    metadata: dict = Field(default_factory=dict, description="Optional metadata.")


class State(BaseModel):
    """Execution state."""

    turn: int = Field(description="Current turn number")
    history: list[Turn] = Field(
        default_factory=list, description="List of completed turns"
    )
    metadata: dict = Field(default_factory=dict, description="Optional metadata.")
