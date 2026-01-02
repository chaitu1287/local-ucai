"""Service for batch execution and management."""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.enums import BatchStatus
from src.database.models import Batch

logger = logging.getLogger(__name__)


class BatchService:
    """Handles batch creation and orchestration."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_batch(
        self, config_id: UUID, parent_batch_id: UUID | None = None
    ) -> Batch:
        """Create a new batch record."""
        batch = Batch(
            config_id=config_id,
            parent_batch_id=parent_batch_id,
            status=BatchStatus.RUNNING,
        )
        self.session.add(batch)
        await self.session.flush()
        return batch
