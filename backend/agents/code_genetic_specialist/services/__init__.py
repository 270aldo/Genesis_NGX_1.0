"""
CODE Agent Services
===================

Export specialized services for genetic data management.
"""

from .genetic_security_service import GeneticSecurityService
from .consent_management_service import ConsentManagementService

__all__ = [
    "GeneticSecurityService",
    "ConsentManagementService"
]