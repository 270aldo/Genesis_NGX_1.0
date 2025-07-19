#!/usr/bin/env python3
"""
NGX Agents Database Migration Runner
==================================

Script para ejecutar las migraciones de base de datos de NGX Agents de forma segura
y con verificación de integridad completa.

Usage:
    python scripts/run_database_migrations.py [--dry-run] [--rollback] [--force]

Options:
    --dry-run    : Solo verifica las migraciones sin ejecutarlas
    --rollback   : Deshace la última migración (NO IMPLEMENTADO AÚN)
    --force      : Fuerza la ejecución sin confirmación
    --verbose    : Muestra información detallada
"""

import os
import sys
import asyncio
import argparse
import asyncpg
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import hashlib
import json
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
env_path = project_root / '.env'
load_dotenv(env_path)

try:
    from clients.supabase_client import get_supabase_client
    from core.logging_config import get_logger
    from core.settings import settings
except ImportError as e:
    print(f"Error importing NGX modules: {e}")
    print("Please ensure you're running from the project root directory")
    sys.exit(1)

logger = get_logger(__name__)

class DatabaseMigrationRunner:
    """Ejecutor de migraciones de base de datos con verificación de integridad"""
    
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.migrations_dir = project_root / "data" / "sql"
        self.settings = settings
        self.migration_files = [
            "001_master_setup.sql",
            "002_advanced_features.sql"
        ]
        
    async def get_database_connection(self) -> asyncpg.Connection:
        """Establece conexión a la base de datos"""
        try:
            # Try to get connection details from Supabase client
            supabase = get_supabase_client()
            
            # For now, we'll use environment variables
            # In production, this should use proper Supabase connection details
            database_url = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL')
            
            if not database_url:
                raise ValueError("No database URL found in environment variables")
                
            conn = await asyncpg.connect(database_url)
            logger.info("Database connection established successfully")
            return conn
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def calculate_file_checksum(self, file_path: Path) -> str:
        """Calcula checksum MD5 del archivo de migración"""
        with open(file_path, 'rb') as f:
            content = f.read()
            return hashlib.md5(content).hexdigest()
    
    async def check_migration_table(self, conn: asyncpg.Connection) -> bool:
        """Verifica si existe la tabla de log de migraciones"""
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'migration_log' AND table_schema = 'public'
            )
        """)
        return result
    
    async def get_executed_migrations(self, conn: asyncpg.Connection) -> Dict[str, Dict]:
        """Obtiene lista de migraciones ya ejecutadas"""
        if not await self.check_migration_table(conn):
            return {}
            
        rows = await conn.fetch("""
            SELECT migration_name, status, executed_at, checksum
            FROM migration_log
            ORDER BY executed_at
        """)
        
        return {
            row['migration_name']: {
                'status': row['status'],
                'executed_at': row['executed_at'],
                'checksum': row['checksum']
            }
            for row in rows
        }
    
    async def verify_prerequisites(self, conn: asyncpg.Connection) -> bool:
        """Verifica prerrequisitos del sistema"""
        logger.info("Verificando prerrequisitos del sistema...")
        
        # Check PostgreSQL version
        version = await conn.fetchval("SELECT version()")
        logger.info(f"PostgreSQL version: {version}")
        
        # Check for uuid-ossp extension
        uuid_ext = await conn.fetchval("""
            SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'uuid-ossp')
        """)
        
        if not uuid_ext:
            logger.warning("uuid-ossp extension not found - will be created during migration")
        
        # Check disk space (basic check)
        db_size = await conn.fetchval("SELECT pg_size_pretty(pg_database_size(current_database()))")
        logger.info(f"Current database size: {db_size}")
        
        return True
    
    async def execute_migration_file(self, conn: asyncpg.Connection, file_path: Path) -> Dict:
        """Ejecuta un archivo de migración específico"""
        start_time = datetime.now()
        migration_name = file_path.stem
        checksum = self.calculate_file_checksum(file_path)
        
        logger.info(f"Ejecutando migración: {migration_name}")
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Archivo: {file_path}")
            logger.info(f"[DRY RUN] Checksum: {checksum}")
            return {
                'name': migration_name,
                'status': 'dry_run',
                'execution_time': 0,
                'checksum': checksum
            }
        
        try:
            # Read and execute SQL file
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Execute in a transaction
            async with conn.transaction():
                await conn.execute(sql_content)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Migración {migration_name} completada en {execution_time:.2f} segundos")
            
            return {
                'name': migration_name,
                'status': 'completed',
                'execution_time': execution_time,
                'checksum': checksum
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error en migración {migration_name}: {e}")
            
            return {
                'name': migration_name,
                'status': 'failed',
                'execution_time': execution_time,
                'error': str(e),
                'checksum': checksum
            }
    
    async def verify_migration_integrity(self, conn: asyncpg.Connection) -> Dict:
        """Verifica la integridad de las migraciones ejecutadas"""
        logger.info("Verificando integridad post-migración...")
        
        verification_results = {
            'tables_created': 0,
            'indexes_created': 0,
            'views_created': 0,
            'triggers_created': 0,
            'critical_tables_missing': [],
            'agents_registered': 0,
            'partnerships_configured': 0
        }
        
        # Count database objects
        verification_results['tables_created'] = await conn.fetchval("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        
        verification_results['indexes_created'] = await conn.fetchval("""
            SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public'
        """)
        
        verification_results['views_created'] = await conn.fetchval("""
            SELECT COUNT(*) FROM information_schema.views WHERE table_schema = 'public'
        """)
        
        verification_results['triggers_created'] = await conn.fetchval("""
            SELECT COUNT(*) FROM information_schema.triggers WHERE trigger_schema = 'public'
        """)
        
        # Check critical tables
        critical_tables = [
            'users', 'agents', 'conversation_memory', 'agent_partnerships', 
            'query_performance_metrics', 'user_sessions', 'collaboration_requests'
        ]
        
        for table in critical_tables:
            exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = $1 AND table_schema = 'public'
                )
            """, table)
            
            if not exists:
                verification_results['critical_tables_missing'].append(table)
        
        # Check data integrity
        try:
            verification_results['agents_registered'] = await conn.fetchval(
                "SELECT COUNT(*) FROM agents"
            ) or 0
        except Exception:
            verification_results['agents_registered'] = 0
            
        try:
            verification_results['partnerships_configured'] = await conn.fetchval(
                "SELECT COUNT(*) FROM agent_partnerships"
            ) or 0
        except Exception:
            verification_results['partnerships_configured'] = 0
        
        return verification_results
    
    async def run_migrations(self, force: bool = False) -> bool:
        """Ejecuta todas las migraciones en orden"""
        logger.info("=== INICIANDO MIGRACIONES DE NGX AGENTS ===")
        
        if self.dry_run:
            logger.info("MODO DRY RUN - No se ejecutarán cambios reales")
        
        try:
            conn = await self.get_database_connection()
            
            # Verify prerequisites
            await self.verify_prerequisites(conn)
            
            # Get executed migrations
            executed_migrations = await self.get_executed_migrations(conn)
            
            if executed_migrations and not force and not self.dry_run:
                logger.warning(f"Se encontraron {len(executed_migrations)} migraciones previas")
                logger.warning("Use --force para forzar re-ejecución")
                
                response = input("¿Continuar de todos modos? (y/N): ")
                if response.lower() != 'y':
                    logger.info("Migración cancelada por el usuario")
                    return False
            
            # Execute migrations
            migration_results = []
            
            for migration_file in self.migration_files:
                file_path = self.migrations_dir / migration_file
                
                if not file_path.exists():
                    logger.error(f"Archivo de migración no encontrado: {file_path}")
                    return False
                
                migration_name = file_path.stem
                
                # Check if already executed
                if migration_name in executed_migrations:
                    existing = executed_migrations[migration_name]
                    current_checksum = self.calculate_file_checksum(file_path)
                    
                    if existing['status'] == 'completed' and existing.get('checksum') == current_checksum:
                        logger.info(f"Migración {migration_name} ya ejecutada - saltando")
                        continue
                    elif not force:
                        logger.warning(f"Migración {migration_name} cambió desde la última ejecución")
                        logger.warning("Use --force para forzar re-ejecución")
                        continue
                
                # Execute migration
                result = await self.execute_migration_file(conn, file_path)
                migration_results.append(result)
                
                if result['status'] == 'failed':
                    logger.error(f"Migración falló: {migration_name}")
                    return False
            
            # Verify integrity
            if not self.dry_run:
                verification = await self.verify_migration_integrity(conn)
                
                logger.info("=== VERIFICACIÓN POST-MIGRACIÓN ===")
                logger.info(f"Tablas creadas: {verification['tables_created']}")
                logger.info(f"Índices creados: {verification['indexes_created']}")
                logger.info(f"Vistas creadas: {verification['views_created']}")
                logger.info(f"Triggers creados: {verification['triggers_created']}")
                logger.info(f"Agentes registrados: {verification['agents_registered']}")
                logger.info(f"Partnerships configurados: {verification['partnerships_configured']}")
                
                if verification['critical_tables_missing']:
                    logger.error(f"Tablas críticas faltantes: {verification['critical_tables_missing']}")
                    return False
                
                logger.info("✅ Verificación de integridad exitosa")
            
            logger.info("=== MIGRACIONES COMPLETADAS EXITOSAMENTE ===")
            
            if not self.dry_run:
                logger.info("La base de datos está lista para NGX Agents FASE 12")
                logger.info("Próximos pasos:")
                logger.info("  1. Actualizar configuración de la aplicación")
                logger.info("  2. Ejecutar tests de la aplicación")
                logger.info("  3. Monitorear métricas de rendimiento")
            
            return True
            
        except Exception as e:
            logger.error(f"Error durante la migración: {e}")
            return False
        finally:
            if 'conn' in locals():
                await conn.close()

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="NGX Agents Database Migration Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Solo verifica las migraciones sin ejecutarlas'
    )
    
    parser.add_argument(
        '--force', 
        action='store_true',
        help='Fuerza la ejecución sin confirmación'
    )
    
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Muestra información detallada'
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run migrations
    runner = DatabaseMigrationRunner(dry_run=args.dry_run, verbose=args.verbose)
    
    try:
        success = asyncio.run(runner.run_migrations(force=args.force))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Migración cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()