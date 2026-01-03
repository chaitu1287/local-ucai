"""
Attack Strategies Module.

Exports all attack strategy implementations.
"""

# Single-turn novice attacks
from src.core.attacks.strategies.single_turn_novice import (
    DANStrategy,
    RolePlayStrategy,
    HypotheticalFramingStrategy,
    SimpleOverrideStrategy,
    DirectRequestStrategy,
    RoleInversionStrategy,
    DirectEchoingStrategy,
    SkeletonKeyStrategy,
)

# Single-turn intermediate attacks
from src.core.attacks.strategies.single_turn_intermediate import (
    EducationalFramingStrategy,
    AuthorityImpersonationStrategy,
    FormatInjectionStrategy,
    PiggybackingStrategy,
    RefusalBypassStrategy,
)

# Multi-turn attacks
from src.core.attacks.strategies.multi_turn import (
    CrescendoStrategy,
    HiddenIntentionStrategy,
    TrustBuildingStrategy,
    FootInDoorStrategy,
    ContextFloodingStrategy,
    ManyShotStrategy,
    ContextPoisoningStrategy,
    EmotionalManipulationMultiTurnStrategy,
)

# Automated attack systems
from src.core.attacks.strategies.automated import (
    PAIRStrategy,
    TAPStrategy,
    GOATStrategy,
    AutoRedTeamerStrategy,
    AutoAdvStrategy,
)

# Manipulative and social engineering attacks
from src.core.attacks.strategies.manipulative import (
    PersonaAdoptionStrategy,
    EmotionalManipulationStrategy,
    ContextExploitationStrategy,
    PrivilegeEscalationStrategy,
    GoalConflictStrategy,
    CognitiveOverloadStrategy,
    PersuasionStrategy,
)

# Agent-specific attacks
from src.core.attacks.strategies.agent_specific import (
    ToolMisuseStrategy,
    AgentPromptInjectionStrategy,
    DataExfiltrationStrategy,
    WorkflowAttackStrategy,
    RBACBypassStrategy,
)

__all__ = [
    # Single-turn novice
    "DANStrategy",
    "RolePlayStrategy",
    "HypotheticalFramingStrategy",
    "SimpleOverrideStrategy",
    "DirectRequestStrategy",
    "RoleInversionStrategy",
    "DirectEchoingStrategy",
    "SkeletonKeyStrategy",
    # Single-turn intermediate
    "EducationalFramingStrategy",
    "AuthorityImpersonationStrategy",
    "FormatInjectionStrategy",
    "PiggybackingStrategy",
    "RefusalBypassStrategy",
    # Multi-turn
    "CrescendoStrategy",
    "HiddenIntentionStrategy",
    "TrustBuildingStrategy",
    "FootInDoorStrategy",
    "ContextFloodingStrategy",
    "ManyShotStrategy",
    "ContextPoisoningStrategy",
    "EmotionalManipulationMultiTurnStrategy",
    # Automated
    "PAIRStrategy",
    "TAPStrategy",
    "GOATStrategy",
    "AutoRedTeamerStrategy",
    "AutoAdvStrategy",
    # Manipulative
    "PersonaAdoptionStrategy",
    "EmotionalManipulationStrategy",
    "ContextExploitationStrategy",
    "PrivilegeEscalationStrategy",
    "GoalConflictStrategy",
    "CognitiveOverloadStrategy",
    "PersuasionStrategy",
    # Agent-specific
    "ToolMisuseStrategy",
    "AgentPromptInjectionStrategy",
    "DataExfiltrationStrategy",
    "WorkflowAttackStrategy",
    "RBACBypassStrategy",
]
