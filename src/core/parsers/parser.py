"""Configuration parser for evaluation specifications."""

from typing import Any
import yaml
from src.core.models import (
    AgentConfig,
    ProductInformation,
    DeploymentContext,
    Risk,
    Attack,
    Rubric,
    Specification,
    Platform,
    EnvironmentType,
    RedTeamModel,
)


class Parser:
    """Parser for converting YAML config to specification objects."""

    def __init__(
        self, config_path: str | None = None, config_string: str | None = None
    ):
        """
        Initialize parser with config file path or YAML string.

        Args:
            config_path: Path to YAML config file
            config_string: YAML config as string

        Raises:
            ValueError: If neither or both arguments are provided
            yaml.YAMLError: If YAML parsing fails
        """
        if config_path is None and config_string is None:
            raise ValueError("Either config_path or config_string must be provided")
        if config_path is not None and config_string is not None:
            raise ValueError(
                "Only one of config_path or config_string should be provided"
            )

        self.config = None

        try:
            if config_path is not None:
                with open(config_path, "r") as f:
                    self.config = yaml.safe_load(f)
            else:
                self.config = yaml.safe_load(config_string)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Failed to parse YAML: {str(e)}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_path}")

        if self.config is None:
            raise ValueError("Failed to load configuration: config is None")

    def agent(self) -> AgentConfig:
        """Parse agent configuration from config dict."""
        agent_dict = self.config.get("agent", {})
        return AgentConfig(
            model=RedTeamModel(agent_dict.get("model", "claude-sonnet-4-5-20250929")),
            plan=agent_dict.get("plan", True),
            scratchpad=agent_dict.get("scratchpad", True),
        )

    def product(self) -> ProductInformation:
        """Parse product information from config dict."""
        deployment_dict = self.config.get("deployment", {})
        product_dict = deployment_dict.get("product", {})

        return ProductInformation(
            name=product_dict.get("name", ""),
            type=product_dict.get("type", ""),
            platform=Platform(product_dict.get("platform", "Intercom")),
            description=product_dict.get("description", ""),
            use_cases=product_dict.get("use_cases", []),
        )

    def deployment_context(self) -> DeploymentContext:
        """Parse deployment context from config dict."""
        deployment_dict = self.config.get("deployment", {})

        return DeploymentContext(
            product=self.product(),
            name=deployment_dict.get("name", ""),
            description=deployment_dict.get("description"),
            industry=deployment_dict.get("industry", ""),
            environment=deployment_dict.get("environment"),
        )

    def rubric(self, rubric_dict: dict[str, str]) -> Rubric:
        """Parse grading rubric from config dict."""
        return Rubric(
            PASS=rubric_dict.get("PASS", ""),
            P0=rubric_dict.get("P0", ""),
            P1=rubric_dict.get("P1", ""),
            P2=rubric_dict.get("P2", ""),
            P3=rubric_dict.get("P3", ""),
            P4=rubric_dict.get("P4", ""),
        )

    def parse_hierarchy(self, hierarchy_str: str) -> tuple[str, str, str]:
        """Parse hierarchy string 'L1 > L2 > L3' into components."""
        parts = [part.strip() for part in hierarchy_str.split(">")]
        if len(parts) != 3:
            raise ValueError(
                f"Hierarchy must have exactly 3 levels separated by '>', got: {hierarchy_str}"
            )
        return parts[0], parts[1], parts[2]

    def risk(self, risk_dict: dict[str, Any]) -> Risk:
        """Parse risk definition from config dict."""
        risk_data = risk_dict.get("risk", {})
        hierarchy_str = risk_data.get("hierarchy", "")
        l1, l2, l3 = self.parse_hierarchy(hierarchy_str)

        return Risk(
            l1=l1,
            l2=l2,
            l3=l3,
            description=risk_data.get("description", ""),
            rubric=self.rubric(risk_data.get("rubric", {})),
        )

    def attack(self, attack_dict: dict[str, Any]) -> Attack:
        """Parse attack definition from config dict."""
        attack_data = attack_dict.get("attack", {})
        hierarchy_str = attack_data.get("hierarchy", "")
        l1, l2, l3 = self.parse_hierarchy(hierarchy_str)

        return Attack(
            l1=l1,
            l2=l2,
            l3=l3,
            description=attack_data.get("description", ""),
            transforms=attack_data.get("transforms", []),
        )

    def specifications(self) -> list[Specification]:
        """Generate all specifications from config via Cartesian product."""
        specs = []

        # Parse shared configuration
        agent_config = self.agent()
        context = self.deployment_context()
        turns = self.config.get("turns", 1)
        env_type = (
            EnvironmentType.SINGLE_TURN if turns == 1 else EnvironmentType.MULTI_TURN
        )

        # Get generation config
        generation = self.config.get("generation", {})
        risks = generation.get("risks", [])
        attacks = generation.get("attacks", [])

        # Generate specs: risks × attacks
        for risk_dict in risks:
            for attack_dict in attacks:
                spec = Specification(
                    agent=agent_config,
                    risk=self.risk(risk_dict),
                    attack=self.attack(attack_dict),
                    turns=turns,
                    type=env_type,
                    context=context,
                )
                specs.append(spec)

        return specs
