"""
Single-turn evaluation environment.
"""

from src.core.models.state import State, Turn
from src.core.models.specification import Specification
from src.core.environments.base import BaseEnvironment
from src.core.utils.logging import log_section
import logging

logger = logging.getLogger(__name__)


class SingleTurnEnv(BaseEnvironment):
    """Single-turn evaluation environment."""

    async def execute(self, spec: Specification) -> State:
        """Execute single-turn evaluation."""
        state = await self.setup()
        state.metadata["eval_id"] = spec.id
        state.turn = 1

        logger.info("TURN 1/1 STARTED")

        # Generate initial plan (if enabled)
        plan = await self.agent.plan()
        if plan:
            log_section(logger, "INFO", "INITIAL PLAN", plan)

        # Generate single adversarial response
        xml, scratchpad, response = await self.agent.respond(1, 1)

        if scratchpad:
            log_section(logger, "INFO", "SCRATCHPAD (Turn 1)", scratchpad)

        log_section(logger, "INFO", "RESPONSE (Turn 1)", response)

        output = await self.adapter.interact(response)

        log_section(logger, "INFO", "OUTPUT (Turn 1)", output)

        if self.tracker:
            state = await self.tracker.update(state, scratchpad, output)

        turn = Turn(
            idx=state.turn,
            xml=xml,
            response=response,
            output=output,
            scratchpad=scratchpad,
            metadata=state.metadata.copy(),
        )
        state.history.append(turn)

        await self.emit(self.UPDATE, state)

        logger.info("TURN 1/1 COMPLETED")

        await self.cleanup()

        return state
