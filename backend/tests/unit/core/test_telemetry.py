"""
Unit tests for telemetry module in core.telemetry.

Tests cover initialization, shutdown, tracing, metrics, and instrumentation
with proper mocking of OpenTelemetry dependencies.
"""

from unittest.mock import Mock, patch

import pytest

import core.telemetry


class TestTelemetryInitialization:
    """Test telemetry initialization scenarios."""

    @pytest.fixture(autouse=True)
    def reset_globals(self):
        """Reset global variables before each test."""

        core.telemetry._tracer_provider = None
        core.telemetry._meter_provider = None
        yield
        core.telemetry._tracer_provider = None
        core.telemetry._meter_provider = None

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        with patch("core.telemetry.settings") as mock:
            mock.APP_VERSION = "1.0.0"
            mock.ENVIRONMENT = "development"
            mock.GCP_PROJECT_ID = "test-project"
            yield mock

    @pytest.fixture
    def mock_otel_modules(self):
        """Mock OpenTelemetry modules."""
        # Create individual mocks
        mock_tracer_provider = Mock()
        mock_meter_provider = Mock()
        mock_resource = Mock()
        mock_resource.create.return_value = Mock()
        mock_batch_span_processor = Mock()
        mock_periodic_reader = Mock()
        mock_trace = Mock()
        mock_metrics = Mock()
        mock_httpx_instrumentor = Mock()
        mock_logging_instrumentor = Mock()
        mock_aiohttp_instrumentor = Mock()

        # Return mock that includes all required methods
        mock_httpx_instrumentor.return_value.instrument.return_value = None
        mock_logging_instrumentor.return_value.instrument.return_value = None
        mock_aiohttp_instrumentor.return_value.instrument.return_value = None

        with patch.multiple(
            "core.telemetry",
            TracerProvider=mock_tracer_provider,
            MeterProvider=mock_meter_provider,
            Resource=mock_resource,
            BatchSpanProcessor=mock_batch_span_processor,
            PeriodicExportingMetricReader=mock_periodic_reader,
            trace=mock_trace,
            metrics=mock_metrics,
            HTTPXClientInstrumentor=mock_httpx_instrumentor,
            LoggingInstrumentor=mock_logging_instrumentor,
            AioHttpClientInstrumentor=mock_aiohttp_instrumentor,
        ):
            yield {
                "TracerProvider": mock_tracer_provider,
                "MeterProvider": mock_meter_provider,
                "Resource": mock_resource,
                "BatchSpanProcessor": mock_batch_span_processor,
                "PeriodicExportingMetricReader": mock_periodic_reader,
                "trace": mock_trace,
                "metrics": mock_metrics,
                "HTTPXClientInstrumentor": mock_httpx_instrumentor,
                "LoggingInstrumentor": mock_logging_instrumentor,
                "AioHttpClientInstrumentor": mock_aiohttp_instrumentor,
            }

    def test_initialize_telemetry_development_environment(
        self, mock_settings, mock_otel_modules
    ):
        """Test initialization in development environment."""
        from core.telemetry import initialize_telemetry

        mock_settings.ENVIRONMENT = "development"

        # Mock console exporters
        with (
            patch(
                "opentelemetry.sdk.trace.export.ConsoleSpanExporter"
            ) as mock_console_span,
            patch(
                "opentelemetry.sdk.metrics.export.ConsoleMetricExporter"
            ) as mock_console_metric,
        ):
            initialize_telemetry()

            # Verify Resource creation
            mock_otel_modules["Resource"].create.assert_called_once()
            resource_attrs = mock_otel_modules["Resource"].create.call_args[0][0]
            assert resource_attrs["service.name"] == "ngx-agents"
            assert resource_attrs["deployment.environment"] == "development"

            # Verify console exporters were used
            mock_console_span.assert_called_once()
            mock_console_metric.assert_called_once()

            # Verify instrumentors were called
            mock_otel_modules["HTTPXClientInstrumentor"].assert_called()
            mock_otel_modules["LoggingInstrumentor"].assert_called()
            mock_otel_modules["AioHttpClientInstrumentor"].assert_called()

    def test_initialize_telemetry_production_environment(
        self, mock_settings, mock_otel_modules
    ):
        """Test initialization in production environment with cloud exporters."""
        from core.telemetry import initialize_telemetry

        mock_settings.ENVIRONMENT = "production"
        mock_settings.GCP_PROJECT_ID = "prod-project"

        # Mock cloud exporters using core.telemetry references
        with (
            patch("core.telemetry.CloudTraceSpanExporter") as mock_cloud_trace,
            patch(
                "core.telemetry.CloudMonitoringMetricExporter"
            ) as mock_cloud_monitoring,
        ):
            initialize_telemetry()

            # Verify cloud exporters were configured
            mock_cloud_trace.assert_called_once_with(project_id="prod-project")
            mock_cloud_monitoring.assert_called_once_with(
                project_id="prod-project", prefix="ngx_agents"
            )

    def test_initialize_telemetry_with_missing_cloud_exporters(
        self, mock_settings, mock_otel_modules
    ):
        """Test fallback to console exporters when cloud exporters unavailable."""
        from core.telemetry import initialize_telemetry

        mock_settings.ENVIRONMENT = "production"

        # Simulate missing cloud exporters
        with (
            patch("core.telemetry.CloudTraceSpanExporter", None),
            patch("core.telemetry.CloudMonitoringMetricExporter", None),
            patch(
                "opentelemetry.sdk.trace.export.ConsoleSpanExporter"
            ) as mock_console_span,
            patch(
                "opentelemetry.sdk.metrics.export.ConsoleMetricExporter"
            ) as mock_console_metric,
        ):
            initialize_telemetry()

            # Should fall back to console exporters
            mock_console_span.assert_called_once()
            mock_console_metric.assert_called_once()

    def test_initialize_telemetry_multiple_calls(
        self, mock_settings, mock_otel_modules
    ):
        """Test multiple initialization calls."""
        from core.telemetry import initialize_telemetry

        with (
            patch("opentelemetry.sdk.trace.export.ConsoleSpanExporter"),
            patch("opentelemetry.sdk.metrics.export.ConsoleMetricExporter"),
        ):
            # First call
            initialize_telemetry()

            # Second call should create new providers
            initialize_telemetry()

            # Verify providers were created twice
            assert mock_otel_modules["TracerProvider"].call_count == 2
            assert mock_otel_modules["MeterProvider"].call_count == 2


