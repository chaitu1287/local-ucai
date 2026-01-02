from abc import ABC, abstractmethod
from typing import Awaitable, Callable, Iterable

from src.core.models.state import State
from src.core.models.specification import Specification
from src.core.models.grade import Grade
from src.core.adapters.base import BaseAdapter
from src.core.agent.red_teamer import RedTeamer
from src.core.tracking.tracker import Tracker
from src.core.grading.grader import Grader
from src.core.environments.callbacks import CallbackRegistry, CallbackEvent
import logging

logger = logging.getLogger(__name__)


class BaseEnvironment(ABC):
    """Base environment for evaluation execution."""

    UPDATE = CallbackEvent.UPDATE

    def __init__(
        self,
        adapter: BaseAdapter,
        agent: RedTeamer,
        tracker: Tracker | None = None,
        grader: Grader | None = None,
    ):
        """Initialize environment with injected dependencies."""
        self.adapter = adapter
        self.agent = agent
        self.tracker = tracker
        self.grader = grader
        self.callbacks = CallbackRegistry()

    def on(
        self,
        event: CallbackEvent | Iterable[CallbackEvent],
        callback: Callable[[object], Awaitable[None]],
    ) -> None:
        """Register a callback for one or more events."""
        self.callbacks.on(event, callback)

    async def emit(self, event: CallbackEvent, payload: object) -> None:
        """Emit an event with the provided payload."""
        await self.callbacks.emit(event, payload)

    async def setup(self) -> State:
        """Set up initial state."""
        logger.info("Setting up environment")
        await self.adapter.setup()
        logger.debug("Environment setup complete")
        return State(turn=0, history=[], metadata={})

    @abstractmethod
    async def execute(self, spec: Specification) -> State:
        """Execute the evaluation."""
        pass

    async def preview(self, spec: Specification) -> dict:
        """Generate first message only for preview (no adapter interaction)."""
        logger.info("Generating first message for preview")

        # Generate plan if enabled
        plan = None
        if spec.agent.plan:
            plan = await self.agent.plan()
            logger.debug(f"Generated plan: {plan[:100] if plan else 'None'}...")

        # Generate first response
        xml, scratchpad, output = await self.agent.respond(1, spec.turns)

        return {
            "system_prompt": self.agent.system_prompt,
            "plan": plan,
            "first_message": output,
            "scratchpad": scratchpad,
            "xml": xml,
        }

    async def grade(self, state: State) -> Grade | None:
        """Grade the completed evaluation."""
        if self.grader:
            logger.info("Grading evaluation")
            grade = await self.grader.grade(state)
            if grade:
                logger.info(f"Grade result: {grade.severity}")
            return grade
        logger.debug("No grader configured, skipping grading")
        return None

    async def cleanup(self) -> None:
        """Clean up environment resources."""
        logger.info("Cleaning up environment")
        await self.adapter.close()
        logger.debug("Environment cleanup complete")
