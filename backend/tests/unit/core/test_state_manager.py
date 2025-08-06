"""
Pruebas para el StateManager.

Este módulo contiene pruebas para verificar el funcionamiento
del StateManager con Supabase.
"""

import uuid
from typing import Any, Dict

import pytest

# Importar el adaptador
from infrastructure.adapters.state_manager_adapter import (
    ConversationContext,
    StateManagerAdapter,
)


# Fixture para el StateManagerAdapter
@pytest.fixture
def state_manager_for_test():
    # Crear una instancia del adaptador
    adapter = StateManagerAdapter()
    # Limpiar el estado entre pruebas
    adapter._conversations = {}
    adapter._cache = {}
    adapter._reset_stats()
    yield adapter


@pytest.mark.asyncio
async def test_save_state(
    state_manager_for_test: StateManagerAdapter, test_settings: Dict[str, Any]
):
    """Prueba la función save_conversation del StateManager (equivalente a save_state)."""
    # Datos de prueba
    user_id = test_settings["test_user_id"]
    conversation_id = test_settings["test_conversation_id"]

    # Crear contexto de conversación
    context = ConversationContext(
        conversation_id=conversation_id,
        user_id=user_id,
        messages=[{"role": "user", "content": "test message"}],
        metadata={"key": "value", "nested": {"foo": "bar"}},
    )

    # Guardar conversación
    result = await state_manager_for_test.save_conversation(context)

    # Verificar resultado
    assert result is True


@pytest.mark.asyncio
async def test_load_state(
    state_manager_for_test: StateManagerAdapter, test_settings: Dict[str, Any]
):
    """Prueba la función get_conversation del StateManager (equivalente a load_state)."""
    # Datos de prueba
    user_id = test_settings["test_user_id"]
    conversation_id = test_settings["test_conversation_id"]

    # Crear contexto de conversación
    context = ConversationContext(
        conversation_id=conversation_id,
        user_id=user_id,
        messages=[{"role": "user", "content": "test message"}],
        metadata={"key": "value", "nested": {"foo": "bar"}},
    )

    # Guardar conversación
    await state_manager_for_test.save_conversation(context)

    # Cargar conversación
    loaded_context = await state_manager_for_test.get_conversation(conversation_id)

    # Verificar resultado
    assert loaded_context is not None
    assert loaded_context.conversation_id == conversation_id
    assert loaded_context.user_id == user_id


@pytest.mark.asyncio
async def test_delete_state(
    state_manager_for_test: StateManagerAdapter, test_settings: Dict[str, Any]
):
    """Prueba la función delete_conversation del StateManager (equivalente a delete_state)."""
    # Datos de prueba
    user_id = test_settings["test_user_id"]
    conversation_id = test_settings["test_conversation_id"]

    # Crear contexto de conversación
    context = ConversationContext(
        conversation_id=conversation_id,
        user_id=user_id,
        messages=[{"role": "user", "content": "test message"}],
        metadata={"key": "value"},
    )

    # Guardar conversación
    result = await state_manager_for_test.save_conversation(context)
    assert result is True

    # Eliminar conversación
    deleted = await state_manager_for_test.delete_conversation(conversation_id)

    # Verificar que se eliminó correctamente
    assert deleted is True

    # Intentar cargar la conversación eliminada
    loaded_context = await state_manager_for_test.get_conversation(conversation_id)
    assert loaded_context is None


@pytest.mark.asyncio
async def test_update_existing_state(
    state_manager_for_test: StateManagerAdapter, test_settings: Dict[str, Any]
):
    """Prueba la actualización de una conversación existente."""
    # Datos de prueba
    user_id = test_settings["test_user_id"]
    conversation_id = test_settings["test_conversation_id"]

    # Crear contexto inicial
    initial_context = ConversationContext(
        conversation_id=conversation_id,
        user_id=user_id,
        messages=[{"role": "user", "content": "initial message"}],
        metadata={"key": "value", "counter": 1},
    )

    # Guardar conversación inicial
    await state_manager_for_test.save_conversation(initial_context)

    # Actualizar contexto
    updated_context = ConversationContext(
        conversation_id=conversation_id,
        user_id=user_id,
        messages=[
            {"role": "user", "content": "initial message"},
            {"role": "assistant", "content": "response message"},
        ],
        metadata={"key": "new_value", "counter": 2, "new_key": "added"},
    )

    # Actualizar conversación
    result = await state_manager_for_test.save_conversation(updated_context)
    assert result is True

    # Cargar conversación actualizada
    loaded_context = await state_manager_for_test.get_conversation(conversation_id)

    # Verificar que el estado se actualizó correctamente
    assert loaded_context is not None
    assert len(loaded_context.messages) == 2
    assert loaded_context.metadata["key"] == "new_value"
    assert loaded_context.metadata["counter"] == 2
    assert "new_key" in loaded_context.metadata


@pytest.mark.asyncio
async def test_get_state_field(state_manager_for_test, test_settings: Dict[str, Any]):
    """Prueba funcionalidad básica del StateManager (field access not directly supported)."""
    # Skip this test as get_state_field is not implemented in the adapter
    pytest.skip("get_state_field method not implemented in StateManagerAdapter")


@pytest.mark.asyncio
async def test_update_state_field(
    state_manager_for_test, test_settings: Dict[str, Any]
):
    """Prueba funcionalidad de actualización de campos (no soportada directamente)."""
    # Skip this test as update_state_field is not implemented in the adapter
    pytest.skip("update_state_field method not implemented in StateManagerAdapter")


@pytest.mark.asyncio
async def test_list_user_sessions(
    state_manager_for_test, test_settings: Dict[str, Any]
):
    """Prueba la función get_conversations_by_user del StateManager."""
    # Datos de prueba
    user_id = test_settings["test_user_id"]
    conversation_id1 = str(uuid.uuid4())
    conversation_id2 = str(uuid.uuid4())

    # Crear y guardar conversaciones
    context1 = ConversationContext(
        conversation_id=conversation_id1,
        user_id=user_id,
        messages=[{"role": "user", "content": "session1 message"}],
    )
    context2 = ConversationContext(
        conversation_id=conversation_id2,
        user_id=user_id,
        messages=[{"role": "user", "content": "session2 message"}],
    )

    await state_manager_for_test.save_conversation(context1)
    await state_manager_for_test.save_conversation(context2)

    # Listar conversaciones del usuario
    conversations = await state_manager_for_test.get_conversations_by_user(user_id)

    # Verificar resultado
    assert (
        len(conversations) >= 2
    )  # Puede haber más conversaciones de pruebas anteriores
    conversation_ids = [c.conversation_id for c in conversations]
    assert conversation_id1 in conversation_ids
    assert conversation_id2 in conversation_ids
