"""
Enhanced Streaming Router v2 with ADK
=====================================

This module provides improved SSE streaming endpoints using the ADK patterns
for better reliability, monitoring, and performance.
"""

import asyncio
import json
import uuid
import time
from typing import AsyncGenerator, Dict, Any, Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field

from core.auth import get_current_user
from core.logging_config import get_logger
from core.metrics import (
    chat_sessions_total,
    chat_messages_total,
    stream_chunks_sent_total,
    stream_ttfb_seconds,
)

# Import ADK components
from adk.patterns import StreamingMixin, StreamEvent, StreamEventType
from adk.patterns.circuit_breaker import CircuitBreaker
from adk.patterns.retry import retry, CommonRetryPolicies
from adk.toolkit.monitoring import track_performance, MetricsCollector

# Import orchestrator
from agents.orchestrator.streaming_orchestrator import StreamingNGXNexusOrchestrator
from infrastructure.adapters.state_manager_adapter import state_manager_adapter
from core.settings import Settings

logger = get_logger(__name__)
settings = Settings()

# Create router
router = APIRouter(
    prefix="/v2/stream",
    tags=["stream-v2"],
    responses={
        401: {"description": "Unauthorized"},
        503: {"description": "Service Unavailable"}
    },
)

# Enhanced request model
class StreamChatRequest(BaseModel):
    """Enhanced chat request for streaming."""
    
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Streaming options
    stream_options: Dict[str, Any] = Field(
        default_factory=lambda: {
            "chunk_size": 50,
            "include_heartbeat": True,
            "heartbeat_interval": 30,
            "include_progress": True,
            "format": "sse"  # sse or json-lines
        }
    )
    
    # User preferences
    preferences: Dict[str, Any] = Field(
        default_factory=lambda: {
            "language": "es",
            "detail_level": "normal",
            "include_artifacts": True
        }
    )


class StreamingService(StreamingMixin):
    """
    Enhanced streaming service using ADK patterns.
    
    Provides reliable streaming with circuit breakers, retry logic,
    and comprehensive monitoring.
    """
    
    def __init__(self):
        super().__init__()
        self.orchestrator = None
        self._init_lock = asyncio.Lock()
        self.metrics = MetricsCollector("streaming_service")
        
        # Circuit breakers for different components
        self.orchestrator_cb = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60,
            name="orchestrator_streaming"
        )
        
        self.llm_cb = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30,
            name="llm_streaming"
        )
    
    async def get_orchestrator(self) -> StreamingNGXNexusOrchestrator:
        """Get or create orchestrator instance with proper initialization."""
        async with self._init_lock:
            if self.orchestrator is None:
                logger.info("Initializing StreamingNGXNexusOrchestrator")
                
                self.orchestrator = StreamingNGXNexusOrchestrator(
                    state_manager=state_manager_adapter,
                    a2a_server_url=settings.A2A_SERVER_URL,
                    use_optimized=True,
                    chunk_size=50,
                    chunk_delay=0.05,
                    use_real_streaming=True
                )
                
                logger.info("StreamingNGXNexusOrchestrator initialized")
            
            return self.orchestrator
    
    @track_performance(operation_name="stream_chat_response")
    async def stream_chat_response(
        self,
        request: StreamChatRequest,
        user: Dict[str, Any]
    ) -> AsyncGenerator[StreamEvent, None]:
        """
        Stream chat response with enhanced reliability.
        
        Uses ADK patterns for:
        - Circuit breaking on failures
        - Retry logic for transient errors
        - Structured event streaming
        - Performance monitoring
        """
        conversation_id = request.conversation_id or str(uuid.uuid4())
        start_time = time.time()
        
        # Record request
        self.metrics.record_request(0, success=True)
        chat_sessions_total.labels(type="streaming_v2", status="started").inc()
        
        try:
            # Get orchestrator with circuit breaker
            orchestrator = await self.orchestrator_cb.async_call(
                self.get_orchestrator
            )
            
            # Create async generator for orchestrator response
            async def orchestrator_generator():
                async for chunk in orchestrator.stream_response(
                    input_text=request.message,
                    user_id=user["id"],
                    session_id=conversation_id,
                    metadata={
                        **request.metadata,
                        "preferences": request.preferences,
                        "stream_options": request.stream_options
                    }
                ):
                    yield chunk
            
            # Stream with ADK patterns
            chunk_count = 0
            async for event in self.stream_response(
                generator=orchestrator_generator(),
                stream_id=conversation_id,
                include_heartbeat=request.stream_options.get("include_heartbeat", True),
                heartbeat_interval=request.stream_options.get("heartbeat_interval", 30),
                include_metadata=True
            ):
                # Track metrics
                if event.event_type == StreamEventType.DATA:
                    chunk_count += 1
                    stream_chunks_sent_total.inc()
                    
                    # Record TTFB on first chunk
                    if chunk_count == 1:
                        ttfb = time.time() - start_time
                        stream_ttfb_seconds.observe(ttfb)
                
                yield event
            
            # Record successful completion
            duration = time.time() - start_time
            self.metrics.record_request(duration, success=True)
            chat_sessions_total.labels(type="streaming_v2", status="completed").inc()
            
            logger.info(
                f"Stream completed: {chunk_count} chunks in {duration:.2f}s",
                extra={
                    "conversation_id": conversation_id,
                    "chunk_count": chunk_count,
                    "duration": duration
                }
            )
            
        except Exception as e:
            # Record error
            self.metrics.record_error(type(e).__name__)
            chat_sessions_total.labels(type="streaming_v2", status="error").inc()
            
            logger.error(
                f"Stream error: {str(e)}",
                extra={
                    "conversation_id": conversation_id,
                    "error_type": type(e).__name__
                },
                exc_info=True
            )
            
            # Yield error event
            yield StreamEvent(
                event_type=StreamEventType.ERROR,
                data={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "conversation_id": conversation_id,
                    "recoverable": self._is_recoverable_error(e)
                }
            )
    
    def _is_recoverable_error(self, error: Exception) -> bool:
        """Determine if error is recoverable."""
        recoverable_types = (
            ConnectionError,
            TimeoutError,
            asyncio.TimeoutError
        )
        return isinstance(error, recoverable_types)
    
    async def format_sse_response(
        self,
        events: AsyncGenerator[StreamEvent, None]
    ) -> AsyncGenerator[str, None]:
        """Format stream events as SSE."""
        async for event in events:
            # Convert ADK StreamEvent to SSE format
            yield event.to_sse()
    
    async def format_json_lines_response(
        self,
        events: AsyncGenerator[StreamEvent, None]
    ) -> AsyncGenerator[str, None]:
        """Format stream events as JSON lines."""
        async for event in events:
            # Convert ADK StreamEvent to JSON lines format
            yield event.to_json() + "\n"


