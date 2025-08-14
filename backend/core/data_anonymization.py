"""
Data Anonymization and Pseudonymization Service
===============================================

GDPR and HIPAA compliant data anonymization utilities for
privacy protection and compliance requirements.
"""

import hashlib
import hmac
import random
import re
import string
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from core.logging_config import get_logger
from core.security.encryption_service import get_encryption_service

logger = get_logger(__name__)


class AnonymizationType(Enum):
    """Types of anonymization techniques."""

    MASKING = "masking"
    REDACTION = "redaction"
    GENERALIZATION = "generalization"
    PSEUDONYMIZATION = "pseudonymization"
    PERTURBATION = "perturbation"
    SYNTHETIC_DATA = "synthetic_data"
    SUPPRESSION = "suppression"
    K_ANONYMITY = "k_anonymity"


class DataSensitivity(Enum):
    """Data sensitivity levels."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


@dataclass
class AnonymizationRule:
    """Represents a data anonymization rule."""

    field_pattern: str  # Regex pattern for field names
    technique: AnonymizationType
    parameters: Dict[str, Any]
    sensitivity_level: DataSensitivity
    preserve_format: bool = False
    preserve_length: bool = False


class PIIDetector:
    """Detects personally identifiable information in data."""

    # Compiled regex patterns for PII detection
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    PHONE_PATTERN = re.compile(
        r"\b(?:\+?1[-.\s]?)?(?:\([0-9]{3}\)|[0-9]{3})[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b"
    )
    SSN_PATTERN = re.compile(r"\b\d{3}-?\d{2}-?\d{4}\b")
    CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
    IP_ADDRESS_PATTERN = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")

    # Name patterns (common first and last names)
    FIRST_NAMES = {
        "james",
        "john",
        "robert",
        "michael",
        "william",
        "david",
        "richard",
        "charles",
        "joseph",
        "thomas",
        "mary",
        "patricia",
        "jennifer",
        "linda",
        "elizabeth",
        "barbara",
        "susan",
        "jessica",
        "sarah",
        "karen",
    }

    LAST_NAMES = {
        "smith",
        "johnson",
        "williams",
        "brown",
        "jones",
        "garcia",
        "miller",
        "davis",
        "rodriguez",
        "martinez",
        "hernandez",
        "lopez",
        "gonzalez",
        "wilson",
        "anderson",
    }

    def __init__(self):
        self.pii_patterns = {
            "email": self.EMAIL_PATTERN,
            "phone": self.PHONE_PATTERN,
            "ssn": self.SSN_PATTERN,
            "credit_card": self.CREDIT_CARD_PATTERN,
            "ip_address": self.IP_ADDRESS_PATTERN,
        }

    def detect_pii_in_text(self, text: str) -> Dict[str, List[str]]:
        """
        Detect PII in text content.

        Args:
            text: Text to scan for PII

        Returns:
            Dictionary mapping PII types to found instances
        """
        if not isinstance(text, str):
            return {}

        detected_pii = {}

        for pii_type, pattern in self.pii_patterns.items():
            matches = pattern.findall(text.lower())
            if matches:
                detected_pii[pii_type] = matches

        # Check for potential names
        words = text.lower().split()
        potential_names = []

        for word in words:
            word = re.sub(r"[^\w]", "", word)  # Remove punctuation
            if word in self.FIRST_NAMES or word in self.LAST_NAMES:
                potential_names.append(word)

        if potential_names:
            detected_pii["potential_names"] = potential_names

        return detected_pii

    def detect_pii_in_data(
        self, data: Dict[str, Any]
    ) -> Dict[str, Dict[str, List[str]]]:
        """
        Detect PII in structured data.

        Args:
            data: Dictionary containing data to scan

        Returns:
            Dictionary mapping field names to detected PII
        """
        pii_findings = {}

        for field_name, field_value in data.items():
            if isinstance(field_value, str):
                pii_in_field = self.detect_pii_in_text(field_value)
                if pii_in_field:
                    pii_findings[field_name] = pii_in_field
            elif isinstance(field_value, (list, tuple)):
                for i, item in enumerate(field_value):
                    if isinstance(item, str):
                        pii_in_item = self.detect_pii_in_text(item)
                        if pii_in_item:
                            pii_findings[f"{field_name}[{i}]"] = pii_in_item
            elif isinstance(field_value, dict):
                nested_findings = self.detect_pii_in_data(field_value)
                if nested_findings:
                    for nested_field, nested_pii in nested_findings.items():
                        pii_findings[f"{field_name}.{nested_field}"] = nested_pii

        return pii_findings

    def is_field_potentially_sensitive(self, field_name: str) -> bool:
        """
        Check if a field name suggests it contains sensitive data.

        Args:
            field_name: Name of the field to check

        Returns:
            True if field is potentially sensitive
        """
        field_lower = field_name.lower()

        sensitive_keywords = {
            "password",
            "secret",
            "key",
            "token",
            "auth",
            "login",
            "email",
            "phone",
            "address",
            "ssn",
            "social",
            "tax",
            "credit",
            "card",
            "account",
            "bank",
            "medical",
            "health",
            "diagnosis",
            "treatment",
            "medication",
            "dob",
            "birth",
            "name",
            "first",
            "last",
            "full_name",
            "username",
        }

        return any(keyword in field_lower for keyword in sensitive_keywords)


class DataAnonymizer:
    """Main data anonymization service."""

    def __init__(self):
        self.encryption_service = get_encryption_service()
        self.pii_detector = PIIDetector()
        self.pseudonym_map: Dict[str, str] = {}
        self.synthetic_generators = self._initialize_synthetic_generators()

    def _initialize_synthetic_generators(self) -> Dict[str, Callable]:
        """Initialize synthetic data generators."""
        return {
            "email": self._generate_synthetic_email,
            "phone": self._generate_synthetic_phone,
            "name": self._generate_synthetic_name,
            "address": self._generate_synthetic_address,
            "ssn": self._generate_synthetic_ssn,
            "date": self._generate_synthetic_date,
            "number": self._generate_synthetic_number,
        }

    def mask_data(
        self,
        data: str,
        mask_char: str = "*",
        preserve_format: bool = True,
        reveal_chars: int = 0,
    ) -> str:
        """
        Mask sensitive data with specified character.

        Args:
            data: Data to mask
            mask_char: Character to use for masking
            preserve_format: Whether to preserve original format
            reveal_chars: Number of characters to reveal at the end

        Returns:
            Masked data string
        """
        if not data:
            return data

        data_str = str(data)

        if reveal_chars > 0 and len(data_str) > reveal_chars:
            masked_part = mask_char * (len(data_str) - reveal_chars)
            revealed_part = data_str[-reveal_chars:]
            result = masked_part + revealed_part
        else:
            if preserve_format:
                # Preserve format by replacing alphanumeric chars only
                result = "".join(
                    mask_char if char.isalnum() else char for char in data_str
                )
            else:
                result = mask_char * len(data_str)

        return result

    def redact_data(self, data: str, redaction_text: str = "[REDACTED]") -> str:
        """
        Redact sensitive data by replacing with redaction text.

        Args:
            data: Data to redact
            redaction_text: Text to replace sensitive data with

        Returns:
            Redacted data string
        """
        return redaction_text if data else data

    def generalize_data(self, data: Any, generalization_rules: Dict[str, Any]) -> Any:
        """
        Generalize data by reducing precision.

        Args:
            data: Data to generalize
            generalization_rules: Rules for generalization

        Returns:
            Generalized data
        """
        if isinstance(data, (int, float)):
            if "round_to" in generalization_rules:
                return round(data, generalization_rules["round_to"])
            elif "bucket_size" in generalization_rules:
                bucket_size = generalization_rules["bucket_size"]
                return (data // bucket_size) * bucket_size

        elif isinstance(data, datetime):
            if generalization_rules.get("precision") == "month":
                return data.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            elif generalization_rules.get("precision") == "year":
                return data.replace(
                    month=1, day=1, hour=0, minute=0, second=0, microsecond=0
                )

        elif isinstance(data, str):
            if generalization_rules.get("truncate_to"):
                return data[: generalization_rules["truncate_to"]]

        return data

    def pseudonymize_data(
        self, data: str, key: Optional[str] = None, consistent: bool = True
    ) -> str:
        """
        Pseudonymize data using deterministic or random pseudonyms.

        Args:
            data: Data to pseudonymize
            key: Optional key for deterministic pseudonymization
            consistent: Whether pseudonyms should be consistent

        Returns:
            Pseudonymized data
        """
        if not data:
            return data

        data_str = str(data)

        if consistent:
            # Use consistent pseudonymization (same input -> same output)
            if data_str in self.pseudonym_map:
                return self.pseudonym_map[data_str]

            # Generate deterministic pseudonym
            if key:
                # Use HMAC for deterministic pseudonym generation
                pseudonym = hmac.new(
                    key.encode("utf-8"), data_str.encode("utf-8"), hashlib.sha256
                ).hexdigest()[:16]
            else:
                # Use hash for deterministic pseudonym
                pseudonym = hashlib.sha256(data_str.encode("utf-8")).hexdigest()[:16]

            # Store mapping for consistency
            self.pseudonym_map[data_str] = pseudonym
            return pseudonym

        else:
            # Generate random pseudonym
            return "".join(random.choices(string.ascii_letters + string.digits, k=16))

    def perturb_numeric_data(
        self,
        data: Union[int, float],
        noise_factor: float = 0.1,
        distribution: str = "gaussian",
    ) -> Union[int, float]:
        """
        Add noise to numeric data for privacy protection.

        Args:
            data: Numeric data to perturb
            noise_factor: Factor for noise generation
            distribution: Noise distribution (gaussian, uniform, laplacian)

        Returns:
            Perturbed numeric value
        """
        if not isinstance(data, (int, float)):
            return data

        if distribution == "gaussian":
            noise = random.gauss(0, abs(data) * noise_factor)
        elif distribution == "uniform":
            noise_range = abs(data) * noise_factor
            noise = random.uniform(-noise_range, noise_range)
        elif distribution == "laplacian":
            # Simplified Laplacian noise
            scale = abs(data) * noise_factor
            noise = random.expovariate(1 / scale) - random.expovariate(1 / scale)
        else:
            noise = 0

        result = data + noise

        # Preserve type
        if isinstance(data, int):
            return int(round(result))
        else:
            return result

    def suppress_data(self, data: Any, threshold: int = 5) -> Optional[Any]:
        """
        Suppress data that doesn't meet k-anonymity threshold.

        Args:
            data: Data to potentially suppress
            threshold: Minimum group size for k-anonymity

        Returns:
            Data or None if suppressed
        """
        # Simplified suppression logic
        # In real implementation, would check group sizes
        return None if random.randint(1, 10) <= threshold else data

    def _generate_synthetic_email(self) -> str:
        """Generate synthetic email address."""
        domains = ["example.com", "test.org", "sample.net", "demo.co"]
        username = "".join(random.choices(string.ascii_lowercase, k=8))
        domain = random.choice(domains)
        return f"{username}@{domain}"

    def _generate_synthetic_phone(self) -> str:
        """Generate synthetic phone number."""
        return f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

    def _generate_synthetic_name(self) -> str:
        """Generate synthetic name."""
        first_names = [
            "John",
            "Jane",
            "Alex",
            "Sam",
            "Taylor",
            "Jordan",
            "Casey",
            "Morgan",
        ]
        last_names = [
            "Smith",
            "Johnson",
            "Brown",
            "Davis",
            "Miller",
            "Wilson",
            "Moore",
            "Taylor",
        ]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    def _generate_synthetic_address(self) -> str:
        """Generate synthetic address."""
        streets = ["Main St", "Oak Ave", "Pine Rd", "Elm Dr", "Maple Ln"]
        return f"{random.randint(100, 9999)} {random.choice(streets)}, Anytown, ST {random.randint(10000, 99999)}"

    def _generate_synthetic_ssn(self) -> str:
        """Generate synthetic SSN-like identifier."""
        return f"000-{random.randint(10, 99)}-{random.randint(1000, 9999)}"

    def _generate_synthetic_date(self) -> str:
        """Generate synthetic date."""
        start_date = datetime(1950, 1, 1)
        end_date = datetime(2010, 12, 31)
        time_delta = end_date - start_date
        random_days = random.randint(0, time_delta.days)
        synthetic_date = start_date + timedelta(days=random_days)
        return synthetic_date.strftime("%Y-%m-%d")

    def _generate_synthetic_number(self) -> int:
        """Generate synthetic number."""
        return random.randint(1, 1000000)

    def anonymize_field(
        self, field_name: str, field_value: Any, rule: AnonymizationRule
    ) -> Any:
        """
        Anonymize a single field based on the specified rule.

        Args:
            field_name: Name of the field
            field_value: Value to anonymize
            rule: Anonymization rule to apply

        Returns:
            Anonymized field value
        """
        if field_value is None:
            return field_value

        try:
            if rule.technique == AnonymizationType.MASKING:
                return self.mask_data(
                    str(field_value),
                    mask_char=rule.parameters.get("mask_char", "*"),
                    preserve_format=rule.preserve_format,
                    reveal_chars=rule.parameters.get("reveal_chars", 0),
                )

            elif rule.technique == AnonymizationType.REDACTION:
                return self.redact_data(
                    str(field_value),
                    redaction_text=rule.parameters.get("redaction_text", "[REDACTED]"),
                )

            elif rule.technique == AnonymizationType.GENERALIZATION:
                return self.generalize_data(field_value, rule.parameters)

            elif rule.technique == AnonymizationType.PSEUDONYMIZATION:
                return self.pseudonymize_data(
                    str(field_value),
                    key=rule.parameters.get("key"),
                    consistent=rule.parameters.get("consistent", True),
                )

            elif rule.technique == AnonymizationType.PERTURBATION:
                if isinstance(field_value, (int, float)):
                    return self.perturb_numeric_data(
                        field_value,
                        noise_factor=rule.parameters.get("noise_factor", 0.1),
                        distribution=rule.parameters.get("distribution", "gaussian"),
                    )

            elif rule.technique == AnonymizationType.SYNTHETIC_DATA:
                data_type = rule.parameters.get("data_type", "generic")
                generator = self.synthetic_generators.get(data_type)
                if generator:
                    return generator()

            elif rule.technique == AnonymizationType.SUPPRESSION:
                return self.suppress_data(
                    field_value, threshold=rule.parameters.get("threshold", 5)
                )

            return field_value

        except Exception as e:
            logger.error(f"Error anonymizing field {field_name}: {e}")
            return field_value

    def anonymize_data(
        self,
        data: Dict[str, Any],
        rules: List[AnonymizationRule],
        detect_pii: bool = True,
    ) -> Dict[str, Any]:
        """
        Anonymize data according to specified rules.

        Args:
            data: Dictionary containing data to anonymize
            rules: List of anonymization rules to apply
            detect_pii: Whether to automatically detect and flag PII

        Returns:
            Anonymized data with metadata
        """
        result = data.copy()
        anonymization_metadata = {
            "timestamp": datetime.now().isoformat(),
            "rules_applied": [],
            "fields_anonymized": [],
            "pii_detected": {},
            "anonymization_summary": {},
        }

        # Detect PII if requested
        if detect_pii:
            pii_findings = self.pii_detector.detect_pii_in_data(data)
            anonymization_metadata["pii_detected"] = pii_findings

        # Apply anonymization rules
        for rule in rules:
            pattern = re.compile(rule.field_pattern)
            fields_matched = []

            for field_name in data.keys():
                if pattern.match(
                    field_name
                ) or self.pii_detector.is_field_potentially_sensitive(field_name):
                    original_value = result[field_name]
                    anonymized_value = self.anonymize_field(
                        field_name, original_value, rule
                    )

                    if anonymized_value != original_value:
                        result[field_name] = anonymized_value
                        fields_matched.append(field_name)

            if fields_matched:
                anonymization_metadata["rules_applied"].append(
                    {
                        "pattern": rule.field_pattern,
                        "technique": rule.technique.value,
                        "fields_affected": fields_matched,
                    }
                )
                anonymization_metadata["fields_anonymized"].extend(fields_matched)

        # Summary statistics
        anonymization_metadata["anonymization_summary"] = {
            "total_fields": len(data),
            "fields_anonymized": len(set(anonymization_metadata["fields_anonymized"])),
            "anonymization_rate": (
                len(set(anonymization_metadata["fields_anonymized"])) / len(data) * 100
                if data
                else 0
            ),
        }

        return {"anonymized_data": result, "metadata": anonymization_metadata}

    def create_anonymization_report(
        self, original_data: Dict[str, Any], anonymized_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a detailed anonymization report.

        Args:
            original_data: Original data before anonymization
            anonymized_result: Result from anonymization process

        Returns:
            Detailed anonymization report
        """
        metadata = anonymized_result.get("metadata", {})
        anonymized_data = anonymized_result.get("anonymized_data", {})

        report = {
            "report_id": str(uuid.uuid4()),
            "generated_at": datetime.now().isoformat(),
            "data_summary": {
                "original_fields": len(original_data),
                "anonymized_fields": len(anonymized_data),
                "fields_modified": len(set(metadata.get("fields_anonymized", []))),
            },
            "pii_analysis": metadata.get("pii_detected", {}),
            "anonymization_techniques": {},
            "privacy_impact_assessment": {},
            "compliance_notes": [],
        }

        # Analyze techniques used
        for rule_info in metadata.get("rules_applied", []):
            technique = rule_info["technique"]
            if technique not in report["anonymization_techniques"]:
                report["anonymization_techniques"][technique] = {
                    "fields_count": 0,
                    "examples": [],
                }

            report["anonymization_techniques"][technique]["fields_count"] += len(
                rule_info["fields_affected"]
            )
            report["anonymization_techniques"][technique]["examples"].extend(
                rule_info["fields_affected"][:3]  # First 3 examples
            )

        # Privacy impact assessment
        anonymization_rate = metadata.get("anonymization_summary", {}).get(
            "anonymization_rate", 0
        )

        if anonymization_rate >= 80:
            privacy_risk = "LOW"
        elif anonymization_rate >= 50:
            privacy_risk = "MEDIUM"
        else:
            privacy_risk = "HIGH"

        report["privacy_impact_assessment"] = {
            "privacy_risk_level": privacy_risk,
            "anonymization_coverage": f"{anonymization_rate:.1f}%",
            "recommended_actions": [],
        }

        # Compliance notes
        if privacy_risk == "HIGH":
            report["compliance_notes"].append(
                "Consider additional anonymization techniques"
            )

        if report["pii_analysis"]:
            report["compliance_notes"].append(
                "PII detected and should be properly anonymized"
            )

        return report


