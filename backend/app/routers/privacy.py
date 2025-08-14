"""
Privacy and Compliance API Endpoints
====================================

GDPR and HIPAA compliant endpoints for data subject rights,
consent management, and privacy controls.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from core.audit import AuditEventType, get_audit_logger
from core.compliance import (
    ConsentStatus,
    ConsentType,
    DataCategory,
    LegalBasis,
    get_compliance_controller,
)
from core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/privacy", tags=["privacy", "compliance"])


# Pydantic models for API requests/responses
class ConsentRequest(BaseModel):
    """Request model for granting consent."""

    consent_type: str = Field(
        ..., description="Type of consent (data_processing, marketing, etc.)"
    )
    purpose: str = Field(..., description="Purpose of data processing")
    data_categories: List[str] = Field(
        ..., description="Categories of data to be processed"
    )
    legal_basis: str = Field(
        default="consent", description="Legal basis for processing"
    )
    expires_in_days: Optional[int] = Field(
        None, description="Consent expiration in days"
    )


class ConsentResponse(BaseModel):
    """Response model for consent operations."""

    consent_id: str
    status: str
    granted_at: str
    expires_at: Optional[str] = None
    message: str


class ConsentWithdrawalRequest(BaseModel):
    """Request model for withdrawing consent."""

    consent_id: str
    reason: Optional[str] = None


class DataExportRequest(BaseModel):
    """Request model for data export."""

    format: str = Field(default="json", description="Export format (json, csv, xml)")
    include_metadata: bool = Field(
        default=True, description="Include processing metadata"
    )
    include_audit_log: bool = Field(default=False, description="Include audit trail")


class DataDeletionRequest(BaseModel):
    """Request model for data deletion."""

    reason: str = Field(default="user_request", description="Reason for deletion")
    confirm_deletion: bool = Field(..., description="Confirmation of deletion request")
    retain_legal_basis: bool = Field(
        default=True, description="Retain legally required data"
    )


class DataRectificationRequest(BaseModel):
    """Request model for data rectification."""

    field_updates: Dict[str, Any] = Field(..., description="Fields to update")
    reason: str = Field(
        default="user_correction", description="Reason for rectification"
    )


class ProcessingRestrictionRequest(BaseModel):
    """Request model for processing restriction."""

    restriction_reason: str = Field(..., description="Reason for restriction")
    data_categories: List[str] = Field(..., description="Data categories to restrict")


# Dependency to get current user (mock implementation)
async def get_current_user(request: Request) -> Dict[str, Any]:
    """Get current user from request. Mock implementation."""
    # In real implementation, this would extract user from JWT token
    user_id = request.headers.get("X-User-ID", "test_user")
    ip_address = request.client.host if request.client else None

    return {
        "id": user_id,
        "ip_address": ip_address,
        "user_agent": request.headers.get("User-Agent"),
    }


@router.post("/consent", response_model=ConsentResponse)
async def grant_consent(
    request: ConsentRequest, current_user: Dict[str, Any] = Depends(get_current_user)
) -> ConsentResponse:
    """
    Grant user consent for data processing.

    This endpoint allows users to grant consent for specific types of data processing
    in compliance with GDPR Article 7.
    """
    try:
        compliance_controller = get_compliance_controller()
        audit_logger = get_audit_logger()

        # Validate consent type
        try:
            consent_type = ConsentType(request.consent_type)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid consent type: {request.consent_type}"
            )

        # Validate legal basis
        try:
            legal_basis = LegalBasis(request.legal_basis)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid legal basis: {request.legal_basis}"
            )

        # Validate data categories
        try:
            data_categories = [DataCategory(cat) for cat in request.data_categories]
        except ValueError as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid data category: {str(e)}"
            )

        # Grant consent
        consent_id = await compliance_controller.consent_manager.grant_consent(
            user_id=current_user["id"],
            consent_type=consent_type,
            legal_basis=legal_basis,
            purpose=request.purpose,
            data_categories=data_categories,
            expires_in_days=request.expires_in_days,
        )

        # Calculate expiration date
        expires_at = None
        if request.expires_in_days:
            expires_at = (
                datetime.now(timezone.utc) + timedelta(days=request.expires_in_days)
            ).isoformat()

        # Log API access
        await audit_logger.log_event(
            event_type=AuditEventType.API_REQUEST,
            action="Consent granted via API",
            user_id=current_user["id"],
            ip_address=current_user["ip_address"],
            resource="privacy/consent",
            details={
                "consent_id": consent_id,
                "consent_type": request.consent_type,
                "purpose": request.purpose,
            },
        )

        return ConsentResponse(
            consent_id=consent_id,
            status="granted",
            granted_at=datetime.now(timezone.utc).isoformat(),
            expires_at=expires_at,
            message="Consent granted successfully",
        )

    except Exception as e:
        logger.error(f"Error granting consent: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/consent")
async def withdraw_consent(
    request: ConsentWithdrawalRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Withdraw user consent.

    This endpoint allows users to withdraw previously granted consent
    in compliance with GDPR Article 7(3).
    """
    try:
        compliance_controller = get_compliance_controller()
        audit_logger = get_audit_logger()

        # Withdraw consent
        success = await compliance_controller.consent_manager.withdraw_consent(
            user_id=current_user["id"],
            consent_id=request.consent_id,
            reason=request.reason,
        )

        if not success:
            raise HTTPException(
                status_code=404, detail="Consent not found or already withdrawn"
            )

        # Log API access
        await audit_logger.log_event(
            event_type=AuditEventType.API_REQUEST,
            action="Consent withdrawn via API",
            user_id=current_user["id"],
            ip_address=current_user["ip_address"],
            resource="privacy/consent",
            details={"consent_id": request.consent_id, "reason": request.reason},
        )

        return {
            "message": "Consent withdrawn successfully",
            "consent_id": request.consent_id,
            "withdrawn_at": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error withdrawing consent: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/consent")
async def get_consent_status(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get user's current consent status.

    This endpoint provides users with a complete overview of their
    current consent status for all data processing activities.
    """
    try:
        compliance_controller = get_compliance_controller()
        audit_logger = get_audit_logger()

        # Get user consents
        consents = await compliance_controller.consent_manager.get_user_consents(
            user_id=current_user["id"]
        )

        # Format response
        consent_status = {
            "user_id": current_user["id"],
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "total_consents": len(consents),
            "active_consents": [],
            "withdrawn_consents": [],
            "expired_consents": [],
        }

        for consent in consents:
            consent_data = consent.to_dict()

            if consent.status == ConsentStatus.GRANTED:
                consent_status["active_consents"].append(consent_data)
            elif consent.status == ConsentStatus.WITHDRAWN:
                consent_status["withdrawn_consents"].append(consent_data)
            elif consent.status == ConsentStatus.EXPIRED:
                consent_status["expired_consents"].append(consent_data)

        # Log API access
        await audit_logger.log_event(
            event_type=AuditEventType.API_REQUEST,
            action="Consent status retrieved via API",
            user_id=current_user["id"],
            ip_address=current_user["ip_address"],
            resource="privacy/consent",
            details={
                "total_consents": len(consents),
                "active_consents": len(consent_status["active_consents"]),
            },
        )

        return consent_status

    except Exception as e:
        logger.error(f"Error retrieving consent status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/export-my-data")
async def export_user_data(
    request: DataExportRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Export user's personal data (GDPR Article 20 - Right to data portability).

    This endpoint allows users to request a complete export of their personal data
    in a structured, machine-readable format.
    """
    try:
        compliance_controller = get_compliance_controller()
        audit_logger = get_audit_logger()

        # Export data
        exported_data = (
            await compliance_controller.data_subject_rights.request_data_export(
                user_id=current_user["id"],
                format_type=request.format,
                include_metadata=request.include_metadata,
            )
        )

        # Add audit log if requested
        if request.include_audit_log:
            audit_events = await audit_logger.get_user_activity(
                user_id=current_user["id"], limit=1000
            )
            exported_data["audit_log"] = [event.to_dict() for event in audit_events]

        # Log API access
        await audit_logger.log_event(
            event_type=AuditEventType.DATA_EXPORT,
            action="Data export requested via API",
            user_id=current_user["id"],
            ip_address=current_user["ip_address"],
            resource="privacy/export-my-data",
            details={
                "format": request.format,
                "include_metadata": request.include_metadata,
                "include_audit_log": request.include_audit_log,
                "data_size": len(str(exported_data)),
            },
        )

        return {
            "message": "Data export completed successfully",
            "export_id": exported_data.get("export_id", "unknown"),
            "export_timestamp": exported_data.get("export_timestamp"),
            "format": request.format,
            "data": exported_data,
        }

    except Exception as e:
        logger.error(f"Error exporting user data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/delete-my-data")
async def delete_user_data(
    request: DataDeletionRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Delete user's personal data (GDPR Article 17 - Right to be forgotten).

    This endpoint allows users to request deletion of their personal data
    while respecting legal retention requirements.
    """
    try:
        if not request.confirm_deletion:
            raise HTTPException(
                status_code=400, detail="Deletion confirmation required"
            )

        compliance_controller = get_compliance_controller()
        audit_logger = get_audit_logger()

        # Process deletion request
        deletion_summary = (
            await compliance_controller.data_subject_rights.request_data_deletion(
                user_id=current_user["id"],
                reason=request.reason,
                retain_legal_basis=request.retain_legal_basis,
            )
        )

        # Log API access
        await audit_logger.log_event(
            event_type=AuditEventType.DATA_DELETION,
            action="Data deletion requested via API",
            user_id=current_user["id"],
            ip_address=current_user["ip_address"],
            resource="privacy/delete-my-data",
            details={
                "reason": request.reason,
                "retain_legal_basis": request.retain_legal_basis,
                "deleted_categories": deletion_summary.get(
                    "deleted_data_categories", []
                ),
                "retained_categories": deletion_summary.get(
                    "retained_data_categories", []
                ),
            },
        )

        return {
            "message": "Data deletion request processed successfully",
            "deletion_summary": deletion_summary,
            "notice": (
                "Some data may be retained due to legal obligations"
                if request.retain_legal_basis
                else None
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing data deletion: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/rectify-my-data")
async def rectify_user_data(
    request: DataRectificationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Rectify user's personal data (GDPR Article 16 - Right to rectification).

    This endpoint allows users to correct inaccurate or incomplete personal data.
    """
    try:
        compliance_controller = get_compliance_controller()
        audit_logger = get_audit_logger()

        # Process rectification request
        rectification_summary = (
            await compliance_controller.data_subject_rights.rectify_data(
                user_id=current_user["id"],
                field_updates=request.field_updates,
                reason=request.reason,
            )
        )

        # Log API access
        await audit_logger.log_event(
            event_type=AuditEventType.DATA_UPDATE,
            action="Data rectification requested via API",
            user_id=current_user["id"],
            ip_address=current_user["ip_address"],
            resource="privacy/rectify-my-data",
            details={
                "reason": request.reason,
                "fields_updated": rectification_summary.get("fields_updated", []),
                "fields_encrypted": rectification_summary.get("fields_encrypted", []),
            },
        )

        return {
            "message": "Data rectification completed successfully",
            "rectification_summary": rectification_summary,
        }

    except Exception as e:
        logger.error(f"Error rectifying user data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/restrict-processing")
async def restrict_data_processing(
    request: ProcessingRestrictionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Restrict processing of user's data (GDPR Article 18 - Right to restriction).

    This endpoint allows users to restrict the processing of their personal data
    under certain circumstances.
    """
    try:
        compliance_controller = get_compliance_controller()
        audit_logger = get_audit_logger()

        # Validate data categories
        try:
            data_categories = [DataCategory(cat) for cat in request.data_categories]
        except ValueError as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid data category: {str(e)}"
            )

        # Process restriction request
        success = await compliance_controller.data_subject_rights.restrict_processing(
            user_id=current_user["id"],
            restriction_reason=request.restriction_reason,
            affected_categories=data_categories,
        )

        if not success:
            raise HTTPException(
                status_code=400, detail="Unable to apply processing restriction"
            )

        # Log API access
        await audit_logger.log_event(
            event_type=AuditEventType.API_REQUEST,
            action="Processing restriction requested via API",
            user_id=current_user["id"],
            ip_address=current_user["ip_address"],
            resource="privacy/restrict-processing",
            details={
                "restriction_reason": request.restriction_reason,
                "affected_categories": request.data_categories,
            },
        )

        return {
            "message": "Processing restriction applied successfully",
            "restriction_reason": request.restriction_reason,
            "affected_categories": request.data_categories,
            "applied_at": datetime.now(timezone.utc).isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying processing restriction: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/compliance-status")
async def get_compliance_status(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get user's compliance status and data processing summary.

    This endpoint provides users with an overview of how their data
    is being processed and the compliance status.
    """
    try:
        compliance_controller = get_compliance_controller()
        audit_logger = get_audit_logger()

        # Generate compliance report for user
        compliance_report = await compliance_controller.generate_compliance_report(
            user_id=current_user["id"]
        )

        # Log API access
        await audit_logger.log_event(
            event_type=AuditEventType.API_REQUEST,
            action="Compliance status retrieved via API",
            user_id=current_user["id"],
            ip_address=current_user["ip_address"],
            resource="privacy/compliance-status",
        )

        return {
            "message": "Compliance status retrieved successfully",
            "compliance_report": compliance_report,
        }

    except Exception as e:
        logger.error(f"Error retrieving compliance status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/privacy-policy")
async def get_privacy_policy() -> Dict[str, Any]:
    """
    Get the current privacy policy.

    This endpoint returns the organization's privacy policy
    including data processing practices and user rights.
    """
    try:
        # In a real implementation, this would load from a database or file
        privacy_policy = {
            "version": "1.0",
            "effective_date": "2025-01-01",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "data_controller": {
                "name": "NGX Agents",
                "contact": "privacy@ngxagents.com",
                "address": "123 Privacy Street, Data City, DC 12345",
            },
            "data_processing_purposes": [
                "Providing fitness and nutrition coaching services",
                "Improving service quality through analytics",
                "Communication and customer support",
                "Legal compliance and safety",
            ],
            "data_categories_collected": [
                "Identity data (name, email, phone)",
                "Health and fitness data",
                "Usage and behavioral data",
                "Communication data",
            ],
            "legal_basis": [
                "User consent (GDPR Article 6.1.a)",
                "Contract performance (GDPR Article 6.1.b)",
                "Legal obligations (GDPR Article 6.1.c)",
            ],
            "user_rights": [
                "Right to access (Article 15)",
                "Right to rectification (Article 16)",
                "Right to erasure (Article 17)",
                "Right to restrict processing (Article 18)",
                "Right to data portability (Article 20)",
                "Right to object (Article 21)",
            ],
            "data_retention": {
                "account_data": "Until account deletion + 30 days",
                "health_data": "7 years (HIPAA requirement)",
                "marketing_data": "Until consent withdrawn + 30 days",
                "audit_logs": "6 years (compliance requirement)",
            },
            "third_party_sharing": [
                "Service providers (cloud hosting, analytics)",
                "Legal authorities (when required by law)",
                "Business partners (with explicit consent)",
            ],
            "security_measures": [
                "AES-256 encryption for data at rest",
                "TLS 1.3 for data in transit",
                "Regular security audits and penetration testing",
                "Access controls and audit logging",
                "GDPR and HIPAA compliance programs",
            ],
            "contact_information": {
                "privacy_officer": "privacy@ngxagents.com",
                "data_protection_officer": "dpo@ngxagents.com",
                "support": "support@ngxagents.com",
            },
        }

        return {
            "privacy_policy": privacy_policy,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Error retrieving privacy policy: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/data-processing-activities")
async def get_data_processing_activities(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get list of current data processing activities for the user.

    This endpoint provides transparency about how user data
    is currently being processed.
    """
    try:
        audit_logger = get_audit_logger()

        # Get recent data access events for user
        recent_activity = await audit_logger.get_user_activity(
            user_id=current_user["id"], limit=50
        )

        # Categorize processing activities
        processing_activities = {
            "user_id": current_user["id"],
            "report_timestamp": datetime.now(timezone.utc).isoformat(),
            "current_processing_activities": [
                {
                    "activity": "Health coaching recommendations",
                    "purpose": "Providing personalized fitness and nutrition advice",
                    "data_categories": ["health_data", "behavioral_data"],
                    "legal_basis": "consent",
                    "frequency": "daily",
                },
                {
                    "activity": "Progress tracking",
                    "purpose": "Monitoring user fitness and health progress",
                    "data_categories": ["health_data", "biometric_data"],
                    "legal_basis": "contract",
                    "frequency": "continuous",
                },
                {
                    "activity": "Service improvement",
                    "purpose": "Analyzing usage patterns to improve services",
                    "data_categories": ["behavioral_data"],
                    "legal_basis": "legitimate_interests",
                    "frequency": "weekly",
                },
            ],
            "recent_access_events": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "activity": event.action,
                    "resource": event.resource,
                }
                for event in recent_activity[:10]
            ],
        }

        # Log API access
        await audit_logger.log_event(
            event_type=AuditEventType.API_REQUEST,
            action="Data processing activities retrieved via API",
            user_id=current_user["id"],
            ip_address=current_user["ip_address"],
            resource="privacy/data-processing-activities",
        )

        return processing_activities

    except Exception as e:
        logger.error(f"Error retrieving data processing activities: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
