"""
Base Phase Executor
Abstract base class for phase executors
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

# Add orchestrator parent to path for imports
orchestrator_dir = Path(__file__).parent.parent
if str(orchestrator_dir) not in sys.path:
    sys.path.insert(0, str(orchestrator_dir))

# Import with relative path handling
try:
    from scripts.orchestrator.state_manager import StateManager
except ImportError:
    # Fallback for direct execution
    sys.path.insert(0, str(orchestrator_dir.parent.parent))
    from scripts.orchestrator.state_manager import StateManager


class BaseExecutor(ABC):
    """Base class for phase executors"""

    def __init__(self, phase: int, state_manager: StateManager):
        self.phase = phase
        self.state_manager = state_manager
        self.outputs: List[str] = []
        self.errors: List[str] = []

    @abstractmethod
    def execute(self) -> List[str]:
        """
        Execute phase tasks
        Returns: list of output file paths
        """
        pass

    def run_script(self, script_path: str, args: List[str] = None,
                   cwd: Optional[str] = None) -> tuple[bool, str]:
        """
        Run a Python script
        Returns: (success, output_message)
        """
        if args is None:
            args = []

        script = Path(script_path)
        if not script.exists():
            return False, f"Script not found: {script_path}"

        try:
            cmd = [sys.executable, str(script)] + args
            result = subprocess.run(
                cmd,
                cwd=cwd or Path.cwd(),
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                error_msg = f"Script failed with exit code {result.returncode}\n{result.stderr}"
                return False, error_msg

        except subprocess.TimeoutExpired:
            return False, "Script execution timed out after 1 hour"
        except Exception as e:
            return False, f"Error running script: {str(e)}"

    def collect_outputs(self) -> List[str]:
        """Collect all outputs from phase execution"""
        return self.outputs

    def add_output(self, output_path: str) -> None:
        """Add output file path"""
        if output_path not in self.outputs:
            self.outputs.append(output_path)
            self.state_manager.add_phase_output(self.phase, output_path)

    def add_error(self, error: str) -> None:
        """Add error message"""
        self.errors.append(error)
        self.state_manager.add_phase_error(self.phase, error)

    def ensure_output_dir(self, dir_path: str) -> Path:
        """Ensure output directory exists"""
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def log_info(self, message: str) -> None:
        """Log info message"""
        print(f"[Phase {self.phase}] INFO: {message}")

    def log_error(self, message: str) -> None:
        """Log error message"""
        print(f"[Phase {self.phase}] ERROR: {message}")
        self.add_error(message)

    def log_success(self, message: str) -> None:
        """Log success message"""
        print(f"[Phase {self.phase}] SUCCESS: {message}")

