"""
Comprehensive encryption compliance tests.

Tests encryption functionality for GDPR and HIPAA compliance,
including field-level encryption, key rotation, and data integrity.
"""

import pytest

from core.security.encryption_service import (
    AsyncEncryptionService,
    ComplianceFieldEncryption,
    EncryptionService,
    FieldEncryption,
    KeyRotationManager,
    decrypt_pii,
    encrypt_pii,
    get_encryption_service,
)


class TestEncryptionService:
    """Test the core encryption service functionality."""

    def test_encryption_service_initialization(self):
        """Test encryption service can be initialized."""
        service = EncryptionService()
        assert service is not None
        assert service._key is not None
        assert len(service._key) == 32  # 256-bit key

    def test_string_encryption_decryption(self):
        """Test basic string encryption and decryption."""
        service = EncryptionService()
        plaintext = "This is sensitive data"

        # Encrypt
        ciphertext = service.encrypt_string(plaintext)
        assert ciphertext != plaintext
        assert len(ciphertext) > 0

        # Decrypt
        decrypted = service.decrypt_string(ciphertext)
        assert decrypted == plaintext

    def test_json_encryption_decryption(self):
        """Test JSON data encryption and decryption."""
        service = EncryptionService()
        data = {
            "user_id": "12345",
            "email": "test@example.com",
            "health_data": {
                "weight": 70.5,
                "height": 175,
                "conditions": ["diabetes", "hypertension"],
            },
        }

        # Encrypt
        ciphertext = service.encrypt_json(data)
        assert isinstance(ciphertext, str)

        # Decrypt
        decrypted = service.decrypt_json(ciphertext)
        assert decrypted == data

    def test_encryption_with_associated_data(self):
        """Test authenticated encryption with associated data."""
        service = EncryptionService()
        plaintext = "Sensitive medical data"
        associated_data = "user_12345_medical_record"

        # Encrypt with AAD
        ciphertext = service.encrypt_string(plaintext, associated_data)

        # Decrypt with correct AAD
        decrypted = service.decrypt_string(ciphertext, associated_data)
        assert decrypted == plaintext

        # Attempt decrypt with wrong AAD should fail
        with pytest.raises(ValueError):
            service.decrypt_string(ciphertext, "wrong_aad")

    def test_encryption_with_metadata(self):
        """Test encryption with compliance metadata."""
        service = EncryptionService()
        data = {"ssn": "123-45-6789", "medical_id": "MED12345"}
        metadata = {"data_type": "PHI", "user_consent": True}

        # Encrypt with metadata
        encrypted_obj = service.encrypt_with_metadata(data, metadata)

        assert "encrypted_data" in encrypted_obj
        assert "metadata" in encrypted_obj
        assert encrypted_obj["metadata"]["data_type"] == "PHI"
        assert "timestamp" in encrypted_obj["metadata"]

        # Decrypt with metadata validation
        decrypted = service.decrypt_with_metadata(encrypted_obj)
        assert decrypted == data

    def test_hmac_signature_verification(self):
        """Test HMAC signature for data integrity."""
        service = EncryptionService()
        data = b"Important data that must not be tampered with"

        # Create signature
        signature = service.create_hmac_signature(data)
        assert len(signature) > 0

        # Verify correct signature
        assert service.verify_hmac_signature(data, signature) is True

        # Verify wrong signature
        assert service.verify_hmac_signature(b"tampered data", signature) is False
        assert service.verify_hmac_signature(data, "wrong_signature") is False

    def test_key_derivation_from_password(self):
        """Test password-based key derivation."""
        password = "SecurePassword123!"

        # Derive key with generated salt
        key1, salt1 = EncryptionService.derive_key_from_password(password)
        assert len(key1) == 32  # 256-bit key
        assert len(salt1) == 16  # 128-bit salt

        # Derive key with same salt should produce same key
        key2, salt2 = EncryptionService.derive_key_from_password(password, salt1)
        assert key1 == key2
        assert salt1 == salt2

        # Different salt should produce different key
        key3, salt3 = EncryptionService.derive_key_from_password(password)
        assert key1 != key3
        assert salt1 != salt3

    def test_rsa_encryption_decryption(self):
        """Test RSA asymmetric encryption."""
        service = EncryptionService()
        plaintext = b"Symmetric key for hybrid encryption"

        # Generate key pair
        private_key_pem, public_key_pem = service.generate_key_pair()
        assert b"BEGIN PRIVATE KEY" in private_key_pem
        assert b"BEGIN PUBLIC KEY" in public_key_pem

        # Encrypt with public key
        ciphertext = service.encrypt_with_rsa(plaintext, public_key_pem)
        assert ciphertext != plaintext

        # Decrypt with private key
        decrypted = service.decrypt_with_rsa(ciphertext, private_key_pem)
        assert decrypted == plaintext


