"""Config API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastcrud import FilterConfig, crud_router
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_async_session
from src.database.models import (
    Config,
    ConfigAttack,
    ConfigRisk,
    Context,
    L2Attack,
    L3Attack,
    L2Risk,
    L3Risk,
)
from src.backend.schemas import (
    ConfigAttackCreate,
    ConfigAttackRead,
    ConfigCreate,
    ConfigRead,
    ConfigRiskCreate,
    ConfigRiskRead,
    ConfigUpdate,
)


router = APIRouter()


# Override GET endpoint to include relationships BEFORE including auto-generated routes
@router.get("/configs/{item_id}", response_model=ConfigRead, tags=["Configs"])
async def get_config_with_relationships(
    item_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """Get a config with all relationships loaded."""
    query = (
        select(Config)
        .where(Config.id == item_id, ~Config.is_deleted)
        .options(
            selectinload(Config.prompt_template),
            selectinload(Config.agent_config),
            selectinload(Config.context).selectinload(Context.product),
            selectinload(Config.config_risks)
            .selectinload(ConfigRisk.l3_risk)
            .selectinload(L3Risk.l2_risk)
            .selectinload(L2Risk.l1_risk),
            selectinload(Config.config_attacks)
            .selectinload(ConfigAttack.l3_attack)
            .selectinload(L3Attack.l2_attack)
            .selectinload(L2Attack.l1_attack),
        )
    )

    result = await db.execute(query)
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="Config not found")

    return config


# Auto-generated CRUD endpoints for Config
config_router = crud_router(
    session=get_async_session,
    model=Config,
    create_schema=ConfigCreate,
    update_schema=ConfigUpdate,
    select_schema=ConfigRead,
    path="/configs",
    tags=["Configs"],
    # Exclude get endpoint. Use custom endpoint above instead.
    deleted_methods=["read"],
    filter_config=FilterConfig(is_deleted=False, preview=False),
)

# Auto-generated CRUD endpoints for ConfigRisk junction table
config_risk_router = crud_router(
    session=get_async_session,
    model=ConfigRisk,
    create_schema=ConfigRiskCreate,
    update_schema=None,
    select_schema=ConfigRiskRead,
    path="/config-risks",
    tags=["Configs"],
    filter_config=FilterConfig(is_deleted=False),
)

# Auto-generated CRUD endpoints for ConfigAttack junction table
config_attack_router = crud_router(
    session=get_async_session,
    model=ConfigAttack,
    create_schema=ConfigAttackCreate,
    update_schema=None,
    select_schema=ConfigAttackRead,
    path="/config-attacks",
    tags=["Configs"],
    filter_config=FilterConfig(is_deleted=False),
)

# Include all config routers
router.include_router(config_router)
router.include_router(config_risk_router)
router.include_router(config_attack_router)
