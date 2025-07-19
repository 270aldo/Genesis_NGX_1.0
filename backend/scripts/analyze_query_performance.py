#!/usr/bin/env python3
"""
Script para analizar el rendimiento de las queries en Supabase.

Este script se conecta a la base de datos y analiza:
- Queries más lentas
- Índices no utilizados
- Sugerencias de nuevos índices
- Estadísticas de tablas
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncpg
from tabulate import tabulate

from core.logging_config import get_logger
from config.secrets import settings

logger = get_logger(__name__)


async def get_database_connection():
    """Obtiene una conexión directa a la base de datos."""
    # Construir URL de conexión desde Supabase
    db_url = settings.SUPABASE_URL.replace('https://', '')
    db_url = db_url.split('.')[0]  # Obtener el ID del proyecto
    
    # La URL de conexión directa de Supabase sigue este patrón
    connection_url = f"postgresql://postgres:{settings.SUPABASE_SERVICE_ROLE_KEY}@db.{db_url}.supabase.co:5432/postgres"
    
    return await asyncpg.connect(connection_url)


async def analyze_slow_queries(conn: asyncpg.Connection, limit: int = 10):
    """Analiza las queries más lentas."""
    print("\n=== QUERIES MÁS LENTAS ===\n")
    
    query = """
    SELECT 
        query,
        calls,
        total_time,
        mean_time,
        min_time,
        max_time
    FROM pg_stat_statements
    WHERE query NOT LIKE '%pg_%'
    ORDER BY mean_time DESC
    LIMIT $1;
    """
    
    try:
        rows = await conn.fetch(query, limit)
        
        if rows:
            headers = ["Query", "Llamadas", "Tiempo Total (ms)", "Tiempo Promedio (ms)", "Min (ms)", "Max (ms)"]
            data = []
            
            for row in rows:
                data.append([
                    row['query'][:50] + "..." if len(row['query']) > 50 else row['query'],
                    row['calls'],
                    f"{row['total_time']:.2f}",
                    f"{row['mean_time']:.2f}",
                    f"{row['min_time']:.2f}",
                    f"{row['max_time']:.2f}"
                ])
            
            print(tabulate(data, headers=headers, tablefmt="grid"))
        else:
            print("No se encontraron estadísticas de queries.")
            print("Nota: pg_stat_statements debe estar habilitado en Supabase.")
    
    except Exception as e:
        logger.warning(f"No se pudieron obtener estadísticas de queries: {e}")


async def analyze_unused_indexes(conn: asyncpg.Connection):
    """Identifica índices que no se están utilizando."""
    print("\n=== ÍNDICES NO UTILIZADOS ===\n")
    
    query = """
    SELECT 
        schemaname,
        tablename,
        indexname,
        idx_scan,
        idx_tup_read,
        idx_tup_fetch
    FROM pg_stat_user_indexes
    WHERE schemaname = 'public'
    AND idx_scan = 0
    ORDER BY tablename, indexname;
    """
    
    rows = await conn.fetch(query)
    
    if rows:
        headers = ["Tabla", "Índice", "Escaneos", "Tuplas Leídas", "Tuplas Obtenidas"]
        data = []
        
        for row in rows:
            data.append([
                row['tablename'],
                row['indexname'],
                row['idx_scan'],
                row['idx_tup_read'],
                row['idx_tup_fetch']
            ])
        
        print(tabulate(data, headers=headers, tablefmt="grid"))
        print(f"\nTotal de índices no utilizados: {len(rows)}")
    else:
        print("✅ Todos los índices están siendo utilizados.")


async def analyze_table_statistics(conn: asyncpg.Connection):
    """Analiza estadísticas de las tablas principales."""
    print("\n=== ESTADÍSTICAS DE TABLAS ===\n")
    
    query = """
    SELECT 
        schemaname,
        tablename,
        n_live_tup as live_tuples,
        n_dead_tup as dead_tuples,
        n_mod_since_analyze as mods_since_analyze,
        last_vacuum,
        last_autovacuum,
        last_analyze,
        last_autoanalyze
    FROM pg_stat_user_tables
    WHERE schemaname = 'public'
    ORDER BY n_live_tup DESC;
    """
    
    rows = await conn.fetch(query)
    
    if rows:
        headers = ["Tabla", "Tuplas Vivas", "Tuplas Muertas", "Mods desde Analyze", "Último Vacuum", "Último Analyze"]
        data = []
        
        for row in rows:
            last_vacuum = row['last_vacuum'] or row['last_autovacuum']
            last_analyze = row['last_analyze'] or row['last_autoanalyze']
            
            data.append([
                row['tablename'],
                f"{row['live_tuples']:,}",
                f"{row['dead_tuples']:,}",
                f"{row['mods_since_analyze']:,}",
                last_vacuum.strftime("%Y-%m-%d %H:%M") if last_vacuum else "Nunca",
                last_analyze.strftime("%Y-%m-%d %H:%M") if last_analyze else "Nunca"
            ])
        
        print(tabulate(data, headers=headers, tablefmt="grid"))


async def suggest_missing_indexes(conn: asyncpg.Connection):
    """Sugiere índices que podrían mejorar el rendimiento."""
    print("\n=== SUGERENCIAS DE ÍNDICES ===\n")
    
    # Buscar columnas frecuentemente usadas en WHERE sin índices
    suggestions = []
    
    # Verificar foreign keys sin índices
    fk_query = """
    SELECT
        tc.table_name,
        kcu.column_name,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name
    FROM information_schema.table_constraints AS tc
    JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
        ON ccu.constraint_name = tc.constraint_name
        AND ccu.table_schema = tc.table_schema
    WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_schema = 'public'
    AND NOT EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = tc.table_name
        AND indexdef LIKE '%' || kcu.column_name || '%'
    );
    """
    
    fk_rows = await conn.fetch(fk_query)
    
    if fk_rows:
        print("📌 Foreign Keys sin índices (pueden causar lentitud en JOINs):")
        for row in fk_rows:
            suggestion = f"CREATE INDEX idx_{row['table_name']}_{row['column_name']} ON public.{row['table_name']}({row['column_name']});"
            suggestions.append(suggestion)
            print(f"  - {row['table_name']}.{row['column_name']} → {row['foreign_table_name']}.{row['foreign_column_name']}")
    
    # Sugerir índices para columnas de fecha comúnmente filtradas
    date_columns = [
        ('chat_messages', 'created_at'),
        ('training_sessions', 'session_date'),
        ('nutrition_logs', 'log_date'),
        ('usage_metrics', 'metric_date'),
        ('error_logs', 'created_at'),
    ]
    
    print("\n📌 Columnas de fecha que podrían beneficiarse de índices parciales:")
    for table, column in date_columns:
        suggestion = f"CREATE INDEX idx_{table}_{column}_recent ON public.{table}({column}) WHERE {column} > (NOW() - INTERVAL '30 days');"
        suggestions.append(suggestion)
        print(f"  - {table}.{column} (últimos 30 días)")
    
    if suggestions:
        print("\n📝 Script SQL sugerido:")
        print("-- Copiar y ejecutar en Supabase SQL Editor si es necesario")
        for suggestion in suggestions[:5]:  # Mostrar solo las primeras 5
            print(suggestion)
        if len(suggestions) > 5:
            print(f"-- ... y {len(suggestions) - 5} sugerencias más")


async def main():
    """Función principal."""
    print("=== ANÁLISIS DE RENDIMIENTO DE QUERIES - GENESIS ===")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # Conectar a la base de datos
        print("Conectando a Supabase...")
        conn = await get_database_connection()
        print("✅ Conexión establecida\n")
        
        # Ejecutar análisis
        await analyze_slow_queries(conn)
        await analyze_unused_indexes(conn)
        await analyze_table_statistics(conn)
        await suggest_missing_indexes(conn)
        
        print("\n=== RECOMENDACIONES GENERALES ===")
        print("1. Ejecutar VACUUM ANALYZE regularmente en tablas grandes")
        print("2. Monitorear el crecimiento de tuplas muertas")
        print("3. Revisar y eliminar índices no utilizados")
        print("4. Considerar particionamiento para tablas muy grandes")
        print("5. Habilitar pg_stat_statements para mejor análisis")
        
        # Cerrar conexión
        await conn.close()
        
    except Exception as e:
        logger.error(f"Error en el análisis: {e}")
        print(f"\n❌ Error: {e}")
        print("\nNota: Este script requiere conexión directa a PostgreSQL.")
        print("Verifica que las credenciales de Supabase estén configuradas correctamente.")


if __name__ == "__main__":
    asyncio.run(main())