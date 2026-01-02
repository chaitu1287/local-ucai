"""Service for eval record creation and management."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.backend.exceptions import EvalNotFoundException
from src.core import load_environment
from src.core.models.state import State
from src.core.agent.red_teamer import RedTeamer
from src.core.builders import SpecificationBuilder
from src.core.environments.callbacks import CallbackEvent
from src.database.config import get_async_session
from src.database.enums import EvalStatus
from src.database.models import (
    Batch,
    Config,
    Context,
    Conversation,
    Eval,
    L1Risk,
    L2Attack,
    L2Risk,
    L3Attack,
    L3Risk,
    Prompt,
)

logger = logging.getLogger(__name__)


class EvalService:
    """Async service for eval operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _state_update_callback(self, eval_obj: Eval):
        conversation_id = eval_obj.conversation_id

        async def _on_state_update(state: State):
            history = state.model_dump()["history"]

            if conversation_id:
                async for session in get_async_session():
                    await session.execute(
                        update(Conversation)
                        .where(Conversation.id == conversation_id)
                        .values(history=history)
                    )
                eval_obj.conversation.history = history
                return

            eval_obj.conversation.history = history
            await self.session.flush()

        return _on_state_update

    async def get_with_relationships(self, eval_id: UUID) -> Eval | None:
        """Get eval with all relationships eagerly loaded."""
        result = await self.session.execute(
            select(Eval)
            .where(Eval.id == eval_id)
            .options(
                joinedload(Eval.l3_risk)
                .joinedload(L3Risk.l2_risk)
                .joinedload(L2Risk.l1_risk),
                joinedload(Eval.l3_attack)
                .joinedload(L3Attack.l2_attack)
                .joinedload(L2Attack.l1_attack),
                joinedload(Eval.rubric),
                joinedload(Eval.batch)
                .joinedload(Batch.config)
                .joinedload(Config.agent_config),
                joinedload(Eval.batch)
                .joinedload(Batch.config)
                .joinedload(Config.prompt_template),
                joinedload(Eval.batch)
                .joinedload(Batch.config)
                .joinedload(Config.context)
                .joinedload(Context.product),
                joinedload(Eval.prompt),
                joinedload(Eval.conversation),
            )
        )
        return result.unique().scalar_one_or_none()

    async def initialise_records(
        self,
        batch_id: UUID,
        risk_ids: list[UUID],
        attack_ids: list[UUID],
        prompt_template_id: UUID,
        rubric_id: Optional[UUID] = None,
    ) -> list[UUID]:
        resolved_rubrics: dict[UUID, UUID] = {}

        if rubric_id is None:
            resolved_rubrics = await self._resolve_rubrics(risk_ids)

        eval_ids = []
        for risk_id in risk_ids:
            for attack_id in attack_ids:
                prompt = Prompt(template_id=prompt_template_id, value="")
                self.session.add(prompt)
                await self.session.flush()

                conversation = Conversation(history={})
                self.session.add(conversation)
                await self.session.flush()

                eval_obj = Eval(
                    batch_id=batch_id,
                    prompt_id=prompt.id,
                    conversation_id=conversation.id,
                    rubric_id=rubric_id or resolved_rubrics.get(risk_id),
                    l3_risk_id=risk_id,
                    l3_attack_id=attack_id,
                    status=EvalStatus.PENDING,
                )
                self.session.add(eval_obj)
                await self.session.flush()
                eval_ids.append(eval_obj.id)
        return eval_ids

    async def _resolve_rubrics(self, risk_ids: list[UUID]) -> dict[UUID, UUID]:
        """Resolve rubric for each L3 risk with L3 -> L2 -> L1 fallback."""
        result = await self.session.execute(
            select(L3Risk)
            .where(L3Risk.id.in_(risk_ids))
            .options(
                joinedload(L3Risk.rubric),
                joinedload(L3Risk.l2_risk).joinedload(L2Risk.rubric),
                joinedload(L3Risk.l2_risk)
                .joinedload(L2Risk.l1_risk)
                .joinedload(L1Risk.rubric),
            )
        )

        l3_risks = result.unique().scalars().all()
        rubric_map: dict[UUID, UUID] = {}

        resolved = None
        for l3_risk in l3_risks:
            resolved = (
                l3_risk.rubric.id
                if l3_risk.rubric
                else (
                    l3_risk.l2_risk.rubric.id
                    if l3_risk.l2_risk and l3_risk.l2_risk.rubric
                    else (
                        l3_risk.l2_risk.l1_risk.rubric.id
                        if l3_risk.l2_risk
                        and l3_risk.l2_risk.l1_risk
                        and l3_risk.l2_risk.l1_risk.rubric
                        else None
                    )
                )
            )

            if not resolved:
                raise ValueError(
                    f"No rubric configured for risk {l3_risk.id} or its parents"
                )

            rubric_map[l3_risk.id] = resolved

        missing = set(risk_ids) - set(rubric_map.keys())
        if missing:
            raise ValueError(f"Risks not found when resolving rubrics: {missing}")

        return rubric_map

    async def execute_eval(self, eval_id: UUID):
        """Execute eval asynchronously (no commit - caller controls transaction)."""
        eval_obj = await self.get_with_relationships(eval_id)
        if not eval_obj:
            raise EvalNotFoundException(eval_id)

        eval_obj.status = EvalStatus.RUNNING
        logger.info(f"Updated eval {eval_obj.id} status to {EvalStatus.RUNNING.value}")
        await self.session.flush()

        # Execute core logic
        spec = SpecificationBuilder.from_eval(eval_obj)
        agent = RedTeamer(spec)
        environment = load_environment(spec, agent)
        environment.on(CallbackEvent.UPDATE, self._state_update_callback(eval_obj))

        state = await environment.execute(spec)

        # Save results
        self.save_results(eval_obj, agent, state)

        logger.info(f"Eval {eval_obj.id} completed with {len(state.history)} messages")
        return state

    def save_results(self, eval_obj: Eval, agent: RedTeamer, state: State):
        eval_obj.prompt.value = agent.system_prompt
        eval_obj.conversation.history = state.model_dump()["history"]
        eval_obj.status = EvalStatus.COMPLETED
        logger.info(f"Saved results for eval {eval_obj.id}")
