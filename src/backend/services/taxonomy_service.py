"""Service for taxonomy-related operations (risks, attacks, combinations)."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import ConfigAttack, ConfigRisk, L3Attack, L3Risk


class TaxonomyService:
    """Handles risk and attack taxonomy operations."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session

    async def get_leaf_risks(self, config_id: UUID) -> list[L3Risk]:
        """Get all leaf risks for a config."""
        result = await self.session.execute(
            select(L3Risk).join(ConfigRisk).filter(ConfigRisk.config_id == config_id)
        )
        leaf_risks = result.scalars().all()

        if not leaf_risks:
            raise ValueError(f"Config {config_id} has no leaf risks configured")
        return leaf_risks

    async def get_leaf_attacks(self, config_id: UUID) -> list[L3Attack]:
        """Get all attacks for a config."""
        result = await self.session.execute(
            select(L3Attack)
            .join(ConfigAttack)
            .filter(ConfigAttack.config_id == config_id)
        )
        leaf_attacks = result.scalars().all()

        if not leaf_attacks:
            raise ValueError(f"Config {config_id} has no leaf attacks configured")
        return leaf_attacks

    async def get_risk_attack_combinations(
        self, config_id: UUID
    ) -> tuple[list[UUID], list[UUID]]:
        """Get risk and attack IDs for a config."""
        leaf_risks = await self.get_leaf_risks(config_id)
        leaf_attacks = await self.get_leaf_attacks(config_id)
        return [risk.id for risk in leaf_risks], [attack.id for attack in leaf_attacks]
