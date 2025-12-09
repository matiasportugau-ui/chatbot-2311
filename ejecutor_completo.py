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

# Importar Model Integrator para IA
try:
    from model_integrator import get_model_integrator
    MODEL_INTEGRATOR_AVAILABLE = True
except ImportError:
    MODEL_INTEGRATOR_AVAILABLE = False
    # print_warning aún no está definido aquí, usar print básico
    pass

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

class AIAssistant:
    """Asistente de IA para mejorar interacciones y diagnóstico"""

    def __init__(self):
        self.integrator = None
        self.enabled = False
        self.conversation_history = []

        if MODEL_INTEGRATOR_AVAILABLE:
            try:
                self.integrator = get_model_integrator()
                self.enabled = True
            except Exception as e:
                print_warning(f"IA no disponible: {e}")
                self.enabled = False

    def is_available(self) -> bool:
        """Verifica si la IA está disponible"""
        return self.enabled and self.integrator is not None

    def generate_message(self, context: str, message_type: str = "info") -> str:
        """
        Genera mensajes mejorados usando IA

        Args:
            context: Contexto del mensaje
            message_type: Tipo de mensaje (info, success, warning, error)
        """
        if not self.is_available():
            return context

        try:
            system_prompt = f"""Eres un asistente experto en sistemas de software.
Genera mensajes claros, concisos y profesionales en español para un ejecutor de sistema.
Tipo de mensaje: {message_type}
Mantén el mensaje breve (máximo 2-3 líneas) y técnicamente preciso."""

            prompt = f"Contexto: {context}\n\nGenera un mensaje mejorado y profesional:"

            response = self.integrator.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=150
            )

            if response and 'content' in response:
                return response['content'].strip()
        except Exception as e:
            print_warning(f"Error generando mensaje con IA: {e}")

        return context

    def diagnose_issue(self, issue: str, context: Dict) -> Dict:
        """
        Diagnostica problemas usando IA

        Args:
            issue: Descripción del problema
            context: Contexto adicional (review_result, etc.)

        Returns:
            Dict con diagnóstico, sugerencias y solución
        """
        if not self.is_available():
            return {
                'diagnosis': issue,
                'suggestions': [],
                'solution': None,
                'confidence': 0.0
            }

        try:
            system_prompt = """Eres un experto en diagnóstico de sistemas de software.
Analiza problemas técnicos y proporciona:
1. Diagnóstico claro del problema
2. Sugerencias de solución paso a paso
3. Solución recomendada
4. Nivel de confianza (0.0-1.0)

Responde en formato JSON con las claves: diagnosis, suggestions (array), solution, confidence."""

            context_str = json.dumps(context, indent=2, default=str)
            prompt = f"""Problema detectado: {issue}

Contexto del sistema:
{context_str}

Proporciona un diagnóstico detallado y soluciones prácticas."""

            response = self.integrator.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=500
            )

            if response and 'content' in response:
                content = response['content'].strip()
                # Intentar parsear JSON si está en el contenido
                try:
                    # Buscar JSON válido en el contenido usando método robusto
                    result = self._extract_json_from_text(content)
                    if result is not None:
                        return result
                    else:
                        # Si no hay JSON válido, crear estructura desde el texto
                        return {
                            'diagnosis': content,
                            'suggestions': self._extract_suggestions(content),
                            'solution': content[:200],
                            'confidence': 0.7
                        }
                except Exception:
                    # Cualquier error, crear estructura desde el texto
                    return {
                        'diagnosis': content,
                        'suggestions': self._extract_suggestions(content),
                        'solution': content[:200],
                        'confidence': 0.7
                    }
        except Exception as e:
            print_warning(f"Error en diagnóstico con IA: {e}")

        return {
            'diagnosis': issue,
            'suggestions': [],
            'solution': None,
            'confidence': 0.0
        }

    def _extract_json_from_text(self, text: str) -> Optional[Dict]:
        """
        Extrae el primer JSON válido del texto, manejando casos donde hay
        texto antes/después o múltiples estructuras JSON.
        Valida que el JSON contiene las claves requeridas: diagnosis, suggestions, solution, confidence.

        Args:
            text: Texto que puede contener JSON

        Returns:
            Dict con el JSON parseado y validado, o None si no se encuentra JSON válido
            o si no contiene las claves requeridas
        """
        def _validate_json_structure(parsed_json: Dict) -> bool:
            """Valida que el JSON contiene las claves requeridas"""
            required_keys = {'diagnosis', 'suggestions', 'solution', 'confidence'}
            return isinstance(parsed_json, dict) and required_keys.issubset(parsed_json.keys())

        # Estrategia 1: Buscar JSON usando coincidencia no greedy
        # Esto encuentra el primer objeto JSON completo
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                if _validate_json_structure(parsed):
                    return parsed
            except json.JSONDecodeError:
                pass

        # Estrategia 2: Buscar JSON balanceado desde el primer {
        # Encuentra el primer { y luego busca el } correspondiente balanceado
        # Intenta múltiples veces si el primer intento falla
        search_start = 0
        while True:
            start_idx = text.find('{', search_start)
            if start_idx == -1:
                break

            # Contar llaves para encontrar el cierre balanceado
            brace_count = 0
            in_string = False
            escape_next = False

            for i in range(start_idx, len(text)):
                char = text[i]

                if escape_next:
                    escape_next = False
                    continue

                if char == '\\':
                    escape_next = True
                    continue

                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue

                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            # Encontramos el JSON balanceado
                            json_str = text[start_idx:i+1]
                            try:
                                parsed = json.loads(json_str)
                                if _validate_json_structure(parsed):
                                    return parsed
                            except json.JSONDecodeError:
                                # Este JSON no es válido, continuar buscando
                                search_start = start_idx + 1
                                break
            else:
                # No se encontró cierre balanceado, salir
                break

        # Estrategia 3: Intentar parsear todo el texto como JSON
        try:
            parsed = json.loads(text.strip())
            if _validate_json_structure(parsed):
                return parsed
        except json.JSONDecodeError:
            pass

        return None

    def _extract_suggestions(self, text: str) -> List[str]:
        """Extrae sugerencias de un texto"""
        suggestions = []
        # Buscar listas numeradas o con viñetas
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or
                        re.match(r'^\d+[\.\)]', line)):
                suggestions.append(line.lstrip('-• ').lstrip('0123456789.) '))
        return suggestions[:5]  # Máximo 5 sugerencias

    def interactive_chat(self, user_input: str, system_context: Dict = None) -> str:
        """
        Modo interactivo de chat con IA

        Args:
            user_input: Pregunta del usuario
            system_context: Contexto del sistema actual

        Returns:
            Respuesta de la IA
        """
        if not self.is_available():
            return "Lo siento, la funcionalidad de IA no está disponible en este momento."

        try:
            # Construir contexto del sistema
            context_info = ""
            if system_context:
                context_info = f"\n\nContexto del sistema:\n{json.dumps(system_context, indent=2, default=str)}"

            system_prompt = """Eres un asistente experto en sistemas de software y deployment.
Ayudas a los usuarios a entender y resolver problemas con sistemas de software.
Sé claro, conciso y técnicamente preciso. Responde en español."""

            # Agregar historial de conversación
            conversation_context = ""
            if self.conversation_history:
                recent = self.conversation_history[-5:]  # Últimas 5 interacciones
                conversation_context = "\n\nConversación reciente:\n"
                for msg in recent:
                    conversation_context += f"Usuario: {msg.get('user', '')}\n"
                    conversation_context += f"Asistente: {msg.get('assistant', '')}\n"

            prompt = f"{user_input}{context_info}{conversation_context}"

            response = self.integrator.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=500
            )

            if response and 'content' in response:
                answer = response['content'].strip()
                # Guardar en historial
                self.conversation_history.append({
                    'user': user_input,
                    'assistant': answer,
                    'timestamp': datetime.now().isoformat()
                })
                return answer
        except Exception as e:
            return f"Error al procesar tu pregunta: {e}"

        return "No pude generar una respuesta. Por favor, intenta de nuevo."

    def clear_history(self):
        """Limpia el historial de conversación"""
        self.conversation_history = []

