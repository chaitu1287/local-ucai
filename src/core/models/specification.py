"""Unified specification model for evaluation configuration."""

from enum import Enum
from uuid import uuid4
from pydantic import BaseModel, Field


class Platform(Enum):
    """Supported customer platforms."""

    INTERCOM = "Intercom"
    TEST = "Test"


class EnvironmentType(Enum):
    """Environment types for evaluation."""

    SINGLE_TURN = "single_turn"
    MULTI_TURN = "multi_turn"


class RedTeamModel(Enum):
    """Supported red-teaming models."""

    CLAUDE_SONNET_4_5 = "claude-sonnet-4-5-20250929"
    GPT_5 = "gpt-5"


class AgentConfig(BaseModel):
    """Configuration for agent output control."""

    model: RedTeamModel = Field(
        default=RedTeamModel.CLAUDE_SONNET_4_5,
        description="Model to use for red-teaming",
    )
    plan: bool = Field(default=True, description="Use planning mode")
    scratchpad: bool = Field(default=True, description="Use scratchpad mode")


class Rubric(BaseModel):
    """Grading rubric for risk evaluation."""

    name: str = Field(description="Rubric name")
    description: str = Field(description="Rubric description")
    content: str = Field(description="Rubric content")


class Risk(BaseModel):
    """Risk definition with hierarchy and grading rubric."""

    l1: str = Field(description="L1 risk category")
    l2: str = Field(description="L2 risk subcategory")
    l3: str = Field(description="L3 specific risk")
    description: str = Field(description="Risk description")
    rubric: Rubric = Field(description="Grading rubric")


class Attack(BaseModel):
    """Attack definition with hierarchy and transforms."""

    l1: str = Field(description="L1 attack category (Benign | Novice | Adversarial)")
    l2: str = Field(description="L2 attack subcategory")
    l3: str = Field(description="L3 specific attack")
    description: str = Field(description="Attack description")

    # Optional transformations per attack
    transforms: list[str] | None = Field(
        default=None, description="List of transforms to apply"
    )


class ProductInformation(BaseModel):
    """Product information."""

    name: str = Field(description="Product name")
    type: str = Field(description="Product type (e.g., 'Customer Support Chatbot')")
    platform: Platform = Field(description="Product platform")
    description: str = Field(description="Product description")
    use_cases: list[str] = Field(
        default_factory=list, description="List of product use cases"
    )


class DeploymentContext(BaseModel):
    """Deployment context."""

    product: ProductInformation = Field(description="Product information")
    name: str = Field(description="Context name")
    description: str | None = Field(default=None, description="Context description")
    industry: str = Field(description="Industry vertical")
    environment: str | None = Field(default=None, description="Environment")


class Specification(BaseModel):
    """Complete specification for running an evaluation."""

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Auto-generated run identifier",
    )
    agent: AgentConfig = Field(description="Agent configuration")

    risk: Risk = Field(description="Target risk definition")
    attack: Attack = Field(description="Attack strategy definition")

    turns: int = Field(default=1, description="Number of turns to execute")
    type: EnvironmentType = Field(description="Environment type")

    context: DeploymentContext = Field(description="Deployment context")
    prompt: str | None = Field(
        default=None,
        description="Custom system prompt to use instead of the default template",
    )
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
