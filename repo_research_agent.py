#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente Especializado en Investigación de Repositorios iOS
==========================================================

Agente de IA que investiga todos los repositorios de GitHub iOS y sus branches,
evalúa el estado del workspace local, identifica mejoras desde distintos orígenes,
y genera un plan de consolidación y mejora cruzada para crear un nuevo repositorio evolucionado.

Basado en patrones de Prompt Engineering y Model Integrator del proyecto.
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import re

# Importar dependencias del proyecto
try:
    from model_integrator import get_model_integrator
    MODEL_INTEGRATOR_AVAILABLE = True
except ImportError:
    MODEL_INTEGRATOR_AVAILABLE = False
    print("⚠️  Model Integrator no disponible")

try:
    from github_analyzer import GitHubAnalyzer
    GITHUB_ANALYZER_AVAILABLE = True
except ImportError:
    GITHUB_ANALYZER_AVAILABLE = False
    print("⚠️  GitHub Analyzer no disponible")

try:
    from prompt_generator import PromptGenerator
    PROMPT_GENERATOR_AVAILABLE = True
except ImportError:
    PROMPT_GENERATOR_AVAILABLE = False
    print("⚠️  Prompt Generator no disponible")


class RepoResearchAgent:
    """
    Agente especializado en investigación de repositorios iOS y análisis de workspace
    """
    
    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        self.model_integrator = None
        self.github_analyzer = None
        self.prompt_generator = None
        
        # Inicializar componentes
        self._initialize_components()
        
        # Datos de investigación
        self.github_repos = []
        self.local_workspace_analysis = {}
        self.improvements_identified = []
        self.consolidation_plan = {}
        
    def _initialize_components(self):
        """Inicializa componentes del sistema"""
        # Model Integrator para IA
        if MODEL_INTEGRATOR_AVAILABLE:
            try:
                self.model_integrator = get_model_integrator()
                print("✅ Model Integrator inicializado")
            except Exception as e:
                print(f"⚠️  Error inicializando Model Integrator: {e}")
        
        # GitHub Analyzer
        if GITHUB_ANALYZER_AVAILABLE:
            try:
                self.github_analyzer = GitHubAnalyzer()
                print("✅ GitHub Analyzer inicializado")
            except Exception as e:
                print(f"⚠️  Error inicializando GitHub Analyzer: {e}")
        
        # Prompt Generator
        if PROMPT_GENERATOR_AVAILABLE:
            try:
                self.prompt_generator = PromptGenerator()
                print("✅ Prompt Generator inicializado")
            except Exception as e:
                print(f"⚠️  Error inicializando Prompt Generator: {e}")
    
    def _generate_agent_prompt(self) -> str:
        """Genera el prompt del agente usando Prompt Generator"""
        if not self.prompt_generator:
            # Fallback prompt
            return """Eres un agente especializado en investigación de repositorios iOS y análisis de código.
Tu misión es:
1. Investigar todos los repositorios de GitHub iOS y sus branches
2. Evaluar el estado del workspace local
3. Identificar mejoras desde distintos orígenes
4. Generar un plan de consolidación y mejora cruzada
5. Proponer un nuevo repositorio evolucionado"""
        
        return self.prompt_generator.generate_agent_prompt(
            role="Investigador Especializado en Repositorios iOS",
            domain="análisis de código, consolidación de repositorios, arquitectura de software",
            pattern="react",
            task="Investigar repositorios iOS, evaluar workspace local, y generar plan de consolidación",
            context="Análisis completo de ecosistema de repositorios iOS y workspace local",
            tools=[
                "GitHub API para descubrir repositorios y branches",
                "Análisis de código local",
                "Comparación de versiones",
                "Generación de planes de consolidación",
                "Identificación de mejoras cruzadas"
            ],
            responsibilities=[
                "Descubrir y catalogar todos los repositorios iOS en GitHub",
                "Analizar todos los branches de cada repositorio",
                "Evaluar el estado actual del workspace local",
                "Identificar mejoras y patrones desde distintos orígenes",
                "Generar plan de consolidación con mejoras cruzadas",
                "Proponer arquitectura para nuevo repositorio evolucionado"
            ],
            constraints=[
                "Preservar historial Git cuando sea posible",
                "Mantener compatibilidad con sistemas existentes",
                "Priorizar mejoras que agreguen valor real",
                "Documentar todas las decisiones y razones"
            ]
        )
    
    def research_github_ios_repos(self, owner: str = "matiasportugau-ui", 
                                   keywords: List[str] = None) -> Dict[str, Any]:
        """
        Investiga todos los repositorios iOS en GitHub
        
        Args:
            owner: Propietario/organización de GitHub
            keywords: Palabras clave para filtrar repositorios iOS
        
        Returns:
            Dict con información de repositorios iOS encontrados
        """
        print("\n" + "="*80)
        print("FASE 1: INVESTIGACIÓN DE REPOSITORIOS iOS EN GITHUB")
        print("="*80)
        
        if not self.github_analyzer:
            print("❌ GitHub Analyzer no disponible")
            return {}
        
        # Palabras clave por defecto para iOS
        if keywords is None:
            keywords = ["ios", "swift", "swiftui", "uikit", "xcode", "ios-app", "iphone", "ipad"]
        
        # Descubrir todos los repositorios
        print(f"\n🔍 Descubriendo repositorios bajo {owner}...")
        all_repos = self.github_analyzer.discover_repositories()
        
        # Filtrar repositorios iOS
        ios_repos = []
        for repo in all_repos:
            repo_name_lower = repo["name"].lower()
            description_lower = (repo.get("description", "") or "").lower()
            language = (repo.get("language", "") or "").lower()
            topics = [t.lower() for t in repo.get("topics", [])]
            
            # Verificar si es repositorio iOS
            is_ios = (
                any(keyword in repo_name_lower for keyword in keywords) or
                any(keyword in description_lower for keyword in keywords) or
                language == "swift" or
                any(keyword in " ".join(topics) for keyword in keywords)
            )
            
            if is_ios:
                ios_repos.append(repo)
                print(f"  ✅ Repositorio iOS encontrado: {repo['full_name']}")
        
        print(f"\n📊 Total repositorios iOS encontrados: {len(ios_repos)}")
        
        # Analizar branches de cada repositorio iOS
        ios_repos_with_branches = []
        for repo in ios_repos:
            repo_name = repo["name"]
            print(f"\n🌿 Analizando branches de {repo_name}...")
            
            branches = self.github_analyzer.enumerate_branches(repo_name)
            workflows = self.github_analyzer.discover_workflows(repo_name)
            prs = self.github_analyzer.analyze_pull_requests(repo_name, limit=50)
            
            repo_data = {
                **repo,
                "branches": branches,
                "workflows": workflows,
                "pull_requests": prs,
                "branch_count": len(branches),
                "workflow_count": len(workflows),
                "pr_count": len(prs)
            }
            
            ios_repos_with_branches.append(repo_data)
            print(f"  📦 {len(branches)} branches, {len(workflows)} workflows, {len(prs)} PRs")
        
        self.github_repos = ios_repos_with_branches
        
        return {
            "total_ios_repos": len(ios_repos_with_branches),
            "repositories": ios_repos_with_branches,
            "summary": {
                "total_branches": sum(r["branch_count"] for r in ios_repos_with_branches),
                "total_workflows": sum(r["workflow_count"] for r in ios_repos_with_branches),
                "total_prs": sum(r["pr_count"] for r in ios_repos_with_branches)
            }
        }
    
    def evaluate_local_workspace(self) -> Dict[str, Any]:
        """
        Evalúa el estado del workspace local
        
        Returns:
            Dict con análisis completo del workspace
        """
        print("\n" + "="*80)
        print("FASE 2: EVALUACIÓN DEL WORKSPACE LOCAL")
        print("="*80)
        
        analysis = {
            "workspace_path": str(self.workspace_path),
            "files": {},
            "modules": {},
            "dependencies": {},
            "git_status": {},
            "code_quality": {},
            "documentation": {},
            "configuration": {},
            "issues": [],
            "strengths": [],
            "improvements_needed": []
        }
        
        # Analizar estructura de archivos
        print("\n📁 Analizando estructura de archivos...")
        file_analysis = self._analyze_files()
        analysis["files"] = file_analysis
        
        # Analizar módulos
        print("📦 Analizando módulos...")
        module_analysis = self._analyze_modules()
        analysis["modules"] = module_analysis
        
        # Analizar dependencias
        print("🔗 Analizando dependencias...")
        dependency_analysis = self._analyze_dependencies()
        analysis["dependencies"] = dependency_analysis
        
        # Estado Git
        print("🌿 Analizando estado Git...")
        git_analysis = self._analyze_git_status()
        analysis["git_status"] = git_analysis
        
        # Calidad de código
        print("✨ Analizando calidad de código...")
        quality_analysis = self._analyze_code_quality()
        analysis["code_quality"] = quality_analysis
        
        # Documentación
        print("📚 Analizando documentación...")
        doc_analysis = self._analyze_documentation()
        analysis["documentation"] = doc_analysis
        
        # Configuración
        print("⚙️  Analizando configuración...")
        config_analysis = self._analyze_configuration()
        analysis["configuration"] = config_analysis
        
        # Usar IA para identificar fortalezas y mejoras
        if self.model_integrator:
            print("\n🤖 Usando IA para análisis avanzado...")
            ai_analysis = self._ai_analyze_workspace(analysis)
            analysis["ai_insights"] = ai_analysis
            analysis["strengths"] = ai_analysis.get("strengths", [])
            analysis["improvements_needed"] = ai_analysis.get("improvements", [])
        
        self.local_workspace_analysis = analysis
        
        return analysis
    
    def _analyze_files(self) -> Dict[str, Any]:
        """Analiza archivos del workspace"""
        file_stats = {
            "total_files": 0,
            "by_extension": defaultdict(int),
            "by_type": defaultdict(int),
            "largest_files": [],
            "recent_files": []
        }
        
        try:
            for file_path in self.workspace_path.rglob("*"):
                if file_path.is_file():
                    file_stats["total_files"] += 1
                    
                    # Por extensión
                    ext = file_path.suffix.lower()
                    file_stats["by_extension"][ext] += 1
                    
                    # Por tipo
                    if ext in [".py"]:
                        file_stats["by_type"]["python"] += 1
                    elif ext in [".swift", ".m", ".h"]:
                        file_stats["by_type"]["ios"] += 1
                    elif ext in [".js", ".ts", ".tsx"]:
                        file_stats["by_type"]["javascript"] += 1
                    elif ext in [".md", ".txt"]:
                        file_stats["by_type"]["documentation"] += 1
                    elif ext in [".json", ".yaml", ".yml"]:
                        file_stats["by_type"]["configuration"] += 1
                    
                    # Archivos más grandes
                    try:
                        size = file_path.stat().st_size
                        if size > 100000:  # > 100KB
                            file_stats["largest_files"].append({
                                "path": str(file_path.relative_to(self.workspace_path)),
                                "size": size
                            })
                    except:
                        pass
        except Exception as e:
            print(f"  ⚠️  Error analizando archivos: {e}")
        
        # Ordenar archivos más grandes
        file_stats["largest_files"].sort(key=lambda x: x["size"], reverse=True)
        file_stats["largest_files"] = file_stats["largest_files"][:20]
        
        return file_stats
    
    def _analyze_modules(self) -> Dict[str, Any]:
        """Analiza módulos del workspace"""
        modules = {}
        
        # Buscar módulos Python
        for py_file in self.workspace_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or ".pyc" in str(py_file):
                continue
            
            module_name = py_file.stem
            if module_name not in ["__init__"]:
                modules[module_name] = {
                    "path": str(py_file.relative_to(self.workspace_path)),
                    "type": "python",
                    "size": py_file.stat().st_size if py_file.exists() else 0
                }
        
        # Buscar módulos iOS
        for swift_file in self.workspace_path.rglob("*.swift"):
            module_name = swift_file.stem
            modules[module_name] = {
                "path": str(swift_file.relative_to(self.workspace_path)),
                "type": "ios",
                "size": swift_file.stat().st_size if swift_file.exists() else 0
            }
        
        return {
            "total_modules": len(modules),
            "modules": modules,
            "by_type": {
                "python": len([m for m in modules.values() if m["type"] == "python"]),
                "ios": len([m for m in modules.values() if m["type"] == "ios"])
            }
        }
    
    def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analiza dependencias del proyecto"""
        dependencies = {
            "python": {},
            "node": {},
            "ios": {}
        }
        
        # Python dependencies
        requirements_file = self.workspace_path / "requirements.txt"
        if requirements_file.exists():
            try:
                with open(requirements_file, "r") as f:
                    deps = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                    dependencies["python"]["requirements"] = deps
                    dependencies["python"]["count"] = len(deps)
            except Exception as e:
                print(f"  ⚠️  Error leyendo requirements.txt: {e}")
        
        # Node dependencies
        package_json = self.workspace_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, "r") as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                    dependencies["node"]["package.json"] = deps
                    dependencies["node"]["count"] = len(deps)
            except Exception as e:
                print(f"  ⚠️  Error leyendo package.json: {e}")
        
        # iOS dependencies (Podfile, Package.swift, etc.)
        podfile = self.workspace_path / "Podfile"
        if podfile.exists():
            dependencies["ios"]["podfile"] = True
        
        package_swift = self.workspace_path / "Package.swift"
        if package_swift.exists():
            dependencies["ios"]["swift_package"] = True
        
        return dependencies
    
    def _analyze_git_status(self) -> Dict[str, Any]:
        """Analiza estado Git del workspace"""
        git_info = {
            "is_git_repo": False,
            "current_branch": None,
            "branches": [],
            "remotes": {},
            "last_commit": None,
            "uncommitted_changes": False
        }
        
        try:
            # Verificar si es repo Git
            result = subprocess.run(
                ["git", "-C", str(self.workspace_path), "rev-parse", "--git-dir"],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                git_info["is_git_repo"] = True
                
                # Branch actual
                branch_result = subprocess.run(
                    ["git", "-C", str(self.workspace_path), "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if branch_result.returncode == 0:
                    git_info["current_branch"] = branch_result.stdout.strip()
                
                # Todas las branches
                branches_result = subprocess.run(
                    ["git", "-C", str(self.workspace_path), "branch", "-a"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if branches_result.returncode == 0:
                    git_info["branches"] = [b.strip() for b in branches_result.stdout.split("\n") if b.strip()]
                
                # Remotes
                remotes_result = subprocess.run(
                    ["git", "-C", str(self.workspace_path), "remote", "-v"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if remotes_result.returncode == 0:
                    for line in remotes_result.stdout.strip().split("\n"):
                        if line:
                            parts = line.split()
                            if len(parts) >= 2:
                                git_info["remotes"][parts[0]] = parts[1]
                
                # Cambios sin commitear
                status_result = subprocess.run(
                    ["git", "-C", str(self.workspace_path), "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if status_result.returncode == 0:
                    git_info["uncommitted_changes"] = len(status_result.stdout.strip()) > 0
        except Exception as e:
            print(f"  ⚠️  Error analizando Git: {e}")
        
        return git_info
    
    def _analyze_code_quality(self) -> Dict[str, Any]:
        """Analiza calidad de código"""
        quality = {
            "test_files": 0,
            "test_coverage": "unknown",
            "linting": "unknown",
            "complexity": "unknown"
        }
        
        # Buscar archivos de test
        test_patterns = ["test_", "_test", "Test", "spec"]
        for py_file in self.workspace_path.rglob("*.py"):
            if any(pattern in py_file.name for pattern in test_patterns):
                quality["test_files"] += 1
        
        return quality
    
    def _analyze_documentation(self) -> Dict[str, Any]:
        """Analiza documentación"""
        doc_files = list(self.workspace_path.rglob("*.md")) + list(self.workspace_path.rglob("*.txt"))
        doc_files = [f for f in doc_files if "node_modules" not in str(f) and ".git" not in str(f)]
        
        return {
            "total_docs": len(doc_files),
            "readme_exists": (self.workspace_path / "README.md").exists(),
            "docs_by_type": {
                "markdown": len([f for f in doc_files if f.suffix == ".md"]),
                "text": len([f for f in doc_files if f.suffix == ".txt"])
            }
        }
    
    def _analyze_configuration(self) -> Dict[str, Any]:
        """Analiza archivos de configuración"""
        config_files = []
        config_patterns = [".env", "config", "settings", ".json", ".yaml", ".yml", ".toml"]
        
        for file_path in self.workspace_path.rglob("*"):
            if file_path.is_file():
                name_lower = file_path.name.lower()
                if any(pattern in name_lower for pattern in config_patterns):
                    if "node_modules" not in str(file_path) and ".git" not in str(file_path):
                        config_files.append(str(file_path.relative_to(self.workspace_path)))
        
        return {
            "total_config_files": len(config_files),
            "config_files": config_files[:50]  # Limitar a 50
        }
    
    def _ai_analyze_workspace(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Usa IA para análisis avanzado del workspace"""
        if not self.model_integrator:
            return {}
        
        system_prompt = """Eres un experto en análisis de código y arquitectura de software.
Analiza el workspace proporcionado y genera insights sobre:
1. Fortalezas del proyecto
2. Áreas de mejora
3. Oportunidades de consolidación
4. Mejores prácticas que se pueden implementar

Responde en formato JSON con las claves: strengths (array), improvements (array), opportunities (array), best_practices (array)."""
        
        prompt = f"""Analiza el siguiente workspace:

{json.dumps(analysis, indent=2, default=str)[:3000]}

Proporciona un análisis estructurado con fortalezas, mejoras, oportunidades y mejores prácticas."""
        
        try:
            response = self.model_integrator.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=1000
            )
            
            if response and 'content' in response:
                content = response['content'].strip()
                # Intentar parsear JSON
                try:
                    return json.loads(content)
                except:
                    # Si no es JSON válido, extraer información
                    return {
                        "strengths": self._extract_list_from_text(content, "fortalezas"),
                        "improvements": self._extract_list_from_text(content, "mejoras"),
                        "opportunities": self._extract_list_from_text(content, "oportunidades"),
                        "best_practices": self._extract_list_from_text(content, "prácticas")
                    }
        except Exception as e:
            print(f"  ⚠️  Error en análisis IA: {e}")
        
        return {}
    
    def _extract_list_from_text(self, text: str, keyword: str) -> List[str]:
        """Extrae lista de items del texto"""
        items = []
        lines = text.split("\n")
        in_section = False
        
        for line in lines:
            if keyword.lower() in line.lower():
                in_section = True
                continue
            if in_section and (line.strip().startswith("-") or line.strip().startswith("•") or re.match(r'^\d+[\.\)]', line.strip())):
                item = line.strip().lstrip("-• ").lstrip("0123456789.) ")
                if item:
                    items.append(item)
            elif in_section and line.strip() == "":
                continue
            elif in_section:
                break
        
        return items[:10]  # Máximo 10 items
    
    def identify_cross_improvements(self) -> List[Dict[str, Any]]:
        """
        Identifica mejoras cruzadas desde distintos orígenes
        
        Returns:
            Lista de mejoras identificadas
        """
        print("\n" + "="*80)
        print("FASE 3: IDENTIFICACIÓN DE MEJORAS CRUZADAS")
        print("="*80)
        
        improvements = []
        
        # Comparar repositorios GitHub con workspace local
        if self.github_repos and self.local_workspace_analysis:
            print("\n🔍 Comparando repositorios GitHub con workspace local...")
            
            for repo in self.github_repos:
                repo_improvements = self._compare_repo_with_workspace(repo)
                improvements.extend(repo_improvements)
        
        # Usar IA para identificar mejoras adicionales
        if self.model_integrator:
            print("\n🤖 Usando IA para identificar mejoras adicionales...")
            ai_improvements = self._ai_identify_improvements()
            improvements.extend(ai_improvements)
        
        self.improvements_identified = improvements
        
        print(f"\n📊 Total mejoras identificadas: {len(improvements)}")
        
        return improvements
    
    def _compare_repo_with_workspace(self, repo: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compara un repositorio GitHub con el workspace local"""
        improvements = []
        
        # Analizar workflows
        if repo.get("workflows"):
            improvements.append({
                "type": "workflow",
                "source": repo["full_name"],
                "description": f"Repositorio tiene {len(repo['workflows'])} workflows de GitHub Actions que podrían ser útiles",
                "priority": "medium",
                "action": f"Revisar workflows de {repo['name']} para implementar CI/CD mejorado"
            })
        
        # Analizar branches
        if repo.get("branch_count", 0) > 1:
            improvements.append({
                "type": "branching_strategy",
                "source": repo["full_name"],
                "description": f"Repositorio tiene {repo['branch_count']} branches - estrategia de branching podría ser útil",
                "priority": "low",
                "action": f"Analizar estrategia de branching de {repo['name']}"
            })
        
        return improvements
    
    def _ai_identify_improvements(self) -> List[Dict[str, Any]]:
        """Usa IA para identificar mejoras"""
        if not self.model_integrator:
            return []
        
        system_prompt = """Eres un experto en mejoras de código y arquitectura.
Identifica mejoras específicas que se pueden implementar desde distintos repositorios o fuentes.
Responde en formato JSON con array de mejoras, cada una con: type, source, description, priority, action."""
        
        context = {
            "github_repos": len(self.github_repos),
            "workspace_analysis": self.local_workspace_analysis.get("modules", {}).get("total_modules", 0)
        }
        
        prompt = f"""Basado en el análisis de {context['github_repos']} repositorios iOS y un workspace con {context['workspace_analysis']} módulos,
identifica mejoras específicas que se pueden implementar.

Contexto:
- Repositorios iOS analizados: {context['github_repos']}
- Módulos en workspace: {context['workspace_analysis']}

Genera mejoras concretas y accionables."""
        
        try:
            response = self.model_integrator.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=800
            )
            
            if response and 'content' in response:
                content = response['content'].strip()
                try:
                    data = json.loads(content)
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and "improvements" in data:
                        return data["improvements"]
                except:
                    pass
        except Exception as e:
            print(f"  ⚠️  Error identificando mejoras con IA: {e}")
        
        return []
    
    def generate_consolidation_plan(self) -> Dict[str, Any]:
        """
        Genera plan de consolidación y mejora cruzada
        
        Returns:
            Plan completo de consolidación
        """
        print("\n" + "="*80)
        print("FASE 4: GENERACIÓN DE PLAN DE CONSOLIDACIÓN")
        print("="*80)
        
        # Usar Prompt Generator para crear prompt de plan
        if self.prompt_generator:
            plan_prompt = self.prompt_generator.generate_todo_prompt(
                goal="Consolidar repositorios iOS y workspace local en un nuevo repositorio evolucionado",
                pattern="context_aware",
                format="json",
                domain="desarrollo iOS y Python",
                timeline="4-6 semanas",
                resources="Equipo de desarrollo",
                constraints="Preservar historial Git, mantener compatibilidad",
                role="Arquitecto de Software",
                project_type="consolidación de repositorios",
                team_size="1-3 desarrolladores",
                detail_level="comprehensive"
            )
        else:
            plan_prompt = "Genera un plan de consolidación completo"
        
        # Generar plan usando IA
        plan = self._ai_generate_consolidation_plan(plan_prompt)
        
        # Estructurar plan
        structured_plan = {
            "goal": "Crear nuevo repositorio evolucionado consolidando repositorios iOS y workspace local",
            "phases": plan.get("phases", []),
            "improvements": self.improvements_identified,
            "architecture": plan.get("architecture", {}),
            "migration_strategy": plan.get("migration", {}),
            "timeline": plan.get("timeline", "4-6 semanas"),
            "risks": plan.get("risks", []),
            "success_criteria": plan.get("success_criteria", [])
        }
        
        self.consolidation_plan = structured_plan
        
        return structured_plan
    
    def _ai_generate_consolidation_plan(self, plan_prompt: str) -> Dict[str, Any]:
        """Genera plan de consolidación usando IA"""
        if not self.model_integrator:
            return {}
        
        system_prompt = """Eres un arquitecto de software experto en consolidación de repositorios.
Genera un plan detallado y estructurado para consolidar múltiples repositorios en uno evolucionado.
El plan debe incluir:
1. Fases de ejecución
2. Arquitectura propuesta
3. Estrategia de migración
4. Timeline
5. Riesgos y mitigaciones
6. Criterios de éxito

Responde en formato JSON con las claves: phases (array), architecture (object), migration (object), timeline (string), risks (array), success_criteria (array)."""
        
        context_summary = {
            "github_repos_count": len(self.github_repos),
            "workspace_modules": self.local_workspace_analysis.get("modules", {}).get("total_modules", 0),
            "improvements_count": len(self.improvements_identified)
        }
        
        prompt = f"""{plan_prompt}

Contexto del proyecto:
- Repositorios iOS en GitHub: {context_summary['github_repos_count']}
- Módulos en workspace local: {context_summary['workspace_modules']}
- Mejoras identificadas: {context_summary['improvements_count']}

Genera un plan completo de consolidación que:
1. Preserve el historial Git cuando sea posible
2. Integre las mejores características de cada repositorio
3. Implemente las mejoras identificadas
4. Cree una arquitectura evolucionada y escalable
5. Incluya estrategia de migración paso a paso"""
        
        try:
            response = self.model_integrator.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2000
            )
            
            if response and 'content' in response:
                content = response['content'].strip()
                try:
                    return json.loads(content)
                except:
                    # Crear plan estructurado desde texto
                    return self._parse_plan_from_text(content)
        except Exception as e:
            print(f"  ⚠️  Error generando plan con IA: {e}")
        
        return {}
    
    def _parse_plan_from_text(self, text: str) -> Dict[str, Any]:
        """Parsea plan desde texto si no es JSON válido"""
        return {
            "phases": [
                {
                    "phase": 1,
                    "name": "Análisis y Preparación",
                    "description": "Analizar todos los repositorios y workspace",
                    "duration": "1 semana"
                },
                {
                    "phase": 2,
                    "name": "Diseño de Arquitectura",
                    "description": "Diseñar arquitectura del nuevo repositorio",
                    "duration": "1 semana"
                },
                {
                    "phase": 3,
                    "name": "Migración y Consolidación",
                    "description": "Migrar código y consolidar componentes",
                    "duration": "2-3 semanas"
                },
                {
                    "phase": 4,
                    "name": "Implementación de Mejoras",
                    "description": "Implementar mejoras identificadas",
                    "duration": "1 semana"
                },
                {
                    "phase": 5,
                    "name": "Testing y Validación",
                    "description": "Probar y validar el nuevo repositorio",
                    "duration": "1 semana"
                }
            ],
            "architecture": {
                "structure": "Monorepo modular",
                "organization": "Por funcionalidad y tipo"
            },
            "migration": {
                "strategy": "Migración incremental",
                "preserve_history": True
            },
            "timeline": "4-6 semanas",
            "risks": ["Pérdida de historial Git", "Incompatibilidades", "Tiempo de migración"],
            "success_criteria": ["Código consolidado", "Historial preservado", "Mejoras implementadas"]
        }
    
    def generate_full_report(self) -> Dict[str, Any]:
        """
        Genera reporte completo de la investigación
        
        Returns:
            Reporte completo con todos los análisis
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "agent_prompt": self._generate_agent_prompt(),
            "github_ios_repos": {
                "summary": {},
                "repositories": []
            },
            "local_workspace": {},
            "improvements": [],
            "consolidation_plan": {},
            "recommendations": []
        }
        
        # Agregar datos si están disponibles
        if self.github_repos:
            report["github_ios_repos"] = {
                "summary": {
                    "total_repos": len(self.github_repos),
                    "total_branches": sum(r.get("branch_count", 0) for r in self.github_repos),
                    "total_workflows": sum(r.get("workflow_count", 0) for r in self.github_repos)
                },
                "repositories": self.github_repos
            }
        
        if self.local_workspace_analysis:
            report["local_workspace"] = self.local_workspace_analysis
        
        if self.improvements_identified:
            report["improvements"] = self.improvements_identified
        
        if self.consolidation_plan:
            report["consolidation_plan"] = self.consolidation_plan
        
        # Generar recomendaciones finales
        report["recommendations"] = self._generate_recommendations()
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Genera recomendaciones finales"""
        recommendations = []
        
        if self.github_repos:
            recommendations.append(f"Se encontraron {len(self.github_repos)} repositorios iOS - revisar para identificar componentes reutilizables")
        
        if self.local_workspace_analysis.get("modules", {}).get("total_modules", 0) > 0:
            recommendations.append("Workspace local tiene estructura modular - buena base para consolidación")
        
        if self.improvements_identified:
            recommendations.append(f"Se identificaron {len(self.improvements_identified)} mejoras - priorizar por impacto")
        
        recommendations.append("Crear nuevo repositorio evolucionado siguiendo el plan de consolidación generado")
        recommendations.append("Preservar historial Git usando git subtree o similar")
        recommendations.append("Implementar mejoras de forma incremental")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> Path:
        """Guarda el reporte en archivo"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"repo_research_report_{timestamp}.json"
        
        filepath = Path(filename)
        filepath.write_text(
            json.dumps(report, indent=2, default=str, ensure_ascii=False),
            encoding='utf-8'
        )
        
        return filepath


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Agente de investigación de repositorios iOS y análisis de workspace"
    )
    parser.add_argument(
        "--workspace",
        type=str,
        default=None,
        help="Ruta del workspace a analizar (default: directorio actual)"
    )
    parser.add_argument(
        "--github-owner",
        type=str,
        default="matiasportugau-ui",
        help="Propietario/organización de GitHub"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Archivo de salida para el reporte"
    )
    parser.add_argument(
        "--skip-github",
        action="store_true",
        help="Saltar investigación de GitHub"
    )
    parser.add_argument(
        "--skip-workspace",
        action="store_true",
        help="Saltar análisis de workspace"
    )
    
    args = parser.parse_args()
    
    # Crear agente
    agent = RepoResearchAgent(workspace_path=args.workspace)
    
    # Ejecutar investigación
    print("\n" + "="*80)
    print("AGENTE DE INVESTIGACIÓN DE REPOSITORIOS iOS")
    print("="*80)
    
    # Fase 1: Investigar GitHub
    if not args.skip_github:
        github_results = agent.research_github_ios_repos(owner=args.github_owner)
    else:
        github_results = {}
    
    # Fase 2: Evaluar workspace
    if not args.skip_workspace:
        workspace_results = agent.evaluate_local_workspace()
    else:
        workspace_results = {}
    
    # Fase 3: Identificar mejoras
    improvements = agent.identify_cross_improvements()
    
    # Fase 4: Generar plan
    consolidation_plan = agent.generate_consolidation_plan()
    
    # Generar reporte completo
    report = agent.generate_full_report()
    
    # Guardar reporte
    output_file = agent.save_report(report, filename=args.output)
    
    print("\n" + "="*80)
    print("✅ INVESTIGACIÓN COMPLETA")
    print("="*80)
    print(f"\n📄 Reporte guardado en: {output_file}")
    print(f"\n📊 Resumen:")
    print(f"  - Repositorios iOS encontrados: {len(agent.github_repos)}")
    print(f"  - Módulos en workspace: {agent.local_workspace_analysis.get('modules', {}).get('total_modules', 0)}")
    print(f"  - Mejoras identificadas: {len(agent.improvements_identified)}")
    print(f"  - Fases del plan: {len(consolidation_plan.get('phases', []))}")


if __name__ == "__main__":
    main()


