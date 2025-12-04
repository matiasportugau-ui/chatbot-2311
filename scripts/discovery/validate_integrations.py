#!/usr/bin/env python3
"""
T0.4: Validación de integraciones específicas
Validates WhatsApp, n8n, Qdrant, and Chatwoot integrations
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class IntegrationValidator:
    """Validates BMC integrations"""
    
    def __init__(self, workspace_path: str = "/Users/matias/chatbot2511/chatbot-2311"):
        self.workspace_path = Path(workspace_path)
    
    def validate(self) -> Dict[str, Any]:
        """Perform complete integration validation"""
        print("🔍 Starting integration validation...")
        
        results = {
            "validation_date": datetime.now().isoformat(),
            "whatsapp": self._validate_whatsapp(),
            "n8n": self._validate_n8n(),
            "qdrant": self._validate_qdrant(),
            "chatwoot": self._validate_chatwoot(),
            "summary": {}
        }
        
        # Generate summary
        results["summary"] = self._generate_summary(results)
        
        print("✅ Integration validation complete")
        return results
    
    def _validate_whatsapp(self) -> Dict[str, Any]:
        """Validate WhatsApp Business API integration"""
        validation = {
            "status": "not_configured",
            "files_found": [],
            "credentials": {
                "access_token": False,
                "phone_number_id": False,
                "business_account_id": False,
                "webhook_verify_token": False
            },
            "configuration": {
                "webhook_configured": False,
                "signature_validation": False
            },
            "missing_credentials": []
        }
        
        # Find WhatsApp integration files
        whatsapp_files = list(self.workspace_path.rglob("*whatsapp*.py"))
        if whatsapp_files:
            validation["files_found"] = [str(f.relative_to(self.workspace_path)) for f in whatsapp_files]
            validation["status"] = "files_found"
            
            # Check for credentials in environment or files
            env_vars = [
                "WHATSAPP_ACCESS_TOKEN",
                "WHATSAPP_PHONE_NUMBER_ID",
                "WHATSAPP_BUSINESS_ACCOUNT_ID",
                "WHATSAPP_WEBHOOK_VERIFY_TOKEN"
            ]
            
            for var in env_vars:
                if os.getenv(var):
                    key = var.replace("WHATSAPP_", "").lower()
                    if key in validation["credentials"]:
                        validation["credentials"][key] = True
                else:
                    validation["missing_credentials"].append(var)
            
            # Check code for webhook and signature validation
            try:
                content = whatsapp_files[0].read_text(encoding='utf-8', errors='ignore')
                if "webhook" in content.lower():
                    validation["configuration"]["webhook_configured"] = True
                if "signature" in content.lower() or "hmac" in content.lower():
                    validation["configuration"]["signature_validation"] = True
            except:
                pass
            
            # Determine overall status
            if all(validation["credentials"].values()):
                validation["status"] = "configured"
            elif any(validation["credentials"].values()):
                validation["status"] = "partially_configured"
            else:
                validation["status"] = "pending_credentials"
        
        return validation
    
    def _validate_n8n(self) -> Dict[str, Any]:
        """Validate n8n integration"""
        validation = {
            "status": "not_configured",
            "files_found": [],
            "workflows_found": [],
            "credentials": {
                "api_key": False,
                "base_url": False
            },
            "configuration": {
                "workflows_imported": False,
                "api_client_configured": False
            },
            "missing_credentials": []
        }
        
        # Find n8n integration files
        n8n_files = list(self.workspace_path.rglob("*n8n*.py"))
        if n8n_files:
            validation["files_found"] = [str(f.relative_to(self.workspace_path)) for f in n8n_files]
            validation["status"] = "files_found"
            
            # Check for credentials
            if os.getenv("N8N_API_KEY") or os.getenv("N8N_API_TOKEN"):
                validation["credentials"]["api_key"] = True
            else:
                validation["missing_credentials"].append("N8N_API_KEY")
            
            if os.getenv("N8N_BASE_URL") or os.getenv("N8N_URL"):
                validation["credentials"]["base_url"] = True
            else:
                validation["missing_credentials"].append("N8N_BASE_URL")
            
            # Check for workflows
            workflow_dirs = [
                self.workspace_path / "n8n_workflows",
                self.workspace_path / "n8n-workflows"
            ]
            
            for wf_dir in workflow_dirs:
                if wf_dir.exists():
                    workflows = list(wf_dir.rglob("*.json"))
                    validation["workflows_found"] = [f.name for f in workflows]
                    validation["configuration"]["workflows_imported"] = len(workflows) > 0
                    break
            
            # Check code for API client
            try:
                content = n8n_files[0].read_text(encoding='utf-8', errors='ignore')
                if "api" in content.lower() and ("client" in content.lower() or "request" in content.lower()):
                    validation["configuration"]["api_client_configured"] = True
            except:
                pass
            
            # Determine overall status
            if validation["credentials"]["api_key"] and validation["credentials"]["base_url"]:
                validation["status"] = "configured"
            elif validation["credentials"]["api_key"] or validation["credentials"]["base_url"]:
                validation["status"] = "partially_configured"
            else:
                validation["status"] = "pending_credentials"
        
        return validation
    
    def _validate_qdrant(self) -> Dict[str, Any]:
        """Validate Qdrant integration"""
        validation = {
            "status": "not_configured",
            "files_found": [],
            "credentials": {
                "url": False,
                "api_key": False
            },
            "configuration": {
                "client_configured": False,
                "collections_created": False
            },
            "missing_credentials": []
        }
        
        # Find Qdrant references in code
        qdrant_files = []
        for py_file in self.workspace_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if "qdrant" in content.lower() or "from qdrant" in content.lower():
                    qdrant_files.append(py_file)
            except:
                pass
        
        if qdrant_files:
            validation["files_found"] = [str(f.relative_to(self.workspace_path)) for f in qdrant_files]
            validation["status"] = "files_found"
            
            # Check for credentials
            if os.getenv("QDRANT_URL") or os.getenv("QDRANT_HOST"):
                validation["credentials"]["url"] = True
            else:
                validation["missing_credentials"].append("QDRANT_URL")
            
            if os.getenv("QDRANT_API_KEY"):
                validation["credentials"]["api_key"] = True
            else:
                validation["missing_credentials"].append("QDRANT_API_KEY")
            
            # Check code for client configuration
            try:
                content = qdrant_files[0].read_text(encoding='utf-8', errors='ignore')
                if "QdrantClient" in content or "qdrant_client" in content.lower():
                    validation["configuration"]["client_configured"] = True
                if "create_collection" in content.lower() or "collection" in content.lower():
                    validation["configuration"]["collections_created"] = True
            except:
                pass
            
            # Determine overall status
            if validation["credentials"]["url"]:
                validation["status"] = "configured" if validation["credentials"]["api_key"] else "partially_configured"
            else:
                validation["status"] = "pending_credentials"
        
        return validation
    
    def _validate_chatwoot(self) -> Dict[str, Any]:
        """Validate Chatwoot integration"""
        validation = {
            "status": "not_found",
            "files_found": [],
            "credentials": {
                "api_access_token": False,
                "base_url": False
            },
            "configuration": {
                "client_configured": False
            },
            "missing_credentials": []
        }
        
        # Find Chatwoot references
        chatwoot_files = []
        for py_file in self.workspace_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if "chatwoot" in content.lower():
                    chatwoot_files.append(py_file)
            except:
                pass
        
        if chatwoot_files:
            validation["files_found"] = [str(f.relative_to(self.workspace_path)) for f in chatwoot_files]
            validation["status"] = "files_found"
            
            # Check for credentials
            if os.getenv("CHATWOOT_API_ACCESS_TOKEN") or os.getenv("CHATWOOT_TOKEN"):
                validation["credentials"]["api_access_token"] = True
            else:
                validation["missing_credentials"].append("CHATWOOT_API_ACCESS_TOKEN")
            
            if os.getenv("CHATWOOT_BASE_URL") or os.getenv("CHATWOOT_URL"):
                validation["credentials"]["base_url"] = True
            else:
                validation["missing_credentials"].append("CHATWOOT_BASE_URL")
            
            # Check code for client
            try:
                content = chatwoot_files[0].read_text(encoding='utf-8', errors='ignore')
                if "api" in content.lower() and "client" in content.lower():
                    validation["configuration"]["client_configured"] = True
            except:
                pass
            
            # Determine overall status
            if validation["credentials"]["api_access_token"] and validation["credentials"]["base_url"]:
                validation["status"] = "configured"
            elif validation["credentials"]["api_access_token"] or validation["credentials"]["base_url"]:
                validation["status"] = "partially_configured"
            else:
                validation["status"] = "pending_credentials"
        else:
            validation["status"] = "not_found"
        
        return validation
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation summary"""
        integrations = ["whatsapp", "n8n", "qdrant", "chatwoot"]
        configured = 0
        partially_configured = 0
        pending = 0
        not_found = 0
        
        for integration in integrations:
            status = results.get(integration, {}).get("status", "unknown")
            if status == "configured":
                configured += 1
            elif status == "partially_configured":
                partially_configured += 1
            elif status in ["pending_credentials", "not_configured"]:
                pending += 1
            elif status == "not_found":
                not_found += 1
        
        return {
            "total_integrations": len(integrations),
            "configured": configured,
            "partially_configured": partially_configured,
            "pending_credentials": pending,
            "not_found": not_found,
            "readiness_score": round(configured / len(integrations), 2),
            "status": "completed"
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate integrations")
    parser.add_argument("--workspace", "-w", default="/Users/matias/chatbot2511/chatbot-2311",
                       help="Workspace path to analyze")
    parser.add_argument("--output", "-o", default="consolidation/discovery/integrations_status.json",
                       help="Output file path")
    
    args = parser.parse_args()
    
    # Run validation
    validator = IntegrationValidator(workspace_path=args.workspace)
    results = validator.validate()
    
    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Results saved to: {output_path}")
    print(f"📊 Summary: {results.get('summary', {})}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

