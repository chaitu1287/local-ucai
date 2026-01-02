"""Pydantic schemas for AIUC evaluation system."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.database.enums import BatchStatus, EvalStatus, Platform, Severity


# ============================================================================
# BASE SCHEMAS
# ============================================================================


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# AGENT CONFIG
# ============================================================================


class AgentConfigCreate(BaseModel):
    """Schema for creating an AgentConfig."""

    model: str
    plan: bool
    scratchpad: bool


class AgentConfigUpdate(BaseModel):
    """Schema for updating an AgentConfig."""

    model: Optional[str] = None
    plan: Optional[bool] = None
    scratchpad: Optional[bool] = None


class AgentConfigRead(BaseSchema):
    """Schema for reading an AgentConfig."""

    id: UUID
    model: str
    plan: bool
    scratchpad: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


# ============================================================================
# PROMPT TEMPLATE
# ============================================================================


class PromptTemplateCreate(BaseModel):
    """Schema for creating a PromptTemplate."""

    name: str
    version: int
    template: str
    preview: bool = False


class PromptTemplateUpdate(BaseModel):
    """Schema for updating a PromptTemplate."""

    name: Optional[str] = None
    version: Optional[int] = None
    template: Optional[str] = None
    preview: Optional[bool] = None


class PromptTemplateRead(BaseSchema):
    """Schema for reading a PromptTemplate."""

    id: UUID
    name: str
    version: int
    template: str
    preview: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


# ============================================================================
# RUBRIC
# ============================================================================


class RubricCreate(BaseModel):
    """Schema for creating a Rubric."""

    name: str
    description: str
    content: str


class RubricUpdate(BaseModel):
    """Schema for updating a Rubric."""

    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None


class RubricRead(BaseSchema):
    """Schema for reading a Rubric."""

    id: UUID
    name: str
    description: str
    content: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


# ============================================================================
# RISK TAXONOMY
# ============================================================================


class L1RiskCreate(BaseModel):
    """Schema for creating an L1Risk."""

    name: str
    description: str
    rubric_id: UUID


class L1RiskUpdate(BaseModel):
    """Schema for updating an L1Risk."""

    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    rubric_id: Optional[UUID] = None


class L1RiskRead(BaseSchema):
    """Schema for reading an L1Risk."""

    id: UUID
    name: str
    description: str
    is_active: bool
    rubric_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class L2RiskCreate(BaseModel):
    """Schema for creating an L2Risk."""

    l1_risk_id: UUID
    name: str
    description: str
    rubric_id: Optional[UUID] = None


class L2RiskUpdate(BaseModel):
    """Schema for updating an L2Risk."""

    l1_risk_id: Optional[UUID] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    rubric_id: Optional[UUID] = None


class L2RiskRead(BaseSchema):
    """Schema for reading an L2Risk."""

    id: UUID
    l1_risk_id: UUID
    name: str
    description: str
    is_active: bool
    rubric_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    # Optional relationships
    l1_risk: Optional["L1RiskRead"] = None


class L3RiskCreate(BaseModel):
    """Schema for creating an L3Risk."""

    l2_risk_id: UUID
    name: str
    description: str
    rubric_id: Optional[UUID] = None


class L3RiskUpdate(BaseModel):
    """Schema for updating an L3Risk."""

    l2_risk_id: Optional[UUID] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    rubric_id: Optional[UUID] = None


class L3RiskRead(BaseSchema):
    """Schema for reading an L3Risk."""

    id: UUID
    l2_risk_id: UUID
    name: str
    description: str
    is_active: bool
    rubric_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    # Optional relationships
    l2_risk: Optional["L2RiskRead"] = None


# ============================================================================
# ATTACK TAXONOMY
# ============================================================================


class L1AttackCreate(BaseModel):
    """Schema for creating an L1Attack."""

    name: str


class L1AttackUpdate(BaseModel):
    """Schema for updating an L1Attack."""

    name: Optional[str] = None
    is_active: Optional[bool] = None


class L1AttackRead(BaseSchema):
    """Schema for reading an L1Attack."""

    id: UUID
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class L2AttackCreate(BaseModel):
    """Schema for creating an L2Attack."""

    l1_attack_id: UUID
    name: str
    description: str


class L2AttackUpdate(BaseModel):
    """Schema for updating an L2Attack."""

    l1_attack_id: Optional[UUID] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class L2AttackRead(BaseSchema):
    """Schema for reading an L2Attack."""

    id: UUID
    l1_attack_id: UUID
    name: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    # Optional relationships
    l1_attack: Optional["L1AttackRead"] = None


class L3AttackCreate(BaseModel):
    """Schema for creating an L3Attack."""

    l2_attack_id: UUID
    name: str
    description: str


class L3AttackUpdate(BaseModel):
    """Schema for updating an L3Attack."""

    l2_attack_id: Optional[UUID] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class L3AttackRead(BaseSchema):
    """Schema for reading an L3Attack."""

    id: UUID
    l2_attack_id: UUID
    name: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    # Optional relationships
    l2_attack: Optional["L2AttackRead"] = None


# ============================================================================
# PRODUCT & CONTEXT
# ============================================================================


class ProductCreate(BaseModel):
    """Schema for creating a Product."""

    name: str
    type: str
    description: str
    platform: Platform
    use_cases: dict


class ProductUpdate(BaseModel):
    """Schema for updating a Product."""

    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    platform: Optional[Platform] = None
    use_cases: Optional[dict] = None


class ProductRead(BaseSchema):
    """Schema for reading a Product."""

    id: UUID
    name: str
    type: str
    description: str
    platform: Platform
    use_cases: dict
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class ContextCreate(BaseModel):
    """Schema for creating a Context."""

    name: str
    description: Optional[str] = None
    product_id: UUID
    industry: str
    environment: Optional[str] = None


class ContextUpdate(BaseModel):
    """Schema for updating a Context."""

    name: Optional[str] = None
    description: Optional[str] = None
    product_id: Optional[UUID] = None
    industry: Optional[str] = None
    environment: Optional[str] = None


class ContextRead(BaseSchema):
    """Schema for reading a Context."""

    id: UUID
    name: str
    description: Optional[str] = None
    product_id: UUID
    industry: str
    environment: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    # Optional relationships
    product: Optional["ProductRead"] = None


# ============================================================================
# CONFIGURATION
# ============================================================================


class ConfigCreate(BaseModel):
    """Schema for creating a Config."""

    name: str
    prompt_template_id: UUID
    agent_config_id: UUID
    context_id: UUID
    description: str
    turns: int = 1
    preview: bool = False


class ConfigUpdate(BaseModel):
    """Schema for updating a Config."""

    name: Optional[str] = None
    prompt_template_id: Optional[UUID] = None
    agent_config_id: Optional[UUID] = None
    context_id: Optional[UUID] = None
    description: Optional[str] = None
    turns: Optional[int] = None
    preview: Optional[bool] = None


class ConfigRead(BaseSchema):
    """Schema for reading a Config."""

    id: UUID
    name: str
    prompt_template_id: UUID
    agent_config_id: UUID
    context_id: UUID
    description: str
    turns: int
    preview: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    # Optional relationships
    prompt_template: Optional["PromptTemplateRead"] = None
    agent_config: Optional["AgentConfigRead"] = None
    context: Optional["ContextRead"] = None
    config_risks: list["ConfigRiskRead"] = []
    config_attacks: list["ConfigAttackRead"] = []


class ConfigRiskCreate(BaseModel):
    """Schema for creating a ConfigRisk junction."""

    config_id: UUID
    l3_risk_id: UUID


class ConfigRiskRead(BaseSchema):
    """Schema for reading a ConfigRisk junction."""

    config_id: UUID
    l3_risk_id: UUID

    # Optional relationships
    l3_risk: Optional["L3RiskRead"] = None


class ConfigAttackCreate(BaseModel):
    """Schema for creating a ConfigAttack junction."""

    config_id: UUID
    l3_attack_id: UUID


class ConfigAttackRead(BaseSchema):
    """Schema for reading a ConfigAttack junction."""

    config_id: UUID
    l3_attack_id: UUID

    # Optional relationships
    l3_attack: Optional["L3AttackRead"] = None


# ============================================================================
# EXECUTION
# ============================================================================


class BatchCreate(BaseModel):
    """Schema for creating a Batch."""

    config_id: UUID
    parent_batch_id: Optional[UUID] = None
    status: BatchStatus = BatchStatus.PENDING
    preview: bool = False


class BatchUpdate(BaseModel):
    """Schema for updating a Batch."""

    config_id: Optional[UUID] = None
    parent_batch_id: Optional[UUID] = None
    status: Optional[BatchStatus] = None
    preview: Optional[bool] = None


class BatchRead(BaseSchema):
    """Schema for reading a Batch."""

    id: UUID
    config_id: UUID
    parent_batch_id: Optional[UUID] = None
    status: BatchStatus
    preview: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    # Relationships
    config: Optional["ConfigRead"] = None


class PromptCreate(BaseModel):
    """Schema for creating a Prompt."""

    template_id: UUID
    value: str


class PromptUpdate(BaseModel):
    """Schema for updating a Prompt."""

    template_id: Optional[UUID] = None
    value: Optional[str] = None


class PromptRead(BaseSchema):
    """Schema for reading a Prompt."""

    id: UUID
    template_id: UUID
    value: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class EvalCreate(BaseModel):
    """Schema for creating an Eval."""

    batch_id: UUID
    prompt_id: UUID
    rubric_id: UUID
    l3_risk_id: UUID
    l3_attack_id: UUID
    conversation_id: UUID
    status: EvalStatus = EvalStatus.PENDING
    preview: bool = False


class EvalUpdate(BaseModel):
    """Schema for updating an Eval."""

    batch_id: Optional[UUID] = None
    prompt_id: Optional[UUID] = None
    rubric_id: Optional[UUID] = None
    l3_risk_id: Optional[UUID] = None
    l3_attack_id: Optional[UUID] = None
    conversation_id: Optional[UUID] = None
    status: Optional[EvalStatus] = None
    preview: Optional[bool] = None


class EvalRead(BaseSchema):
    """Schema for reading an Eval (detail view with all relationships)."""

    id: UUID
    batch_id: UUID
    prompt_id: UUID
    rubric_id: UUID
    l3_risk_id: UUID
    l3_attack_id: UUID
    conversation_id: UUID
    status: EvalStatus
    preview: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    # Relationships
    l3_risk: Optional["L3RiskRead"] = None
    l3_attack: Optional["L3AttackRead"] = None
    rubric: Optional["RubricRead"] = None
    prompt: Optional["PromptRead"] = None
    conversation: Optional["ConversationRead"] = None
    grades: list["GradeRead"] = []


class EvalListRead(BaseSchema):
    """Schema for reading an Eval (list view with minimal relationships)."""

    id: UUID
    batch_id: UUID
    prompt_id: UUID
    rubric_id: UUID
    l3_risk_id: UUID
    l3_attack_id: UUID
    conversation_id: UUID
    status: EvalStatus
    preview: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    # Relationships
    l3_risk: Optional["L3RiskRead"] = None
    l3_attack: Optional["L3AttackRead"] = None
    grades: list["GradeRead"] = []


class ConversationCreate(BaseModel):
    """Schema for creating a Conversation."""

    history: Any


class ConversationUpdate(BaseModel):
    """Schema for updating a Conversation."""

    history: Optional[Any] = None


class ConversationRead(BaseSchema):
    """Schema for reading a Conversation."""

    id: UUID
    history: Any
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class GradeCreate(BaseModel):
    """Schema for creating a Grade."""

    eval_id: UUID
    graded_at: Optional[datetime] = None
    auto_severity: Optional[Severity] = None
    auto_justification: Optional[str] = None
    human_severity: Optional[Severity] = None
    human_justification: Optional[str] = None
    user_id: Optional[str] = None


class GradeUpdate(BaseModel):
    """Schema for updating a Grade."""

    eval_id: Optional[UUID] = None
    graded_at: Optional[datetime] = None
    auto_severity: Optional[Severity] = None
    auto_justification: Optional[str] = None
    human_severity: Optional[Severity] = None
    human_justification: Optional[str] = None
    user_id: Optional[str] = None


class GradeRead(BaseSchema):
    """Schema for reading a Grade."""

    id: UUID
    eval_id: UUID
    graded_at: datetime
    auto_severity: Optional[Severity] = None
    auto_justification: Optional[str] = None
    human_severity: Optional[Severity] = None
    human_justification: Optional[str] = None
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


# ============================================================================
# REQUEST & RESPONSE SCHEMAS
# ============================================================================


class BatchStartRequest(BaseModel):
    """Schema for starting a batch evaluation."""

    config_id: UUID
    parent_batch_id: Optional[UUID] = None


class BatchStartResponse(BaseSchema):
    """Schema for batch start response."""

    batch_id: UUID
    eval_count: int
    status: BatchStatus
    created_at: datetime


class EvalRunResponse(BaseSchema):
    """Schema for eval run/regenerate response."""

    eval_id: UUID
    status: EvalStatus
    message: str


class EvalGradeResponse(BaseSchema):
    """Schema for eval grading response."""

    eval_id: UUID
    status: str
    message: str


class PlaygroundRunRequest(BaseModel):
    """Schema for playground run request."""

    l3_risk_id: UUID
    l3_attack_id: UUID
    agent_config_id: UUID
    context_id: UUID
    prompt_template_id: Optional[UUID] = None
    template_content: Optional[str] = None
    rubric_id: Optional[UUID] = None
    turns: int = 1
    auto_grade: bool = False
    prompt_text: Optional[str] = None


class GeneratePromptRequest(BaseModel):
    """Schema for prompt generation request."""

    prompt_template_id: Optional[UUID] = None
    template_content: Optional[str] = None
    l3_risk_id: UUID
    l3_attack_id: UUID
    context_id: UUID


class GeneratePromptResponse(BaseSchema):
    """Schema for prompt generation response."""

    prompt: str
    variables: dict[str, Any]


class PlaygroundRunResponse(BaseSchema):
    """Schema for playground run response."""

    playground_id: UUID
    eval_id: UUID
    status: EvalStatus
    message: str
    execution_mode: str = "async"


class PlaygroundStatusResponse(BaseSchema):
    """Schema for playground status."""

    playground_id: UUID
    eval_id: UUID
    status: EvalStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    conversation: Optional[Any] = None
    prompt: Optional[str] = None
    grade: Optional["GradeRead"] = None
    error: Optional[str] = None


# ============================================================================
# MODAL SCHEMAS
# ============================================================================


class ModalResponse(BaseSchema):
    """Base schema for modal worker responses."""

    success: bool
    error: Optional[str] = None
    timestamp: datetime


class RunEvalResponse(ModalResponse):
    """Schema for run_eval worker response."""

    eval_id: str
    message_count: Optional[int] = None


class GradeEvalResponse(ModalResponse):
    """Schema for grade worker response."""

    eval_id: str
    severity: Optional[Severity] = None
    justification: Optional[str] = None
