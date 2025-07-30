#!/usr/bin/env python3
"""
Script for rotating secrets in GENESIS API.

This script helps with:
- Generating new secure secrets
- Updating .env files
- Providing instructions for external service rotation
"""

import os
import secrets
import string
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.logging_config import get_logger

logger = get_logger(__name__)


class SecretRotator:
    """Handles secret rotation for the application."""
    
    def __init__(self, env_file: str = ".env"):
        self.env_file = Path(env_file)
        self.backup_dir = Path("backups/secrets")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_jwt_secret(self, length: int = 64) -> str:
        """Generate a secure JWT secret."""
        return secrets.token_urlsafe(length)
    
    def generate_api_key(self, prefix: str = "ngx", length: int = 32) -> str:
        """Generate a secure API key with prefix."""
        key = secrets.token_urlsafe(length)
        return f"{prefix}_{key}"
    
    def generate_password(self, length: int = 24) -> str:
        """Generate a secure password with mixed characters."""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        # Ensure at least one of each type
        password = [
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.digits),
            secrets.choice("!@#$%^&*")
        ]
        # Fill the rest
        for _ in range(length - 4):
            password.append(secrets.choice(alphabet))
        
        # Shuffle and return
        secrets.SystemRandom().shuffle(password)
        return ''.join(password)
    
    def backup_current_env(self):
        """Backup current .env file."""
        if self.env_file.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f".env.backup_{timestamp}"
            
            # Copy content
            backup_path.write_text(self.env_file.read_text())
            logger.info(f"Backed up current .env to {backup_path}")
            return backup_path
        return None
    
    def read_env_file(self) -> Dict[str, str]:
        """Read current .env file into dictionary."""
        env_vars = {}
        
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        
        return env_vars
    
    def write_env_file(self, env_vars: Dict[str, str], template_file: str = ".env.example"):
        """Write updated env vars to file, preserving comments from template."""
        output_lines = []
        template_path = Path(template_file)
        
        # Read template to preserve structure and comments
        if template_path.exists():
            with open(template_path, 'r') as f:
                for line in f:
                    stripped = line.strip()
                    
                    # Keep comments and empty lines
                    if not stripped or stripped.startswith('#'):
                        output_lines.append(line.rstrip())
                    elif '=' in line:
                        key = line.split('=', 1)[0].strip()
                        if key in env_vars:
                            output_lines.append(f"{key}={env_vars[key]}")
                        else:
                            output_lines.append(line.rstrip())
        
        # Write the new file
        with open(self.env_file, 'w') as f:
            f.write('\n'.join(output_lines))
        
        logger.info(f"Updated {self.env_file}")
    
    def rotate_internal_secrets(self) -> Dict[str, str]:
        """Rotate internally generated secrets."""
        rotated = {}
        
        # JWT Secret
        rotated['JWT_SECRET'] = self.generate_jwt_secret()
        logger.info("✅ Generated new JWT_SECRET")
        
        # Redis password (if using local Redis)
        rotated['REDIS_PASSWORD'] = self.generate_password()
        logger.info("✅ Generated new REDIS_PASSWORD")
        
        return rotated
    
    def get_external_rotation_instructions(self) -> List[str]:
        """Get instructions for rotating external service secrets."""
        instructions = [
            "\n🔄 External Service Secret Rotation Instructions:\n",
            "1. Google Cloud / Vertex AI:",
            "   - Go to: https://console.cloud.google.com/apis/credentials",
            "   - Create new service account key",
            "   - Download JSON and update GOOGLE_APPLICATION_CREDENTIALS path",
            "   - Delete old key after confirming new one works\n",
            
            "2. Supabase:",
            "   - Go to: https://app.supabase.com/project/[your-project]/settings/api",
            "   - Regenerate anon key and service role key",
            "   - Update SUPABASE_ANON_KEY and SUPABASE_KEY",
            "   - Note: This will affect all existing clients!\n",
            
            "3. ElevenLabs:",
            "   - Go to: https://elevenlabs.io/speech-synthesis",
            "   - Profile → API Keys → Generate new key",
            "   - Update ELEVENLABS_API_KEY",
            "   - Delete old key\n",
            
            "4. OpenAI (if used):",
            "   - Go to: https://platform.openai.com/api-keys",
            "   - Create new secret key",
            "   - Update OPENAI_API_KEY",
            "   - Delete old key\n",
            
            "5. Database (if external):",
            "   - Update database user password",
            "   - Update connection strings",
            "   - Test connectivity before removing old credentials\n",
            
            "⚠️  IMPORTANT:",
            "- Rotate secrets one at a time",
            "- Test each service after rotation",
            "- Keep backup of old .env file",
            "- Update all deployment environments",
            "- Notify team members of changes"
        ]
        
        return instructions
    
    def perform_rotation(self, rotate_all: bool = False):
        """Perform secret rotation."""
        print("🔐 GENESIS Secret Rotation Tool\n")
        
        # Backup current configuration
        backup_path = self.backup_current_env()
        if backup_path:
            print(f"✅ Backed up current configuration to: {backup_path}\n")
        
        # Read current env
        current_env = self.read_env_file()
        
        # Rotate internal secrets
        print("🔄 Rotating internal secrets...")
        rotated_secrets = self.rotate_internal_secrets()
        
        # Update env vars
        current_env.update(rotated_secrets)
        
        # Write updated file
        self.write_env_file(current_env)
        print("\n✅ Internal secrets rotated successfully!")
        
        # Show external rotation instructions
        instructions = self.get_external_rotation_instructions()
        for instruction in instructions:
            print(instruction)
        
        # Security checklist
        print("\n📋 Post-Rotation Checklist:")
        print("[ ] Update secrets in all deployment environments")
        print("[ ] Update CI/CD pipeline secrets")
        print("[ ] Test all integrations")
        print("[ ] Remove old credentials from external services")
        print("[ ] Notify team members")
        print("[ ] Update documentation if needed")
        
        return rotated_secrets


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Rotate secrets for GENESIS API")
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to .env file (default: .env)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Rotate all secrets including external (shows instructions)"
    )
    
    args = parser.parse_args()
    
    # Create rotator
    rotator = SecretRotator(env_file=args.env_file)
    
    # Perform rotation
    try:
        rotator.perform_rotation(rotate_all=args.all)
    except Exception as e:
        logger.error(f"Error during rotation: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()