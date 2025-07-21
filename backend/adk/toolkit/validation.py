"""
Validation Utilities for ADK
============================

Provides decorators and utilities for input/output validation
in agent operations.
"""

from typing import Any, Callable, Dict, Optional, Type, Union, List
from functools import wraps
import json
from datetime import datetime

from pydantic import BaseModel, ValidationError, create_model
from pydantic.fields import FieldInfo

from core.logging_config import get_logger
from ..core.exceptions import AgentValidationError

logger = get_logger(__name__)


class InputValidator:
    """Validates input data against schemas."""
    
    def __init__(self, schema: Union[Type[BaseModel], Dict[str, Any]]):
        """
        Initialize validator with a schema.
        
        Args:
            schema: Either a Pydantic model or a dictionary schema
        """
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            self.schema_model = schema
        else:
            # Create a Pydantic model from dictionary schema
            self.schema_model = self._create_model_from_dict(schema)
    
    def _create_model_from_dict(self, schema: Dict[str, Any]) -> Type[BaseModel]:
        """Create a Pydantic model from a dictionary schema."""
        fields = {}
        for field_name, field_info in schema.items():
            if isinstance(field_info, dict):
                field_type = field_info.get('type', Any)
                default = field_info.get('default', ...)
                description = field_info.get('description', '')
                fields[field_name] = (field_type, FieldInfo(default=default, description=description))
            else:
                fields[field_name] = (field_info, ...)
        
        return create_model('DynamicInputModel', **fields)
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data against schema.
        
        Returns:
            Validated and cleaned data
            
        Raises:
            AgentValidationError: If validation fails
        """
        try:
            validated = self.schema_model(**data)
            return validated.dict()
        except ValidationError as e:
            errors = []
            for error in e.errors():
                field = " -> ".join(str(loc) for loc in error['loc'])
                errors.append(f"{field}: {error['msg']}")
            
            raise AgentValidationError(
                f"Input validation failed: {'; '.join(errors)}",
                details={"errors": e.errors()}
            )


class OutputValidator:
    """Validates output data against schemas."""
    
    def __init__(self, schema: Union[Type[BaseModel], Dict[str, Any]]):
        """
        Initialize validator with a schema.
        
        Args:
            schema: Either a Pydantic model or a dictionary schema
        """
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            self.schema_model = schema
        else:
            self.schema_model = self._create_model_from_dict(schema)
    
    def _create_model_from_dict(self, schema: Dict[str, Any]) -> Type[BaseModel]:
        """Create a Pydantic model from a dictionary schema."""
        fields = {}
        for field_name, field_info in schema.items():
            if isinstance(field_info, dict):
                field_type = field_info.get('type', Any)
                default = field_info.get('default', ...)
                description = field_info.get('description', '')
                fields[field_name] = (field_type, FieldInfo(default=default, description=description))
            else:
                fields[field_name] = (field_info, ...)
        
        return create_model('DynamicOutputModel', **fields)
    
    def validate(self, data: Any) -> Any:
        """
        Validate output data against schema.
        
        Returns:
            Validated data (as model instance if schema is a model)
            
        Raises:
            AgentValidationError: If validation fails
        """
        try:
            if isinstance(data, dict):
                return self.schema_model(**data)
            else:
                # Try to parse if it's a model instance
                return self.schema_model.parse_obj(data)
        except ValidationError as e:
            errors = []
            for error in e.errors():
                field = " -> ".join(str(loc) for loc in error['loc'])
                errors.append(f"{field}: {error['msg']}")
            
            raise AgentValidationError(
                f"Output validation failed: {'; '.join(errors)}",
                details={"errors": e.errors()}
            )


class SchemaValidator:
    """General purpose schema validator with advanced features."""
    
    def __init__(self):
        self.custom_validators = {}
    
    def register_validator(
        self,
        field_type: str,
        validator_func: Callable[[Any], bool]
    ):
        """Register a custom validator for a field type."""
        self.custom_validators[field_type] = validator_func
    
    def validate_schema(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate data against a schema definition.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        for field, rules in schema.items():
            if field not in data and rules.get('required', False):
                return False, f"Required field '{field}' is missing"
            
            if field in data:
                value = data[field]
                
                # Type validation
                expected_type = rules.get('type')
                if expected_type and not self._check_type(value, expected_type):
                    return False, f"Field '{field}' must be of type {expected_type}"
                
                # Min/Max validation for numbers
                if isinstance(value, (int, float)):
                    min_val = rules.get('min')
                    max_val = rules.get('max')
                    if min_val is not None and value < min_val:
                        return False, f"Field '{field}' must be >= {min_val}"
                    if max_val is not None and value > max_val:
                        return False, f"Field '{field}' must be <= {max_val}"
                
                # Length validation for strings
                if isinstance(value, str):
                    min_len = rules.get('min_length')
                    max_len = rules.get('max_length')
                    if min_len is not None and len(value) < min_len:
                        return False, f"Field '{field}' must have at least {min_len} characters"
                    if max_len is not None and len(value) > max_len:
                        return False, f"Field '{field}' must have at most {max_len} characters"
                    
                    # Pattern validation
                    pattern = rules.get('pattern')
                    if pattern:
                        import re
                        if not re.match(pattern, value):
                            return False, f"Field '{field}' does not match required pattern"
                
                # Enum validation
                enum_values = rules.get('enum')
                if enum_values and value not in enum_values:
                    return False, f"Field '{field}' must be one of {enum_values}"
                
                # Custom validation
                custom_type = rules.get('custom_type')
                if custom_type and custom_type in self.custom_validators:
                    if not self.custom_validators[custom_type](value):
                        return False, f"Field '{field}' failed custom validation"
        
        return True, None
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type."""
        type_map = {
            'string': str,
            'integer': int,
            'float': float,
            'boolean': bool,
            'list': list,
            'dict': dict,
            'datetime': datetime
        }
        
        expected_python_type = type_map.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        
        return True


