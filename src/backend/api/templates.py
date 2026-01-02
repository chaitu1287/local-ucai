"""PromptTemplate API routes."""

from fastapi import APIRouter, Depends
from fastcrud import FilterConfig, crud_router
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.database.models import PromptTemplate
from src.backend.schemas import (
    PromptTemplateCreate,
    PromptTemplateRead,
    PromptTemplateUpdate,
)

router = APIRouter()


@router.get(
    "/templates/live",
    response_model=list[PromptTemplateRead],
    tags=["Prompt Templates"],
)
async def list_live_templates(session: AsyncSession = Depends(get_async_session)):
    """Get all live (non-preview) templates."""
    query = select(PromptTemplate).where(
        ~PromptTemplate.is_deleted, ~PromptTemplate.preview
    )
    result = await session.execute(query)
    return result.scalars().all()


@router.get(
    "/templates/preview",
    response_model=list[PromptTemplateRead],
    tags=["Prompt Templates"],
)
async def list_preview_templates(session: AsyncSession = Depends(get_async_session)):
    """Get all preview (playground) templates."""
    query = select(PromptTemplate).where(
        ~PromptTemplate.is_deleted, PromptTemplate.preview
    )
    result = await session.execute(query)
    return result.scalars().all()


templates_router = crud_router(
    session=get_async_session,
    model=PromptTemplate,
    create_schema=PromptTemplateCreate,
    update_schema=PromptTemplateUpdate,
    select_schema=PromptTemplateRead,
    path="/templates",
    tags=["Prompt Templates"],
    filter_config=FilterConfig(is_deleted=False),
)

router.include_router(templates_router)
