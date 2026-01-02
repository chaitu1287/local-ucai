from src.core.models.specification import Platform
from src.core.adapters.base import BaseAdapter
from src.core.adapters.intercom import IntercomAdapter
from src.core.adapters.test import TestAdapter


class AdapterFactory:
    """Factory for creating customer platform adapters."""

    @staticmethod
    def create(platform: Platform) -> BaseAdapter:
        """Create an adapter for the specified platform."""
        match platform:
            case Platform.TEST:
                return TestAdapter()
            case Platform.INTERCOM:
                return IntercomAdapter()
            case _:
                raise NotImplementedError(
                    f"Adapter for platform {platform} not implemented"
                )