def validate_input(
    schema: Union[Type[BaseModel], Dict[str, Any]],
    allow_extra: bool = False
):
    """
    Decorator to validate function input.
    
    Args:
        schema: Pydantic model or dictionary schema
        allow_extra: Whether to allow extra fields
    
    Example:
        @validate_input(MyRequestSchema)
        async def process(data: dict):
            # data is now validated
            return result
    """
    def decorator(func: Callable) -> Callable:
        validator = InputValidator(schema)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Assume first argument is the data to validate
            if args:
                data = args[0]
                if isinstance(data, dict):
                    try:
                        validated_data = validator.validate(data)
                        # Replace first argument with validated data
                        args = (validated_data,) + args[1:]
                    except AgentValidationError as e:
                        logger.error(f"Input validation failed for {func.__name__}: {str(e)}")
                        raise
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if args:
                data = args[0]
                if isinstance(data, dict):
                    try:
                        validated_data = validator.validate(data)
                        args = (validated_data,) + args[1:]
                    except AgentValidationError as e:
                        logger.error(f"Input validation failed for {func.__name__}: {str(e)}")
                        raise
            
            return func(*args, **kwargs)
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def validate_output(
    schema: Union[Type[BaseModel], Dict[str, Any]]
):
    """
    Decorator to validate function output.
    
    Args:
        schema: Pydantic model or dictionary schema
    
    Example:
        @validate_output(MyResponseSchema)
        async def generate():
            # Generate response
            return response_data
    """
    def decorator(func: Callable) -> Callable:
        validator = OutputValidator(schema)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            try:
                validated_result = validator.validate(result)
                return validated_result
            except AgentValidationError as e:
                logger.error(f"Output validation failed for {func.__name__}: {str(e)}")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            try:
                validated_result = validator.validate(result)
                return validated_result
            except AgentValidationError as e:
                logger.error(f"Output validation failed for {func.__name__}: {str(e)}")
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Common validation schemas
class CommonSchemas:
    """Common validation schemas for reuse."""
    
    @staticmethod
    def pagination_schema() -> Dict[str, Any]:
        """Schema for pagination parameters."""
        return {
            'page': {'type': 'integer', 'min': 1, 'default': 1},
            'per_page': {'type': 'integer', 'min': 1, 'max': 100, 'default': 20},
            'sort_by': {'type': 'string', 'required': False},
            'sort_order': {'type': 'string', 'enum': ['asc', 'desc'], 'default': 'asc'}
        }
    
    @staticmethod
    def date_range_schema() -> Dict[str, Any]:
        """Schema for date range parameters."""
        return {
            'start_date': {'type': 'datetime', 'required': True},
            'end_date': {'type': 'datetime', 'required': True}
        }
    
    @staticmethod
    def search_schema() -> Dict[str, Any]:
        """Schema for search parameters."""
        return {
            'query': {'type': 'string', 'min_length': 1, 'max_length': 500},
            'filters': {'type': 'dict', 'required': False},
            'include_archived': {'type': 'boolean', 'default': False}
        }