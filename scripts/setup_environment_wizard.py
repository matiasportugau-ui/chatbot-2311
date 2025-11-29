#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Environment Setup Wizard
Guides users through setting up environment variables for first-time setup
"""

import os
import sys
import secrets
from pathlib import Path
from typing import Dict, Optional

# Import validator
sys.path.insert(0, str(Path(__file__).parent))
from validate_environment import EnvironmentValidator


class EnvironmentWizard:
    """Interactive wizard for environment setup"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent.resolve()
        self.env_file = self.root_dir / ".env"
        self.env_example = self.root_dir / "env.example"
        self.env_vars: Dict[str, str] = {}
        
    def print_header(self):
        """Print wizard header"""
        print("\n" + "=" * 70)
        print("BMC CHATBOT SYSTEM - ENVIRONMENT SETUP WIZARD")
        print("=" * 70)
        print("\nThis wizard will guide you through setting up your environment variables.")
        print("You can skip optional variables by pressing Enter.\n")
    
    def load_existing(self) -> bool:
        """Load existing .env file if it exists"""
        if self.env_file.exists():
            print(f"Found existing .env file: {self.env_file}")
            response = input("Do you want to update it? (y/n, default: n): ").strip().lower()
            if response != 'y':
                return False
            
            # Load existing values
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        self.env_vars[key] = value
            return True
        return False
    
    def load_template(self):
        """Load template from env.example"""
        if self.env_example.exists():
            with open(self.env_example, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        # Only set if not already in env_vars
                        if key not in self.env_vars:
                            self.env_vars[key] = value
    
    def prompt_required(self):
        """Prompt for required variables"""
        print("\n" + "=" * 70)
        print("REQUIRED VARIABLES")
        print("=" * 70 + "\n")
        
        required = {
            "OPENAI_API_KEY": {
                "description": "OpenAI API key (required for AI features)",
                "help": "Get your API key from https://platform.openai.com/api-keys",
                "format": "sk-..."
            }
        }
        
        for var, config in required.items():
            current = self.env_vars.get(var, "")
            if current and not current.startswith("your-") and current:
                print(f"✅ {var} is already set")
                response = input(f"  Keep current value? (y/n, default: y): ").strip().lower()
                if response != 'n':
                    continue
            
            print(f"\n{var}")
            print(f"  Description: {config['description']}")
            print(f"  Help: {config['help']}")
            if "format" in config:
                print(f"  Format: {config['format']}")
            
            while True:
                value = input(f"  Enter value (required): ").strip()
                if value:
                    if "format" in config and config["format"] == "sk-...":
                        if not value.startswith("sk-") or len(value) < 20:
                            print("  ⚠️  Invalid format. Should start with 'sk-' and be at least 20 characters")
                            continue
                    self.env_vars[var] = value
                    break
                else:
                    print("  ⚠️  This variable is required. Please enter a value.")
    
    def prompt_optional(self):
        """Prompt for optional variables"""
        print("\n" + "=" * 70)
        print("OPTIONAL VARIABLES")
        print("=" * 70)
        print("\nPress Enter to skip optional variables.\n")
        
        optional = {
            "MONGODB_URI": {
                "description": "MongoDB connection string",
                "default": "mongodb://localhost:27017/bmc_chat",
                "help": "Leave default for local MongoDB, or use MongoDB Atlas connection string"
            },
            "WHATSAPP_ACCESS_TOKEN": {
                "description": "WhatsApp Business API access token",
                "help": "Get from Meta for Developers: https://developers.facebook.com"
            },
            "WHATSAPP_PHONE_NUMBER_ID": {
                "description": "WhatsApp Business phone number ID",
                "help": "Numeric ID from Meta for Developers"
            },
            "WHATSAPP_VERIFY_TOKEN": {
                "description": "WhatsApp webhook verify token",
                "help": "Create a secure random token for webhook verification"
            },
            "NEXTAUTH_SECRET": {
                "description": "NextAuth.js secret for session encryption",
                "generate": True,
                "help": "Auto-generated if not provided"
            },
            "NEXTAUTH_URL": {
                "description": "NextAuth.js base URL",
                "default": "http://localhost:3000",
                "help": "Change for production deployment"
            },
            "PY_CHAT_SERVICE_URL": {
                "description": "Python chat service API URL",
                "default": "http://localhost:8000",
                "help": "Change if API runs on different port"
            }
        }
        
        for var, config in optional.items():
            current = self.env_vars.get(var, "")
            
            # Auto-generate if needed
            if "generate" in config and config.get("generate") and not current:
                generated = secrets.token_urlsafe(32)
                print(f"\n{var}")
                print(f"  Description: {config['description']}")
                print(f"  Generated value: {generated}")
                response = input(f"  Use generated value? (y/n, default: y): ").strip().lower()
                if response != 'n':
                    self.env_vars[var] = generated
                    continue
            
            # Use default if available
            if not current or current.startswith("your-"):
                default = config.get("default", "")
                if default:
                    print(f"\n{var}")
                    print(f"  Description: {config['description']}")
                    print(f"  Help: {config.get('help', '')}")
                    print(f"  Default: {default}")
                    value = input(f"  Enter value (or press Enter for default): ").strip()
                    if value:
                        self.env_vars[var] = value
                    elif default:
                        self.env_vars[var] = default
                else:
                    print(f"\n{var}")
                    print(f"  Description: {config['description']}")
                    print(f"  Help: {config.get('help', '')}")
                    value = input(f"  Enter value (or press Enter to skip): ").strip()
                    if value:
                        self.env_vars[var] = value
            else:
                print(f"\n✅ {var} is already set: {current[:20]}...")
                response = input(f"  Keep current value? (y/n, default: y): ").strip().lower()
                if response == 'n':
                    value = input(f"  Enter new value (or press Enter to skip): ").strip()
                    if value:
                        self.env_vars[var] = value
    
    def save_env_file(self) -> bool:
        """Save environment variables to .env file"""
        try:
            # Read template to preserve comments and structure
            lines = []
            if self.env_example.exists():
                with open(self.env_example, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            
            # Create new .env file
            with open(self.env_file, 'w', encoding='utf-8') as f:
                for line in lines:
                    stripped = line.strip()
                    # Skip empty lines and comments
                    if not stripped or stripped.startswith('#'):
                        f.write(line)
                        continue
                    
                    # Replace values for variables we have
                    if '=' in stripped:
                        key = stripped.split('=', 1)[0].strip()
                        if key in self.env_vars:
                            f.write(f"{key}={self.env_vars[key]}\n")
                        else:
                            f.write(line)
                    else:
                        f.write(line)
                
                # Add any new variables not in template
                template_keys = set()
                for line in lines:
                    if '=' in line and not line.strip().startswith('#'):
                        template_keys.add(line.split('=', 1)[0].strip())
                
                for key, value in self.env_vars.items():
                    if key not in template_keys:
                        f.write(f"{key}={value}\n")
            
            return True
        except Exception as e:
            print(f"\n❌ Error saving .env file: {e}")
            return False
    
    def validate_setup(self) -> bool:
        """Validate the setup"""
        print("\n" + "=" * 70)
        print("VALIDATING SETUP")
        print("=" * 70 + "\n")
        
        validator = EnvironmentValidator(self.env_file)
        result = validator.validate_all()
        
        if result["valid"]:
            print("✅ All required variables are valid!\n")
        else:
            print("❌ Some required variables have errors:\n")
            for error in result["errors"]:
                print(f"  ❌ {error['variable']}: {error['message']}")
            print()
        
        if result["warnings"]:
            print("⚠️  Warnings (optional variables):\n")
            for warning in result["warnings"]:
                print(f"  ⚠️  {warning['variable']}: {warning['message']}")
            print()
        
        return result["valid"]
    
    def run(self):
        """Run the wizard"""
        self.print_header()
        
        # Load existing or template
        if not self.load_existing():
            self.load_template()
        
        # Prompt for required variables
        self.prompt_required()
        
        # Prompt for optional variables
        self.prompt_optional()
        
        # Save .env file
        print("\n" + "=" * 70)
        print("SAVING CONFIGURATION")
        print("=" * 70 + "\n")
        
        if self.save_env_file():
            print(f"✅ Environment file saved to: {self.env_file}\n")
        else:
            print("❌ Failed to save environment file\n")
            return False
        
        # Validate setup
        if self.validate_setup():
            print("\n" + "=" * 70)
            print("SETUP COMPLETE!")
            print("=" * 70)
            print("\n✅ Your environment is configured and ready to use.")
            print(f"\nNext steps:")
            print(f"  1. Review your .env file: {self.env_file}")
            print(f"  2. Run: python unified_launcher.py --setup-only")
            print(f"  3. Start the system: python unified_launcher.py\n")
            return True
        else:
            print("\n⚠️  Setup completed with errors. Please fix the errors above.")
            return False


def main():
    """Main entry point"""
    wizard = EnvironmentWizard()
    success = wizard.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

