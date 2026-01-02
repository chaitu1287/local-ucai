"""Context API routes."""

from fastcrud import FilterConfig, crud_router

from src.database import get_async_session
from src.database.models import Context
from src.backend.schemas import ContextCreate, ContextRead, ContextUpdate

router = crud_router(
    session=get_async_session,
    model=Context,
    create_schema=ContextCreate,
    update_schema=ContextUpdate,
    select_schema=ContextRead,
    path="/contexts",
    tags=["Contexts"],
    filter_config=FilterConfig(is_deleted=False),
)
