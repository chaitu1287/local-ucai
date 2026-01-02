"""Grade API routes."""

from fastcrud import FilterConfig, crud_router

from src.database import get_async_session
from src.database.models import Grade
from src.backend.schemas import GradeCreate, GradeRead, GradeUpdate

router = crud_router(
    session=get_async_session,
    model=Grade,
    create_schema=GradeCreate,
    update_schema=GradeUpdate,
    select_schema=GradeRead,
    path="/grades",
    tags=["Grades"],
    filter_config=FilterConfig(is_deleted=False),
)