class TestFieldEncryption:
    """Test field-level encryption functionality."""

    def test_field_encryption_basic(self):
        """Test basic field encryption and decryption."""
        field_encryption = FieldEncryption()
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30,
            "public_info": "This is public",
        }

        # Encrypt specific fields
        encrypted_data = field_encryption.encrypt_fields(data, ["name", "email"])

        # Check that specified fields are encrypted
        assert encrypted_data["name"]["_encrypted"] is True
        assert encrypted_data["email"]["_encrypted"] is True
        assert encrypted_data["age"] == 30  # Not encrypted
        assert encrypted_data["public_info"] == "This is public"  # Not encrypted

        # Decrypt fields
        decrypted_data = field_encryption.decrypt_fields(encrypted_data)
        assert decrypted_data["name"] == "John Doe"
        assert decrypted_data["email"] == "john@example.com"
        assert decrypted_data["age"] == 30
        assert decrypted_data["public_info"] == "This is public"

    def test_field_encryption_with_integrity_check(self):
        """Test field encryption with integrity verification."""
        field_encryption = FieldEncryption()
        data = {"ssn": "123-45-6789"}

        # Encrypt field
        encrypted_data = field_encryption.encrypt_fields(data, ["ssn"])

        # Check integrity signature exists
        assert "signature" in encrypted_data["ssn"]
        assert "algorithm" in encrypted_data["ssn"]
        assert encrypted_data["ssn"]["algorithm"] == "AES-256-GCM"

        # Decrypt should work with valid signature
        decrypted_data = field_encryption.decrypt_fields(encrypted_data)
        assert decrypted_data["ssn"] == "123-45-6789"

    def test_field_encryption_detection(self):
        """Test encrypted field detection."""
        field_encryption = FieldEncryption()
        data = {
            "name": "John Doe",
            "encrypted_field": {
                "_encrypted": True,
                "value": "encrypted_content",
                "signature": "hmac_signature",
            },
            "normal_field": "normal_value",
        }

        # Test field detection
        assert field_encryption.is_field_encrypted(data, "encrypted_field") is True
        assert field_encryption.is_field_encrypted(data, "normal_field") is False

        # Test getting encrypted field list
        encrypted_fields = field_encryption.get_encrypted_fields(data)
        assert "encrypted_field" in encrypted_fields
        assert "normal_field" not in encrypted_fields

    def test_selective_decryption(self):
        """Test selective field decryption."""
        field_encryption = FieldEncryption()
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-1234",
            "address": "123 Main St",
        }

        # Encrypt all fields
        encrypted_data = field_encryption.encrypt_fields(
            data, ["name", "email", "phone", "address"]
        )

        # Selectively decrypt only name and email
        partially_decrypted = field_encryption.selective_decrypt(
            encrypted_data, ["name", "email"]
        )

        assert partially_decrypted["name"] == "John Doe"
        assert partially_decrypted["email"] == "john@example.com"
        assert partially_decrypted["phone"]["_encrypted"] is True  # Still encrypted
        assert partially_decrypted["address"]["_encrypted"] is True  # Still encrypted


