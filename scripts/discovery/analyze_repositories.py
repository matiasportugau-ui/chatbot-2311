#!/usr/bin/env python3
"""
Phase 1: Repository Analysis Script
Analyzes repository structure, technologies, dependencies, and identifies duplicates
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import subprocess

def analyze_repository_structure(workspace_path: str) -> Dict[str, Any]:
    """Analyze the repository structure"""
    workspace = Path(workspace_path)
    
    structure = {
        "root": str(workspace),
        "directories": [],
        "python_files": [],
        "markdown_files": [],
        "config_files": [],
        "docker_files": [],
        "total_files": 0
    }
    
    # Count files by type
    for root, dirs, files in os.walk(workspace):
        # Skip hidden directories and common ignore patterns
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]
        
        for file in files:
            if file.startswith('.'):
                continue
                
            file_path = Path(root) / file
            rel_path = file_path.relative_to(workspace)
            
            structure["total_files"] += 1
            
            if file.endswith('.py'):
                structure["python_files"].append(str(rel_path))
            elif file.endswith('.md'):
                structure["markdown_files"].append(str(rel_path))
            elif file.endswith(('.json', '.yaml', '.yml', '.toml', '.env')):
                structure["config_files"].append(str(rel_path))
            elif 'docker' in file.lower() or file == 'Dockerfile':
                structure["docker_files"].append(str(rel_path))
    
    # Get top-level directories
    for item in workspace.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            structure["directories"].append(item.name)
    
    return structure

def analyze_technologies(workspace_path: str) -> Dict[str, Any]:
    """Identify technologies and frameworks used"""
    workspace = Path(workspace_path)
    
    technologies = {
        "languages": [],
        "frameworks": [],
        "databases": [],
        "services": [],
        "tools": []
    }
    
    # Check for Python
    if (workspace / "requirements.txt").exists():
        technologies["languages"].append("Python")
        technologies["frameworks"].append("FastAPI")  # Based on api_server.py
    
    # Check for Node.js/Next.js
    if (workspace / "package.json").exists():
        technologies["languages"].append("TypeScript/JavaScript")
        technologies["frameworks"].append("Next.js")
    
    # Check for Docker
    if (workspace / "docker-compose.yml").exists() or (workspace / "Dockerfile").exists():
        technologies["tools"].append("Docker")
    
    # Check for MongoDB
    if (workspace / "mongodb_service.py").exists() or "pymongo" in open(workspace / "requirements.txt").read():
        technologies["databases"].append("MongoDB")
    
    # Check for n8n
    if (workspace / "n8n_integration.py").exists() or (workspace / "n8n_workflows").exists():
        technologies["services"].append("n8n")
    
    # Check for Qdrant
    if "qdrant" in str(workspace).lower() or any("qdrant" in str(f) for f in (workspace / "consolidation").rglob("*") if (workspace / "consolidation").exists()):
        technologies["databases"].append("Qdrant")
    
    return technologies

def analyze_dependencies(workspace_path: str) -> Dict[str, Any]:
    """Map dependencies from requirements.txt and package.json"""
    workspace = Path(workspace_path)
    
    dependencies = {
        "python": [],
        "node": [],
        "system": []
    }
    
    # Python dependencies
    if (workspace / "requirements.txt").exists():
        with open(workspace / "requirements.txt", 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    dependencies["python"].append(line.split('>=')[0].split('==')[0].strip())
    
    # Node dependencies
    if (workspace / "package.json").exists():
        import json as json_module
        with open(workspace / "package.json", 'r') as f:
            package_data = json_module.load(f)
            if "dependencies" in package_data:
                dependencies["node"].extend(list(package_data["dependencies"].keys()))
            if "devDependencies" in package_data:
                dependencies["node"].extend([f"{dep} (dev)" for dep in package_data["devDependencies"].keys()])
    
    return dependencies

def identify_duplicates(workspace_path: str) -> Dict[str, Any]:
    """Identify potential duplicate files and components"""
    workspace = Path(workspace_path)
    
    duplicates = {
        "potential_duplicates": [],
        "similar_files": [],
        "duplicate_functions": []
    }
    
    # Check for similar file names
    python_files = list(workspace.rglob("*.py"))
    file_basenames = {}
    
    for py_file in python_files:
        basename = py_file.stem
        if basename in file_basenames:
            duplicates["similar_files"].append({
                "basename": basename,
                "files": [str(file_basenames[basename]), str(py_file)]
            })
        else:
            file_basenames[basename] = py_file
    
    # Check for multiple versions of same concept
    concepts = {
        "chatbot": [],
        "cotizacion": [],
        "integration": [],
        "api": []
    }
    
    for py_file in python_files:
        name_lower = py_file.stem.lower()
        if "chatbot" in name_lower or "chat" in name_lower:
            concepts["chatbot"].append(str(py_file))
        if "cotizacion" in name_lower or "quotation" in name_lower:
            concepts["cotizacion"].append(str(py_file))
        if "integration" in name_lower or "integracion" in name_lower:
            concepts["integration"].append(str(py_file))
        if "api" in name_lower:
            concepts["api"].append(str(py_file))
    
    for concept, files in concepts.items():
        if len(files) > 1:
            duplicates["potential_duplicates"].append({
                "concept": concept,
                "files": files,
                "count": len(files)
            })
    
    return duplicates

def main():
    """Main execution function"""
    workspace_path = "/Users/matias/chatbot2511/chatbot-2311"
    output_dir = Path(workspace_path) / "consolidation" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔍 Starting Phase 1: Repository Analysis...")
    
    # Perform analysis
    structure = analyze_repository_structure(workspace_path)
    technologies = analyze_technologies(workspace_path)
    dependencies = analyze_dependencies(workspace_path)
    duplicates = identify_duplicates(workspace_path)
    
    # Compile results
    analysis = {
        "phase": 1,
        "task": "T1.1 - Repository Analysis",
        "timestamp": datetime.utcnow().isoformat(),
        "workspace": workspace_path,
        "structure": structure,
        "technologies": technologies,
        "dependencies": dependencies,
        "duplicates": duplicates,
        "summary": {
            "total_files": structure["total_files"],
            "python_files_count": len(structure["python_files"]),
            "markdown_files_count": len(structure["markdown_files"]),
            "languages": technologies["languages"],
            "frameworks": technologies["frameworks"],
            "potential_duplicates": len(duplicates["potential_duplicates"])
        }
    }
    
    # Save output
    output_file = output_dir / "repository_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Analysis complete! Output saved to: {output_file}")
    print(f"📊 Summary:")
    print(f"   - Total files: {structure['total_files']}")
    print(f"   - Python files: {len(structure['python_files'])}")
    print(f"   - Markdown files: {len(structure['markdown_files'])}")
    print(f"   - Technologies: {', '.join(technologies['languages'])}")
    print(f"   - Potential duplicates: {len(duplicates['potential_duplicates'])}")
    
    return str(output_file)

if __name__ == "__main__":
    main()