class TestTelemetryShutdown:
    """Test telemetry shutdown scenarios."""

    @pytest.fixture
    def mock_providers(self):
        """Mock tracer and meter providers."""
        tracer_provider = Mock()
        meter_provider = Mock()
        with (
            patch.object(core.telemetry, "_tracer_provider", tracer_provider),
            patch.object(core.telemetry, "_meter_provider", meter_provider),
        ):
            yield tracer_provider, meter_provider

    def test_shutdown_telemetry_after_initialization(self, mock_providers):
        """Test shutdown after initialization."""
        from core.telemetry import shutdown_telemetry

        tracer_provider, meter_provider = mock_providers

        shutdown_telemetry()

        # Verify shutdown was called on both providers
        tracer_provider.shutdown.assert_called_once()
        meter_provider.shutdown.assert_called_once()

    def test_shutdown_telemetry_before_initialization(self):
        """Test shutdown before initialization."""
        from core.telemetry import shutdown_telemetry

        # Should not raise errors
        shutdown_telemetry()

    def test_shutdown_telemetry_multiple_calls(self, mock_providers):
        """Test multiple shutdown calls."""
        from core.telemetry import shutdown_telemetry

        tracer_provider, meter_provider = mock_providers

        # Multiple calls should be safe
        shutdown_telemetry()
        shutdown_telemetry()

        # Current implementation calls shutdown every time (not optimized)
        assert tracer_provider.shutdown.call_count == 2
        assert meter_provider.shutdown.call_count == 2


