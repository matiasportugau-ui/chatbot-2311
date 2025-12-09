#!/usr/bin/env python3
"""
Phase 1: Workspace Analysis Script
Analyzes workspace structure and identifies functional components
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

def analyze_workspace_structure(workspace_path: str) -> Dict[str, Any]:
    """Analyze workspace structure and identify functional components"""
    workspace = Path(workspace_path)
    
    analysis = {
        "workspace_path": str(workspace),
        "key_components": [],
        "functional_modules": [],
        "configuration_files": [],
        "documentation_files": [],
        "test_files": [],
        "completeness_indicators": {}
    }
    
    # Key components mapping
    key_files = {
        "api_server.py": {"type": "API", "status": "functional", "description": "FastAPI main server"},
        "ia_conversacional_integrada.py": {"type": "AI", "status": "functional", "description": "Conversational AI engine"},
        "sistema_cotizaciones.py": {"type": "Business Logic", "status": "functional", "description": "Quotation system"},
        "base_conocimiento_dinamica.py": {"type": "Knowledge Base", "status": "functional", "description": "Dynamic knowledge base"},
        "integracion_whatsapp.py": {"type": "Integration", "status": "functional", "description": "WhatsApp integration"},
        "n8n_integration.py": {"type": "Integration", "status": "functional", "description": "n8n workflow integration"},
        "mongodb_service.py": {"type": "Database", "status": "functional", "description": "MongoDB service"},
        "model_integrator.py": {"type": "AI", "status": "functional", "description": "AI model integrator"}
    }
    
    # Check for key files
    for filename, info in key_files.items():
        file_path = workspace / filename
        if file_path.exists():
            file_info = info.copy()
            file_info["path"] = str(file_path)
            file_info["size"] = file_path.stat().st_size
            analysis["key_components"].append(file_info)
    
    # Identify functional modules by directory
    functional_dirs = {
        "backup_system": "Backup and recovery system",
        "scripts": "Utility scripts",
        "utils": "Utility functions",
        "system": "System modules",
        "data": "Data storage",
        "n8n_workflows": "n8n workflow definitions",
        "nextjs-app": "Next.js frontend application",
        "consolidation": "Consolidation artifacts"
    }
    
    for dir_name, description in functional_dirs.items():
        dir_path = workspace / dir_name
        if dir_path.exists() and dir_path.is_dir():
            analysis["functional_modules"].append({
                "name": dir_name,
                "path": str(dir_path),
                "description": description,
                "file_count": len(list(dir_path.rglob("*"))) if dir_path.exists() else 0
            })
    
    # Configuration files
    config_patterns = ["*.json", "*.yaml", "*.yml", "*.toml", "*.env", "docker-compose*.yml", "Dockerfile*"]
    for pattern in config_patterns:
        for config_file in workspace.rglob(pattern):
            if config_file.is_file() and not any(skip in str(config_file) for skip in ['.git', 'node_modules', '__pycache__']):
                analysis["configuration_files"].append({
                    "name": config_file.name,
                    "path": str(config_file.relative_to(workspace)),
                    "type": config_file.suffix
                })
    
    # Documentation files
    for md_file in workspace.rglob("*.md"):
        if md_file.is_file() and not any(skip in str(md_file) for skip in ['.git', 'node_modules']):
            analysis["documentation_files"].append({
                "name": md_file.name,
                "path": str(md_file.relative_to(workspace)),
                "size": md_file.stat().st_size
            })
    
    # Test files
    for test_file in workspace.rglob("test_*.py"):
        if test_file.is_file():
            analysis["test_files"].append({
                "name": test_file.name,
                "path": str(test_file.relative_to(workspace))
            })
    
    # Completeness indicators
    analysis["completeness_indicators"] = {
        "has_api_server": any("api_server" in str(c["path"]) for c in analysis["key_components"]),
        "has_ai_engine": any("ia_conversacional" in str(c["path"]) for c in analysis["key_components"]),
        "has_quotation_system": any("cotizacion" in str(c["path"]) for c in analysis["key_components"]),
        "has_whatsapp_integration": any("whatsapp" in str(c["path"]) for c in analysis["key_components"]),
        "has_n8n_integration": any("n8n" in str(c["path"]) for c in analysis["key_components"]),
        "has_database": any("mongodb" in str(c["path"]) for c in analysis["key_components"]),
        "has_docker": any("docker-compose" in str(c["path"]) for c in analysis["configuration_files"]),
        "has_frontend": any("nextjs" in m["name"] for m in analysis["functional_modules"]),
        "documentation_count": len(analysis["documentation_files"]),
        "test_coverage": len(analysis["test_files"])
    }
    
    # Calculate completeness percentage
    indicators = analysis["completeness_indicators"]
    required_components = [
        indicators["has_api_server"],
        indicators["has_ai_engine"],
        indicators["has_quotation_system"],
        indicators["has_whatsapp_integration"],
        indicators["has_docker"]
    ]
    analysis["completeness_percentage"] = (sum(required_components) / len(required_components)) * 100
    
    return analysis

def main():
    """Main execution function"""
    workspace_path = "/Users/matias/chatbot2511/chatbot-2311"
    output_dir = Path(workspace_path) / "consolidation" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔍 Starting Phase 1: Workspace Analysis...")
    
    # Perform analysis
    analysis = analyze_workspace_structure(workspace_path)
    
    # Add metadata
    analysis["phase"] = 1
    analysis["task"] = "T1.2 - Workspace Analysis"
    analysis["timestamp"] = datetime.now(timezone.utc).isoformat()
    
    # Save output
    output_file = output_dir / "workspace_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Analysis complete! Output saved to: {output_file}")
    print(f"📊 Summary:")
    print(f"   - Key components: {len(analysis['key_components'])}")
    print(f"   - Functional modules: {len(analysis['functional_modules'])}")
    print(f"   - Configuration files: {len(analysis['configuration_files'])}")
    print(f"   - Documentation files: {len(analysis['documentation_files'])}")
    print(f"   - Completeness: {analysis['completeness_percentage']:.1f}%")
    
    return str(output_file)

if __name__ == "__main__":
    main()
