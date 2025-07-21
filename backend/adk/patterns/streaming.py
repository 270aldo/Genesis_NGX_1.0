"""
Streaming Pattern for ADK
========================

Provides utilities and mixins for implementing streaming responses
in agents, supporting both SSE and WebSocket protocols.
"""

from typing import AsyncGenerator, Any, Dict, Optional, Callable, List, Union
from abc import ABC, abstractmethod
import asyncio
import json
import time
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps

from core.logging_config import get_logger
from ..core.exceptions import AgentExecutionError

logger = get_logger(__name__)


class StreamEventType(str, Enum):
    """Types of streaming events."""
    START = "start"
    DATA = "data"
    ERROR = "error"
    END = "end"
    HEARTBEAT = "heartbeat"
    METADATA = "metadata"
    PROGRESS = "progress"


@dataclass
class StreamEvent:
    """Represents a single event in a stream."""
    
    event_type: StreamEventType
    data: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
    sequence: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_sse(self) -> str:
        """Convert to Server-Sent Events format."""
        lines = []
        
        # Event type
        lines.append(f"event: {self.event_type.value}")
        
        # Data
        if isinstance(self.data, str):
            lines.append(f"data: {self.data}")
        else:
            lines.append(f"data: {json.dumps(self.data)}")
        
        # ID (sequence number)
        if self.sequence is not None:
            lines.append(f"id: {self.sequence}")
        
        # Empty line to end event
        lines.append("")
        
        return "\n".join(lines) + "\n"
    
    def to_json(self) -> str:
        """Convert to JSON format."""
        return json.dumps({
            "type": self.event_type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "sequence": self.sequence,
            "metadata": self.metadata
        })


class StreamProcessor(ABC):
    """Base class for stream processors."""
    
    @abstractmethod
    async def process(self, chunk: Any) -> Any:
        """Process a single chunk of data."""
        pass


class ChunkAggregator:
    """Aggregates streaming chunks into complete responses."""
    
    def __init__(self, buffer_size: int = 100):
        self.buffer_size = buffer_size
        self.chunks: List[Any] = []
        self.metadata: Dict[str, Any] = {}
    
    def add_chunk(self, chunk: Any):
        """Add a chunk to the aggregator."""
        self.chunks.append(chunk)
        
        # Maintain buffer size
        if len(self.chunks) > self.buffer_size:
            self.chunks.pop(0)
    
    def get_aggregated(self) -> str:
        """Get aggregated result as string."""
        if all(isinstance(chunk, str) for chunk in self.chunks):
            return "".join(self.chunks)
        else:
            return json.dumps(self.chunks)
    
    def clear(self):
        """Clear the aggregator."""
        self.chunks.clear()
        self.metadata.clear()


