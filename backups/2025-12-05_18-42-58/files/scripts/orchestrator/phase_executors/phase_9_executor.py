"""
Phase 9 Executor: Production Security Hardening
Comprehensive security implementation and analysis
"""

from .base_executor import BaseExecutor
from typing import List, Dict, Any, Optional
import json
import sys
import os
import re
from pathlib import Path

ORCHESTRATOR_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ORCHESTRATOR_DIR.parent.parent))


class Phase9Executor(BaseExecutor):
    """Executes Phase 9: Production Security Hardening"""

    def __init__(self, phase: int, state_manager):
        super().__init__(phase, state_manager)
        self.workspace_path = Path.cwd()

    def execute(self) -> List[str]:
        """Execute Phase 9: Production Security Hardening"""
        self.log_info("Starting Phase 9: Production Security Hardening")

        output_dir = self.ensure_output_dir("consolidation/security")

        # T9.1: WhatsApp webhook signature validation
        self.log_info("T9.1: Analyzing WhatsApp webhook signature validation...")
        webhook_whatsapp_file = self._execute_t9_1(output_dir)
        if webhook_whatsapp_file:
            self.add_output(webhook_whatsapp_file)

        # T9.2: n8n webhook signature validation
        self.log_info("T9.2: Analyzing n8n webhook signature validation...")
        webhook_n8n_file = self._execute_t9_2(output_dir)
        if webhook_n8n_file:
            self.add_output(webhook_n8n_file)

        # T9.3: Secrets management analysis
        self.log_info("T9.3: Analyzing secrets management...")
        secrets_file = self._execute_t9_3(output_dir)
        if secrets_file:
            self.add_output(secrets_file)

        # T9.4: Rate limiting analysis
        self.log_info("T9.4: Analyzing rate limiting implementation...")
        rate_limiting_file = self._execute_t9_4(output_dir)
        if rate_limiting_file:
            self.add_output(rate_limiting_file)

        # T9.5: CORS configuration analysis
        self.log_info("T9.5: Analyzing CORS configuration...")
        cors_file = self._execute_t9_5(output_dir)
        if cors_file:
            self.add_output(cors_file)

        # T9.6: API authentication analysis
        self.log_info("T9.6: Analyzing API authentication...")
        auth_file = self._execute_t9_6(output_dir)
        if auth_file:
            self.add_output(auth_file)

        # T9.7: Security audit
        self.log_info("T9.7: Conducting security audit...")
        audit_file = self._execute_t9_7(output_dir)
        if audit_file:
            self.add_output(audit_file)

        # T9.8: Penetration testing plan
        self.log_info("T9.8: Creating penetration testing plan...")
        pentest_file = self._execute_t9_8(output_dir)
        if pentest_file:
            self.add_output(pentest_file)

        # Generate comprehensive security report
        self.log_info("Generating comprehensive security report...")
        summary_file = self._generate_security_summary(output_dir)
        if summary_file:
            self.add_output(summary_file)

        self.log_success("Phase 9 completed: Security hardening analysis completed")
        return self.collect_outputs()

    def _execute_t9_1(self, output_dir: Path) -> Optional[str]:
        """T9.1: Analyze WhatsApp webhook signature validation"""
        try:
            whatsapp_file = self.workspace_path / "integracion_whatsapp.py"

            analysis = {
                "phase": 9,
                "task": "T9.1 - WhatsApp Webhook Signature Validation",
                "timestamp": self._get_timestamp(),
                "status": "analyzed",
                "current_state": {},
                "recommendations": [],
                "implementation_required": True
            }

            if whatsapp_file.exists():
                content = whatsapp_file.read_text(encoding='utf-8')

                # Check for webhook validation
                has_validation = "validate_webhook_request" in content or "webhook_validation" in content
                has_hmac = "hmac" in content.lower() or "sha256" in content.lower()
                has_secret = "WEBHOOK_SECRET" in content or "webhook_secret" in content

                analysis["current_state"] = {
                    "file_exists": True,
                    "has_validation_import": "webhook_validation" in content,
                    "has_hmac_validation": has_hmac,
                    "has_secret_config": has_secret,
                    "validation_implemented": has_validation and has_hmac
                }

                if not has_validation or not has_hmac:
                    analysis["recommendations"].append({
                        "priority": "P0 - Critical",
                        "action": "Implement HMAC SHA256 signature validation",
                        "details": "Add webhook signature verification using HMAC SHA256"
                    })

                if not has_secret:
                    analysis["recommendations"].append({
                        "priority": "P0 - Critical",
                        "action": "Configure webhook secret",
                        "details": "Add WHATSAPP_WEBHOOK_SECRET to environment variables"
                    })
            else:
                analysis["current_state"] = {
                    "file_exists": False,
                    "validation_implemented": False
                }
                analysis["recommendations"].append({
                    "priority": "P0 - Critical",
                    "action": "Create WhatsApp integration file",
                    "details": "WhatsApp integration file not found"
                })

            output_file = output_dir / "webhook_validation_whatsapp.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)

            self.log_success(f"T9.1 completed: {output_file}")
            return str(output_file)

        except Exception as e:
            self.log_error(f"Error executing T9.1: {e}")
            return None

    def _execute_t9_2(self, output_dir: Path) -> Optional[str]:
        """T9.2: Analyze n8n webhook signature validation"""
        try:
            n8n_file = self.workspace_path / "n8n_integration.py"

            analysis = {
                "phase": 9,
                "task": "T9.2 - n8n Webhook Signature Validation",
                "timestamp": self._get_timestamp(),
                "status": "analyzed",
                "current_state": {},
                "recommendations": [],
                "implementation_required": True
            }

            if n8n_file.exists():
                content = n8n_file.read_text(encoding='utf-8')

                has_validation = "validate" in content.lower() and "webhook" in content.lower()
                has_signature_check = "signature" in content.lower()

                analysis["current_state"] = {
                    "file_exists": True,
                    "has_validation": has_validation,
                    "has_signature_check": has_signature_check,
                    "validation_implemented": has_validation and has_signature_check
                }

                if not has_validation:
                    analysis["recommendations"].append({
                        "priority": "P0 - Critical",
                        "action": "Implement n8n webhook validation",
                        "details": "Add signature verification for n8n webhooks"
                    })
            else:
                analysis["current_state"] = {
                    "file_exists": False,
                    "validation_implemented": False
                }

            output_file = output_dir / "webhook_validation_n8n.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)

            self.log_success(f"T9.2 completed: {output_file}")
            return str(output_file)

        except Exception as e:
            self.log_error(f"Error executing T9.2: {e}")
            return None

    def _execute_t9_3(self, output_dir: Path) -> Optional[str]:
        """T9.3: Analyze secrets management"""
        try:
            analysis = {
                "phase": 9,
                "task": "T9.3 - Secrets Management Migration",
                "timestamp": self._get_timestamp(),
                "status": "analyzed",
                "current_state": {},
                "recommendations": [],
                "implementation_required": True
            }

            # Check docker-compose.yml
            docker_compose = self.workspace_path / "docker-compose.yml"
            hardcoded_creds = []

            if docker_compose.exists():
                content = docker_compose.read_text(encoding='utf-8')

                # Look for hardcoded credentials
                patterns = [
                    r'password:\s*["\']([^"\']+)["\']',
                    r'PASSWORD:\s*["\']([^"\']+)["\']',
                    r'token:\s*["\']([^"\']+)["\']',
                    r'TOKEN:\s*["\']([^"\']+)["\']',
                ]

                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if match and match not in ["${", "$", ""]:
                            hardcoded_creds.append({
                                "type": "docker-compose",
                                "pattern": pattern,
                                "found": True
                            })

            # Check .env files
            env_files = list(self.workspace_path.glob("**/.env*"))
            env_files = [f for f in env_files if f.is_file()]

            analysis["current_state"] = {
                "docker_compose_exists": docker_compose.exists(),
                "hardcoded_credentials_found": len(hardcoded_creds) > 0,
                "hardcoded_credentials_count": len(hardcoded_creds),
                "env_files_found": len(env_files),
                "env_files": [str(f.relative_to(self.workspace_path)) for f in env_files[:10]]
            }

            if hardcoded_creds:
                analysis["recommendations"].append({
                    "priority": "P0 - Critical",
                    "action": "Remove hardcoded credentials",
                    "details": f"Found {len(hardcoded_creds)} potential hardcoded credentials in docker-compose.yml"
                })

            analysis["recommendations"].append({
                "priority": "P0 - Critical",
                "action": "Migrate to Docker secrets or HashiCorp Vault",
                "details": "Set up secure secrets management system"
            })

            analysis["recommendations"].append({
                "priority": "P1 - Important",
                "action": "Document secret rotation strategy",
                "details": "Create documentation for rotating secrets"
            })

            output_file = output_dir / "secrets_migration.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)

            self.log_success(f"T9.3 completed: {output_file}")
            return str(output_file)

        except Exception as e:
            self.log_error(f"Error executing T9.3: {e}")
            return None

    def _execute_t9_4(self, output_dir: Path) -> Optional[str]:
        """T9.4: Analyze rate limiting implementation"""
        try:
            api_file = self.workspace_path / "api_server.py"

            analysis = {
                "phase": 9,
                "task": "T9.4 - Rate Limiting Implementation",
                "timestamp": self._get_timestamp(),
                "status": "analyzed",
                "current_state": {},
                "recommendations": [],
                "implementation_required": True
            }

            if api_file.exists():
                content = api_file.read_text(encoding='utf-8')

                has_slowapi = "slowapi" in content.lower()
                has_limiter = "limiter" in content.lower()
                has_rate_limit_decorator = "@limiter" in content or "@app.limiter" in content

                # Check requirements.txt
                req_file = self.workspace_path / "requirements.txt"
                slowapi_in_requirements = False
                if req_file.exists():
                    req_content = req_file.read_text(encoding='utf-8')
                    slowapi_in_requirements = "slowapi" in req_content.lower()

                analysis["current_state"] = {
                    "file_exists": True,
                    "has_slowapi_import": has_slowapi,
                    "has_limiter": has_limiter,
                    "has_rate_limit_decorators": has_rate_limit_decorator,
                    "slowapi_in_requirements": slowapi_in_requirements,
                    "rate_limiting_implemented": has_slowapi and has_limiter and has_rate_limit_decorator
                }

                if not slowapi_in_requirements:
                    analysis["recommendations"].append({
                        "priority": "P1 - Important",
                        "action": "Add slowapi to requirements.txt",
                        "details": "Install slowapi package for rate limiting"
                    })

                if not has_rate_limit_decorator:
                    analysis["recommendations"].append({
                        "priority": "P1 - Important",
                        "action": "Implement rate limiting on endpoints",
                        "details": "Add @limiter.limit() decorators to API endpoints"
                    })
            else:
                analysis["current_state"] = {
                    "file_exists": False,
                    "rate_limiting_implemented": False
                }

            # Recommended limits
            analysis["recommended_limits"] = {
                "/chat/process": "10 req/min",
                "/cotizacion/generar": "5 req/min",
                "/webhook/*": "20 req/min"
            }

            output_file = output_dir / "rate_limiting.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)

            self.log_success(f"T9.4 completed: {output_file}")
            return str(output_file)

        except Exception as e:
            self.log_error(f"Error executing T9.4: {e}")
            return None

    def _execute_t9_5(self, output_dir: Path) -> Optional[str]:
        """T9.5: Analyze CORS configuration"""
        try:
            api_file = self.workspace_path / "api_server.py"

            analysis = {
                "phase": 9,
                "task": "T9.5 - CORS Configuration",
                "timestamp": self._get_timestamp(),
                "status": "analyzed",
                "current_state": {},
                "recommendations": [],
                "implementation_required": True
            }

            if api_file.exists():
                content = api_file.read_text(encoding='utf-8')

                # Check for wildcard CORS
                has_wildcard = '"*"' in content or "'*'" in content
                has_cors_middleware = "CORSMiddleware" in content
                has_allow_origins = "allow_origins" in content

                # Check if using environment variable
                uses_env_var = "CORS_ALLOWED_ORIGINS" in content or "ALLOWED_ORIGINS" in content

                # Check for production check
                has_prod_check = "ENVIRONMENT" in content and "production" in content.lower()

                analysis["current_state"] = {
                    "file_exists": True,
                    "has_cors_middleware": has_cors_middleware,
                    "has_allow_origins": has_allow_origins,
                    "uses_wildcard": has_wildcard,
                    "uses_environment_variable": uses_env_var,
                    "has_production_check": has_prod_check,
                    "cors_properly_configured": has_cors_middleware and uses_env_var and has_prod_check and not has_wildcard
                }

                if has_wildcard and not has_prod_check:
                    analysis["recommendations"].append({
                        "priority": "P0 - Critical",
                        "action": "Remove wildcard CORS configuration",
                        "details": "Replace allow_origins=['*'] with specific domains"
                    })

                if not uses_env_var:
                    analysis["recommendations"].append({
                        "priority": "P0 - Critical",
                        "action": "Use environment variable for CORS origins",
                        "details": "Configure CORS_ALLOWED_ORIGINS environment variable"
                    })
            else:
                analysis["current_state"] = {
                    "file_exists": False,
                    "cors_properly_configured": False
                }

            analysis["recommended_domains"] = [
                "https://whatsapp.business.facebook.com",
                "https://n8n.yourdomain.com",
                "https://dashboard.yourdomain.com"
            ]

            output_file = output_dir / "cors_config.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)

            self.log_success(f"T9.5 completed: {output_file}")
            return str(output_file)

        except Exception as e:
            self.log_error(f"Error executing T9.5: {e}")
            return None

    def _execute_t9_6(self, output_dir: Path) -> Optional[str]:
        """T9.6: Analyze API authentication"""
        try:
            api_file = self.workspace_path / "api_server.py"

            analysis = {
                "phase": 9,
                "task": "T9.6 - API Authentication",
                "timestamp": self._get_timestamp(),
                "status": "analyzed",
                "current_state": {},
                "recommendations": [],
                "implementation_required": True
            }

            if api_file.exists():
                content = api_file.read_text(encoding='utf-8')

                has_jwt = "jwt" in content.lower() or "pyjwt" in content.lower()
                has_auth_middleware = "authentication" in content.lower() or "auth" in content.lower()
                has_api_key = "api_key" in content.lower() or "apikey" in content.lower()
                has_bearer = "bearer" in content.lower()

                analysis["current_state"] = {
                    "file_exists": True,
                    "has_jwt": has_jwt,
                    "has_auth_middleware": has_auth_middleware,
                    "has_api_key": has_api_key,
                    "has_bearer_token": has_bearer,
                    "authentication_implemented": has_jwt or (has_auth_middleware and has_api_key)
                }

                if not has_jwt and not has_api_key:
                    analysis["recommendations"].append({
                        "priority": "P1 - Important",
                        "action": "Implement JWT token authentication",
                        "details": "Add JWT token authentication for API endpoints"
                    })

                if not has_api_key:
                    analysis["recommendations"].append({
                        "priority": "P1 - Important",
                        "action": "Implement API key authentication for webhooks",
                        "details": "Add API key validation for webhook endpoints"
                    })
            else:
                analysis["current_state"] = {
                    "file_exists": False,
                    "authentication_implemented": False
                }

            output_file = output_dir / "auth_implementation.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)

            self.log_success(f"T9.6 completed: {output_file}")
            return str(output_file)

        except Exception as e:
            self.log_error(f"Error executing T9.6: {e}")
            return None

    def _execute_t9_7(self, output_dir: Path) -> Optional[str]:
        """T9.7: Conduct security audit"""
        try:
            analysis = {
                "phase": 9,
                "task": "T9.7 - Security Audit",
                "timestamp": self._get_timestamp(),
                "status": "analyzed",
                "audit_tools": {},
                "vulnerabilities": [],
                "recommendations": [],
                "implementation_required": True
            }

            # Check for security scanning tools
            req_file = self.workspace_path / "requirements.txt"
            if req_file.exists():
                req_content = req_file.read_text(encoding='utf-8')
                analysis["audit_tools"] = {
                    "bandit_available": "bandit" in req_content.lower(),
                    "safety_available": "safety" in req_content.lower(),
                    "bandit_installed": False,
                    "safety_installed": False
                }

            # Check package.json for npm audit
            package_json = self.workspace_path / "package.json"
            if package_json.exists():
                analysis["audit_tools"]["npm_available"] = True
            else:
                analysis["audit_tools"]["npm_available"] = False

            # Common vulnerabilities to check
            vulnerabilities = []

            # Check for SQL injection risks
            py_files = list(self.workspace_path.glob("**/*.py"))
            sql_injection_risks = 0
            for py_file in py_files[:20]:  # Sample first 20 files
                try:
                    content = py_file.read_text(encoding='utf-8')
                    if "execute(" in content and "SELECT" in content and "%" in content:
                        sql_injection_risks += 1
                except:
                    pass

            if sql_injection_risks > 0:
                vulnerabilities.append({
                    "type": "SQL Injection Risk",
                    "severity": "High",
                    "count": sql_injection_risks,
                    "description": "Potential SQL injection vulnerabilities found"
                })

            analysis["vulnerabilities"] = vulnerabilities

            analysis["recommendations"].append({
                "priority": "P1 - Important",
                "action": "Run bandit security scanner",
                "details": "Install and run: pip install bandit && bandit -r ."
            })

            analysis["recommendations"].append({
                "priority": "P1 - Important",
                "action": "Run safety check",
                "details": "Install and run: pip install safety && safety check"
            })

            if package_json.exists():
                analysis["recommendations"].append({
                    "priority": "P1 - Important",
                    "action": "Run npm audit",
                    "details": "Run: npm audit"
                })

            output_file = output_dir / "security_audit_report.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)

            self.log_success(f"T9.7 completed: {output_file}")
            return str(output_file)

        except Exception as e:
            self.log_error(f"Error executing T9.7: {e}")
            return None

    def _execute_t9_8(self, output_dir: Path) -> Optional[str]:
        """T9.8: Create penetration testing plan"""
        try:
            analysis = {
                "phase": 9,
                "task": "T9.8 - Penetration Testing Plan",
                "timestamp": self._get_timestamp(),
                "status": "planned",
                "testing_areas": [],
                "recommendations": [],
                "implementation_required": True
            }

            analysis["testing_areas"] = [
                {
                    "area": "Webhook Endpoints",
                    "priority": "High",
                    "tests": [
                        "Test webhook signature validation",
                        "Test unauthorized access attempts",
                        "Test payload manipulation"
                    ]
                },
                {
                    "area": "API Endpoints",
                    "priority": "High",
                    "tests": [
                        "Test rate limiting effectiveness",
                        "Test authentication bypass attempts",
                        "Test input validation"
                    ]
                },
                {
                    "area": "Cotization Endpoints",
                    "priority": "Medium",
                    "tests": [
                        "Test quote generation security",
                        "Test data validation",
                        "Test authorization checks"
                    ]
                }
            ]

            analysis["recommendations"].append({
                "priority": "P1 - Important",
                "action": "Conduct professional penetration testing",
                "details": "Engage security team or external auditor for comprehensive testing"
            })

            analysis["recommendations"].append({
                "priority": "P1 - Important",
                "action": "Test all webhook endpoints",
                "details": "Verify webhook signature validation and authorization"
            })

            output_file = output_dir / "penetration_test_report.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)

            self.log_success(f"T9.8 completed: {output_file}")
            return str(output_file)

        except Exception as e:
            self.log_error(f"Error executing T9.8: {e}")
            return None

    def _generate_security_summary(self, output_dir: Path) -> Optional[str]:
        """Generate comprehensive security summary"""
        try:
            summary = {
                "phase": 9,
                "task": "Security Hardening Summary",
                "timestamp": self._get_timestamp(),
                "status": "completed",
                "tasks_completed": 8,
                "critical_issues": [],
                "recommendations": [],
                "next_steps": []
            }

            # Collect all security reports
            security_files = list(output_dir.glob("*.json"))
            for sec_file in security_files:
                try:
                    with open(sec_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "recommendations" in data:
                            for rec in data["recommendations"]:
                                if rec.get("priority", "").startswith("P0"):
                                    summary["critical_issues"].append({
                                        "task": data.get("task", "Unknown"),
                                        "recommendation": rec
                                    })
                except:
                    pass

            summary["next_steps"] = [
                "Implement webhook signature validation (T9.1, T9.2)",
                "Migrate to secure secrets management (T9.3)",
                "Fix CORS configuration (T9.5)",
                "Implement rate limiting (T9.4)",
                "Add API authentication (T9.6)",
                "Run security audit tools (T9.7)",
                "Plan penetration testing (T9.8)"
            ]

            output_file = output_dir / "security_summary.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

            self.log_success(f"Security summary generated: {output_file}")
            return str(output_file)

        except Exception as e:
            self.log_error(f"Error generating security summary: {e}")
            return None

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

