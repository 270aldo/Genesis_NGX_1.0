#!/usr/bin/env python3
"""
Service Refactoring Script
==========================

Automates the migration of existing services to use new base classes,
reducing code duplication across the NGX agents ecosystem.
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import click
import difflib


class ServiceRefactorer:
    """Handles automated refactoring of services to use base classes."""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.stats = {
            "files_analyzed": 0,
            "files_refactored": 0,
            "lines_removed": 0,
            "errors": []
        }
    
    def analyze_service_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a service file to determine refactoring potential."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        analysis = {
            "file": str(file_path),
            "type": self._detect_service_type(content),
            "duplicate_methods": [],
            "lines_of_code": len(content.splitlines()),
            "can_refactor": False,
            "estimated_reduction": 0
        }
        
        # Parse AST to find methods
        try:
            tree = ast.parse(content)
            class_node = self._find_service_class(tree)
            
            if class_node:
                analysis["class_name"] = class_node.name
                analysis["methods"] = [node.name for node in class_node.body 
                                     if isinstance(node, ast.FunctionDef)]
                
                # Check for duplicate patterns
                if analysis["type"] == "data":
                    analysis["duplicate_methods"] = self._find_data_service_duplicates(analysis["methods"])
                elif analysis["type"] == "security":
                    analysis["duplicate_methods"] = self._find_security_service_duplicates(analysis["methods"])
                elif analysis["type"] == "integration":
                    analysis["duplicate_methods"] = self._find_integration_service_duplicates(analysis["methods"])
                
                # Calculate potential reduction
                if analysis["duplicate_methods"]:
                    analysis["can_refactor"] = True
                    analysis["estimated_reduction"] = len(analysis["duplicate_methods"]) * 30  # ~30 lines per method
                
        except Exception as e:
            analysis["parse_error"] = str(e)
        
        return analysis
    
    def generate_refactored_service(self, analysis: Dict[str, Any]) -> str:
        """Generate refactored service code using appropriate base class."""
        if not analysis.get("can_refactor"):
            return ""
        
        service_type = analysis["type"]
        class_name = analysis["class_name"]
        
        if service_type == "data":
            return self._generate_data_service(class_name, analysis)
        elif service_type == "security":
            return self._generate_security_service(class_name, analysis)
        elif service_type == "integration":
            return self._generate_integration_service(class_name, analysis)
        
        return ""
    
    def refactor_directory(self, directory: Path, pattern: str = "*_service.py") -> None:
        """Refactor all matching service files in a directory."""
        service_files = list(directory.rglob(pattern))
        
        click.echo(f"Found {len(service_files)} service files to analyze")
        
        for file_path in service_files:
            self.stats["files_analyzed"] += 1
            
            # Skip already refactored files
            if "_refactored" in str(file_path):
                continue
            
            click.echo(f"\nAnalyzing: {file_path}")
            analysis = self.analyze_service_file(file_path)
            
            if analysis["can_refactor"]:
                click.echo(f"  ✓ Can refactor (estimated {analysis['estimated_reduction']} lines reduction)")
                
                if not self.dry_run:
                    try:
                        # Generate refactored code
                        new_code = self.generate_refactored_service(analysis)
                        
                        # Save refactored version
                        new_path = file_path.with_name(file_path.stem + "_refactored.py")
                        with open(new_path, 'w') as f:
                            f.write(new_code)
                        
                        self.stats["files_refactored"] += 1
                        self.stats["lines_removed"] += analysis["estimated_reduction"]
                        
                        click.echo(f"  ✓ Refactored to: {new_path}")
                        
                    except Exception as e:
                        self.stats["errors"].append(f"{file_path}: {str(e)}")
                        click.echo(f"  ✗ Error: {str(e)}", err=True)
            else:
                click.echo(f"  - No refactoring needed")
    
    def show_diff(self, original_path: Path, refactored_path: Path) -> None:
        """Show diff between original and refactored file."""
        with open(original_path, 'r') as f:
            original = f.readlines()
        
        with open(refactored_path, 'r') as f:
            refactored = f.readlines()
        
        diff = difflib.unified_diff(
            original, refactored,
            fromfile=str(original_path),
            tofile=str(refactored_path),
            lineterm=''
        )
        
        click.echo('\n'.join(diff))
    
    # ==================== Private Methods ====================
    
    def _detect_service_type(self, content: str) -> str:
        """Detect type of service based on patterns in code."""
        content_lower = content.lower()
        
        # Check imports and class names
        if "supabase" in content_lower and ("save" in content_lower or "get" in content_lower):
            return "data"
        elif "encrypt" in content_lower or "compliance" in content_lower or "audit" in content_lower:
            return "security"
        elif "webhook" in content_lower or "external" in content_lower or "api" in content_lower:
            return "integration"
        
        return "unknown"
    
    def _find_service_class(self, tree: ast.AST) -> Optional[ast.ClassDef]:
        """Find the main service class in AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and "service" in node.name.lower():
                return node
        return None
    
    def _find_data_service_duplicates(self, methods: List[str]) -> List[str]:
        """Find methods that duplicate BaseDataService functionality."""
        duplicate_patterns = [
            "save", "get", "update", "delete", "list",
            "_save_to_database", "_get_from_database", "_update_cache",
            "_get_from_cache", "_is_cache_valid"
        ]
        
        return [m for m in methods if any(pattern in m for pattern in duplicate_patterns)]
    
    def _find_security_service_duplicates(self, methods: List[str]) -> List[str]:
        """Find methods that duplicate BaseSecurityService functionality."""
        duplicate_patterns = [
            "validate", "encrypt", "decrypt", "audit",
            "check_compliance", "sanitize", "_detect_pii"
        ]
        
        return [m for m in methods if any(pattern in m for pattern in duplicate_patterns)]
    
    def _find_integration_service_duplicates(self, methods: List[str]) -> List[str]:
        """Find methods that duplicate BaseIntegrationService functionality."""
        duplicate_patterns = [
            "sync", "fetch", "send", "handle_webhook",
            "_make_request", "_retry", "test_connection"
        ]
        
        return [m for m in methods if any(pattern in m for pattern in duplicate_patterns)]
    
    def _generate_data_service(self, class_name: str, analysis: Dict[str, Any]) -> str:
        """Generate refactored data service code."""
        # Extract service name for table
        table_name = class_name.lower().replace("dataservice", "").replace("service", "")
        
        return f'''"""
Refactored {class_name} using BaseDataService
{'=' * (len(class_name) + 35)}

Automatically refactored to use base class, reducing code duplication.
Original: {analysis["lines_of_code"]} lines → Refactored: ~{analysis["lines_of_code"] - analysis["estimated_reduction"]} lines
"""

from typing import Dict, Any, Optional
from agents.base.base_data_service import BaseDataService
from core.logging_config import get_logger

logger = get_logger(__name__)


class {class_name}(BaseDataService[Dict[str, Any]]):
    """Refactored {class_name} with automatic caching and error handling."""
    
    def __init__(self, **kwargs):
        super().__init__(
            table_name="{table_name}",
            cache_prefix="{table_name}",
            **kwargs
        )
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate data before storage."""
        # TODO: Implement validation logic
        required_fields = ["user_id"]  # Add your required fields
        return all(field in data for field in required_fields)
    
    def transform_for_storage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data for database storage."""
        # TODO: Implement transformation logic
        return data
    
    def transform_from_storage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data from database format."""
        # TODO: Implement transformation logic
        return data
    
    # Add any service-specific methods here
'''
    
    def _generate_security_service(self, class_name: str, analysis: Dict[str, Any]) -> str:
        """Generate refactored security service code."""
        return f'''"""
Refactored {class_name} using BaseSecurityService
{'=' * (len(class_name) + 37)}

Automatically refactored to use base class with built-in compliance checks.
"""

from typing import Set, List, Dict, Any
from agents.base.base_security_service import BaseSecurityService
from core.logging_config import get_logger

logger = get_logger(__name__)


class {class_name}(BaseSecurityService):
    """Refactored {class_name} with automatic compliance and audit logging."""
    
    def __init__(self, **kwargs):
        super().__init__(
            service_name="{class_name}",
            compliance_level="standard",  # or "hipaa", "gdpr"
            **kwargs
        )
    
    def get_sensitive_fields(self) -> Set[str]:
        """Define fields that need encryption."""
        # TODO: Add your sensitive fields
        return {{"ssn", "credit_card", "health_data"}}
    
    def validate_business_rules(self, data: Dict[str, Any]) -> List[str]:
        """Validate business-specific rules."""
        errors = []
        
        # TODO: Implement your business rules
        # Example:
        # if "age" in data and data["age"] < 18:
        #     errors.append("User must be 18 or older")
        
        return errors
'''
    
    def _generate_integration_service(self, class_name: str, analysis: Dict[str, Any]) -> str:
        """Generate refactored integration service code."""
        return f'''"""
Refactored {class_name} using BaseIntegrationService
{'=' * (len(class_name) + 40)}

Automatically refactored with retry logic and circuit breaker pattern.
"""

from typing import Dict, Any
from agents.base.base_integration_service import BaseIntegrationService, IntegrationType
from core.logging_config import get_logger

logger = get_logger(__name__)


class {class_name}(BaseIntegrationService):
    """Refactored {class_name} with automatic retry and circuit breaker."""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__(
            service_name="{class_name}",
            integration_type=IntegrationType.FITNESS,  # Change as needed
            base_url="https://api.example.com",  # TODO: Set actual base URL
            api_key=api_key,
            **kwargs
        )
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        return {{
            "X-API-Key": self.api_key
        }}
    
    def transform_request_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data before sending to external API."""
        # TODO: Implement transformation
        return data
    
    def transform_response_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data received from external API."""
        # TODO: Implement transformation
        return data
    
    def create_fallback_response(self, operation: str) -> Dict[str, Any]:
        """Create fallback response when API is unavailable."""
        return {{
            "success": False,
            "fallback": True,
            "operation": operation,
            "message": "Service temporarily unavailable"
        }}
'''


