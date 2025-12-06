#!/usr/bin/env python3
"""
Service Health - Health checks de servicios.
Fase -1: Validación y Testing Base
"""

from system.validation.health_checker import HealthChecker
from typing import Dict, Any


class ServiceHealth:
    """Maneja health checks de servicios específicos."""
    
    def __init__(self, health_checker: HealthChecker):
        self.checker = health_checker
    
    def check_service(self, service_name: str) -> Dict[str, Any]:
        """Realiza health check de un servicio específico."""
        # Service-specific health checks
        if service_name == "state_manager":
            return self._check_state_manager()
        elif service_name == "context_service":
            return self._check_context_service()
        elif service_name == "backup_service":
            return self._check_backup_service()
        else:
            return {
                "status": "unknown",
                "message": f"Unknown service: {service_name}"
            }
    
    def _check_state_manager(self) -> Dict[str, Any]:
        """Health check del StateManager."""
        try:
            from system.context.state_manager import StateManager
            sm = StateManager()
            phases = sm.get_all_phases()
            return {
                "status": "healthy",
                "phases_tracked": len(phases)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def _check_context_service(self) -> Dict[str, Any]:
        """Health check del ContextService."""
        try:
            from system.context.context_service import ContextService
            cs = ContextService()
            return {
                "status": "healthy",
                "agents": len(cs.context.get("agents", {}))
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def _check_backup_service(self) -> Dict[str, Any]:
        """Health check del servicio de backup."""
        backup_dir = Path("system/backup/backups")
        if backup_dir.exists():
            return {
                "status": "healthy",
                "backups_available": len(list(backup_dir.glob("*.json")))
            }
        return {
            "status": "degraded",
            "message": "Backup directory not found"
        }

