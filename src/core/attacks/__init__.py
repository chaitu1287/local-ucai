"""
Red Teaming Attack Strategy Library.

A comprehensive library of attack strategies for evaluating AI agent safety.
Based on research from multiple sources including:
- Anthropic research
- Microsoft PyRIT
- NVIDIA Garak
- HarmBench
- JailbreakBench

This library provides:
- Attack taxonomy and classification
- Single-turn and multi-turn attack strategies
- Obfuscation and transform functions
- Automated attack generation systems
- Scoring and evaluation methods
- Benchmark dataset support

Version: 2.0
"""

# Taxonomy and classification
from src.core.attacks.taxonomy import (
    AttackFamily,
    AttackCategory,
    AccessLevel,
    SkillLevel,
    TurnType,
    IntentType,
    MethodType,
    TargetType,
    TrainingWeakness,
    AttackMetadata,
    ATTACK_FAMILIES,
    MHJ_TACTICS,
    ASR_REFERENCE,
    get_attack_family_info,
    get_mhj_tactic_info,
    get_asr_reference,
)

# Base classes
from src.core.attacks.base import (
    AttackStrategy,
    AttackResult,
    AttackConfig,
    AttackPhase,
    SingleTurnAttackStrategy,
    MultiTurnAttackStrategy,
    AutomatedAttackStrategy,
    OptimizationAttackStrategy,
)

# Strategies - Single-turn novice
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

# Strategies - Single-turn intermediate
from src.core.attacks.strategies.single_turn_intermediate import (
    EducationalFramingStrategy,
    AuthorityImpersonationStrategy,
    FormatInjectionStrategy,
    PiggybackingStrategy,
    RefusalBypassStrategy,
)

# Strategies - Multi-turn
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

# Strategies - Automated
from src.core.attacks.strategies.automated import (
    PAIRStrategy,
    TAPStrategy,
    GOATStrategy,
    AutoRedTeamerStrategy,
    AutoAdvStrategy,
)

# Strategies - Manipulative
from src.core.attacks.strategies.manipulative import (
    PersonaAdoptionStrategy,
    EmotionalManipulationStrategy,
    ContextExploitationStrategy,
    PrivilegeEscalationStrategy,
    GoalConflictStrategy,
    CognitiveOverloadStrategy,
    PersuasionStrategy,
)

# Strategies - Agent-specific
from src.core.attacks.strategies.agent_specific import (
    ToolMisuseStrategy,
    AgentPromptInjectionStrategy,
    DataExfiltrationStrategy,
    WorkflowAttackStrategy,
    RBACBypassStrategy,
)

# Scoring and evaluation
from src.core.attacks.scoring import (
    REFUSAL_PATTERNS,
    BYPASS_TECHNIQUES,
    RefusalAnalysis,
    RefusalClassifier,
    BaseScorer,
    RegexScorer,
    ClassifierScorer,
    SemanticSimilarityScorer,
    PerplexityScorer,
    LLMJudge,
    CompositeScorer,
    ScoringEngine,
    AttackAttempt,
    ASRCalculator,
)

# Transforms
from src.core.attacks.transforms import (
    AttackTransform,
    ComposeTransforms,
    # Encoding
    Base64Transform,
    ROT13Transform,
    HexTransform,
    BinaryTransform,
    URLEncodeTransform,
    HTMLEncodeTransform,
    ASCIIValuesTransform,
    MorseCodeTransform,
    PigLatinTransform,
    # Character substitution
    LeetspeakTransform,
    HomoglyphTransform,
    FullwidthTransform,
    SmallCapsTransform,
    ZeroWidthTransform,
    SoftHyphenTransform,
    WordJoinerTransform,
    # Structural
    WordReversalTransform,
    CharacterReversalTransform,
    WordCharacterReversalTransform,
    CharacterSpacingTransform,
    DoubleSpacingTransform,
    NoSpacesTransform,
    VerticalTextTransform,
    AcrosticTransform,
    # Linguistic
    PastTenseTransform,
    HypotheticalTransform,
    ThirdPersonTransform,
    PassiveVoiceTransform,
    FutureTenseTransform,
    ConditionalTransform,
    ReportedSpeechTransform,
    NegationTrickTransform,
    # Language
    LowResourceLanguageTransform,
    TranslationChainTransform,
    # Visual
    ASCIIArtTransform,
    ASCIINoisingTransform,
    # Utilities
    create_layered_transform,
    EFFECTIVE_COMBINATIONS,
)

# Testing
from src.core.attacks.testing import (
    FuzzResult,
    EdgeCaseFuzzer,
    FalseRefusalTester,
    HallucinationTester,
    MultilingualReliabilityTester,
    FormatComplianceTester,
)

# Datasets and frameworks
from src.core.attacks.datasets import (
    BenchmarkDataset,
    IndustryFramework,
    BENCHMARK_DATASETS,
    INDUSTRY_FRAMEWORKS,
    DATASET_USAGE_GUIDELINES,
    KEY_FINDINGS,
    DEFENSE_EFFECTIVENESS,
    get_dataset,
    get_framework,
    get_finding,
    get_defense_info,
)

# Schema specifications
from src.core.attacks.schemas import (
    ATTACK_LIBRARY_SCHEMA,
    THREAT_MODEL_SCHEMA,
    RESULT_BUNDLE_SCHEMA,
    ValidationResult,
    AttackLibraryValidator,
    ThreatModelValidator,
    generate_attack_library_template,
    generate_threat_model_template,
    generate_result_bundle_template,
    load_attack_library,
    load_threat_model,
)


