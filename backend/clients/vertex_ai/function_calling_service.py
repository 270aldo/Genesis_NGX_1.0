"""
Function Calling Service for Vertex AI Client.

This module handles function calling functionality,
providing structured interaction with AI models using function declarations.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

from core.logging_config import get_logger
from infrastructure.adapters.telemetry_adapter import (
    get_telemetry_adapter,
    measure_execution_time,
)

from .cache import CacheManager
from .connection import ConnectionPool
from .decorators import with_retries

logger = get_logger(__name__)
telemetry_adapter = get_telemetry_adapter()

try:
    from vertexai.generative_models import (
        FunctionDeclaration,
        GenerationConfig,
        GenerativeModel,
        Tool,
    )

    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False

    class GenerativeModel:
        pass

    class FunctionDeclaration:
        pass

    class Tool:
        pass

    class GenerationConfig:
        pass


class FunctionCallingService:
    """
    Service responsible for function calling with Vertex AI models.

    This service handles:
    - Function declaration and tool configuration
    - Structured function calls
    - Result parsing and validation
    - Error handling and retries
    """

    def __init__(
        self,
        model_name: str,
        cache_manager: CacheManager = None,
        connection_pool: ConnectionPool = None,
        **kwargs,
    ):
        """Initialize the function calling service."""
        self.model_name = model_name
        self.cache_manager = cache_manager
        self.connection_pool = connection_pool
        self.model = None
        self.stats = {
            "function_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "latency_ms": [],
        }

    async def initialize(self) -> bool:
        """Initialize the function calling model."""
        try:
            if not VERTEX_AI_AVAILABLE:
                logger.warning("Vertex AI not available - using mock mode")
                return False

            self.model = GenerativeModel(model_name=self.model_name)
            logger.info(
                f"Function calling service initialized with model: {self.model_name}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize function calling service: {e}")
            return False

    def _get_cache_key(
        self, prompt: str, functions: List[Dict[str, Any]], **kwargs
    ) -> str:
        """Generate cache key for function calling request."""
        import hashlib

        # Include function signatures in cache key
        functions_str = json.dumps(functions, sort_keys=True)
        content = f"{prompt}|{functions_str}|{self.model_name}"
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"function_call:{self.model_name}:{content_hash}"

    def _create_function_declarations(
        self, functions: List[Dict[str, Any]]
    ) -> List[FunctionDeclaration]:
        """Create function declarations from function specs."""
        declarations = []

        for func in functions:
            try:
                declaration = FunctionDeclaration(
                    name=func["name"],
                    description=func.get("description", ""),
                    parameters=func.get("parameters", {}),
                )
                declarations.append(declaration)
            except Exception as e:
                logger.warning(
                    f"Failed to create function declaration for {func.get('name', 'unknown')}: {e}"
                )

        return declarations

    def _parse_function_call_response(self, response) -> Dict[str, Any]:
        """Parse function call response from Vertex AI."""
        try:
            if not hasattr(response, "candidates") or not response.candidates:
                return {"type": "text", "content": str(response)}

            candidate = response.candidates[0]

            # Check for function calls
            if hasattr(candidate, "function_calls") and candidate.function_calls:
                function_call = candidate.function_calls[0]
                return {
                    "type": "function_call",
                    "function_name": function_call.name,
                    "arguments": dict(function_call.args),
                    "raw_response": str(response),
                }

            # Check for regular text content
            if hasattr(candidate, "content") and candidate.content:
                return {
                    "type": "text",
                    "content": (
                        candidate.content.parts[0].text
                        if candidate.content.parts
                        else str(candidate.content)
                    ),
                    "raw_response": str(response),
                }

            return {"type": "text", "content": str(response)}

        except Exception as e:
            logger.error(f"Error parsing function call response: {e}")
            return {"type": "error", "error": str(e), "raw_response": str(response)}

    @measure_execution_time("vertex_ai.function_calling.generate_with_functions")
    @with_retries(max_retries=3, base_delay=1.0, backoff_factor=2)
    async def generate_with_functions(
        self,
        prompt: str,
        functions: List[Dict[str, Any]],
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: Optional[int] = None,
        skip_cache: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate content with function calling capabilities.

        Args:
            prompt: Input prompt for the model
            functions: List of available functions
            system_instruction: System instruction (optional)
            temperature: Temperature for generation (0.0-1.0)
            max_output_tokens: Maximum output tokens limit
            skip_cache: If True, skip cache and always call API

        Returns:
            Dict[str, Any]: Response with function calls or text content
        """
        if not self.model:
            raise RuntimeError("Function calling service not initialized")

        self.stats["function_calls"] += 1

        # Generate cache key
        cache_key = self._get_cache_key(prompt, functions, temperature=temperature)

        # Try cache first (unless skipped)
        if not skip_cache and self.cache_manager:
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                self.stats["cache_hits"] += 1
                return cached_result

        self.stats["cache_misses"] += 1

        span_attributes = {
            "service.prompt_length": len(prompt),
            "service.function_count": len(functions),
            "service.temperature": temperature,
            "service.model_name": self.model_name,
        }

        span = telemetry_adapter.start_span(
            "FunctionCallingService.generate_with_functions", attributes=span_attributes
        )

        try:
            start_time = asyncio.get_event_loop().time()

            if VERTEX_AI_AVAILABLE:
                # Create function declarations
                function_declarations = self._create_function_declarations(functions)

                if not function_declarations:
                    raise ValueError("No valid function declarations created")

                # Create tools
                tools = [Tool(function_declarations=function_declarations)]

                # Create generation config
                generation_config = GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                )

                # Prepare content
                contents = [prompt]
                if system_instruction:
                    contents.insert(0, system_instruction)

                # Make API call
                response = await self.model.generate_content_async(
                    contents=contents,
                    generation_config=generation_config,
                    tools=tools,
                )

                # Parse response
                parsed_response = self._parse_function_call_response(response)

                result = {
                    **parsed_response,
                    "model_name": self.model_name,
                    "available_functions": [f["name"] for f in functions],
                    "usage": {
                        "prompt_tokens": getattr(response, "usage_metadata", {}).get(
                            "prompt_token_count", 0
                        ),
                        "completion_tokens": getattr(
                            response, "usage_metadata", {}
                        ).get("candidates_token_count", 0),
                    },
                    "timestamp": start_time,
                }

            else:
                # Mock function call response
                await asyncio.sleep(0.1)  # Simulate API delay

                # Randomly choose between function call and text response
                import random

                if random.random() < 0.7 and functions:  # 70% chance of function call
                    selected_function = random.choice(functions)
                    result = {
                        "type": "function_call",
                        "function_name": selected_function["name"],
                        "arguments": {"mock": "argument"},
                        "model_name": self.model_name,
                        "available_functions": [f["name"] for f in functions],
                        "usage": {
                            "prompt_tokens": len(prompt.split()),
                            "completion_tokens": 10,
                        },
                        "timestamp": start_time,
                    }
                else:
                    result = {
                        "type": "text",
                        "content": f"Mock response for: {prompt[:50]}...",
                        "model_name": self.model_name,
                        "available_functions": [f["name"] for f in functions],
                        "usage": {
                            "prompt_tokens": len(prompt.split()),
                            "completion_tokens": 10,
                        },
                        "timestamp": start_time,
                    }

            # Record latency
            latency = int((asyncio.get_event_loop().time() - start_time) * 1000)
            self.stats["latency_ms"].append(latency)
            self.stats["successful_calls"] += 1

            # Cache the result
            if not skip_cache and self.cache_manager:
                await self.cache_manager.set(cache_key, result)

            telemetry_adapter.record_counter(
                "vertex_ai_requests",
                1,
                {"model": self.model_name, "type": "function_calling"},
            )

            span.set_attribute("service.success", True)
            span.set_attribute("service.response_type", result["type"])

            return result

        except Exception as e:
            self.stats["failed_calls"] += 1
            logger.error(f"Error in function calling: {e}")

            telemetry_adapter.record_counter(
                "vertex_ai_errors",
                1,
                {
                    "model": self.model_name,
                    "type": "function_calling",
                    "error": str(type(e).__name__),
                },
            )

            span.set_attribute("service.success", False)
            span.set_attribute("service.error", str(e))

            raise

        finally:
            span.end()

    def validate_function_schema(self, function: Dict[str, Any]) -> bool:
        """
        Validate function schema for compatibility.

        Args:
            function: Function specification to validate

        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ["name", "description"]

        for field in required_fields:
            if field not in function:
                logger.warning(f"Function missing required field: {field}")
                return False

        # Validate parameters schema if present
        if "parameters" in function:
            parameters = function["parameters"]
            if not isinstance(parameters, dict):
                logger.warning("Function parameters must be a dictionary")
                return False

            # Check for OpenAPI-style schema structure
            if "type" not in parameters:
                logger.warning("Function parameters must include 'type' field")
                return False

        return True

    async def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        avg_latency = (
            sum(self.stats["latency_ms"]) / len(self.stats["latency_ms"])
            if self.stats["latency_ms"]
            else 0
        )
        success_rate = (
            (self.stats["successful_calls"] / self.stats["function_calls"]) * 100
            if self.stats["function_calls"] > 0
            else 0
        )

        return {
            "service": "function_calling",
            "model_name": self.model_name,
            "stats": {
                **self.stats,
                "avg_latency_ms": avg_latency,
                "success_rate_percent": success_rate,
            },
            "cache_stats": (
                await self.cache_manager.get_stats() if self.cache_manager else {}
            ),
        }
