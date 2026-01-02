#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cursor Analytics Service
Servicio para recolectar y analizar métricas de Cursor Analytics API
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from cursor_api_client import CursorAPIClient

logger = logging.getLogger(__name__)


@dataclass
class DailyActiveUsers:
    """Métricas de usuarios activos diarios"""
    date: str
    count: int
    percentage: float


@dataclass
class ModelUsage:
    """Uso de modelos de IA"""
    model: str
    requests: int
    tokens_input: int
    tokens_output: int
    cost: float


@dataclass
class TeamMetrics:
    """Métricas agregadas del equipo"""
    date: str
    dau: int
    total_users: int
    sessions: int
    avg_session_duration: float
    model_usage: List[ModelUsage]
    total_cost: float


class CursorAnalyticsService:
    """
    Servicio para interactuar con Cursor Analytics API
    Recolecta y procesa métricas de uso del equipo
    """
    
    def __init__(self, client: Optional[CursorAPIClient] = None):
        """
        Inicializa servicio de analytics
        
        Args:
            client: Cliente de Cursor API (opcional, crea uno nuevo si no se proporciona)
        """
        self.client = client or CursorAPIClient()
    
    def get_daily_active_users(
        self,
        start_date: str = "7d",
        end_date: str = "today"
    ) -> List[DailyActiveUsers]:
        """
        Obtiene usuarios activos diarios
        
        Args:
            start_date: Fecha de inicio (formato: "7d", "30d", "2024-12-01")
            end_date: Fecha de fin (formato: "today", "2024-12-28")
        
        Returns:
            Lista de métricas de DAU
        """
        try:
            response = self.client.get(
                "/analytics/team/dau",
                params={
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            dau_list = []
            for item in response.get("data", []):
                dau_list.append(DailyActiveUsers(
                    date=item.get("date"),
                    count=item.get("count", 0),
                    percentage=item.get("percentage", 0.0)
                ))
            
            logger.info(f"Obtenidos {len(dau_list)} registros de DAU")
            return dau_list
        
        except Exception as e:
            logger.error(f"Error obteniendo DAU: {e}")
            raise
    
    def get_model_usage(
        self,
        start_date: str = "30d",
        end_date: str = "today"
    ) -> List[ModelUsage]:
        """
        Obtiene uso de modelos de IA
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
        
        Returns:
            Lista de uso por modelo
        """
        try:
            response = self.client.get(
                "/analytics/team/model-usage",
                params={
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            model_usage = []
            for item in response.get("data", []):
                model_usage.append(ModelUsage(
                    model=item.get("model", "unknown"),
                    requests=item.get("requests", 0),
                    tokens_input=item.get("tokens_input", 0),
                    tokens_output=item.get("tokens_output", 0),
                    cost=item.get("cost", 0.0)
                ))
            
            logger.info(f"Obtenido uso de {len(model_usage)} modelos")
            return model_usage
        
        except Exception as e:
            logger.error(f"Error obteniendo uso de modelos: {e}")
            raise
    
    def get_user_metrics(
        self,
        user_id: str,
        start_date: str = "7d",
        end_date: str = "today"
    ) -> Dict[str, Any]:
        """
        Obtiene métricas de un usuario específico
        
        Args:
            user_id: ID del usuario
            start_date: Fecha de inicio
            end_date: Fecha de fin
        
        Returns:
            Métricas del usuario
        """
        try:
            response = self.client.get(
                f"/analytics/user/{user_id}",
                params={
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Error obteniendo métricas de usuario {user_id}: {e}")
            raise
    
    def get_team_metrics(
        self,
        date: Optional[str] = None
    ) -> TeamMetrics:
        """
        Obtiene métricas agregadas del equipo para una fecha
        
        Args:
            date: Fecha (formato: "2024-12-28" o None para hoy)
        
        Returns:
            Métricas del equipo
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            # Obtener DAU
            dau_data = self.get_daily_active_users(
                start_date=date,
                end_date=date
            )
            dau = dau_data[0].count if dau_data else 0
            
            # Obtener uso de modelos
            model_usage = self.get_model_usage(
                start_date=date,
                end_date=date
            )
            
            # Calcular totales
            total_cost = sum(m.cost for m in model_usage)
            total_users = dau_data[0].percentage * 100 if dau_data else 0
            
            return TeamMetrics(
                date=date,
                dau=dau,
                total_users=int(total_users),
                sessions=0,  # Requiere endpoint adicional
                avg_session_duration=0.0,  # Requiere endpoint adicional
                model_usage=model_usage,
                total_cost=total_cost
            )
        
        except Exception as e:
            logger.error(f"Error obteniendo métricas del equipo: {e}")
            raise
    
    def get_usage_summary(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Obtiene resumen de uso para los últimos N días
        
        Args:
            days: Número de días a analizar
        
        Returns:
            Resumen de uso
        """
        try:
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")
            
            # Obtener DAU
            dau_data = self.get_daily_active_users(
                start_date=start_date,
                end_date=end_date
            )
            
            # Obtener uso de modelos
            model_usage = self.get_model_usage(
                start_date=start_date,
                end_date=end_date
            )
            
            # Calcular promedios
            avg_dau = sum(d.count for d in dau_data) / len(dau_data) if dau_data else 0
            total_cost = sum(m.cost for m in model_usage)
            total_requests = sum(m.requests for m in model_usage)
            
            # Modelo más usado
            most_used_model = max(
                model_usage, 
                key=lambda m: m.requests
            ) if model_usage else None
            
            return {
                "period": {
                    "start": start_date,
                    "end": end_date,
                    "days": days
                },
                "dau": {
                    "average": avg_dau,
                    "max": max(d.count for d in dau_data) if dau_data else 0,
                    "min": min(d.count for d in dau_data) if dau_data else 0,
                    "trend": "up" if len(dau_data) > 1 and dau_data[-1].count > dau_data[0].count else "down"
                },
                "model_usage": {
                    "total_requests": total_requests,
                    "total_cost": total_cost,
                    "models": [asdict(m) for m in model_usage],
                    "most_used": asdict(most_used_model) if most_used_model else None
                },
                "cost": {
                    "total": total_cost,
                    "average_per_day": total_cost / days if days > 0 else 0,
                    "average_per_user": total_cost / avg_dau if avg_dau > 0 else 0
                }
            }
        
        except Exception as e:
            logger.error(f"Error obteniendo resumen de uso: {e}")
            raise


# Ejemplo de uso
if __name__ == "__main__":
    # Inicializar servicio
    service = CursorAnalyticsService()
    
    # Obtener resumen de últimos 30 días
    try:
        summary = service.get_usage_summary(days=30)
        print("Usage Summary:")
        print(json.dumps(summary, indent=2, default=str))
    except Exception as e:
        print(f"Error: {e}")

