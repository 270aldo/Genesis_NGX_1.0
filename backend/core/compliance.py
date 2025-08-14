"""
GDPR and HIPAA Compliance Management System
==========================================

Comprehensive compliance controls including consent management,
data subject rights, data minimization, and privacy controls.
"""

import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from core.audit import AuditEventType, get_audit_logger
from core.logging_config import get_logger
from core.security.encryption_service import (
    ComplianceFieldEncryption,
    get_encryption_service,
)

logger = get_logger(__name__)


class ConsentType(Enum):
    """Types of user consent."""

    DATA_PROCESSING = "data_processing"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    THIRD_PARTY_SHARING = "third_party_sharing"
    MEDICAL_DATA = "medical_data"
    BIOMETRIC_DATA = "biometric_data"
    LOCATION_DATA = "location_data"
    BEHAVIORAL_TRACKING = "behavioral_tracking"


class ConsentStatus(Enum):
    """Consent status values."""

    GRANTED = "granted"
    WITHDRAWN = "withdrawn"
    PENDING = "pending"
    EXPIRED = "expired"


class LegalBasis(Enum):
    """GDPR legal basis for processing."""

    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"


class DataCategory(Enum):
    """Categories of personal data."""

    BASIC_IDENTITY = "basic_identity"  # Name, email, phone
    SENSITIVE_IDENTITY = "sensitive_identity"  # SSN, government ID
    HEALTH_DATA = "health_data"  # Medical records, health metrics
    BIOMETRIC_DATA = "biometric_data"  # Fingerprints, facial recognition
    FINANCIAL_DATA = "financial_data"  # Payment info, bank details
    LOCATION_DATA = "location_data"  # GPS, address information
    BEHAVIORAL_DATA = "behavioral_data"  # Usage patterns, preferences
    COMMUNICATION_DATA = "communication_data"  # Messages, call logs


@dataclass
class ConsentRecord:
    """Represents a user consent record."""

    consent_id: str
    user_id: str
    consent_type: ConsentType
    status: ConsentStatus
    legal_basis: LegalBasis
    purpose: str
    data_categories: List[DataCategory]
    granted_at: Optional[datetime]
    withdrawn_at: Optional[datetime]
    expires_at: Optional[datetime]
    version: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result["consent_type"] = self.consent_type.value
        result["status"] = self.status.value
        result["legal_basis"] = self.legal_basis.value
        result["data_categories"] = [cat.value for cat in self.data_categories]
        if self.granted_at:
            result["granted_at"] = self.granted_at.isoformat()
        if self.withdrawn_at:
            result["withdrawn_at"] = self.withdrawn_at.isoformat()
        if self.expires_at:
            result["expires_at"] = self.expires_at.isoformat()
        return result


@dataclass
class DataProcessingRecord:
    """Record of data processing activity."""

    processing_id: str
    user_id: str
    data_categories: List[DataCategory]
    purpose: str
    legal_basis: LegalBasis
    processing_timestamp: datetime
    retention_period: str
    data_location: str
    third_party_recipients: List[str]
    security_measures: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result["data_categories"] = [cat.value for cat in self.data_categories]
        result["legal_basis"] = self.legal_basis.value
        result["processing_timestamp"] = self.processing_timestamp.isoformat()
        return result


