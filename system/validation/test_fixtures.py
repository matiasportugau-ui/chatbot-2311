#!/usr/bin/env python3
"""
Test Fixtures - Fixtures y mocks para testing.
Fase -1: Validación y Testing Base
"""

from typing import Dict, Any, Callable
from unittest.mock import Mock, MagicMock


class TestFixtures:
    """Provee fixtures y mocks para tests."""
    
    @staticmethod
    def create_mock_state() -> Dict[str, Any]:
        """Crea un mock del estado."""
        return {
            "phases": {},
            "tasks": {},
            "checkpoints": []
        }
    
    @staticmethod
    def create_mock_context() -> Dict[str, Any]:
        """Crea un mock del contexto."""
        return {
            "agents": {},
            "shared_data": {},
            "events": []
        }
    
    @staticmethod
    def create_mock_agent(name: str) -> Mock:
        """Crea un mock de un agente."""
        agent = Mock()
        agent.name = name
        agent.execute = MagicMock(return_value={"success": True})
        return agent
    
    @staticmethod
    def create_mock_output(phase: int) -> Dict[str, Any]:
        """Crea un mock de output de fase."""
        return {
            "phase": phase,
            "status": "completed",
            "outputs": [f"consolidation/phase_{phase}/output.json"]
        }

