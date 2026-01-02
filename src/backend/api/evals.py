"""Eval API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastcrud import crud_router
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.database import get_async_session
from src.database.models import (
    Batch,
    Config,
    Eval,
    L3Risk,
    L2Risk,
    L3Attack,
    L2Attack,
)
from src.backend.schemas import (
    EvalCreate,
    EvalListRead,
    EvalRead,
    EvalUpdate,
)

router = APIRouter()


# Custom GET list endpoint with minimal relationships
@router.get("/evals", response_model=list[EvalListRead], tags=["Evals"])
async def get_evals_list(
    db: AsyncSession = Depends(get_async_session),
    skip: int = 0,
    limit: int = 100,
    preview: bool = False,
):
    """Get list of evals with minimal relationships (risk, attack, grades only)."""
    query = (
        select(Eval)
        .join(Batch, Eval.batch_id == Batch.id)
        .join(Config, Batch.config_id == Config.id)
        .where(~Eval.is_deleted)
    )

    query = query.where(Config.preview == preview)

    query = (
        query.offset(skip)
        .limit(limit)
        .options(
            joinedload(Eval.l3_risk)
            .joinedload(L3Risk.l2_risk)
            .joinedload(L2Risk.l1_risk),
            joinedload(Eval.l3_attack)
            .joinedload(L3Attack.l2_attack)
            .joinedload(L2Attack.l1_attack),
            joinedload(Eval.grades),
        )
    )

    result = await db.execute(query)
    evals = result.unique().scalars().all()
    return evals


# Custom GET detail endpoint with full relationships
@router.get("/evals/{item_id}", response_model=EvalRead, tags=["Evals"])
async def get_eval_detail(
    item_id: UUID,
    db: AsyncSession = Depends(get_async_session),
):
    """Get an eval with all relationships loaded."""
    query = (
        select(Eval)
        .where(Eval.id == item_id, ~Eval.is_deleted)
        .options(
            joinedload(Eval.l3_risk)
            .joinedload(L3Risk.l2_risk)
            .joinedload(L2Risk.l1_risk),
            joinedload(Eval.l3_attack)
            .joinedload(L3Attack.l2_attack)
            .joinedload(L2Attack.l1_attack),
            joinedload(Eval.rubric),
            joinedload(Eval.prompt),
            joinedload(Eval.conversation),
            joinedload(Eval.grades),
        )
    )

    result = await db.execute(query)
    eval_obj = result.unique().scalar_one_or_none()

    if not eval_obj:
        raise HTTPException(status_code=404, detail="Eval not found")

    return eval_obj


# Auto-generated CRUD endpoints (excluding GET endpoints)
eval_crud = crud_router(
    session=get_async_session,
    model=Eval,
    create_schema=EvalCreate,
    update_schema=EvalUpdate,
    select_schema=EvalRead,
    path="/evals",
    tags=["Evals"],
    deleted_methods=["read", "read_multi"],
)

router.include_router(eval_crud)