class ConsentManager:
    """Manages user consent for GDPR compliance."""

    def __init__(self):
        self.encryption = get_encryption_service()
        self.audit_logger = get_audit_logger()
        self._consent_records: Dict[str, List[ConsentRecord]] = {}

    async def grant_consent(
        self,
        user_id: str,
        consent_type: ConsentType,
        legal_basis: LegalBasis,
        purpose: str,
        data_categories: List[DataCategory],
        expires_in_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Grant user consent.

        Args:
            user_id: ID of the user granting consent
            consent_type: Type of consent being granted
            legal_basis: Legal basis for processing
            purpose: Purpose for data processing
            data_categories: Categories of data to be processed
            expires_in_days: Optional expiration period
            metadata: Additional metadata

        Returns:
            Consent ID
        """
        consent_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        expires_at = None
        if expires_in_days:
            expires_at = now + timedelta(days=expires_in_days)

        consent_record = ConsentRecord(
            consent_id=consent_id,
            user_id=user_id,
            consent_type=consent_type,
            status=ConsentStatus.GRANTED,
            legal_basis=legal_basis,
            purpose=purpose,
            data_categories=data_categories,
            granted_at=now,
            withdrawn_at=None,
            expires_at=expires_at,
            version="1.0",
            metadata=metadata or {},
        )

        # Store consent record
        if user_id not in self._consent_records:
            self._consent_records[user_id] = []

        self._consent_records[user_id].append(consent_record)

        # Audit log
        await self.audit_logger.log_consent_event(
            user_id=user_id,
            consent_type=consent_type.value,
            granted=True,
            details={
                "consent_id": consent_id,
                "purpose": purpose,
                "legal_basis": legal_basis.value,
                "data_categories": [cat.value for cat in data_categories],
                "expires_at": expires_at.isoformat() if expires_at else None,
            },
        )

        logger.info(f"Consent granted for user {user_id}: {consent_type.value}")
        return consent_id

    async def withdraw_consent(
        self, user_id: str, consent_id: str, reason: Optional[str] = None
    ) -> bool:
        """
        Withdraw user consent.

        Args:
            user_id: ID of the user withdrawing consent
            consent_id: ID of the consent to withdraw
            reason: Optional reason for withdrawal

        Returns:
            True if consent was successfully withdrawn
        """
        user_consents = self._consent_records.get(user_id, [])

        for consent in user_consents:
            if consent.consent_id == consent_id:
                if consent.status == ConsentStatus.GRANTED:
                    consent.status = ConsentStatus.WITHDRAWN
                    consent.withdrawn_at = datetime.now(timezone.utc)

                    if reason:
                        consent.metadata["withdrawal_reason"] = reason

                    # Audit log
                    await self.audit_logger.log_consent_event(
                        user_id=user_id,
                        consent_type=consent.consent_type.value,
                        granted=False,
                        details={
                            "consent_id": consent_id,
                            "reason": reason,
                            "original_purpose": consent.purpose,
                        },
                    )

                    logger.info(f"Consent withdrawn for user {user_id}: {consent_id}")
                    return True

        logger.warning(f"Consent not found or already withdrawn: {consent_id}")
        return False

    async def check_consent(
        self,
        user_id: str,
        consent_type: ConsentType,
        data_categories: Optional[List[DataCategory]] = None,
    ) -> bool:
        """
        Check if user has valid consent for specified processing.

        Args:
            user_id: ID of the user
            consent_type: Type of consent to check
            data_categories: Optional specific data categories to check

        Returns:
            True if valid consent exists
        """
        user_consents = self._consent_records.get(user_id, [])
        now = datetime.now(timezone.utc)

        for consent in user_consents:
            if (
                consent.consent_type == consent_type
                and consent.status == ConsentStatus.GRANTED
            ):

                # Check expiration
                if consent.expires_at and consent.expires_at < now:
                    consent.status = ConsentStatus.EXPIRED
                    continue

                # Check data categories if specified
                if data_categories:
                    consent_categories = set(consent.data_categories)
                    required_categories = set(data_categories)
                    if not required_categories.issubset(consent_categories):
                        continue

                return True

        return False

    async def get_user_consents(
        self, user_id: str, active_only: bool = False
    ) -> List[ConsentRecord]:
        """
        Get all consent records for a user.

        Args:
            user_id: ID of the user
            active_only: Only return active (granted) consents

        Returns:
            List of consent records
        """
        user_consents = self._consent_records.get(user_id, [])

        if active_only:
            now = datetime.now(timezone.utc)
            active_consents = []

            for consent in user_consents:
                if consent.status == ConsentStatus.GRANTED:
                    # Check expiration
                    if consent.expires_at and consent.expires_at < now:
                        consent.status = ConsentStatus.EXPIRED
                    else:
                        active_consents.append(consent)

            return active_consents

        return user_consents.copy()

    async def expire_old_consents(self) -> int:
        """
        Expire old consent records.

        Returns:
            Number of consents expired
        """
        now = datetime.now(timezone.utc)
        expired_count = 0

        for user_id, consents in self._consent_records.items():
            for consent in consents:
                if (
                    consent.status == ConsentStatus.GRANTED
                    and consent.expires_at
                    and consent.expires_at < now
                ):

                    consent.status = ConsentStatus.EXPIRED
                    expired_count += 1

                    # Audit log
                    await self.audit_logger.log_event(
                        event_type=AuditEventType.CONSENT_WITHDRAWN,
                        action="Consent expired automatically",
                        user_id=user_id,
                        details={
                            "consent_id": consent.consent_id,
                            "consent_type": consent.consent_type.value,
                            "expired_at": now.isoformat(),
                        },
                    )

        logger.info(f"Expired {expired_count} old consent records")
        return expired_count


class DataSubjectRights:
    """Implements GDPR data subject rights."""

    def __init__(self):
        self.encryption = get_encryption_service()
        self.field_encryption = ComplianceFieldEncryption()
        self.audit_logger = get_audit_logger()
        self._processing_records: Dict[str, List[DataProcessingRecord]] = {}
        self._data_store: Dict[str, Dict[str, Any]] = {}  # Simulated data store

    async def request_data_export(
        self, user_id: str, format_type: str = "json", include_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Handle data export request (GDPR Article 20).

        Args:
            user_id: ID of the user requesting data export
            format_type: Format for export (json, csv, xml)
            include_metadata: Whether to include processing metadata

        Returns:
            Exported user data
        """
        # Audit the request
        await self.audit_logger.log_privacy_request(
            request_type="export",
            user_id=user_id,
            details={
                "format": format_type,
                "include_metadata": include_metadata,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        # Collect all user data
        user_data = {
            "user_id": user_id,
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "format": format_type,
            "data": {},
        }

        # Get data from simulated store
        if user_id in self._data_store:
            raw_data = self._data_store[user_id].copy()

            # Decrypt sensitive fields
            decrypted_data = self.field_encryption.decrypt_fields(raw_data)
            user_data["data"]["profile"] = decrypted_data

        # Include processing records if requested
        if include_metadata:
            processing_records = self._processing_records.get(user_id, [])
            user_data["processing_history"] = [
                record.to_dict() for record in processing_records
            ]

        logger.info(f"Data export completed for user {user_id}")
        return user_data

    async def request_data_deletion(
        self,
        user_id: str,
        reason: str = "user_request",
        retain_legal_basis: bool = True,
    ) -> Dict[str, Any]:
        """
        Handle data deletion request (GDPR Article 17 - Right to be forgotten).

        Args:
            user_id: ID of the user requesting deletion
            reason: Reason for deletion
            retain_legal_basis: Whether to retain data required by legal obligations

        Returns:
            Deletion summary
        """
        # Audit the request
        await self.audit_logger.log_privacy_request(
            request_type="deletion",
            user_id=user_id,
            details={
                "reason": reason,
                "retain_legal_basis": retain_legal_basis,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        deletion_summary = {
            "user_id": user_id,
            "deletion_timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
            "deleted_data_categories": [],
            "retained_data_categories": [],
            "processing_records_affected": 0,
        }

        # Identify data that can be deleted vs. retained
        if user_id in self._data_store:
            user_data = self._data_store[user_id]

            # Categories that must be retained for legal compliance
            legal_retention_fields = set()
            if retain_legal_basis:
                # Example: financial records, audit trails, etc.
                legal_retention_fields = {
                    "financial_records",
                    "audit_trail",
                    "legal_documents",
                }

            # Delete non-legally required data
            deleted_fields = []
            retained_fields = []

            for field_name, field_value in user_data.copy().items():
                if field_name in legal_retention_fields:
                    retained_fields.append(field_name)
                else:
                    # Delete the field
                    del self._data_store[user_id][field_name]
                    deleted_fields.append(field_name)

                    # Determine data category
                    data_category = self._classify_data_field(field_name)
                    if (
                        data_category
                        and data_category
                        not in deletion_summary["deleted_data_categories"]
                    ):
                        deletion_summary["deleted_data_categories"].append(
                            data_category
                        )

            # Track retained data
            for field in retained_fields:
                data_category = self._classify_data_field(field)
                if (
                    data_category
                    and data_category
                    not in deletion_summary["retained_data_categories"]
                ):
                    deletion_summary["retained_data_categories"].append(data_category)

            # If no data remains, remove user entirely
            if not self._data_store[user_id]:
                del self._data_store[user_id]

        # Update processing records
        if user_id in self._processing_records:
            processing_records = self._processing_records[user_id]
            deletion_summary["processing_records_affected"] = len(processing_records)

            if not retain_legal_basis:
                # Remove all processing records
                del self._processing_records[user_id]
            else:
                # Mark records as subject to deletion request
                for record in processing_records:
                    record.metadata = record.metadata or {}
                    record.metadata["deletion_requested"] = True
                    record.metadata["deletion_timestamp"] = datetime.now(
                        timezone.utc
                    ).isoformat()

        logger.info(f"Data deletion completed for user {user_id}")
        return deletion_summary

    def _classify_data_field(self, field_name: str) -> Optional[str]:
        """Classify data field into GDPR data category."""
        field_lower = field_name.lower()

        if any(term in field_lower for term in ["name", "email", "phone"]):
            return "basic_identity"
        elif any(term in field_lower for term in ["ssn", "social_security", "tax_id"]):
            return "sensitive_identity"
        elif any(term in field_lower for term in ["health", "medical", "diagnosis"]):
            return "health_data"
        elif any(
            term in field_lower for term in ["fingerprint", "biometric", "facial"]
        ):
            return "biometric_data"
        elif any(term in field_lower for term in ["payment", "bank", "financial"]):
            return "financial_data"
        elif any(term in field_lower for term in ["location", "address", "gps"]):
            return "location_data"
        elif any(term in field_lower for term in ["behavior", "usage", "preference"]):
            return "behavioral_data"
        elif any(term in field_lower for term in ["message", "communication", "call"]):
            return "communication_data"

        return None

    async def rectify_data(
        self,
        user_id: str,
        field_updates: Dict[str, Any],
        reason: str = "user_correction",
    ) -> Dict[str, Any]:
        """
        Handle data rectification request (GDPR Article 16).

        Args:
            user_id: ID of the user requesting rectification
            field_updates: Dictionary of field updates
            reason: Reason for rectification

        Returns:
            Rectification summary
        """
        # Audit the request
        await self.audit_logger.log_event(
            event_type=AuditEventType.DATA_UPDATE,
            action="Data rectification request",
            user_id=user_id,
            details={
                "reason": reason,
                "fields_updated": list(field_updates.keys()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        rectification_summary = {
            "user_id": user_id,
            "rectification_timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
            "fields_updated": [],
            "fields_encrypted": [],
        }

        if user_id in self._data_store:
            user_data = self._data_store[user_id]

            for field_name, new_value in field_updates.items():
                if field_name in user_data:
                    # Update the field
                    old_value = user_data[field_name]
                    user_data[field_name] = new_value
                    rectification_summary["fields_updated"].append(field_name)

                    # Re-encrypt if it was previously encrypted
                    if self.field_encryption.is_field_encrypted(user_data, field_name):
                        # Re-encrypt with new value
                        encrypted_data = self.field_encryption.encrypt_fields(
                            {field_name: new_value}, [field_name]
                        )
                        user_data[field_name] = encrypted_data[field_name]
                        rectification_summary["fields_encrypted"].append(field_name)

        logger.info(f"Data rectification completed for user {user_id}")
        return rectification_summary

    async def restrict_processing(
        self,
        user_id: str,
        restriction_reason: str,
        affected_categories: List[DataCategory],
    ) -> bool:
        """
        Handle processing restriction request (GDPR Article 18).

        Args:
            user_id: ID of the user requesting restriction
            restriction_reason: Reason for restriction
            affected_categories: Data categories to restrict

        Returns:
            True if restriction was applied
        """
        # Audit the request
        await self.audit_logger.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action="Processing restriction requested",
            user_id=user_id,
            details={
                "restriction_reason": restriction_reason,
                "affected_categories": [cat.value for cat in affected_categories],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        # Mark processing records as restricted
        if user_id in self._processing_records:
            processing_records = self._processing_records[user_id]

            for record in processing_records:
                record_categories = set(record.data_categories)
                restriction_categories = set(affected_categories)

                if record_categories.intersection(restriction_categories):
                    record.metadata = record.metadata or {}
                    record.metadata["processing_restricted"] = True
                    record.metadata["restriction_reason"] = restriction_reason
                    record.metadata["restriction_timestamp"] = datetime.now(
                        timezone.utc
                    ).isoformat()

        logger.info(f"Processing restriction applied for user {user_id}")
        return True


class DataMinimization:
    """Implements data minimization principles."""

    def __init__(self):
        self.encryption = get_encryption_service()
        self.audit_logger = get_audit_logger()

    async def assess_data_necessity(
        self, data_fields: Dict[str, Any], processing_purpose: str
    ) -> Dict[str, Any]:
        """
        Assess which data fields are necessary for the specified purpose.

        Args:
            data_fields: Dictionary of data fields to assess
            processing_purpose: Purpose for data processing

        Returns:
            Assessment results with necessary/unnecessary fields
        """
        # Define purpose-based field requirements
        purpose_requirements = {
            "user_authentication": ["email", "password_hash", "user_id"],
            "health_coaching": [
                "health_metrics",
                "fitness_goals",
                "medical_conditions",
            ],
            "nutrition_planning": ["dietary_preferences", "allergies", "health_goals"],
            "progress_tracking": [
                "fitness_metrics",
                "workout_history",
                "body_measurements",
            ],
            "billing": ["payment_info", "billing_address", "user_id"],
            "marketing": ["email", "preferences", "consent_marketing"],
        }

        required_fields = purpose_requirements.get(processing_purpose, [])

        assessment = {
            "processing_purpose": processing_purpose,
            "assessment_timestamp": datetime.now(timezone.utc).isoformat(),
            "necessary_fields": [],
            "unnecessary_fields": [],
            "potentially_excessive": [],
            "recommendations": [],
        }

        for field_name, field_value in data_fields.items():
            field_lower = field_name.lower()

            # Check if field is necessary for the purpose
            if any(req in field_lower for req in required_fields):
                assessment["necessary_fields"].append(field_name)
            else:
                # Check if it's potentially useful but not strictly necessary
                if self._is_potentially_useful(field_name, processing_purpose):
                    assessment["potentially_excessive"].append(field_name)
                else:
                    assessment["unnecessary_fields"].append(field_name)

        # Generate recommendations
        if assessment["unnecessary_fields"]:
            assessment["recommendations"].append(
                f"Consider removing {len(assessment['unnecessary_fields'])} unnecessary fields"
            )

        if assessment["potentially_excessive"]:
            assessment["recommendations"].append(
                f"Review {len(assessment['potentially_excessive'])} potentially excessive fields"
            )

        # Audit the assessment
        await self.audit_logger.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action="Data minimization assessment",
            details={
                "processing_purpose": processing_purpose,
                "total_fields": len(data_fields),
                "necessary_fields": len(assessment["necessary_fields"]),
                "unnecessary_fields": len(assessment["unnecessary_fields"]),
                "potentially_excessive": len(assessment["potentially_excessive"]),
            },
        )

        return assessment

    def _is_potentially_useful(self, field_name: str, purpose: str) -> bool:
        """Check if a field might be useful but not strictly necessary."""
        field_lower = field_name.lower()

        if purpose == "health_coaching":
            return any(
                term in field_lower
                for term in ["age", "gender", "activity_level", "sleep_pattern"]
            )
        elif purpose == "nutrition_planning":
            return any(
                term in field_lower
                for term in ["weight", "height", "activity_level", "age"]
            )
        elif purpose == "marketing":
            return any(
                term in field_lower
                for term in ["location", "demographics", "usage_pattern"]
            )

        return False

    async def apply_retention_policy(
        self,
        data_records: List[Dict[str, Any]],
        retention_rules: Dict[str, int],  # field -> days
    ) -> Dict[str, Any]:
        """
        Apply data retention policies.

        Args:
            data_records: List of data records to evaluate
            retention_rules: Retention rules (field -> retention days)

        Returns:
            Retention policy application results
        """
        now = datetime.now(timezone.utc)

        results = {
            "evaluation_timestamp": now.isoformat(),
            "records_processed": len(data_records),
            "records_expired": 0,
            "fields_purged": 0,
            "expired_records": [],
        }

        for record in data_records:
            record_timestamp = datetime.fromisoformat(
                record.get("created_at", now.isoformat())
            )

            expired_fields = []
            for field_name, retention_days in retention_rules.items():
                if field_name in record:
                    field_age = (now - record_timestamp).days

                    if field_age > retention_days:
                        expired_fields.append(field_name)
                        del record[field_name]
                        results["fields_purged"] += 1

            if expired_fields:
                results["expired_records"].append(
                    {
                        "record_id": record.get("id", "unknown"),
                        "expired_fields": expired_fields,
                        "record_age_days": (now - record_timestamp).days,
                    }
                )
                results["records_expired"] += 1

        # Audit retention policy application
        await self.audit_logger.log_event(
            event_type=AuditEventType.DATA_DELETE,
            action="Data retention policy applied",
            details=results,
        )

        return results


class ComplianceController:
    """Main compliance controller orchestrating all compliance functions."""

    def __init__(self):
        self.consent_manager = ConsentManager()
        self.data_subject_rights = DataSubjectRights()
        self.data_minimization = DataMinimization()
        self.audit_logger = get_audit_logger()

    async def check_processing_compliance(
        self, user_id: str, processing_purpose: str, data_categories: List[DataCategory]
    ) -> Dict[str, Any]:
        """
        Check if data processing complies with all requirements.

        Args:
            user_id: ID of the user
            processing_purpose: Purpose of processing
            data_categories: Categories of data to be processed

        Returns:
            Compliance check results
        """
        compliance_results = {
            "user_id": user_id,
            "processing_purpose": processing_purpose,
            "data_categories": [cat.value for cat in data_categories],
            "check_timestamp": datetime.now(timezone.utc).isoformat(),
            "compliant": False,
            "consent_check": False,
            "legal_basis": None,
            "issues": [],
            "recommendations": [],
        }

        # Check consent for each data category
        consent_checks = {}
        for category in data_categories:
            # Map data categories to consent types
            consent_type = self._map_data_category_to_consent_type(category)

            if consent_type:
                has_consent = await self.consent_manager.check_consent(
                    user_id=user_id,
                    consent_type=consent_type,
                    data_categories=[category],
                )
                consent_checks[category.value] = has_consent
            else:
                consent_checks[category.value] = True  # No consent required

        # Overall consent check
        compliance_results["consent_check"] = all(consent_checks.values())
        compliance_results["consent_details"] = consent_checks

        if not compliance_results["consent_check"]:
            compliance_results["issues"].append("Missing required consents")
            compliance_results["recommendations"].append(
                "Obtain user consent before processing"
            )

        # Check for sensitive data categories requiring special handling
        sensitive_categories = {
            DataCategory.HEALTH_DATA,
            DataCategory.BIOMETRIC_DATA,
            DataCategory.SENSITIVE_IDENTITY,
        }

        if any(cat in sensitive_categories for cat in data_categories):
            compliance_results["requires_enhanced_protection"] = True
            compliance_results["recommendations"].append(
                "Apply enhanced security measures for sensitive data"
            )

        # Overall compliance
        compliance_results["compliant"] = (
            compliance_results["consent_check"]
            and len(compliance_results["issues"]) == 0
        )

        # Audit the compliance check
        await self.audit_logger.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action="Compliance check performed",
            user_id=user_id,
            details={
                "processing_purpose": processing_purpose,
                "data_categories": [cat.value for cat in data_categories],
                "compliant": compliance_results["compliant"],
                "issues_found": len(compliance_results["issues"]),
            },
        )

        return compliance_results

    def _map_data_category_to_consent_type(
        self, category: DataCategory
    ) -> Optional[ConsentType]:
        """Map data category to consent type."""
        mapping = {
            DataCategory.HEALTH_DATA: ConsentType.MEDICAL_DATA,
            DataCategory.BIOMETRIC_DATA: ConsentType.BIOMETRIC_DATA,
            DataCategory.LOCATION_DATA: ConsentType.LOCATION_DATA,
            DataCategory.BEHAVIORAL_DATA: ConsentType.BEHAVIORAL_TRACKING,
        }

        return mapping.get(category)

    async def generate_compliance_report(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive compliance report.

        Args:
            user_id: Optional specific user ID
            start_date: Optional start date for report
            end_date: Optional end date for report

        Returns:
            Comprehensive compliance report
        """
        report = {
            "report_id": str(uuid.uuid4()),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "report_period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            },
            "user_scope": user_id or "all_users",
            "consent_summary": {},
            "data_subject_requests": {},
            "compliance_metrics": {},
            "recommendations": [],
        }

        # Get consent summary
        if user_id:
            user_consents = await self.consent_manager.get_user_consents(user_id)
            report["consent_summary"] = {
                "total_consents": len(user_consents),
                "active_consents": len(
                    [c for c in user_consents if c.status == ConsentStatus.GRANTED]
                ),
                "withdrawn_consents": len(
                    [c for c in user_consents if c.status == ConsentStatus.WITHDRAWN]
                ),
                "expired_consents": len(
                    [c for c in user_consents if c.status == ConsentStatus.EXPIRED]
                ),
            }

        # Add compliance metrics
        report["compliance_metrics"] = {
            "consent_coverage": self._calculate_consent_coverage(),
            "data_retention_compliance": self._check_retention_compliance(),
            "encryption_coverage": self._check_encryption_coverage(),
        }

        # Generate recommendations
        if report["compliance_metrics"]["consent_coverage"] < 100:
            report["recommendations"].append(
                "Improve consent coverage for all data processing activities"
            )

        if report["compliance_metrics"]["encryption_coverage"] < 100:
            report["recommendations"].append(
                "Ensure all sensitive data is properly encrypted"
            )

        return report

    def _calculate_consent_coverage(self) -> float:
        """Calculate percentage of data processing activities with valid consent."""
        # Simplified calculation - in real implementation, would check all processing activities
        return 95.0

    def _check_retention_compliance(self) -> float:
        """Check compliance with data retention policies."""
        # Simplified calculation - in real implementation, would check all data stores
        return 98.0

    def _check_encryption_coverage(self) -> float:
        """Check percentage of sensitive data that is encrypted."""
        # Simplified calculation - in real implementation, would scan all data stores
        return 100.0


# Global compliance controller instance
_compliance_controller: Optional[ComplianceController] = None


def get_compliance_controller() -> ComplianceController:
    """Get the global compliance controller instance."""
    global _compliance_controller
    if _compliance_controller is None:
        _compliance_controller = ComplianceController()
    return _compliance_controller
