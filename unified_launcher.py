#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Launcher for BMC Chatbot System
Single entry point for all system operations
"""

import sys
import subprocess
import platform
import signal
import time
import logging
from pathlib import Path
from typing import List, Optional
import argparse


# Color codes for terminal output
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


class UnifiedLauncher:
    """Unified launcher for BMC Chatbot System"""

    def __init__(
        self, skip_setup: bool = False, production: bool = False, dev: bool = False
    ):
        self.root_dir = Path(__file__).parent.resolve()
        self.python_cmd = self._find_python()
        self.node_cmd = self._find_node()
        self.npm_cmd = self._find_npm()
        self.is_windows = platform.system() == "Windows"
        self.setup_complete = False
        self.skip_setup = skip_setup
        self.production = production
        self.dev = dev
        self.background_processes: List[subprocess.Popen] = []

        # Setup logging
        self.log_dir = self.root_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)
        self._setup_logging()

        # Signal handlers for cleanup
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _setup_logging(self):
        """Setup logging system"""
        log_file = self.log_dir / "launcher.log"
        log_level = logging.DEBUG if self.dev else logging.INFO

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def _signal_handler(self, signum, frame):
        """Handle signals for graceful shutdown"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self._cleanup_processes()
        sys.exit(0)

    def _cleanup_processes(self):
        """Clean up background processes"""
        for process in self.background_processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass
        self.background_processes.clear()

    def _find_python(self) -> Optional[str]:
        """Find Python executable"""
        for cmd in ["python3", "python", "py"]:
            try:
                result = subprocess.run(
                    [cmd, "--version"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    version = result.stdout.strip()
                    # Check for Python 3.11+
                    version_parts = version.split()
                    if len(version_parts) >= 2:
                        version_str = version_parts[1]
                        major, minor = map(int, version_str.split(".")[:2])
                        if major > 3 or (major == 3 and minor >= 11):
                            return cmd
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue
        return None

    def _find_node(self) -> Optional[str]:
        """Find Node.js executable"""
        for cmd in ["node", "nodejs"]:
            try:
                result = subprocess.run(
                    [cmd, "--version"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return cmd
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue
        return None

    def _find_npm(self) -> Optional[str]:
        """Find npm executable"""
        for cmd in ["npm", "yarn"]:
            try:
                result = subprocess.run(
                    [cmd, "--version"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return cmd
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue
        return None

    def check_prerequisites(self) -> bool:
        """Check all prerequisites"""
        print_header("Checking Prerequisites")

        all_ok = True

        # Check Python
        if not self.python_cmd:
            print_error("Python 3.11+ not found!")
            print_info("Please install Python 3.11 or higher")
            all_ok = False
        else:
            version = subprocess.run(
                [self.python_cmd, "--version"], capture_output=True, text=True
            ).stdout.strip()
            print_success(f"Python found: {version} ({self.python_cmd})")

        # Check Node.js (optional)
        if not self.node_cmd:
            print_warning("Node.js not found (optional for Next.js dashboard)")
        else:
            version = subprocess.run(
                [self.node_cmd, "--version"], capture_output=True, text=True
            ).stdout.strip()
            print_success(f"Node.js found: {version}")

        # Check npm/yarn
        if self.node_cmd and not self.npm_cmd:
            print_warning("npm/yarn not found (needed for Next.js dependencies)")
        elif self.npm_cmd:
            version = subprocess.run(
                [self.npm_cmd, "--version"], capture_output=True, text=True
            ).stdout.strip()
            print_success(f"Package manager found: {self.npm_cmd} {version}")

        return all_ok

    def setup_environment(self) -> bool:
        """Run all setup steps"""
        if self.skip_setup:
            print_info("Skipping setup (--skip-setup flag)")
            return True

        print_header("Setting Up Environment")

        setup_steps = [
            ("Installing Python dependencies", self._install_python_deps),
            ("Configuring environment", self._configure_env),
            ("Consolidating knowledge base", self._consolidate_knowledge),
            ("Managing services", self._manage_services),
            ("Installing Node.js dependencies", self._install_nodejs_deps),
            ("Verifying system", self._verify_system),
        ]

        for step_name, step_func in setup_steps:
            print_info(f"{step_name}...")
            try:
                if not step_func():
                    print_warning(f"{step_name} completed with warnings")
            except Exception as e:
                print_error(f"{step_name} failed: {e}")
                self.logger.error(f"{step_name} failed", exc_info=True)
                if "dependencies" in step_name.lower():
                    return False

        self.setup_complete = True
        print_success("Environment setup complete!")
        return True

    def _install_python_deps(self) -> bool:
        """Install Python dependencies"""
        req_file = self.root_dir / "requirements.txt"
        if not req_file.exists():
            print_warning("requirements.txt not found")
            return False

        try:
            # Upgrade pip
            subprocess.run(
                [self.python_cmd, "-m", "pip", "install", "--upgrade", "pip"],
                check=False,
                capture_output=True,
            )

            # Install requirements
            subprocess.run(
                [self.python_cmd, "-m", "pip", "install", "-r", str(req_file)],
                check=True,
                capture_output=True,
                text=True,
            )
            print_success("Python dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to install dependencies: {e}")
            self.logger.error(f"Failed to install Python deps: {e.stderr}")
            return False

    def _configure_env(self) -> bool:
        """Configure environment file"""
        env_file = self.root_dir / ".env"
        env_example = self.root_dir / "env.example"

        # If .env exists, check if it has required keys
        if env_file.exists():
            env_content = env_file.read_text()
            if "OPENAI_API_KEY" in env_content and "your-" not in env_content:
                print_success(".env file exists and configured")
                return True

        # Try to run configurar_entorno.py
        config_script = self.root_dir / "configurar_entorno.py"
        if config_script.exists():
            try:
                # Import and call the function directly
                import importlib.util

                spec = importlib.util.spec_from_file_location(
                    "configurar_entorno", config_script
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                else:
                    raise ImportError("Could not load configurar_entorno module")

                # Call main function
                if hasattr(module, "main"):
                    module.main()
                    print_success(".env configured")
                    return True
            except Exception as e:
                self.logger.warning(f"Could not import configurar_entorno: {e}")

        # Create minimal .env from example
        if env_example.exists():
            print_info("Creating .env from env.example...")
            example_content = env_example.read_text()
            env_file.write_text(example_content)
            print_warning("Please configure OPENAI_API_KEY in .env file")
            return False

        return False

    def _consolidate_knowledge(self) -> bool:
        """Consolidate knowledge base files if they exist"""
        consolidate_script = self.root_dir / "consolidar_conocimiento.py"
        consolidated_file = self.root_dir / "conocimiento_consolidado.json"
        
        # Check if consolidation is needed
        if consolidated_file.exists():
            # Check if it's recent (less than 7 days old)
            import time
            file_age = time.time() - consolidated_file.stat().st_mtime
            if file_age < 7 * 24 * 3600:  # 7 days
                print_success("Consolidated knowledge file exists and is recent")
                return True
        
        # Try to consolidate if script exists
        if consolidate_script.exists():
            try:
                import importlib.util
                
                spec = importlib.util.spec_from_file_location(
                    "consolidar_conocimiento", consolidate_script
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                else:
                    raise ImportError("Could not load consolidar_conocimiento module")
                
                # Check if ConsolidadorConocimiento class exists
                if hasattr(module, "ConsolidadorConocimiento"):
                    consolidador = module.ConsolidadorConocimiento()
                    conocimiento = consolidador.consolidar_todos()
                    consolidador.guardar(str(consolidated_file))
                    print_success("Knowledge base consolidated successfully")
                    return True
            except Exception as e:
                self.logger.warning(f"Could not consolidate knowledge: {e}")
                print_warning("Knowledge consolidation skipped (not critical)")
        
        return True  # Not critical, system can work without consolidation

    def _manage_services(self) -> bool:
        """Manage optional services (MongoDB, etc.)"""
        gestion_script = self.root_dir / "gestionar_servicios.py"
        if gestion_script.exists():
            try:
                # Import and call the function directly
                import importlib.util

                spec = importlib.util.spec_from_file_location(
                    "gestionar_servicios", gestion_script
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                else:
                    raise ImportError("Could not load gestionar_servicios module")

                if hasattr(module, "main"):
                    module.main()
                    return True
            except Exception as e:
                self.logger.warning(f"Could not manage services: {e}")
        return True  # Not critical

    def _install_nodejs_deps(self) -> bool:
        """Install Node.js dependencies"""
        if not self.node_cmd or not self.npm_cmd:
            print_warning("Node.js or npm not found, skipping Node.js dependencies")
            return True  # Not critical

        # Check for package.json in root or nextjs-app
        package_json_paths = [
            self.root_dir / "package.json",
            self.root_dir / "nextjs-app" / "package.json",
        ]

        for package_json in package_json_paths:
            if package_json.exists():
                print_info(
                    f"Installing Node.js dependencies from {package_json.parent.name}..."
                )
                try:
                    result = subprocess.run(
                        [self.npm_cmd, "install"],
                        cwd=package_json.parent,
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    print_success(
                        f"Node.js dependencies installed in {package_json.parent.name}"
                    )
                    return True
                except subprocess.CalledProcessError as e:
                    print_warning(f"Failed to install Node.js dependencies: {e}")
                    return False

        return True  # No package.json found, not an error

    def _verify_system(self) -> bool:
        """Verify system setup"""
        verify_script = self.root_dir / "verificar_sistema_completo.py"
        if verify_script.exists():
            try:
                # Import and call the function directly
                import importlib.util

                spec = importlib.util.spec_from_file_location(
                    "verificar_sistema_completo", verify_script
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                else:
                    raise ImportError(
                        "Could not load verificar_sistema_completo module"
                    )

                if hasattr(module, "main"):
                    module.main()
                    return True
            except Exception as e:
                self.logger.warning(f"Could not verify system: {e}")
        return True

    def show_menu(self):
        """Show main menu"""
        print_header("BMC Chatbot System - Unified Launcher")

        modes = [
            ("1", "Interactive Chatbot", "chat_interactivo.py", "python"),
            ("2", "API Server", "api_server.py", "python"),
            ("3", "Chat Simulator", "simulate_chat.py", "python"),
            ("4", "Enhanced CLI Simulator", "simulate_chat_cli.py", "python"),
            ("5", "Main System Menu", "main.py", "python"),
            ("6", "Automated Agent System", "automated_agent_system.py", "python"),
            ("7", "System Complete", "sistema_completo_integrado.py", "python"),
            ("8", "Next.js Dashboard (Dev)", "next dev", "node", "nextjs-app"),
            (
                "9",
                "Next.js Dashboard (Production)",
                "next build && next start",
                "node",
                "nextjs-app",
            ),
            ("a", "Full Stack (API + Dashboard)", self._run_fullstack, "custom"),
            ("0", "Exit", None, None),
        ]

        print(f"{Colors.BOLD}Execution Modes:{Colors.ENDC}\n")
        for num, name, _, _, *extra in modes:
            print(f"  {Colors.OKCYAN}{num}.{Colors.ENDC} {name}")

        print(f"\n{Colors.BOLD}Development Tools:{Colors.ENDC}\n")
        dev_tools = [
            ("s", "System Status", self._show_status),
            ("t", "Run Tests", self._run_tests),
            ("c", "Check Configuration", self._check_config),
            ("r", "Reset Setup", self._reset_setup),
            ("l", "View Logs", self._view_logs),
        ]

        for key, name, _ in dev_tools:
            print(f"  {Colors.OKCYAN}{key}.{Colors.ENDC} {name}")

        return modes, dev_tools

    def _run_fullstack(self):
        """Run API server and dashboard together"""
        print_header("Starting Full Stack System")

        # Start API server in background
        print_info("Starting API server...")
        try:
            api_log = self.log_dir / "api_server.log"
            with open(api_log, "w", encoding="utf-8") as log_file:
                api_process = subprocess.Popen(
                    [self.python_cmd, "api_server.py"],
                    cwd=self.root_dir,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
            self.background_processes.append(api_process)
            print_success(f"API server started (PID: {api_process.pid})")
            print_info(f"API server logs: {api_log}")

            # Wait for API to be ready
            try:
                import requests

                max_attempts = 30
                for i in range(max_attempts):
                    try:
                        response = requests.get(
                            "http://localhost:8000/health", timeout=2
                        )
                        if response.status_code == 200:
                            print_success("API server is ready")
                            break
                    except:
                        if i < max_attempts - 1:
                            time.sleep(1)
                        else:
                            print_warning("API server may not be ready yet")
            except ImportError:
                print_warning("requests module not available, skipping health check")
        except Exception as e:
            print_error(f"Failed to start API server: {e}")
            self.logger.error("Failed to start API server", exc_info=True)
            return

        # Start Next.js dashboard
        if self.node_cmd:
            print_info("Starting Next.js dashboard...")
            nextjs_dir = self.root_dir / "nextjs-app"
            if not nextjs_dir.exists():
                nextjs_dir = self.root_dir

            try:
                if self.production:
                    # Production: build then start
                    print_info("Building Next.js application...")
                    subprocess.run(
                        [self.npm_cmd, "run", "build"], cwd=nextjs_dir, check=True
                    )
                    print_success("Build complete, starting production server...")
                    subprocess.run([self.npm_cmd, "run", "start"], cwd=nextjs_dir)
                else:
                    # Development
                    print_info("Starting Next.js development server...")
                    print_info("Dashboard will be available at http://localhost:3000")
                    subprocess.run([self.npm_cmd, "run", "dev"], cwd=nextjs_dir)
            except KeyboardInterrupt:
                print_warning("\nShutting down...")
            except Exception as e:
                print_error(f"Failed to start dashboard: {e}")
                self.logger.error("Failed to start dashboard", exc_info=True)
        else:
            print_warning("Node.js not found, skipping dashboard")

        # Cleanup on exit
        self._cleanup_processes()

    def _show_status(self):
        """Show system status"""
        print_header("System Status")

        # Check Python modules
        critical_modules = ["openai", "fastapi", "pymongo", "uvicorn", "dotenv"]
        print(f"\n{Colors.BOLD}Python Modules:{Colors.ENDC}")
        for module in critical_modules:
            try:
                __import__(module)
                print_success(f"  {module}")
            except ImportError:
                print_error(f"  {module} (missing)")

        # Check environment
        print(f"\n{Colors.BOLD}Environment:{Colors.ENDC}")
        env_file = self.root_dir / ".env"
        if env_file.exists():
            env_content = env_file.read_text()
            has_openai = "OPENAI_API_KEY" in env_content and "your-" not in env_content
            has_mongo = "MONGODB_URI" in env_content
            print_success("  .env file exists")
            (
                print_success("  OPENAI_API_KEY configured")
                if has_openai
                else print_warning("  OPENAI_API_KEY not configured")
            )
            (
                print_success("  MONGODB_URI configured")
                if has_mongo
                else print_warning("  MONGODB_URI not configured")
            )
        else:
            print_error("  .env file missing")

        # Check services
        print(f"\n{Colors.BOLD}Services:{Colors.ENDC}")
        # Check MongoDB
        try:
            import socket

            try:
                with socket.create_connection(("localhost", 27017), timeout=2):
                    print_success("  MongoDB: Connected")
            except (socket.error, OSError, ConnectionRefusedError):
                print_warning("  MongoDB: Not connected (optional)")
        except ImportError:
            print_warning("  MongoDB: socket not available")

        # Check API server
        try:
            import requests

            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    print_success("  API Server: Running")
                else:
                    print_warning("  API Server: Not responding")
            except (requests.RequestException, ConnectionError):
                print_warning("  API Server: Not running")
        except ImportError:
            print_warning("  API Server: requests not installed")

    def _run_tests(self):
        """Run system tests"""
        print_header("Running Tests")
        print_info("Test functionality coming soon")
        # Future: Implement test runner using pytest

    def _check_config(self):
        """Check configuration"""
        self._show_status()

    def _reset_setup(self):
        """Reset setup"""
        print_header("Resetting Setup")
        response = input("Are you sure you want to reset setup? (yes/no): ")
        if response.lower() == "yes":
            # Remove .env and re-run setup
            env_file = self.root_dir / ".env"
            if env_file.exists():
                env_file.unlink()
                print_success(".env removed")
            self.setup_environment()

    def _view_logs(self):
        """View logs"""
        print_header("View Logs")
        log_file = self.log_dir / "launcher.log"
        if log_file.exists():
            print_info(f"Showing last 50 lines of {log_file}")
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for line in lines[-50:]:
                        print(line.rstrip())
            except Exception as e:
                print_error(f"Could not read log file: {e}")
        else:
            print_warning("No log file found")

    def run(self, mode: Optional[str] = None):
        """Run the launcher"""
        # Check prerequisites
        if not self.check_prerequisites():
            print_error("Prerequisites check failed!")
            sys.exit(1)

        # Run setup
        if not self.setup_environment():
            print_warning("Setup completed with warnings. Continuing...")

        # If mode specified, run directly
        if mode:
            return self._execute_mode(mode)

        # Otherwise show menu
        while True:
            try:
                modes, dev_tools = self.show_menu()

                choice = (
                    input(f"\n{Colors.BOLD}Select option: {Colors.ENDC}")
                    .strip()
                    .lower()
                )

                if choice == "0":
                    print_success("Goodbye!")
                    self._cleanup_processes()
                    break

                # Check dev tools
                handled = False
                for key, name, func in dev_tools:
                    if choice == key:
                        func()
                        input("\nPress Enter to continue...")
                        handled = True
                        break

                if handled:
                    continue

                # Check modes
                for num, name, script, script_type, *extra in modes:
                    if choice == num:
                        if script_type == "custom":
                            script()
                        else:
                            self._execute_mode((script, script_type, *extra))
                        break
                else:
                    print_error("Invalid option!")
            except KeyboardInterrupt:
                print_warning("\n\nInterrupted by user")
                self._cleanup_processes()
                break
            except Exception as e:
                print_error(f"Error: {e}")
                self.logger.error("Error in menu loop", exc_info=True)
                input("\nPress Enter to continue...")

    def _execute_mode(self, mode_info):
        """Execute a specific mode"""
        try:
            if isinstance(mode_info, tuple):
                script, script_type, *extra = mode_info
                if script_type == "python":
                    script_path = self.root_dir / script
                    if not script_path.exists():
                        print_error(f"Script not found: {script}")
                        return
                    print_header(f"Starting: {script}")
                    try:
                        subprocess.run(
                            [self.python_cmd, str(script_path)], cwd=self.root_dir
                        )
                    except KeyboardInterrupt:
                        print_warning("\nInterrupted by user")
                elif script_type == "node":
                    if not self.node_cmd:
                        print_error("Node.js not found!")
                        return
                    node_dir = extra[0] if extra else None
                    work_dir = self.root_dir / node_dir if node_dir else self.root_dir
                    if not work_dir.exists():
                        print_error(f"Directory not found: {work_dir}")
                        return
                    print_header(f"Starting: {script}")
                    # Parse command
                    if " && " in script:
                        commands = script.split(" && ")
                        for cmd in commands:
                            parts = cmd.strip().split()
                            subprocess.run(
                                [self.npm_cmd, "run"] + parts[1:], cwd=work_dir
                            )
                    else:
                        parts = script.split()
                        subprocess.run([self.npm_cmd, "run"] + parts[1:], cwd=work_dir)
            else:
                mode_info()
        except KeyboardInterrupt:
            print_warning("\nInterrupted by user")
        except Exception as e:
            print_error(f"Error executing mode: {e}")
            self.logger.error("Error executing mode", exc_info=True)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Unified Launcher for BMC Chatbot System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python unified_launcher.py                    # Show menu
  python unified_launcher.py --mode chat        # Run interactive chatbot
  python unified_launcher.py --mode api         # Run API server
  python unified_launcher.py --mode fullstack   # Run API + Dashboard
  python unified_launcher.py --setup-only       # Only run setup
  python unified_launcher.py --skip-setup       # Skip setup steps
        """,
    )
    parser.add_argument(
        "--mode",
        choices=[
            "chat",
            "api",
            "simulator",
            "dashboard",
            "fullstack",
            "agent",
            "system",
        ],
        help="Run specific mode directly (skips menu)",
    )
    parser.add_argument(
        "--setup-only", action="store_true", help="Only run setup, don't start anything"
    )
    parser.add_argument(
        "--skip-setup",
        action="store_true",
        help="Skip setup steps (assume already configured)",
    )
    parser.add_argument(
        "--production", action="store_true", help="Production mode (optimized settings)"
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Development mode (verbose logging, hot reload)",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Custom API server port (default: 8000)"
    )

    args = parser.parse_args()

    launcher = UnifiedLauncher(
        skip_setup=args.skip_setup, production=args.production, dev=args.dev
    )

    if args.setup_only:
        launcher.check_prerequisites()
        launcher.setup_environment()
        return

    # Map mode arguments
    mode_map = {
        "chat": ("chat_interactivo.py", "python"),
        "api": ("api_server.py", "python"),
        "simulator": ("simulate_chat.py", "python"),
        "dashboard": ("next dev", "node", "nextjs-app"),
        "fullstack": launcher._run_fullstack,
        "agent": ("automated_agent_system.py", "python"),
        "system": ("sistema_completo_integrado.py", "python"),
    }

    if args.mode:
        mode_info = mode_map.get(args.mode)
        if mode_info:
            launcher._execute_mode(mode_info)
        else:
            launcher.run()
    else:
        launcher.run()


if __name__ == "__main__":
    main()
