"""Attack taxonomy API routes."""

from fastapi import APIRouter
from fastcrud import FilterConfig, crud_router

from src.database import get_async_session
from src.database.models import L1Attack, L2Attack, L3Attack
from src.backend.schemas import (
    L1AttackCreate,
    L1AttackRead,
    L1AttackUpdate,
    L2AttackCreate,
    L2AttackRead,
    L2AttackUpdate,
    L3AttackCreate,
    L3AttackRead,
    L3AttackUpdate,
)

router = APIRouter()

l1_attack_router = crud_router(
    session=get_async_session,
    model=L1Attack,
    create_schema=L1AttackCreate,
    update_schema=L1AttackUpdate,
    select_schema=L1AttackRead,
    path="/l1-attacks",
    tags=["L1 Attacks"],
    filter_config=FilterConfig(is_deleted=False),
)

l2_attack_router = crud_router(
    session=get_async_session,
    model=L2Attack,
    create_schema=L2AttackCreate,
    update_schema=L2AttackUpdate,
    select_schema=L2AttackRead,
    path="/l2-attacks",
    tags=["L2 Attacks"],
    filter_config=FilterConfig(is_deleted=False),
)

l3_attack_router = crud_router(
    session=get_async_session,
    model=L3Attack,
    create_schema=L3AttackCreate,
    update_schema=L3AttackUpdate,
    select_schema=L3AttackRead,
    path="/l3-attacks",
    tags=["L3 Attacks"],
    filter_config=FilterConfig(is_deleted=False),
)

router.include_router(l1_attack_router)
router.include_router(l2_attack_router)
router.include_router(l3_attack_router)
