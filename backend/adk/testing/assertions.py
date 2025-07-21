"""
Assertion Utilities for ADK Testing
==================================

Common assertions for testing ADK agents.
"""

from typing import Any, Dict, List, Optional, Union
import json

from ..core import AgentResponse
from ..patterns.streaming import StreamEvent, StreamEventType


def assert_valid_response(response: AgentResponse, check_content: bool = True):
    """
    Assert that an agent response is valid.
    
    Args:
        response: The response to validate
        check_content: Whether to check that content is non-empty
    
    Raises:
        AssertionError: If response is invalid
    """
    assert response is not None, "Response is None"
    assert isinstance(response, AgentResponse), f"Response is not AgentResponse, got {type(response)}"
    
    # Check required fields
    assert response.agent_id is not None, "Response missing agent_id"
    assert response.agent_name is not None, "Response missing agent_name"
    assert response.session_id is not None, "Response missing session_id"
    assert response.timestamp is not None, "Response missing timestamp"
    
    # Check success/error state
    if response.success:
        assert response.error is None, f"Successful response has error: {response.error}"
        if check_content:
            assert response.content is not None, "Successful response has no content"
    else:
        assert response.error is not None, "Failed response has no error message"
    
    # Check performance metrics
    assert response.processing_time >= 0, f"Invalid processing time: {response.processing_time}"
    
    if response.tokens_used is not None:
        assert response.tokens_used >= 0, f"Invalid tokens used: {response.tokens_used}"


def assert_response_contains(
    response: AgentResponse,
    expected: Union[str, List[str], Dict[str, Any]]
):
    """
    Assert that response content contains expected values.
    
    Args:
        response: The response to check
        expected: String, list of strings, or dict to look for
    
    Raises:
        AssertionError: If expected content not found
    """
    assert response.success, f"Response failed with error: {response.error}"
    
    content = response.content
    
    if isinstance(expected, str):
        # Check string content
        if isinstance(content, str):
            assert expected in content, f"Expected '{expected}' not found in content"
        else:
            content_str = json.dumps(content) if isinstance(content, dict) else str(content)
            assert expected in content_str, f"Expected '{expected}' not found in content"
    
    elif isinstance(expected, list):
        # Check multiple strings
        for exp in expected:
            assert_response_contains(response, exp)
    
    elif isinstance(expected, dict):
        # Check dict content
        assert isinstance(content, dict), f"Expected dict content, got {type(content)}"
        for key, value in expected.items():
            assert key in content, f"Expected key '{key}' not found in content"
            if value is not None:
                assert content[key] == value, f"Expected {key}={value}, got {key}={content[key]}"


def assert_streaming_response(
    events: List[StreamEvent],
    expected_types: Optional[List[StreamEventType]] = None,
    min_data_events: int = 1
):
    """
    Assert that streaming response is valid.
    
    Args:
        events: List of stream events
        expected_types: Expected event types in order (if specified)
        min_data_events: Minimum number of data events expected
    
    Raises:
        AssertionError: If streaming response is invalid
    """
    assert len(events) > 0, "No stream events received"
    
    # Check for required events
    event_types = [e.event_type for e in events]
    assert StreamEventType.START in event_types, "No START event in stream"
    assert StreamEventType.END in event_types, "No END event in stream"
    
    # Check order: START should be first, END should be last
    assert events[0].event_type == StreamEventType.START, "Stream doesn't start with START event"
    assert events[-1].event_type == StreamEventType.END, "Stream doesn't end with END event"
    
    # Count data events
    data_events = [e for e in events if e.event_type == StreamEventType.DATA]
    assert len(data_events) >= min_data_events, \
        f"Expected at least {min_data_events} data events, got {len(data_events)}"
    
    # Check expected types if provided
    if expected_types:
        assert event_types == expected_types, \
            f"Event types mismatch. Expected: {expected_types}, Got: {event_types}"
    
    # Check for errors
    error_events = [e for e in events if e.event_type == StreamEventType.ERROR]
    if error_events:
        raise AssertionError(f"Stream contained errors: {[e.data for e in error_events]}")
    
    # Validate event structure
    for event in events:
        assert event.timestamp is not None, f"Event missing timestamp: {event}"
        if event.sequence is not None:
            assert event.sequence > 0, f"Invalid sequence number: {event.sequence}"


def assert_metrics_valid(metrics: Dict[str, Any], agent_id: str):
    """
    Assert that agent metrics are valid.
    
    Args:
        metrics: Metrics dictionary
        agent_id: Expected agent ID
    
    Raises:
        AssertionError: If metrics are invalid
    """
    assert metrics is not None, "Metrics are None"
    assert isinstance(metrics, dict), f"Metrics should be dict, got {type(metrics)}"
    
    # Check required fields
    assert metrics.get("agent_id") == agent_id, \
        f"Wrong agent_id in metrics. Expected: {agent_id}, Got: {metrics.get('agent_id')}"
    
    # Check numeric fields
    numeric_fields = [
        "uptime_seconds", "request_count", "error_count",
        "error_rate", "average_duration"
    ]
    
    for field in numeric_fields:
        if field in metrics:
            value = metrics[field]
            assert isinstance(value, (int, float)), \
                f"Metric {field} should be numeric, got {type(value)}"
            assert value >= 0, f"Metric {field} should be non-negative, got {value}"
    
    # Check rates are between 0 and 1
    rate_fields = ["error_rate", "cache_hit_rate"]
    for field in rate_fields:
        if field in metrics:
            value = metrics[field]
            assert 0 <= value <= 1, \
                f"Rate metric {field} should be between 0 and 1, got {value}"


def assert_skill_result(
    result: Dict[str, Any],
    expected_keys: List[str],
    check_values: Optional[Dict[str, Any]] = None
):
    """
    Assert that skill execution result is valid.
    
    Args:
        result: Skill execution result
        expected_keys: Keys that should be present in result
        check_values: Optional dict of key-value pairs to check
    
    Raises:
        AssertionError: If result is invalid
    """
    assert result is not None, "Skill result is None"
    assert isinstance(result, dict), f"Skill result should be dict, got {type(result)}"
    
    # Check expected keys
    for key in expected_keys:
        assert key in result, f"Expected key '{key}' not found in skill result"
    
    # Check specific values if provided
    if check_values:
        for key, expected_value in check_values.items():
            assert key in result, f"Key '{key}' not found in skill result"
            actual_value = result[key]
            assert actual_value == expected_value, \
                f"Expected {key}={expected_value}, got {key}={actual_value}"


def assert_health_check_passed(health_status: Dict[str, Any]):
    """
    Assert that health check passed.
    
    Args:
        health_status: Health check result
    
    Raises:
        AssertionError: If health check failed
    """
    assert health_status is not None, "Health status is None"
    assert health_status.get("healthy") is True, \
        f"Health check failed: {health_status}"
    
    # Check individual checks if present
    if "checks" in health_status:
        checks = health_status["checks"]
        failed_checks = [k for k, v in checks.items() if not v]
        assert len(failed_checks) == 0, \
            f"Failed health checks: {failed_checks}"