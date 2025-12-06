#!/usr/bin/env python3
"""
Monitoring and Alerting System
Tracks backup status, storage usage, and sends alerts
"""
import os
import json
import logging
import smtplib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backup_service import BackupService
from storage_manager import StorageManager

logger = logging.getLogger(__name__)


@dataclass
class BackupStatus:
    """Backup status information"""
    backup_id: str
    status: str  # success, failed, in_progress
    timestamp: str
    size: int
    duration: Optional[float] = None
    error: Optional[str] = None


@dataclass
class Alert:
    """Alert information"""
    alert_id: str
    timestamp: str
    level: str  # info, warning, error, critical
    type: str  # backup_failure, storage_full, recovery_needed
    message: str
    resolved: bool = False
    resolved_at: Optional[str] = None


class MonitoringService:
    """Service for monitoring backup operations and sending alerts"""
    
    def __init__(self, config: Dict, backup_service: BackupService = None, storage_manager: StorageManager = None):
        """
        Initialize MonitoringService
        
        Args:
            config: Configuration dictionary
            backup_service: BackupService instance
            storage_manager: StorageManager instance
        """
        self.config = config
        self.backup_service = backup_service
        self.storage_manager = storage_manager
        self.monitoring_config = config.get("monitoring", {})
        self.alerts_dir = "./backup_alerts"
        self.status_dir = "./backup_status"
        
        os.makedirs(self.alerts_dir, exist_ok=True)
        os.makedirs(self.status_dir, exist_ok=True)
    
    def record_backup_status(self, backup_result) -> BackupStatus:
        """
        Record backup operation status
        
        Args:
            backup_result: BackupResult object
        
        Returns:
            BackupStatus object
        """
        status = BackupStatus(
            backup_id=backup_result.backup_id,
            status="success" if backup_result.success else "failed",
            timestamp=backup_result.timestamp,
            size=backup_result.size,
            error=backup_result.error
        )
        
        # Save status
        status_file = os.path.join(self.status_dir, f"{backup_result.backup_id}.json")
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(status), f, indent=2, default=str)
        
        # Check for alerts
        if not backup_result.success:
            self.create_alert(
                level="error",
                alert_type="backup_failure",
                message=f"Backup {backup_result.backup_id} failed: {backup_result.error}"
            )
        
        return status
    
    def check_storage_usage(self) -> Dict:
        """
        Check storage usage and create alerts if needed
        
        Returns:
            Dictionary with storage usage information
        """
        if not self.storage_manager:
            return {}
        
        usage = self.storage_manager.get_storage_usage()
        
        # Check thresholds
        max_size_str = self.config.get("storage", {}).get("local", {}).get("max_size", "10GB")
        max_size_bytes = self._parse_size(max_size_str)
        
        if max_size_bytes and usage.total_size > max_size_bytes * 0.9:  # 90% threshold
            self.create_alert(
                level="warning",
                alert_type="storage_full",
                message=f"Storage usage at {usage.total_size / max_size_bytes * 100:.1f}% ({usage.total_size:,} bytes)"
            )
        
        return {
            "total_size": usage.total_size,
            "backup_count": usage.backup_count,
            "max_size": max_size_bytes,
            "usage_percentage": (usage.total_size / max_size_bytes * 100) if max_size_bytes else 0
        }
    
    def check_backup_health(self) -> Dict:
        """
        Check overall backup health
        
        Returns:
            Dictionary with health status
        """
        if not self.backup_service:
            return {"status": "unknown", "error": "Backup service not available"}
        
        # Get recent backups
        recent_backups = self.backup_service.list_backups()
        
        if not recent_backups:
            self.create_alert(
                level="warning",
                alert_type="backup_missing",
                message="No backups found in the last 24 hours"
            )
            return {
                "status": "warning",
                "message": "No recent backups"
            }
        
        # Check last backup
        last_backup = recent_backups[0]
        last_backup_time = datetime.fromisoformat(last_backup.timestamp)
        hours_since_backup = (datetime.now() - last_backup_time).total_seconds() / 3600
        
        if hours_since_backup > 48:
            self.create_alert(
                level="warning",
                alert_type="backup_stale",
                message=f"Last backup was {hours_since_backup:.1f} hours ago"
            )
        
        # Check verification status
        unverified_count = sum(1 for b in recent_backups[:10] if not b.verified)
        if unverified_count > 0:
            self.create_alert(
                level="warning",
                alert_type="backup_unverified",
                message=f"{unverified_count} recent backups are unverified"
            )
        
        return {
            "status": "healthy",
            "last_backup": last_backup.timestamp,
            "hours_since_backup": hours_since_backup,
            "recent_backups": len(recent_backups),
            "unverified": unverified_count
        }
    
    def create_alert(self, level: str, alert_type: str, message: str) -> Alert:
        """
        Create an alert
        
        Args:
            level: Alert level (info, warning, error, critical)
            alert_type: Type of alert
            message: Alert message
        
        Returns:
            Alert object
        """
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        alert = Alert(
            alert_id=alert_id,
            timestamp=datetime.now().isoformat(),
            level=level,
            type=alert_type,
            message=message
        )
        
        # Save alert
        alert_file = os.path.join(self.alerts_dir, f"{alert_id}.json")
        with open(alert_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(alert), f, indent=2, default=str)
        
        # Send notification if enabled
        if self.monitoring_config.get("alert_on_failure", True):
            self._send_alert(alert)
        
        logger.warning(f"Alert created: {level} - {message}")
        return alert
    
    def _send_alert(self, alert: Alert):
        """Send alert notification"""
        # Check if alert should be sent based on level
        alert_levels = self.monitoring_config.get("alert_levels", ["error", "critical"])
        if alert.level not in alert_levels:
            return
        
        # Email notification (if configured)
        email_config = self.monitoring_config.get("email", {})
        if email_config.get("enabled", False):
            self._send_email_alert(alert, email_config)
        
        # Log notification
        logger.warning(f"ALERT [{alert.level.upper()}]: {alert.message}")
    
    def _send_email_alert(self, alert: Alert, email_config: Dict):
        """Send email alert"""
        try:
            smtp_server = email_config.get("smtp_server", "smtp.gmail.com")
            smtp_port = email_config.get("smtp_port", 587)
            sender = email_config.get("sender")
            recipients = email_config.get("recipients", [])
            username = email_config.get("username")
            password = email_config.get("password")
            
            if not sender or not recipients:
                return
            
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"Backup Alert [{alert.level.upper()}]: {alert.type}"
            
            body = f"""
Backup System Alert

Level: {alert.level.upper()}
Type: {alert.type}
Time: {alert.timestamp}
Message: {alert.message}

Alert ID: {alert.alert_id}
"""
            msg.attach(MIMEText(body, 'plain'))
            
            if username and password:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(username, password)
                server.send_message(msg)
                server.quit()
                logger.info(f"Email alert sent to {recipients}")
        
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def get_alerts(self, unresolved_only: bool = True, level: Optional[str] = None) -> List[Alert]:
        """
        Get alerts
        
        Args:
            unresolved_only: Only return unresolved alerts
            level: Filter by alert level
        
        Returns:
            List of Alert objects
        """
        alerts = []
        
        if not os.path.exists(self.alerts_dir):
            return alerts
        
        for filename in os.listdir(self.alerts_dir):
            if filename.endswith('.json'):
                alert_file = os.path.join(self.alerts_dir, filename)
                try:
                    with open(alert_file, 'r', encoding='utf-8') as f:
                        alert_data = json.load(f)
                    
                    alert = Alert(**alert_data)
                    
                    if unresolved_only and alert.resolved:
                        continue
                    
                    if level and alert.level != level:
                        continue
                    
                    alerts.append(alert)
                
                except Exception as e:
                    logger.warning(f"Error reading alert {filename}: {e}")
        
        # Sort by timestamp (newest first)
        alerts.sort(key=lambda x: x.timestamp, reverse=True)
        return alerts
    
    def resolve_alert(self, alert_id: str):
        """Mark an alert as resolved"""
        alert_file = os.path.join(self.alerts_dir, f"{alert_id}.json")
        if os.path.exists(alert_file):
            with open(alert_file, 'r', encoding='utf-8') as f:
                alert_data = json.load(f)
            
            alert_data["resolved"] = True
            alert_data["resolved_at"] = datetime.now().isoformat()
            
            with open(alert_file, 'w', encoding='utf-8') as f:
                json.dump(alert_data, f, indent=2, default=str)
    
    def get_metrics(self) -> Dict:
        """
        Get monitoring metrics
        
        Returns:
            Dictionary with metrics
        """
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "storage": self.check_storage_usage(),
            "health": self.check_backup_health(),
            "alerts": {
                "total": len(self.get_alerts(unresolved_only=False)),
                "unresolved": len(self.get_alerts(unresolved_only=True)),
                "by_level": {}
            }
        }
        
        # Count alerts by level
        for level in ["info", "warning", "error", "critical"]:
            metrics["alerts"]["by_level"][level] = len(self.get_alerts(level=level, unresolved_only=False))
        
        return metrics
    
    def _parse_size(self, size_str: str) -> Optional[int]:
        """Parse size string to bytes"""
        if not size_str:
            return None
        
        size_str = size_str.upper().strip()
        
        multipliers = {
            "KB": 1024,
            "MB": 1024 * 1024,
            "GB": 1024 * 1024 * 1024,
            "TB": 1024 * 1024 * 1024 * 1024
        }
        
        for unit, multiplier in multipliers.items():
            if size_str.endswith(unit):
                number = float(size_str[:-len(unit)])
                return int(number * multiplier)
        
        # Try to parse as number (assume bytes)
        try:
            return int(size_str)
        except:
            return None


