#!/usr/bin/env python3
"""
Script to help rotate credentials for NGX Agents.

This script guides you through the process of rotating all sensitive credentials
and provides commands to update them in various services.

IMPORTANT: Run this script in a secure environment and never share the output.
"""

import os
import sys
import secrets
import string
import json
from datetime import datetime
from typing import Dict, List, Optional
import subprocess

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_secure_password(length: int = 32) -> str:
    """Generate a cryptographically secure password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_jwt_secret() -> str:
    """Generate a secure JWT secret (256 bits)."""
    return secrets.token_urlsafe(32)


def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)


def generate_encryption_key() -> str:
    """Generate a secure encryption key for AES-256."""
    return secrets.token_bytes(32).hex()


class CredentialRotator:
    """Manages the credential rotation process."""
    
    def __init__(self):
        self.timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.new_credentials: Dict[str, str] = {}
        self.rotation_log: List[str] = []
    
    def log(self, message: str):
        """Log a rotation action."""
        log_entry = f"[{datetime.utcnow().isoformat()}] {message}"
        self.rotation_log.append(log_entry)
        print(log_entry)
    
    def generate_all_credentials(self) -> Dict[str, str]:
        """Generate new credentials for all services."""
        self.log("Starting credential generation...")
        
        credentials = {
            # JWT
            "JWT_SECRET": generate_jwt_secret(),
            
            # Database
            "REDIS_PASSWORD": generate_secure_password(32),
            
            # Encryption
            "ENCRYPTION_KEY": generate_encryption_key(),
            "ENCRYPTION_SALT": secrets.token_hex(16),
            
            # Note: External service credentials must be rotated through their platforms
            "INSTRUCTIONS": {
                "GOOGLE_CLOUD": "Rotate through Google Cloud Console > APIs & Services > Credentials",
                "SUPABASE": "Rotate through Supabase Dashboard > Settings > API",
                "ELEVENLABS": "Rotate through ElevenLabs Dashboard > Profile > API Keys",
                "OPENAI": "Rotate through OpenAI Platform > API Keys",
            }
        }
        
        self.new_credentials = credentials
        self.log(f"Generated {len(credentials) - 1} new credentials")
        
        return credentials
    
    def save_credentials_securely(self, output_dir: str = "credentials_backup"):
        """Save new credentials to a secure location."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save credentials
        credentials_file = os.path.join(output_dir, f"credentials_{self.timestamp}.json")
        with open(credentials_file, 'w') as f:
            json.dump(self.new_credentials, f, indent=2)
        
        # Save rotation log
        log_file = os.path.join(output_dir, f"rotation_log_{self.timestamp}.txt")
        with open(log_file, 'w') as f:
            f.write('\n'.join(self.rotation_log))
        
        # Set secure permissions
        os.chmod(credentials_file, 0o600)
        os.chmod(log_file, 0o600)
        
        self.log(f"Credentials saved to {credentials_file}")
        self.log(f"Rotation log saved to {log_file}")
        
        return credentials_file
    
    def generate_env_update(self) -> str:
        """Generate .env update commands."""
        env_updates = []
        
        for key, value in self.new_credentials.items():
            if key != "INSTRUCTIONS" and isinstance(value, str):
                env_updates.append(f"{key}={value}")
        
        return '\n'.join(env_updates)
    
    def generate_gcloud_commands(self) -> List[str]:
        """Generate Google Cloud Secret Manager commands."""
        commands = []
        
        for key, value in self.new_credentials.items():
            if key != "INSTRUCTIONS" and isinstance(value, str):
                secret_name = f"ngx-agents-{key.lower().replace('_', '-')}"
                commands.append(
                    f"echo -n '{value}' | gcloud secrets create {secret_name} --data-file=-"
                )
        
        return commands
    
    def print_rotation_guide(self):
        """Print a comprehensive rotation guide."""
        print("\n" + "="*60)
        print("CREDENTIAL ROTATION GUIDE")
        print("="*60)
        
        print("\n1. BACKUP CURRENT CREDENTIALS")
        print("   - Make a backup of your current .env file")
        print("   - Note down any custom configurations")
        
        print("\n2. UPDATE LOCAL .env FILE")
        print("   Copy these values to your .env file:")
        print("-"*40)
        print(self.generate_env_update())
        print("-"*40)
        
        print("\n3. UPDATE GOOGLE SECRET MANAGER (Production)")
        print("   Run these commands:")
        print("-"*40)
        for cmd in self.generate_gcloud_commands():
            print(f"   {cmd}")
        print("-"*40)
        
        print("\n4. ROTATE EXTERNAL SERVICE CREDENTIALS")
        if "INSTRUCTIONS" in self.new_credentials:
            for service, instruction in self.new_credentials["INSTRUCTIONS"].items():
                print(f"   - {service}: {instruction}")
        
        print("\n5. UPDATE SERVICES")
        print("   - Restart Redis with new password")
        print("   - Update any CI/CD pipelines")
        print("   - Update any documentation")
        
        print("\n6. VERIFY")
        print("   - Test authentication")
        print("   - Test encryption/decryption")
        print("   - Check all integrations")
        
        print("\n7. SECURE CLEANUP")
        print("   - Delete old credentials from .env")
        print("   - Remove credential backup files after confirming everything works")
        print("   - Clear shell history: history -c")
        
        print("\n" + "="*60)
        print("IMPORTANT SECURITY NOTES:")
        print("- Never commit credentials to git")
        print("- Use secure channels to share credentials")
        print("- Enable MFA on all service accounts")
        print("- Set up alerts for credential usage")
        print("="*60 + "\n")


def main():
    """Main function to run credential rotation."""
    print("NGX Agents Credential Rotation Tool")
    print("===================================\n")
    
    # Check if running in production
    env = os.getenv("ENV", "development")
    if env == "production":
        response = input("WARNING: Running in production. Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Rotation cancelled.")
            return
    
    rotator = CredentialRotator()
    
    # Generate new credentials
    credentials = rotator.generate_all_credentials()
    
    # Save credentials
    backup_file = rotator.save_credentials_securely()
    
    # Print rotation guide
    rotator.print_rotation_guide()
    
    print(f"\n✅ Credential generation complete!")
    print(f"📁 Backup saved to: {backup_file}")
    print(f"⚠️  Remember to delete the backup file after updating all services")
    
    # Offer to create .env.new file
    response = input("\nCreate .env.new file with updated values? (yes/no): ")
    if response.lower() == "yes":
        # Read current .env
        current_env = {}
        if os.path.exists(".env"):
            with open(".env", 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        current_env[key.strip()] = value.strip()
        
        # Update with new credentials
        for key, value in credentials.items():
            if key != "INSTRUCTIONS" and isinstance(value, str):
                current_env[key] = value
        
        # Write .env.new
        with open(".env.new", 'w') as f:
            f.write("# NGX Agents Configuration - Rotated Credentials\n")
            f.write(f"# Generated: {datetime.utcnow().isoformat()}\n")
            f.write("# IMPORTANT: Review and rename to .env after verification\n\n")
            
            for key, value in sorted(current_env.items()):
                f.write(f"{key}={value}\n")
        
        os.chmod(".env.new", 0o600)
        print("✅ Created .env.new with updated credentials")
        print("   Review the file and rename to .env when ready")


if __name__ == "__main__":
    main()