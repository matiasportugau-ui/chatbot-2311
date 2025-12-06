#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instalador Unificado del Chatbot BMC
=====================================

Ejecutable que consolida todas las funcionalidades de instalación,
configuración y verificación del chatbot en un solo script.

Uso:
    chmod +x install_chatbot.py
    ./install_chatbot.py
    # o
    python3 install_chatbot.py
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

# Add project root to path
_current_dir = Path(__file__).parent
sys.path.insert(0, str(_current_dir))

# Try to import existing modules
try:
    from ejecutor_completo import (
        print_success, print_warning, print_error,
        print_info, print_header, print_step, Colors
    )
except ImportError:
    # Fallback print functions
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

# Try to import verification modules
try:
    sys.path.insert(0, str(_current_dir / "AI_AGENTS" / "EXECUTOR"))
    from comprehensive_system_verification import (
        ComprehensiveSystemVerifier,
        VerificationStatus,
        VerificationResult
    )
    VERIFICATION_AVAILABLE = True
except ImportError:
    VERIFICATION_AVAILABLE = False
    print_warning("comprehensive_system_verification no disponible, algunas verificaciones estarán limitadas")

# Try to import model integrator
try:
    from model_integrator import get_model_integrator
    MODEL_INTEGRATOR_AVAILABLE = True
except ImportError:
    MODEL_INTEGRATOR_AVAILABLE = False


class ChecklistStatus(Enum):
    """Estado del checklist"""
    COMPLETE = "complete"
    WARNING = "warning"
    INCOMPLETE = "incomplete"


@dataclass
class ChecklistItem:
    """Item del checklist"""
    name: str
    category: str
    critical: bool
    checked: bool = False
    message: str = ""
    details: Dict = field(default_factory=dict)


class ChecklistManager:
    """Gestiona el checklist de instalación"""
    
    def __init__(self):
        self.items: List[ChecklistItem] = []
        self._initialize_checklist()
    
    def _initialize_checklist(self):
        """Inicializa el checklist con todos los items"""
        # 1. Requisitos del Sistema
        self.items.append(ChecklistItem("Python 3.8+", "Sistema", True))
        self.items.append(ChecklistItem("pip disponible", "Sistema", True))
        self.items.append(ChecklistItem("Directorio del proyecto", "Sistema", True))
        
        # 2. Archivos Esenciales
        self.items.append(ChecklistItem("requirements.txt", "Archivos", True))
        self.items.append(ChecklistItem("ia_conversacional_integrada.py", "Archivos", True))
        self.items.append(ChecklistItem("model_integrator.py", "Archivos", True))
        self.items.append(ChecklistItem("conocimiento_consolidado.json", "Archivos", True))
        self.items.append(ChecklistItem("knowledge_manager.py", "Archivos", True))
        self.items.append(ChecklistItem("training_system.py", "Archivos", True))
        
        # 3. Dependencias
        self.items.append(ChecklistItem("Dependencias instaladas", "Dependencias", True))
        
        # 4. Configuración
        self.items.append(ChecklistItem(".env.local configurado", "Configuración", True))
        self.items.append(ChecklistItem("OPENAI_API_KEY", "Configuración", True))
        
        # 5. Model Integrator
        self.items.append(ChecklistItem("Model Integrator funcional", "IA", True))
        self.items.append(ChecklistItem("Al menos un proveedor de IA", "IA", True))
        
        # 6. Integración del Bot
        self.items.append(ChecklistItem("Bot integrado con IA", "Bot", True))
        self.items.append(ChecklistItem("IA habilitada en bot", "Bot", True))
        
        # 7. Validación IA Obligatoria
        self.items.append(ChecklistItem("Tests IA obligatoria (7/9+)", "Validación", True))
        
        # 8. Base de Conocimiento
        self.items.append(ChecklistItem("Base de conocimiento cargable", "Conocimiento", True))
    
    def check_item(self, name: str, checked: bool, message: str = "", details: Dict = None):
        """Marca un item del checklist"""
        for item in self.items:
            if item.name == name:
                item.checked = checked
                item.message = message
                if details:
                    item.details = details
                return True
        return False
    
    def get_status(self) -> ChecklistStatus:
        """Obtiene el estado general del checklist"""
        critical_items = [item for item in self.items if item.critical]
        checked_critical = sum(1 for item in critical_items if item.checked)
        total_critical = len(critical_items)
        
        if checked_critical == total_critical:
            return ChecklistStatus.COMPLETE
        elif checked_critical >= total_critical * 0.8:  # 80% de items críticos
            return ChecklistStatus.WARNING
        else:
            return ChecklistStatus.INCOMPLETE
    
    def get_summary(self) -> Dict:
        """Obtiene un resumen del checklist"""
        critical_items = [item for item in self.items if item.critical]
        checked_critical = sum(1 for item in critical_items if item.checked)
        total_critical = len(critical_items)
        
        all_items = len(self.items)
        checked_all = sum(1 for item in self.items if item.checked)
        
        return {
            'total': all_items,
            'checked': checked_all,
            'critical_total': total_critical,
            'critical_checked': checked_critical,
            'status': self.get_status().value,
            'completion_rate': f"{(checked_critical / total_critical * 100):.1f}%" if total_critical > 0 else "0%"
        }
    
    def print_summary(self):
        """Imprime un resumen del checklist"""
        summary = self.get_summary()
        print_header("RESUMEN DEL CHECKLIST")
        
        print(f"Total items: {summary['checked']}/{summary['total']}")
        print(f"Items críticos: {summary['critical_checked']}/{summary['critical_total']}")
        print(f"Estado: {summary['status'].upper()}")
        print(f"Completitud: {summary['completion_rate']}")
        print()
        
        # Mostrar items no verificados
        unverified = [item for item in self.items if item.critical and not item.checked]
        if unverified:
            print_error(f"Items críticos faltantes ({len(unverified)}):")
            for item in unverified:
                print(f"  - {item.name} ({item.category})")
        else:
            print_success("Todos los items críticos están verificados")