# Global streaming service instance
_streaming_service = StreamingService()


@router.post("/chat", response_class=EventSourceResponse)
async def stream_chat_v2(
    request: StreamChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Enhanced streaming chat endpoint with ADK patterns.
    
    Features:
    - Circuit breaking for resilience
    - Retry logic for transient failures
    - Structured event streaming
    - Heartbeat support
    - Progress tracking
    - Multiple output formats
    
    Returns:
        EventSourceResponse with structured stream events
    """
    try:
        logger.info(
            f"Stream chat v2 request from user {current_user['id']}",
            extra={
                "user_id": current_user["id"],
                "message_length": len(request.message),
                "has_conversation_id": bool(request.conversation_id)
            }
        )
        
        # Generate event stream
        event_stream = _streaming_service.stream_chat_response(
            request=request,
            user=current_user
        )
        
        # Format based on requested format
        if request.stream_options.get("format") == "json-lines":
            formatted_stream = _streaming_service.format_json_lines_response(event_stream)
            return StreamingResponse(
                formatted_stream,
                media_type="application/x-ndjson"
            )
        else:
            # Default to SSE
            formatted_stream = _streaming_service.format_sse_response(event_stream)
            return EventSourceResponse(
                formatted_stream,
                media_type="text/event-stream"
            )
    
    except Exception as e:
        logger.error(f"Stream chat v2 error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Streaming error: {str(e)}"
        )


@router.get("/health")
async def stream_health_v2():
    """
    Enhanced health check for streaming service.
    
    Returns:
        Detailed health status including circuit breaker states
    """
    health_status = {
        "status": "healthy",
        "service": "stream-v2",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "sse_enabled": True,
            "json_lines_enabled": True,
            "circuit_breakers": True,
            "retry_logic": True,
            "heartbeat": True,
            "progress_tracking": True
        }
    }
    
    # Add circuit breaker status
    if _streaming_service.orchestrator_cb:
        health_status["circuit_breakers"] = {
            "orchestrator": _streaming_service.orchestrator_cb.get_stats(),
            "llm": _streaming_service.llm_cb.get_stats()
        }
    
    # Add metrics
    health_status["metrics"] = _streaming_service.metrics.get_metrics()
    
    return health_status


@router.get("/metrics")
async def stream_metrics_v2(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get detailed streaming metrics.
    
    Requires authentication. Returns comprehensive metrics about
    streaming performance and reliability.
    """
    return {
        "service_metrics": _streaming_service.metrics.get_metrics(),
        "circuit_breakers": {
            "orchestrator": _streaming_service.orchestrator_cb.get_stats(),
            "llm": _streaming_service.llm_cb.get_stats()
        },
        "active_streams": len(_streaming_service._active_streams),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/test")
async def test_streaming(
    message: str = Query(default="Test streaming message"),
    chunks: int = Query(default=10, ge=1, le=100),
    delay: float = Query(default=0.1, ge=0.01, le=1.0),
    include_error: bool = Query(default=False),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Test endpoint for streaming functionality.
    
    Useful for testing client implementations and debugging.
    """
    async def test_generator():
        for i in range(chunks):
            if include_error and i == chunks // 2:
                raise Exception("Test error in stream")
            
            yield {
                "chunk": i + 1,
                "total": chunks,
                "message": f"{message} - chunk {i + 1}/{chunks}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await asyncio.sleep(delay)
    
    # Create test stream
    async def create_test_stream():
        async for event in _streaming_service.stream_response(
            generator=test_generator(),
            stream_id=f"test_{uuid.uuid4()}",
            include_heartbeat=True,
            heartbeat_interval=5
        ):
            yield event.to_sse()
    
    return EventSourceResponse(
        create_test_stream(),
        media_type="text/event-stream"
    )