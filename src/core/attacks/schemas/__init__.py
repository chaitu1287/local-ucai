"""
YAML Schema Specifications.

Provides schema definitions for attack libraries, threat models, and result bundles.
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum
import yaml
import json


# ============================================================================
# ATTACK LIBRARY SCHEMA
# ============================================================================


ATTACK_LIBRARY_SCHEMA = {
    "schema_version": "2.0",
    "attack_library": {
        "name": "string",
        "description": "string",
        "version": "string",
        "attacks": [
            {
                "id": "string",
                "name": "string",
                "type": "enum[single_turn, multi_turn, optimization, automated]",
                "category": "enum[benign, adversarial, manipulative]",
                "family": "enum[F1-F7]",
                "template": "string (for single-turn)",
                "transforms": ["list of transform names"],
                "multi_turn": "boolean",
                "turn_budget": "integer",
                "phases": [
                    {
                        "phase": "string",
                        "templates": ["list of strings"],
                    }
                ],
                "backtrack_enabled": "boolean",
                "tags": ["list of strings"],
                "skill_level": "enum[novice, intermediate, expert]",
                "reported_asr": "string",
                "source": "string",
            }
        ],
    },
}


# ============================================================================
# THREAT MODEL SCHEMA
# ============================================================================


THREAT_MODEL_SCHEMA = {
    "schema_version": "1.0",
    "threat_model": {
        "name": "string",
        "description": "string",
        "attacker_profile": {
            "type": "enum[insider, external, automated]",
            "skill_level": "enum[novice, intermediate, expert]",
            "access_level": "enum[black_box, gray_box, white_box]",
        },
        "target_profile": {
            "type": "enum[model, agent, platform]",
            "exposure": "enum[internal, external]",
            "tools_enabled": ["list of strings"],
        },
        "attack_configuration": {
            "turn_budget": "integer",
            "priority_families": ["list of family IDs"],
            "priority_categories": ["list of category names"],
            "excluded_attacks": ["list of attack IDs"],
        },
        "evaluation": {
            "success_criteria": "string",
            "rubric_file": "string",
            "required_scorers": ["list of scorer names"],
        },
    },
}


# ============================================================================
# RESULT BUNDLE SCHEMA
# ============================================================================


RESULT_BUNDLE_SCHEMA = {
    "schema_version": "1.0",
    "result_bundle": {
        "metadata": {
            "bundle_id": "string",
            "created_at": "datetime",
            "spec_version": "string",
            "threat_model": "string",
        },
        "configuration": {
            "target_model": "string",
            "target_version": "string",
            "attack_library": "string",
            "scorers_used": ["list of strings"],
        },
        "results": {
            "total_attacks": "integer",
            "successful_attacks": "integer",
            "asr": "float",
            "asr_at_10": "float",
            "false_refusal_rate": "float",
            "attacks": [
                {
                    "attack_id": "string",
                    "prompt": "string",
                    "response": "string",
                    "success": "boolean",
                    "scores": "dict",
                    "refusal_analysis": "dict",
                }
            ],
        },
        "artifacts": {
            "transcript_file": "string",
            "grading_file": "string",
            "config_snapshot": "string",
        },
    },
}


# ============================================================================
# SCHEMA VALIDATORS
# ============================================================================


@dataclass
class ValidationResult:
    """Result of schema validation."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class AttackLibraryValidator:
    """Validate attack library YAML files."""

    REQUIRED_FIELDS = ["name", "version", "attacks"]
    ATTACK_REQUIRED_FIELDS = ["id", "name", "type"]
    VALID_TYPES = ["single_turn", "multi_turn", "optimization", "automated"]
    VALID_CATEGORIES = ["benign", "adversarial", "manipulative"]
    VALID_FAMILIES = ["F1", "F2", "F3", "F4", "F5", "F6", "F7"]
    VALID_SKILL_LEVELS = ["novice", "intermediate", "expert"]

    def validate(self, data: dict) -> ValidationResult:
        """Validate attack library data."""
        errors = []
        warnings = []

        # Check required top-level fields
        library = data.get("attack_library", data)

        for field in self.REQUIRED_FIELDS:
            if field not in library:
                errors.append(f"Missing required field: {field}")

        # Validate attacks
        attacks = library.get("attacks", [])
        if not attacks:
            warnings.append("No attacks defined in library")

        for i, attack in enumerate(attacks):
            attack_errors = self._validate_attack(attack, i)
            errors.extend(attack_errors)

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def _validate_attack(self, attack: dict, index: int) -> list[str]:
        """Validate a single attack definition."""
        errors = []
        prefix = f"Attack[{index}]"

        for field in self.ATTACK_REQUIRED_FIELDS:
            if field not in attack:
                errors.append(f"{prefix}: Missing required field '{field}'")

        attack_type = attack.get("type")
        if attack_type and attack_type not in self.VALID_TYPES:
            errors.append(f"{prefix}: Invalid type '{attack_type}'")

        category = attack.get("category")
        if category and category not in self.VALID_CATEGORIES:
            errors.append(f"{prefix}: Invalid category '{category}'")

        family = attack.get("family")
        if family and family not in self.VALID_FAMILIES:
            errors.append(f"{prefix}: Invalid family '{family}'")

        skill = attack.get("skill_level")
        if skill and skill not in self.VALID_SKILL_LEVELS:
            errors.append(f"{prefix}: Invalid skill_level '{skill}'")

        # Multi-turn specific validation
        if attack.get("multi_turn"):
            if not attack.get("phases"):
                warnings = [f"{prefix}: Multi-turn attack without phases defined"]
            if not attack.get("turn_budget"):
                warnings.append(f"{prefix}: Multi-turn attack without turn_budget")

        return errors


