"""Rubric API routes."""

from fastcrud import FilterConfig, crud_router

from src.database import get_async_session
from src.database.models import Rubric
from src.backend.schemas import RubricCreate, RubricRead, RubricUpdate

router = crud_router(
    session=get_async_session,
    model=Rubric,
    create_schema=RubricCreate,
    update_schema=RubricUpdate,
    select_schema=RubricRead,
    path="/rubrics",
    tags=["Rubrics"],
    filter_config=FilterConfig(is_deleted=False),
)