class SystemReviewer:
    """Fase 1: Review del Sistema"""

    def __init__(self, ai_assistant: Optional['AIAssistant'] = None):
        self.issues = []
        self.warnings = []
        self.ready = True
        self.ai_assistant = ai_assistant

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

        # Mejorar mensaje de inicio con IA si está disponible
        if self.ai_assistant and self.ai_assistant.is_available():
            enhanced_msg = self.ai_assistant.generate_message(
                "Iniciando verificación completa del sistema",
                "info"
            )
            if enhanced_msg:
                print_info(enhanced_msg)

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

    def install(self, review_result: Dict, ai_assistant: Optional['AIAssistant'] = None) -> bool:
        """Ejecuta instalación completa"""
        print_header("FASE 2: INSTALACIÓN AUTOMÁTICA")

        # Mejorar mensaje con IA si está disponible
        if ai_assistant and ai_assistant.is_available():
            enhanced_msg = ai_assistant.generate_message(
                "Verificando e instalando dependencias del sistema",
                "info"
            )
            if enhanced_msg:
                print_info(enhanced_msg)

        needs_install = False

        # Verificar si necesita instalación
        req_deps, _ = review_result['dependencies']
        if req_deps < 2:
            needs_install = True

        if not needs_install:
            msg = "Todas las dependencias están instaladas"
            if ai_assistant and ai_assistant.is_available():
                enhanced = ai_assistant.generate_message(msg, "success")
                if enhanced:
                    print_success(enhanced)
                else:
                    print_success(msg)
            else:
                print_success(msg)
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
                         capture_output=True, check=True, timeout=10)
        except subprocess.TimeoutExpired:
            print_warning("Docker está tardando en responder (timeout 10s)")
            print_info("MongoDB se asume como opcional - el sistema puede funcionar sin él")
            return False
        except FileNotFoundError:
            print_warning("Docker no está instalado o no está en el PATH")
            print_info("MongoDB no se configurará - el sistema puede funcionar sin él")
            return False
        except subprocess.CalledProcessError:
            print_warning("Docker no responde correctamente")
            print_info("MongoDB no se configurará - el sistema puede funcionar sin él")
            return False
        except Exception as e:
            print_warning(f"Error verificando Docker: {e}")
            print_info("MongoDB no se configurará - el sistema puede funcionar sin él")
            return False

        # Verificar si ya existe contenedor
        try:
            result = subprocess.run(
                ['docker', 'ps', '-a', '--format', '{{.Names}}'],
                capture_output=True,
                text=True,
                timeout=10  # Aumentado a 10 segundos
            )
        except subprocess.TimeoutExpired:
            print_warning("Docker está tardando en responder (timeout 10s al listar contenedores)")
            print_info("MongoDB se asume como opcional - el sistema puede funcionar sin él")
            print_info("Si Docker está iniciando, espera unos segundos y vuelve a intentar")
            return False
        except Exception as e:
            print_warning(f"Docker no responde correctamente: {e}")
            print_info("MongoDB no se configurará - el sistema puede funcionar sin él")
            return False

        # Parsear nombres reales de contenedores
        container_names = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        mongo_keywords = ['mongodb', 'bmc-mongodb', 'mongo']

        # Buscar contenedor que contenga alguna palabra clave
        existing = None
        for container_name in container_names:
            container_lower = container_name.lower()
            for keyword in mongo_keywords:
                if keyword in container_lower:
                    existing = container_name  # Usar nombre real del contenedor
                    break
            if existing:
                break

        if existing:
            print_info(f"Contenedor MongoDB encontrado: {existing}")
            # Iniciar si está detenido
            try:
                subprocess.run(['docker', 'start', existing],
                             capture_output=True, timeout=15)
                print_success(f"MongoDB iniciado: {existing}")
                return True
            except subprocess.TimeoutExpired:
                print_warning("Timeout al iniciar contenedor MongoDB (15s)")
                print_info("El contenedor puede estar iniciando - verifica manualmente con: docker ps")
                return False
            except Exception as e:
                print_warning(f"MongoDB encontrado pero no se pudo iniciar: {e}")
                print_info(f"Intenta iniciarlo manualmente con: docker start {existing}")
                return False

        # Crear nuevo contenedor
        print_info("Creando contenedor MongoDB...")
        try:
            # Crear volumen
            try:
                subprocess.run(['docker', 'volume', 'create', 'mongodb_data'],
                             capture_output=True, timeout=15)
            except (subprocess.TimeoutExpired, Exception):
                pass  # El volumen puede ya existir

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
        except subprocess.TimeoutExpired:
            print_warning("Timeout configurando MongoDB - se asume como opcional")
            return False
        except Exception as e:
            print_warning(f"Error configurando MongoDB: {e}")
            return False

    def setup_services(self) -> Dict:
        """Configura todos los servicios"""
        print_header("FASE 3: CONFIGURACIÓN DE SERVICIOS")

        try:
            mongodb_ok = self.setup_mongodb()
        except Exception as e:
            print_warning(f"Error configurando MongoDB (continuando sin MongoDB): {e}")
            mongodb_ok = False

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