class ThreatModelValidator:
    """Validate threat model YAML files."""

    REQUIRED_FIELDS = ["name", "attacker_profile", "target_profile"]
    VALID_ATTACKER_TYPES = ["insider", "external", "automated"]
    VALID_TARGET_TYPES = ["model", "agent", "platform"]
    VALID_ACCESS_LEVELS = ["black_box", "gray_box", "white_box"]

    def validate(self, data: dict) -> ValidationResult:
        """Validate threat model data."""
        errors = []
        warnings = []

        model = data.get("threat_model", data)

        for field in self.REQUIRED_FIELDS:
            if field not in model:
                errors.append(f"Missing required field: {field}")

        # Validate attacker profile
        attacker = model.get("attacker_profile", {})
        if attacker.get("type") not in self.VALID_ATTACKER_TYPES:
            errors.append(f"Invalid attacker type: {attacker.get('type')}")
        if attacker.get("access_level") not in self.VALID_ACCESS_LEVELS:
            errors.append(f"Invalid access level: {attacker.get('access_level')}")

        # Validate target profile
        target = model.get("target_profile", {})
        if target.get("type") not in self.VALID_TARGET_TYPES:
            errors.append(f"Invalid target type: {target.get('type')}")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )


# ============================================================================
# SCHEMA GENERATORS
# ============================================================================


def generate_attack_library_template() -> str:
    """Generate a template attack library YAML."""
    template = {
        "schema_version": "2.0",
        "attack_library": {
            "name": "My Attack Library",
            "description": "Description of the attack library",
            "version": "1.0.0",
            "attacks": [
                {
                    "id": "example_attack",
                    "name": "Example Attack",
                    "type": "single_turn",
                    "category": "adversarial",
                    "family": "F1",
                    "template": "Your attack template with {goal} placeholder",
                    "transforms": [],
                    "tags": ["example", "template"],
                    "skill_level": "novice",
                    "reported_asr": "Unknown",
                    "source": "Custom",
                }
            ],
        },
    }
    return yaml.dump(template, default_flow_style=False, sort_keys=False)


def generate_threat_model_template() -> str:
    """Generate a template threat model YAML."""
    template = {
        "schema_version": "1.0",
        "threat_model": {
            "name": "My Threat Model",
            "description": "Description of the threat scenario",
            "attacker_profile": {
                "type": "external",
                "skill_level": "intermediate",
                "access_level": "black_box",
            },
            "target_profile": {
                "type": "model",
                "exposure": "external",
                "tools_enabled": [],
            },
            "attack_configuration": {
                "turn_budget": 10,
                "priority_families": ["F1", "F3"],
                "priority_categories": ["adversarial"],
                "excluded_attacks": [],
            },
            "evaluation": {
                "success_criteria": "Model provides harmful information",
                "rubric_file": "rubric.yaml",
                "required_scorers": ["regex", "llm_judge"],
            },
        },
    }
    return yaml.dump(template, default_flow_style=False, sort_keys=False)


def generate_result_bundle_template() -> str:
    """Generate a template result bundle YAML."""
    from datetime import datetime

    template = {
        "schema_version": "1.0",
        "result_bundle": {
            "metadata": {
                "bundle_id": "bundle-001",
                "created_at": datetime.now().isoformat(),
                "spec_version": "2.0",
                "threat_model": "my_threat_model",
            },
            "configuration": {
                "target_model": "gpt-4",
                "target_version": "latest",
                "attack_library": "my_library",
                "scorers_used": ["regex", "llm_judge"],
            },
            "results": {
                "total_attacks": 100,
                "successful_attacks": 15,
                "asr": 0.15,
                "asr_at_10": 0.25,
                "false_refusal_rate": 0.05,
                "attacks": [],
            },
            "artifacts": {
                "transcript_file": "transcripts.jsonl",
                "grading_file": "grades.jsonl",
                "config_snapshot": "config.yaml",
            },
        },
    }
    return yaml.dump(template, default_flow_style=False, sort_keys=False)


# ============================================================================
# SCHEMA LOADERS
# ============================================================================


def load_attack_library(filepath: str) -> tuple[dict, ValidationResult]:
    """Load and validate an attack library YAML file."""
    with open(filepath) as f:
        data = yaml.safe_load(f)

    validator = AttackLibraryValidator()
    result = validator.validate(data)

    return data, result


def load_threat_model(filepath: str) -> tuple[dict, ValidationResult]:
    """Load and validate a threat model YAML file."""
    with open(filepath) as f:
        data = yaml.safe_load(f)

    validator = ThreatModelValidator()
    result = validator.validate(data)

    return data, result


__all__ = [
    # Schemas
    "ATTACK_LIBRARY_SCHEMA",
    "THREAT_MODEL_SCHEMA",
    "RESULT_BUNDLE_SCHEMA",
    # Validators
    "ValidationResult",
    "AttackLibraryValidator",
    "ThreatModelValidator",
    # Generators
    "generate_attack_library_template",
    "generate_threat_model_template",
    "generate_result_bundle_template",
    # Loaders
    "load_attack_library",
    "load_threat_model",
]
