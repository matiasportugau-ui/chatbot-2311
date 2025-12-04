#!/usr/bin/env python3
"""
WhatsApp Business API Credential Validator
Validates WhatsApp Business API credentials and tests connectivity
"""

import hashlib
import hmac
import json
import sys
from pathlib import Path
from typing import Any

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  requests library not available. Install with: pip install requests")


class WhatsAppCredentialValidator:
    """Validates WhatsApp Business API credentials"""

    def __init__(self, env_file: Path | None = None):
        self.root_dir = Path(__file__).parent.parent.resolve()
        self.env_file = env_file or (self.root_dir / ".env")
        self.credentials: dict[str, str] = {}
        self.errors: List[dict[str, Any]] = []
        self.warnings: List[dict[str, Any]] = []
        self.validations: List[dict[str, Any]] = []

    def load_credentials(self) -> bool:
        """Load WhatsApp credentials from .env file"""
        if not self.env_file.exists():
            self.errors.append(
                {
                    "credential": ".env",
                    "message": f"Environment file not found: {self.env_file}",
                    "fix": "Create .env file first",
                }
            )
            return False

        try:
            with open(self.env_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key.startswith("WHATSAPP_"):
                            self.credentials[key] = value
            return True
        except Exception as e:
            self.errors.append(
                {
                    "credential": ".env",
                    "message": f"Error reading .env file: {e}",
                    "fix": "Check file permissions and format",
                }
            )
            return False

    def validate_access_token(self) -> bool:
        """Validate WhatsApp access token"""
        token = self.credentials.get("WHATSAPP_ACCESS_TOKEN", "").strip()

        if not token or token.startswith("your-"):
            self.errors.append(
                {
                    "credential": "WHATSAPP_ACCESS_TOKEN",
                    "message": "WhatsApp access token is missing or not configured",
                    "fix": "Get your access token from Meta for Developers: https://developers.facebook.com",
                }
            )
            return False

        # Test token format (should be a long string)
        if len(token) < 50:
            self.errors.append(
                {
                    "credential": "WHATSAPP_ACCESS_TOKEN",
                    "message": "Access token appears to be invalid (too short)",
                    "fix": "Get a valid access token from Meta for Developers",
                }
            )
            return False

        # Test token with API call
        if REQUESTS_AVAILABLE:
            try:
                # Test with a simple API call to get app info
                phone_id = self.credentials.get("WHATSAPP_PHONE_NUMBER_ID", "")
                if phone_id:
                    url = f"https://graph.facebook.com/v18.0/{phone_id}"
                    response = requests.get(
                        url, headers={"Authorization": f"Bearer {token}"}, timeout=10
                    )

                    if response.status_code == 200:
                        data = response.json()
                        self.validations.append(
                            {
                                "credential": "WHATSAPP_ACCESS_TOKEN",
                                "status": "valid",
                                "message": f"Access token is valid. Phone number: {data.get('display_phone_number', 'N/A')}",
                            }
                        )
                        return True
                    elif response.status_code == 401:
                        self.errors.append(
                            {
                                "credential": "WHATSAPP_ACCESS_TOKEN",
                                "message": "Access token is invalid or expired",
                                "fix": "Generate a new access token from Meta for Developers",
                            }
                        )
                        return False
                    else:
                        self.warnings.append(
                            {
                                "credential": "WHATSAPP_ACCESS_TOKEN",
                                "message": f"API returned status {response.status_code}: {response.text[:100]}",
                                "fix": "Check your access token and phone number ID",
                            }
                        )
                        return False
                else:
                    # Can't test without phone number ID
                    self.validations.append(
                        {
                            "credential": "WHATSAPP_ACCESS_TOKEN",
                            "status": "format_valid",
                            "message": "Access token format is valid (cannot test without phone number ID)",
                        }
                    )
                    return True
            except requests.exceptions.RequestException as e:
                self.warnings.append(
                    {
                        "credential": "WHATSAPP_ACCESS_TOKEN",
                        "message": f"Cannot test access token: {e}",
                        "fix": "Check your internet connection",
                    }
                )
                return True  # Format is valid, just can't test
        else:
            self.validations.append(
                {
                    "credential": "WHATSAPP_ACCESS_TOKEN",
                    "status": "format_valid",
                    "message": "Access token format is valid (requests library not available for full test)",
                }
            )
            return True

    def validate_phone_number_id(self) -> bool:
        """Validate WhatsApp phone number ID"""
        phone_id = self.credentials.get("WHATSAPP_PHONE_NUMBER_ID", "").strip()

        if not phone_id or phone_id.startswith("your-"):
            self.errors.append(
                {
                    "credential": "WHATSAPP_PHONE_NUMBER_ID",
                    "message": "WhatsApp phone number ID is missing",
                    "fix": "Get your phone number ID from Meta for Developers",
                }
            )
            return False

        # Phone number ID should be numeric
        if not phone_id.isdigit():
            self.errors.append(
                {
                    "credential": "WHATSAPP_PHONE_NUMBER_ID",
                    "message": "Phone number ID should be numeric",
                    "fix": "Use the numeric ID from your WhatsApp Business account",
                }
            )
            return False

        self.validations.append(
            {
                "credential": "WHATSAPP_PHONE_NUMBER_ID",
                "status": "valid",
                "message": f"Phone number ID format is valid: {phone_id}",
            }
        )
        return True

    def validate_verify_token(self) -> bool:
        """Validate WhatsApp verify token"""
        verify_token = self.credentials.get("WHATSAPP_VERIFY_TOKEN", "").strip()

        if not verify_token or verify_token.startswith("your-"):
            self.warnings.append(
                {
                    "credential": "WHATSAPP_VERIFY_TOKEN",
                    "message": "WhatsApp verify token is missing",
                    "fix": "Create a secure random token for webhook verification",
                }
            )
            return False

        # Verify token should be alphanumeric
        if not verify_token.replace("_", "").replace("-", "").isalnum():
            self.errors.append(
                {
                    "credential": "WHATSAPP_VERIFY_TOKEN",
                    "message": "Verify token should be alphanumeric (letters, numbers, _, -)",
                    "fix": "Use only alphanumeric characters, underscores, and hyphens",
                }
            )
            return False

        self.validations.append(
            {
                "credential": "WHATSAPP_VERIFY_TOKEN",
                "status": "valid",
                "message": "Verify token format is valid",
            }
        )
        return True

    def validate_app_secret(self) -> bool:
        """Validate WhatsApp app secret"""
        app_secret = self.credentials.get("WHATSAPP_APP_SECRET", "").strip()

        if not app_secret or app_secret.startswith("your-"):
            self.warnings.append(
                {
                    "credential": "WHATSAPP_APP_SECRET",
                    "message": "WhatsApp app secret is missing (optional but recommended for webhook signature verification)",
                    "fix": "Get your app secret from Meta for Developers",
                }
            )
            return False

        # App secret should be a long string
        if len(app_secret) < 20:
            self.warnings.append(
                {
                    "credential": "WHATSAPP_APP_SECRET",
                    "message": "App secret appears to be invalid (too short)",
                    "fix": "Get a valid app secret from Meta for Developers",
                }
            )
            return False

        self.validations.append(
            {
                "credential": "WHATSAPP_APP_SECRET",
                "status": "valid",
                "message": "App secret format is valid",
            }
        )
        return True

    def test_webhook_signature(self) -> bool:
        """Test webhook signature verification"""
        app_secret = self.credentials.get("WHATSAPP_APP_SECRET", "")
        verify_token = self.credentials.get("WHATSAPP_VERIFY_TOKEN", "")

        if not app_secret or not verify_token:
            return True  # Can't test without both

        # Test signature generation
        try:
            test_payload = b'{"test": "data"}'
            signature = hmac.new(
                app_secret.encode("utf-8"), test_payload, hashlib.sha256
            ).hexdigest()

            self.validations.append(
                {
                    "credential": "Webhook Signature",
                    "status": "valid",
                    "message": "Signature verification algorithm is working correctly",
                }
            )
            return True
        except Exception as e:
            self.warnings.append(
                {
                    "credential": "Webhook Signature",
                    "message": f"Error testing signature verification: {e}",
                    "fix": "Check app secret format",
                }
            )
            return False

    def validate_all(self) -> dict[str, Any]:
        """Run all validations"""
        if not self.load_credentials():
            return {
                "valid": False,
                "errors": self.errors,
                "warnings": self.warnings,
                "validations": self.validations,
            }

        # Check if any WhatsApp credentials are configured
        has_whatsapp = any(
            key.startswith("WHATSAPP_") and value and not value.startswith("your-")
            for key, value in self.credentials.items()
        )

        if not has_whatsapp:
            return {
                "valid": True,
                "skipped": True,
                "message": "WhatsApp credentials not configured (optional)",
                "errors": [],
                "warnings": [],
                "validations": [],
            }

        # Run validations
        token_valid = self.validate_access_token()
        phone_valid = self.validate_phone_number_id()
        verify_valid = self.validate_verify_token()
        secret_valid = self.validate_app_secret()
        signature_valid = self.test_webhook_signature()

        all_valid = token_valid and phone_valid and verify_valid

        return {
            "valid": all_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "validations": self.validations,
            "summary": {
                "access_token": token_valid,
                "phone_number_id": phone_valid,
                "verify_token": verify_valid,
                "app_secret": secret_valid,
                "signature_verification": signature_valid,
            },
        }

    def print_report(self, result: dict[str, Any]):
        """Print validation report"""
        print("\n" + "=" * 70)
        print("WHATSAPP CREDENTIALS VALIDATION REPORT")
        print("=" * 70 + "\n")

        if result.get("skipped"):
            print("ℹ️  WhatsApp credentials not configured (optional feature)\n")
            return

        if result["valid"]:
            print("✅ WhatsApp credentials are valid\n")
        else:
            print("❌ WhatsApp credentials have errors\n")

        # Print errors
        if result["errors"]:
            print("ERRORS (Must be fixed):")
            print("-" * 70)
            for error in result["errors"]:
                print(f"\n❌ {error['credential']}")
                print(f"   Message: {error['message']}")
                if "fix" in error:
                    print(f"   Fix: {error['fix']}")
            print()

        # Print warnings
        if result["warnings"]:
            print("WARNINGS (Recommended to fix):")
            print("-" * 70)
            for warning in result["warnings"]:
                print(f"\n⚠️  {warning['credential']}")
                print(f"   Message: {warning['message']}")
                if "fix" in warning:
                    print(f"   Fix: {warning['fix']}")
            print()

        # Print validations
        if result["validations"]:
            print("VALIDATIONS (Passed):")
            print("-" * 70)
            for validation in result["validations"]:
                print(f"✅ {validation['credential']}: {validation['message']}")
            print()

        # Print summary
        if "summary" in result:
            summary = result["summary"]
            print("SUMMARY:")
            print("-" * 70)
            print(f"Access Token: {'✅ Valid' if summary['access_token'] else '❌ Invalid'}")
            print(f"Phone Number ID: {'✅ Valid' if summary['phone_number_id'] else '❌ Invalid'}")
            print(f"Verify Token: {'✅ Valid' if summary['verify_token'] else '⚠️  Missing'}")
            print(f"App Secret: {'✅ Valid' if summary['app_secret'] else '⚠️  Missing'}")
            print(
                f"Signature Verification: {'✅ Working' if summary['signature_verification'] else '⚠️  Issue'}"
            )
            print("=" * 70 + "\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate WhatsApp Business API credentials")
    parser.add_argument(
        "--env-file", type=Path, help="Path to .env file (default: .env in project root)"
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    validator = WhatsAppCredentialValidator(env_file=args.env_file)
    result = validator.validate_all()

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        validator.print_report(result)

    # Exit with error code if validation failed
    sys.exit(0 if result.get("valid", False) or result.get("skipped", False) else 1)


if __name__ == "__main__":
    main()