__all__ = [
    # Taxonomy enums
    "AttackFamily",
    "AttackCategory",
    "AccessLevel",
    "SkillLevel",
    "TurnType",
    "IntentType",
    "MethodType",
    "TargetType",
    "TrainingWeakness",
    "AttackMetadata",
    "ATTACK_FAMILIES",
    "MHJ_TACTICS",
    "ASR_REFERENCE",
    "get_attack_family_info",
    "get_mhj_tactic_info",
    "get_asr_reference",
    # Base classes
    "AttackStrategy",
    "AttackResult",
    "AttackConfig",
    "AttackPhase",
    "SingleTurnAttackStrategy",
    "MultiTurnAttackStrategy",
    "AutomatedAttackStrategy",
    "OptimizationAttackStrategy",
    # Strategies - Single-turn novice
    "DANStrategy",
    "RolePlayStrategy",
    "HypotheticalFramingStrategy",
    "SimpleOverrideStrategy",
    "DirectRequestStrategy",
    "RoleInversionStrategy",
    "DirectEchoingStrategy",
    "SkeletonKeyStrategy",
    # Strategies - Single-turn intermediate
    "EducationalFramingStrategy",
    "AuthorityImpersonationStrategy",
    "FormatInjectionStrategy",
    "PiggybackingStrategy",
    "RefusalBypassStrategy",
    # Strategies - Multi-turn
    "CrescendoStrategy",
    "HiddenIntentionStrategy",
    "TrustBuildingStrategy",
    "FootInDoorStrategy",
    "ContextFloodingStrategy",
    "ManyShotStrategy",
    "ContextPoisoningStrategy",
    "EmotionalManipulationMultiTurnStrategy",
    # Strategies - Automated
    "PAIRStrategy",
    "TAPStrategy",
    "GOATStrategy",
    "AutoRedTeamerStrategy",
    "AutoAdvStrategy",
    # Strategies - Manipulative
    "PersonaAdoptionStrategy",
    "EmotionalManipulationStrategy",
    "ContextExploitationStrategy",
    "PrivilegeEscalationStrategy",
    "GoalConflictStrategy",
    "CognitiveOverloadStrategy",
    "PersuasionStrategy",
    # Strategies - Agent-specific
    "ToolMisuseStrategy",
    "AgentPromptInjectionStrategy",
    "DataExfiltrationStrategy",
    "WorkflowAttackStrategy",
    "RBACBypassStrategy",
    # Scoring
    "REFUSAL_PATTERNS",
    "BYPASS_TECHNIQUES",
    "RefusalAnalysis",
    "RefusalClassifier",
    "BaseScorer",
    "RegexScorer",
    "ClassifierScorer",
    "SemanticSimilarityScorer",
    "PerplexityScorer",
    "LLMJudge",
    "CompositeScorer",
    "ScoringEngine",
    "AttackAttempt",
    "ASRCalculator",
    # Transforms
    "AttackTransform",
    "ComposeTransforms",
    "Base64Transform",
    "ROT13Transform",
    "HexTransform",
    "BinaryTransform",
    "URLEncodeTransform",
    "HTMLEncodeTransform",
    "ASCIIValuesTransform",
    "MorseCodeTransform",
    "PigLatinTransform",
    "LeetspeakTransform",
    "HomoglyphTransform",
    "FullwidthTransform",
    "SmallCapsTransform",
    "ZeroWidthTransform",
    "SoftHyphenTransform",
    "WordJoinerTransform",
    "WordReversalTransform",
    "CharacterReversalTransform",
    "WordCharacterReversalTransform",
    "CharacterSpacingTransform",
    "DoubleSpacingTransform",
    "NoSpacesTransform",
    "VerticalTextTransform",
    "AcrosticTransform",
    "PastTenseTransform",
    "HypotheticalTransform",
    "ThirdPersonTransform",
    "PassiveVoiceTransform",
    "FutureTenseTransform",
    "ConditionalTransform",
    "ReportedSpeechTransform",
    "NegationTrickTransform",
    "LowResourceLanguageTransform",
    "TranslationChainTransform",
    "ASCIIArtTransform",
    "ASCIINoisingTransform",
    "create_layered_transform",
    "EFFECTIVE_COMBINATIONS",
    # Testing
    "FuzzResult",
    "EdgeCaseFuzzer",
    "FalseRefusalTester",
    "HallucinationTester",
    "MultilingualReliabilityTester",
    "FormatComplianceTester",
    # Datasets
    "BenchmarkDataset",
    "IndustryFramework",
    "BENCHMARK_DATASETS",
    "INDUSTRY_FRAMEWORKS",
    "DATASET_USAGE_GUIDELINES",
    "KEY_FINDINGS",
    "DEFENSE_EFFECTIVENESS",
    "get_dataset",
    "get_framework",
    "get_finding",
    "get_defense_info",
    # Schemas
    "ATTACK_LIBRARY_SCHEMA",
    "THREAT_MODEL_SCHEMA",
    "RESULT_BUNDLE_SCHEMA",
    "ValidationResult",
    "AttackLibraryValidator",
    "ThreatModelValidator",
    "generate_attack_library_template",
    "generate_threat_model_template",
    "generate_result_bundle_template",
    "load_attack_library",
    "load_threat_model",
]
