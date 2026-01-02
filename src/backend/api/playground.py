"""Playground API routes."""

import traceback
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.backend.schemas import (
    GeneratePromptRequest,
    GeneratePromptResponse,
    PlaygroundRunRequest,
    PlaygroundRunResponse,
    PlaygroundStatusResponse,
)
from src.backend.services.playground_service import PlaygroundService
from src.backend.workers.eval_workers import run_eval
from src.database import get_async_session
from src.database.enums import EvalStatus
from src.database.models import Eval, L2Attack, L2Risk, L3Attack, L3Risk

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/playground/generate-prompt",
    response_model=GeneratePromptResponse,
    tags=["Playground"],
)
async def generate_prompt(
    request: GeneratePromptRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """Generate a prompt from a template and context variables."""
    try:
        playground_service = PlaygroundService(session)
        prompt, variables = await playground_service.generate_prompt(
            prompt_template_id=request.prompt_template_id,
            template_content=request.template_content,
            l3_risk_id=request.l3_risk_id,
            l3_attack_id=request.l3_attack_id,
            context_id=request.context_id,
        )
        return GeneratePromptResponse(prompt=prompt, variables=variables)

    except ValueError as e:
        logger.error(f"Failed to generate prompt: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate prompt: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate prompt: {str(e)}"
        )


@router.post(
    "/playground/run", response_model=PlaygroundRunResponse, tags=["Playground"]
)
async def run_playground(
    request: PlaygroundRunRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """Create and execute a playground evaluation."""
    try:
        playground_service = PlaygroundService(session)

        eval_obj = await playground_service.create_playground_execution(
            l3_risk_id=request.l3_risk_id,
            l3_attack_id=request.l3_attack_id,
            agent_config_id=request.agent_config_id,
            context_id=request.context_id,
            prompt_template_id=request.prompt_template_id,
            template_content=request.template_content,
            rubric_id=request.rubric_id,
            turns=request.turns,
            prompt_text=request.prompt_text,
        )

        await session.commit()
        eval_id_str = str(eval_obj.id)
        run_eval.spawn(eval_id_str)

        return PlaygroundRunResponse(
            playground_id=eval_obj.id,
            eval_id=eval_obj.id,
            status=eval_obj.status,
            message=f"Playground run started for {request.turns} turns",
            execution_mode="async",
        )

    except ValueError as e:
        await session.rollback()
        logger.error(
            f"Failed to create playground run: {str(e)}\n{traceback.format_exc()}"
        )
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        await session.rollback()
        logger.error(
            f"Failed to create playground run: {str(e)}\n{traceback.format_exc()}"
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to create playground run: {str(e)}"
        )


@router.get(
    "/playground/{playground_id}",
    response_model=PlaygroundStatusResponse,
    tags=["Playground"],
)
async def get_playground_status(
    playground_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """Get playground execution status and results."""
    try:
        query = (
            select(Eval)
            .where(Eval.id == playground_id)
            .options(
                joinedload(Eval.l3_risk)
                .joinedload(L3Risk.l2_risk)
                .joinedload(L2Risk.l1_risk),
                joinedload(Eval.l3_attack)
                .joinedload(L3Attack.l2_attack)
                .joinedload(L2Attack.l1_attack),
                joinedload(Eval.prompt),
                joinedload(Eval.conversation),
                joinedload(Eval.grades),
            )
        )

        result = await session.execute(query)
        eval_obj = result.unique().scalar_one_or_none()

        if not eval_obj:
            raise HTTPException(status_code=404, detail="Playground run not found")

        response = PlaygroundStatusResponse(
            playground_id=eval_obj.id,
            eval_id=eval_obj.id,
            status=eval_obj.status,
            created_at=eval_obj.created_at,
            completed_at=eval_obj.updated_at
            if eval_obj.status in [EvalStatus.COMPLETED, EvalStatus.GRADED]
            else None,
        )

        if eval_obj.conversation:
            response.conversation = eval_obj.conversation.history

        if eval_obj.prompt:
            response.prompt = eval_obj.prompt.value

        if eval_obj.status == EvalStatus.GRADED and eval_obj.grades:
            response.grade = eval_obj.grades[0]

        if eval_obj.status == EvalStatus.FAILED:
            response.error = "Evaluation failed during execution"

        return response

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(
            f"Failed to get playground status for {playground_id}: {str(e)}\n{traceback.format_exc()}"
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to get playground status: {str(e)}"
        )