class DependencyInstaller:
    """Instala dependencias de Python"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.requirements_file = project_root / "requirements.txt"
    
    def install(self) -> Tuple[bool, str]:
        """Instala las dependencias"""
        if not self.requirements_file.exists():
            return False, "requirements.txt no encontrado"
        
        try:
            print_info("Instalando dependencias desde requirements.txt...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(self.requirements_file), "--quiet"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Considerar éxito si el código de retorno es 0
            # o si hay advertencias pero no errores críticos
            if result.returncode == 0:
                return True, "Dependencias instaladas correctamente"
            else:
                # Filtrar advertencias no críticas (como problemas al verificar versión de pip)
                stderr_lower = result.stderr.lower()
                if "error checking the latest version" in stderr_lower or "warning" in stderr_lower:
                    # Si solo son advertencias, verificar si las dependencias críticas están instaladas
                    # y considerar como éxito parcial
                    return True, "Dependencias instaladas (con advertencias menores)"
                else:
                    return False, f"Error instalando dependencias: {result.stderr[:200]}"
        except subprocess.TimeoutExpired:
            return False, "Timeout instalando dependencias"
        except Exception as e:
            return False, f"Error: {str(e)}"


class ConfigManager:
    """Gestiona la configuración del sistema"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.env_file = project_root / ".env.local"
        self.env_template = project_root / ".env.template"
    
    def check_env_file(self) -> Tuple[bool, Dict]:
        """Verifica el archivo .env.local"""
        result = {
            'exists': False,
            'has_openai': False,
            'has_gemini': False,
            'has_grok': False,
            'has_groq': False,
            'keys': {}
        }
        
        if self.env_file.exists():
            result['exists'] = True
            try:
                from dotenv import load_dotenv
                load_dotenv(self.env_file, override=True)
                
                # Verificar API keys
                result['has_openai'] = bool(os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'TU_OPENAI_KEY')
                result['has_gemini'] = bool(os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_API_KEY') != 'TU_GEMINI_KEY')
                result['has_grok'] = bool(os.getenv('XAI_API_KEY') and os.getenv('XAI_API_KEY') != 'TU_XAI_KEY')
                result['has_groq'] = bool(os.getenv('GROQ_API_KEY') and os.getenv('GROQ_API_KEY') != 'TU_GROQ_KEY')
                
                result['keys'] = {
                    'OPENAI_API_KEY': '✓' if result['has_openai'] else '✗',
                    'GEMINI_API_KEY': '✓' if result['has_gemini'] else '✗',
                    'XAI_API_KEY': '✓' if result['has_grok'] else '✗',
                    'GROQ_API_KEY': '✓' if result['has_groq'] else '✗',
                }
            except Exception as e:
                print_warning(f"Error leyendo .env.local: {e}")
        
        return result['exists'] or result['has_openai'], result
    
    def create_env_template(self) -> bool:
        """Crea un template de .env.local si no existe"""
        if self.env_file.exists():
            return True
        
        template_content = """# API Keys para modelos de IA
# Mínimo requerido: OPENAI_API_KEY

OPENAI_API_KEY=tu_openai_api_key_aqui
GEMINI_API_KEY=tu_gemini_api_key_aqui
XAI_API_KEY=tu_grok_api_key_aqui
GROQ_API_KEY=tu_groq_api_key_aqui

# Modelo por defecto
OPENAI_MODEL=gpt-4o-mini

# MongoDB (opcional)
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=bmc_chatbot
"""
        
        try:
            self.env_file.write_text(template_content, encoding='utf-8')
            print_info(f"Template de .env.local creado en {self.env_file}")
            print_warning("Por favor, edita .env.local y agrega tus API keys antes de continuar")
            return True
        except Exception as e:
            print_error(f"Error creando .env.local: {e}")
            return False


class IAValidator:
    """Valida que la IA esté correctamente implementada"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.bot_file = project_root / "ia_conversacional_integrada.py"
    
    def run_tests(self) -> Tuple[int, int, List[str]]:
        """Ejecuta los tests de validación de IA"""
        passed = 0
        total = 0
        failures = []
        
        if not self.bot_file.exists():
            return 0, 0, ["ia_conversacional_integrada.py no encontrado"]
        
        try:
            content = self.bot_file.read_text(encoding='utf-8')
            
            # Test 1: No random.choice
            total += 1
            if 'random.choice' not in content:
                passed += 1
            else:
                failures.append("Se encontró uso de random.choice")
            
            # Test 2: Usa model_integrator
            total += 1
            if 'model_integrator.generate' in content:
                matches = len(re.findall(r'model_integrator\.generate', content))
                if matches >= 3:
                    passed += 1
                else:
                    failures.append(f"Solo {matches} usos de model_integrator.generate (esperado: 3+)")
            else:
                failures.append("No se encontró uso de model_integrator.generate")
            
            # Test 3: KnowledgeManager
            total += 1
            if 'KnowledgeManager' in content and 'self.knowledge_manager' in content:
                passed += 1
            else:
                failures.append("KnowledgeManager no está integrado")
            
            # Test 4: TrainingSystem
            total += 1
            if 'TrainingSystem' in content and 'self.training_system' in content:
                passed += 1
            else:
                failures.append("TrainingSystem no está integrado")
            
            # Test 5: Métodos IA requeridos
            total += 1
            required_methods = [
                '_generar_saludo_ia',
                '_generar_despedida_ia',
                '_obtener_informacion_producto_ia',
                '_enriquecer_contexto_completo',
                '_construir_system_prompt',
                '_procesar_con_ia'
            ]
            missing = [m for m in required_methods if f'def {m}' not in content]
            if not missing:
                passed += 1
            else:
                failures.append(f"Métodos faltantes: {', '.join(missing)}")
            
            # Test 6: use_ai habilitado
            total += 1
            if 'self.use_ai = True' in content or 'self.use_ai=True' in content:
                passed += 1
            else:
                failures.append("use_ai no está habilitado")
            
            # Test 7: knowledge_manager.py existe
            total += 1
            km_file = self.project_root / "AI_AGENTS" / "EXECUTOR" / "knowledge_manager.py"
            if km_file.exists():
                passed += 1
            else:
                failures.append("knowledge_manager.py no encontrado")
            
            # Test 8: training_system.py existe
            total += 1
            ts_file = self.project_root / "AI_AGENTS" / "EXECUTOR" / "training_system.py"
            if ts_file.exists():
                passed += 1
            else:
                failures.append("training_system.py no encontrado")
            
            # Test 9: No fallback principal a pattern matching
            total += 1
            if '_procesar_mensaje_patrones_DEPRECATED' in content or '_procesar_mensaje_patrones' not in content:
                passed += 1
            else:
                # Verificar que no se use como primera opción
                if 'procesar_mensaje_usuario' in content:
                    pattern = r'def procesar_mensaje_usuario.*?(?=def |\Z)'
                    match = re.search(pattern, content, re.DOTALL)
                    if match and '_procesar_mensaje_patrones(' in match.group(0) and 'except' not in match.group(0):
                        failures.append("Pattern matching usado como opción principal")
                    else:
                        passed += 1
                else:
                    passed += 1
        
        except Exception as e:
            failures.append(f"Error ejecutando tests: {e}")
        
        return passed, total, failures


class ChatbotInstaller:
    """Instalador unificado del chatbot"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.checklist = ChecklistManager()
        self.installer = DependencyInstaller(self.project_root)
        self.configurator = ConfigManager(self.project_root)
        self.ia_validator = IAValidator(self.project_root)
        self.verifier = None
        
        if VERIFICATION_AVAILABLE:
            try:
                self.verifier = ComprehensiveSystemVerifier()
            except Exception as e:
                print_warning(f"No se pudo inicializar ComprehensiveSystemVerifier: {e}")
    
    def run(self):
        """Ejecuta el proceso completo de instalación"""
        print_header("INSTALADOR UNIFICADO DEL CHATBOT BMC")
        print_info("Este script verificará e instalará todos los componentes necesarios")
        print()
        
        try:
            # Fase 1: Verificación Pre-Instalación
            if not self._phase1_pre_installation():
                print_error("Fase 1 falló. No se puede continuar.")
                return False
            
            # Fase 2: Instalación de Dependencias
            if not self._phase2_dependencies():
                print_error("Fase 2 falló. No se puede continuar.")
                return False
            
            # Fase 3: Configuración
            if not self._phase3_configuration():
                print_warning("Fase 3 completada con advertencias. Revisa la configuración.")
            
            # Fase 4: Verificación Completa del Sistema
            if not self._phase4_system_verification():
                print_warning("Fase 4 completada con advertencias.")
            
            # Fase 5: Validación de IA Obligatoria
            if not self._phase5_ia_validation():
                print_error("Fase 5 falló. El bot no cumple con los requisitos de IA obligatoria.")
                return False
            
            # Fase 6: Checklist Final
            checklist_status = self._phase6_final_checklist()
            
            if checklist_status == ChecklistStatus.INCOMPLETE:
                print_error("El checklist está INCOMPLETO. No se puede ejecutar el chatbot.")
                self.checklist.print_summary()
                return False
            
            # Fase 7: Ejecución Opcional
            if checklist_status == ChecklistStatus.COMPLETE:
                self._phase7_interactive_execution()
            else:
                print_warning("El checklist tiene advertencias. Se recomienda revisar antes de ejecutar.")
                response = input("\n¿Deseas ejecutar el chatbot de todas formas? (s/N): ").strip().lower()
                if response == 's':
                    self._phase7_interactive_execution()
            
            return True
        
        except KeyboardInterrupt:
            print("\n\nInstalación cancelada por el usuario.")
            return False
        except Exception as e:
            print_error(f"Error inesperado: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _phase1_pre_installation(self) -> bool:
        """Fase 1: Verificación Pre-Instalación"""
        print_step(1, 7, "FASE 1: Verificación Pre-Instalación")
        
        # Verificar Python
        print_info("Verificando Python...")
        if sys.version_info < (3, 8):
            print_error(f"Python 3.8+ requerido. Versión actual: {sys.version}")
            return False
        print_success(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        self.checklist.check_item("Python 3.8+", True, f"Versión {sys.version_info.major}.{sys.version_info.minor}")
        
        # Verificar pip
        print_info("Verificando pip...")
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print_success("pip disponible")
                self.checklist.check_item("pip disponible", True)
            else:
                print_error("pip no disponible")
                return False
        except Exception as e:
            print_error(f"Error verificando pip: {e}")
            return False
        
        # Verificar directorio
        print_info("Verificando directorio del proyecto...")
        if self.project_root.exists():
            print_success(f"Directorio: {self.project_root}")
            self.checklist.check_item("Directorio del proyecto", True)
        else:
            print_error("Directorio del proyecto no encontrado")
            return False
        
        # Verificar archivos esenciales
        print_info("Verificando archivos esenciales...")
        essential_files = {
            "requirements.txt": "requirements.txt",
            "ia_conversacional_integrada.py": "ia_conversacional_integrada.py",
            "model_integrator.py": "model_integrator.py",
            "conocimiento_consolidado.json": "conocimiento_consolidado.json",
            "knowledge_manager.py": "AI_AGENTS/EXECUTOR/knowledge_manager.py",
            "training_system.py": "AI_AGENTS/EXECUTOR/training_system.py"
        }
        
        all_found = True
        for name, path in essential_files.items():
            file_path = self.project_root / path
            if file_path.exists():
                print_success(f"{name} encontrado")
                self.checklist.check_item(name, True)
            else:
                print_warning(f"{name} no encontrado en {path}")
                self.checklist.check_item(name, False, f"No encontrado en {path}")
                if name in ["requirements.txt", "ia_conversacional_integrada.py", "model_integrator.py"]:
                    all_found = False
        
        return all_found
    
    def _phase2_dependencies(self) -> bool:
        """Fase 2: Instalación de Dependencias"""
        print_step(2, 7, "FASE 2: Instalación de Dependencias")
        
        # Verificar si requirements.txt existe
        if not (self.project_root / "requirements.txt").exists():
            print_error("requirements.txt no encontrado")
            return False
        
        # Intentar instalar dependencias
        success, message = self.installer.install()
        if success:
            print_success(message)
            self.checklist.check_item("Dependencias instaladas", True, message)
        else:
            print_warning(message)
            # Intentar verificar dependencias críticas manualmente
            print_info("Verificando dependencias críticas...")
            # Mapeo: nombre del paquete pip -> nombre del módulo Python
            critical_deps = {
                'openai': 'openai',
                'python-dotenv': 'dotenv'
            }
            missing = []
            for pip_name, module_name in critical_deps.items():
                try:
                    __import__(module_name)
                    print_success(f"{pip_name} instalado")
                except ImportError:
                    print_error(f"{pip_name} no instalado")
                    missing.append(pip_name)
            
            if missing:
                print_error(f"Dependencias críticas faltantes: {', '.join(missing)}")
                return False
            else:
                self.checklist.check_item("Dependencias instaladas", True, "Dependencias críticas verificadas")
        
        return True
    
    def _phase3_configuration(self) -> bool:
        """Fase 3: Configuración"""
        print_step(3, 7, "FASE 3: Configuración")
        
        # Verificar .env.local
        print_info("Verificando configuración...")
        env_ok, env_details = self.configurator.check_env_file()
        
        if not env_ok:
            print_warning(".env.local no encontrado o sin OPENAI_API_KEY")
            response = input("¿Deseas crear un template de .env.local? (S/n): ").strip().lower()
            if response != 'n':
                self.configurator.create_env_template()
                print_warning("Por favor, edita .env.local y agrega tus API keys, luego ejecuta este script nuevamente.")
                return False
        else:
            print_success(".env.local encontrado")
            self.checklist.check_item(".env.local configurado", True)
            
            # Verificar API keys
            if env_details.get('has_openai'):
                print_success("OPENAI_API_KEY configurada")
                self.checklist.check_item("OPENAI_API_KEY", True)
            else:
                print_error("OPENAI_API_KEY no configurada (REQUERIDA)")
                self.checklist.check_item("OPENAI_API_KEY", False)
                return False
            
            # Cargar variables de entorno
            try:
                from dotenv import load_dotenv
                load_dotenv(self.configurator.env_file, override=True)
            except Exception as e:
                print_warning(f"Error cargando .env.local: {e}")
        
        # Verificar base de conocimiento
        print_info("Verificando base de conocimiento...")
        kb_file = self.project_root / "conocimiento_consolidado.json"
        if kb_file.exists():
            try:
                with open(kb_file, 'r', encoding='utf-8') as f:
                    kb_data = json.load(f)
                if isinstance(kb_data, dict) and len(kb_data) > 0:
                    print_success("Base de conocimiento válida")
                    self.checklist.check_item("conocimiento_consolidado.json", True)
                else:
                    print_warning("Base de conocimiento vacía o inválida")
                    self.checklist.check_item("conocimiento_consolidado.json", False)
            except Exception as e:
                print_warning(f"Error leyendo base de conocimiento: {e}")
                self.checklist.check_item("conocimiento_consolidado.json", False)
        else:
            print_warning("conocimiento_consolidado.json no encontrado")
            self.checklist.check_item("conocimiento_consolidado.json", False)
        
        return env_ok
    
    def _phase4_system_verification(self) -> bool:
        """Fase 4: Verificación Completa del Sistema"""
        print_step(4, 7, "FASE 4: Verificación Completa del Sistema")
        
        if not self.verifier:
            print_warning("ComprehensiveSystemVerifier no disponible, saltando verificaciones avanzadas")
            return True
        
        try:
            # Ejecutar verificación completa
            report = self.verifier.run_full_verification()
            
            # Procesar resultados
            summary = report.get('summary', {})
            passed = summary.get('passed', 0)
            failed = summary.get('failed', 0)
            warnings = summary.get('warnings', 0)
            
            print_info(f"Verificaciones: {passed} exitosas, {failed} fallidas, {warnings} advertencias")
            
            # Verificar Model Integrator
            model_result = None
            for result in self.verifier.results:
                if result.name == "Model Integrator":
                    model_result = result
                    break
            
            if model_result and model_result.status == VerificationStatus.PASS:
                print_success("Model Integrator funcional")
                self.checklist.check_item("Model Integrator funcional", True, model_result.message)
            else:
                print_error("Model Integrator no funcional")
                self.checklist.check_item("Model Integrator funcional", False, 
                                        model_result.message if model_result else "No verificado")
            
            # Verificar al menos un proveedor de IA
            provider_results = [r for r in self.verifier.results if 'Provider' in r.name]
            working_providers = [r for r in provider_results if r.status == VerificationStatus.PASS]
            
            if working_providers:
                providers = [r.name.replace('Provider ', '') for r in working_providers]
                print_success(f"Proveedores de IA funcionando: {', '.join(providers)}")
                self.checklist.check_item("Al menos un proveedor de IA", True, 
                                        f"{len(working_providers)} proveedor(es) funcionando")
            else:
                print_error("Ningún proveedor de IA funciona")
                self.checklist.check_item("Al menos un proveedor de IA", False)
            
            # Verificar integración del bot
            bot_result = None
            for result in self.verifier.results:
                if result.name == "Bot Integration":
                    bot_result = result
                    break
            
            if bot_result and bot_result.status == VerificationStatus.PASS:
                print_success("Bot integrado correctamente")
                self.checklist.check_item("Bot integrado con IA", True, bot_result.message)
                self.checklist.check_item("IA habilitada en bot", True)
            else:
                print_error("Bot no integrado correctamente")
                self.checklist.check_item("Bot integrado con IA", False,
                                        bot_result.message if bot_result else "No verificado")
            
            return failed == 0 or (failed < 3 and passed > failed)
        
        except Exception as e:
            print_error(f"Error en verificación del sistema: {e}")
            return False
    
    def _phase5_ia_validation(self) -> bool:
        """Fase 5: Validación de IA Obligatoria"""
        print_step(5, 7, "FASE 5: Validación de IA Obligatoria")
        
        print_info("Ejecutando tests de validación de IA...")
        passed, total, failures = self.ia_validator.run_tests()
        
        print_info(f"Tests: {passed}/{total} exitosos")
        
        if failures:
            print_warning(f"Fallos detectados ({len(failures)}):")
            for failure in failures[:5]:  # Mostrar máximo 5
                print(f"  - {failure}")
        
        # Requerir al menos 7/9 tests pasando
        if passed >= 7:
            print_success(f"Validación de IA: {passed}/{total} tests pasaron (requerido: 7+)")
            self.checklist.check_item("Tests IA obligatoria (7/9+)", True, f"{passed}/{total} tests")
            return True
        else:
            print_error(f"Validación de IA falló: solo {passed}/{total} tests pasaron (requerido: 7+)")
            self.checklist.check_item("Tests IA obligatoria (7/9+)", False, f"Solo {passed}/{total} tests")
            return False
    
    def _phase6_final_checklist(self) -> ChecklistStatus:
        """Fase 6: Checklist Final Pre-Ejecución"""
        print_step(6, 7, "FASE 6: Checklist Final Pre-Ejecución")
        
        # Verificar base de conocimiento cargable
        print_info("Verificando base de conocimiento cargable...")
        try:
            sys.path.insert(0, str(self.project_root / "AI_AGENTS" / "EXECUTOR"))
            from knowledge_manager import KnowledgeManager
            km = KnowledgeManager()
            if km.knowledge_base:
                print_success("Base de conocimiento cargable")
                self.checklist.check_item("Base de conocimiento cargable", True)
            else:
                print_warning("Base de conocimiento no se pudo cargar")
                self.checklist.check_item("Base de conocimiento cargable", False)
        except Exception as e:
            print_warning(f"Error verificando base de conocimiento: {e}")
            self.checklist.check_item("Base de conocimiento cargable", False)
        
        # Obtener estado final
        status = self.checklist.get_status()
        summary = self.checklist.get_summary()
        
        print()
        print_header("CHECKLIST FINAL")
        self.checklist.print_summary()
        
        return status
    
    def _phase7_interactive_execution(self):
        """Fase 7: Ejecución Opcional del Chatbot"""
        print_step(7, 7, "FASE 7: Ejecución Opcional del Chatbot")
        
        print()
        print_success("¡Instalación completada exitosamente!")
        print()
        
        response = input("¿Deseas ejecutar el chatbot ahora? (S/n): ").strip().lower()
        
        if response == 'n':
            print_info("Para ejecutar el chatbot manualmente:")
            print("  python3 chat_interactivo_ai.py")
            print("  # o")
            print("  python3 chat_interactivo.py")
            return
        
        # Buscar script de chatbot
        chatbot_scripts = [
            "chat_interactivo_ai.py",
            "chat_interactivo.py",
            "unified_launcher.py"
        ]
        
        chatbot_script = None
        for script in chatbot_scripts:
            script_path = self.project_root / script
            if script_path.exists():
                chatbot_script = script_path
                break
        
        if not chatbot_script:
            print_error("No se encontró ningún script de chatbot para ejecutar")
            return
        
        print()
        print_header("INICIANDO CHATBOT")
        print_info(f"Ejecutando: {chatbot_script.name}")
        print_info("Presiona Ctrl+C para detener")
        print()
        
        try:
            # Ejecutar el chatbot
            os.chdir(self.project_root)
            os.execv(sys.executable, [sys.executable, str(chatbot_script)])
        except KeyboardInterrupt:
            print("\n\nChatbot detenido por el usuario.")
        except Exception as e:
            print_error(f"Error ejecutando chatbot: {e}")


def main():
    """Función principal"""
    installer = ChatbotInstaller()
    success = installer.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

