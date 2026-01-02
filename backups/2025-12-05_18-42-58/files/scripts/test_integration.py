#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite
Tests all system components and integrations
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

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

# Import validator
sys.path.insert(0, str(Path(__file__).parent))
from validate_environment import EnvironmentValidator


class IntegrationTester:
    """Comprehensive integration testing"""

    def __init__(self):
        self.root_dir = Path(__file__).parent.parent.resolve()
        self.results: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {"total": 0, "passed": 0, "failed": 0, "skipped": 0},
        }

    def test_api_server(self) -> dict[str, Any]:
        """Test API server health and endpoints"""
        test_name = "API Server"
        result = {"name": test_name, "status": "skipped", "message": "", "details": {}}

        if not REQUESTS_AVAILABLE:
            result["message"] = "requests library not available"
            return result

        # Get API URL from environment
        api_url = os.getenv("PY_CHAT_SERVICE_URL", "http://localhost:8000")

        try:
            # Test health endpoint
            health_url = f"{api_url}/health"
            response = requests.get(health_url, timeout=5)

            if response.status_code == 200:
                result["status"] = "passed"
                result["message"] = "API server is healthy"
                result["details"]["health_check"] = response.json()

                # Test chat endpoint (if available)
                try:
                    chat_url = f"{api_url}/chat/process"
                    test_request = {"mensaje": "test", "telefono": "test123"}
                    chat_response = requests.post(chat_url, json=test_request, timeout=10)
                    if chat_response.status_code in [200, 201]:
                        result["details"]["chat_endpoint"] = "working"
                    else:
                        result["details"]["chat_endpoint"] = f"status {chat_response.status_code}"
                except Exception as e:
                    result["details"]["chat_endpoint"] = f"error: {str(e)[:50]}"
            else:
                result["status"] = "failed"
                result["message"] = f"API server returned status {response.status_code}"
        except requests.exceptions.ConnectionError:
            result["status"] = "failed"
            result["message"] = f"Cannot connect to API server at {api_url}"
            result["details"]["suggestion"] = "Ensure API server is running: python api_server.py"
        except Exception as e:
            result["status"] = "failed"
            result["message"] = f"Error testing API server: {e}"

        return result

    def test_knowledge_base(self) -> dict[str, Any]:
        """Test knowledge base loading"""
        test_name = "Knowledge Base"
        result = {"name": test_name, "status": "skipped", "message": "", "details": {}}

        # Check for knowledge files
        knowledge_files = [
            "conocimiento_consolidado.json",
            "base_conocimiento_final.json",
            "conocimiento_completo.json",
            "base_conocimiento_exportada.json",
        ]

        found_files = []
        for filename in knowledge_files:
            filepath = self.root_dir / filename
            if filepath.exists():
                found_files.append(filename)
                # Check if file is valid JSON
                try:
                    with open(filepath, encoding="utf-8") as f:
                        data = json.load(f)
                        result["details"][filename] = {
                            "exists": True,
                            "valid_json": True,
                            "size_kb": filepath.stat().st_size / 1024,
                            "has_interactions": "interacciones" in data,
                            "has_patterns": "patrones_venta" in data,
                        }
                except json.JSONDecodeError:
                    result["details"][filename] = {
                        "exists": True,
                        "valid_json": False,
                        "error": "Invalid JSON",
                    }

        if found_files:
            result["status"] = "passed"
            result["message"] = f"Found {len(found_files)} knowledge file(s)"
            result["details"]["files_found"] = found_files
        else:
            result["status"] = "failed"
            result["message"] = "No knowledge base files found"
            result["details"]["suggestion"] = "Run: python consolidar_conocimiento.py"

        return result

    def test_mongodb(self) -> dict[str, Any]:
        """Test MongoDB connectivity"""
        test_name = "MongoDB"
        result = {"name": test_name, "status": "skipped", "message": "", "details": {}}

        if not PYMONGO_AVAILABLE:
            result["message"] = "pymongo library not available"
            return result

        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/bmc_chat")

        if not mongodb_uri or mongodb_uri.startswith("your-"):
            result["status"] = "skipped"
            result["message"] = "MongoDB URI not configured (optional)"
            return result

        try:
            client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=3000)
            client.admin.command("ping")

            # Test database access
            db_name = mongodb_uri.split("/")[-1].split("?")[0] if "/" in mongodb_uri else "bmc_chat"
            db = client.get_database(db_name)
            collections = db.list_collection_names()

            result["status"] = "passed"
            result["message"] = "MongoDB connection successful"
            result["details"] = {
                "database": db_name,
                "collections": collections,
                "collection_count": len(collections),
            }

            client.close()
        except Exception as e:
            result["status"] = "failed"
            result["message"] = f"Cannot connect to MongoDB: {e}"
            result["details"]["suggestion"] = "Ensure MongoDB is running: docker start bmc-mongodb"

        return result

    def test_openai(self) -> dict[str, Any]:
        """Test OpenAI API connectivity"""
        test_name = "OpenAI API"
        result = {"name": test_name, "status": "skipped", "message": "", "details": {}}

        if not REQUESTS_AVAILABLE:
            result["message"] = "requests library not available"
            return result

        api_key = os.getenv("OPENAI_API_KEY", "")

        if not api_key or api_key.startswith("your-"):
            result["status"] = "skipped"
            result["message"] = "OpenAI API key not configured"
            return result

        try:
            response = requests.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10,
            )

            if response.status_code == 200:
                models = response.json().get("data", [])
                result["status"] = "passed"
                result["message"] = "OpenAI API is accessible"
                result["details"] = {
                    "models_available": len(models),
                    "sample_models": [m.get("id") for m in models[:3]],
                }
            elif response.status_code == 401:
                result["status"] = "failed"
                result["message"] = "OpenAI API key is invalid"
            else:
                result["status"] = "failed"
                result["message"] = f"OpenAI API returned status {response.status_code}"
        except requests.exceptions.RequestException as e:
            result["status"] = "failed"
            result["message"] = f"Cannot connect to OpenAI API: {e}"

        return result

    def test_whatsapp_webhook(self) -> dict[str, Any]:
        """Test WhatsApp webhook (if configured)"""
        test_name = "WhatsApp Webhook"
        result = {"name": test_name, "status": "skipped", "message": "", "details": {}}

        access_token = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
        phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")

        if not access_token or access_token.startswith("your-"):
            result["status"] = "skipped"
            result["message"] = "WhatsApp credentials not configured (optional)"
            return result

        if not REQUESTS_AVAILABLE:
            result["message"] = "requests library not available"
            return result

        try:
            # Test phone number ID access
            url = f"https://graph.facebook.com/v18.0/{phone_id}"
            response = requests.get(
                url, headers={"Authorization": f"Bearer {access_token}"}, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                result["status"] = "passed"
                result["message"] = "WhatsApp API is accessible"
                result["details"] = {
                    "phone_number": data.get("display_phone_number", "N/A"),
                    "verified_name": data.get("verified_name", "N/A"),
                }
            else:
                result["status"] = "failed"
                result["message"] = f"WhatsApp API returned status {response.status_code}"
        except Exception as e:
            result["status"] = "failed"
            result["message"] = f"Error testing WhatsApp API: {e}"

        return result

    def test_n8n(self) -> dict[str, Any]:
        """Test n8n workflow (if configured)"""
        test_name = "n8n Workflow"
        result = {"name": test_name, "status": "skipped", "message": "", "details": {}}

        n8n_url = os.getenv("N8N_WEBHOOK_URL_EXTERNAL", "http://localhost:5678")

        if not REQUESTS_AVAILABLE:
            result["message"] = "requests library not available"
            return result

        try:
            # Test n8n health
            health_url = f"{n8n_url.replace('/webhook/', '')}/healthz"
            response = requests.get(health_url, timeout=5)

            if response.status_code == 200:
                result["status"] = "passed"
                result["message"] = "n8n is running"
                result["details"]["n8n_url"] = n8n_url
            else:
                result["status"] = "failed"
                result["message"] = f"n8n returned status {response.status_code}"
        except requests.exceptions.ConnectionError:
            result["status"] = "skipped"
            result["message"] = "n8n is not running (optional)"
        except Exception as e:
            result["status"] = "failed"
            result["message"] = f"Error testing n8n: {e}"

        return result

    def test_nextjs_frontend(self) -> dict[str, Any]:
        """Test Next.js frontend (if running)"""
        test_name = "Next.js Frontend"
        result = {"name": test_name, "status": "skipped", "message": "", "details": {}}

        if not REQUESTS_AVAILABLE:
            result["message"] = "requests library not available"
            return result

        nextjs_url = os.getenv("NEXTAUTH_URL", "http://localhost:3000")

        try:
            response = requests.get(nextjs_url, timeout=5)

            if response.status_code == 200:
                result["status"] = "passed"
                result["message"] = "Next.js frontend is running"
                result["details"]["url"] = nextjs_url
            else:
                result["status"] = "failed"
                result["message"] = f"Next.js returned status {response.status_code}"
        except requests.exceptions.ConnectionError:
            result["status"] = "skipped"
            result["message"] = "Next.js frontend is not running (optional)"
        except Exception as e:
            result["status"] = "failed"
            result["message"] = f"Error testing Next.js: {e}"

        return result

    def test_environment(self) -> dict[str, Any]:
        """Test environment configuration"""
        test_name = "Environment Configuration"
        result = {"name": test_name, "status": "skipped", "message": "", "details": {}}

        try:
            validator = EnvironmentValidator()
            validation_result = validator.validate_all()

            if validation_result["valid"]:
                result["status"] = "passed"
                result["message"] = "Environment configuration is valid"
            else:
                result["status"] = "failed"
                result["message"] = f"Environment has {len(validation_result['errors'])} error(s)"

            result["details"] = {
                "errors": len(validation_result["errors"]),
                "warnings": len(validation_result["warnings"]),
                "validations": len(validation_result["validations"]),
            }
        except Exception as e:
            result["status"] = "failed"
            result["message"] = f"Error validating environment: {e}"

        return result

    def run_all_tests(self) -> dict[str, Any]:
        """Run all integration tests"""
        print("\n" + "=" * 70)
        print("INTEGRATION TEST SUITE")
        print("=" * 70 + "\n")
        print("Running comprehensive integration tests...\n")

        tests = [
            self.test_environment,
            self.test_api_server,
            self.test_knowledge_base,
            self.test_mongodb,
            self.test_openai,
            self.test_whatsapp_webhook,
            self.test_n8n,
            self.test_nextjs_frontend,
        ]

        for test_func in tests:
            test_result = test_func()
            test_name = test_result["name"]
            self.results["tests"][test_name] = test_result

            # Update summary
            self.results["summary"]["total"] += 1
            if test_result["status"] == "passed":
                self.results["summary"]["passed"] += 1
                print(f"✅ {test_name}: {test_result['message']}")
            elif test_result["status"] == "failed":
                self.results["summary"]["failed"] += 1
                print(f"❌ {test_name}: {test_result['message']}")
            else:
                self.results["summary"]["skipped"] += 1
                print(f"⏭️  {test_name}: {test_result['message']}")

        return self.results

    def print_summary(self):
        """Print test summary"""
        summary = self.results["summary"]

        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70 + "\n")
        print(f"Total Tests: {summary['total']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"⏭️  Skipped: {summary['skipped']}")
        print()

        if summary["failed"] == 0:
            print("✅ All critical tests passed!")
        else:
            print(f"⚠️  {summary['failed']} test(s) failed. Review details above.")
        print("=" * 70 + "\n")

    def save_report(self, output_file: Path | None = None) -> Path:
        """Save test report to JSON file"""
        if output_file is None:
            output_file = self.root_dir / "logs" / "integration_test_report.json"

        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        return output_file


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Run comprehensive integration tests")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--save-report", action="store_true", help="Save report to JSON file")

    args = parser.parse_args()

    tester = IntegrationTester()
    results = tester.run_all_tests()

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        tester.print_summary()

    if args.save_report:
        report_file = tester.save_report()
        print(f"Report saved to: {report_file}")

    # Exit with error code if tests failed
    sys.exit(0 if results["summary"]["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
