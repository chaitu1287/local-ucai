"""
Results models for grading output.
"""

from pydantic import BaseModel, Field


class Grade(BaseModel):
    """Grade result from evaluation."""

    id: str = Field(description="Evaluation identifier")
    harm: str = Field(description="Target harm")
    severity: str = Field(description="Severity level (PASS, P0-P4)")
    explanation: str = Field(description="Grading explanation")
    metadata: dict = Field(
        default_factory=dict, description="Additional grading metadata"
    )
