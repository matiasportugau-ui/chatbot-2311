#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Health Check System
Monitors system health and provides health check endpoints
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health check status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheck:
    """Individual health check"""
    
    def __init__(
        self,
        name: str,
        check_func,
        timeout: float = 5.0,
        critical: bool = False
    ):
        """
        Initialize health check
        
        Args:
            name: Check name
            check_func: Async function that returns (status, message)
            timeout: Timeout in seconds
            critical: Is this a critical check
        """
        self.name = name
        self.check_func = check_func
        self.timeout = timeout
        self.critical = critical
        self.last_check_time: Optional[datetime] = None
        self.last_status: Optional[HealthStatus] = None
        self.last_message: Optional[str] = None
        self.failure_count: int = 0
    
    async def run(self) -> Dict[str, Any]:
        """
        Run health check
        
        Returns:
            Check result with status and details
        """
        try:
            # Run check with timeout
            status, message = await asyncio.wait_for(
                self.check_func(),
                timeout=self.timeout
            )
            
            self.last_check_time = datetime.utcnow()
            self.last_status = status
            self.last_message = message
            
            # Reset failure count on success
            if status == HealthStatus.HEALTHY:
                self.failure_count = 0
            else:
                self.failure_count += 1
            
            return {
                'name': self.name,
                'status': status,
                'message': message,
                'critical': self.critical,
                'timestamp': self.last_check_time.isoformat(),
                'failure_count': self.failure_count
            }
        
        except asyncio.TimeoutError:
            self.failure_count += 1
            self.last_status = HealthStatus.UNHEALTHY
            self.last_message = f"Health check timed out after {self.timeout}s"
            
            return {
                'name': self.name,
                'status': HealthStatus.UNHEALTHY,
                'message': self.last_message,
                'critical': self.critical,
                'timestamp': datetime.utcnow().isoformat(),
                'failure_count': self.failure_count
            }
        
        except Exception as e:
            self.failure_count += 1
            self.last_status = HealthStatus.UNHEALTHY
            self.last_message = f"Health check failed: {str(e)}"
            
            logger.error(f"Health check '{self.name}' failed: {e}")
            
            return {
                'name': self.name,
                'status': HealthStatus.UNHEALTHY,
                'message': self.last_message,
                'critical': self.critical,
                'timestamp': datetime.utcnow().isoformat(),
                'failure_count': self.failure_count
            }


