#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
n8n Workflow Importer
Automatically imports n8n workflows via API
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  requests library not available. Install with: pip install requests")


class N8NWorkflowImporter:
    """Imports n8n workflows via API"""
    
    def __init__(self, n8n_url: str = "http://localhost:5678", api_key: Optional[str] = None):
        self.n8n_url = n8n_url.rstrip('/')
        self.api_key = api_key
        self.workflows_dir = Path(__file__).parent.parent / "n8n_workflows"
        self.imported: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []
        
    def check_n8n_available(self) -> bool:
        """Check if n8n is available"""
        if not REQUESTS_AVAILABLE:
            return False
        
        try:
            response = requests.get(f"{self.n8n_url}/healthz", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-N8N-API-KEY"] = self.api_key
        return headers
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List existing workflows in n8n"""
        if not REQUESTS_AVAILABLE:
            return []
        
        try:
            response = requests.get(
                f"{self.n8n_url}/api/v1/workflows",
                headers=self.get_headers(),
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                self.errors.append({
                    "action": "list_workflows",
                    "message": f"Failed to list workflows: {response.status_code}",
                    "response": response.text[:200]
                })
                return []
        except requests.exceptions.RequestException as e:
            self.errors.append({
                "action": "list_workflows",
                "message": f"Error connecting to n8n: {e}",
                "fix": f"Ensure n8n is running at {self.n8n_url}"
            })
            return []
    
    def import_workflow(self, workflow_file: Path, activate: bool = True) -> Optional[Dict[str, Any]]:
        """Import a workflow from JSON file"""
        if not REQUESTS_AVAILABLE:
            self.errors.append({
                "action": "import_workflow",
                "workflow": workflow_file.name,
                "message": "requests library not available"
            })
            return None
        
        if not workflow_file.exists():
            self.errors.append({
                "action": "import_workflow",
                "workflow": workflow_file.name,
                "message": f"Workflow file not found: {workflow_file}"
            })
            return None
        
        try:
            # Load workflow JSON
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            
            # Check if workflow already exists
            existing_workflows = self.list_workflows()
            workflow_name = workflow_data.get("name", workflow_file.stem)
            
            existing_id = None
            for wf in existing_workflows:
                if wf.get("name") == workflow_name:
                    existing_id = wf.get("id")
                    break
            
            # Prepare workflow data for import
            import_data = {
                "name": workflow_name,
                "nodes": workflow_data.get("nodes", []),
                "connections": workflow_data.get("connections", {}),
                "settings": workflow_data.get("settings", {}),
                "staticData": workflow_data.get("staticData", {}),
                "tags": workflow_data.get("tags", []),
                "active": activate if not existing_id else False  # Don't auto-activate existing
            }
            
            # Create or update workflow
            if existing_id:
                # Update existing workflow
                response = requests.put(
                    f"{self.n8n_url}/api/v1/workflows/{existing_id}",
                    headers=self.get_headers(),
                    json=import_data,
                    timeout=30
                )
                action = "updated"
            else:
                # Create new workflow
                response = requests.post(
                    f"{self.n8n_url}/api/v1/workflows",
                    headers=self.get_headers(),
                    json=import_data,
                    timeout=30
                )
                action = "imported"
            
            if response.status_code in [200, 201]:
                result = response.json()
                workflow_id = result.get("id") or existing_id
                
                # Activate if requested
                if activate and workflow_id:
                    self.activate_workflow(workflow_id)
                
                self.imported.append({
                    "workflow": workflow_name,
                    "file": workflow_file.name,
                    "action": action,
                    "id": workflow_id,
                    "active": activate
                })
                
                return result
            else:
                self.errors.append({
                    "action": "import_workflow",
                    "workflow": workflow_name,
                    "message": f"Failed to import workflow: {response.status_code}",
                    "response": response.text[:200]
                })
                return None
                
        except json.JSONDecodeError as e:
            self.errors.append({
                "action": "import_workflow",
                "workflow": workflow_file.name,
                "message": f"Invalid JSON in workflow file: {e}",
                "fix": "Check workflow file format"
            })
            return None
        except Exception as e:
            self.errors.append({
                "action": "import_workflow",
                "workflow": workflow_file.name,
                "message": f"Error importing workflow: {e}",
                "fix": "Check workflow file and n8n connection"
            })
            return None
    
    def activate_workflow(self, workflow_id: str) -> bool:
        """Activate a workflow"""
        if not REQUESTS_AVAILABLE:
            return False
        
        try:
            response = requests.post(
                f"{self.n8n_url}/api/v1/workflows/{workflow_id}/activate",
                headers=self.get_headers(),
                timeout=10
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_webhook_urls(self) -> Dict[str, str]:
        """Get webhook URLs for active workflows"""
        webhooks = {}
        
        if not REQUESTS_AVAILABLE:
            return webhooks
        
        try:
            workflows = self.list_workflows()
            for wf in workflows:
                if wf.get("active"):
                    workflow_id = wf.get("id")
                    # Get workflow details to find webhook nodes
                    response = requests.get(
                        f"{self.n8n_url}/api/v1/workflows/{workflow_id}",
                        headers=self.get_headers(),
                        timeout=10
                    )
                    if response.status_code == 200:
                        workflow_data = response.json()
                        nodes = workflow_data.get("nodes", [])
                        for node in nodes:
                            if node.get("type") == "n8n-nodes-base.webhook":
                                webhook_path = node.get("parameters", {}).get("path", "")
                                if webhook_path:
                                    webhook_url = f"{self.n8n_url}/webhook/{webhook_path}"
                                    webhooks[wf.get("name", "unknown")] = webhook_url
        except Exception:
            pass
        
        return webhooks
    
    def import_all_workflows(self, activate: bool = True) -> Dict[str, Any]:
        """Import all workflows from n8n_workflows directory"""
        if not self.workflows_dir.exists():
            self.errors.append({
                "action": "import_all",
                "message": f"Workflows directory not found: {self.workflows_dir}",
                "fix": "Ensure n8n_workflows directory exists"
            })
            return {
                "success": False,
                "imported": [],
                "errors": self.errors
            }
        
        # Find all workflow JSON files
        workflow_files = list(self.workflows_dir.glob("workflow-*.json"))
        
        if not workflow_files:
            self.errors.append({
                "action": "import_all",
                "message": "No workflow files found in n8n_workflows directory",
                "fix": "Add workflow JSON files to n8n_workflows directory"
            })
            return {
                "success": False,
                "imported": [],
                "errors": self.errors
            }
        
        # Import each workflow
        for workflow_file in workflow_files:
            self.import_workflow(workflow_file, activate=activate)
        
        # Get webhook URLs
        webhooks = self.get_webhook_urls()
        
        return {
            "success": len(self.errors) == 0,
            "imported": self.imported,
            "errors": self.errors,
            "webhooks": webhooks
        }
    
    def print_report(self, result: Dict[str, Any]):
        """Print import report"""
        print("\n" + "=" * 70)
        print("N8N WORKFLOW IMPORT REPORT")
        print("=" * 70 + "\n")
        
        if result["success"]:
            print("✅ All workflows imported successfully\n")
        else:
            print("⚠️  Some workflows had errors\n")
        
        # Print imported workflows
        if result["imported"]:
            print("IMPORTED WORKFLOWS:")
            print("-" * 70)
            for item in result["imported"]:
                status = "✅ Active" if item.get("active") else "⏸️  Inactive"
                print(f"{status} {item['workflow']} ({item['action']})")
                print(f"   File: {item['file']}")
                if item.get("id"):
                    print(f"   ID: {item['id']}")
            print()
        
        # Print webhook URLs
        if result.get("webhooks"):
            print("WEBHOOK URLs:")
            print("-" * 70)
            for workflow_name, url in result["webhooks"].items():
                print(f"  {workflow_name}: {url}")
            print()
        
        # Print errors
        if result["errors"]:
            print("ERRORS:")
            print("-" * 70)
            for error in result["errors"]:
                print(f"\n❌ {error.get('workflow', error.get('action', 'Unknown'))}")
                print(f"   Message: {error['message']}")
                if "fix" in error:
                    print(f"   Fix: {error['fix']}")
            print()
    
    def save_report(self, result: Dict[str, Any], output_file: Optional[Path] = None) -> Path:
        """Save import report to JSON file"""
        if output_file is None:
            output_file = Path(__file__).parent.parent / "logs" / "n8n_import_report.json"
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        return output_file


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Import n8n workflows via API")
    parser.add_argument(
        "--n8n-url",
        default="http://localhost:5678",
        help="n8n instance URL (default: http://localhost:5678)"
    )
    parser.add_argument(
        "--api-key",
        help="n8n API key (optional, for authentication)"
    )
    parser.add_argument(
        "--workflow",
        type=Path,
        help="Import specific workflow file"
    )
    parser.add_argument(
        "--no-activate",
        action="store_true",
        help="Don't activate workflows after import"
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
    
    importer = N8NWorkflowImporter(n8n_url=args.n8n_url, api_key=args.api_key)
    
    # Check if n8n is available
    if not importer.check_n8n_available():
        print(f"❌ n8n is not available at {args.n8n_url}")
        print("   Please ensure n8n is running and accessible")
        sys.exit(1)
    
    # Import workflow(s)
    if args.workflow:
        result = {
            "success": importer.import_workflow(args.workflow, activate=not args.no_activate) is not None,
            "imported": importer.imported,
            "errors": importer.errors,
            "webhooks": importer.get_webhook_urls()
        }
    else:
        result = importer.import_all_workflows(activate=not args.no_activate)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        importer.print_report(result)
    
    if args.save_report:
        report_file = importer.save_report(result)
        print(f"Report saved to: {report_file}")
    
    # Exit with error code if import failed
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()

