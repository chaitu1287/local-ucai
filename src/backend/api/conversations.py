"""Conversation API routes."""

from fastcrud import FilterConfig, crud_router

from src.database import get_async_session
from src.database.models import Conversation
from src.backend.schemas import ConversationCreate, ConversationRead, ConversationUpdate

router = crud_router(
    session=get_async_session,
    model=Conversation,
    create_schema=ConversationCreate,
    update_schema=ConversationUpdate,
    select_schema=ConversationRead,
    path="/conversations",
    tags=["Conversations"],
    filter_config=FilterConfig(is_deleted=False),
)
