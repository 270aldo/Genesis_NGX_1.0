#!/usr/bin/env python3
"""
Script de prueba para verificar el streaming real con SSE.

Este script prueba la funcionalidad de streaming en tiempo real
del sistema NGX Agents.
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime


async def test_streaming_endpoint():
    """Prueba el endpoint de streaming."""
    # URL del endpoint
    url = "http://localhost:8000/api/v1/stream/chat"
    
    # Headers con autenticación (ajustar según tu configuración)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-token",  # Reemplazar con token válido
    }
    
    # Datos de prueba
    data = {
        "message": "Dame un plan de entrenamiento para principiantes",
        "conversation_id": "test-stream-123",
        "metadata": {
            "test": True,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    print(f"[{datetime.now()}] Iniciando prueba de streaming...")
    print(f"[{datetime.now()}] URL: {url}")
    print(f"[{datetime.now()}] Mensaje: {data['message']}")
    print("-" * 80)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                print(f"[{datetime.now()}] Status: {response.status}")
                
                if response.status != 200:
                    error_text = await response.text()
                    print(f"[{datetime.now()}] Error: {error_text}")
                    return
                
                # Leer stream SSE
                chunk_count = 0
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if not line:
                        continue
                    
                    # Parsear eventos SSE
                    if line.startswith('event:'):
                        event_type = line[6:].strip()
                        print(f"[{datetime.now()}] Evento: {event_type}")
                    
                    elif line.startswith('data:'):
                        try:
                            data_str = line[5:].strip()
                            data = json.loads(data_str)
                            chunk_count += 1
                            
                            # Mostrar contenido según el tipo
                            if data.get('type') == 'content':
                                print(f"[Chunk {chunk_count}] {data.get('content', '')}", end='', flush=True)
                            elif data.get('type') == 'status':
                                print(f"\n[Status] {data.get('message', '')}")
                            elif data.get('type') == 'intent_analysis':
                                print(f"\n[Intent] {data.get('intent', '')} (confianza: {data.get('confidence', 0):.2f})")
                            elif data.get('type') == 'agent_start':
                                print(f"\n[Agent] Iniciando {data.get('agent_id', '')}")
                            elif data.get('type') == 'complete':
                                print(f"\n[Complete] Total chunks: {data.get('chunk_count', chunk_count)}")
                            elif data.get('type') == 'error':
                                print(f"\n[Error] {data.get('error', 'Unknown error')}")
                            
                        except json.JSONDecodeError:
                            print(f"[{datetime.now()}] Error parsing JSON: {data_str}")
                
                print(f"\n[{datetime.now()}] Streaming completado. Total chunks: {chunk_count}")
                
    except Exception as e:
        print(f"[{datetime.now()}] Error: {e}")
        import traceback
        traceback.print_exc()


async def test_health_endpoint():
    """Verifica que el servicio esté activo."""
    url = "http://localhost:8000/api/v1/stream/health"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                print(f"[Health Check] {data}")
                return response.status == 200
    except Exception as e:
        print(f"[Health Check Failed] {e}")
        return False


async def main():
    """Función principal."""
    print("=== NGX Agents - Prueba de Streaming SSE ===\n")
    
    # Verificar salud del servicio
    print("Verificando servicio...")
    if not await test_health_endpoint():
        print("❌ El servicio no está disponible. Asegúrate de que el backend esté ejecutándose.")
        sys.exit(1)
    
    print("✅ Servicio disponible\n")
    
    # Ejecutar prueba de streaming
    await test_streaming_endpoint()
    
    print("\n=== Prueba completada ===")


if __name__ == "__main__":
    asyncio.run(main())