class StreamingMixin:
    """
    Mixin to add streaming capabilities to agents.
    
    This mixin provides:
    - Stream generation and management
    - Error handling for streams
    - Progress tracking
    - Heartbeat support
    - Stream transformation
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stream_sequence = 0
        self._active_streams: Dict[str, bool] = {}
    
    async def stream_response(
        self,
        generator: AsyncGenerator[Any, None],
        stream_id: Optional[str] = None,
        transform: Optional[Callable[[Any], Any]] = None,
        include_heartbeat: bool = True,
        heartbeat_interval: float = 30.0,
        include_metadata: bool = True
    ) -> AsyncGenerator[StreamEvent, None]:
        """
        Stream response with proper event formatting.
        
        Args:
            generator: Async generator producing chunks
            stream_id: Unique identifier for the stream
            transform: Optional transformation function for chunks
            include_heartbeat: Whether to send heartbeat events
            heartbeat_interval: Seconds between heartbeats
            include_metadata: Whether to include metadata events
        
        Yields:
            StreamEvent objects
        """
        stream_id = stream_id or f"stream_{int(time.time() * 1000)}"
        self._active_streams[stream_id] = True
        
        try:
            # Send start event
            yield StreamEvent(
                event_type=StreamEventType.START,
                data={"stream_id": stream_id, "started_at": datetime.utcnow().isoformat()},
                sequence=self._get_next_sequence()
            )
            
            # Setup heartbeat if enabled
            heartbeat_task = None
            if include_heartbeat:
                heartbeat_queue = asyncio.Queue()
                heartbeat_task = asyncio.create_task(
                    self._heartbeat_generator(
                        stream_id,
                        heartbeat_interval,
                        heartbeat_queue
                    )
                )
            
            # Stream data
            chunk_count = 0
            async for chunk in generator:
                # Check if stream is still active
                if not self._active_streams.get(stream_id, False):
                    logger.info(f"Stream {stream_id} cancelled")
                    break
                
                # Transform chunk if needed
                if transform:
                    chunk = transform(chunk)
                
                # Yield data event
                yield StreamEvent(
                    event_type=StreamEventType.DATA,
                    data=chunk,
                    sequence=self._get_next_sequence(),
                    metadata={"chunk_index": chunk_count}
                )
                chunk_count += 1
                
                # Check for heartbeat
                if include_heartbeat:
                    try:
                        heartbeat = heartbeat_queue.get_nowait()
                        yield heartbeat
                    except asyncio.QueueEmpty:
                        pass
                
                # Yield control to prevent blocking
                await asyncio.sleep(0)
            
            # Send metadata if enabled
            if include_metadata:
                yield StreamEvent(
                    event_type=StreamEventType.METADATA,
                    data={
                        "total_chunks": chunk_count,
                        "duration": f"{time.time() - int(stream_id.split('_')[1]) / 1000:.2f}s"
                    },
                    sequence=self._get_next_sequence()
                )
            
            # Send end event
            yield StreamEvent(
                event_type=StreamEventType.END,
                data={"stream_id": stream_id, "ended_at": datetime.utcnow().isoformat()},
                sequence=self._get_next_sequence()
            )
            
        except Exception as e:
            # Send error event
            yield StreamEvent(
                event_type=StreamEventType.ERROR,
                data={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "stream_id": stream_id
                },
                sequence=self._get_next_sequence()
            )
            raise
            
        finally:
            # Cleanup
            self._active_streams.pop(stream_id, None)
            if heartbeat_task:
                heartbeat_task.cancel()
    
    async def _heartbeat_generator(
        self,
        stream_id: str,
        interval: float,
        queue: asyncio.Queue
    ):
        """Generate heartbeat events at regular intervals."""
        while self._active_streams.get(stream_id, False):
            await asyncio.sleep(interval)
            if self._active_streams.get(stream_id, False):
                event = StreamEvent(
                    event_type=StreamEventType.HEARTBEAT,
                    data={"stream_id": stream_id, "timestamp": datetime.utcnow().isoformat()},
                    sequence=self._get_next_sequence()
                )
                await queue.put(event)
    
    def _get_next_sequence(self) -> int:
        """Get next sequence number for events."""
        self._stream_sequence += 1
        return self._stream_sequence
    
    def cancel_stream(self, stream_id: str) -> bool:
        """Cancel an active stream."""
        if stream_id in self._active_streams:
            self._active_streams[stream_id] = False
            logger.info(f"Stream {stream_id} cancelled")
            return True
        return False
    
    def format_stream_chunk(
        self,
        content: Any,
        chunk_type: str = "content"
    ) -> Dict[str, Any]:
        """Format a chunk for streaming."""
        return {
            "type": chunk_type,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def stream_with_progress(
        self,
        total_steps: int,
        generator: AsyncGenerator[Any, None],
        stream_id: Optional[str] = None
    ) -> AsyncGenerator[StreamEvent, None]:
        """
        Stream with progress tracking.
        
        Args:
            total_steps: Total number of steps expected
            generator: Async generator producing chunks
            stream_id: Unique identifier for the stream
        
        Yields:
            StreamEvent objects including progress updates
        """
        stream_id = stream_id or f"stream_{int(time.time() * 1000)}"
        current_step = 0
        
        async for event in self.stream_response(generator, stream_id):
            yield event
            
            # Add progress events
            if event.event_type == StreamEventType.DATA:
                current_step += 1
                if current_step % max(1, total_steps // 10) == 0:  # Progress every 10%
                    progress = (current_step / total_steps) * 100
                    yield StreamEvent(
                        event_type=StreamEventType.PROGRESS,
                        data={
                            "current": current_step,
                            "total": total_steps,
                            "percentage": round(progress, 2)
                        },
                        sequence=self._get_next_sequence()
                    )


class StreamTransformer:
    """Transforms stream data between different formats."""
    
    @staticmethod
    def to_sse(stream: AsyncGenerator[StreamEvent, None]) -> AsyncGenerator[str, None]:
        """Convert stream events to SSE format."""
        async for event in stream:
            yield event.to_sse()
    
    @staticmethod
    def to_json_lines(stream: AsyncGenerator[StreamEvent, None]) -> AsyncGenerator[str, None]:
        """Convert stream events to JSON lines format."""
        async for event in stream:
            yield event.to_json() + "\n"
    
    @staticmethod
    def filter_by_type(
        stream: AsyncGenerator[StreamEvent, None],
        event_types: List[StreamEventType]
    ) -> AsyncGenerator[StreamEvent, None]:
        """Filter stream events by type."""
        async for event in stream:
            if event.event_type in event_types:
                yield event


class BufferedStreamProcessor:
    """Processes stream data with buffering for better performance."""
    
    def __init__(
        self,
        buffer_size: int = 10,
        flush_interval: float = 1.0
    ):
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self.buffer: List[Any] = []
        self.last_flush = time.time()
    
    async def process_stream(
        self,
        stream: AsyncGenerator[Any, None],
        processor: Callable[[List[Any]], Any]
    ) -> AsyncGenerator[Any, None]:
        """
        Process stream with buffering.
        
        Args:
            stream: Input stream
            processor: Function to process buffered data
        
        Yields:
            Processed results
        """
        try:
            async for item in stream:
                self.buffer.append(item)
                
                # Check if we should flush
                should_flush = (
                    len(self.buffer) >= self.buffer_size or
                    time.time() - self.last_flush >= self.flush_interval
                )
                
                if should_flush:
                    if self.buffer:
                        result = processor(self.buffer)
                        yield result
                        self.buffer.clear()
                        self.last_flush = time.time()
            
            # Final flush
            if self.buffer:
                result = processor(self.buffer)
                yield result
                
        finally:
            self.buffer.clear()


# Convenience decorators
def streamable(
    chunk_size: int = 100,
    include_progress: bool = True
):
    """
    Decorator to make a function streamable.
    
    Args:
        chunk_size: Size of chunks to yield
        include_progress: Whether to include progress events
    
    Example:
        @streamable(chunk_size=50)
        async def generate_report(data):
            for i in range(0, len(data), 50):
                chunk = process_chunk(data[i:i+50])
                yield chunk
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Create generator from function
            if asyncio.iscoroutinefunction(func):
                generator = func(self, *args, **kwargs)
            else:
                # Convert sync to async generator
                async def async_gen():
                    for item in func(self, *args, **kwargs):
                        yield item
                generator = async_gen()
            
            # Use streaming mixin if available
            if hasattr(self, 'stream_response'):
                async for event in self.stream_response(generator):
                    yield event
            else:
                # Fallback to simple streaming
                async for chunk in generator:
                    yield chunk
        
        return wrapper
    
    return decorator