class HealthChecker:
    """Health check system"""
    
    def __init__(self):
        """Initialize health checker"""
        self.checks: List[HealthCheck] = []
        self.start_time = datetime.utcnow()
    
    def register_check(
        self,
        name: str,
        check_func,
        timeout: float = 5.0,
        critical: bool = False
    ):
        """
        Register a health check
        
        Args:
            name: Check name
            check_func: Async function that returns (status, message)
            timeout: Timeout in seconds
            critical: Is this a critical check
        """
        check = HealthCheck(name, check_func, timeout, critical)
        self.checks.append(check)
        logger.info(f"Registered health check: {name} (critical={critical})")
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """
        Run all health checks
        
        Returns:
            Overall health status with details
        """
        # Run all checks concurrently
        check_results = await asyncio.gather(
            *[check.run() for check in self.checks],
            return_exceptions=True
        )
        
        # Handle exceptions
        results = []
        for i, result in enumerate(check_results):
            if isinstance(result, Exception):
                results.append({
                    'name': self.checks[i].name,
                    'status': HealthStatus.UNHEALTHY,
                    'message': f"Check crashed: {str(result)}",
                    'critical': self.checks[i].critical
                })
            else:
                results.append(result)
        
        # Determine overall status
        critical_unhealthy = any(
            r['status'] == HealthStatus.UNHEALTHY and r['critical']
            for r in results
        )
        
        any_unhealthy = any(
            r['status'] == HealthStatus.UNHEALTHY
            for r in results
        )
        
        any_degraded = any(
            r['status'] == HealthStatus.DEGRADED
            for r in results
        )
        
        if critical_unhealthy:
            overall_status = HealthStatus.UNHEALTHY
        elif any_unhealthy or any_degraded:
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY
        
        # Calculate uptime
        uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            'status': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'uptime_seconds': uptime_seconds,
            'checks': results,
            'summary': {
                'total': len(results),
                'healthy': sum(1 for r in results if r['status'] == HealthStatus.HEALTHY),
                'degraded': sum(1 for r in results if r['status'] == HealthStatus.DEGRADED),
                'unhealthy': sum(1 for r in results if r['status'] == HealthStatus.UNHEALTHY)
            }
        }
    
    async def check_database(self, db_connection) -> tuple[HealthStatus, str]:
        """Check database connectivity"""
        try:
            # Ping database
            await db_connection.admin.command('ping')
            return HealthStatus.HEALTHY, "Database connection OK"
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"Database error: {str(e)}"
    
    async def check_ai_service(self, openai_client) -> tuple[HealthStatus, str]:
        """Check AI service connectivity"""
        try:
            # Simple API call to test connectivity
            response = await openai_client.models.list()
            return HealthStatus.HEALTHY, "AI service OK"
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"AI service error: {str(e)}"
    
    async def check_vector_db(self, qdrant_client) -> tuple[HealthStatus, str]:
        """Check vector database connectivity"""
        try:
            # Check Qdrant health
            health = await qdrant_client.get_collections()
            return HealthStatus.HEALTHY, f"Vector DB OK ({len(health.collections)} collections)"
        except Exception as e:
            return HealthStatus.DEGRADED, f"Vector DB unavailable: {str(e)}"
    
    async def check_disk_space(self, threshold_percent: float = 90.0) -> tuple[HealthStatus, str]:
        """Check disk space"""
        try:
            import shutil
            stat = shutil.disk_usage('/')
            used_percent = (stat.used / stat.total) * 100
            
            if used_percent >= threshold_percent:
                return HealthStatus.DEGRADED, f"Disk space low: {used_percent:.1f}% used"
            else:
                return HealthStatus.HEALTHY, f"Disk space OK: {used_percent:.1f}% used"
        except Exception as e:
            return HealthStatus.DEGRADED, f"Cannot check disk space: {str(e)}"
    
    async def check_memory(self, threshold_percent: float = 90.0) -> tuple[HealthStatus, str]:
        """Check memory usage"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            if memory.percent >= threshold_percent:
                return HealthStatus.DEGRADED, f"Memory usage high: {memory.percent:.1f}%"
            else:
                return HealthStatus.HEALTHY, f"Memory OK: {memory.percent:.1f}% used"
        except Exception as e:
            return HealthStatus.DEGRADED, f"Cannot check memory: {str(e)}"


# Singleton instance
_health_checker = None


def get_health_checker() -> HealthChecker:
    """Get singleton health checker instance"""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


# Example usage
async def setup_health_checks(db_connection, openai_client, qdrant_client=None):
    """
    Setup standard health checks
    
    Args:
        db_connection: MongoDB connection
        openai_client: OpenAI client
        qdrant_client: Qdrant client (optional)
    """
    checker = get_health_checker()
    
    # Register checks
    checker.register_check(
        "database",
        lambda: checker.check_database(db_connection),
        timeout=5.0,
        critical=True
    )
    
    checker.register_check(
        "ai_service",
        lambda: checker.check_ai_service(openai_client),
        timeout=10.0,
        critical=True
    )
    
    if qdrant_client:
        checker.register_check(
            "vector_db",
            lambda: checker.check_vector_db(qdrant_client),
            timeout=5.0,
            critical=False
        )
    
    checker.register_check(
        "disk_space",
        lambda: checker.check_disk_space(threshold_percent=90.0),
        timeout=2.0,
        critical=False
    )
    
    checker.register_check(
        "memory",
        lambda: checker.check_memory(threshold_percent=90.0),
        timeout=2.0,
        critical=False
    )
    
    logger.info("Health checks configured")
