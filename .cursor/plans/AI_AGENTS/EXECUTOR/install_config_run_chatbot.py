#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Install, Configure and Run Chatbot
===================================

Unified script that:
1. Installs all dependencies
2. Configures the system
3. Runs the chatbot for user testing

Usage:
    python AI_AGENTS/EXECUTOR/install_config_run_chatbot.py
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add project root to path
_current_dir = Path(__file__).parent
_project_root = _current_dir.parent.parent
sys.path.insert(0, str(_project_root))

try:
    from ejecutor_completo import (
        print_success, print_warning, print_error,
        print_info, print_header
    )
except ImportError:
    def print_success(text): print(f"✅ {text}")
    def print_warning(text): print(f"⚠️  {text}")
    def print_error(text): print(f"❌ {text}")
    def print_info(text): print(f"ℹ️  {text}")
    def print_header(text): print(f"\n{'='*80}\n{text}\n{'='*80}\n")


class ChatbotInstaller:
    """Install, configure and run chatbot"""

    def __init__(self):
        self.project_root = _project_root
        self.python_cmd = sys.executable

    def check_python(self) -> bool:
        """Check Python version"""
        print_info("Verificando Python...")
        try:
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                print_success(f"Python {version.major}.{version.minor}.{version.micro}")
                return True
            else:
                print_error(f"Python {version.major}.{version.minor} - Se requiere 3.8+")
                return False
        except Exception as e:
            print_error(f"Error verificando Python: {e}")
            return False

    def install_dependencies(self) -> bool:
        """Install Python dependencies"""
        print_header("INSTALANDO DEPENDENCIAS")

        requirements_file = self.project_root / "requirements.txt"

        if not requirements_file.exists():
            print_warning("requirements.txt no encontrado")
            print_info("Instalando dependencias básicas...")
            deps = [
                "openai", "python-dotenv", "pymongo",
                "fastapi", "uvicorn", "requests",
                "groq", "google-genai"
            ]
            try:
                subprocess.run(
                    [self.python_cmd, "-m", "pip", "install"] + deps,
                    check=True,
                    timeout=300
                )
                print_success("Dependencias básicas instaladas")
                return True
            except Exception as e:
                print_error(f"Error instalando dependencias: {e}")
                return False

        try:
            print_info("Instalando desde requirements.txt...")
            result = subprocess.run(
                [self.python_cmd, "-m", "pip", "install", "-r", str(requirements_file)],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                print_success("Dependencias instaladas correctamente")
                return True
            else:
                print_warning(f"Algunas dependencias pueden no haberse instalado")
                print_info("Continuando...")
                return True  # Continuar aunque haya advertencias
        except subprocess.TimeoutExpired:
            print_error("Timeout instalando dependencias")
            return False
        except Exception as e:
            print_error(f"Error: {e}")
            return False

    def verify_configuration(self) -> bool:
        """Verify system configuration"""
        print_header("VERIFICANDO CONFIGURACIÓN")

        # Check .env files
        env_files = ['.env.local', '.env']
        env_found = False

        for env_file in env_files:
            env_path = self.project_root / env_file
            if env_path.exists():
                print_success(f"Archivo de configuración encontrado: {env_file}")
                env_found = True
                break

        if not env_found:
            print_warning("No se encontró archivo .env o .env.local")
            print_info("El sistema intentará usar variables de entorno del sistema")

        # Check critical files
        critical_files = [
            'ia_conversacional_integrada.py',
            'model_integrator.py',
            'sistema_cotizaciones.py'
        ]

        all_present = True
        for file in critical_files:
            file_path = self.project_root / file
            if file_path.exists():
                print_success(f"Archivo encontrado: {file}")
            else:
                print_error(f"Archivo faltante: {file}")
                all_present = False

        return all_present

    def check_services(self) -> bool:
        """Check if MongoDB is running"""
        print_info("Verificando servicios...")

        try:
            result = subprocess.run(
                ['docker', 'ps', '--format', '{{.Names}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if 'mongodb' in result.stdout.lower() or 'mongo' in result.stdout.lower():
                print_success("MongoDB detectado en Docker")
                return True
            else:
                print_warning("MongoDB no está corriendo (opcional)")
                return True  # No crítico
        except:
            print_warning("Docker no disponible o MongoDB no corriendo (opcional)")
            return True  # No crítico

    def run_chatbot(self, mode: str = "interactive") -> bool:
        """Run the chatbot"""
        print_header("EJECUTANDO CHATBOT")

        # Determine which script to run
        if mode == "interactive":
            script = self.project_root / "chat_interactivo.py"
        elif mode == "api":
            script = self.project_root / "api_server.py"
        elif mode == "unified":
            script = self.project_root / "unified_launcher.py"
        else:
            script = self.project_root / "chat_interactivo.py"

        if not script.exists():
            print_error(f"Script no encontrado: {script}")
            return False

        print_info(f"Ejecutando: {script.name}")
        print_info("Presiona Ctrl+C para detener")
        print()

        try:
            # Run in foreground
            subprocess.run([self.python_cmd, str(script)])
            return True
        except KeyboardInterrupt:
            print("\n\nChatbot detenido por el usuario")
            return True
        except Exception as e:
            print_error(f"Error ejecutando chatbot: {e}")
            return False

    def run_full_setup(self, chatbot_mode: str = "interactive") -> bool:
        """Run complete setup and launch"""
        print_header("INSTALACIÓN, CONFIGURACIÓN Y EJECUCIÓN DEL CHATBOT")
        print_info("Este script realizará:")
        print_info("  1. Verificación de Python")
        print_info("  2. Instalación de dependencias")
        print_info("  3. Verificación de configuración")
        print_info("  4. Verificación de servicios")
        print_info("  5. Ejecución del chatbot")
        print()

        # Step 1: Check Python
        if not self.check_python():
            return False

        # Step 2: Install dependencies
        if not self.install_dependencies():
            print_warning("Continuando a pesar de errores en instalación...")

        # Step 3: Verify configuration
        if not self.verify_configuration():
            print_warning("Algunos archivos faltan, pero continuando...")

        # Step 4: Check services
        self.check_services()

        # Step 5: Run chatbot
        print()
        print_success("✅ Setup completado. Iniciando chatbot...")
        print()
        time.sleep(2)

        return self.run_chatbot(chatbot_mode)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Install, configure and run BMC Chatbot"
    )

    parser.add_argument(
        '--mode',
        choices=['interactive', 'api', 'unified'],
        default='interactive',
        help='Chatbot execution mode (default: interactive)'
    )

    parser.add_argument(
        '--skip-install',
        action='store_true',
        help='Skip dependency installation'
    )

    args = parser.parse_args()

    installer = ChatbotInstaller()

    if args.skip_install:
        # Just run chatbot
        installer.run_chatbot(args.mode)
    else:
        # Full setup
        success = installer.run_full_setup(args.mode)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProceso cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nError fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