# Global anonymizer instance
_data_anonymizer: Optional[DataAnonymizer] = None


def get_data_anonymizer() -> DataAnonymizer:
    """Get the global data anonymizer instance."""
    global _data_anonymizer
    if _data_anonymizer is None:
        _data_anonymizer = DataAnonymizer()
    return _data_anonymizer


# Convenience functions
def anonymize_user_data(
    data: Dict[str, Any],
    sensitivity_level: DataSensitivity = DataSensitivity.CONFIDENTIAL,
) -> Dict[str, Any]:
    """
    Anonymize user data with predefined rules based on sensitivity level.

    Args:
        data: User data to anonymize
        sensitivity_level: Data sensitivity level

    Returns:
        Anonymized data with metadata
    """
    anonymizer = get_data_anonymizer()

    # Define rules based on sensitivity level
    if sensitivity_level == DataSensitivity.RESTRICTED:
        rules = [
            AnonymizationRule(
                field_pattern=r".*email.*",
                technique=AnonymizationType.REDACTION,
                parameters={"redaction_text": "[EMAIL_REDACTED]"},
                sensitivity_level=sensitivity_level,
            ),
            AnonymizationRule(
                field_pattern=r".*name.*",
                technique=AnonymizationType.SYNTHETIC_DATA,
                parameters={"data_type": "name"},
                sensitivity_level=sensitivity_level,
            ),
            AnonymizationRule(
                field_pattern=r".*phone.*",
                technique=AnonymizationType.SYNTHETIC_DATA,
                parameters={"data_type": "phone"},
                sensitivity_level=sensitivity_level,
            ),
            AnonymizationRule(
                field_pattern=r".*ssn.*",
                technique=AnonymizationType.REDACTION,
                parameters={"redaction_text": "[SSN_REDACTED]"},
                sensitivity_level=sensitivity_level,
            ),
        ]
    else:
        rules = [
            AnonymizationRule(
                field_pattern=r".*email.*",
                technique=AnonymizationType.MASKING,
                parameters={"reveal_chars": 4},
                sensitivity_level=sensitivity_level,
                preserve_format=True,
            ),
            AnonymizationRule(
                field_pattern=r".*phone.*",
                technique=AnonymizationType.MASKING,
                parameters={"reveal_chars": 4},
                sensitivity_level=sensitivity_level,
                preserve_format=True,
            ),
            AnonymizationRule(
                field_pattern=r".*name.*",
                technique=AnonymizationType.MASKING,
                parameters={"reveal_chars": 2},
                sensitivity_level=sensitivity_level,
            ),
        ]

    return anonymizer.anonymize_data(data, rules)
