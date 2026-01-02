#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente de IA para Análisis y Mejora del Repositorio
====================================================

Agente especializado que:
1. Analiza el estado completo del repositorio usando prompts optimizados
2. Evalúa commits, branches, y estructura del repo
3. Sugiere mejores prácticas para:
   - Gestión de commits (conventional commits, mensajes, frecuencia)
   - Administración de branches (estrategias, naming, limpieza)
   - Almacenamiento del repo (backups, estructura, organización)
   - Almacenamiento local (organización de archivos, backups locales)
4. Genera plan de mejora accionable

Basado en:
- Prompt Engineering patterns del proyecto
- Mejores prácticas de Git y repositorios
- Análisis inteligente con IA
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

# Cargar credenciales automáticamente
try:
    from unified_credentials_manager import get_credential
    GITHUB_TOKEN = get_credential('GITHUB_TOKEN')
    if GITHUB_TOKEN:
        os.environ['GITHUB_TOKEN'] = GITHUB_TOKEN
except ImportError:
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

# Importar dependencias
try:
    from model_integrator import get_model_integrator
    MODEL_INTEGRATOR_AVAILABLE = True
except ImportError:
    MODEL_INTEGRATOR_AVAILABLE = False

try:
    from prompt_generator import PromptGenerator
    PROMPT_GENERATOR_AVAILABLE = True
except ImportError:
    PROMPT_GENERATOR_AVAILABLE = False

try:
    from github_analyzer import GitHubAnalyzer
    GITHUB_ANALYZER_AVAILABLE = True
except ImportError:
    GITHUB_ANALYZER_AVAILABLE = False