class TestComplianceFieldEncryption:
    """Test GDPR/HIPAA compliant field encryption."""

    def test_pii_detection(self):
        """Test automatic PII detection."""
        compliance_encryption = ComplianceFieldEncryption()
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone_number": "555-1234",
            "medical_record": "Patient has diabetes",
            "favorite_color": "blue",  # Not sensitive
        }

        sensitive_fields = compliance_encryption.identify_sensitive_fields(data)

        assert sensitive_fields["first_name"] == "PII"
        assert sensitive_fields["last_name"] == "PII"
        assert sensitive_fields["email"] == "PII"
        assert sensitive_fields["phone_number"] == "PII"
        assert sensitive_fields["medical_record"] == "PHI"
        assert "favorite_color" not in sensitive_fields

    def test_compliance_encryption_with_metadata(self):
        """Test encryption with compliance metadata."""
        compliance_encryption = ComplianceFieldEncryption()
        data = {
            "patient_name": "Jane Smith",
            "diagnosis": "Type 2 Diabetes",
            "public_info": "General wellness tips",
        }

        # Auto-detect and encrypt sensitive data
        encrypted_data = compliance_encryption.encrypt_sensitive_data(data)

        # Check that sensitive fields are encrypted with compliance metadata
        assert encrypted_data["patient_name"]["_compliance"] is True
        assert encrypted_data["diagnosis"]["_compliance"] is True
        assert encrypted_data["public_info"] == "General wellness tips"  # Not encrypted

        # Check compliance metadata
        patient_meta = encrypted_data["patient_name"]["metadata"]
        assert patient_meta["sensitivity_type"] == "PII"
        assert "GDPR" in patient_meta["compliance_tags"]
        assert patient_meta["data_classification"] == "RESTRICTED"

        diagnosis_meta = encrypted_data["diagnosis"]["metadata"]
        assert diagnosis_meta["sensitivity_type"] == "PHI"
        assert "HIPAA" in diagnosis_meta["compliance_tags"]
        assert "GDPR" in diagnosis_meta["compliance_tags"]

    def test_audit_log_generation(self):
        """Test audit log generation for encryption activities."""
        compliance_encryption = ComplianceFieldEncryption()
        data = {"ssn": "123-45-6789", "email": "test@example.com"}

        # Encrypt data (should generate audit log)
        compliance_encryption.encrypt_sensitive_data(data)

        # Check audit log
        audit_log = compliance_encryption.get_audit_log()
        assert len(audit_log) == 2  # Two sensitive fields encrypted

        for entry in audit_log:
            assert entry["action"] == "encrypt"
            assert "timestamp" in entry
            assert entry["field"] in ["ssn", "email"]
            assert entry["sensitivity_type"] in ["PII"]


class TestKeyRotationManager:
    """Test key rotation functionality."""

    def test_key_rotation_basic(self):
        """Test basic key rotation."""
        service = EncryptionService()
        rotation_manager = KeyRotationManager(service)

        # Should need rotation for new key
        assert rotation_manager.should_rotate_key("test_key") is True

        # Rotate key
        new_key = rotation_manager.rotate_key("test_key")
        assert len(new_key) == 32  # 256-bit key

        # Should not need immediate rotation
        assert rotation_manager.should_rotate_key("test_key") is False

    def test_key_versioning(self):
        """Test key versioning functionality."""
        service = EncryptionService()
        rotation_manager = KeyRotationManager(service)

        # Rotate key multiple times
        key1 = rotation_manager.rotate_key("test_key")
        key2 = rotation_manager.rotate_key("test_key")
        key3 = rotation_manager.rotate_key("test_key")

        assert key1 != key2 != key3

        # Test version retrieval
        assert rotation_manager.get_active_key("test_key") == key3
        assert rotation_manager.get_key_by_version("test_key", 1) == key1
        assert rotation_manager.get_key_by_version("test_key", 2) == key2
        assert rotation_manager.get_key_by_version("test_key", 3) == key3


@pytest.mark.asyncio
class TestAsyncEncryptionService:
    """Test asynchronous encryption functionality."""

    async def test_async_encryption(self):
        """Test asynchronous encryption and decryption."""
        async_service = AsyncEncryptionService()
        plaintext = "Async encrypted data"

        # Async encrypt
        ciphertext = await async_service.encrypt_async(plaintext)
        assert ciphertext != plaintext

        # Async decrypt
        decrypted_bytes = await async_service.decrypt_async(ciphertext)
        decrypted = decrypted_bytes.decode("utf-8")
        assert decrypted == plaintext

    async def test_batch_encryption(self):
        """Test batch encryption functionality."""
        async_service = AsyncEncryptionService()
        data_list = [
            "First sensitive item",
            "Second sensitive item",
            "Third sensitive item",
        ]

        # Batch encrypt
        encrypted_list = await async_service.encrypt_batch(data_list)
        assert len(encrypted_list) == 3
        assert all(
            item != original for item, original in zip(encrypted_list, data_list)
        )

        # Batch decrypt
        decrypted_list = await async_service.decrypt_batch(encrypted_list)
        decrypted_strings = [item.decode("utf-8") for item in decrypted_list]
        assert decrypted_strings == data_list


