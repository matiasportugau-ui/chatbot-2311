#!/usr/bin/env python3
"""
T0.7: Creación de baseline de producción
Creates production baseline documenting current state, metrics, and acceptance criteria
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class ProductionBaselineCreator:
    """Creates production baseline from discovery results"""

    def __init__(self, discovery_results_dir: str = "consolidation/discovery"):
        self.discovery_dir = Path(discovery_results_dir)

    def create(self, repository_analysis: Dict = None, workspace_analysis: Dict = None,
               bmc_inventory: Dict = None, integrations_status: Dict = None,
               quotation_assessment: Dict = None, production_gaps: Dict = None) -> Dict[str, Any]:
        """Create production baseline"""
        print("🔍 Creating production baseline...")

        # Load discovery results if not provided
        if not repository_analysis:
            repo_file = self.discovery_dir / "repository_analysis.json"
            if repo_file.exists():
                repository_analysis = json.loads(repo_file.read_text(encoding='utf-8'))

        if not workspace_analysis:
            ws_file = self.discovery_dir / "workspace_analysis.json"
            if ws_file.exists():
                workspace_analysis = json.loads(ws_file.read_text(encoding='utf-8'))

        if not bmc_inventory:
            bmc_file = self.discovery_dir / "bmc_inventory.json"
            if bmc_file.exists():
                bmc_inventory = json.loads(bmc_file.read_text(encoding='utf-8'))

        if not integrations_status:
            int_file = self.discovery_dir / "integrations_status.json"
            if int_file.exists():
                integrations_status = json.loads(int_file.read_text(encoding='utf-8'))

        if not quotation_assessment:
            quot_file = self.discovery_dir / "quotation_assessment.json"
            if quot_file.exists():
                quotation_assessment = json.loads(quot_file.read_text(encoding='utf-8'))

        if not production_gaps:
            gaps_file = self.discovery_dir / "production_gaps.json"
            if gaps_file.exists():
                production_gaps = json.loads(gaps_file.read_text(encoding='utf-8'))

        baseline = {
            "baseline_date": datetime.now().isoformat(),
            "current_state": self._document_current_state(
                repository_analysis, workspace_analysis, bmc_inventory,
                integrations_status, quotation_assessment
            ),
            "metrics": self._define_metrics(
                repository_analysis, workspace_analysis, bmc_inventory,
                integrations_status, quotation_assessment, production_gaps
            ),
            "production_checklist": self._create_production_checklist(production_gaps),
            "acceptance_criteria": self._define_acceptance_criteria(),
            "success_metrics": self._define_success_metrics(),
            "summary": {}
        }

        # Generate summary
        baseline["summary"] = self._generate_summary(baseline)

        print("✅ Production baseline created")
        return baseline

    def _document_current_state(self, repo_analysis: Dict = None, workspace_analysis: Dict = None,
                                bmc_inventory: Dict = None, integrations_status: Dict = None,
                                quotation_assessment: Dict = None) -> Dict[str, Any]:
        """Document current system state"""
        state = {
            "phase": "discovery_complete",
            "repositories": {},
            "workspace": {},
            "components": {},
            "integrations": {},
            "quotation_engine": {}
        }

        if repo_analysis:
            # Handle technologies as either list or dict
            techs = repo_analysis.get("technologies", [])
            if isinstance(techs, dict):
                tech_list = list(techs.keys())
            else:
                tech_list = techs if isinstance(techs, list) else []

            state["repositories"] = {
                "total": repo_analysis.get("summary", {}).get("total_repositories", 0),
                "analyzed": repo_analysis.get("summary", {}).get("repositories_analyzed", 0),
                "technologies": tech_list
            }

        if workspace_analysis:
            summary = workspace_analysis.get("summary", {})
            state["workspace"] = {
                "total_files": summary.get("total_files", 0),
                "python_files": summary.get("python_files", 0),
                "components_found": summary.get("components_found", 0),
                "completeness_score": workspace_analysis.get("completeness", {}).get("completeness_score", 0)
            }

        if bmc_inventory:
            summary = bmc_inventory.get("summary", {})
            state["components"] = {
                "quotation_engine": summary.get("quotation_engine_found", False),
                "products": summary.get("products_found", 0),
                "zones": summary.get("zones_found", 0),
                "integrations": summary.get("integrations_found", 0),
                "n8n_workflows": summary.get("n8n_workflows_found", False)
            }

        if integrations_status:
            summary = integrations_status.get("summary", {})
            state["integrations"] = {
                "configured": summary.get("configured", 0),
                "partially_configured": summary.get("partially_configured", 0),
                "readiness_score": summary.get("readiness_score", 0)
            }

        if quotation_assessment:
            summary = quotation_assessment.get("summary", {})
            state["quotation_engine"] = {
                "overall_completeness": summary.get("overall_completeness", 0),
                "status": summary.get("status", "unknown")
            }

        return state

    def _define_metrics(self, repo_analysis: Dict = None, workspace_analysis: Dict = None,
                        bmc_inventory: Dict = None, integrations_status: Dict = None,
                        quotation_assessment: Dict = None, production_gaps: Dict = None) -> Dict[str, Any]:
        """Define success metrics"""
        metrics = {
            "components_identified": 0,
            "integrations_configured": 0,
            "production_readiness": 0.0,
            "code_quality": 0.0,
            "documentation_coverage": 0.0
        }

        if bmc_inventory:
            summary = bmc_inventory.get("summary", {})
            metrics["components_identified"] = summary.get("components_found", 0)

        if integrations_status:
            summary = integrations_status.get("summary", {})
            metrics["integrations_configured"] = summary.get("configured", 0)

        if production_gaps:
            summary = production_gaps.get("summary", {})
            metrics["production_readiness"] = summary.get("production_readiness", 0.0)

        if workspace_analysis:
            completeness = workspace_analysis.get("completeness", {})
            metrics["code_quality"] = completeness.get("completeness_score", 0.0)

            files_data = workspace_analysis.get("files", {})
            md_count = files_data.get("markdown_count", 0)
            total_files = files_data.get("total_count", 1)
            metrics["documentation_coverage"] = round(min(md_count / (total_files * 0.1), 1.0), 2)

        return metrics

    def _create_production_checklist(self, production_gaps: Dict = None) -> List[Dict[str, Any]]:
        """Create production readiness checklist"""
        checklist = [
            {
                "category": "integrations",
                "item": "WhatsApp Business API configured",
                "status": "pending",
                "priority": "P0"
            },
            {
                "category": "integrations",
                "item": "n8n workflows configured",
                "status": "pending",
                "priority": "P0"
            },
            {
                "category": "integrations",
                "item": "Qdrant vector database configured",
                "status": "pending",
                "priority": "P1"
            },
            {
                "category": "security",
                "item": "Webhook signature validation implemented",
                "status": "pending",
                "priority": "P0"
            },
            {
                "category": "security",
                "item": "Secrets management configured",
                "status": "pending",
                "priority": "P0"
            },
            {
                "category": "security",
                "item": "Rate limiting implemented",
                "status": "pending",
                "priority": "P1"
            },
            {
                "category": "infrastructure",
                "item": "Docker configuration complete",
                "status": "pending",
                "priority": "P0"
            },
            {
                "category": "infrastructure",
                "item": "CI/CD pipeline configured",
                "status": "pending",
                "priority": "P1"
            },
            {
                "category": "monitoring",
                "item": "Logging system configured",
                "status": "pending",
                "priority": "P1"
            },
            {
                "category": "monitoring",
                "item": "Metrics collection set up",
                "status": "pending",
                "priority": "P1"
            },
            {
                "category": "quotation_engine",
                "item": "Product catalog complete",
                "status": "pending",
                "priority": "P0"
            },
            {
                "category": "quotation_engine",
                "item": "Pricing zones configured",
                "status": "pending",
                "priority": "P0"
            }
        ]

        # Update checklist based on gaps
        if production_gaps:
            gaps = production_gaps.get("prioritized_gaps", [])
            for gap in gaps:
                category = gap.get("category", "")
                component = gap.get("component", "")

                # Find matching checklist item
                for item in checklist:
                    if item["category"] == category and component.lower() in item["item"].lower():
                        item["status"] = "blocked"
                        break

        return checklist

    def _define_acceptance_criteria(self) -> Dict[str, Any]:
        """Define acceptance criteria for production"""
        return {
            "integrations": {
                "whatsapp": "Fully configured with webhook validation",
                "n8n": "Workflows imported and functional",
                "qdrant": "Connected and collections created"
            },
            "security": {
                "webhook_validation": "All webhooks validate signatures",
                "secrets_management": "No hardcoded credentials",
                "rate_limiting": "Rate limits configured for all endpoints"
            },
            "quotation_engine": {
                "products": "All products (Isodec, Isoroof, Isopanel) supported",
                "zones": "All zones (Montevideo, Canelones, Maldonado, Rivera) configured",
                "completeness": "Overall completeness >= 0.9"
            },
            "infrastructure": {
                "docker": "Docker compose configuration complete",
                "ci_cd": "CI/CD pipeline runs successfully",
                "monitoring": "Logging and metrics collection active"
            },
            "performance": {
                "response_time": "API response time < 2s (p95)",
                "availability": "System availability >= 99.5%"
            }
        }

    def _define_success_metrics(self) -> Dict[str, Any]:
        """Define success metrics for production"""
        return {
            "production_readiness": {
                "target": 0.95,
                "current": 0.0,
                "unit": "score"
            },
            "integration_readiness": {
                "target": 1.0,
                "current": 0.0,
                "unit": "score"
            },
            "quotation_completeness": {
                "target": 0.9,
                "current": 0.0,
                "unit": "score"
            },
            "security_score": {
                "target": 0.95,
                "current": 0.0,
                "unit": "score"
            },
            "code_quality": {
                "target": 0.8,
                "current": 0.0,
                "unit": "score"
            }
        }

    def _generate_summary(self, baseline: Dict[str, Any]) -> Dict[str, Any]:
        """Generate baseline summary"""
        current_state = baseline.get("current_state", {})
        metrics = baseline.get("metrics", {})
        checklist = baseline.get("production_checklist", [])

        completed_items = sum(1 for item in checklist if item.get("status") == "completed")
        total_items = len(checklist)

        return {
            "baseline_date": baseline.get("baseline_date", ""),
            "phase": current_state.get("phase", "unknown"),
            "components_identified": metrics.get("components_identified", 0),
            "integrations_configured": metrics.get("integrations_configured", 0),
            "production_readiness": metrics.get("production_readiness", 0.0),
            "checklist_progress": f"{completed_items}/{total_items}",
            "status": "baseline_created"
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Create production baseline")
    parser.add_argument("--discovery-dir", "-d", default="consolidation/discovery",
                       help="Directory containing discovery results")
    parser.add_argument("--output", "-o", default="consolidation/discovery/production_baseline.json",
                       help="Output file path")

    args = parser.parse_args()

    # Create baseline
    creator = ProductionBaselineCreator(discovery_results_dir=args.discovery_dir)
    baseline = creator.create()

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(baseline, f, indent=2, ensure_ascii=False)

    print(f"✅ Results saved to: {output_path}")
    print(f"📊 Summary: {baseline.get('summary', {})}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

