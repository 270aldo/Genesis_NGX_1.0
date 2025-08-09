"""
Pagination System for GENESIS API
=================================

Provides consistent pagination across all endpoints with support for:
- Offset-based pagination
- Cursor-based pagination
- Page number pagination
- Configurable page sizes
- Total count calculation
"""

from typing import TypeVar, Generic, List, Optional, Dict, Any, Union, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
import base64
import json
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, validator
from fastapi import Query, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from core.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class PaginationType(str, Enum):
    """Types of pagination supported."""
    OFFSET = "offset"      # Traditional limit/offset
    CURSOR = "cursor"      # Cursor-based for large datasets
    PAGE = "page"          # Page number based


@dataclass
class PaginationParams:
    """Common pagination parameters."""
    limit: int = 20
    offset: int = 0
    cursor: Optional[str] = None
    page: Optional[int] = None
    order_by: str = "created_at"
    order_dir: str = "desc"
    include_total: bool = True
    
    def __post_init__(self):
        """Validate and adjust parameters."""
        # Ensure reasonable limits
        self.limit = min(max(1, self.limit), 100)
        self.offset = max(0, self.offset)
        
        # Convert page to offset if provided
        if self.page is not None:
            self.page = max(1, self.page)
            self.offset = (self.page - 1) * self.limit
        
        # Validate order direction
        self.order_dir = self.order_dir.lower()
        if self.order_dir not in ["asc", "desc"]:
            self.order_dir = "desc"