class TestProviderAccess:
    """Test tracer and meter provider access."""

    def test_get_tracer(self):
        """Test getting a tracer."""
        from core.telemetry import get_tracer

        with patch("core.telemetry.trace") as mock_trace:
            mock_trace.get_tracer.return_value = Mock()

            tracer = get_tracer("test_component")

            mock_trace.get_tracer.assert_called_once_with("test_component")
            assert tracer is not None

    def test_get_meter(self):
        """Test getting a meter."""
        from core.telemetry import get_meter

        with patch("core.telemetry.metrics") as mock_metrics:
            mock_metrics.get_meter.return_value = Mock()

            meter = get_meter("test_component")

            mock_metrics.get_meter.assert_called_once_with("test_component")
            assert meter is not None


class TestTraceContextPropagation:
    """Test distributed tracing context management."""

    @pytest.fixture
    def mock_propagator(self):
        """Mock trace context propagator."""
        with patch("core.telemetry._propagator") as mock:
            yield mock

    def test_extract_trace_context(self, mock_propagator):
        """Test extracting trace context from headers."""
        from core.telemetry import extract_trace_context

        headers = {"traceparent": "00-trace-id-span-id-01"}
        mock_context = Mock()
        mock_propagator.extract.return_value = mock_context

        result = extract_trace_context(headers)

        mock_propagator.extract.assert_called_once_with(carrier=headers)
        assert result == mock_context

    def test_inject_trace_context(self, mock_propagator):
        """Test injecting trace context into headers."""
        from core.telemetry import inject_trace_context

        headers = {}
        inject_trace_context(headers)

        mock_propagator.inject.assert_called_once_with(carrier=headers)


class TestManualInstrumentation:
    """Test manual span and event creation."""

    @pytest.fixture
    def mock_trace(self):
        """Mock trace module."""
        with patch("core.telemetry.trace") as mock:
            mock.SpanKind = Mock()
            mock.SpanKind.INTERNAL = "INTERNAL"
            yield mock

    def test_create_span_with_attributes(self, mock_trace):
        """Test creating a span with attributes."""
        from core.telemetry import create_span

        mock_tracer = Mock()
        mock_span = Mock()
        mock_trace.get_tracer.return_value = mock_tracer
        mock_tracer.start_span.return_value = mock_span

        attributes = {"key": "value"}
        span = create_span("test_span", attributes=attributes)

        from unittest.mock import ANY

        mock_trace.get_tracer.assert_called_once_with("ngx_agents.manual")
        mock_tracer.start_span.assert_called_once_with(
            name="test_span", attributes=attributes, kind=ANY
        )
        assert span == mock_span

    def test_add_span_event_to_active_span(self, mock_trace):
        """Test adding event to active span."""
        from core.telemetry import add_span_event

        mock_span = Mock()
        mock_trace.get_current_span.return_value = mock_span

        add_span_event("test_event", {"attr": "value"})

        mock_span.add_event.assert_called_once_with(
            name="test_event", attributes={"attr": "value"}
        )

    def test_add_span_event_without_active_span(self, mock_trace):
        """Test adding event without active span."""
        from core.telemetry import add_span_event

        mock_trace.get_current_span.return_value = None

        # Should not raise error
        add_span_event("test_event")

    def test_set_span_attribute_on_active_span(self, mock_trace):
        """Test setting attribute on active span."""
        from core.telemetry import set_span_attribute

        mock_span = Mock()
        mock_trace.get_current_span.return_value = mock_span

        set_span_attribute("key", "value")

        mock_span.set_attribute.assert_called_once_with("key", "value")

    def test_record_exception_on_active_span(self, mock_trace):
        """Test recording exception on active span."""
        from core.telemetry import record_exception

        mock_span = Mock()
        mock_trace.get_current_span.return_value = mock_span
        mock_trace.Status.return_value = Mock()
        mock_trace.StatusCode.ERROR = "ERROR"

        exception = ValueError("test error")
        record_exception(exception, {"context": "test"})

        mock_span.record_exception.assert_called_once_with(
            exception, attributes={"context": "test"}
        )
        mock_span.set_status.assert_called_once()


