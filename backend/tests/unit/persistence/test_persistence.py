"""
Pruebas unitarias para la capa de persistencia con Supabase.

Este módulo contiene pruebas para verificar el funcionamiento
de la persistencia de usuarios y conversaciones en Supabase.
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from clients.supabase_client import MockSupabaseClient, SupabaseClient

# Constantes para pruebas
TEST_API_KEY = "test_api_key_123"
TEST_USER_ID = str(uuid.uuid4())
TEST_CONVERSATION_ID = str(uuid.uuid4())
TEST_MESSAGE = "Mensaje de prueba"


@pytest.fixture
def supabase_client():
    """Fixture que proporciona un cliente Supabase simulado."""
    client = SupabaseClient()
    # Usar cliente mock
    client.supabase = MockSupabaseClient()
    client.is_initialized = True
    return client


class TestUserPersistence:
    """Pruebas para la persistencia de usuarios."""

    @pytest.mark.asyncio
    async def test_get_or_create_user_by_api_key_new(self, supabase_client):
        """Prueba la creación de un nuevo usuario por API key."""
        with patch.object(
            supabase_client, "execute_query", new_callable=AsyncMock
        ) as mock_execute:
            # Mock: primero no encuentra usuario, luego lo crea
            mock_execute.side_effect = [
                {"data": []},  # No existe usuario
                {
                    "data": [
                        {
                            "id": str(uuid.uuid4()),
                            "api_key": TEST_API_KEY,
                            "created_at": "2024-01-01 00:00:00",
                            "is_active": True,
                        }
                    ]
                },  # Usuario creado
            ]

            # Obtener un usuario que no existe (se creará)
            user = await supabase_client.get_or_create_user_by_api_key(TEST_API_KEY)

            # Verificar que se creó correctamente
            assert user is not None
            assert "id" in user
            assert user["api_key"] == TEST_API_KEY
            assert "created_at" in user

            # Verificar que se llamaron los métodos correctos
            assert mock_execute.call_count == 2

    @pytest.mark.asyncio
    async def test_get_or_create_user_by_api_key_existing(self, supabase_client):
        """Prueba la obtención de un usuario existente por API key."""
        existing_user = {
            "id": str(uuid.uuid4()),
            "api_key": TEST_API_KEY,
            "created_at": "2024-01-01 00:00:00",
            "is_active": True,
        }

        with patch.object(
            supabase_client, "execute_query", new_callable=AsyncMock
        ) as mock_execute:
            # Mock: encuentra el usuario existente
            mock_execute.return_value = {"data": [existing_user]}

            # Obtener el usuario existente
            user = await supabase_client.get_or_create_user_by_api_key(TEST_API_KEY)

            # Verificar que es el usuario existente
            assert user["id"] == existing_user["id"]
            assert user["api_key"] == existing_user["api_key"]

            # Verificar que solo se hizo una consulta de búsqueda
            assert mock_execute.call_count == 1


class TestConversationPersistence:
    """Pruebas para la persistencia de conversaciones."""

    @pytest.mark.asyncio
    async def test_log_conversation_message(self, supabase_client):
        """Prueba el registro de un mensaje de conversación."""
        message_data = {
            "id": str(uuid.uuid4()),
            "conversation_id": TEST_CONVERSATION_ID,
            "user_id": TEST_USER_ID,
            "role": "user",
            "content": TEST_MESSAGE,
            "created_at": "2024-01-01 00:00:00",
        }

        with patch.object(
            supabase_client, "execute_query", new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = {"data": [message_data]}

            # Registrar un mensaje
            result = await supabase_client.log_conversation_message(
                TEST_CONVERSATION_ID, TEST_USER_ID, "user", TEST_MESSAGE
            )

            # Verificar que se registró correctamente
            assert result is not None
            assert "id" in result
            assert result["user_id"] == TEST_USER_ID
            assert result["role"] == "user"
            assert result["content"] == TEST_MESSAGE

            # Verificar que se llamó el método correcto
            mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_conversation_history_empty(self, supabase_client):
        """Prueba la obtención de un historial de conversación vacío."""
        with patch.object(
            supabase_client, "execute_query", new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = {"data": []}

            # Obtener historial (vacío)
            history = await supabase_client.get_conversation_history(
                TEST_CONVERSATION_ID
            )

            # Verificar que está vacío
            assert history == []

    @pytest.mark.asyncio
    async def test_get_conversation_history_with_messages(self, supabase_client):
        """Prueba la obtención de un historial de conversación con mensajes."""
        messages = [
            {
                "id": str(uuid.uuid4()),
                "conversation_id": TEST_CONVERSATION_ID,
                "role": "user",
                "content": "Mensaje 1",
                "created_at": "2024-01-01 00:00:00",
            },
            {
                "id": str(uuid.uuid4()),
                "conversation_id": TEST_CONVERSATION_ID,
                "role": "assistant",
                "content": "Respuesta 1",
                "created_at": "2024-01-01 00:00:01",
            },
            {
                "id": str(uuid.uuid4()),
                "conversation_id": TEST_CONVERSATION_ID,
                "role": "user",
                "content": "Mensaje 2",
                "created_at": "2024-01-01 00:00:02",
            },
            {
                "id": str(uuid.uuid4()),
                "conversation_id": TEST_CONVERSATION_ID,
                "role": "assistant",
                "content": "Respuesta 2",
                "created_at": "2024-01-01 00:00:03",
            },
        ]

        with patch.object(
            supabase_client, "execute_query", new_callable=AsyncMock
        ) as mock_execute:
            mock_execute.return_value = {"data": messages}

            # Obtener historial
            history = await supabase_client.get_conversation_history(
                TEST_CONVERSATION_ID
            )

            # Verificar que contiene los mensajes
            assert len(history) == 4
            assert history[0]["content"] == "Mensaje 1"
            assert history[1]["content"] == "Respuesta 1"
            assert history[2]["content"] == "Mensaje 2"
            assert history[3]["content"] == "Respuesta 2"

    @pytest.mark.asyncio
    async def test_get_conversation_history_with_pagination(self, supabase_client):
        """Prueba la paginación del historial de conversación."""
        # Preparar mensajes para paginación
        all_messages = [
            {
                "id": str(uuid.uuid4()),
                "conversation_id": TEST_CONVERSATION_ID,
                "role": "user",
                "content": "Mensaje 1",
                "created_at": "2024-01-01 00:00:00",
            },
            {
                "id": str(uuid.uuid4()),
                "conversation_id": TEST_CONVERSATION_ID,
                "role": "assistant",
                "content": "Respuesta 1",
                "created_at": "2024-01-01 00:00:01",
            },
            {
                "id": str(uuid.uuid4()),
                "conversation_id": TEST_CONVERSATION_ID,
                "role": "user",
                "content": "Mensaje 2",
                "created_at": "2024-01-01 00:00:02",
            },
            {
                "id": str(uuid.uuid4()),
                "conversation_id": TEST_CONVERSATION_ID,
                "role": "assistant",
                "content": "Respuesta 2",
                "created_at": "2024-01-01 00:00:03",
            },
            {
                "id": str(uuid.uuid4()),
                "conversation_id": TEST_CONVERSATION_ID,
                "role": "user",
                "content": "Mensaje 3",
                "created_at": "2024-01-01 00:00:04",
            },
            {
                "id": str(uuid.uuid4()),
                "conversation_id": TEST_CONVERSATION_ID,
                "role": "assistant",
                "content": "Respuesta 3",
                "created_at": "2024-01-01 00:00:05",
            },
        ]

        with patch.object(
            supabase_client, "execute_query", new_callable=AsyncMock
        ) as mock_execute:
            # Mock para primera página (primeros 4 mensajes)
            mock_execute.side_effect = [
                {"data": all_messages[:4]},  # Primera página
                {"data": all_messages[4:]},  # Segunda página
            ]

            # Obtener primera página
            page1 = await supabase_client.get_conversation_history(
                TEST_CONVERSATION_ID, limit=4, offset=0
            )
            assert len(page1) == 4
            assert page1[0]["content"] == "Mensaje 1"
            assert page1[1]["content"] == "Respuesta 1"
            assert page1[2]["content"] == "Mensaje 2"
            assert page1[3]["content"] == "Respuesta 2"

            # Obtener segunda página
            page2 = await supabase_client.get_conversation_history(
                TEST_CONVERSATION_ID, limit=4, offset=4
            )
            assert len(page2) == 2  # Solo quedan 2 mensajes
            assert page2[0]["content"] == "Mensaje 3"
            assert page2[1]["content"] == "Respuesta 3"

    @pytest.mark.asyncio
    async def test_get_conversation_history_for_different_conversations(
        self, supabase_client
    ):
        """Prueba que el historial se filtra correctamente por conversación."""
        # Crear otro ID de conversación
        other_conversation_id = str(uuid.uuid4())

        with patch.object(
            supabase_client, "execute_query", new_callable=AsyncMock
        ) as mock_execute:
            # Mock para diferentes conversaciones
            mock_execute.side_effect = [
                {
                    "data": [
                        {
                            "id": str(uuid.uuid4()),
                            "conversation_id": TEST_CONVERSATION_ID,
                            "content": "Mensaje conversación 1",
                        }
                    ]
                },
                {
                    "data": [
                        {
                            "id": str(uuid.uuid4()),
                            "conversation_id": other_conversation_id,
                            "content": "Mensaje conversación 2",
                        }
                    ]
                },
            ]

            # Obtener historial para la primera conversación
            history1 = await supabase_client.get_conversation_history(
                TEST_CONVERSATION_ID
            )
            assert len(history1) == 1
            assert history1[0]["content"] == "Mensaje conversación 1"

            # Obtener historial para la segunda conversación
            history2 = await supabase_client.get_conversation_history(
                other_conversation_id
            )
            assert len(history2) == 1
            assert history2[0]["content"] == "Mensaje conversación 2"


class TestSupabaseClientModes:
    """Pruebas para verificar el comportamiento del cliente."""

    @pytest.mark.asyncio
    async def test_get_or_create_user_with_error_fallback(self, supabase_client):
        """Prueba que el método maneja errores correctamente y retorna un usuario mock."""
        with patch.object(
            supabase_client, "execute_query", new_callable=AsyncMock
        ) as mock_execute:
            # Mock de error
            mock_execute.side_effect = Exception("Database connection error")

            # Ejecutar la función
            user = await supabase_client.get_or_create_user_by_api_key(TEST_API_KEY)

            # Verificar que se retorna un usuario mock válido
            assert user is not None
            assert "id" in user
            assert user["api_key"] == TEST_API_KEY
            assert "created_at" in user
            assert user["is_active"] is True

    @pytest.mark.asyncio
    async def test_log_conversation_message_with_error_fallback(self, supabase_client):
        """Prueba que el método maneja errores correctamente y retorna un mensaje mock."""
        with patch.object(
            supabase_client, "execute_query", new_callable=AsyncMock
        ) as mock_execute:
            # Mock de error
            mock_execute.side_effect = Exception("Database connection error")

            # Ejecutar la función
            result = await supabase_client.log_conversation_message(
                TEST_CONVERSATION_ID, TEST_USER_ID, "user", TEST_MESSAGE
            )

            # Verificar que se retorna un mensaje mock válido
            assert result is not None
            assert "id" in result
            assert result["conversation_id"] == TEST_CONVERSATION_ID
            assert result["user_id"] == TEST_USER_ID
            assert result["role"] == "user"
            assert result["content"] == TEST_MESSAGE
            assert "created_at" in result

    @pytest.mark.asyncio
    async def test_get_conversation_history_with_error_fallback(self, supabase_client):
        """Prueba que el método maneja errores correctamente y retorna una lista vacía."""
        with patch.object(
            supabase_client, "execute_query", new_callable=AsyncMock
        ) as mock_execute:
            # Mock de error
            mock_execute.side_effect = Exception("Database connection error")

            # Ejecutar la función
            result = await supabase_client.get_conversation_history(
                TEST_CONVERSATION_ID
            )

            # Verificar que se retorna una lista vacía
            assert result == []
