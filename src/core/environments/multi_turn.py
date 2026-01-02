"""
Multi-turn evaluation environment.
"""

from src.core.models.state import State, Turn
from src.core.models.specification import Specification
from src.core.environments.base import BaseEnvironment
from src.core.utils.logging import log_section
import logging

logger = logging.getLogger(__name__)


class MultiTurnEnv(BaseEnvironment):
    """Multi-turn adversarial evaluation environment."""

    async def execute(self, spec: Specification) -> State:
        """Execute multi-turn evaluation."""
        state = await self.setup()
        state.metadata["run_id"] = spec.id

        # Generate initial plan (if enabled)
        plan = await self.agent.plan()
        log_section(logger, "INFO", "INITIAL PLAN", plan)

        # Execute turns
        for turn_idx in range(1, spec.turns + 1):
            state.turn = turn_idx
            logger.info(f"TURN {turn_idx}/{spec.turns} STARTED")

            # Generate adversarial response
            xml, scratchpad, response = await self.agent.respond(turn_idx, spec.turns)

            log_section(logger, "INFO", f"SCRATCHPAD (Turn {turn_idx})", scratchpad)
            log_section(logger, "INFO", f"RESPONSE (Turn {turn_idx})", response)

            # Send to customer agent
            output = await self.adapter.interact(response)

            # Record completed turn (includes customer output)
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

            log_section(logger, "INFO", f"OUTPUT (Turn {turn_idx})", output)
            logger.info(f"TURN {turn_idx}/{spec.turns} COMPLETED")

            # Evaluate and update plan (skip on last turn)
            if turn_idx < spec.turns:
                updated_plan = await self.agent.update(output)
                log_section(
                    logger, "INFO", f"UPDATED PLAN (Turn {turn_idx + 1})", updated_plan
                )

        await self.cleanup()

        return state
