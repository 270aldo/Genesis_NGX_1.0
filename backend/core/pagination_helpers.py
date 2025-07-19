"""
Helpers para implementar paginación en los endpoints.

Este módulo proporciona funciones utilitarias para facilitar
la implementación de paginación en consultas a base de datos.
"""

from typing import List, TypeVar, Optional, Tuple, Any, Dict
from sqlalchemy import select, func
from sqlalchemy.sql import Select
from sqlalchemy.ext.asyncio import AsyncSession
import base64
import json
from datetime import datetime

from app.schemas.pagination import (
    PaginationParams, 
    PaginatedResponse,
    CursorPaginationParams,
    CursorPaginatedResponse
)
from core.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


async def paginate_query(
    db: AsyncSession,
    query: Select,
    params: PaginationParams,
    base_url: str,
    model_class: type
) -> PaginatedResponse:
    """
    Paginar una consulta SQLAlchemy.
    
    Args:
        db: Sesión de base de datos
        query: Query de SQLAlchemy a paginar
        params: Parámetros de paginación
        base_url: URL base para generar links
        model_class: Clase del modelo para serialización
        
    Returns:
        PaginatedResponse con los resultados
    """
    # Contar total de items
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total_items = total_result.scalar() or 0
    
    # Aplicar ordenamiento si se especifica
    if params.sort_by:
        # Verificar que el campo existe en el modelo
        if hasattr(model_class, params.sort_by):
            order_column = getattr(model_class, params.sort_by)
            if params.sort_order == "desc":
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        else:
            logger.warning(f"Campo de ordenamiento no válido: {params.sort_by}")
    
    # Aplicar paginación
    query = query.offset(params.offset).limit(params.limit)
    
    # Ejecutar query
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Crear respuesta paginada
    return PaginatedResponse.create(
        items=items,
        params=params,
        total_items=total_items,
        base_url=base_url
    )


def paginate_list(
    items: List[T],
    params: PaginationParams,
    base_url: str
) -> PaginatedResponse[T]:
    """
    Paginar una lista en memoria.
    
    Args:
        items: Lista completa de items
        params: Parámetros de paginación
        base_url: URL base para generar links
        
    Returns:
        PaginatedResponse con los items paginados
    """
    total_items = len(items)
    
    # Aplicar ordenamiento si se especifica
    if params.sort_by:
        reverse = params.sort_order == "desc"
        try:
            # Intentar ordenar por atributo
            items = sorted(
                items, 
                key=lambda x: getattr(x, params.sort_by, None),
                reverse=reverse
            )
        except Exception as e:
            logger.warning(f"Error al ordenar por {params.sort_by}: {e}")
    
    # Aplicar paginación
    start = params.offset
    end = start + params.limit
    paginated_items = items[start:end]
    
    return PaginatedResponse.create(
        items=paginated_items,
        params=params,
        total_items=total_items,
        base_url=base_url
    )


def encode_cursor(data: Dict[str, Any]) -> str:
    """
    Codificar datos en un cursor.
    
    Args:
        data: Diccionario con los datos a codificar
        
    Returns:
        String del cursor codificado
    """
    json_str = json.dumps(data, default=str)
    return base64.urlsafe_b64encode(json_str.encode()).decode()


def decode_cursor(cursor: str) -> Dict[str, Any]:
    """
    Decodificar un cursor.
    
    Args:
        cursor: String del cursor codificado
        
    Returns:
        Diccionario con los datos decodificados
    """
    try:
        json_str = base64.urlsafe_b64decode(cursor.encode()).decode()
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"Error decodificando cursor: {e}")
        return {}


async def cursor_paginate_query(
    db: AsyncSession,
    query: Select,
    params: CursorPaginationParams,
    cursor_field: str = "id",
    model_class: type = None
) -> CursorPaginatedResponse:
    """
    Paginar una consulta usando cursor.
    
    Args:
        db: Sesión de base de datos
        query: Query de SQLAlchemy a paginar
        params: Parámetros de paginación con cursor
        cursor_field: Campo a usar para el cursor
        model_class: Clase del modelo
        
    Returns:
        CursorPaginatedResponse con los resultados
    """
    # Decodificar cursor si existe
    if params.cursor:
        cursor_data = decode_cursor(params.cursor)
        cursor_value = cursor_data.get(cursor_field)
        
        if cursor_value and model_class:
            cursor_column = getattr(model_class, cursor_field)
            if params.direction == "next":
                query = query.filter(cursor_column > cursor_value)
            else:
                query = query.filter(cursor_column < cursor_value)
                query = query.order_by(cursor_column.desc())
    
    # Aplicar límite (+1 para saber si hay más)
    query = query.limit(params.limit + 1)
    
    # Ejecutar query
    result = await db.execute(query)
    items = result.scalars().all()
    
    # Determinar si hay más items
    has_more = len(items) > params.limit
    if has_more:
        items = items[:params.limit]
    
    # Generar cursors
    next_cursor = None
    previous_cursor = None
    
    if items:
        if has_more:
            last_item = items[-1]
            next_cursor = encode_cursor({
                cursor_field: getattr(last_item, cursor_field)
            })
        
        if params.cursor or params.page > 1:
            first_item = items[0]
            previous_cursor = encode_cursor({
                cursor_field: getattr(first_item, cursor_field)
            })
    
    return CursorPaginatedResponse(
        items=items,
        next_cursor=next_cursor,
        previous_cursor=previous_cursor,
        has_more=has_more
    )


class PaginationMixin:
    """
    Mixin para agregar paginación a modelos SQLAlchemy.
    
    Uso:
        class User(Base, PaginationMixin):
            __tablename__ = "users"
            id = Column(Integer, primary_key=True)
            name = Column(String)
    """
    
    @classmethod
    async def paginate(
        cls,
        db: AsyncSession,
        params: PaginationParams,
        base_url: str,
        filters: Optional[List] = None
    ) -> PaginatedResponse:
        """
        Paginar registros del modelo.
        
        Args:
            db: Sesión de base de datos
            params: Parámetros de paginación
            base_url: URL base para links
            filters: Filtros adicionales para la query
            
        Returns:
            PaginatedResponse con los registros
        """
        query = select(cls)
        
        # Aplicar filtros si existen
        if filters:
            for filter_condition in filters:
                query = query.filter(filter_condition)
        
        return await paginate_query(
            db=db,
            query=query,
            params=params,
            base_url=base_url,
            model_class=cls
        )


def apply_pagination_to_dict_list(
    items: List[Dict[str, Any]],
    params: PaginationParams,
    base_url: str,
    sort_key: Optional[str] = None
) -> PaginatedResponse[Dict[str, Any]]:
    """
    Paginar una lista de diccionarios.
    
    Args:
        items: Lista de diccionarios
        params: Parámetros de paginación
        base_url: URL base
        sort_key: Clave para ordenar (si es diferente a sort_by)
        
    Returns:
        PaginatedResponse con los diccionarios paginados
    """
    total_items = len(items)
    
    # Aplicar ordenamiento
    if params.sort_by or sort_key:
        key_to_sort = sort_key or params.sort_by
        reverse = params.sort_order == "desc"
        try:
            items = sorted(
                items,
                key=lambda x: x.get(key_to_sort),
                reverse=reverse
            )
        except Exception as e:
            logger.warning(f"Error al ordenar por {key_to_sort}: {e}")
    
    # Aplicar paginación
    start = params.offset
    end = start + params.limit
    paginated_items = items[start:end]
    
    return PaginatedResponse.create(
        items=paginated_items,
        params=params,
        total_items=total_items,
        base_url=base_url
    )