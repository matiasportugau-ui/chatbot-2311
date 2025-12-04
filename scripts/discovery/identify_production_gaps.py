#!/usr/bin/env python3
"""
T0.6: Identificación de gaps de producción
Identifies production readiness gaps by comparing current state vs production requirements
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class ProductionGapIdentifier:
    """Identifies gaps between current state and production requirements"""

    def __init__(self, discovery_results_dir: str = "consolidation/discovery"):
        self.discovery_dir = Path(discovery_results_dir)
        self.production_requirements = self._load_production_requirements()

    def identify(self, repository_analysis: Dict = None, integrations_status: Dict = None,
                 quotation_assessment: Dict = None) -> Dict[str, Any]:
        """Identify production gaps"""
        print("🔍 Identifying production gaps...")

        # Load discovery results if not provided
        if not repository_analysis:
            repo_file = self.discovery_dir / "repository_analysis.json"
            if repo_file.exists():
                repository_analysis = json.loads(repo_file.read_text(encoding='utf-8'))

        if not integrations_status:
            int_file = self.discovery_dir / "integrations_status.json"
            if int_file.exists():
                integrations_status = json.loads(int_file.read_text(encoding='utf-8'))

        if not quotation_assessment:
            quot_file = self.discovery_dir / "quotation_assessment.json"
            if quot_file.exists():
                quotation_assessment = json.loads(quot_file.read_text(encoding='utf-8'))

        results = {
            "gap_analysis_date": datetime.now().isoformat(),
            "critical_blockers": self._identify_critical_blockers(integrations_status, quotation_assessment),
            "improvements": self._identify_improvements(repository_analysis, integrations_status),
            "security_gaps": self._identify_security_gaps(integrations_status),
            "infrastructure_gaps": self._identify_infrastructure_gaps(repository_analysis),
            "monitoring_gaps": self._identify_monitoring_gaps(),
            "prioritized_gaps": [],
            "summary": {}
        }

        # Prioritize all gaps
        results["prioritized_gaps"] = self._prioritize_gaps(results)

        # Generate summary
        results["summary"] = self._generate_summary(results)

        print("✅ Production gap identification complete")
        return results

    def _load_production_requirements(self) -> Dict[str, Any]:
        """Load production requirements checklist"""
        return {
            "integrations": {
                "whatsapp": {"required": True, "priority": "P0"},
                "n8n": {"required": True, "priority": "P0"},
                "qdrant": {"required": True, "priority": "P1"},
                "chatwoot": {"required": False, "priority": "P2"}
            },
            "security": {
                "webhook_validation": {"required": True, "priority": "P0"},
                "secrets_management": {"required": True, "priority": "P0"},
                "rate_limiting": {"required": True, "priority": "P1"},
                "authentication": {"required": True, "priority": "P1"}
            },
            "infrastructure": {
                "docker": {"required": True, "priority": "P0"},
                "ci_cd": {"required": True, "priority": "P1"},
                "monitoring": {"required": True, "priority": "P1"},
                "logging": {"required": True, "priority": "P1"}
            },
            "quotation_engine": {
                "products_complete": {"required": True, "priority": "P0"},
                "zones_complete": {"required": True, "priority": "P0"},
                "pricing_logic": {"required": True, "priority": "P0"}
            }
        }

    def _identify_critical_blockers(self, integrations_status: Dict = None,
                                    quotation_assessment: Dict = None) -> List[Dict[str, Any]]:
        """Identify critical blockers for production"""
        blockers = []

        # Check integrations
        if integrations_status:
            integrations = integrations_status.get("whatsapp", {})
            if integrations.get("status") != "configured":
                blockers.append({
                    "category": "integration",
                    "component": "whatsapp",
                    "description": "WhatsApp integration not fully configured",
                    "priority": "P0",
                    "impact": "critical"
                })

            integrations = integrations_status.get("n8n", {})
            if integrations.get("status") != "configured":
                blockers.append({
                    "category": "integration",
                    "component": "n8n",
                    "description": "n8n integration not fully configured",
                    "priority": "P0",
                    "impact": "critical"
                })

        # Check quotation engine
        if quotation_assessment:
            summary = quotation_assessment.get("summary", {})
            if summary.get("overall_completeness", 0) < 0.7:
                blockers.append({
                    "category": "quotation_engine",
                    "component": "completeness",
                    "description": f"Quotation engine completeness below threshold: {summary.get('overall_completeness', 0)}",
                    "priority": "P0",
                    "impact": "critical"
                })

        return blockers

    def _identify_improvements(self, repository_analysis: Dict = None,
                               integrations_status: Dict = None) -> List[Dict[str, Any]]:
        """Identify improvements needed"""
        improvements = []

        # Check for duplicate code
        if repository_analysis:
            duplicates = repository_analysis.get("duplicates", [])
            if duplicates:
                improvements.append({
                    "category": "code_quality",
                    "description": f"Found {len(duplicates)} duplicate files across repositories",
                    "priority": "P1",
                    "impact": "medium"
                })

        # Check integration completeness
        if integrations_status:
            summary = integrations_status.get("summary", {})
            if summary.get("readiness_score", 0) < 0.75:
                improvements.append({
                    "category": "integration",
                    "description": f"Integration readiness score: {summary.get('readiness_score', 0)}",
                    "priority": "P1",
                    "impact": "medium"
                })

        return improvements

    def _identify_security_gaps(self, integrations_status: Dict = None) -> List[Dict[str, Any]]:
        """Identify security gaps"""
        gaps = []

        if integrations_status:
            whatsapp = integrations_status.get("whatsapp", {})
            if not whatsapp.get("configuration", {}).get("signature_validation", False):
                gaps.append({
                    "category": "security",
                    "component": "whatsapp",
                    "description": "WhatsApp webhook signature validation not implemented",
                    "priority": "P0",
                    "impact": "high"
                })

        # Standard security gaps
        gaps.extend([
            {
                "category": "security",
                "component": "secrets",
                "description": "Secrets management not implemented (using environment variables directly)",
                "priority": "P0",
                "impact": "high"
            },
            {
                "category": "security",
                "component": "rate_limiting",
                "description": "Rate limiting not implemented",
                "priority": "P1",
                "impact": "medium"
            }
        ])

        return gaps

    def _identify_infrastructure_gaps(self, repository_analysis: Dict = None) -> List[Dict[str, Any]]:
        """Identify infrastructure gaps"""
        gaps = []

        # Check for Docker
        if repository_analysis:
            repos = repository_analysis.get("repositories", [])
            docker_found = False
            # Handle both list and dict formats
            if isinstance(repos, dict):
                repos_list = list(repos.values())
            else:
                repos_list = repos if isinstance(repos, list) else []

            # Check technologies list directly from repository_analysis
            techs = repository_analysis.get("technologies", [])
            if "Docker" in techs:
                docker_found = True
            else:
                # Also check individual repos if they have tech info
                for repo_data in repos_list:
                    if isinstance(repo_data, dict):
                        repo_techs = repo_data.get("technologies", [])
                        if "Docker" in repo_techs:
                            docker_found = True
                            break

            if not docker_found:
                gaps.append({
                    "category": "infrastructure",
                    "component": "docker",
                    "description": "Docker configuration not found",
                    "priority": "P0",
                    "impact": "high"
                })

        gaps.extend([
            {
                "category": "infrastructure",
                "component": "ci_cd",
                "description": "CI/CD pipeline not configured",
                "priority": "P1",
                "impact": "medium"
            },
            {
                "category": "infrastructure",
                "component": "monitoring",
                "description": "Monitoring and observability not set up",
                "priority": "P1",
                "impact": "medium"
            }
        ])

        return gaps

    def _identify_monitoring_gaps(self) -> List[Dict[str, Any]]:
        """Identify monitoring gaps"""
        return [
            {
                "category": "monitoring",
                "component": "logging",
                "description": "Structured logging not implemented",
                "priority": "P1",
                "impact": "medium"
            },
            {
                "category": "monitoring",
                "component": "metrics",
                "description": "Metrics collection not set up",
                "priority": "P1",
                "impact": "medium"
            },
            {
                "category": "monitoring",
                "component": "alerts",
                "description": "Alerting system not configured",
                "priority": "P2",
                "impact": "low"
            }
        ]

    def _prioritize_gaps(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize all identified gaps"""
        all_gaps = []

        # Collect all gaps
        all_gaps.extend(results.get("critical_blockers", []))
        all_gaps.extend(results.get("improvements", []))
        all_gaps.extend(results.get("security_gaps", []))
        all_gaps.extend(results.get("infrastructure_gaps", []))
        all_gaps.extend(results.get("monitoring_gaps", []))

        # Sort by priority (P0 > P1 > P2) and impact (critical > high > medium > low)
        priority_order = {"P0": 0, "P1": 1, "P2": 2}
        impact_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

        all_gaps.sort(key=lambda x: (
            priority_order.get(x.get("priority", "P2"), 2),
            impact_order.get(x.get("impact", "low"), 3)
        ))

        return all_gaps

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate gap analysis summary"""
        prioritized = results.get("prioritized_gaps", [])

        p0_count = sum(1 for g in prioritized if g.get("priority") == "P0")
        p1_count = sum(1 for g in prioritized if g.get("priority") == "P1")
        p2_count = sum(1 for g in prioritized if g.get("priority") == "P2")

        critical_count = sum(1 for g in prioritized if g.get("impact") == "critical")

        return {
            "total_gaps": len(prioritized),
            "critical_blockers": len(results.get("critical_blockers", [])),
            "p0_gaps": p0_count,
            "p1_gaps": p1_count,
            "p2_gaps": p2_count,
            "critical_impact": critical_count,
            "production_readiness": max(0, 1.0 - (p0_count * 0.2) - (p1_count * 0.1)),
            "status": "completed"
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Identify production gaps")
    parser.add_argument("--discovery-dir", "-d", default="consolidation/discovery",
                       help="Directory containing discovery results")
    parser.add_argument("--output", "-o", default="consolidation/discovery/production_gaps.json",
                       help="Output file path")

    args = parser.parse_args()

    # Run gap identification
    identifier = ProductionGapIdentifier(discovery_results_dir=args.discovery_dir)
    results = identifier.identify()

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