class RepoAnalysisImprovementAgent:
    """
    Agente de IA para análisis completo del repositorio y sugerencias de mejora
    """
    
    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.model_integrator = None
        self.prompt_generator = None
        self.github_analyzer = None
        
        # Inicializar componentes
        self._initialize_components()
        
        # Datos de análisis
        self.git_analysis = {}
        self.repo_structure = {}
        self.commit_analysis = {}
        self.branch_analysis = {}
        self.storage_analysis = {}
        self.improvements = []
        self.recommendations = {}
    
    def _initialize_components(self):
        """Inicializa componentes del sistema"""
        if MODEL_INTEGRATOR_AVAILABLE:
            try:
                self.model_integrator = get_model_integrator()
                print("✅ Model Integrator inicializado")
            except Exception as e:
                print(f"⚠️  Model Integrator no disponible: {e}")
        
        if PROMPT_GENERATOR_AVAILABLE:
            try:
                self.prompt_generator = PromptGenerator()
                print("✅ Prompt Generator inicializado")
            except Exception as e:
                print(f"⚠️  Prompt Generator no disponible: {e}")
        
        if GITHUB_ANALYZER_AVAILABLE:
            try:
                self.github_analyzer = GitHubAnalyzer()
                print("✅ GitHub Analyzer inicializado")
            except Exception as e:
                print(f"⚠️  Error inicializando GitHub Analyzer: {e}")
    
    def _generate_analysis_prompt(self) -> str:
        """Genera prompt optimizado para análisis del repo"""
        if not self.prompt_generator:
            return """Eres un experto en análisis de repositorios Git y mejores prácticas.
Analiza el repositorio y proporciona recomendaciones específicas."""
        
        return self.prompt_generator.generate_agent_prompt(
            role="Experto en Análisis de Repositorios y Mejores Prácticas Git",
            domain="Git, gestión de código, mejores prácticas de desarrollo",
            pattern="react",
            task="Analizar repositorio completo y sugerir mejoras en commits, branches, y almacenamiento",
            context="Análisis completo del estado del repositorio y estructura",
            tools=[
                "Análisis de commits y mensajes",
                "Análisis de branches y estrategias",
                "Análisis de estructura del repositorio",
                "Evaluación de almacenamiento local y remoto",
                "Generación de recomendaciones accionables"
            ],
            responsibilities=[
                "Analizar estado actual del repositorio Git",
                "Evaluar calidad de commits y mensajes",
                "Revisar estrategia de branches",
                "Analizar estructura y organización del código",
                "Evaluar sistemas de almacenamiento y backup",
                "Generar recomendaciones específicas y accionables"
            ],
            constraints=[
                "Seguir mejores prácticas de Git y desarrollo",
                "Considerar el contexto del proyecto actual",
                "Proporcionar recomendaciones prácticas y realizables",
                "Priorizar mejoras de alto impacto"
            ]
        )
    
    def analyze_git_repository(self) -> Dict[str, Any]:
        """Analiza el repositorio Git completo"""
        print("\n" + "="*80)
        print("FASE 1: ANÁLISIS DEL REPOSITORIO GIT")
        print("="*80)
        
        analysis = {
            "repo_path": str(self.repo_path),
            "is_git_repo": False,
            "branches": {},
            "commits": {},
            "remotes": {},
            "status": {},
            "issues": [],
            "statistics": {}
        }
        
        # Verificar si es repo Git
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "rev-parse", "--git-dir"],
                capture_output=True,
                timeout=5
            )
            analysis["is_git_repo"] = result.returncode == 0
        except:
            analysis["is_git_repo"] = False
        
        if not analysis["is_git_repo"]:
            print("⚠️  No es un repositorio Git")
            return analysis
        
        print("✅ Repositorio Git detectado")
        
        # Analizar branches
        print("\n🌿 Analizando branches...")
        analysis["branches"] = self._analyze_branches()
        
        # Analizar commits
        print("📝 Analizando commits...")
        analysis["commits"] = self._analyze_commits()
        
        # Analizar remotes
        print("🔗 Analizando remotes...")
        analysis["remotes"] = self._analyze_remotes()
        
        # Estado actual
        print("📊 Analizando estado actual...")
        analysis["status"] = self._analyze_git_status()
        
        # Estadísticas
        analysis["statistics"] = self._calculate_statistics(analysis)
        
        # Identificar issues
        analysis["issues"] = self._identify_git_issues(analysis)
        
        self.git_analysis = analysis
        
        return analysis
    
    def _analyze_branches(self) -> Dict[str, Any]:
        """Analiza todas las branches"""
        branches_info = {
            "local": [],
            "remote": [],
            "total": 0,
            "merged": [],
            "stale": [],
            "naming_issues": []
        }
        
        try:
            # Branches locales
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "branch"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                local_branches = [b.strip().lstrip('* ') for b in result.stdout.split('\n') if b.strip()]
                branches_info["local"] = local_branches
            
            # Branches remotas
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "branch", "-r"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                remote_branches = [b.strip() for b in result.stdout.split('\n') if b.strip() and 'HEAD' not in b]
                branches_info["remote"] = remote_branches
            
            branches_info["total"] = len(branches_info["local"]) + len(branches_info["remote"])
            
            # Verificar branches merged
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "branch", "--merged"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                merged = [b.strip().lstrip('* ') for b in result.stdout.split('\n') if b.strip()]
                branches_info["merged"] = [b for b in merged if b not in ['main', 'master', 'develop']]
            
            # Analizar naming
            for branch in branches_info["local"]:
                if not self._is_valid_branch_name(branch):
                    branches_info["naming_issues"].append(branch)
        
        except Exception as e:
            print(f"  ⚠️  Error analizando branches: {e}")
        
        return branches_info
    
    def _is_valid_branch_name(self, name: str) -> bool:
        """Verifica si el nombre de branch sigue mejores prácticas"""
        # Mejores prácticas: feature/, fix/, hotfix/, release/, etc.
        valid_patterns = [
            r'^(main|master|develop|dev)$',
            r'^(feature|fix|hotfix|release|bugfix)/.+',
            r'^[a-z0-9-]+$'
        ]
        return any(re.match(pattern, name) for pattern in valid_patterns)
    
    def _analyze_commits(self, limit: int = 100) -> Dict[str, Any]:
        """Analiza commits recientes"""
        commits_info = {
            "total": 0,
            "recent": [],
            "message_quality": {},
            "conventional_commits": 0,
            "issues": []
        }
        
        try:
            # Obtener commits recientes
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "log", 
                 "--pretty=format:%H|%an|%ae|%ad|%s", 
                 "--date=iso", "-n", str(limit)],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                commits = []
                for line in result.stdout.strip().split('\n'):
                    if not line:
                        continue
                    parts = line.split('|', 4)
                    if len(parts) >= 5:
                        commits.append({
                            "hash": parts[0][:8],
                            "author": parts[1],
                            "email": parts[2],
                            "date": parts[3],
                            "message": parts[4]
                        })
                
                commits_info["recent"] = commits
                commits_info["total"] = len(commits)
                
                # Analizar calidad de mensajes
                conventional_count = 0
                quality_issues = []
                
                for commit in commits:
                    msg = commit["message"]
                    # Verificar conventional commits
                    if re.match(r'^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+', msg):
                        conventional_count += 1
                    elif len(msg) < 10:
                        quality_issues.append(f"Commit {commit['hash']}: mensaje muy corto")
                    elif len(msg) > 100:
                        quality_issues.append(f"Commit {commit['hash']}: mensaje muy largo")
                    elif not msg[0].isupper():
                        quality_issues.append(f"Commit {commit['hash']}: no empieza con mayúscula")
                
                commits_info["conventional_commits"] = conventional_count
                commits_info["message_quality"] = {
                    "conventional_percentage": (conventional_count / len(commits) * 100) if commits else 0,
                    "issues": quality_issues[:10]  # Limitar a 10
                }
        
        except Exception as e:
            print(f"  ⚠️  Error analizando commits: {e}")
        
        return commits_info
    
    def _analyze_remotes(self) -> Dict[str, Any]:
        """Analiza remotes configurados"""
        remotes_info = {
            "remotes": {},
            "upstream_configured": False,
            "issues": []
        }
        
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "remote", "-v"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if not line:
                        continue
                    parts = line.split()
                    if len(parts) >= 2:
                        remote_name = parts[0]
                        remote_url = parts[1]
                        if remote_name not in remotes_info["remotes"]:
                            remotes_info["remotes"][remote_name] = remote_url
                        if remote_name == "upstream":
                            remotes_info["upstream_configured"] = True
        except Exception as e:
            print(f"  ⚠️  Error analizando remotes: {e}")
        
        return remotes_info
    
    def _analyze_git_status(self) -> Dict[str, Any]:
        """Analiza estado actual de Git"""
        status_info = {
            "clean": False,
            "unstaged_changes": 0,
            "staged_changes": 0,
            "untracked_files": 0,
            "ahead": 0,
            "behind": 0
        }
        
        try:
            # Estado general
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                status_info["clean"] = len([l for l in lines if l.strip()]) == 0
                
                for line in lines:
                    if line.startswith('??'):
                        status_info["untracked_files"] += 1
                    elif line[0] in ['A', 'M', 'D']:
                        status_info["staged_changes"] += 1
                    elif line[1] in ['M', 'D']:
                        status_info["unstaged_changes"] += 1
            
            # Verificar ahead/behind
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "status", "-sb"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Buscar patrones como "ahead 2, behind 1"
                ahead_match = re.search(r'ahead (\d+)', result.stdout)
                behind_match = re.search(r'behind (\d+)', result.stdout)
                if ahead_match:
                    status_info["ahead"] = int(ahead_match.group(1))
                if behind_match:
                    status_info["behind"] = int(behind_match.group(1))
        
        except Exception as e:
            print(f"  ⚠️  Error analizando status: {e}")
        
        return status_info
    
    def _calculate_statistics(self, analysis: Dict) -> Dict[str, Any]:
        """Calcula estadísticas del repositorio"""
        stats = {
            "total_branches": analysis["branches"].get("total", 0),
            "total_commits": analysis["commits"].get("total", 0),
            "conventional_commits_pct": analysis["commits"].get("message_quality", {}).get("conventional_percentage", 0),
            "merged_branches": len(analysis["branches"].get("merged", [])),
            "stale_branches": len(analysis["branches"].get("stale", [])),
            "naming_issues": len(analysis["branches"].get("naming_issues", []))
        }
        return stats
    
    def _identify_git_issues(self, analysis: Dict) -> List[str]:
        """Identifica problemas en el repositorio"""
        issues = []
        
        # Branches merged que deberían eliminarse
        if analysis["branches"].get("merged"):
            issues.append(f"{len(analysis['branches']['merged'])} branches merged que deberían eliminarse")
        
        # Naming issues
        if analysis["branches"].get("naming_issues"):
            issues.append(f"{len(analysis['branches']['naming_issues'])} branches con nombres que no siguen convenciones")
        
        # Commits no convencionales
        conventional_pct = analysis["commits"].get("message_quality", {}).get("conventional_percentage", 0)
        if conventional_pct < 50:
            issues.append(f"Solo {conventional_pct:.1f}% de commits siguen conventional commits")
        
        # Estado no limpio
        if not analysis["status"].get("clean"):
            issues.append("Working directory tiene cambios sin commitear")
        
        # Sin upstream
        if not analysis["remotes"].get("upstream_configured"):
            issues.append("No hay remote 'upstream' configurado")
        
        return issues
    
    def analyze_repo_structure(self) -> Dict[str, Any]:
        """Analiza estructura del repositorio"""
        print("\n" + "="*80)
        print("FASE 2: ANÁLISIS DE ESTRUCTURA DEL REPOSITORIO")
        print("="*80)
        
        structure = {
            "files_by_type": defaultdict(int),
            "directories": [],
            "large_files": [],
            "duplicate_files": [],
            "organization_score": 0
        }
        
        try:
            for item in self.repo_path.rglob("*"):
                if item.is_file():
                    # Por tipo
                    ext = item.suffix.lower()
                    structure["files_by_type"][ext] += 1
                    
                    # Archivos grandes
                    try:
                        size = item.stat().st_size
                        if size > 1_000_000:  # > 1MB
                            structure["large_files"].append({
                                "path": str(item.relative_to(self.repo_path)),
                                "size_mb": size / 1_000_000
                            })
                    except:
                        pass
                
                elif item.is_dir():
                    if item.name not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']:
                        structure["directories"].append(str(item.relative_to(self.repo_path)))
            
            # Ordenar archivos grandes
            structure["large_files"].sort(key=lambda x: x["size_mb"], reverse=True)
            structure["large_files"] = structure["large_files"][:20]
        except Exception as e:
            print(f"  ⚠️  Error analizando estructura: {e}")
        
        self.repo_structure = structure
        
        return structure
    
    def analyze_storage(self) -> Dict[str, Any]:
        """Analiza sistemas de almacenamiento y backup"""
        print("\n" + "="*80)
        print("FASE 3: ANÁLISIS DE ALMACENAMIENTO Y BACKUPS")
        print("="*80)
        
        storage = {
            "local_backups": [],
            "remote_backups": [],
            "backup_frequency": "unknown",
            "backup_locations": [],
            "storage_issues": []
        }
        
        # Buscar carpetas de backup locales
        backup_paths = [
            Path.home() / "Desktop" / "cursor_workspace_backups",
            Path.home() / "Desktop" / "cursor_workspace_backup_20251201_175806",
            self.repo_path / "backups",
            self.repo_path / "backup",
            self.repo_path.parent / "backups"
        ]
        
        for backup_path in backup_paths:
            if backup_path.exists() and backup_path.is_dir():
                try:
                    files = list(backup_path.rglob("*"))
                    storage["local_backups"].append({
                        "path": str(backup_path),
                        "files_count": len([f for f in files if f.is_file()]),
                        "size_mb": sum(f.stat().st_size for f in files if f.is_file()) / 1_000_000
                    })
                    storage["backup_locations"].append(str(backup_path))
                except:
                    pass
        
        # Verificar remotes para backups remotos
        if self.git_analysis.get("remotes", {}).get("remotes"):
            storage["remote_backups"] = list(self.git_analysis["remotes"]["remotes"].keys())
        
        self.storage_analysis = storage
        
        return storage
    
    def generate_improvements(self) -> List[Dict[str, Any]]:
        """Genera recomendaciones de mejora usando IA"""
        print("\n" + "="*80)
        print("FASE 4: GENERACIÓN DE MEJORAS CON IA")
        print("="*80)
        
        if not self.model_integrator:
            print("⚠️  Model Integrator no disponible - usando recomendaciones básicas")
            return self._generate_basic_improvements()
        
        # Generar prompt para IA
        system_prompt = """Eres un experto en mejores prácticas de Git, gestión de repositorios y almacenamiento.
Analiza el estado del repositorio y genera recomendaciones específicas y accionables.

Responde en formato JSON con:
{
  "commit_recommendations": [
    {
      "priority": "high|medium|low",
      "category": "conventional_commits|message_quality|frequency",
      "issue": "descripción del problema",
      "recommendation": "recomendación específica",
      "action": "acción concreta a tomar",
      "example": "ejemplo de implementación"
    }
  ],
  "branch_recommendations": [...],
  "storage_recommendations": [...],
  "general_recommendations": [...]
}"""
        
        context = {
            "git_analysis": self.git_analysis,
            "repo_structure": self.repo_structure,
            "storage_analysis": self.storage_analysis
        }
        
        prompt = f"""Analiza el siguiente repositorio y genera recomendaciones:

{json.dumps(context, indent=2, default=str)[:4000]}

Genera recomendaciones específicas para:
1. Mejora de commits (conventional commits, mensajes, frecuencia)
2. Gestión de branches (naming, limpieza, estrategia)
3. Almacenamiento y backups (local, remoto, frecuencia)
4. Organización del repositorio"""
        
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
                    improvements = json.loads(content)
                    return self._format_improvements(improvements)
                except:
                    return self._parse_improvements_from_text(content)
        except Exception as e:
            print(f"  ⚠️  Error generando mejoras con IA: {e}")
        
        return self._generate_basic_improvements()
    
    def _format_improvements(self, improvements: Dict) -> List[Dict[str, Any]]:
        """Formatea mejoras desde JSON"""
        formatted = []
        
        for category in ['commit_recommendations', 'branch_recommendations', 
                        'storage_recommendations', 'general_recommendations']:
            if category in improvements:
                for rec in improvements[category]:
                    formatted.append({
                        "category": category.replace('_recommendations', ''),
                        "priority": rec.get("priority", "medium"),
                        "issue": rec.get("issue", ""),
                        "recommendation": rec.get("recommendation", ""),
                        "action": rec.get("action", ""),
                        "example": rec.get("example", "")
                    })
        
        return formatted
    
    def _parse_improvements_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Parsea mejoras desde texto"""
        improvements = []
        # Implementación básica de parsing
        return improvements
    
    def _generate_basic_improvements(self) -> List[Dict[str, Any]]:
        """Genera mejoras básicas sin IA"""
        improvements = []
        
        # Mejoras de commits
        if self.git_analysis.get("commits", {}).get("message_quality", {}).get("conventional_percentage", 100) < 50:
            improvements.append({
                "category": "commits",
                "priority": "high",
                "issue": "Bajo porcentaje de conventional commits",
                "recommendation": "Usar conventional commits (feat:, fix:, docs:, etc.)",
                "action": "Configurar commitizen o similar, documentar convenciones",
                "example": "feat: agregar sistema de autenticación"
            })
        
        # Mejoras de branches
        if self.git_analysis.get("branches", {}).get("merged"):
            improvements.append({
                "category": "branches",
                "priority": "medium",
                "issue": f"{len(self.git_analysis['branches']['merged'])} branches merged sin eliminar",
                "recommendation": "Eliminar branches merged que ya no se usan",
                "action": "git branch -d <branch-name> para branches locales",
                "example": "git branch -d feature/old-feature"
            })
        
        # Mejoras de almacenamiento
        if not self.storage_analysis.get("local_backups"):
            improvements.append({
                "category": "storage",
                "priority": "high",
                "issue": "No se detectaron backups locales organizados",
                "recommendation": "Implementar sistema de backups automáticos",
                "action": "Configurar script de backup periódico",
                "example": "Usar auto_backup_agent.py con frecuencia configurada"
            })
        
        return improvements
    
    def generate_storage_recommendations(self) -> Dict[str, Any]:
        """Genera recomendaciones específicas de almacenamiento"""
        recommendations = {
            "local_storage": {
                "current": self.storage_analysis.get("backup_locations", []),
                "recommendations": []
            },
            "git_storage": {
                "recommendations": []
            },
            "backup_strategy": {
                "recommendations": []
            }
        }
        
        # Recomendaciones de almacenamiento local
        if not self.storage_analysis.get("local_backups"):
            recommendations["local_storage"]["recommendations"].append({
                "priority": "high",
                "recommendation": "Crear estructura de backups local organizada",
                "structure": {
                    "backups/": {
                        "daily/": "Backups diarios",
                        "weekly/": "Backups semanales",
                        "monthly/": "Backups mensuales"
                    }
                },
                "action": "Crear directorio ~/backups/chatbot-2311/ con subdirectorios por frecuencia"
            })
        
        # Recomendaciones de Git
        recommendations["git_storage"]["recommendations"].append({
            "priority": "high",
            "recommendation": "Configurar múltiples remotes para redundancia",
            "action": "git remote add backup <backup-repo-url>",
            "benefit": "Backup automático en cada push"
        })
        
        # Estrategia de backup
        recommendations["backup_strategy"]["recommendations"] = [
            {
                "type": "local",
                "frequency": "daily",
                "tool": "auto_backup_agent.py",
                "location": "~/backups/chatbot-2311/daily/"
            },
            {
                "type": "git_remote",
                "frequency": "on_push",
                "tool": "git push",
                "location": "GitHub + backup remote"
            },
            {
                "type": "snapshot",
                "frequency": "weekly",
                "tool": "git bundle",
                "location": "~/backups/chatbot-2311/weekly/"
            }
        ]
        
        self.recommendations = recommendations
        
        return recommendations
    
    def generate_full_report(self) -> Dict[str, Any]:
        """Genera reporte completo"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "repo_path": str(self.repo_path),
            "git_analysis": self.git_analysis,
            "repo_structure": self.repo_structure,
            "storage_analysis": self.storage_analysis,
            "improvements": self.improvements,
            "recommendations": self.recommendations,
            "action_plan": self._generate_action_plan()
        }
        
        return report
    
    def _generate_action_plan(self) -> List[Dict[str, Any]]:
        """Genera plan de acción priorizado"""
        plan = []
        
        # Agrupar mejoras por prioridad
        high_priority = [i for i in self.improvements if i.get("priority") == "high"]
        medium_priority = [i for i in self.improvements if i.get("priority") == "medium"]
        low_priority = [i for i in self.improvements if i.get("priority") == "low"]
        
        if high_priority:
            plan.append({
                "phase": "Inmediato (Esta semana)",
                "items": high_priority
            })
        
        if medium_priority:
            plan.append({
                "phase": "Corto plazo (Este mes)",
                "items": medium_priority
            })
        
        if low_priority:
            plan.append({
                "phase": "Largo plazo (Este trimestre)",
                "items": low_priority
            })
        
        return plan
    
    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> Path:
        """Guarda el reporte"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"repo_analysis_report_{timestamp}.json"
        
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
        description="Agente de IA para Análisis y Mejora del Repositorio"
    )
    parser.add_argument(
        "--repo-path",
        type=str,
        default=None,
        help="Ruta del repositorio (default: directorio actual)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Archivo de salida para el reporte"
    )
    
    args = parser.parse_args()
    
    # Crear agente
    agent = RepoAnalysisImprovementAgent(repo_path=args.repo_path)
    
    print("\n" + "="*80)
    print("AGENTE DE IA PARA ANÁLISIS Y MEJORA DEL REPOSITORIO")
    print("="*80)
    
    # Ejecutar análisis completo
    git_analysis = agent.analyze_git_repository()
    repo_structure = agent.analyze_repo_structure()
    storage_analysis = agent.analyze_storage()
    improvements = agent.generate_improvements()
    storage_recommendations = agent.generate_storage_recommendations()
    
    # Generar reporte
    report = agent.generate_full_report()
    
    # Guardar reporte
    output_file = agent.save_report(report, filename=args.output)
    
    # Mostrar resumen
    print("\n" + "="*80)
    print("RESUMEN DEL ANÁLISIS")
    print("="*80)
    print(f"\n📊 Estadísticas:")
    stats = git_analysis.get("statistics", {})
    print(f"  • Branches: {stats.get('total_branches', 0)}")
    print(f"  • Commits: {stats.get('total_commits', 0)}")
    print(f"  • Conventional commits: {stats.get('conventional_commits_pct', 0):.1f}%")
    print(f"  • Issues detectados: {len(git_analysis.get('issues', []))}")
    
    print(f"\n💡 Mejoras identificadas: {len(improvements)}")
    print(f"  • Alta prioridad: {len([i for i in improvements if i.get('priority') == 'high'])}")
    print(f"  • Media prioridad: {len([i for i in improvements if i.get('priority') == 'medium'])}")
    
    print(f"\n📄 Reporte completo guardado en: {output_file}")
    print("="*80)


if __name__ == "__main__":
    main()