@click.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--pattern', default='*_service.py', help='File pattern to match')
@click.option('--dry-run/--no-dry-run', default=True, help='Perform dry run without making changes')
@click.option('--show-diff', is_flag=True, help='Show diff for refactored files')
def main(directory: str, pattern: str, dry_run: bool, show_diff: bool):
    """Refactor service files to use base classes."""
    refactorer = ServiceRefactorer(dry_run=dry_run)
    
    click.echo(f"{'DRY RUN MODE' if dry_run else 'REFACTORING MODE'}")
    click.echo("=" * 50)
    
    # Run refactoring
    refactorer.refactor_directory(Path(directory), pattern)
    
    # Show statistics
    click.echo("\n" + "=" * 50)
    click.echo("REFACTORING SUMMARY")
    click.echo("=" * 50)
    click.echo(f"Files analyzed: {refactorer.stats['files_analyzed']}")
    click.echo(f"Files refactored: {refactorer.stats['files_refactored']}")
    click.echo(f"Estimated lines removed: {refactorer.stats['lines_removed']}")
    
    if refactorer.stats['errors']:
        click.echo(f"\nErrors encountered: {len(refactorer.stats['errors'])}")
        for error in refactorer.stats['errors']:
            click.echo(f"  - {error}", err=True)
    
    if dry_run and refactorer.stats['files_analyzed'] > 0:
        click.echo("\nRun with --no-dry-run to apply changes")


if __name__ == '__main__':
    main()