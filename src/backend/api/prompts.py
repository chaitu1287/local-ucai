"""Prompt API routes."""

from fastcrud import FilterConfig, crud_router

from src.database import get_async_session
from src.database.models import Prompt
from src.backend.schemas import PromptCreate, PromptRead, PromptUpdate

router = crud_router(
    session=get_async_session,
    model=Prompt,
    create_schema=PromptCreate,
    update_schema=PromptUpdate,
    select_schema=PromptRead,
    path="/prompts",
    tags=["Prompts"],
    filter_config=FilterConfig(is_deleted=False),
)
