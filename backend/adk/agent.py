"""
Adaptador para Google ADK Agent.

Este módulo proporciona una implementación que utiliza la biblioteca oficial
de Google ADK en lugar de stubs locales.
"""

try:
    # Intentar importar la biblioteca oficial de Google ADK
    # NOTA: Hay un conflicto conocido entre pydantic 2.9.2 y mcp 1.5.0
    # que causa RuntimeError: Unable to apply constraint 'host_required'
    from google.adk.agent import Agent as GoogleADKAgent
    from google.adk.agent import Skill as GoogleADKSkill

    class Agent(GoogleADKAgent):
        """
        Implementación de Agent que utiliza la biblioteca oficial de Google ADK.

        Esta clase hereda directamente de google.adk.agent.Agent y proporciona
        compatibilidad con el sistema NGX Agents.
        """

        def __init__(self, toolkit=None, **kwargs):
            """
            Inicializa un agente ADK.

            Args:
                toolkit: Toolkit para el agente
                **kwargs: Argumentos adicionales para pasar a la clase base
            """
            super().__init__(toolkit=toolkit, **kwargs)

    class Skill(GoogleADKSkill):
        """
        Implementación de Skill que utiliza la biblioteca oficial de Google ADK.

        Esta clase hereda directamente de google.adk.agent.Skill y proporciona
        compatibilidad con el sistema NGX Agents.
        """

        def __init__(
            self,
            name: str,
            description: str,
            input_schema=None,
            output_schema=None,
            handler=None,
        ):
            """
            Inicializa una skill ADK.

            Args:
                name: Nombre de la skill
                description: Descripción de la skill
                input_schema: Esquema de entrada (opcional)
                output_schema: Esquema de salida (opcional)
                handler: Función que implementa la skill (opcional)
            """
            super().__init__(
                name=name,
                description=description,
                input_schema=input_schema,
                output_schema=output_schema,
                handler=handler,
            )

except (ImportError, RuntimeError, Exception) as e:
    # Fallback a stubs locales si la biblioteca oficial no está disponible
    import logging

    logger = logging.getLogger(__name__)
    logger.warning(
        f"No se pudo importar la biblioteca oficial de Google ADK: {str(e)}. Usando stubs locales."
    )

    class Agent:
        """Stub de Google ADK Agent para pruebas locales."""

        def __init__(self, toolkit=None, **kwargs):
            self.toolkit = toolkit
            # Atributos adicionales pueden inicializarse si es necesario

        async def run(self, *args, **kwargs):
            """Stub del método run."""
            return {}

    class Skill:
        """Stub de la clase Skill de Google ADK."""

        def __init__(
            self,
            name: str,
            description: str,
            input_schema=None,
            output_schema=None,
            handler=None,
            func=None,  # Alias para handler para compatibilidad
        ):
            self.name = name
            self.description = description
            self.input_schema = input_schema
            self.output_schema = output_schema
            # Usar func si se proporciona, de lo contrario usar handler
            self.handler = func if func is not None else handler

        async def __call__(self, *args, **kwargs):
            if self.handler:
                return await self.handler(*args, **kwargs)
            raise NotImplementedError("Skill handler no implementado")
