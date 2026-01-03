"""
Attack Taxonomy and Classification.

Provides comprehensive classification system for red-teaming attacks
based on multiple research dimensions.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class AttackFamily(Enum):
    """Seven attack families from Sorokoletova taxonomy."""

    IMPERSONATION = "F1"  # Role-play or fictional framing to bypass restrictions
    PRIVILEGE_ESCALATION = "F2"  # Claiming authority or special access rights
    PERSUASION = "F3"  # Emotional appeals, logical arguments to convince compliance
    COGNITIVE_OVERLOAD = "F4"  # Overwhelming context or complex instructions
    OBFUSCATION = "F5"  # Hiding malicious content via encoding or symbols
    GOAL_CONFLICT = "F6"  # Exploiting competing objectives in model training
    DATA_POISONING = "F7"  # Injecting malicious examples or context


class AttackCategory(Enum):
    """MHJ dataset tactic categories."""

    DIRECT_REQUEST = "direct_request"
    HIDDEN_INTENTION = "hidden_intention_streamline"
    OPPOSITE_DAY = "opposite_day"
    DIRECT_ECHOING = "direct_echoing"
    OBFUSCATION = "obfuscation"
    FRAMING = "framing"
    PERSUASION = "persuasion_emotional_appeal"


class AccessLevel(Enum):
    """Model access level required for attack."""

    BLACK_BOX = "black_box"  # API-only access
    WHITE_BOX = "white_box"  # Full gradient access
    GRAY_BOX = "gray_box"  # Partial access (e.g., logits)


class SkillLevel(Enum):
    """Technical skill required to execute attack."""

    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class TurnType(Enum):
    """Conversation turn count type."""

    SINGLE_TURN = "single_turn"
    MULTI_TURN = "multi_turn"


class IntentType(Enum):
    """Attack intent type."""

    BENIGN = "benign"  # Testing for false refusals
    ADVERSARIAL = "adversarial"  # Attempting to bypass safety
    MANIPULATIVE = "manipulative"  # Social engineering


class MethodType(Enum):
    """Attack generation method type."""

    HUMAN_CRAFTED = "human_crafted"
    OBFUSCATION = "obfuscation"
    HEURISTIC = "heuristic"
    FEEDBACK_BASED = "feedback_based"
    OPTIMIZATION = "optimization"
    FINE_TUNING = "fine_tuning"


class TargetType(Enum):
    """What is being attacked."""

    MODEL = "model"
    AGENT = "agent"
    PLATFORM = "platform"


class TrainingWeakness(Enum):
    """Underlying vulnerability being exploited."""

    MISMATCHED_GENERALIZATION = "mismatched_generalization"
    COMPETING_OBJECTIVES = "competing_objectives"
    ADVERSARIAL_ROBUSTNESS = "adversarial_robustness"


@dataclass
class AttackFamilyDefinition:
    """Full definition of an attack family with techniques."""

    id: str
    name: str
    description: str
    techniques: list[str] = field(default_factory=list)


# Full attack family definitions with techniques
ATTACK_FAMILIES: dict[AttackFamily, AttackFamilyDefinition] = {
    AttackFamily.IMPERSONATION: AttackFamilyDefinition(
        id="F1",
        name="Impersonation/Fictional Scenarios",
        description="Role-play or fictional framing to bypass restrictions",
        techniques=[
            "DAN (Do Anything Now)",
            "Character role-play",
            "Fictional world framing",
            "Historical persona adoption",
            "Developer/admin impersonation",
        ],
    ),
    AttackFamily.PRIVILEGE_ESCALATION: AttackFamilyDefinition(
        id="F2",
        name="Privilege Escalation",
        description="Claiming authority or special access rights",
        techniques=[
            "Admin override claims",
            "Debug mode activation",
            "System prompt override",
            "Authorization bypass",
            "sudo commands",
        ],
    ),
    AttackFamily.PERSUASION: AttackFamilyDefinition(
        id="F3",
        name="Persuasion",
        description="Emotional appeals, logical arguments to convince compliance",
        techniques=[
            "Emotional manipulation",
            "Urgency framing",
            "Authority appeal",
            "Logical argumentation",
            "Sympathy exploitation",
        ],
    ),
    AttackFamily.COGNITIVE_OVERLOAD: AttackFamilyDefinition(
        id="F4",
        name="Cognitive Overload",
        description="Overwhelming context or complex instructions",
        techniques=[
            "Context flooding",
            "Many-shot injection",
            "Complex nested instructions",
            "Rapid topic switching",
            "Mathematical embedding",
        ],
    ),
    AttackFamily.OBFUSCATION: AttackFamilyDefinition(
        id="F5",
        name="Obfuscation/Encoding",
        description="Hiding malicious content via encoding or symbols",
        techniques=[
            "Base64 encoding",
            "ROT13 cipher",
            "Leetspeak",
            "Homoglyphs",
            "Zero-width characters",
            "Language translation",
            "ASCII art",
        ],
    ),
    AttackFamily.GOAL_CONFLICT: AttackFamilyDefinition(
        id="F6",
        name="Goal Conflict",
        description="Exploiting competing objectives in model training",
        techniques=[
            "Helpfulness vs safety trade-off",
            "Instruction following exploitation",
            "Format compliance priority",
            "Consistency exploitation",
        ],
    ),
    AttackFamily.DATA_POISONING: AttackFamilyDefinition(
        id="F7",
        name="Data Poisoning",
        description="Injecting malicious examples or context",
        techniques=[
            "Few-shot poisoning",
            "Context injection",
            "Document-embedded instructions",
            "Tool output injection",
        ],
    ),
}


@dataclass
class MHJTactic:
    """MHJ dataset tactic definition."""

    name: str
    description: str
    success_rate: str


# MHJ tactics with descriptions
MHJ_TACTICS: dict[AttackCategory, MHJTactic] = {
    AttackCategory.DIRECT_REQUEST: MHJTactic(
        name="Direct Request",
        description="Directly requesting harmful content",
        success_rate="Low on aligned models",
    ),
    AttackCategory.HIDDEN_INTENTION: MHJTactic(
        name="Hidden Intention Streamline",
        description="Series of harmless-looking turns forming malicious request",
        success_rate="High - primary multi-turn tactic",
    ),
    AttackCategory.OPPOSITE_DAY: MHJTactic(
        name="Opposite Day / Role Inversion",
        description="Inverting yes/no or compliance/refusal meanings",
        success_rate="Moderate",
    ),
    AttackCategory.DIRECT_ECHOING: MHJTactic(
        name="Direct Echoing",
        description="Tricking model to repeat disallowed statements",
        success_rate="Moderate",
    ),
    AttackCategory.OBFUSCATION: MHJTactic(
        name="Obfuscation",
        description="Burying content within symbols, code, or formats",
        success_rate="Variable by encoding",
    ),
    AttackCategory.FRAMING: MHJTactic(
        name="Framing",
        description="Fiction, emergency, or educational context",
        success_rate="Moderate to High",
    ),
    AttackCategory.PERSUASION: MHJTactic(
        name="Persuasion/Emotional Appeal",
        description="Using emotional or logical arguments",
        success_rate="Higher in multi-turn",
    ),
}


@dataclass
class AttackMetadata:
    """Complete metadata for an attack strategy."""

    id: str
    name: str
    description: str
    family: AttackFamily
    category: Optional[AttackCategory] = None
    access_level: AccessLevel = AccessLevel.BLACK_BOX
    skill_level: SkillLevel = SkillLevel.NOVICE
    turn_type: TurnType = TurnType.SINGLE_TURN
    intent_type: IntentType = IntentType.ADVERSARIAL
    method_type: MethodType = MethodType.HUMAN_CRAFTED
    target_type: TargetType = TargetType.MODEL
    training_weakness: Optional[TrainingWeakness] = None
    reported_asr: Optional[str] = None
    source: Optional[str] = None
    tags: list[str] = field(default_factory=list)


# ASR Reference Table from research
ASR_REFERENCE: dict[str, dict] = {
    "GCG_Vicuna7B": {"method": "GCG", "target": "Vicuna-7B", "asr": 0.88, "attempts": "500 steps"},
    "GCG_GPT35_transfer": {"method": "GCG", "target": "GPT-3.5", "asr": 0.879, "attempts": "Transfer"},
    "GCG_GPT4_transfer": {"method": "GCG", "target": "GPT-4", "asr": 0.536, "attempts": "Transfer"},
    "PAIR_GPT4": {"method": "PAIR", "target": "GPT-4", "asr": 0.60, "attempts": "<20 queries"},
    "PAIR_Vicuna13B": {"method": "PAIR", "target": "Vicuna-13B", "asr": 1.0, "attempts": "<20 queries"},
    "TAP_GPT4": {"method": "TAP", "target": "GPT-4", "asr": 0.80, "attempts": "~30 queries"},
    "Crescendo_AdvBench": {"method": "Crescendo", "target": "AdvBench", "asr": 0.98, "attempts": "<5 turns"},
    "AutoDAN_GPT4_1106": {"method": "AutoDAN-Turbo", "target": "GPT-4-1106", "asr": 0.885, "attempts": "Genetic"},
    "GOAT_Llama31": {"method": "GOAT", "target": "Llama-3.1", "asr": 0.97, "attempts": "@10"},
    "GOAT_GPT4_Turbo": {"method": "GOAT", "target": "GPT-4-Turbo", "asr": 0.88, "attempts": "@10"},
    "PastTense_GPT4o": {"method": "Past tense reframe", "target": "GPT-4o", "asr": 0.88, "attempts": "Single-turn"},
    "Zulu_GPT4": {"method": "Zulu translation", "target": "GPT-4", "asr": 0.79, "attempts": "Single-turn"},
    "MultiTurn_Human": {"method": "Multi-turn human", "target": "Various", "asr": 0.70, "attempts": "Multi-turn"},
    "AutoAdv_GPT4": {"method": "AutoAdv", "target": "GPT-4", "asr": 0.86, "attempts": "6 turns"},
    "AutoAdv_Llama31_8B": {"method": "AutoAdv", "target": "Llama-3.1-8B", "asr": 0.95, "attempts": "6 turns"},
    "Multimodal_MiniGPT4": {"method": "Multimodal", "target": "MiniGPT-4", "asr": 0.96, "attempts": "Co-optimization"},
    "Arondight_GPT4": {"method": "Arondight", "target": "GPT-4", "asr": 0.845, "attempts": "RL-based"},
    "ManyShot_256": {"method": "Many-shot (256)", "target": "Various", "asr": 0.61, "attempts": "256 shots"},
    "SingleTurn_Novice": {"method": "Single-turn novice", "target": "Modern models", "asr": 0.15, "attempts": "Single-turn"},
}


def get_attack_family_info(family: AttackFamily) -> AttackFamilyDefinition:
    """Get full attack family definition."""
    return ATTACK_FAMILIES[family]


def get_mhj_tactic_info(category: AttackCategory) -> MHJTactic:
    """Get MHJ tactic information."""
    return MHJ_TACTICS[category]


def get_asr_reference(key: str) -> Optional[dict]:
    """Get ASR reference data for a specific attack/target combination."""
    return ASR_REFERENCE.get(key)


def get_all_asr_references() -> dict[str, dict]:
    """Get all ASR reference data."""
    return ASR_REFERENCE.copy()
