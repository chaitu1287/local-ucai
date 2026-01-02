"""AIUC Core - Evaluation framework for AI agent safety testing."""

from src.core.models import (
    State,
    Turn,
    Specification,
    Platform,
    EnvironmentType,
    Grade,
)
from src.core.environments import BaseEnvironment, SingleTurnEnv, MultiTurnEnv
from src.core.adapters import AdapterFactory
from src.core.agent import RedTeamer
from src.core.tracking import Tracker


def load_environment(
    spec: Specification,
    agent: RedTeamer,
    use_tracker: bool = False,
) -> BaseEnvironment:
    """Load the environment based on the specification.

    Factory function that assembles all components needed for an evaluation environment.
    """
    adapter = AdapterFactory.create(spec.context.product.platform)
    grader = None  # TODO: Change later
    tracker = Tracker() if use_tracker else None

    match spec.type:
        case EnvironmentType.MULTI_TURN:
            env = MultiTurnEnv(
                adapter=adapter, agent=agent, tracker=tracker, grader=grader
            )
        case EnvironmentType.SINGLE_TURN:
            env = SingleTurnEnv(
                adapter=adapter, agent=agent, tracker=tracker, grader=grader
            )
        case _:
            raise ValueError(f"Unknown environment type: {spec.type}")

    return env


__all__ = [
    # Entry point
    "load_environment",
    # Models
    "State",
    "Turn",
    "Specification",
    "Platform",
    "EnvironmentType",
    "Grade",
    # Environments
    "BaseEnvironment",
    "SingleTurnEnv",
    "MultiTurnEnv",
]