def main():
    """Main entry point for monitoring"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Backup Monitoring Service')
    parser.add_argument('--config', default='backup_system/backup_config.json',
                       help='Path to configuration file')
    parser.add_argument('--check', action='store_true', help='Run health check')
    parser.add_argument('--alerts', action='store_true', help='Show alerts')
    parser.add_argument('--metrics', action='store_true', help='Show metrics')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load config
    with open(args.config, 'r') as f:
        config = json.load(f)
    
    storage_manager = StorageManager(config.get("storage", {}))
    backup_service = BackupService(storage_manager, args.config)
    monitoring = MonitoringService(config, backup_service, storage_manager)
    
    if args.check:
        health = monitoring.check_backup_health()
        print(json.dumps(health, indent=2, default=str))
    
    if args.alerts:
        alerts = monitoring.get_alerts()
        print(f"\nFound {len(alerts)} unresolved alerts:\n")
        for alert in alerts:
            print(f"[{alert.level.upper()}] {alert.type}: {alert.message}")
            print(f"  Time: {alert.timestamp}")
            print()
    
    if args.metrics:
        metrics = monitoring.get_metrics()
        print(json.dumps(metrics, indent=2, default=str))
    
    if not any([args.check, args.alerts, args.metrics]):
        # Run all checks
        print("Running monitoring checks...")
        health = monitoring.check_backup_health()
        storage = monitoring.check_storage_usage()
        alerts = monitoring.get_alerts()
        
        print(f"\nHealth Status: {health.get('status', 'unknown')}")
        print(f"Storage Usage: {storage.get('usage_percentage', 0):.1f}%")
        print(f"Unresolved Alerts: {len(alerts)}")
        
        if alerts:
            print("\nRecent Alerts:")
            for alert in alerts[:5]:
                print(f"  [{alert.level}] {alert.message}")


if __name__ == "__main__":
    main()


