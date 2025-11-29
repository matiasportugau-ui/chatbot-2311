#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Environment Variable Validator
Validates all required and optional environment variables for the BMC Chatbot System
"""

import os
import re
import sys
import json
import socket
import urllib.parse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from urllib.parse import urlparse

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from pymongo import MongoClient
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False


class EnvironmentValidator:
    """Validates environment variables comprehensively"""
    
    def __init__(self, env_file: Optional[Path] = None):
        self.root_dir = Path(__file__).parent.parent.resolve()
        self.env_file = env_file or (self.root_dir / ".env")
        self.env_vars: Dict[str, str] = {}
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.validations: List[Dict[str, Any]] = []
        
    def load_environment(self) -> bool:
        """Load environment variables from .env file"""
        if not self.env_file.exists():
            self.errors.append({
                "variable": ".env",
                "message": f"Environment file not found: {self.env_file}",
                "fix": f"Create .env file from env.example: cp env.example .env"
            })
            return False
        
        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    # Parse KEY=VALUE
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        self.env_vars[key] = value
            return True
        except Exception as e:
            self.errors.append({
                "variable": ".env",
                "message": f"Error reading .env file: {e}",
                "fix": "Check file permissions and format"
            })
            return False
    
    def validate_required(self) -> bool:
        """Validate required environment variables"""
        required_vars = {
            "OPENAI_API_KEY": {
                "description": "OpenAI API key for AI features",
                "format": "sk-...",
                "test": self._test_openai_key
            }
        }
        
        all_valid = True
        for var, config in required_vars.items():
            value = self.env_vars.get(var, "").strip()
            
            if not value or value.startswith("your-") or value == "":
                self.errors.append({
                    "variable": var,
                    "message": f"Required variable {var} is missing or not configured",
                    "description": config.get("description", ""),
                    "fix": f"Set {var} in .env file. {config.get('description', '')}"
                })
                all_valid = False
            else:
                # Test format
                if "format" in config:
                    if not self._validate_format(var, value, config["format"]):
                        all_valid = False
                
                # Test functionality if test function provided
                if "test" in config and config["test"]:
                    test_result = config["test"](value)
                    if not test_result["valid"]:
                        self.errors.append({
                            "variable": var,
                            "message": test_result["message"],
                            "fix": test_result.get("fix", "")
                        })
                        all_valid = False
                    else:
                        self.validations.append({
                            "variable": var,
                            "status": "valid",
                            "message": test_result.get("message", "Valid")
                        })
        
        return all_valid
    
    def validate_optional(self) -> bool:
        """Validate optional environment variables"""
        optional_vars = {
            "MONGODB_URI": {
                "description": "MongoDB connection string",
                "format": "mongodb://...",
                "test": self._test_mongodb_uri
            },
            "WHATSAPP_ACCESS_TOKEN": {
                "description": "WhatsApp Business API access token",
                "format": "EAA...",
                "test": None  # Will be tested separately
            },
            "WHATSAPP_PHONE_NUMBER_ID": {
                "description": "WhatsApp Business phone number ID",
                "format": "numeric",
                "test": None
            },
            "WHATSAPP_VERIFY_TOKEN": {
                "description": "WhatsApp webhook verify token",
                "format": "alphanumeric",
                "test": None
            },
            "NEXTAUTH_SECRET": {
                "description": "NextAuth.js secret for session encryption",
                "format": "random string",
                "test": None,
                "generate": self._generate_nextauth_secret
            },
            "NEXTAUTH_URL": {
                "description": "NextAuth.js base URL",
                "format": "http://... or https://...",
                "test": self._test_url
            },
            "PY_CHAT_SERVICE_URL": {
                "description": "Python chat service API URL",
                "format": "http://... or https://...",
                "test": self._test_url
            }
        }
        
        all_valid = True
        for var, config in optional_vars.items():
            value = self.env_vars.get(var, "").strip()
            
            if not value or value.startswith("your-"):
                # Check if we should generate it
                if "generate" in config and config["generate"]:
                    generated = config["generate"]()
                    if generated:
                        self.warnings.append({
                            "variable": var,
                            "message": f"{var} is missing but can be auto-generated",
                            "fix": f"Add to .env: {var}={generated}",
                            "generated_value": generated
                        })
                else:
                    self.warnings.append({
                        "variable": var,
                        "message": f"Optional variable {var} is not configured",
                        "description": config.get("description", ""),
                        "fix": f"Configure {var} in .env if needed"
                    })
                continue
            
            # Validate format
            if "format" in config:
                if not self._validate_format(var, value, config["format"]):
                    all_valid = False
            
            # Test functionality if test function provided
            if "test" in config and config["test"]:
                test_result = config["test"](value)
                if not test_result["valid"]:
                    self.warnings.append({
                        "variable": var,
                        "message": test_result["message"],
                        "fix": test_result.get("fix", "")
                    })
                else:
                    self.validations.append({
                        "variable": var,
                        "status": "valid",
                        "message": test_result.get("message", "Valid")
                    })
        
        return all_valid
    
    def _validate_format(self, var: str, value: str, format_hint: str) -> bool:
        """Validate value format"""
        if format_hint == "sk-...":
            if not value.startswith("sk-") or len(value) < 20:
                self.errors.append({
                    "variable": var,
                    "message": f"{var} format is invalid. Should start with 'sk-' and be at least 20 characters",
                    "fix": f"Get a valid OpenAI API key from https://platform.openai.com/api-keys"
                })
                return False
            return True
        
        elif format_hint == "mongodb://...":
            if not value.startswith("mongodb://") and not value.startswith("mongodb+srv://"):
                self.errors.append({
                    "variable": var,
                    "message": f"{var} format is invalid. Should start with 'mongodb://' or 'mongodb+srv://'",
                    "fix": "Use format: mongodb://localhost:27017/dbname or mongodb+srv://cluster.mongodb.net/dbname"
                })
                return False
            return True
        
        elif format_hint == "http://... or https://...":
            return self._test_url(value)["valid"]
        
        elif format_hint == "numeric":
            if not value.isdigit():
                self.errors.append({
                    "variable": var,
                    "message": f"{var} should be numeric",
                    "fix": f"Use a numeric value for {var}"
                })
                return False
            return True
        
        elif format_hint == "alphanumeric":
            if not re.match(r'^[a-zA-Z0-9_-]+$', value):
                self.errors.append({
                    "variable": var,
                    "message": f"{var} should be alphanumeric (letters, numbers, _, -)",
                    "fix": f"Use only alphanumeric characters, underscores, and hyphens"
                })
                return False
            return True
        
        return True
    
    def _test_url(self, url: str) -> Dict[str, Any]:
        """Test if URL is valid and accessible"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return {
                    "valid": False,
                    "message": f"Invalid URL format: {url}",
                    "fix": "Use format: http://hostname:port or https://hostname:port"
                }
            
            # Test if host is reachable (for localhost)
            if parsed.hostname in ["localhost", "127.0.0.1"]:
                port = parsed.port or (443 if parsed.scheme == "https" else 80)
                try:
                    sock = socket.create_connection((parsed.hostname, port), timeout=2)
                    sock.close()
                except (socket.error, OSError):
                    return {
                        "valid": False,
                        "message": f"Cannot connect to {url}",
                        "fix": f"Ensure the service is running on {parsed.hostname}:{port}"
                    }
            
            return {"valid": True, "message": "URL is valid and reachable"}
        except Exception as e:
            return {
                "valid": False,
                "message": f"Error validating URL: {e}",
                "fix": "Check URL format"
            }
    
    def _test_openai_key(self, api_key: str) -> Dict[str, Any]:
        """Test OpenAI API key by making a test request"""
        if not REQUESTS_AVAILABLE:
            return {
                "valid": True,
                "message": "Format valid (requests library not available for full test)"
            }
        
        try:
            response = requests.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5
            )
            
            if response.status_code == 200:
                return {
                    "valid": True,
                    "message": "OpenAI API key is valid and working"
                }
            elif response.status_code == 401:
                return {
                    "valid": False,
                    "message": "OpenAI API key is invalid or expired",
                    "fix": "Get a new API key from https://platform.openai.com/api-keys"
                }
            else:
                return {
                    "valid": False,
                    "message": f"OpenAI API returned status {response.status_code}",
                    "fix": "Check your API key and OpenAI service status"
                }
        except requests.exceptions.RequestException as e:
            return {
                "valid": False,
                "message": f"Cannot connect to OpenAI API: {e}",
                "fix": "Check your internet connection and OpenAI service status"
            }
    
    def _test_mongodb_uri(self, uri: str) -> Dict[str, Any]:
        """Test MongoDB connection"""
        if not PYMONGO_AVAILABLE:
            return {
                "valid": True,
                "message": "Format valid (pymongo not available for connection test)"
            }
        
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=3000)
            client.admin.command("ping")
            client.close()
            return {
                "valid": True,
                "message": "MongoDB connection successful"
            }
        except Exception as e:
            return {
                "valid": False,
                "message": f"Cannot connect to MongoDB: {e}",
                "fix": "Check MongoDB URI and ensure MongoDB is running"
            }
    
    def _generate_nextauth_secret(self) -> Optional[str]:
        """Generate a secure random secret for NextAuth"""
        try:
            import secrets
            return secrets.token_urlsafe(32)
        except ImportError:
            import random
            import string
            chars = string.ascii_letters + string.digits + "-_"
            return ''.join(random.choice(chars) for _ in range(32))
    
    def validate_all(self) -> Dict[str, Any]:
        """Run all validations"""
        if not self.load_environment():
            return {
                "valid": False,
                "errors": self.errors,
                "warnings": self.warnings,
                "validations": self.validations
            }
        
        required_valid = self.validate_required()
        optional_valid = self.validate_optional()
        
        return {
            "valid": required_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "validations": self.validations,
            "summary": {
                "total_errors": len(self.errors),
                "total_warnings": len(self.warnings),
                "total_validations": len(self.validations),
                "required_valid": required_valid,
                "optional_valid": optional_valid
            }
        }
    
    def print_report(self, result: Dict[str, Any]):
        """Print validation report"""
        print("\n" + "=" * 70)
        print("ENVIRONMENT VALIDATION REPORT")
        print("=" * 70 + "\n")
        
        if result["valid"]:
            print("✅ Required environment variables are valid\n")
        else:
            print("❌ Required environment variables have errors\n")
        
        # Print errors
        if result["errors"]:
            print("ERRORS (Must be fixed):")
            print("-" * 70)
            for error in result["errors"]:
                print(f"\n❌ {error['variable']}")
                print(f"   Message: {error['message']}")
                if "fix" in error:
                    print(f"   Fix: {error['fix']}")
            print()
        
        # Print warnings
        if result["warnings"]:
            print("WARNINGS (Optional but recommended):")
            print("-" * 70)
            for warning in result["warnings"]:
                print(f"\n⚠️  {warning['variable']}")
                print(f"   Message: {warning['message']}")
                if "fix" in warning:
                    print(f"   Fix: {warning['fix']}")
                if "generated_value" in warning:
                    print(f"   Generated value: {warning['generated_value']}")
            print()
        
        # Print validations
        if result["validations"]:
            print("VALIDATIONS (Passed):")
            print("-" * 70)
            for validation in result["validations"]:
                print(f"✅ {validation['variable']}: {validation['message']}")
            print()
        
        # Print summary
        summary = result["summary"]
        print("SUMMARY:")
        print("-" * 70)
        print(f"Errors: {summary['total_errors']}")
        print(f"Warnings: {summary['total_warnings']}")
        print(f"Validations: {summary['total_validations']}")
        print(f"Required variables: {'✅ Valid' if summary['required_valid'] else '❌ Invalid'}")
        print(f"Optional variables: {'✅ Valid' if summary['optional_valid'] else '⚠️  Some issues'}")
        print("=" * 70 + "\n")
    
    def save_report(self, result: Dict[str, Any], output_file: Optional[Path] = None) -> Path:
        """Save validation report to JSON file"""
        if output_file is None:
            output_file = self.root_dir / "logs" / "environment_validation.json"
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        return output_file


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate environment variables")
    parser.add_argument(
        "--env-file",
        type=Path,
        help="Path to .env file (default: .env in project root)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--save-report",
        action="store_true",
        help="Save report to JSON file"
    )
    
    args = parser.parse_args()
    
    validator = EnvironmentValidator(env_file=args.env_file)
    result = validator.validate_all()
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        validator.print_report(result)
    
    if args.save_report:
        report_file = validator.save_report(result)
        print(f"Report saved to: {report_file}")
    
    # Exit with error code if validation failed
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()

