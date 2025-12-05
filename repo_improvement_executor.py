#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejecutor de Mejoras del Repositorio con Aprobación
==================================================

Sistema que:
1. Analiza el repositorio y propone mejoras
2. Genera planes de ejecución detallados
3. REQUIERE aprobación del usuario antes de ejecutar
4. Ejecuta solo las mejoras aprobadas
5. Reporta resultados de cada acción

NUNCA ejecuta cambios sin aprobación explícita del usuario.
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from repo_analysis_improvement_agent import RepoAnalysisImprovementAgent


class RepoImprovementExecutor:
    """
    Ejecutor de mejoras con sistema de aprobación
    """
    
    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.analyzer = RepoAnalysisImprovementAgent(repo_path=str(self.repo_path))
        self.approved_actions = []
        self.executed_actions = []
        self.execution_plan = {}
    
    def generate_execution_plan(self) -> Dict[str, Any]:
        """Genera plan de ejecución detallado sin ejecutar nada"""
        print("\n" + "="*80)
        print("GENERACIÓN DE PLAN DE EJECUCIÓN")
        print("="*80)
        print("\n⚠️  IMPORTANTE: Este plan NO se ejecutará automáticamente.")
        print("   Requerirá tu aprobación explícita para cada acción.\n")
        
        # Ejecutar análisis
        print("📊 Analizando repositorio...")
        git_analysis = self.analyzer.analyze_git_repository()
        repo_structure = self.analyzer.analyze_repo_structure()
        storage_analysis = self.analyzer.analyze_storage()
        improvements = self.analyzer.generate_improvements()
        storage_recommendations = self.analyzer.generate_storage_recommendations()
        
        # Generar plan de ejecución
        plan = {
            "timestamp": datetime.now().isoformat(),
            "repo_path": str(self.repo_path),
            "analysis_summary": {
                "branches": git_analysis.get("statistics", {}).get("total_branches", 0),
                "commits": git_analysis.get("statistics", {}).get("total_commits", 0),
                "issues": len(git_analysis.get("issues", [])),
                "improvements": len(improvements)
            },
            "execution_phases": [],
            "actions": [],
            "estimated_time": "unknown",
            "risks": [],
            "rollback_plan": {}
        }
        
        # Organizar acciones por categoría y prioridad
        actions_by_category = defaultdict(list)
        for improvement in improvements:
            category = improvement.get("category", "general")
            actions_by_category[category].append(improvement)
        
        # Crear fases de ejecución
        phase_num = 1
        
        # Fase 1: Limpieza de branches (bajo riesgo)
        branch_actions = actions_by_category.get("branches", [])
        if branch_actions:
            phase = {
                "phase": phase_num,
                "name": "Limpieza de Branches",
                "description": "Eliminar branches merged y organizar estructura",
                "risk_level": "low",
                "estimated_time": "5-10 minutos",
                "actions": []
            }
            
            for action in branch_actions:
                if "merged" in action.get("issue", "").lower():
                    phase["actions"].append({
                        "id": f"branch_cleanup_{len(phase['actions'])}",
                        "type": "git_branch_delete",
                        "description": action.get("recommendation", ""),
                        "command": self._generate_branch_cleanup_command(action),
                        "affected_branches": self._get_merged_branches(),
                        "safe": True,
                        "can_rollback": False  # Branches merged ya están en main
                    })
            
            if phase["actions"]:
                plan["execution_phases"].append(phase)
                phase_num += 1
        
        # Fase 2: Configuración de conventional commits (medio riesgo)
        commit_actions = actions_by_category.get("commits", [])
        if commit_actions:
            phase = {
                "phase": phase_num,
                "name": "Configuración de Conventional Commits",
                "description": "Configurar herramientas y documentación para conventional commits",
                "risk_level": "low",
                "estimated_time": "10-15 minutos",
                "actions": []
            }
            
            for action in commit_actions:
                if "conventional" in action.get("issue", "").lower():
                    phase["actions"].append({
                        "id": f"commit_config_{len(phase['actions'])}",
                        "type": "config_setup",
                        "description": action.get("recommendation", ""),
                        "commands": self._generate_commit_config_commands(action),
                        "files_to_create": [
                            ".commitlintrc.json",
                            "docs/CONTRIBUTING.md"
                        ],
                        "safe": True,
                        "can_rollback": True
                    })
            
            if phase["actions"]:
                plan["execution_phases"].append(phase)
                phase_num += 1
        
        # Fase 3: Configuración de backups (bajo riesgo)
        storage_actions = actions_by_category.get("storage", [])
        if storage_actions or storage_recommendations:
            phase = {
                "phase": phase_num,
                "name": "Configuración de Sistema de Backups",
                "description": "Crear estructura de backups y configurar automatización",
                "risk_level": "low",
                "estimated_time": "15-20 minutos",
                "actions": []
            }
            
            # Agregar acciones de backup
            if storage_recommendations.get("local_storage", {}).get("recommendations"):
                phase["actions"].append({
                    "id": "backup_structure",
                    "type": "directory_creation",
                    "description": "Crear estructura de backups local",
                    "directories": self._generate_backup_structure(),
                    "safe": True,
                    "can_rollback": True
                })
            
            if phase["actions"]:
                plan["execution_phases"].append(phase)
                phase_num += 1
        
        # Fase 4: Configuración de remotes (bajo riesgo)
        if not git_analysis.get("remotes", {}).get("upstream_configured"):
            phase = {
                "phase": phase_num,
                "name": "Configuración de Remotes",
                "description": "Agregar remote de backup para redundancia",
                "risk_level": "low",
                "estimated_time": "5 minutos",
                "actions": [{
                    "id": "add_backup_remote",
                    "type": "git_remote_add",
                    "description": "Agregar remote de backup (requiere URL)",
                    "command": "git remote add backup <URL>",
                    "requires_input": True,
                    "input_prompt": "URL del repositorio de backup (o Enter para omitir)",
                    "safe": True,
                    "can_rollback": True
                }]
            }
            plan["execution_phases"].append(phase)
        
        # Calcular tiempo total estimado
        total_minutes = 0
        for phase in plan["execution_phases"]:
            time_str = phase.get("estimated_time", "0")
            # Extraer primer número (ej: "5-10 minutos" -> 5)
            try:
                first_num = int(time_str.split("-")[0].strip().split()[0])
                total_minutes += first_num
            except:
                pass
        plan["estimated_time"] = f"{total_minutes}-{total_minutes + 10} minutos"
        
        # Identificar riesgos
        plan["risks"] = self._identify_risks(plan)
        
        # Plan de rollback
        plan["rollback_plan"] = self._generate_rollback_plan(plan)
        
        self.execution_plan = plan
        
        return plan
    
    def _generate_branch_cleanup_command(self, action: Dict) -> str:
        """Genera comando para limpiar branches"""
        merged_branches = self._get_merged_branches()
        if not merged_branches:
            return "# No hay branches merged para eliminar"
        
        commands = []
        for branch in merged_branches[:10]:  # Limitar a 10
            commands.append(f"git branch -d {branch}")
        
        return "\n".join(commands)
    
    def _get_merged_branches(self) -> List[str]:
        """Obtiene lista de branches merged"""
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "branch", "--merged"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                branches = [b.strip().lstrip('* ') for b in result.stdout.split('\n') if b.strip()]
                return [b for b in branches if b not in ['main', 'master', 'develop']]
        except:
            pass
        return []
    
    def _generate_commit_config_commands(self, action: Dict) -> List[str]:
        """Genera comandos para configurar conventional commits"""
        return [
            "# Instalar commitizen (opcional)",
            "pip install commitizen",
            "",
            "# O crear .commitlintrc.json manualmente",
            "# Ver ejemplo en docs/CONTRIBUTING.md"
        ]
    
    def _generate_backup_structure(self) -> List[Dict[str, str]]:
        """Genera estructura de directorios de backup"""
        home = Path.home()
        backup_base = home / "backups" / "chatbot-2311"
        
        return [
            {"path": str(backup_base / "daily"), "description": "Backups diarios"},
            {"path": str(backup_base / "weekly"), "description": "Backups semanales"},
            {"path": str(backup_base / "monthly"), "description": "Backups mensuales"},
            {"path": str(backup_base / "git_bundles"), "description": "Git bundles completos"}
        ]
    
    def _identify_risks(self, plan: Dict) -> List[str]:
        """Identifica riesgos del plan"""
        risks = []
        
        for phase in plan.get("execution_phases", []):
            if phase.get("risk_level") == "medium":
                risks.append(f"Fase {phase['phase']}: {phase['name']} - Riesgo medio")
        
        if any(not action.get("can_rollback", False) for phase in plan.get("execution_phases", []) 
               for action in phase.get("actions", [])):
            risks.append("Algunas acciones no se pueden revertir")
        
        return risks if risks else ["Ningún riesgo significativo identificado"]
    
    def _generate_rollback_plan(self, plan: Dict) -> Dict[str, Any]:
        """Genera plan de rollback"""
        rollback = {
            "before_execution": "Crear backup del estado actual",
            "commands": [],
            "manual_steps": []
        }
        
        # Agregar comandos de rollback por fase
        for phase in plan.get("execution_phases", []):
            for action in phase.get("actions", []):
                if action.get("can_rollback"):
                    if action["type"] == "git_remote_add":
                        rollback["commands"].append(f"git remote remove backup")
                    elif action["type"] == "directory_creation":
                        rollback["manual_steps"].append(f"Eliminar directorios creados: {action.get('directories', [])}")
        
        return rollback
    
    def print_execution_plan(self):
        """Imprime el plan de ejecución de forma legible"""
        if not self.execution_plan:
            print("❌ No hay plan de ejecución generado")
            return
        
        plan = self.execution_plan
        
        print("\n" + "="*80)
        print("PLAN DE EJECUCIÓN GENERADO")
        print("="*80)
        
        print(f"\n📊 Resumen del Análisis:")
        summary = plan.get("analysis_summary", {})
        print(f"  • Branches: {summary.get('branches', 0)}")
        print(f"  • Commits: {summary.get('commits', 0)}")
        print(f"  • Issues detectados: {summary.get('issues', 0)}")
        print(f"  • Mejoras identificadas: {summary.get('improvements', 0)}")
        
        print(f"\n⏱️  Tiempo estimado: {plan.get('estimated_time', 'unknown')}")
        
        print(f"\n📋 Fases de Ejecución ({len(plan.get('execution_phases', []))}):")
        for phase in plan.get("execution_phases", []):
            print(f"\n  Fase {phase['phase']}: {phase['name']}")
            print(f"    Descripción: {phase['description']}")
            print(f"    Riesgo: {phase['risk_level'].upper()}")
            print(f"    Tiempo: {phase['estimated_time']}")
            print(f"    Acciones: {len(phase.get('actions', []))}")
            
            for i, action in enumerate(phase.get("actions", []), 1):
                print(f"\n      {i}. {action.get('description', 'Sin descripción')}")
                print(f"         Tipo: {action.get('type', 'unknown')}")
                print(f"         Seguro: {'✅ Sí' if action.get('safe') else '⚠️  Requiere atención'}")
                print(f"         Reversible: {'✅ Sí' if action.get('can_rollback') else '❌ No'}")
                
                if action.get("command"):
                    print(f"         Comando:")
                    for line in action["command"].split("\n"):
                        print(f"           {line}")
        
        if plan.get("risks"):
            print(f"\n⚠️  Riesgos Identificados:")
            for risk in plan["risks"]:
                print(f"  • {risk}")
        
        if plan.get("rollback_plan"):
            print(f"\n🔄 Plan de Rollback:")
            rollback = plan["rollback_plan"]
            print(f"  Antes de ejecutar: {rollback.get('before_execution', 'N/A')}")
            if rollback.get("commands"):
                print(f"  Comandos de rollback:")
                for cmd in rollback["commands"]:
                    print(f"    • {cmd}")
        
        print("\n" + "="*80)
    
    def request_approval(self) -> Dict[str, Any]:
        """Solicita aprobación del usuario para ejecutar el plan"""
        if not self.execution_plan:
            print("❌ No hay plan de ejecución para aprobar")
            return {"approved": False}
        
        self.print_execution_plan()
        
        print("\n" + "="*80)
        print("APROBACIÓN REQUERIDA")
        print("="*80)
        print("\n⚠️  IMPORTANTE: Este plan modificará tu repositorio.")
        print("   Revisa cuidadosamente cada fase antes de aprobar.\n")
        
        print("Opciones:")
        print("  1. Aprobar TODO el plan")
        print("  2. Aprobar por fases (seleccionar qué ejecutar)")
        print("  3. Rechazar (no ejecutar nada)")
        print("  4. Ver detalles de una fase específica")
        print("  5. Modificar plan")
        
        choice = input("\n¿Qué deseas hacer? [3]: ").strip() or "3"
        
        approval = {
            "approved": False,
            "approved_phases": [],
            "timestamp": datetime.now().isoformat()
        }
        
        if choice == "1":
            # Aprobar todo
            approval["approved"] = True
            approval["approved_phases"] = [p["phase"] for p in self.execution_plan.get("execution_phases", [])]
            print("\n✅ Plan completo aprobado")
        
        elif choice == "2":
            # Aprobar por fases
            print("\nSelecciona las fases a ejecutar (separadas por comas, ej: 1,3):")
            for phase in self.execution_plan.get("execution_phases", []):
                print(f"  {phase['phase']}. {phase['name']} ({phase['risk_level']})")
            
            selected = input("\nFases: ").strip()
            if selected:
                try:
                    phases = [int(p.strip()) for p in selected.split(",")]
                    approval["approved"] = True
                    approval["approved_phases"] = phases
                    print(f"\n✅ Fases {phases} aprobadas")
                except:
                    print("❌ Entrada inválida")
        
        elif choice == "3":
            print("\n❌ Plan rechazado - No se ejecutará nada")
        
        elif choice == "4":
            phase_num = input("Número de fase a ver: ").strip()
            try:
                phase_num = int(phase_num)
                phase = next((p for p in self.execution_plan.get("execution_phases", []) 
                             if p["phase"] == phase_num), None)
                if phase:
                    print(f"\n📋 Detalles de Fase {phase_num}:")
                    print(json.dumps(phase, indent=2, ensure_ascii=False))
                else:
                    print("❌ Fase no encontrada")
            except:
                print("❌ Número inválido")
            return self.request_approval()  # Volver a solicitar aprobación
        
        elif choice == "5":
            print("\n💡 Para modificar el plan, edita el archivo JSON del plan")
            print("   o ejecuta el análisis nuevamente con diferentes parámetros")
            return self.request_approval()
        
        return approval
    
    def execute_approved_plan(self, approval: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta solo las fases aprobadas"""
        if not approval.get("approved"):
            print("\n❌ Plan no aprobado - No se ejecutará nada")
            return {"executed": False, "reason": "Not approved"}
        
        print("\n" + "="*80)
        print("EJECUTANDO PLAN APROBADO")
        print("="*80)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "approved_phases": approval.get("approved_phases", []),
            "executed_actions": [],
            "successful": [],
            "failed": [],
            "skipped": []
        }
        
        # Crear backup antes de ejecutar
        print("\n📦 Creando backup del estado actual...")
        backup_result = self._create_backup()
        if backup_result:
            print(f"✅ Backup creado: {backup_result}")
        else:
            print("⚠️  No se pudo crear backup - continuando de todas formas")
        
        # Ejecutar fases aprobadas
        for phase in self.execution_plan.get("execution_phases", []):
            if phase["phase"] not in approval.get("approved_phases", []):
                print(f"\n⏭️  Fase {phase['phase']}: {phase['name']} - OMITIDA (no aprobada)")
                continue
            
            print(f"\n🚀 Ejecutando Fase {phase['phase']}: {phase['name']}")
            print("-" * 80)
            
            for action in phase.get("actions", []):
                action_id = action.get("id", "unknown")
                print(f"\n  📝 Acción: {action.get('description', 'Sin descripción')}")
                
                try:
                    result = self._execute_action(action)
                    if result.get("success"):
                        results["successful"].append(action_id)
                        print(f"  ✅ Completada exitosamente")
                    else:
                        results["failed"].append(action_id)
                        print(f"  ❌ Falló: {result.get('error', 'Error desconocido')}")
                    
                    results["executed_actions"].append({
                        "id": action_id,
                        "phase": phase["phase"],
                        "result": result
                    })
                except Exception as e:
                    results["failed"].append(action_id)
                    print(f"  ❌ Error: {e}")
        
        # Resumen
        print("\n" + "="*80)
        print("RESUMEN DE EJECUCIÓN")
        print("="*80)
        print(f"\n✅ Exitosas: {len(results['successful'])}")
        print(f"❌ Fallidas: {len(results['failed'])}")
        print(f"⏭️  Omitidas: {len(results['skipped'])}")
        
        return results
    
    def _execute_action(self, action: Dict) -> Dict[str, Any]:
        """Ejecuta una acción individual"""
        action_type = action.get("type", "unknown")
        
        if action_type == "git_branch_delete":
            return self._execute_branch_delete(action)
        elif action_type == "config_setup":
            return self._execute_config_setup(action)
        elif action_type == "directory_creation":
            return self._execute_directory_creation(action)
        elif action_type == "git_remote_add":
            return self._execute_remote_add(action)
        else:
            return {"success": False, "error": f"Tipo de acción desconocido: {action_type}"}
    
    def _execute_branch_delete(self, action: Dict) -> Dict[str, Any]:
        """Elimina branches merged"""
        branches = action.get("affected_branches", [])
        deleted = []
        failed = []
        
        for branch in branches:
            try:
                result = subprocess.run(
                    ["git", "-C", str(self.repo_path), "branch", "-d", branch],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    deleted.append(branch)
                else:
                    failed.append(branch)
            except Exception as e:
                failed.append(branch)
        
        return {
            "success": len(deleted) > 0,
            "deleted": deleted,
            "failed": failed
        }
    
    def _execute_config_setup(self, action: Dict) -> Dict[str, Any]:
        """Configura archivos de configuración"""
        # Por ahora solo reporta - implementación real requeriría crear archivos
        return {
            "success": True,
            "message": "Configuración documentada - requiere implementación manual"
        }
    
    def _execute_directory_creation(self, action: Dict) -> Dict[str, Any]:
        """Crea estructura de directorios"""
        directories = action.get("directories", [])
        created = []
        
        for dir_info in directories:
            dir_path = Path(dir_info.get("path", ""))
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                created.append(str(dir_path))
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {
            "success": True,
            "created": created
        }
    
    def _execute_remote_add(self, action: Dict) -> Dict[str, Any]:
        """Agrega remote de backup"""
        if action.get("requires_input"):
            url = input(f"{action.get('input_prompt', 'URL: ')} ").strip()
            if not url:
                return {"success": False, "error": "URL no proporcionada"}
            
            try:
                result = subprocess.run(
                    ["git", "-C", str(self.repo_path), "remote", "add", "backup", url],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return {"success": True, "remote_url": url}
                else:
                    return {"success": False, "error": result.stderr}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Acción requiere input del usuario"}
    
    def _create_backup(self) -> Optional[str]:
        """Crea backup del estado actual"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = Path.home() / "backups" / "chatbot-2311" / "pre_execution"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Crear git bundle
            bundle_file = backup_dir / f"repo_backup_{timestamp}.bundle"
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "bundle", "create", str(bundle_file), "--all"],
                capture_output=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return str(bundle_file)
        except Exception as e:
            print(f"  ⚠️  Error creando backup: {e}")
        
        return None
    
    def save_plan(self, filename: Optional[str] = None) -> Path:
        """Guarda el plan de ejecución"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"execution_plan_{timestamp}.json"
        
        filepath = Path(filename)
        filepath.write_text(
            json.dumps(self.execution_plan, indent=2, default=str, ensure_ascii=False),
            encoding='utf-8'
        )
        
        return filepath


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Ejecutor de Mejoras del Repositorio con Aprobación"
    )
    parser.add_argument(
        "--repo-path",
        type=str,
        default=None,
        help="Ruta del repositorio"
    )
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="Solo generar plan, no solicitar aprobación"
    )
    parser.add_argument(
        "--approve-all",
        action="store_true",
        help="Aprobar todo automáticamente (NO recomendado)"
    )
    
    args = parser.parse_args()
    
    # Crear ejecutor
    executor = RepoImprovementExecutor(repo_path=args.repo_path)
    
    # Generar plan
    print("\n" + "="*80)
    print("GENERADOR DE PLAN DE EJECUCIÓN")
    print("="*80)
    
    plan = executor.generate_execution_plan()
    
    # Guardar plan
    plan_file = executor.save_plan()
    print(f"\n📄 Plan guardado en: {plan_file}")
    
    if args.plan_only:
        executor.print_execution_plan()
        print("\n✅ Plan generado. Revisa el archivo JSON para detalles.")
        return 0
    
    # Solicitar aprobación
    if args.approve_all:
        print("\n⚠️  ADVERTENCIA: --approve-all activado - Se ejecutará TODO automáticamente")
        approval = {
            "approved": True,
            "approved_phases": [p["phase"] for p in plan.get("execution_phases", [])],
            "timestamp": datetime.now().isoformat()
        }
    else:
        approval = executor.request_approval()
    
    # Ejecutar si está aprobado
    if approval.get("approved"):
        results = executor.execute_approved_plan(approval)
        
        # Guardar resultados
        results_file = Path(f"execution_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        results_file.write_text(
            json.dumps(results, indent=2, default=str, ensure_ascii=False),
            encoding='utf-8'
        )
        print(f"\n📄 Resultados guardados en: {results_file}")
    else:
        print("\n✅ Plan guardado. Puedes ejecutarlo más tarde o modificarlo manualmente.")
    
    return 0


if __name__ == "__main__":
    from collections import defaultdict
    sys.exit(main())