def interactive_mode(ai_assistant: AIAssistant, system_context: Dict):
    """Modo interactivo con IA"""
    print_header("MODO INTERACTIVO CON IA")
    print_info("Puedes hacer preguntas sobre el sistema, problemas detectados, o solicitar ayuda.")
    print_info("Escribe 'salir' o 'exit' para terminar.\n")

    while True:
        try:
            user_input = input(f"{Colors.OKCYAN}Tu pregunta: {Colors.ENDC}").strip()

            if not user_input:
                continue

            if user_input.lower() in ['salir', 'exit', 'quit', 'q']:
                print_info("Saliendo del modo interactivo...")
                break

            # Mostrar que está procesando
            print(f"{Colors.OKCYAN}🤔 Procesando...{Colors.ENDC}")

            # Obtener respuesta de la IA
            response = ai_assistant.interactive_chat(user_input, system_context)

            # Mostrar respuesta
            print(f"\n{Colors.OKGREEN}Asistente IA:{Colors.ENDC}")
            print(f"{response}\n")

        except KeyboardInterrupt:
            print("\n\nSaliendo del modo interactivo...")
            break
        except Exception as e:
            print_error(f"Error: {e}")

def main():
    """Ejecuta proceso completo con auto-reparación"""
    print_header("EJECUTOR COMPLETO DEL SISTEMA CHATBOT BMC")
    print_info("Este script automatiza: Review → Instalación → Configuración → Ejecución")
    print_info("Con auto-reparación automática de problemas detectados")
    print()

    # Cargar variables de entorno PRIMERO (antes de inicializar IA)
    print_info("Cargando credenciales desde archivos de configuración...")

    # Intentar cargar secretos automáticamente desde archivo local cifrado
    secrets_loaded = False
    try:
        from load_secrets_automatically import load_secrets_automatically
        if load_secrets_automatically():
            print_success("✅ Secretos cargados desde archivo local cifrado")
            secrets_loaded = True
    except ImportError:
        pass
    except Exception as e:
        print_warning(f"Error cargando secretos automáticos: {e}")

    # Cargar desde archivos .env (si no se cargaron secretos automáticos o como respaldo)
    if not secrets_loaded:
        try:
            from dotenv import load_dotenv

            # Intentar cargar .env.local primero, luego .env
            env_loaded = False
            if Path('.env.local').exists():
                load_dotenv('.env.local', override=True)
                print_success("✅ Variables cargadas desde .env.local")
                env_loaded = True
            elif Path('.env').exists():
                load_dotenv('.env', override=True)
                print_success("✅ Variables cargadas desde .env")
                env_loaded = True

            if not env_loaded:
                print_warning("⚠️  No se encontraron archivos .env o .env.local")
        except ImportError:
            print_warning("⚠️  python-dotenv no está instalado - usando variables de entorno del sistema")
        except Exception as e:
            print_warning(f"⚠️  Error cargando .env: {e}")

    print()

    # Inicializar AI Assistant DESPUÉS de cargar variables de entorno
    ai_assistant = AIAssistant()
    if ai_assistant.is_available():
        print_success("✅ Asistente de IA disponible - Funciones inteligentes habilitadas")
        print_info("   • Diagnóstico inteligente de problemas")
        print_info("   • Mensajes mejorados con generación de texto")
        print_info("   • Modo interactivo para preguntas y ayuda")

        # Mostrar qué proveedor de IA está disponible
        api_keys_found = []
        if os.getenv('OPENAI_API_KEY'):
            api_keys_found.append("OpenAI")
        if os.getenv('GROQ_API_KEY'):
            api_keys_found.append("Groq")
        if os.getenv('GEMINI_API_KEY'):
            api_keys_found.append("Gemini")
        if os.getenv('XAI_API_KEY') or os.getenv('GROK_API_KEY'):
            api_keys_found.append("Grok/xAI")

        if api_keys_found:
            print_info(f"   • Proveedores disponibles: {', '.join(api_keys_found)}")
    else:
        print_info("ℹ️  Asistente de IA no disponible - Funcionando en modo estándar")
        print_info("   (Configura OPENAI_API_KEY, GROQ_API_KEY, o GEMINI_API_KEY en .env para habilitar IA)")
    print()

    # Inicializar AutoFixer
    autofixer = AutoFixer()
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            # Fase 1: Review
            reviewer = SystemReviewer(ai_assistant=ai_assistant)
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

                # Diagnóstico inteligente con IA
                if ai_assistant and ai_assistant.is_available():
                    print()
                    print_header("DIAGNÓSTICO INTELIGENTE CON IA")
                    for issue in review_result['issues']:
                        print_error(f"  • {issue}")
                        diagnosis = ai_assistant.diagnose_issue(issue, review_result)
                        if diagnosis and diagnosis.get('confidence', 0) > 0.5:
                            print_info(f"\n  Diagnóstico: {diagnosis.get('diagnosis', issue)}")
                            if diagnosis.get('suggestions'):
                                print_info("  Sugerencias:")
                                for suggestion in diagnosis['suggestions']:
                                    print_info(f"    - {suggestion}")
                            if diagnosis.get('solution'):
                                print_success(f"  Solución: {diagnosis['solution']}")
                else:
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
        install_ok = installer.install(review_result, ai_assistant=ai_assistant)

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
    except subprocess.TimeoutExpired as e:
        print_warning(f"Timeout configurando servicios: {e}")
        print_info("Los servicios opcionales (MongoDB) no se configurarán")
        print_info("El sistema puede funcionar sin MongoDB - se usará almacenamiento alternativo si está disponible")
        services_result = {'mongodb': False}
    except Exception as e:
        error_msg = str(e)
        print_warning(f"Error configurando servicios (continuando sin servicios opcionales): {error_msg}")

        # Intentar auto-reparar solo si no es un timeout
        if 'timeout' not in error_msg.lower():
            fixed, message = autofixer.detect_and_fix(error_msg, {'context': 'services'})
            if fixed:
                print_success(f"✅ Error reparado: {message}")
                try:
                    services_result = service_manager.setup_services()
                except Exception:
                    services_result = {'mongodb': False}
            else:
                services_result = {'mongodb': False}
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
    if ai_assistant.is_available():
        print("  4. interactive - Modo interactivo con IA (preguntas y ayuda)")
        print("  5. diagnostic - Diagnóstico inteligente del sistema")

    mode = input("\nSelecciona modo [1]: ").strip() or "1"
    mode_map = {'1': 'unified', '2': 'chat', '3': 'api', '4': 'interactive', '5': 'diagnostic'}
    execution_mode = mode_map.get(mode, 'unified')

    # Modo interactivo con IA
    if execution_mode == 'interactive':
        if ai_assistant.is_available():
            system_context = {
                'review': review_result,
                'installation': {'completed': install_ok},
                'services': services_result
            }
            interactive_mode(ai_assistant, system_context)
            execute_ok = True
        else:
            print_error("El modo interactivo requiere que la IA esté disponible")
            print_info("Continuando con modo estándar...")
            execution_mode = 'unified'
            execute_ok = executor.execute(execution_mode)
    # Modo diagnóstico inteligente
    elif execution_mode == 'diagnostic':
        if ai_assistant.is_available():
            print_header("DIAGNÓSTICO INTELIGENTE DEL SISTEMA")
            system_context = {
                'review': review_result,
                'installation': {'completed': install_ok},
                'services': services_result
            }

            # Diagnosticar todos los problemas
            all_issues = review_result.get('issues', []) + review_result.get('warnings', [])
            if all_issues:
                print_info(f"Analizando {len(all_issues)} problemas detectados...\n")
                for issue in all_issues:
                    print(f"\n{Colors.BOLD}Problema: {issue}{Colors.ENDC}")
                    diagnosis = ai_assistant.diagnose_issue(issue, system_context)
                    if diagnosis:
                        print_info(f"Diagnóstico: {diagnosis.get('diagnosis', issue)}")
                        if diagnosis.get('suggestions'):
                            print_info("Sugerencias:")
                            for suggestion in diagnosis['suggestions']:
                                print(f"  • {suggestion}")
                        if diagnosis.get('solution'):
                            print_success(f"Solución recomendada: {diagnosis['solution']}")
                        print(f"Confianza: {diagnosis.get('confidence', 0.0):.1%}")
            else:
                print_success("✅ No se detectaron problemas - El sistema está en buen estado")

            # Preguntar si quiere modo interactivo
            print()
            if input("¿Deseas entrar al modo interactivo para más ayuda? [s/N]: ").strip().lower() == 's':
                interactive_mode(ai_assistant, system_context)

            execute_ok = True
        else:
            print_error("El modo diagnóstico requiere que la IA esté disponible")
            execute_ok = False
    else:
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

