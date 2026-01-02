"""Risk taxonomy API routes."""

from fastapi import APIRouter
from fastcrud import FilterConfig, crud_router

from src.database import get_async_session
from src.database.models import L1Risk, L2Risk, L3Risk
from src.backend.schemas import (
    L1RiskCreate,
    L1RiskRead,
    L1RiskUpdate,
    L2RiskCreate,
    L2RiskRead,
    L2RiskUpdate,
    L3RiskCreate,
    L3RiskRead,
    L3RiskUpdate,
)

router = APIRouter()

# Auto-generated CRUD endpoints for L1Risk
l1_risk_router = crud_router(
    session=get_async_session,
    model=L1Risk,
    create_schema=L1RiskCreate,
    update_schema=L1RiskUpdate,
    select_schema=L1RiskRead,
    path="/l1-risks",
    tags=["L1 Risks"],
    filter_config=FilterConfig(is_deleted=False),
)

# Auto-generated CRUD endpoints for L2Risk
l2_risk_router = crud_router(
    session=get_async_session,
    model=L2Risk,
    create_schema=L2RiskCreate,
    update_schema=L2RiskUpdate,
    select_schema=L2RiskRead,
    path="/l2-risks",
    tags=["L2 Risks"],
    filter_config=FilterConfig(is_deleted=False),
)

# Auto-generated CRUD endpoints for L3Risk
l3_risk_router = crud_router(
    session=get_async_session,
    model=L3Risk,
    create_schema=L3RiskCreate,
    update_schema=L3RiskUpdate,
    select_schema=L3RiskRead,
    path="/l3-risks",
    tags=["L3 Risks"],
    filter_config=FilterConfig(is_deleted=False),
)

# Include all risk routers
router.include_router(l1_risk_router)
router.include_router(l2_risk_router)
router.include_router(l3_risk_router)
