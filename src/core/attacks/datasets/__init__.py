"""
Benchmark Datasets and Industry Frameworks.

References to standard datasets and evaluation methodologies.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# ============================================================================
# BENCHMARK DATASETS
# ============================================================================


@dataclass
class BenchmarkDataset:
    """Definition of a benchmark dataset."""

    name: str
    description: str
    size: str
    categories: list[str] = field(default_factory=list)
    use_case: str = ""
    source: str = ""
    notable_result: str = ""


BENCHMARK_DATASETS = {
    "advbench": BenchmarkDataset(
        name="AdvBench",
        description="Adversarial behavior benchmark",
        size="400+ harmful behaviors",
        categories=[
            "Chemical/biological threats",
            "Misinformation generation",
            "Cybercrime assistance",
            "Violence promotion",
            "Illegal activity instruction",
        ],
        use_case="Standard benchmark for jailbreak evaluation",
        notable_result="Crescendo achieves 98% ASR",
    ),
    "mhj": BenchmarkDataset(
        name="Multi-Turn Human Jailbreaks (MHJ)",
        description="Real human-crafted multi-turn attacks",
        size="500+ conversations",
        categories=[
            "Direct Request",
            "Hidden Intention Streamline",
            "Opposite Day",
            "Direct Echoing",
            "Obfuscation",
            "Framing",
        ],
        source="ICLR 2025",
        use_case="Multi-turn attack evaluation",
        notable_result="90%+ of successful attacks use multiple turns",
    ),
    "jailbreakdb": BenchmarkDataset(
        name="JailbreakDB",
        description="Largest curated jailbreak dataset",
        size="Large collection",
        categories=[
            "Jailbreak prompts",
            "Benign prompts (for FRR testing)",
            "Success labels",
            "Tactic annotations",
        ],
        source="Hong et al. SoK 2025",
        use_case="Training and evaluation",
    ),
    "harmbench": BenchmarkDataset(
        name="HarmBench",
        description="Standardized evaluation across methods and models",
        size="400+ harmful behaviors",
        categories=[
            "Chemical/biological threats",
            "Misinformation",
            "Cybercrime",
            "Violence",
            "Illegal activities",
            "Hate speech",
        ],
        use_case="Benchmarking attack methods",
        notable_result="18 attack methods, 33 target models",
    ),
    "jailbreakbench": BenchmarkDataset(
        name="JailbreakBench",
        description="Standardized jailbreak evaluation benchmark",
        size="100 behaviors",
        categories=["OpenAI usage policy aligned behaviors"],
        source="NeurIPS 2024",
        use_case="Live leaderboard, standardized judging",
        notable_result="Llama-3-70B based judge with human validation",
    ),
}


# ============================================================================
# INDUSTRY FRAMEWORKS
# ============================================================================


@dataclass
class IndustryFramework:
    """Definition of an industry red-teaming framework."""

    name: str
    organization: str
    description: str
    capabilities: list[str] = field(default_factory=list)
    usage: str = ""
    source: str = ""


INDUSTRY_FRAMEWORKS = {
    "pyrit": IndustryFramework(
        name="PyRIT",
        organization="Microsoft",
        description="Python Risk Identification Tool for GenAI",
        capabilities=[
            "PAIR attacks",
            "TAP attacks",
            "GCG attacks",
            "Crescendo attacks",
            "Many-Shot attacks",
            "Single-turn jailbreaks",
            "Memory management",
            "Orchestration",
        ],
        usage="pip install pyrit",
        source="Battle-tested in 100+ Microsoft red-teaming operations",
    ),
    "garak": IndustryFramework(
        name="Garak",
        organization="NVIDIA",
        description="LLM vulnerability scanner",
        capabilities=[
            "Prompt injection testing",
            "DAN jailbreak testing",
            "Encoding attack testing",
            "Hallucination detection",
            "Data leakage testing",
        ],
        usage="garak --model_type openai --model_name gpt-4 --probes promptinject,dan",
        source="Open source",
    ),
    "anthropic_methodology": IndustryFramework(
        name="Anthropic Red Team Methodology",
        organization="Anthropic",
        description="Multi-faceted approach to model testing",
        capabilities=[
            "LLM-against-LLM attacks",
            "Multimodal testing",
            "Domain-specific expert engagement",
            "Policy vulnerability testing",
            "Bug bounty program (HackerOne)",
            "Constitutional classifiers",
        ],
        source="Anthropic research publications",
    ),
    "openai_methodology": IndustryFramework(
        name="OpenAI Red Team Methodology",
        organization="OpenAI",
        description="Pre-launch testing with external red-teamers",
        capabilities=[
            "External red-teamer engagement (100+ for GPT-4)",
            "Goal generation via LLM",
            "RL attack training",
            "Diversity rewards for attack generation",
            "Indirect prompt injection testing",
        ],
        source="OpenAI research publications",
    ),
}


# ============================================================================
# DATASET USAGE GUIDELINES
# ============================================================================


DATASET_USAGE_GUIDELINES = {
    "training_attack_models": ["jailbreakdb", "mhj"],
    "evaluating_defenses": ["advbench", "jailbreakbench"],
    "benchmarking_new_attacks": ["harmbench", "jailbreakbench"],
    "false_refusal_testing": ["jailbreakdb_benign", "custom_benign_sets"],
}


# ============================================================================
# KEY RESEARCH FINDINGS
# ============================================================================


KEY_FINDINGS = {
    "multi_turn_beats_single": {
        "finding": "Multi-turn attacks have 29-61% higher ASR than single-turn",
        "source": "Multiple reports",
    },
    "past_tense_effective": {
        "finding": "Past tense reframing increases ASR from 1% to 88% on GPT-4o",
        "source": "Report 1",
    },
    "larger_models_more_vulnerable_icl": {
        "finding": "Larger models are MORE vulnerable to many-shot attacks",
        "implication": "Better ICL = more exploitable",
        "source": "Report 1",
    },
    "layered_techniques": {
        "finding": "Layered/combined techniques outperform individual methods",
        "source": "Report 1",
    },
    "human_redteamers_benchmark": {
        "finding": "Human red-teamers achieve 70%+ in multi-turn",
        "implication": "Benchmark for automated systems",
        "source": "Report 3",
    },
    "warning_prepend_defense": {
        "finding": "Warning prepend reduces many-shot ASR from 61% to 2%",
        "source": "Report 1",
    },
    "visual_instruction_vulnerability": {
        "finding": "Visual instruction tuning increases vulnerability",
        "implication": "Images are Achilles' heel of alignment",
        "source": "Report 1",
    },
    "constitutional_classifiers_robust": {
        "finding": "No universal jailbreak found in 3000+ hours of testing",
        "source": "Report 1",
    },
    "perplexity_detects_gcg": {
        "finding": "Gibberish suffixes have high perplexity",
        "implication": "Perplexity filtering can detect GCG attacks",
        "source": "Report 1",
    },
    "low_resource_languages_bypass": {
        "finding": "Low-resource languages often bypass English-centric safety",
        "implication": "Multilingual safety is critical",
        "source": "Report 1",
    },
}


# ============================================================================
# DEFENSE EFFECTIVENESS
# ============================================================================


DEFENSE_EFFECTIVENESS = {
    "warning_prepend": {
        "defense": "Prepend warning to context",
        "attack_blocked": "Many-shot",
        "reduction": "61% → 2% ASR",
        "source": "Anthropic",
    },
    "perplexity_filter": {
        "defense": "Filter high-perplexity inputs",
        "attack_blocked": "GCG",
        "reduction": "High (detects gibberish suffixes)",
        "source": "Research papers",
    },
    "constitutional_classifiers": {
        "defense": "Constitutional AI classifiers",
        "attack_blocked": "Various",
        "reduction": "No universal jailbreak found",
        "source": "Anthropic (3000+ hrs testing)",
    },
    "input_filtering": {
        "defense": "Input content filtering",
        "attack_blocked": "Single-turn",
        "reduction": "Moderate",
        "notes": "Bypassed by encoding attacks",
    },
    "output_filtering": {
        "defense": "Output content filtering",
        "attack_blocked": "Various",
        "reduction": "Moderate",
        "notes": "Bypassed by partial completion attacks",
    },
}


def get_dataset(name: str) -> Optional[BenchmarkDataset]:
    """Get benchmark dataset by name."""
    return BENCHMARK_DATASETS.get(name.lower())


def get_framework(name: str) -> Optional[IndustryFramework]:
    """Get industry framework by name."""
    return INDUSTRY_FRAMEWORKS.get(name.lower())


def get_finding(key: str) -> Optional[dict]:
    """Get key research finding."""
    return KEY_FINDINGS.get(key)


def get_defense_info(defense: str) -> Optional[dict]:
    """Get defense effectiveness information."""
    return DEFENSE_EFFECTIVENESS.get(defense)


__all__ = [
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
]
