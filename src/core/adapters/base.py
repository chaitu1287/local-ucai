from abc import ABC, abstractmethod
from httpx import AsyncClient


class BaseAdapter(ABC):
    """
    Abstract base class for customer platform adapters.

    API Interface:
    - setup(): Initialise connection and authenticate
    - interact(): Interact with the agent
    - close(): Close the connection
    """

    def __init__(self):
        self.client: AsyncClient | None = None

    @abstractmethod
    async def setup(self) -> None:
        """Initialize connection and authenticate with the platform."""
        pass

    @abstractmethod
    async def interact(self, message: str) -> str:
        """Send a message to the agent and return the response."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the connection and clean up resources."""
        pass
