#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Status Checker
Comprehensive status check for the BMC Chatbot Platform project
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from scripts.orchestrator.state_manager import StateManager
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False


class ProjectStatusChecker:
    """Comprehensive project status checker"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.consolidation_dir = self.project_root / "consolidation"
        self.reports_dir = self.consolidation_dir / "reports"
        self.state_file = self.consolidation_dir / "execution_state.json"
        
    def check_all(self) -> Dict[str, Any]:
        """Run all status checks"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "overall_status": "unknown",
            "checks": {}
        }
        
        # Run individual checks
        status["checks"]["directory_structure"] = self.check_directory_structure()
        status["checks"]["orchestrator"] = self.check_orchestrator()
        status["checks"]["phase_status"] = self.check_phase_status()
        status["checks"]["components"] = self.check_components()
        status["checks"]["integrations"] = self.check_integrations()
        status["checks"]["security"] = self.check_security()
        status["checks"]["documentation"] = self.check_documentation()
        
        # Calculate overall status
        status["overall_status"] = self.calculate_overall_status(status["checks"])
        
        return status
    
    def check_directory_structure(self) -> Dict[str, Any]:
        """Check if required directories exist"""
        required_dirs = {
            "consolidation": self.consolidation_dir,
            "consolidation/reports": self.reports_dir,
            "scripts/orchestrator": self.project_root / "scripts" / "orchestrator",
            "scripts/discovery": self.project_root / "scripts" / "discovery",
            "agents": self.project_root / "agents",
        }
        
        results = {}
        all_exist = True
        
        for name, path in required_dirs.items():
            exists = path.exists() and path.is_dir()
            results[name] = {
                "exists": exists,
                "path": str(path)
            }
            if not exists:
                all_exist = False
        
        return {
            "status": "ok" if all_exist else "missing_directories",
            "directories": results,
            "all_exist": all_exist
        }
    
    def check_orchestrator(self) -> Dict[str, Any]:
        """Check orchestrator system status"""
        if not ORCHESTRATOR_AVAILABLE:
            return {
                "status": "not_available",
                "message": "Orchestrator modules not importable"
            }
        
        try:
            state_manager = StateManager()
            can_resume = state_manager.can_resume()
            current_phase = state_manager.get_current_phase()
            overall_status = state_manager.get_overall_status()
            
            return {
                "status": "ok",
                "available": True,
                "can_resume": can_resume,
                "current_phase": current_phase,
                "overall_status": overall_status,
                "state_file_exists": self.state_file.exists()
            }
        except Exception as e:
            return {
                "status": "error",
                "available": True,
                "error": str(e)
            }
    
    def check_phase_status(self) -> Dict[str, Any]:
        """Check status of all phases (0-15)"""
        if not self.state_file.exists():
            return {
                "status": "no_state_file",
                "phases": {},
                "message": "No execution state file found. Phase 0 not started."
            }
        
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            
            phases = {}
            for phase_num in range(16):
                phase_key = str(phase_num)
                phase_data = state.get("phases", {}).get(phase_key, {})
                phases[phase_num] = {
                    "status": phase_data.get("status", "pending"),
                    "started_at": phase_data.get("started_at"),
                    "completed_at": phase_data.get("completed_at"),
                    "approved": phase_data.get("approved", False)
                }
            
            completed = sum(1 for p in phases.values() if p["status"] == "completed")
            in_progress = sum(1 for p in phases.values() if p["status"] == "in_progress")
            pending = sum(1 for p in phases.values() if p["status"] == "pending")
            
            return {
                "status": "ok",
                "phases": phases,
                "summary": {
                    "total": 16,
                    "completed": completed,
                    "in_progress": in_progress,
                    "pending": pending,
                    "progress_percent": int((completed / 16) * 100)
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def check_components(self) -> Dict[str, Any]:
        """Check core component files"""
        components = {
            "api_server": self.project_root / "api_server.py",
            "conversational_ai": self.project_root / "ia_conversacional_integrada.py",
            "quotation_system": self.project_root / "sistema_cotizaciones.py",
            "knowledge_base": self.project_root / "base_conocimiento_dinamica.py",
            "whatsapp_integration": self.project_root / "integracion_whatsapp.py",
            "n8n_integration": self.project_root / "n8n_integration.py",
            "google_sheets": self.project_root / "integracion_google_sheets.py",
            "docker_compose": self.project_root / "docker-compose.yml",
        }
        
        results = {}
        all_exist = True
        
        for name, path in components.items():
            exists = path.exists() and path.is_file()
            results[name] = {
                "exists": exists,
                "path": str(path),
                "size": path.stat().st_size if exists else 0
            }
            if not exists:
                all_exist = False
        
        return {
            "status": "ok" if all_exist else "missing_components",
            "components": results,
            "all_exist": all_exist
        }
    
    def check_integrations(self) -> Dict[str, Any]:
        """Check integration status"""
        integrations = {
            "whatsapp": {
                "file": self.project_root / "integracion_whatsapp.py",
                "config_needed": ["WHATSAPP_TOKEN", "WHATSAPP_PHONE_ID"]
            },
            "n8n": {
                "file": self.project_root / "n8n_integration.py",
                "config_needed": ["N8N_URL", "N8N_API_KEY"]
            },
            "mongodb": {
                "file": self.project_root / "mongodb_service.py",
                "config_needed": ["MONGODB_URI"]
            },
            "qdrant": {
                "file": None,  # Not found
                "config_needed": ["QDRANT_URL", "QDRANT_API_KEY"],
                "status": "missing"
            }
        }
        
        results = {}
        for name, info in integrations.items():
            file_exists = info["file"] and info["file"].exists() if info["file"] else False
            results[name] = {
                "file_exists": file_exists,
                "status": info.get("status", "configured" if file_exists else "missing"),
                "config_required": info["config_needed"]
            }
        
        return {
            "status": "partial",
            "integrations": results
        }
    
    def check_security(self) -> Dict[str, Any]:
        """Check security-related items"""
        security_items = {
            "webhook_validation": {
                "file": self.project_root / "integracion_whatsapp.py",
                "check": "signature validation"
            },
            "secrets_management": {
                "file": self.project_root / ".env",
                "check": "environment variables"
            },
            "cors_config": {
                "file": self.project_root / "api_server.py",
                "check": "CORS configuration"
            }
        }
        
        results = {}
        for name, info in security_items.items():
            file_exists = info["file"].exists() if info["file"] else False
            results[name] = {
                "file_exists": file_exists,
                "status": "needs_review"
            }
        
        return {
            "status": "needs_review",
            "items": results,
            "message": "Security items need manual review"
        }
    
    def check_documentation(self) -> Dict[str, Any]:
        """Check documentation files"""
        docs = {
            "architecture_report": self.project_root / "ARCHITECTURE_STATUS_REPORT.md",
            "consolidation_plan": self.project_root / "consolidation" / "PLAN_COMPLETO_REPOSITORIO_WORKSPACE.md",
            "agent_architecture": self.project_root / "AGENT_ARCHITECTURE.md",
            "readme": self.project_root / "README.md",
        }
        
        results = {}
        all_exist = True
        
        for name, path in docs.items():
            exists = path.exists() and path.is_file()
            results[name] = {
                "exists": exists,
                "path": str(path)
            }
            if not exists:
                all_exist = False
        
        return {
            "status": "ok" if all_exist else "missing_docs",
            "docs": results,
            "all_exist": all_exist
        }
    
    def calculate_overall_status(self, checks: Dict[str, Any]) -> str:
        """Calculate overall project status"""
        # Check critical items
        if not checks.get("directory_structure", {}).get("all_exist", False):
            return "setup_required"
        
        if not checks.get("components", {}).get("all_exist", False):
            return "components_missing"
        
        phase_status = checks.get("phase_status", {})
        if phase_status.get("status") == "no_state_file":
            return "phase_0_not_started"
        
        summary = phase_status.get("summary", {})
        progress = summary.get("progress_percent", 0)
        
        if progress == 0:
            return "phase_0_not_started"
        elif progress < 50:
            return "in_progress_early"
        elif progress < 100:
            return "in_progress"
        else:
            return "completed"
    
    def print_report(self, status: Dict[str, Any]):
        """Print formatted status report"""
        print("\n" + "="*70)
        print("📊 BMC CHATBOT PLATFORM - PROJECT STATUS REPORT")
        print("="*70)
        print(f"Timestamp: {status['timestamp']}")
        print(f"Project Root: {status['project_root']}")
        print(f"Overall Status: {status['overall_status'].upper()}")
        print("="*70)
        
        # Phase Status
        phase_status = status["checks"].get("phase_status", {})
        if phase_status.get("status") == "ok":
            summary = phase_status.get("summary", {})
            print(f"\n📈 Phase Progress: {summary.get('progress_percent', 0)}%")
            print(f"   Completed: {summary.get('completed', 0)}/16")
            print(f"   In Progress: {summary.get('in_progress', 0)}")
            print(f"   Pending: {summary.get('pending', 0)}")
        else:
            print("\n⚠️  Phase Status: Phase 0 not started")
        
        # Components
        components = status["checks"].get("components", {})
        if components.get("all_exist"):
            print("\n✅ Core Components: All present")
        else:
            print("\n❌ Core Components: Some missing")
            for name, info in components.get("components", {}).items():
                if not info.get("exists"):
                    print(f"   - Missing: {name}")
        
        # Integrations
        integrations = status["checks"].get("integrations", {})
        print(f"\n🔌 Integrations: {integrations.get('status', 'unknown')}")
        for name, info in integrations.get("integrations", {}).items():
            status_icon = "✅" if info.get("status") == "configured" else "⚠️"
            print(f"   {status_icon} {name}: {info.get('status', 'unknown')}")
        
        # Security
        security = status["checks"].get("security", {})
        print(f"\n🔒 Security: {security.get('status', 'unknown')}")
        print("   ⚠️  Manual review required")
        
        # Recommendations
        print("\n" + "="*70)
        print("💡 RECOMMENDATIONS")
        print("="*70)
        
        overall = status["overall_status"]
        if overall == "phase_0_not_started":
            print("1. Start Phase 0: BMC Discovery & Assessment")
            print("   Run: python scripts/discovery/run_phase_0.py")
        elif overall == "setup_required":
            print("1. Set up required directories")
            print("2. Initialize orchestrator system")
        elif overall == "in_progress_early":
            print("1. Continue with current phase")
            print("2. Review blockers if any")
        elif overall == "in_progress":
            print("1. Continue execution")
            print("2. Monitor progress")
        
        print("\n" + "="*70)


def main():
    """Main entry point"""
    checker = ProjectStatusChecker()
    status = checker.check_all()
    
    # Print report
    checker.print_report(status)
    
    # Save to file
    report_file = checker.reports_dir / f"status_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(status, f, indent=2)
    
    print(f"\n📄 Full report saved to: {report_file}")
    
    # Return exit code based on status
    overall = status["overall_status"]
    if overall in ["setup_required", "components_missing"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

