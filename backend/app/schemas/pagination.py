"""
Esquemas de paginación reutilizables para la API.

Este módulo proporciona esquemas Pydantic para implementar
paginación consistente en todos los endpoints de lista.
"""

from typing import TypeVar, Generic, List, Optional, Any, Dict
from pydantic import BaseModel, Field, validator
from math import ceil

# Type variable para items genéricos
T = TypeVar('T')


class PaginationParams(BaseModel):
    """Parámetros de paginación para requests."""
    
    page: int = Field(default=1, ge=1, description="Número de página (empieza en 1)")
    page_size: int = Field(
        default=20, 
        ge=1, 
        le=100, 
        description="Cantidad de items por página"
    )
    sort_by: Optional[str] = Field(
        default=None, 
        description="Campo por el cual ordenar"
    )
    sort_order: Optional[str] = Field(
        default="asc", 
        regex="^(asc|desc)$",
        description="Orden de clasificación: 'asc' o 'desc'"
    )
    
    @validator('page')
    def validate_page(cls, v):
        """Validar que la página sea positiva."""
        if v < 1:
            raise ValueError("La página debe ser mayor o igual a 1")
        return v
    
    @validator('page_size')
    def validate_page_size(cls, v):
        """Validar el tamaño de página."""
        if v < 1:
            raise ValueError("El tamaño de página debe ser al menos 1")
        if v > 100:
            raise ValueError("El tamaño de página no puede exceder 100")
        return v
    
    @property
    def offset(self) -> int:
        """Calcular el offset para la consulta."""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Obtener el límite para la consulta."""
        return self.page_size


class PaginationMetadata(BaseModel):
    """Metadata de paginación para responses."""
    
    page: int = Field(description="Página actual")
    page_size: int = Field(description="Tamaño de página")
    total_items: int = Field(description="Total de items")
    total_pages: int = Field(description="Total de páginas")
    has_next: bool = Field(description="Si hay página siguiente")
    has_previous: bool = Field(description="Si hay página anterior")
    
    @classmethod
    def from_params(
        cls, 
        params: PaginationParams, 
        total_items: int
    ) -> "PaginationMetadata":
        """
        Crear metadata desde parámetros y total de items.
        
        Args:
            params: Parámetros de paginación
            total_items: Total de items en la colección
            
        Returns:
            PaginationMetadata con los valores calculados
        """
        total_pages = ceil(total_items / params.page_size) if total_items > 0 else 0
        
        return cls(
            page=params.page,
            page_size=params.page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=params.page < total_pages,
            has_previous=params.page > 1
        )


class PaginatedResponse(BaseModel, Generic[T]):
    """Respuesta paginada genérica."""
    
    items: List[T] = Field(description="Lista de items")
    metadata: PaginationMetadata = Field(description="Metadata de paginación")
    links: Optional[Dict[str, Optional[str]]] = Field(
        default=None,
        description="Enlaces de navegación"
    )
    
    class Config:
        """Configuración del modelo."""
        schema_extra = {
            "example": {
                "items": ["item1", "item2"],
                "metadata": {
                    "page": 1,
                    "page_size": 20,
                    "total_items": 100,
                    "total_pages": 5,
                    "has_next": True,
                    "has_previous": False
                },
                "links": {
                    "self": "/api/v1/items?page=1&page_size=20",
                    "next": "/api/v1/items?page=2&page_size=20",
                    "previous": None,
                    "first": "/api/v1/items?page=1&page_size=20",
                    "last": "/api/v1/items?page=5&page_size=20"
                }
            }
        }
    
    @classmethod
    def create(
        cls,
        items: List[T],
        params: PaginationParams,
        total_items: int,
        base_url: str
    ) -> "PaginatedResponse[T]":
        """
        Crear una respuesta paginada.
        
        Args:
            items: Lista de items para la página actual
            params: Parámetros de paginación usados
            total_items: Total de items en la colección
            base_url: URL base para generar links
            
        Returns:
            PaginatedResponse con items, metadata y links
        """
        metadata = PaginationMetadata.from_params(params, total_items)
        
        # Generar links de navegación
        links = cls._generate_links(params, metadata, base_url)
        
        return cls(
            items=items,
            metadata=metadata,
            links=links
        )
    
    @staticmethod
    def _generate_links(
        params: PaginationParams,
        metadata: PaginationMetadata,
        base_url: str
    ) -> Dict[str, Optional[str]]:
        """Generar links de navegación."""
        def build_url(page: int) -> str:
            query_params = [
                f"page={page}",
                f"page_size={params.page_size}"
            ]
            if params.sort_by:
                query_params.append(f"sort_by={params.sort_by}")
            if params.sort_order:
                query_params.append(f"sort_order={params.sort_order}")
            
            return f"{base_url}?{'&'.join(query_params)}"
        
        links = {
            "self": build_url(params.page),
            "first": build_url(1) if metadata.total_pages > 0 else None,
            "last": build_url(metadata.total_pages) if metadata.total_pages > 0 else None,
            "next": build_url(params.page + 1) if metadata.has_next else None,
            "previous": build_url(params.page - 1) if metadata.has_previous else None
        }
        
        return links


class CursorPaginationParams(BaseModel):
    """Parámetros para paginación basada en cursor."""
    
    cursor: Optional[str] = Field(
        default=None,
        description="Cursor para la siguiente página"
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Cantidad de items a retornar"
    )
    direction: Optional[str] = Field(
        default="next",
        regex="^(next|previous)$",
        description="Dirección de paginación"
    )


class CursorPaginatedResponse(BaseModel, Generic[T]):
    """Respuesta paginada con cursor."""
    
    items: List[T] = Field(description="Lista de items")
    next_cursor: Optional[str] = Field(
        default=None,
        description="Cursor para la siguiente página"
    )
    previous_cursor: Optional[str] = Field(
        default=None,
        description="Cursor para la página anterior"
    )
    has_more: bool = Field(
        description="Si hay más items disponibles"
    )
    
    class Config:
        """Configuración del modelo."""
        schema_extra = {
            "example": {
                "items": ["item1", "item2"],
                "next_cursor": "eyJpZCI6IDEyM30=",
                "previous_cursor": None,
                "has_more": True
            }
        }