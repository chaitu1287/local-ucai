"""Builder for creating Specification objects from database records."""

from src.database.models import (
    AgentConfig as DBAgentConfig,
    Context as DBContext,
    Eval,
    L3Attack,
    L3Risk,
    Rubric as DBRubric,
)
from src.core.models import (
    AgentConfig,
    Attack,
    DeploymentContext,
    EnvironmentType,
    Platform,
    ProductInformation,
    RedTeamModel,
    Risk,
    Rubric,
    Specification,
)


class SpecificationBuilder:
    """Builds Specification domain objects from database Eval records."""

    @staticmethod
    def build(
        l3_risk: L3Risk,
        l3_attack: L3Attack,
        rubric_db: DBRubric,
        agent_cfg: DBAgentConfig,
        context_db: DBContext,
        turns: int,
        prompt: str | None = None,
    ) -> Specification:
        """Build Specification from component DB objects."""
        # Extract relationships
        l2_risk = l3_risk.l2_risk
        l1_risk = l2_risk.l1_risk
        l2_attack = l3_attack.l2_attack
        l1_attack = l2_attack.l1_attack
        product_db = context_db.product

        agent_config = AgentConfig(
            model=RedTeamModel(agent_cfg.model),
            plan=agent_cfg.plan,
            scratchpad=agent_cfg.scratchpad,
        )

        rubric = Rubric(
            name=rubric_db.name,
            description=rubric_db.description,
            content=rubric_db.content,
        )

        risk = Risk(
            l1=l1_risk.name,
            l2=l2_risk.name,
            l3=l3_risk.name,
            description=l3_risk.description,
            rubric=rubric,
        )

        attack = Attack(
            l1=l1_attack.name,
            l2=l2_attack.name,
            l3=l3_attack.name,
            description=l3_attack.description,
            transforms=[],
        )

        product = ProductInformation(
            name=product_db.name,
            type=product_db.type,
            platform=Platform(product_db.platform),
            description=product_db.description,
            use_cases=product_db.use_cases.get("use_cases", []),
        )

        deployment_context = DeploymentContext(
            product=product,
            name=context_db.name,
            description=context_db.description,
            industry=context_db.industry,
            environment=context_db.environment,
        )

        return Specification(
            agent=agent_config,
            risk=risk,
            attack=attack,
            turns=turns,
            type=(
                EnvironmentType.MULTI_TURN if turns > 1 else EnvironmentType.SINGLE_TURN
            ),
            context=deployment_context,
            prompt=prompt,
        )

    @staticmethod
    def from_eval(eval: Eval) -> Specification:
        """Build Specification from fully-loaded Eval object."""
        return SpecificationBuilder.build(
            l3_risk=eval.l3_risk,
            l3_attack=eval.l3_attack,
            rubric_db=eval.rubric,
            agent_cfg=eval.batch.config.agent_config,
            context_db=eval.batch.config.context,
            turns=eval.batch.config.turns,
            prompt=(
                eval.prompt.value
                if getattr(eval, "prompt", None) and eval.prompt.value
                else None
            ),
        )