class PaginationMeta(BaseModel):
    """Metadata about pagination."""
    total: Optional[int] = Field(None, description="Total number of items")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Number of items skipped")
    page: Optional[int] = Field(None, description="Current page number")
    pages: Optional[int] = Field(None, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more items")
    has_prev: bool = Field(..., description="Whether there are previous items")
    next_cursor: Optional[str] = Field(None, description="Cursor for next page")
    prev_cursor: Optional[str] = Field(None, description="Cursor for previous page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: List[T] = Field(..., description="List of items")
    meta: PaginationMeta = Field(..., description="Pagination metadata")
    
    class Config:
        # Allow generic types
        arbitrary_types_allowed = True


class CursorData(BaseModel):
    """Data encoded in pagination cursor."""
    offset: int
    timestamp: datetime
    order_field: str
    order_value: Any
    
    def encode(self) -> str:
        """Encode cursor data to base64 string."""
        data = self.dict()
        # Convert datetime to ISO format
        if isinstance(data.get("timestamp"), datetime):
            data["timestamp"] = data["timestamp"].isoformat()
        
        json_str = json.dumps(data, sort_keys=True)
        return base64.urlsafe_b64encode(json_str.encode()).decode()
    
    @classmethod
    def decode(cls, cursor: str) -> "CursorData":
        """Decode cursor from base64 string."""
        try:
            json_str = base64.urlsafe_b64decode(cursor.encode()).decode()
            data = json.loads(json_str)
            # Convert ISO format back to datetime
            if "timestamp" in data:
                data["timestamp"] = datetime.fromisoformat(data["timestamp"])
            return cls(**data)
        except Exception as e:
            logger.warning(f"Invalid cursor: {e}")
            raise ValueError("Invalid pagination cursor")


class Paginator(ABC):
    """Abstract base class for pagination strategies."""
    
    @abstractmethod
    async def paginate(
        self,
        query: Any,
        params: PaginationParams
    ) -> PaginatedResponse:
        """Apply pagination to query and return results."""
        pass


class SQLAlchemyPaginator(Paginator):
    """Paginator for SQLAlchemy queries."""
    
    def __init__(self, session: AsyncSession, model_class: type):
        self.session = session
        self.model_class = model_class
    
    async def paginate(
        self,
        query: Select,
        params: PaginationParams
    ) -> PaginatedResponse:
        """Paginate SQLAlchemy query."""
        # Apply ordering
        if hasattr(self.model_class, params.order_by):
            order_field = getattr(self.model_class, params.order_by)
            if params.order_dir == "desc":
                query = query.order_by(order_field.desc())
            else:
                query = query.order_by(order_field.asc())
        
        # Get total count if requested
        total = None
        if params.include_total:
            count_query = select(func.count()).select_from(
                query.subquery()
            )
            result = await self.session.execute(count_query)
            total = result.scalar()
        
        # Apply pagination
        query = query.limit(params.limit).offset(params.offset)
        
        # Execute query
        result = await self.session.execute(query)
        items = result.scalars().all()
        
        # Calculate metadata
        has_next = len(items) == params.limit
        has_prev = params.offset > 0
        
        pages = None
        if total is not None:
            pages = (total + params.limit - 1) // params.limit
        
        current_page = None
        if params.page is not None:
            current_page = params.page
        elif pages:
            current_page = (params.offset // params.limit) + 1
        
        # Create cursors for next/prev
        next_cursor = None
        prev_cursor = None
        
        if has_next and items:
            last_item = items[-1]
            cursor_data = CursorData(
                offset=params.offset + params.limit,
                timestamp=datetime.utcnow(),
                order_field=params.order_by,
                order_value=getattr(last_item, params.order_by, None)
            )
            next_cursor = cursor_data.encode()
        
        if has_prev:
            cursor_data = CursorData(
                offset=max(0, params.offset - params.limit),
                timestamp=datetime.utcnow(),
                order_field=params.order_by,
                order_value=None
            )
            prev_cursor = cursor_data.encode()
        
        # Build response
        meta = PaginationMeta(
            total=total,
            limit=params.limit,
            offset=params.offset,
            page=current_page,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev,
            next_cursor=next_cursor,
            prev_cursor=prev_cursor
        )
        
        return PaginatedResponse(items=items, meta=meta)


class ListPaginator(Paginator):
    """Paginator for in-memory lists."""
    
    async def paginate(
        self,
        items: List[T],
        params: PaginationParams
    ) -> PaginatedResponse[T]:
        """Paginate a list of items."""
        total = len(items)
        
        # Apply sorting if items have the order field
        if items and hasattr(items[0], params.order_by):
            reverse = params.order_dir == "desc"
            items = sorted(
                items,
                key=lambda x: getattr(x, params.order_by, 0),
                reverse=reverse
            )
        
        # Apply pagination
        start = params.offset
        end = start + params.limit
        paginated_items = items[start:end]
        
        # Calculate metadata
        has_next = end < total
        has_prev = start > 0
        pages = (total + params.limit - 1) // params.limit
        current_page = (params.offset // params.limit) + 1
        
        # Create cursors
        next_cursor = None
        prev_cursor = None
        
        if has_next:
            cursor_data = CursorData(
                offset=end,
                timestamp=datetime.utcnow(),
                order_field=params.order_by,
                order_value=None
            )
            next_cursor = cursor_data.encode()
        
        if has_prev:
            cursor_data = CursorData(
                offset=max(0, start - params.limit),
                timestamp=datetime.utcnow(),
                order_field=params.order_by,
                order_value=None
            )
            prev_cursor = cursor_data.encode()
        
        # Build response
        meta = PaginationMeta(
            total=total,
            limit=params.limit,
            offset=params.offset,
            page=current_page,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev,
            next_cursor=next_cursor,
            prev_cursor=prev_cursor
        )
        
        return PaginatedResponse(items=paginated_items, meta=meta)


def paginate_params(
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    page: Optional[int] = Query(None, ge=1, description="Page number (alternative to offset)"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    order_by: str = Query("created_at", description="Field to order by"),
    order_dir: str = Query("desc", pattern="^(asc|desc)$", description="Order direction"),
    include_total: bool = Query(True, description="Include total count in response")
) -> PaginationParams:
    """
    FastAPI dependency for pagination parameters.
    
    Usage:
        @router.get("/items")
        async def get_items(pagination: PaginationParams = Depends(paginate_params)):
            ...
    """
    # Handle cursor-based pagination
    if cursor:
        try:
            cursor_data = CursorData.decode(cursor)
            offset = cursor_data.offset
            order_by = cursor_data.order_field
        except ValueError:
            pass  # Fall back to regular params
    
    return PaginationParams(
        limit=limit,
        offset=offset,
        page=page,
        cursor=cursor,
        order_by=order_by,
        order_dir=order_dir,
        include_total=include_total
    )


class PaginationMixin:
    """
    Mixin for adding pagination to FastAPI routers.
    
    Usage:
        class ItemRouter(PaginationMixin):
            async def get_items(self, pagination: PaginationParams = Depends(paginate_params)):
                items = await fetch_items()
                return await self.paginate_list(items, pagination)
    """
    
    async def paginate_list(
        self,
        items: List[T],
        params: PaginationParams
    ) -> PaginatedResponse[T]:
        """Paginate a list of items."""
        paginator = ListPaginator()
        return await paginator.paginate(items, params)
    
    async def paginate_query(
        self,
        session: AsyncSession,
        query: Select,
        model_class: type,
        params: PaginationParams
    ) -> PaginatedResponse:
        """Paginate a SQLAlchemy query."""
        paginator = SQLAlchemyPaginator(session, model_class)
        return await paginator.paginate(query, params)


def add_pagination_headers(response: PaginatedResponse, request: Request) -> Dict[str, str]:
    """
    Add pagination headers to HTTP response.
    
    Headers:
    - X-Total-Count: Total number of items
    - X-Page-Count: Total number of pages
    - X-Current-Page: Current page number
    - X-Per-Page: Items per page
    - Link: RFC 5988 compliant link headers
    """
    headers = {
        "X-Per-Page": str(response.meta.limit),
        "X-Has-Next": str(response.meta.has_next).lower(),
        "X-Has-Prev": str(response.meta.has_prev).lower()
    }
    
    if response.meta.total is not None:
        headers["X-Total-Count"] = str(response.meta.total)
    
    if response.meta.pages is not None:
        headers["X-Page-Count"] = str(response.meta.pages)
    
    if response.meta.page is not None:
        headers["X-Current-Page"] = str(response.meta.page)
    
    # Build Link header
    links = []
    base_url = str(request.url).split("?")[0]
    
    if response.meta.next_cursor:
        links.append(f'<{base_url}?cursor={response.meta.next_cursor}>; rel="next"')
    
    if response.meta.prev_cursor:
        links.append(f'<{base_url}?cursor={response.meta.prev_cursor}>; rel="prev"')
    
    if response.meta.page and response.meta.pages:
        links.append(f'<{base_url}?page=1>; rel="first"')
        links.append(f'<{base_url}?page={response.meta.pages}>; rel="last"')
    
    if links:
        headers["Link"] = ", ".join(links)
    
    return headers


class PaginatedList(list, Generic[T]):
    """
    A list subclass that includes pagination metadata.
    
    Usage:
        items = PaginatedList([1, 2, 3], total=100, page=1, per_page=3)
        return {"items": items, "total": items.total}
    """
    
    def __init__(self, items: List[T], **meta):
        super().__init__(items)
        self.meta = PaginationMeta(**meta)
        self.total = meta.get("total")
        self.page = meta.get("page")
        self.per_page = meta.get("limit", 20)
        self.has_next = meta.get("has_next", False)
        self.has_prev = meta.get("has_prev", False)


# Helper functions for common use cases
async def paginate_supabase(
    table_name: str,
    params: PaginationParams,
    filters: Optional[Dict[str, Any]] = None,
    supabase_client: Any = None
) -> PaginatedResponse:
    """
    Paginate Supabase query results.
    
    Args:
        table_name: Name of the Supabase table
        params: Pagination parameters
        filters: Optional filters to apply
        supabase_client: Supabase client instance
    """
    from clients.supabase_client import supabase_client as default_client
    
    client = supabase_client or default_client
    query = client.table(table_name).select("*")
    
    # Apply filters
    if filters:
        for key, value in filters.items():
            query = query.eq(key, value)
    
    # Get total count if requested
    total = None
    if params.include_total:
        count_result = query.count()
        total = count_result.count if hasattr(count_result, 'count') else None
    
    # Apply ordering
    if params.order_dir == "desc":
        query = query.order(params.order_by, desc=True)
    else:
        query = query.order(params.order_by)
    
    # Apply pagination
    query = query.range(params.offset, params.offset + params.limit - 1)
    
    # Execute query
    result = query.execute()
    items = result.data if hasattr(result, 'data') else []
    
    # Calculate metadata
    has_next = len(items) == params.limit
    has_prev = params.offset > 0
    
    pages = None
    if total is not None:
        pages = (total + params.limit - 1) // params.limit
    
    current_page = (params.offset // params.limit) + 1 if pages else None
    
    # Build response
    meta = PaginationMeta(
        total=total,
        limit=params.limit,
        offset=params.offset,
        page=current_page,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
    )
    
    return PaginatedResponse(items=items, meta=meta)