#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejecutor Completo del Sistema Chatbot BMC
==========================================

Este script unifica todo el proceso:
1. ✅ Review del sistema (verificación pre-instalación)
2. ✅ Instalación automática (dependencias faltantes)
3. ✅ Configuración automática (MongoDB, servicios)
4. ✅ Ejecución del sistema completo
5. ✅ Monitoreo de estado

Mejores Prácticas Implementadas:
- Verificación antes de ejecutar
- Instalación automática de dependencias
- Gestión de servicios (MongoDB, etc.)
- Manejo de errores robusto
- Logging estructurado
- Estado del sistema en tiempo real
"""

import os
import sys
import subprocess
import time
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from collections import defaultdict

# Importar AutoFixer
try:
    from auto_fixer import AutoFixer
except ImportError:
    # Si no está disponible, crear clase dummy
    class AutoFixer:
        def __init__(self, *args, **kwargs):
            self.fixes_applied = []
        def detect_and_fix(self, *args, **kwargs):
            return False, "AutoFixer no disponible"
        def get_fixes_summary(self):
            return {'total_fixes': 0}

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_success(text: str):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def print_step(step: int, total: int, text: str):
    print(f"\n{Colors.BOLD}[{step}/{total}] {text}{Colors.ENDC}")
    print("-" * 80)

class SystemReviewer:
    """Fase 1: Review del Sistema"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.ready = True
    
    def check_python(self) -> bool:
        """Verifica Python"""
        try:
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                print_success(f"Python {version.major}.{version.minor}.{version.micro}")
                return True
            else:
                print_error(f"Python {version.major}.{version.minor} - Se requiere 3.8+")
                self.issues.append("Python version incompatible")
                self.ready = False
                return False
        except Exception as e:
            print_error(f"Error verificando Python: {e}")
            self.ready = False
            return False
    
    def check_dependencies(self) -> Tuple[int, int]:
        """Verifica dependencias Python"""
        required = ['sistema_cotizaciones', 'utils_cotizaciones']
        optional = ['openai', 'pymongo', 'fastapi', 'uvicorn']
        
        required_ok = 0
        optional_ok = 0
        
        for module in required:
            try:
                __import__(module)
                required_ok += 1
            except ImportError:
                self.issues.append(f"Módulo requerido faltante: {module}")
                self.ready = False
        
        for module in optional:
            try:
                __import__(module)
                optional_ok += 1
            except ImportError:
                self.warnings.append(f"Módulo opcional faltante: {module}")
        
        return required_ok, optional_ok
    
    def check_files(self) -> Tuple[int, int]:
        """Verifica archivos del sistema"""
        required = [
            'config.py',
            'sistema_cotizaciones.py',
            'chat_interactivo.py',
            'unified_launcher.py'
        ]
        
        optional = [
            'api_server.py',
            'base_conocimiento_dinamica.py'
        ]
        
        required_ok = 0
        optional_ok = 0
        
        for filename in required:
            if Path(filename).exists():
                required_ok += 1
            else:
                self.issues.append(f"Archivo requerido faltante: {filename}")
                self.ready = False
        
        for filename in optional:
            if Path(filename).exists():
                optional_ok += 1
        
        return required_ok, optional_ok
    
    def check_env(self) -> bool:
        """Verifica configuración .env"""
        env_files = ['.env.local', '.env']
        for env_file in env_files:
            if Path(env_file).exists():
                print_success(f"Archivo de configuración: {env_file}")
                return True
        
        self.warnings.append("No se encontró archivo .env o .env.local")
        return False
    
    def check_mongodb(self) -> bool:
        """Verifica MongoDB"""
        try:
            result = subprocess.run(
                ['docker', 'ps', '--format', '{{.Names}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if 'mongodb' in result.stdout.lower() or 'mongo' in result.stdout.lower():
                print_success("MongoDB Docker detectado")
                return True
            else:
                print_warning("MongoDB no está corriendo (opcional)")
                return False
        except:
            print_warning("Docker no disponible o MongoDB no corriendo")
            return False
    
    def review(self) -> Dict:
        """Ejecuta review completo"""
        print_header("FASE 1: REVIEW DEL SISTEMA")
        
        print_step(1, 4, "Verificando Python")
        python_ok = self.check_python()
        
        print_step(2, 4, "Verificando Dependencias")
        req_deps, opt_deps = self.check_dependencies()
        print_info(f"Módulos requeridos: {req_deps}/2")
        print_info(f"Módulos opcionales: {opt_deps}/4")
        
        print_step(3, 4, "Verificando Archivos")
        req_files, opt_files = self.check_files()
        print_info(f"Archivos requeridos: {req_files}/4")
        print_info(f"Archivos opcionales: {opt_files}/2")
        
        print_step(4, 4, "Verificando Configuración")
        env_ok = self.check_env()
        mongodb_ok = self.check_mongodb()
        
        return {
            'ready': self.ready,
            'issues': self.issues,
            'warnings': self.warnings,
            'python': python_ok,
            'dependencies': (req_deps, opt_deps),
            'files': (req_files, opt_files),
            'env': env_ok,
            'mongodb': mongodb_ok
        }

class SystemInstaller:
    """Fase 2: Instalación Automática"""
    
    def install_python_dependencies(self) -> bool:
        """Instala dependencias Python"""
        print_step(1, 2, "Instalando Dependencias Python")
        
        if not Path('requirements.txt').exists():
            print_warning("requirements.txt no encontrado")
            return False
        
        try:
            print_info("Ejecutando: pip install -r requirements.txt")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print_success("Dependencias Python instaladas")
                return True
            else:
                print_error(f"Error instalando dependencias: {result.stderr}")
                return False
        except Exception as e:
            print_error(f"Error: {e}")
            return False
    
    def install_node_dependencies(self) -> bool:
        """Instala dependencias Node.js"""
        print_step(2, 2, "Instalando Dependencias Node.js")
        
        if not Path('package.json').exists():
            print_warning("package.json no encontrado (opcional)")
            return True
        
        try:
            print_info("Ejecutando: npm install")
            result = subprocess.run(
                ['npm', 'install'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print_success("Dependencias Node.js instaladas")
                return True
            else:
                print_warning(f"Advertencia en npm install: {result.stderr[:200]}")
                return True  # No crítico
        except Exception as e:
            print_warning(f"npm no disponible o error: {e}")
            return True  # No crítico
    
    def install(self, review_result: Dict) -> bool:
        """Ejecuta instalación completa"""
        print_header("FASE 2: INSTALACIÓN AUTOMÁTICA")
        
        needs_install = False
        
        # Verificar si necesita instalación
        req_deps, _ = review_result['dependencies']
        if req_deps < 2:
            needs_install = True
        
        if not needs_install:
            print_success("Todas las dependencias están instaladas")
            return True
        
        # Instalar
        python_ok = self.install_python_dependencies()
        node_ok = self.install_node_dependencies()
        
        return python_ok

class ServiceManager:
    """Fase 3: Gestión de Servicios (MongoDB, etc.)"""
    
    def setup_mongodb(self) -> bool:
        """Configura MongoDB automáticamente"""
        print_step(1, 1, "Configurando MongoDB")
        
        # Verificar Docker
        try:
            subprocess.run(['docker', '--version'], 
                         capture_output=True, check=True, timeout=5)
        except:
            print_warning("Docker no disponible - MongoDB no se configurará")
            return False
        
        # Verificar si ya existe contenedor
        result = subprocess.run(
            ['docker', 'ps', '-a', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        containers = result.stdout.lower()
        
        # Buscar contenedor MongoDB existente
        mongo_containers = ['mongodb', 'bmc-mongodb', 'mongo']
        existing = None
        
        for name in mongo_containers:
            if name in containers:
                existing = name
                break
        
        if existing:
            print_info(f"Contenedor MongoDB encontrado: {existing}")
            # Iniciar si está detenido
            subprocess.run(['docker', 'start', existing], 
                         capture_output=True, timeout=10)
            print_success(f"MongoDB iniciado: {existing}")
            return True
        
        # Crear nuevo contenedor
        print_info("Creando contenedor MongoDB...")
        try:
            # Crear volumen
            subprocess.run(['docker', 'volume', 'create', 'mongodb_data'],
                         capture_output=True, timeout=10)
            
            # Crear contenedor
            result = subprocess.run([
                'docker', 'run', '-d',
                '--name', 'mongodb',
                '-p', '27017:27017',
                '-v', 'mongodb_data:/data/db',
                '--restart', 'unless-stopped',
                'mongo:latest'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print_success("MongoDB configurado y corriendo")
                time.sleep(3)  # Esperar a que inicie
                return True
            else:
                # Puede fallar si el puerto está ocupado
                if 'port is already allocated' in result.stderr:
                    print_warning("Puerto 27017 ocupado - MongoDB puede estar corriendo")
                    return True
                print_warning(f"MongoDB no se pudo configurar: {result.stderr[:100]}")
                return False
        except Exception as e:
            print_warning(f"Error configurando MongoDB: {e}")
            return False
    
    def setup_services(self) -> Dict:
        """Configura todos los servicios"""
        print_header("FASE 3: CONFIGURACIÓN DE SERVICIOS")
        
        mongodb_ok = self.setup_mongodb()
        
        return {
            'mongodb': mongodb_ok
        }

class SystemExecutor:
    """Fase 4: Ejecución del Sistema"""
    
    def __init__(self):
        self.processes = []
    
    def execute(self, mode: str = 'unified') -> bool:
        """Ejecuta el sistema"""
        print_header("FASE 4: EJECUCIÓN DEL SISTEMA")
        
        if mode == 'unified':
            script = 'unified_launcher.py'
        elif mode == 'chat':
            script = 'chat_interactivo.py'
        elif mode == 'api':
            script = 'api_server.py'
        else:
            script = 'unified_launcher.py'
        
        if not Path(script).exists():
            print_error(f"Script no encontrado: {script}")
            return False
        
        print_info(f"Ejecutando: python {script}")
        print_info("Presiona Ctrl+C para detener")
        print()
        
        try:
            # Ejecutar en foreground
            subprocess.run([sys.executable, script])
            return True
        except KeyboardInterrupt:
            print("\n\nSistema detenido por el usuario")
            return True
        except Exception as e:
            print_error(f"Error ejecutando sistema: {e}")
            return False

class StatusReporter:
    """Fase 5: Reporte de Estado"""
    
    def generate_report(self, review: Dict, install: bool, services: Dict, execute: bool) -> Dict:
        """Genera reporte completo"""
        return {
            'timestamp': datetime.now().isoformat(),
            'review': {
                'ready': review['ready'],
                'issues': review['issues'],
                'warnings': review['warnings']
            },
            'installation': {
                'completed': install,
                'dependencies': review['dependencies'],
                'files': review['files']
            },
            'services': services,
            'execution': {
                'started': execute
            },
            'status': 'ready' if review['ready'] and install else 'not_ready'
        }
    
    def print_report(self, report: Dict):
        """Imprime reporte"""
        print_header("REPORTE DE ESTADO DEL SISTEMA")
        
        print(f"{Colors.BOLD}Estado General:{Colors.ENDC}")
        if report['status'] == 'ready':
            print_success("Sistema listo y operativo")
        else:
            print_error("Sistema no está completamente listo")
        
        print(f"\n{Colors.BOLD}Componentes:{Colors.ENDC}")
        print(f"  • Review: {'✅' if report['review']['ready'] else '❌'}")
        print(f"  • Instalación: {'✅' if report['installation']['completed'] else '❌'}")
        print(f"  • MongoDB: {'✅' if report['services']['mongodb'] else '⚠️ '}")
        print(f"  • Ejecución: {'✅' if report['execution']['started'] else '❌'}")
        
        if report['review']['issues']:
            print(f"\n{Colors.BOLD}Problemas:{Colors.ENDC}")
            for issue in report['review']['issues']:
                print_error(f"  • {issue}")
        
        if report['review']['warnings']:
            print(f"\n{Colors.BOLD}Advertencias:{Colors.ENDC}")
            for warning in report['review']['warnings']:
                print_warning(f"  • {warning}")
        
        print(f"\n{Colors.BOLD}Timestamp:{Colors.ENDC} {report['timestamp']}")

def main():
    """Ejecuta proceso completo con auto-reparación"""
    print_header("EJECUTOR COMPLETO DEL SISTEMA CHATBOT BMC")
    print_info("Este script automatiza: Review → Instalación → Configuración → Ejecución")
    print_info("Con auto-reparación automática de problemas detectados")
    print()
    
    # Inicializar AutoFixer
    autofixer = AutoFixer()
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Fase 1: Review
            reviewer = SystemReviewer()
            review_result = reviewer.review()
            
            # Intentar auto-reparar problemas detectados
            if review_result['issues']:
                print()
                print_header("AUTO-REPARACIÓN DE PROBLEMAS DETECTADOS")
                
                fixed_issues = []
                remaining_issues = []
                
                for issue in review_result['issues']:
                    print_info(f"Intentando reparar: {issue}")
                    fixed, message = autofixer.detect_and_fix(issue, {'context': 'review'})
                    
                    if fixed:
                        print_success(f"✅ Reparado: {message}")
                        fixed_issues.append(issue)
                    else:
                        print_warning(f"⚠️  No se pudo reparar automáticamente: {message}")
                        remaining_issues.append(issue)
                
                # Si se repararon problemas, actualizar review_result
                if fixed_issues:
                    review_result['issues'] = remaining_issues
                    review_result['ready'] = len(remaining_issues) == 0
                    
                    if review_result['ready']:
                        print_success("\n✅ Todos los problemas fueron reparados automáticamente")
                        print_info("Re-ejecutando verificación...")
                        retry_count += 1
                        continue
            
            if not review_result['ready']:
                print_error("\n❌ El sistema no está listo para ejecutar")
                print_info("Problemas que requieren intervención manual:")
                for issue in review_result['issues']:
                    print_error(f"  • {issue}")
                print()
                return 1
            
            # Si llegamos aquí, el sistema está listo
            break
            
        except Exception as e:
            error_msg = str(e)
            print_error(f"\n❌ Error durante review: {error_msg}")
            
            # Intentar auto-reparar el error
            print_info("Intentando auto-reparar error...")
            fixed, message = autofixer.detect_and_fix(error_msg, {'context': 'review_error'})
            
            if fixed:
                print_success(f"✅ Error reparado: {message}")
                retry_count += 1
                print_info("Re-intentando...")
                continue
            else:
                print_error(f"❌ No se pudo reparar automáticamente: {message}")
                return 1
    
    if retry_count >= max_retries:
        print_error("\n❌ Máximo de reintentos alcanzado")
        return 1
    
    # Fase 2: Instalación con auto-reparación
    installer = SystemInstaller()
    
    try:
        install_ok = installer.install(review_result)
        
        if not install_ok:
            print_warning("\n⚠️  Algunas dependencias no se pudieron instalar")
            print_info("Intentando auto-reparar...")
            
            # Intentar auto-reparar
            fixed, message = autofixer.detect_and_fix(
                "Dependencias no instaladas correctamente",
                {'context': 'installation'}
            )
            
            if fixed:
                print_success(f"✅ Reparado: {message}")
                print_info("Re-intentando instalación...")
                install_ok = installer.install(review_result)
            else:
                print_warning("Puedes continuar, pero algunas funciones pueden no estar disponibles")
    except Exception as e:
        error_msg = str(e)
        print_error(f"Error durante instalación: {error_msg}")
        
        fixed, message = autofixer.detect_and_fix(error_msg, {'context': 'installation_error'})
        if fixed:
            print_success(f"✅ Error reparado: {message}")
            install_ok = installer.install(review_result)
        else:
            install_ok = False
    
    # Fase 3: Servicios con auto-reparación
    service_manager = ServiceManager()
    
    try:
        services_result = service_manager.setup_services()
    except Exception as e:
        error_msg = str(e)
        print_error(f"Error configurando servicios: {error_msg}")
        
        fixed, message = autofixer.detect_and_fix(error_msg, {'context': 'services'})
        if fixed:
            print_success(f"✅ Error reparado: {message}")
            services_result = service_manager.setup_services()
        else:
            services_result = {'mongodb': False}
    
    # Fase 4: Ejecución
    executor = SystemExecutor()
    
    # Preguntar modo de ejecución
    print()
    print_info("Modos de ejecución disponibles:")
    print("  1. unified - Unified Launcher (recomendado)")
    print("  2. chat - Chat interactivo")
    print("  3. api - API Server")
    
    mode = input("\nSelecciona modo [1]: ").strip() or "1"
    mode_map = {'1': 'unified', '2': 'chat', '3': 'api'}
    execution_mode = mode_map.get(mode, 'unified')
    
    execute_ok = executor.execute(execution_mode)
    
    # Fase 5: Reporte
    reporter = StatusReporter()
    report = reporter.generate_report(
        review_result, install_ok, services_result, execute_ok
    )
    
    # Guardar reporte
    report_file = Path('system_status_report.json')
    report['auto_fixes'] = autofixer.get_fixes_summary()
    report_file.write_text(json.dumps(report, indent=2), encoding='utf-8')
    
    reporter.print_report(report)
    
    # Mostrar resumen de auto-fixes
    fixes_summary = autofixer.get_fixes_summary()
    if fixes_summary['total_fixes'] > 0:
        print()
        print_header("AUTO-REPARACIONES APLICADAS")
        print_success(f"Total de problemas reparados automáticamente: {fixes_summary['total_fixes']}")
        print_info(f"Soluciones guardadas en: auto_fix_solutions.json")
    
    print()
    print_success("✅ Proceso completado")
    print_info(f"Reporte guardado en: {report_file}")
    
    return 0 if review_result['ready'] and install_ok else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nProceso cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nError fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

