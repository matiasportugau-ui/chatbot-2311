#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cursor AI Code Tracking Service
Servicio para rastrear código generado por IA usando AI Code Tracking API
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

from cursor_api_client import CursorAPIClient

logger = logging.getLogger(__name__)


@dataclass
class AICommit:
    """Commit con código generado por IA"""
    commit_id: str
    repository: str
    author: str
    date: str
    message: str
    ai_lines: int
    total_lines: int
    ai_percentage: float
    files_changed: int


@dataclass
class AIChange:
    """Cambio específico generado por IA"""
    change_id: str
    commit_id: str
    file: str
    lines_added: int
    lines_deleted: int
    ai_lines: int
    model_used: Optional[str] = None


@dataclass
class CodeMetrics:
    """Métricas de código generado por IA"""
    period: str
    total_commits: int
    ai_commits: int
    ai_commit_percentage: float
    total_lines: int
    ai_lines: int
    ai_lines_percentage: float
    files_changed: int
    avg_ai_per_file: float


class CursorCodeTrackingService:
    """
    Servicio para rastrear código generado por IA
    Usa AI Code Tracking API de Cursor
    """
    
    def __init__(self, client: Optional[CursorAPIClient] = None):
        """
        Inicializa servicio de code tracking
        
        Args:
            client: Cliente de Cursor API (opcional)
        """
        self.client = client or CursorAPIClient()
    
    def get_ai_commits(
        self,
        repository: str,
        start_date: str = "7d",
        end_date: str = "today",
        limit: int = 100
    ) -> List[AICommit]:
        """
        Obtiene commits con código generado por IA
        
        Args:
            repository: Nombre del repositorio
            start_date: Fecha de inicio
            end_date: Fecha de fin
            limit: Límite de resultados
        
        Returns:
            Lista de commits con código IA
        """
        try:
            response = self.client.get(
                "/ai-code-tracking/commits",
                params={
                    "repository": repository,
                    "start_date": start_date,
                    "end_date": end_date,
                    "limit": limit
                }
            )
            
            commits = []
            for item in response.get("data", []):
                ai_lines = item.get("ai_lines", 0)
                total_lines = item.get("total_lines", 0)
                ai_percentage = (ai_lines / total_lines * 100) if total_lines > 0 else 0
                
                commits.append(AICommit(
                    commit_id=item.get("commit_id"),
                    repository=item.get("repository", repository),
                    author=item.get("author", "unknown"),
                    date=item.get("date"),
                    message=item.get("message", ""),
                    ai_lines=ai_lines,
                    total_lines=total_lines,
                    ai_percentage=ai_percentage,
                    files_changed=item.get("files_changed", 0)
                ))
            
            logger.info(f"Obtenidos {len(commits)} commits con código IA")
            return commits
        
        except Exception as e:
            logger.error(f"Error obteniendo commits con código IA: {e}")
            raise
    
    def get_ai_changes(
        self,
        commit_id: str
    ) -> List[AIChange]:
        """
        Obtiene cambios específicos de un commit
        
        Args:
            commit_id: ID del commit
        
        Returns:
            Lista de cambios generados por IA
        """
        try:
            response = self.client.get(
                "/ai-code-tracking/changes",
                params={"commit_id": commit_id}
            )
            
            changes = []
            for item in response.get("data", []):
                changes.append(AIChange(
                    change_id=item.get("change_id"),
                    commit_id=commit_id,
                    file=item.get("file"),
                    lines_added=item.get("lines_added", 0),
                    lines_deleted=item.get("lines_deleted", 0),
                    ai_lines=item.get("ai_lines", 0),
                    model_used=item.get("model_used")
                ))
            
            logger.info(f"Obtenidos {len(changes)} cambios para commit {commit_id}")
            return changes
        
        except Exception as e:
            logger.error(f"Error obteniendo cambios del commit {commit_id}: {e}")
            raise
    
    def get_code_metrics(
        self,
        repository: str,
        start_date: str = "30d",
        end_date: str = "today"
    ) -> CodeMetrics:
        """
        Obtiene métricas agregadas de código generado por IA
        
        Args:
            repository: Nombre del repositorio
            start_date: Fecha de inicio
            end_date: Fecha de fin
        
        Returns:
            Métricas de código IA
        """
        try:
            # Obtener todos los commits con código IA
            commits = self.get_ai_commits(
                repository=repository,
                start_date=start_date,
                end_date=end_date,
                limit=1000  # Obtener máximo posible
            )
            
            if not commits:
                return CodeMetrics(
                    period=f"{start_date} to {end_date}",
                    total_commits=0,
                    ai_commits=0,
                    ai_commit_percentage=0.0,
                    total_lines=0,
                    ai_lines=0,
                    ai_lines_percentage=0.0,
                    files_changed=0,
                    avg_ai_per_file=0.0
                )
            
            # Calcular métricas
            total_commits = len(commits)
            ai_commits = sum(1 for c in commits if c.ai_lines > 0)
            total_lines = sum(c.total_lines for c in commits)
            ai_lines = sum(c.ai_lines for c in commits)
            files_changed = sum(c.files_changed for c in commits)
            
            ai_commit_percentage = (ai_commits / total_commits * 100) if total_commits > 0 else 0
            ai_lines_percentage = (ai_lines / total_lines * 100) if total_lines > 0 else 0
            avg_ai_per_file = ai_lines / files_changed if files_changed > 0 else 0
            
            return CodeMetrics(
                period=f"{start_date} to {end_date}",
                total_commits=total_commits,
                ai_commits=ai_commits,
                ai_commit_percentage=ai_commit_percentage,
                total_lines=total_lines,
                ai_lines=ai_lines,
                ai_lines_percentage=ai_lines_percentage,
                files_changed=files_changed,
                avg_ai_per_file=avg_ai_per_file
            )
        
        except Exception as e:
            logger.error(f"Error obteniendo métricas de código: {e}")
            raise
    
    def get_contributor_stats(
        self,
        repository: str,
        start_date: str = "30d",
        end_date: str = "today"
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas por contribuidor
        
        Args:
            repository: Nombre del repositorio
            start_date: Fecha de inicio
            end_date: Fecha de fin
        
        Returns:
            Estadísticas por contribuidor
        """
        try:
            commits = self.get_ai_commits(
                repository=repository,
                start_date=start_date,
                end_date=end_date,
                limit=1000
            )
            
            # Agrupar por autor
            contributor_stats = {}
            for commit in commits:
                author = commit.author
                if author not in contributor_stats:
                    contributor_stats[author] = {
                        "commits": 0,
                        "ai_commits": 0,
                        "total_lines": 0,
                        "ai_lines": 0,
                        "files_changed": 0
                    }
                
                stats = contributor_stats[author]
                stats["commits"] += 1
                if commit.ai_lines > 0:
                    stats["ai_commits"] += 1
                stats["total_lines"] += commit.total_lines
                stats["ai_lines"] += commit.ai_lines
                stats["files_changed"] += commit.files_changed
            
            # Calcular porcentajes
            for author, stats in contributor_stats.items():
                stats["ai_commit_percentage"] = (
                    stats["ai_commits"] / stats["commits"] * 100
                    if stats["commits"] > 0 else 0
                )
                stats["ai_lines_percentage"] = (
                    stats["ai_lines"] / stats["total_lines"] * 100
                    if stats["total_lines"] > 0 else 0
                )
            
            return {
                "period": f"{start_date} to {end_date}",
                "contributors": contributor_stats
            }
        
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de contribuidores: {e}")
            raise


# Ejemplo de uso
if __name__ == "__main__":
    import json
    
    # Inicializar servicio
    service = CursorCodeTrackingService()
    
    # Obtener métricas de código
    try:
        metrics = service.get_code_metrics(
            repository="chatbot-2311",
            start_date="30d"
        )
        print("Code Metrics:")
        print(json.dumps(asdict(metrics), indent=2, default=str))
    except Exception as e:
        print(f"Error: {e}")

