"""AgentConfig API routes."""

from fastcrud import FilterConfig, crud_router

from src.database import get_async_session
from src.database.models import AgentConfig
from src.backend.schemas import (
    AgentConfigCreate,
    AgentConfigRead,
    AgentConfigUpdate,
)


router = crud_router(
    session=get_async_session,
    model=AgentConfig,
    create_schema=AgentConfigCreate,
    update_schema=AgentConfigUpdate,
    select_schema=AgentConfigRead,
    path="/agent-configs",
    tags=["Agent Configs"],
    filter_config=FilterConfig(is_deleted=False),
)