class TestCurrentSpanAccess:
    """Test current span/trace ID extraction."""

    @pytest.fixture
    def mock_trace(self):
        """Mock trace module."""
        with patch("core.telemetry.trace") as mock:
            yield mock

    def test_get_current_trace_id_with_active_span(self, mock_trace):
        """Test getting trace ID with active span."""
        from core.telemetry import get_current_trace_id

        mock_span = Mock()
        mock_context = Mock()
        mock_context.trace_id = 0x12345678901234567890123456789012
        mock_span.get_span_context.return_value = mock_context
        mock_trace.get_current_span.return_value = mock_span

        trace_id = get_current_trace_id()

        assert trace_id == "12345678901234567890123456789012"

    def test_get_current_trace_id_without_active_span(self, mock_trace):
        """Test getting trace ID without active span."""
        from core.telemetry import get_current_trace_id

        mock_trace.get_current_span.return_value = None

        trace_id = get_current_trace_id()

        assert trace_id is None

    def test_get_current_span_id_with_active_span(self, mock_trace):
        """Test getting span ID with active span."""
        from core.telemetry import get_current_span_id

        mock_span = Mock()
        mock_context = Mock()
        mock_context.span_id = 0x1234567890123456
        mock_span.get_span_context.return_value = mock_context
        mock_trace.get_current_span.return_value = mock_span

        span_id = get_current_span_id()

        assert span_id == "1234567890123456"


class TestFastAPIInstrumentation:
    """Test FastAPI integration."""

    @pytest.fixture
    def mock_instrumentor(self):
        """Mock FastAPI instrumentor."""
        with patch("core.telemetry.FastAPIInstrumentor") as mock:
            yield mock

    @pytest.fixture
    def mock_providers(self):
        """Mock providers for instrumentation."""
        tracer_provider = Mock()
        meter_provider = Mock()
        with (
            patch.object(core.telemetry, "_tracer_provider", tracer_provider),
            patch.object(core.telemetry, "_meter_provider", meter_provider),
        ):
            yield tracer_provider, meter_provider

    def test_instrument_fastapi_after_initialization(
        self, mock_instrumentor, mock_providers
    ):
        """Test instrumenting FastAPI after telemetry init."""
        from core.telemetry import instrument_fastapi

        app = Mock()
        tracer_provider, meter_provider = mock_providers

        instrument_fastapi(app)

        mock_instrumentor.instrument_app.assert_called_once_with(
            app,
            tracer_provider=tracer_provider,
            excluded_urls="/health,/metrics",
            meter_provider=meter_provider,
        )

    def test_instrument_fastapi_before_initialization(self, mock_instrumentor):
        """Test instrumenting FastAPI before telemetry init."""
        from core.telemetry import instrument_fastapi

        app = Mock()

        # Should work with None providers
        instrument_fastapi(app)

        mock_instrumentor.instrument_app.assert_called_once()


class TestErrorHandling:
    """Test error scenarios and exception handling."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        with patch("core.telemetry.settings") as mock:
            mock.APP_VERSION = "1.0.0"
            mock.ENVIRONMENT = "development"
            mock.GCP_PROJECT_ID = "test-project"
            yield mock

    def test_shutdown_with_provider_errors(self):
        """Test shutdown when providers raise errors."""
        from core.telemetry import shutdown_telemetry

        mock_tracer = Mock()
        mock_tracer.shutdown.side_effect = Exception("Shutdown error")
        mock_meter = Mock()

        with (
            patch.object(core.telemetry, "_tracer_provider", mock_tracer),
            patch.object(core.telemetry, "_meter_provider", mock_meter),
        ):
            # Current implementation does not handle errors, so it should raise
            with pytest.raises(Exception, match="Shutdown error"):
                shutdown_telemetry()

            # Tracer shutdown should have been called
            mock_tracer.shutdown.assert_called_once()
            # Meter shutdown should not be called due to exception
            mock_meter.shutdown.assert_not_called()

    def test_record_exception_with_invalid_span(self):
        """Test recording exception with invalid span context."""
        from core.telemetry import record_exception

        with patch("core.telemetry.trace") as mock_trace:
            mock_span = Mock()
            # Simulate span without context
            mock_span.get_span_context.return_value = None
            mock_trace.get_current_span.return_value = mock_span

            # Should not raise error
            record_exception(ValueError("test"))


# Helper to ensure module import works
