#!/usr/bin/env python3
"""
Phase 1: Component Mapping Script
Maps all components and their relationships
"""

import json
import os
import ast
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Set

def extract_imports(file_path: Path) -> List[str]:
    """Extract imports from a Python file"""
    imports = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=str(file_path))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)
            except (SyntaxError, UnicodeDecodeError):
                pass
    except Exception:
        pass
    return imports

def map_components(workspace_path: str) -> Dict[str, Any]:
    """Map all components and their relationships"""
    workspace = Path(workspace_path)
    
    components = {
        "core_services": [],
        "integrations": [],
        "utilities": [],
        "data_models": [],
        "api_endpoints": [],
        "dependencies": {},
        "relationships": []
    }
    
    # Core services
    core_files = {
        "api_server.py": {"category": "API", "type": "FastAPI Server"},
        "ia_conversacional_integrada.py": {"category": "AI", "type": "Conversational AI"},
        "sistema_cotizaciones.py": {"category": "Business Logic", "type": "Quotation Engine"},
        "base_conocimiento_dinamica.py": {"category": "Knowledge Base", "type": "Dynamic KB"},
        "motor_analisis_conversaciones.py": {"category": "Analytics", "type": "Conversation Analysis"}
    }
    
    for filename, info in core_files.items():
        file_path = workspace / filename
        if file_path.exists():
            imports = extract_imports(file_path)
            component = {
                "name": filename,
                "path": str(file_path.relative_to(workspace)),
                "category": info["category"],
                "type": info["type"],
                "imports": imports,
                "dependencies": [imp for imp in imports if not imp.startswith(".")]
            }
            components["core_services"].append(component)
    
    # Integrations
    integration_files = {
        "integracion_whatsapp.py": {"type": "WhatsApp Business API"},
        "n8n_integration.py": {"type": "n8n Workflows"},
        "mongodb_service.py": {"type": "MongoDB Database"},
        "model_integrator.py": {"type": "AI Model Integration"}
    }
    
    for filename, info in integration_files.items():
        file_path = workspace / filename
        if file_path.exists():
            imports = extract_imports(file_path)
            component = {
                "name": filename,
                "path": str(file_path.relative_to(workspace)),
                "type": info["type"],
                "imports": imports,
                "dependencies": [imp for imp in imports if not imp.startswith(".")]
            }
            components["integrations"].append(component)
    
    # Utilities
    utils_dir = workspace / "utils"
    if utils_dir.exists():
        for util_file in utils_dir.rglob("*.py"):
            if util_file.is_file() and not util_file.name.startswith("__"):
                imports = extract_imports(util_file)
                components["utilities"].append({
                    "name": util_file.name,
                    "path": str(util_file.relative_to(workspace)),
                    "imports": imports
                })
    
    # Build dependency graph
    all_components = components["core_services"] + components["integrations"] + components["utilities"]
    
    for component in all_components:
        comp_name = Path(component["name"]).stem
        for dep in component.get("dependencies", []):
            # Check if dependency is a local component
            for other_comp in all_components:
                other_name = Path(other_comp["name"]).stem
                if dep == other_name or dep.endswith(f".{other_name}"):
                    components["relationships"].append({
                        "from": comp_name,
                        "to": other_name,
                        "type": "imports"
                    })
    
    # External dependencies summary
    all_deps = set()
    for component in all_components:
        all_deps.update(component.get("dependencies", []))
    
    components["dependencies"] = {
        "external": sorted([d for d in all_deps if not any(d.startswith(c["name"].split(".")[0]) for c in all_components)]),
        "internal": sorted([d for d in all_deps if any(d.startswith(c["name"].split(".")[0]) for c in all_components)])
    }
    
    return components

def main():
    """Main execution function"""
    workspace_path = "/Users/matias/chatbot2511/chatbot-2311"
    output_dir = Path(workspace_path) / "consolidation" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔍 Starting Phase 1: Component Mapping...")
    
    # Perform mapping
    mapping = map_components(workspace_path)
    
    # Add metadata
    mapping["phase"] = 1
    mapping["task"] = "T1.3 - Component Mapping"
    mapping["timestamp"] = datetime.now(timezone.utc).isoformat()
    mapping["summary"] = {
        "core_services": len(mapping["core_services"]),
        "integrations": len(mapping["integrations"]),
        "utilities": len(mapping["utilities"]),
        "relationships": len(mapping["relationships"]),
        "external_dependencies": len(mapping["dependencies"]["external"])
    }
    
    # Save output
    output_file = output_dir / "component_mapping.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Mapping complete! Output saved to: {output_file}")
    print(f"📊 Summary:")
    print(f"   - Core services: {mapping['summary']['core_services']}")
    print(f"   - Integrations: {mapping['summary']['integrations']}")
    print(f"   - Utilities: {mapping['summary']['utilities']}")
    print(f"   - Relationships: {mapping['summary']['relationships']}")
    print(f"   - External dependencies: {mapping['summary']['external_dependencies']}")
    
    return str(output_file)

if __name__ == "__main__":
    main()

