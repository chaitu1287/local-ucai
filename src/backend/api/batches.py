"""Batch API routes."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from fastcrud import FilterConfig, crud_router
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.database.models import Batch, Config
from src.backend.schemas import (
    BatchCreate,
    BatchRead,
    BatchStartRequest,
    BatchStartResponse,
    BatchUpdate,
)
from src.backend.services import BatchService, EvalService, TaxonomyService
from src.backend.workers.eval_workers import run_eval

logger = logging.getLogger(__name__)

router = APIRouter()

batch_router = crud_router(
    session=get_async_session,
    model=Batch,
    create_schema=BatchCreate,
    update_schema=BatchUpdate,
    select_schema=BatchRead,
    path="/batches",
    tags=["Batches"],
    filter_config=FilterConfig(is_deleted=False, preview=False),
)

router.include_router(batch_router)


@router.post("/batches/start", response_model=BatchStartResponse, tags=["Batches"])
async def start_batch(
    request: BatchStartRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """Create batch and evals, commit to DB, then spawn Modal workers."""
    try:
        result = await session.execute(
            select(Config).filter(Config.id == request.config_id, ~Config.is_deleted)
        )
        config = result.scalar_one_or_none()
        if not config:
            raise HTTPException(
                status_code=404, detail=f"Config {request.config_id} not found"
            )

        batch_service = BatchService(session)
        batch = await batch_service.create_batch(config.id, request.parent_batch_id)
        logger.info(f"Created batch {batch.id}")

        taxonomy_service = TaxonomyService(session)
        risk_ids, attack_ids = await taxonomy_service.get_risk_attack_combinations(
            config.id
        )
        logger.info(f"Retrieved {len(risk_ids)} risks and {len(attack_ids)} attacks")

        eval_service = EvalService(session)
        eval_ids = await eval_service.initialise_records(
            batch.id,
            risk_ids,
            attack_ids,
            config.prompt_template_id,
            None,
        )
        logger.info(f"Initialised {len(eval_ids)} eval records")

        await session.commit()
        logger.info(f"Committed batch {batch.id} to database")

        for eval_id in eval_ids:
            run_eval.spawn(str(eval_id))

        logger.info(f"Spawned {len(eval_ids)} workers for batch {batch.id}")
        return BatchStartResponse(
            batch_id=batch.id,
            eval_count=len(eval_ids),
            status=batch.status,
            created_at=batch.created_at,
        )

    except ValueError as e:
        logger.error(f"Batch creation failed: {e}")
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    except HTTPException as e:
        await session.rollback()
        raise e

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
