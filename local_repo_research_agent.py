#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente Local de Investigación de Repositorios iOS
==================================================

Agente optimizado para ejecución local que investiga repositorios iOS,
evalúa el workspace y genera planes de consolidación.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Cargar credenciales automáticamente
try:
    from unified_credentials_manager import get_credential
    # Cargar credenciales al importar
    GITHUB_TOKEN = get_credential('GITHUB_TOKEN')
    GITHUB_OWNER = get_credential('GITHUB_OWNER', 'matiasportugau-ui')
    if GITHUB_TOKEN:
        os.environ['GITHUB_TOKEN'] = GITHUB_TOKEN
    if GITHUB_OWNER:
        os.environ['GITHUB_OWNER'] = GITHUB_OWNER
except ImportError:
    # Fallback si no está disponible
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_OWNER = os.getenv('GITHUB_OWNER', 'matiasportugau-ui')

from repo_research_agent import RepoResearchAgent

class LocalRepoResearchAgent(RepoResearchAgent):
    """Agente local optimizado para ejecución directa"""
    
    def __init__(self, workspace_path: Optional[str] = None, auto_execute: bool = True):
        """Inicializa agente local con ejecución automática opcional"""
        super().__init__(workspace_path)
        self.auto_execute = auto_execute
        self.execution_log = []
    
    def log_execution(self, phase: str, status: str, details: str = ""):
        """Registra ejecución de fase"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "status": status,
            "details": details
        }
        self.execution_log.append(log_entry)
        print(f"[{log_entry['timestamp']}] {phase}: {status}")
        if details:
            print(f"  → {details}")
    
    def execute_full_research(self) -> Dict:
        """Ejecuta investigación completa"""
        print("\n" + "="*80)
        print("AGENTE LOCAL DE INVESTIGACIÓN DE REPOSITORIOS iOS")
        print("="*80)
        print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        results = {
            "execution_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": datetime.now().isoformat(),
            "phases": {},
            "summary": {},
            "report_file": None
        }
        
        try:
            # Fase 1: Investigar GitHub
            self.log_execution("Fase 1", "Iniciando", "Investigación de repositorios iOS en GitHub")
            github_results = self.research_github_ios_repos()
            results["phases"]["github_research"] = {
                "status": "completed",
                "repos_found": github_results.get("total_ios_repos", 0),
                "data": github_results
            }
            self.log_execution("Fase 1", "Completada", f"{github_results.get('total_ios_repos', 0)} repositorios encontrados")
            
            # Fase 2: Evaluar workspace
            self.log_execution("Fase 2", "Iniciando", "Evaluación del workspace local")
            workspace_results = self.evaluate_local_workspace()
            results["phases"]["workspace_evaluation"] = {
                "status": "completed",
                "modules_found": workspace_results.get("modules", {}).get("total_modules", 0),
                "data": workspace_results
            }
            self.log_execution("Fase 2", "Completada", f"{workspace_results.get('modules', {}).get('total_modules', 0)} módulos encontrados")
            
            # Fase 3: Identificar mejoras
            self.log_execution("Fase 3", "Iniciando", "Identificación de mejoras cruzadas")
            improvements = self.identify_cross_improvements()
            results["phases"]["improvements"] = {
                "status": "completed",
                "improvements_found": len(improvements),
                "data": improvements
            }
            self.log_execution("Fase 3", "Completada", f"{len(improvements)} mejoras identificadas")
            
            # Fase 4: Generar plan
            self.log_execution("Fase 4", "Iniciando", "Generación de plan de consolidación")
            consolidation_plan = self.generate_consolidation_plan()
            results["phases"]["consolidation_plan"] = {
                "status": "completed",
                "phases_in_plan": len(consolidation_plan.get("phases", [])),
                "data": consolidation_plan
            }
            self.log_execution("Fase 4", "Completada", f"Plan con {len(consolidation_plan.get('phases', []))} fases generado")
            
            # Generar reporte completo
            self.log_execution("Reporte", "Generando", "Reporte completo de investigación")
            report = self.generate_full_report()
            report["execution_log"] = self.execution_log
            
            # Guardar reporte
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.save_report(report, filename=f"local_research_report_{timestamp}.json")
            results["report_file"] = str(report_file)
            results["phases"]["report"] = {"status": "completed", "file": str(report_file)}
            
            # Resumen
            results["summary"] = {
                "total_repos": github_results.get("total_ios_repos", 0),
                "total_modules": workspace_results.get("modules", {}).get("total_modules", 0),
                "total_improvements": len(improvements),
                "plan_phases": len(consolidation_plan.get("phases", [])),
                "status": "success"
            }
            
            results["end_time"] = datetime.now().isoformat()
            results["duration_seconds"] = (
                datetime.fromisoformat(results["end_time"]) - 
                datetime.fromisoformat(results["start_time"])
            ).total_seconds()
            
            self.log_execution("Ejecución", "Completada", f"Reporte guardado en {report_file}")
            
            # Mostrar resumen
            self._print_summary(results)
            
        except Exception as e:
            self.log_execution("Error", "Fallo", str(e))
            results["error"] = str(e)
            results["summary"]["status"] = "error"
            import traceback
            results["traceback"] = traceback.format_exc()
        
        return results
    
    def _print_summary(self, results: Dict):
        """Imprime resumen de ejecución"""
        print("\n" + "="*80)
        print("RESUMEN DE EJECUCIÓN")
        print("="*80)
        print(f"Execution ID: {results['execution_id']}")
        print(f"Duración: {results.get('duration_seconds', 0):.2f} segundos")
        print()
        print("Resultados:")
        summary = results.get("summary", {})
        print(f"  ✅ Repositorios iOS encontrados: {summary.get('total_repos', 0)}")
        print(f"  ✅ Módulos en workspace: {summary.get('total_modules', 0)}")
        print(f"  ✅ Mejoras identificadas: {summary.get('total_improvements', 0)}")
        print(f"  ✅ Fases en plan: {summary.get('plan_phases', 0)}")
        print()
        if results.get("report_file"):
            print(f"📄 Reporte completo: {results['report_file']}")
        print("="*80)


def main():
    """Función principal para ejecución local"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Agente Local de Investigación de Repositorios iOS"
    )
    parser.add_argument(
        "--workspace",
        type=str,
        default=None,
        help="Ruta del workspace (default: directorio actual)"
    )
    parser.add_argument(
        "--github-owner",
        type=str,
        default=os.getenv("GITHUB_OWNER", "matiasportugau-ui"),
        help="Propietario de GitHub"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Archivo de salida personalizado"
    )
    
    args = parser.parse_args()
    
    # Crear y ejecutar agente
    agent = LocalRepoResearchAgent(workspace_path=args.workspace)
    results = agent.execute_full_research()
    
    # Guardar resultados de ejecución
    execution_file = Path(f"local_execution_{results['execution_id']}.json")
    execution_file.write_text(
        json.dumps(results, indent=2, default=str, ensure_ascii=False),
        encoding='utf-8'
    )
    
    print(f"\n✅ Resultados de ejecución guardados en: {execution_file}")
    
    return 0 if results.get("summary", {}).get("status") == "success" else 1


if __name__ == "__main__":
    sys.exit(main())