class TestPIIEncryption:
    """Test PII-specific encryption functions."""

    def test_pii_encryption_with_compliance_metadata(self):
        """Test PII encryption with compliance metadata."""
        medical_data = "Patient has Type 2 diabetes and hypertension"

        # Encrypt as medical data
        encrypted_obj = encrypt_pii(medical_data, data_type="medical")

        assert "encrypted_data" in encrypted_obj
        assert "metadata" in encrypted_obj

        metadata = encrypted_obj["metadata"]
        assert metadata["data_type"] == "medical"
        assert "HIPAA" in metadata["compliance_tags"]
        assert "GDPR" in metadata["compliance_tags"]
        assert metadata["retention_period"] == "7_years"

        # Decrypt PII
        decrypted = decrypt_pii(encrypted_obj)
        assert decrypted == medical_data

    def test_different_pii_types(self):
        """Test encryption of different PII types."""
        # Email PII
        email_encrypted = encrypt_pii("user@example.com", data_type="email")
        assert email_encrypted["metadata"]["data_type"] == "email"
        assert email_encrypted["metadata"]["retention_period"] == "5_years"

        # Medical PII
        medical_encrypted = encrypt_pii("Blood pressure: 140/90", data_type="medical")
        assert medical_encrypted["metadata"]["data_type"] == "medical"
        assert medical_encrypted["metadata"]["retention_period"] == "7_years"
        assert "HIPAA" in medical_encrypted["metadata"]["compliance_tags"]


class TestEncryptionIntegration:
    """Integration tests for encryption system."""

    def test_global_encryption_service(self):
        """Test global encryption service singleton."""
        service1 = get_encryption_service()
        service2 = get_encryption_service()

        # Should be the same instance
        assert service1 is service2

        # Should work for encryption/decryption
        plaintext = "Global service test"
        ciphertext = service1.encrypt_string(plaintext)
        decrypted = service2.decrypt_string(ciphertext)
        assert decrypted == plaintext

    def test_end_to_end_compliance_workflow(self):
        """Test complete encryption workflow for compliance."""
        # Simulate user data with mixed sensitivity
        user_data = {
            "user_id": "12345",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "555-1234",
            "medical_record": "Patient has diabetes",
            "favorite_color": "blue",
            "age": 35,
        }

        # Use compliance encryption
        compliance_encryption = ComplianceFieldEncryption()
        encrypted_result = compliance_encryption.encrypt_sensitive_data(user_data)

        # Verify sensitive fields are encrypted
        assert encrypted_result["name"]["_compliance"] is True
        assert encrypted_result["email"]["_compliance"] is True
        assert encrypted_result["medical_record"]["_compliance"] is True

        # Verify non-sensitive fields are not encrypted
        assert encrypted_result["favorite_color"] == "blue"
        assert encrypted_result["age"] == 35

        # Verify audit trail
        audit_log = compliance_encryption.get_audit_log()
        assert len(audit_log) > 0

        # Test decryption (selective)
        field_encryption = FieldEncryption()
        decrypted_result = field_encryption.decrypt_fields(encrypted_result)

        assert decrypted_result["name"] == "John Doe"
        assert decrypted_result["email"] == "john.doe@example.com"
        assert decrypted_result["medical_record"] == "Patient has diabetes"

    def test_encryption_error_handling(self):
        """Test encryption service error handling."""
        service = EncryptionService()

        # Test invalid ciphertext
        with pytest.raises(ValueError):
            service.decrypt_string("invalid_ciphertext")

        # Test empty data
        empty_encrypted = service.encrypt_string("")
        empty_decrypted = service.decrypt_string(empty_encrypted)
        assert empty_decrypted == ""

        # Test None data
        field_encryption = FieldEncryption()
        data_with_none = {"valid_field": "data", "none_field": None}
        encrypted_data = field_encryption.encrypt_fields(data_with_none, ["none_field"])
        assert encrypted_data["none_field"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
