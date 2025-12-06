"""
Phase Execution Timeout Implementation
Prevents phases from getting stuck indefinitely
"""

import signal
from contextlib import contextmanager
from typing import Optional
from datetime import datetime


class PhaseTimeoutError(Exception):
    """Raised when phase execution exceeds timeout"""
    pass


@contextmanager
def phase_timeout(phase: int, timeout_seconds: int = 3600):
    """
    Context manager for phase execution timeout
    
    Args:
        phase: Phase number
        timeout_seconds: Maximum execution time in seconds (default: 1 hour)
    
    Raises:
        PhaseTimeoutError: If execution exceeds timeout
    """
    def timeout_handler(signum, frame):
        raise PhaseTimeoutError(
            f"Phase {phase} execution exceeded timeout of {timeout_seconds} seconds"
        )
    
    # Set up signal handler (Unix only)
    if hasattr(signal, 'SIGALRM'):
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)
        try:
            yield
        finally:
            signal.alarm(0)  # Cancel timeout
            signal.signal(signal.SIGALRM, old_handler)  # Restore old handler
    else:
        # Windows doesn't support SIGALRM, use threading timer instead
        import threading
        
        def timeout():
            raise PhaseTimeoutError(
                f"Phase {phase} execution exceeded timeout of {timeout_seconds} seconds"
            )
        
        timer = threading.Timer(timeout_seconds, timeout)
        timer.start()
        try:
            yield
        finally:
            timer.cancel()


def get_phase_timeout(phase: int, default_timeout: int = 3600) -> int:
    """
    Get timeout for a specific phase
    
    Some phases might need longer timeouts than others.
    This allows phase-specific timeout configuration.
    """
    # Phase-specific timeouts (in seconds)
    phase_timeouts = {
        0: 1800,   # 30 minutes for discovery
        1: 3600,   # 1 hour for analysis
        2: 2400,   # 40 minutes
        # Add more as needed
    }
    
    return phase_timeouts.get(phase, default_timeout)

