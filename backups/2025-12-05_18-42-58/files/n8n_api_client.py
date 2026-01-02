#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
n8n API Client
Integrates with n8n workflows using API credentials
"""

import os
import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class N8NAPIClient:
    """
    Client for interacting with n8n API
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        public_key: Optional[str] = None,
        private_key: Optional[str] = None
    ):
        """
        Initialize n8n API client
        
        Args:
            base_url: n8n instance URL (e.g., http://localhost:5678)
            api_key: JWT API key token
            public_key: Public API key
            private_key: Private API key
        """
        self.base_url = base_url or os.getenv("N8N_BASE_URL", "http://localhost:5678")
        self.api_key = api_key or os.getenv("N8N_API_KEY")
        self.public_key = public_key or os.getenv("N8N_PUBLIC_KEY")
        self.private_key = private_key or os.getenv("N8N_PRIVATE_KEY")
        
        # Remove trailing slash
        self.base_url = self.base_url.rstrip('/')
        
        # Setup headers
        self.headers = {
            "Content-Type": "application/json",
        }
        
        # Use JWT token if available (n8n expects X-N8N-API-KEY header)
        if self.api_key:
            self.headers["X-N8N-API-KEY"] = self.api_key
        # For public API, use public/private keys
        elif self.public_key and self.private_key:
            self.headers["X-N8N-PUBLIC-KEY"] = self.public_key
            self.headers["X-N8N-PRIVATE-KEY"] = self.private_key
        
        logger.info(f"n8n API client initialized for {self.base_url}")
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make API request to n8n
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., /api/v1/workflows)
            data: Request body data
            params: Query parameters
        
        Returns:
            Response JSON as dict
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            
            # Handle empty responses
            if response.text:
                return response.json()
            return {"success": True}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"n8n API request failed: {e}")
            if hasattr(e.response, 'text'):
                try:
                    error_data = json.loads(e.response.text)
                    raise Exception(f"n8n API error: {error_data}")
                except:
                    raise Exception(f"n8n API error: {e.response.text}")
            raise Exception(f"n8n API error: {str(e)}")
    
    def get_workflows(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get list of workflows
        
        Args:
            active_only: Only return active workflows
        
        Returns:
            List of workflow objects
        """
        params = {}
        if active_only:
            params["active"] = "true"
        
        response = self._request("GET", "/api/v1/workflows", params=params)
        return response.get("data", [])
    
    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get workflow by ID
        
        Args:
            workflow_id: Workflow ID
        
        Returns:
            Workflow object
        """
        return self._request("GET", f"/api/v1/workflows/{workflow_id}")
    
    def execute_workflow(
        self,
        workflow_id: str,
        data: Optional[Dict] = None,
        wait_for_completion: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a workflow via webhook or API
        
        Args:
            workflow_id: Workflow ID
            data: Input data for workflow
            wait_for_completion: Wait for workflow to complete
        
        Returns:
            Execution result
        """
        # For webhook execution, we need the webhook URL
        # This is a simplified version - actual implementation depends on n8n setup
        endpoint = f"/webhook/{workflow_id}"
        
        return self._request("POST", endpoint, data=data or {})
    
    def trigger_workflow_webhook(
        self,
        webhook_path: str,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Trigger workflow via webhook path
        
        Args:
            webhook_path: Webhook path (e.g., "whatsapp" or "webhook/whatsapp")
            data: Webhook payload data
        
        Returns:
            Webhook response
        """
        # Ensure webhook path starts with /webhook/
        if not webhook_path.startswith("/"):
            webhook_path = f"/webhook/{webhook_path}"
        elif not webhook_path.startswith("/webhook/"):
            webhook_path = f"/webhook{webhook_path}"
        
        return self._request("POST", webhook_path, data=data or {})
    
    def get_executions(
        self,
        workflow_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get workflow executions
        
        Args:
            workflow_id: Optional workflow ID to filter
            limit: Maximum number of executions to return
        
        Returns:
            List of execution objects
        """
        params = {"limit": limit}
        if workflow_id:
            params["workflowId"] = workflow_id
        
        response = self._request("GET", "/api/v1/executions", params=params)
        return response.get("data", [])
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check n8n API health
        
        Returns:
            Health status
        """
        try:
            response = requests.get(
                f"{self.base_url}/healthz",
                timeout=5
            )
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code,
                "base_url": self.base_url
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "base_url": self.base_url
            }


# Global instance
_n8n_client_instance: Optional[N8NAPIClient] = None


def get_n8n_client() -> N8NAPIClient:
    """Get or create global n8n API client instance"""
    global _n8n_client_instance
    if _n8n_client_instance is None:
        _n8n_client_instance = N8NAPIClient()
    return _n8n_client_instance


# Example usage
if __name__ == "__main__":
    client = get_n8n_client()
    
    # Health check
    print("🔍 Checking n8n health...")
    health = client.health_check()
    print(f"Status: {health['status']}")
    
    # List workflows
    print("\n📋 Listing workflows...")
    workflows = client.get_workflows()
    print(f"Found {len(workflows)} workflow(s)")
    for wf in workflows[:5]:  # Show first 5
        print(f"  - {wf.get('name', 'Unknown')} (ID: {wf.get('id', 'N/A')})")

