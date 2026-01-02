"""Modal workers for eval execution."""

import logging
from datetime import datetime, timezone
from uuid import UUID

import modal

from src.backend.exceptions import EvalNotFoundException
from src.backend.schemas import GradeEvalResponse, RunEvalResponse
from src.backend.services.eval_service import EvalService
from src.database import get_db
from src.database.enums import EvalStatus
from src.database.models import Grade
from src.backend.modal import app, image

logger = logging.getLogger(__name__)


@app.function(
    image=image,
    timeout=1200,
    secrets=[modal.Secret.from_name("aiuc-secrets")],
    max_containers=10,
)
async def run_eval(eval_id: str) -> RunEvalResponse:
    """Execute eval asynchronously in Modal worker."""
    logger.info(f"Starting eval execution: {eval_id}")

    async with get_db().AsyncSessionLocal() as session:
        try:
            service = EvalService(session)
            state = await service.execute_eval(UUID(eval_id))

            eval_obj = await service.get_with_relationships(UUID(eval_id))
            await session.commit()

            logger.info(f"Eval {eval_id} completed with {len(state.history)} messages")
            return RunEvalResponse(
                success=True,
                eval_id=eval_id,
                timestamp=datetime.now(timezone.utc),
                status=eval_obj.status,
                risk_name=eval_obj.l3_risk.name if eval_obj.l3_risk else None,
                attack_name=eval_obj.l3_attack.name if eval_obj.l3_attack else None,
                conversation_id=str(eval_obj.conversation_id)
                if eval_obj.conversation_id
                else None,
            )

        except EvalNotFoundException as e:
            await session.rollback()
            logger.error(f"Eval not found: {e}")
            return RunEvalResponse(
                success=False,
                eval_id=eval_id,
                error=str(e),
                timestamp=datetime.now(timezone.utc),
                status=EvalStatus.FAILED,
            )

        except Exception as e:
            await session.rollback()
            logger.error(f"Eval {eval_id} execution failed: {e}", exc_info=True)
            return RunEvalResponse(
                success=False,
                eval_id=eval_id,
                error=str(e),
                timestamp=datetime.now(timezone.utc),
                status=EvalStatus.FAILED,
            )


@app.function(
    image=image,
    timeout=600,
    secrets=[modal.Secret.from_name("aiuc-secrets")],
    max_containers=10,
)
async def grade(eval_id: str) -> GradeEvalResponse:
    """Grade eval asynchronously in Modal worker."""
    logger.info(f"Starting grading for eval: {eval_id}")

    async with get_db().AsyncSessionLocal() as session:
        try:
            service = EvalService(session)
            eval_obj = await service.get_with_relationships(UUID(eval_id))

            if not eval_obj:
                raise EvalNotFoundException(eval_id)

            if eval_obj.status != EvalStatus.COMPLETED:
                await session.rollback()
                return GradeEvalResponse(
                    success=False,
                    eval_id=eval_id,
                    error=f"Cannot grade eval with status {eval_obj.status.value}",
                    timestamp=datetime.now(timezone.utc),
                )

            grade = Grade(
                eval_id=eval_obj.id,
                graded_at=datetime.now(timezone.utc),
                auto_severity=None,
                auto_justification="Placeholder - not implemented",
                human_severity=None,
                human_justification=None,
                user_id=None,
            )
            session.add(grade)
            eval_obj.status = EvalStatus.GRADED

            await session.commit()

            logger.info(f"Eval {eval_id} graded successfully")
            return GradeEvalResponse(
                success=True,
                eval_id=eval_id,
                timestamp=datetime.now(timezone.utc),
                severity=grade.auto_severity,
                justification=grade.auto_justification,
            )

        except EvalNotFoundException as e:
            await session.rollback()
            logger.error(f"Eval not found: {e}")
            return GradeEvalResponse(
                success=False,
                eval_id=eval_id,
                error=str(e),
                timestamp=datetime.now(timezone.utc),
            )

        except Exception as e:
            await session.rollback()
            logger.error(f"Grading failed for eval {eval_id}: {e}", exc_info=True)
            return GradeEvalResponse(
                success=False,
                eval_id=eval_id,
                error=str(e),
                timestamp=datetime.now(timezone.utc),
            )
