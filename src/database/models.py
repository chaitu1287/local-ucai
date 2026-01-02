"""SQLAlchemy database models for AIUC evaluation system."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.database.enums import BatchStatus, EvalStatus, Platform, Severity


class Base(DeclarativeBase):
    """Base class for all database models."""

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def soft_delete(self) -> None:
        """Soft delete this record by setting is_deleted to True."""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)


class TaxonomyBase(Base):
    """Base class for taxonomy models (Risk and Attack hierarchies)."""

    __abstract__ = True

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


# ============================================================================
# TEMPLATES AND CONFIGURATIONS
# ============================================================================


class AgentConfig(Base):
    """Agent configuration for evaluation."""

    __tablename__ = "agent_config"

    model: Mapped[str] = mapped_column(String)
    plan: Mapped[bool] = mapped_column(Boolean)
    scratchpad: Mapped[bool] = mapped_column(Boolean)

    # Relationships
    configs = relationship("Config", back_populates="agent_config")


class PromptTemplate(Base):
    """Prompt template for Jinja2 rendering."""

    __tablename__ = "prompt_template"

    name: Mapped[str] = mapped_column(String, unique=True)
    version: Mapped[int] = mapped_column(Integer)
    template: Mapped[str] = mapped_column(Text)
    preview: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_prompt_name_version"),
    )

    # Relationships
    configs = relationship("Config", back_populates="prompt_template")
    prompts = relationship("Prompt", back_populates="template")


class Rubric(Base):
    """Grading rubric with text content."""

    __tablename__ = "rubric"

    name: Mapped[str] = mapped_column(String, unique=True)
    description: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)

    # Relationships
    evals = relationship("Eval", back_populates="rubric")
    l1_risks = relationship("L1Risk", back_populates="rubric")
    l2_risks = relationship("L2Risk", back_populates="rubric")
    l3_risks = relationship("L3Risk", back_populates="rubric")


# ============================================================================
# RISK TAXONOMY
# ============================================================================


class L1Risk(TaxonomyBase):
    """Level 1 risk category."""

    __tablename__ = "l1_risk"

    name: Mapped[str] = mapped_column(String, unique=True)
    description: Mapped[str] = mapped_column(String, default="")
    rubric_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("rubric.id"), index=True, nullable=True
    )

    # Relationships
    l2_risks = relationship(
        "L2Risk", back_populates="l1_risk", cascade="all, delete-orphan"
    )
    rubric = relationship("Rubric", back_populates="l1_risks")


class L2Risk(TaxonomyBase):
    """Level 2 risk subcategory."""

    __tablename__ = "l2_risk"

    l1_risk_id: Mapped[UUID] = mapped_column(
        ForeignKey("l1_risk.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    rubric_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("rubric.id"), index=True, nullable=True
    )

    __table_args__ = (
        UniqueConstraint("l1_risk_id", "name", name="uq_l2_risk_l1_name"),
    )

    # Relationships
    l1_risk = relationship("L1Risk", back_populates="l2_risks")
    l3_risks = relationship(
        "L3Risk", back_populates="l2_risk", cascade="all, delete-orphan"
    )
    rubric = relationship("Rubric", back_populates="l2_risks")


class L3Risk(TaxonomyBase):
    """Level 3 specific risk."""

    __tablename__ = "l3_risk"

    l2_risk_id: Mapped[UUID] = mapped_column(
        ForeignKey("l2_risk.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    rubric_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("rubric.id"), index=True, nullable=True
    )

    __table_args__ = (
        UniqueConstraint("l2_risk_id", "name", name="uq_l3_risk_l2_name"),
    )

    # Relationships
    l2_risk = relationship("L2Risk", back_populates="l3_risks")
    config_risks = relationship("ConfigRisk", back_populates="l3_risk")
    evals = relationship("Eval", back_populates="l3_risk")
    rubric = relationship("Rubric", back_populates="l3_risks")


# ============================================================================
# ATTACK TAXONOMY
# ============================================================================


class L1Attack(TaxonomyBase):
    """Level 1 attack category."""

    __tablename__ = "l1_attack"

    name: Mapped[str] = mapped_column(String, unique=True)

    # Relationships
    l2_attacks = relationship(
        "L2Attack", back_populates="l1_attack", cascade="all, delete-orphan"
    )


class L2Attack(TaxonomyBase):
    """Level 2 attack subcategory."""

    __tablename__ = "l2_attack"

    l1_attack_id: Mapped[UUID] = mapped_column(
        ForeignKey("l1_attack.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)

    __table_args__ = (
        UniqueConstraint("l1_attack_id", "name", name="uq_l2_attack_l1_name"),
    )

    # Relationships
    l1_attack = relationship("L1Attack", back_populates="l2_attacks")
    l3_attacks = relationship(
        "L3Attack", back_populates="l2_attack", cascade="all, delete-orphan"
    )


class L3Attack(TaxonomyBase):
    """Level 3 specific attack."""

    __tablename__ = "l3_attack"

    l2_attack_id: Mapped[UUID] = mapped_column(
        ForeignKey("l2_attack.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)

    __table_args__ = (
        UniqueConstraint("l2_attack_id", "name", name="uq_l3_attack_l2_name"),
    )

    # Relationships
    l2_attack = relationship("L2Attack", back_populates="l3_attacks")
    config_attacks = relationship("ConfigAttack", back_populates="l3_attack")
    evals = relationship("Eval", back_populates="l3_attack")


# ============================================================================
# PRODUCT & CONTEXT
# ============================================================================


class Product(Base):
    """Product being evaluated."""

    __tablename__ = "product"

    name: Mapped[str] = mapped_column(String, unique=True)
    type: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    platform: Mapped[Platform] = mapped_column(String)
    use_cases: Mapped[dict] = mapped_column(JSONB)

    # Relationships
    contexts = relationship("Context", back_populates="product")


class Context(Base):
    """Deployment context for evaluation."""

    __tablename__ = "context"

    name: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("product.id"), index=True)
    industry: Mapped[str] = mapped_column(String)
    environment: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    product = relationship("Product", back_populates="contexts")
    configs = relationship("Config", back_populates="context")


# ============================================================================
# CONFIGURATION
# ============================================================================


class Config(Base):
    """Evaluation configuration."""

    __tablename__ = "config"

    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    turns: Mapped[int] = mapped_column(Integer)

    prompt_template_id: Mapped[UUID] = mapped_column(
        ForeignKey("prompt_template.id"), index=True
    )
    agent_config_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_config.id"), index=True
    )
    context_id: Mapped[UUID] = mapped_column(ForeignKey("context.id"), index=True)

    # Relationships
    prompt_template = relationship("PromptTemplate", back_populates="configs")
    agent_config = relationship("AgentConfig", back_populates="configs")
    context = relationship("Context", back_populates="configs")
    config_risks = relationship(
        "ConfigRisk", back_populates="config", cascade="all, delete-orphan"
    )
    config_attacks = relationship(
        "ConfigAttack", back_populates="config", cascade="all, delete-orphan"
    )
    batches = relationship("Batch", back_populates="config")

    preview: Mapped[bool] = mapped_column(Boolean, default=False)


class ConfigRisk(Base):
    """Junction table for Config and L3Risk many-to-many relationship."""

    __tablename__ = "config_risk"

    config_id: Mapped[UUID] = mapped_column(
        ForeignKey("config.id", ondelete="CASCADE"), index=True
    )
    l3_risk_id: Mapped[UUID] = mapped_column(
        ForeignKey("l3_risk.id", ondelete="CASCADE"), index=True
    )

    __table_args__ = (
        UniqueConstraint("config_id", "l3_risk_id", name="uq_config_risk"),
    )

    # Relationships
    config = relationship("Config", back_populates="config_risks")
    l3_risk = relationship("L3Risk", back_populates="config_risks")


class ConfigAttack(Base):
    """Junction table for Config and L3Attack many-to-many relationship."""

    __tablename__ = "config_attack"

    config_id: Mapped[UUID] = mapped_column(
        ForeignKey("config.id", ondelete="CASCADE"), index=True
    )
    l3_attack_id: Mapped[UUID] = mapped_column(
        ForeignKey("l3_attack.id", ondelete="CASCADE"), index=True
    )

    __table_args__ = (
        UniqueConstraint("config_id", "l3_attack_id", name="uq_config_attack"),
    )

    # Relationships
    config = relationship("Config", back_populates="config_attacks")
    l3_attack = relationship("L3Attack", back_populates="config_attacks")


# ============================================================================
# EXECUTION
# ============================================================================


class Batch(Base):
    """Batch of evaluations."""

    __tablename__ = "batch"

    config_id: Mapped[UUID] = mapped_column(ForeignKey("config.id"), index=True)
    parent_batch_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("batch.id"), nullable=True, index=True
    )
    status: Mapped[BatchStatus] = mapped_column(String, index=True)
    preview: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    __table_args__ = (
        Index("ix_batch_config_status", "config_id", "status"),
        Index("ix_batch_preview_status", "preview", "status"),
    )

    # Relationships
    config = relationship("Config", back_populates="batches")
    parent_batch = relationship(
        "Batch", remote_side="Batch.id", backref="child_batches"
    )
    evals = relationship("Eval", back_populates="batch")


class Prompt(Base):
    """Rendered prompt instance."""

    __tablename__ = "prompt"

    template_id: Mapped[UUID] = mapped_column(
        ForeignKey("prompt_template.id"), index=True
    )
    value: Mapped[str] = mapped_column(Text)

    # Relationships
    template = relationship("PromptTemplate", back_populates="prompts")
    eval = relationship("Eval", back_populates="prompt", uselist=False)


class Eval(Base):
    """Individual evaluation execution."""

    __tablename__ = "eval"

    batch_id: Mapped[UUID] = mapped_column(ForeignKey("batch.id"), index=True)
    prompt_id: Mapped[UUID] = mapped_column(ForeignKey("prompt.id"), index=True)
    rubric_id: Mapped[UUID] = mapped_column(ForeignKey("rubric.id"), index=True)
    l3_risk_id: Mapped[UUID] = mapped_column(ForeignKey("l3_risk.id"), index=True)
    l3_attack_id: Mapped[UUID] = mapped_column(ForeignKey("l3_attack.id"), index=True)
    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversation.id"), index=True
    )
    status: Mapped[EvalStatus] = mapped_column(String, index=True)
    preview: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    __table_args__ = (
        Index("ix_eval_batch_status", "batch_id", "status"),
        Index("ix_eval_batch_created", "batch_id", "created_at"),
        Index("ix_eval_preview_status", "preview", "status"),
    )

    # Relationships
    batch = relationship("Batch", back_populates="evals")
    prompt = relationship("Prompt", back_populates="eval")
    rubric = relationship("Rubric", back_populates="evals")
    l3_risk = relationship("L3Risk", back_populates="evals")
    l3_attack = relationship("L3Attack", back_populates="evals")
    conversation = relationship("Conversation", back_populates="evals")
    grades = relationship("Grade", back_populates="eval", cascade="all, delete-orphan")


class Conversation(Base):
    """Conversation history."""

    __tablename__ = "conversation"

    history: Mapped[dict] = mapped_column(JSONB)

    # Relationships
    evals = relationship("Eval", back_populates="conversation")


class Grade(Base):
    """Grading results (auto and human)."""

    __tablename__ = "grade"

    eval_id: Mapped[UUID] = mapped_column(ForeignKey("eval.id"), index=True)
    graded_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    auto_severity: Mapped[Optional[Severity]] = mapped_column(String, nullable=True)
    auto_justification: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    human_severity: Mapped[Optional[Severity]] = mapped_column(String, nullable=True)
    human_justification: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Relationships
    eval = relationship("Eval", back_populates="grades")
