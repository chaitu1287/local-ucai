"""Product API routes."""

from fastcrud import FilterConfig, crud_router

from src.database import get_async_session
from src.database.models import Product
from src.backend.schemas import ProductCreate, ProductRead, ProductUpdate

router = crud_router(
    session=get_async_session,
    model=Product,
    create_schema=ProductCreate,
    update_schema=ProductUpdate,
    select_schema=ProductRead,
    path="/products",
    tags=["Products"],
    filter_config=FilterConfig(is_deleted=False),
)
