#!/usr/bin/env python3
"""
Unified Launcher for BMC Chatbot System
Single entry point for all system operations
"""

import argparse
import logging
import platform
import signal
import subprocess
import sys
import time
from pathlib import Path




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
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")


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
        self,
        skip_setup: bool = False,
        production: bool = False,
        dev: bool = False,
        non_interactive: bool = False
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

        self.non_interactive = non_interactive
        self.background_processes: list[subprocess.Popen] = []


        # Setup logging
        self.log_dir = self.root_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)
        self._setup_logging()


        # Find executables (critical for system operation)
        self.python_cmd = self._find_python()
        self.node_cmd = self._find_node()
        self.npm_cmd = self._find_npm()

        # Validate Python is available (critical requirement)
        if not self.python_cmd:
            error_msg = (
                "Python 3.11+ is required but not found. Please install Python 3.11 or higher."
            )
            print_error(error_msg)
            if self.logger:
                self.logger.error(error_msg)
            raise RuntimeError(error_msg)

        # Signal handlers for cleanup (only on Unix-like systems)
        if hasattr(signal, "SIGINT"):
            try:
                signal.signal(signal.SIGINT, self._signal_handler)
                signal.signal(signal.SIGTERM, self._signal_handler)
            except (ValueError, OSError) as e:
                # Signal handlers may not work in all contexts (e.g., threads)
                self.logger.warning(f"Could not set signal handlers: {e}")


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

        if not self.background_processes:
            return

        self.logger.info(f"Cleaning up {len(self.background_processes)} background process(es)")
        for process in self.background_processes:
            try:
                if process.poll() is None:  # Process is still running
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                        self.logger.debug(f"Process {process.pid} terminated gracefully")
                    except subprocess.TimeoutExpired:
                        self.logger.warning(f"Process {process.pid} did not terminate, killing...")
                        process.kill()
                        process.wait()
            except (OSError, ProcessLookupError) as e:
                # Process may have already terminated
                self.logger.debug(f"Process cleanup: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error during process cleanup: {e}")
        self.background_processes.clear()

    def _find_python(self) -> str | None:
        """Find Python executable with version 3.11+"""

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

    def _find_node(self) -> str | None:
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

    def _find_npm(self) -> str | None:
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


    def _auto_detect_env_vars(self) -> dict[str, str]:
        """Auto-detect environment variables from system environment"""
        import os

        detected = {}
        # Check system environment variables first (highest priority)
        env_vars_to_check = [
            "OPENAI_API_KEY",
            "MONGODB_URI",
            "NEXTAUTH_SECRET",
            "NEXTAUTH_URL",
            "WHATSAPP_ACCESS_TOKEN",
            "WHATSAPP_PHONE_NUMBER_ID",
            "WHATSAPP_VERIFY_TOKEN",
            "MELI_ACCESS_TOKEN",
            "MELI_SELLER_ID",
            "MERCADO_LIBRE_WEBHOOK_SECRET",
        ]

        for var in env_vars_to_check:
            value = os.environ.get(var)
            if value and value.strip() and not value.startswith("your-"):
                detected[var] = value
                self.logger.debug(f"Auto-detected {var} from system environment")

        return detected

    def _auto_generate_secrets(self) -> dict[str, str]:
        """Auto-generate secrets and tokens"""
        import random
        import secrets
        import string

        generated = {}

        # Generate NEXTAUTH_SECRET if not provided
        if "NEXTAUTH_SECRET" not in generated:
            generated["NEXTAUTH_SECRET"] = secrets.token_urlsafe(32)

        # Generate WhatsApp verify token if not provided
        if "WHATSAPP_VERIFY_TOKEN" not in generated:
            chars = string.ascii_letters + string.digits + "-_"
            generated["WHATSAPP_VERIFY_TOKEN"] = "".join(random.choice(chars) for _ in range(32))

        # Generate Mercado Libre webhook secret if not provided
        if "MERCADO_LIBRE_WEBHOOK_SECRET" not in generated:
            generated["MERCADO_LIBRE_WEBHOOK_SECRET"] = secrets.token_urlsafe(24)

        return generated

    def _get_sensible_defaults(self) -> dict[str, str]:
        """Get sensible default values for optional variables"""
        defaults = {
            "MONGODB_URI": "mongodb://localhost:27017/bmc_chat",
            "NEXTAUTH_URL": "http://localhost:3000",
            "PY_CHAT_SERVICE_URL": "http://localhost:8000",
            "NEXT_PUBLIC_API_URL": "http://localhost:3001/api",
            "NEXT_PUBLIC_WS_URL": "ws://localhost:3001/ws",
            "OPENAI_MODEL": "gpt-4o-mini",
            "MERCADO_LIBRE_AUTH_URL": "https://auth.mercadolibre.com.uy",
            "MERCADO_LIBRE_API_URL": "https://api.mercadolibre.com",
            "N8N_WEBHOOK_URL_EXTERNAL": "http://localhost:5678/webhook/whatsapp",
        }
        return defaults

    def _auto_setup(self) -> tuple[dict[str, str], list[str]]:
        """
        Auto-setup environment variables.
        Returns: (env_updates, missing_required)
        """
        env_file = self.root_dir / ".env"
        env_example = self.root_dir / "env.example"
        env_updates = {}
        missing_required = []

        # Step 1: Auto-detect from system environment
        detected = self._auto_detect_env_vars()
        env_updates.update(detected)
        if detected:
            print_info(f"Auto-detected {len(detected)} variable(s) from system environment")

        # Step 2: Load existing .env file
        env_content = ""
        if env_file.exists():
            env_content = env_file.read_text(encoding="utf-8")
        elif env_example.exists():
            print_info("Creating .env from env.example...")
            env_content = env_example.read_text(encoding="utf-8")

        # Step 3: Extract existing values from .env (don't override detected)
        if env_content:
            for line in env_content.split("\n"):
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    # Only use if not placeholder and not already detected
                    if (
                        key not in env_updates
                        and value
                        and not value.startswith("your-")
                        and value not in ["", '""', "''"]
                    ):
                        env_updates[key] = value

        # Step 4: Auto-generate secrets
        generated = self._auto_generate_secrets()
        for key, value in generated.items():
            if key not in env_updates:
                env_updates[key] = value
                print_success(f"Auto-generated {key}")

        # Step 5: Apply sensible defaults for optional variables
        defaults = self._get_sensible_defaults()
        for key, value in defaults.items():
            if key not in env_updates:
                env_updates[key] = value

        # Step 6: Check for required variables
        if "OPENAI_API_KEY" not in env_updates or not env_updates["OPENAI_API_KEY"]:
            missing_required.append("OPENAI_API_KEY")

        return env_updates, missing_required


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
            ("Validating environment", self._validate_environment),
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


        # Show configuration summary
        if not self.skip_setup:
            print_header("Setup Summary")
            env_file = self.root_dir / ".env"
            if env_file.exists():
                try:
                    env_updates, missing = self._auto_setup()
                    if env_updates:
                        print_info(f"✓ Auto-configured {len(env_updates)} variable(s)")
                    if missing:
                        print_warning(
                            f"⚠ {len(missing)} required variable(s) still need configuration"
                        )
                        if not self.non_interactive:
                            print_info("Run setup again or configure manually in .env file")
                except Exception as e:
                    self.logger.debug(f"Could not show setup summary: {e}")


        # Optional: Validate WhatsApp and import n8n workflows
        if not self.skip_setup:
            self._validate_whatsapp()
            self._import_n8n_workflows()

        # Optional: Run integration tests
        if self.dev:  # Only in dev mode to avoid slowing down production
            self._run_integration_tests()

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


        # Update env_content with auto-detected/generated values
        env_updated = False
        lines = env_content.split("\n")
        updated_lines = []
        existing_keys = set()

        for line in lines:
            line_stripped = line.strip()
            # Skip comments and empty lines
            if not line_stripped or line_stripped.startswith("#"):
                updated_lines.append(line)
                continue

            # Parse existing key=value pairs
            if "=" in line_stripped and not line_stripped.startswith("#"):
                key = line_stripped.split("=", 1)[0].strip()
                existing_keys.add(key)

                # Replace if we have an update for this key
                if key in env_updates:
                    updated_lines.append(f"{key}={env_updates[key]}")
                    env_updated = True
                    # Remove from updates so we can add remaining ones
                    del env_updates[key]
                else:
                    # Keep original line if no update
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        # Add any new variables that weren't in the file
        for key, value in env_updates.items():
            if key not in existing_keys:
                updated_lines.append(f"{key}={value}")
                env_updated = True

        env_content = "\n".join(updated_lines)
        if not env_content.endswith("\n"):
            env_content += "\n"

        # Handle missing required variables
        if missing_required:
            if self.non_interactive:
                print_error(
                    f"Required variables missing in non-interactive mode: {', '.join(missing_required)}"
                )
                print_info("Set them as system environment variables or in .env file")
                return False
            else:
                # Only prompt for OPENAI_API_KEY if missing
                if "OPENAI_API_KEY" in missing_required:
                    print_warning("OPENAI_API_KEY is missing or not configured")
                    print_info("Options:")
                    print_info("  1. Set OPENAI_API_KEY environment variable")
                    print_info("  2. Add it to .env file")
                    print_info("  3. Get API key from: https://platform.openai.com/api-keys")

                    # Try interactive setup
                    config_script = self.root_dir / "configurar_entorno.py"
                    if config_script.exists():
                        try:
                            import importlib.util

                            spec = importlib.util.spec_from_file_location(
                                "configurar_entorno", config_script
                            )
                            if spec and spec.loader:
                                module = importlib.util.module_from_spec(spec)
                                spec.loader.exec_module(module)
                                if hasattr(module, "main"):
                                    print_info("Running interactive OpenAI API key setup...")
                                    module.main()
                                    # Reload to get the new value
                                    env_updates, _ = self._auto_setup()
                                    if "OPENAI_API_KEY" in env_updates:
                                        # Update the content again
                                        env_content = re.sub(
                                            r"OPENAI_API_KEY\s*=\s*.*",
                                            f"OPENAI_API_KEY={env_updates['OPENAI_API_KEY']}",
                                            env_content,
                                            flags=re.MULTILINE,
                                        )
                                        env_updated = True
                                        missing_required.remove("OPENAI_API_KEY")
                        except Exception as e:
                            self.logger.warning(f"Could not import configurar_entorno: {e}")

        # Save updated .env if changes were made
        if env_updated:
            try:
                env_file.write_text(env_content, encoding="utf-8")
                self.logger.info("Updated .env file with auto-detected/generated values")
                print_success("Environment file updated with auto-configuration")
            except (OSError, PermissionError) as e:
                print_error(f"Could not write .env file: {e}")
                return False

        # Show summary
        if env_updates:
            print_info(f"Auto-configured {len(env_updates)} environment variable(s)")

        # Return True if no required variables are missing
        return len(missing_required) == 0


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

                spec = importlib.util.spec_from_file_location("gestionar_servicios", gestion_script)
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
                print_info(f"Installing Node.js dependencies from {package_json.parent.name}...")
                try:
                    result = subprocess.run(
                        [self.npm_cmd, "install"],
                        cwd=package_json.parent,
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    print_success(f"Node.js dependencies installed in {package_json.parent.name}")
                    return True
                except subprocess.CalledProcessError as e:
                    print_warning(f"Failed to install Node.js dependencies: {e}")
                    return False

        return True  # No package.json found, not an error

    def _validate_environment(self) -> bool:
        """Validate environment variables comprehensively"""
        validator_script = self.root_dir / "scripts" / "validate_environment.py"
        if not validator_script.exists():
            print_warning("Environment validator not found, skipping validation")
            return True  # Not critical

        try:
            result = subprocess.run(
                [self.python_cmd, str(validator_script)],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print_success("Environment validation passed")
                return True
            else:
                print_warning("Environment validation found issues")
                # Show first few lines of output
                if result.stdout:
                    lines = result.stdout.split('\n')[:5]
                    for line in lines:
                        if line.strip():
                            print_info(f"  {line}")
                return True  # Continue anyway, user can fix later
        except Exception as e:
            self.logger.warning(f"Could not validate environment: {e}")
            return True  # Not critical

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
                    raise ImportError("Could not load verificar_sistema_completo module")

                if hasattr(module, "main"):
                    module.main()
                    return True
            except Exception as e:
                self.logger.warning(f"Could not verify system: {e}")
        return True

    def _validate_whatsapp(self) -> bool:
        """Validate WhatsApp credentials if configured"""
        whatsapp_validator = self.root_dir / "scripts" / "verify_whatsapp_credentials.py"
        if not whatsapp_validator.exists():
            return True  # Not critical

        # Check if WhatsApp is configured
        env_file = self.root_dir / ".env"
        if not env_file.exists():
            return True

        try:
            env_content = env_file.read_text()
            has_whatsapp = any(

                key in env_content and "your-" not in env_content.split(key)[1].split("\n")[0]

                for key in ["WHATSAPP_ACCESS_TOKEN", "WHATSAPP_PHONE_NUMBER_ID"]
            )

            if not has_whatsapp:
                return True  # Not configured, skip

            print_info("Validating WhatsApp credentials...")
            result = subprocess.run(
                [self.python_cmd, str(whatsapp_validator)],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print_success("WhatsApp credentials validated")
            else:
                print_warning("WhatsApp validation found issues (optional)")

            return True  # Not critical
        except Exception as e:
            self.logger.warning(f"Could not validate WhatsApp: {e}")
            return True

    def _import_n8n_workflows(self) -> bool:
        """Import n8n workflows if n8n is available"""
        n8n_importer = self.root_dir / "scripts" / "import_n8n_workflow.py"
        if not n8n_importer.exists():
            return True  # Not critical

        # Check if n8n is running
        try:
            import requests
            response = requests.get("http://localhost:5678/healthz", timeout=2)
            if response.status_code != 200:
                return True  # n8n not running, skip
        except Exception:
            return True  # Can't check, skip

        print_info("n8n detected. Import workflows? (y/n, default: n):")
        try:
            response = input("  > ").strip().lower()
            if response == 'y':
                print_info("Importing n8n workflows...")
                result = subprocess.run(
                    [self.python_cmd, str(n8n_importer)],
                    cwd=self.root_dir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode == 0:
                    print_success("n8n workflows imported")
                else:
                    print_warning("n8n workflow import had issues")
        except (EOFError, KeyboardInterrupt):
            print_info("Skipping n8n workflow import")

        return True  # Not critical

    def _run_integration_tests(self) -> bool:
        """Run integration tests after setup"""
        test_script = self.root_dir / "scripts" / "test_integration.py"
        if not test_script.exists():
            return True  # Not critical

        print_info("Running integration tests...")
        try:
            result = subprocess.run(
                [self.python_cmd, str(test_script)],
                cwd=self.root_dir,
                timeout=120
            )

            if result.returncode == 0:
                print_success("Integration tests passed")
                return True
            else:
                print_warning("Some integration tests failed (review output above)")
                return True  # Continue anyway
        except Exception as e:
            self.logger.warning(f"Could not run integration tests: {e}")
            return True  # Not critical

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
                        response = requests.get("http://localhost:8000/health", timeout=2)
                        if response.status_code == 200:
                            print_success("API server is ready")
                            break
                    except Exception:
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
                    subprocess.run([self.npm_cmd, "run", "build"], cwd=nextjs_dir, check=True)
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

    def _start_api_server_if_needed(self) -> bool:
        """Start API server automatically if not running"""
        api_server_file = self.root_dir / "api_server.py"
        if not api_server_file.exists():
            return False

        # Check if API server is already running
        try:
            import requests
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    return True  # Already running
            except (requests.RequestException, ConnectionError):
                pass  # Not running, continue to start it
        except ImportError:
            pass  # requests not available, try to start anyway

        # Start API server in background
        print_info("  Starting API Server automatically...")
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
            print_success(f"  API Server started (PID: {api_process.pid})")
            print_info(f"    Logs: {api_log}")

            # Wait for API to be ready (with timeout)
            try:
                import requests
                max_attempts = 15
                for i in range(max_attempts):
                    try:
                        time.sleep(1)  # Wait 1 second between attempts
                        response = requests.get("http://localhost:8000/health", timeout=2)
                        if response.status_code == 200:
                            print_success("  API Server is ready")
                            return True
                    except Exception:
                        if i < max_attempts - 1:
                            continue
                        else:
                            print_warning("  API Server started but may not be ready yet")
                            print_info("    Check logs if issues persist")
                            return True  # Started, even if not ready yet
            except ImportError:
                print_warning("  requests module not available, cannot verify API readiness")
                return True  # Started, but can't verify
        except Exception as e:
            print_error(f"  Failed to start API Server: {e}")
            self.logger.error("Failed to start API Server", exc_info=True)
            return False

        return True

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

        # Check environment with comprehensive validation
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

            # Run comprehensive validation
            validator_script = self.root_dir / "scripts" / "validate_environment.py"
            if validator_script.exists():
                print_info("  Running comprehensive validation...")
                try:
                    result = subprocess.run(
                        [self.python_cmd, str(validator_script)],
                        cwd=self.root_dir,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0:
                        print_success("  Environment validation: Passed")
                    else:
                        print_warning("  Environment validation: Issues found")
                        print_info("    Run: python scripts/validate_environment.py for details")
                except Exception:
                    pass
        else:
            print_error("  .env file missing")
            print_info("    Run: python scripts/setup_environment_wizard.py to create")

        # Check services
        print(f"\n{Colors.BOLD}Services:{Colors.ENDC}")
        # Check MongoDB
        try:
            import socket

            try:
                with socket.create_connection(("localhost", 27017), timeout=2):
                    print_success("  MongoDB: Connected")
            except (OSError, ConnectionRefusedError):
                print_warning("  MongoDB: Not connected (optional)")
        except ImportError:
            print_warning("  MongoDB: socket not available")

        # Check API server and start if needed
        api_running = False
        try:
            import requests

            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    print_success("  API Server: Running")
                    api_running = True
                else:
                    print_warning("  API Server: Not responding")
            except (requests.RequestException, ConnectionError):
                print_warning("  API Server: Not running")
        except ImportError:
            print_warning("  API Server: requests not installed")

        # Auto-start API server if not running
        if not api_running:
            if self._start_api_server_if_needed():
                # Re-check after starting
                time.sleep(2)
                try:
                    import requests
                    try:
                        response = requests.get("http://localhost:8000/health", timeout=2)
                        if response.status_code == 200:
                            print_success("  API Server: Running (auto-started)")
                        else:
                            print_warning("  API Server: Started but not responding yet")
                    except Exception:
                        print_info("  API Server: Starting... (check logs if issues persist)")
                except ImportError:
                    pass

        # Check n8n
        try:
            import requests
            try:
                response = requests.get("http://localhost:5678/healthz", timeout=2)
                if response.status_code == 200:
                    print_success("  n8n: Running")
                else:
                    print_warning("  n8n: Not responding")
            except (requests.RequestException, ConnectionError):
                print_warning("  n8n: Not running (optional)")
        except ImportError:
            pass

    def _run_tests(self):
        """Run system tests"""
        print_header("Running Tests")

        test_script = self.root_dir / "scripts" / "test_integration.py"
        if test_script.exists():
            print_info("Running integration tests...")
            try:
                subprocess.run(
                    [self.python_cmd, str(test_script)],
                    cwd=self.root_dir
                )
            except Exception as e:
                print_error(f"Error running tests: {e}")
        else:
            print_warning("Integration test script not found")
            print_info("Test functionality coming soon")

    def _check_config(self):
        """Check configuration"""
        print_header("Configuration Check")

        # Run comprehensive environment validation
        validator_script = self.root_dir / "scripts" / "validate_environment.py"
        if validator_script.exists():
            print_info("Running environment validation...")
            try:

                subprocess.run([self.python_cmd, str(validator_script)], cwd=self.root_dir)

            except Exception as e:
                print_error(f"Error running validation: {e}")
        else:
            print_warning("Environment validator not found")

        # Also show status
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
                with open(log_file, encoding="utf-8") as f:
                    lines = f.readlines()
                    for line in lines[-50:]:
                        print(line.rstrip())
            except Exception as e:
                print_error(f"Could not read log file: {e}")
        else:
            print_warning("No log file found")

    def run(self, mode: str | None = None):
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

                choice = input(f"\n{Colors.BOLD}Select option: {Colors.ENDC}").strip().lower()

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
                        subprocess.run([self.python_cmd, str(script_path)], cwd=self.root_dir)
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
                            subprocess.run([self.npm_cmd, "run"] + parts[1:], cwd=work_dir)
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
        skip_setup=args.skip_setup,
        production=args.production,
        dev=args.dev,
        non_interactive=False
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
