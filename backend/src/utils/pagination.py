from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Query

T = TypeVar('T')


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(20, ge=1, le=100, description="Number of items per page")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: Optional[str] = Field("asc", description="Sort order: asc or desc")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


def paginate_query(
    query: Query,
    page: int = 1,
    page_size: int = 20,
    sort_by: Optional[str] = None,
    sort_order: str = "asc"
) -> tuple[List, int]:
    """
    Paginate a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        page_size: Number of items per page
        sort_by: Field name to sort by
        sort_order: Sort order ('asc' or 'desc')
    
    Returns:
        Tuple of (items, total_count)
    """
    total = query.count()
    
    if sort_by and hasattr(query.column_descriptions[0]['type'], sort_by):
        model = query.column_descriptions[0]['type']
        sort_column = getattr(model, sort_by)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
    
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    
    return items, total


def create_paginated_response(
    items: List[T],
    total: int,
    page: int,
    page_size: int
) -> dict:
    """
    Create a paginated response dictionary.
    
    Args:
        items: List of items for current page
        total: Total number of items
        page: Current page number
        page_size: Number of items per page
    
    Returns:
        Dictionary with pagination metadata
    """
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }
