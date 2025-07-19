"""
API Management Skill
===================

Manages API design and implementation.
"""

from typing import Dict, Any, List
from core.logging_config import get_logger

logger = get_logger(__name__)


class ApiManagementSkill:
    """Skill for API management and design."""
    
    def __init__(self, agent):
        """Initialize skill with parent agent reference."""
        self.agent = agent
        self.name = "api_management"
        self.description = "Manage API design and implementation"
    
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle API management request.
        
        Args:
            request: Contains api_type, operations, requirements
            
        Returns:
            API design and implementation guide
        """
        try:
            api_data = {
                "api_type": request.get("api_type", "REST"),
                "operations": request.get("operations", ["GET", "POST", "PUT", "DELETE"]),
                "requirements": request.get("requirements", {}),
                "resources": request.get("resources", []),
                "auth_method": request.get("auth_method", "jwt")
            }
            
            # Use agent's prompts system
            prompt = self.agent.prompts.get_api_management_prompt(api_data)
            
            # Generate API design
            response = await self.agent.generate_response(prompt)
            
            # Create API specification
            api_spec = self._create_api_specification(api_data)
            
            return {
                "success": True,
                "api_design": response,
                "skill_used": "api_management",
                "data": {
                    "api_specification": api_spec,
                    "security_setup": self._create_security_setup(api_data),
                    "rate_limiting": self._define_rate_limits(api_data),
                    "documentation_template": self._create_doc_template(api_data)
                },
                "metadata": {
                    "confidence": 0.91,
                    "api_standard": self._determine_standard(api_data),
                    "versioning_strategy": "semantic"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in API management: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "skill_used": "api_management"
            }
    
    def _create_api_specification(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create API specification structure."""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "NGX Integration API",
                "version": "1.0.0",
                "description": "API for system integrations"
            },
            "servers": [
                {"url": "https://api.ngx.com/v1", "description": "Production"},
                {"url": "https://staging-api.ngx.com/v1", "description": "Staging"}
            ],
            "paths": {},
            "components": {
                "securitySchemes": self._define_security_schemes(data),
                "schemas": {}
            }
        }
        
        # Add paths based on resources
        for resource in data.get("resources", ["users", "data"]):
            spec["paths"][f"/{resource}"] = self._create_resource_operations(
                resource, data["operations"]
            )
        
        return spec
    
    def _create_resource_operations(self, resource: str, operations: List[str]) -> Dict[str, Any]:
        """Create operations for a resource."""
        ops = {}
        
        if "GET" in operations:
            ops["get"] = {
                "summary": f"List {resource}",
                "operationId": f"list{resource.capitalize()}",
                "responses": {
                    "200": {"description": "Success"},
                    "401": {"description": "Unauthorized"}
                }
            }
        
        if "POST" in operations:
            ops["post"] = {
                "summary": f"Create {resource}",
                "operationId": f"create{resource.capitalize()}",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{resource.capitalize()}"}
                        }
                    }
                },
                "responses": {
                    "201": {"description": "Created"},
                    "400": {"description": "Bad Request"}
                }
            }
        
        return ops
    
    def _define_security_schemes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Define security schemes for API."""
        schemes = {}
        auth_method = data.get("auth_method", "jwt")
        
        if auth_method == "jwt":
            schemes["bearerAuth"] = {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        elif auth_method == "oauth2":
            schemes["oauth2"] = {
                "type": "oauth2",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": "https://auth.ngx.com/oauth/authorize",
                        "tokenUrl": "https://auth.ngx.com/oauth/token",
                        "scopes": {
                            "read": "Read access",
                            "write": "Write access"
                        }
                    }
                }
            }
        else:
            schemes["apiKey"] = {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key"
            }
        
        return schemes
    
    def _create_security_setup(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create security setup for API."""
        return {
            "authentication": data.get("auth_method", "jwt"),
            "encryption": "TLS 1.3",
            "cors": {
                "enabled": True,
                "allowed_origins": ["https://*.ngx.com"],
                "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
            },
            "headers": {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block"
            }
        }
    
    def _define_rate_limits(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Define rate limiting rules."""
        return {
            "default": {
                "requests_per_minute": 60,
                "requests_per_hour": 1000
            },
            "authenticated": {
                "requests_per_minute": 300,
                "requests_per_hour": 10000
            },
            "burst": {
                "enabled": True,
                "multiplier": 2,
                "duration_seconds": 10
            }
        }
    
    def _create_doc_template(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Create documentation template."""
        return {
            "overview": "API overview and getting started guide",
            "authentication": "Authentication methods and examples",
            "endpoints": "Detailed endpoint documentation",
            "examples": "Code examples in multiple languages",
            "errors": "Error codes and handling",
            "changelog": "Version history and migration guides"
        }
    
    def _determine_standard(self, data: Dict[str, Any]) -> str:
        """Determine API standard to follow."""
        api_type = data.get("api_type", "REST")
        
        if api_type == "REST":
            return "OpenAPI 3.0"
        elif api_type == "GraphQL":
            return "GraphQL Schema"
        elif api_type == "gRPC":
            return "Protocol Buffers"
        else:
            return "Custom"