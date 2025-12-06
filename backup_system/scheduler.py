#!/usr/bin/env python3
"""
Backup Scheduler
Handles scheduled backup operations
"""
import os
import json
import logging
import schedule
import time
from datetime import datetime
from typing import Dict
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backup_service import BackupService
from storage_manager import StorageManager

try:
    from monitoring import MonitoringService
except ImportError:
    MonitoringService = None

try:
    from autosave import AutoSaveService
except ImportError:
    AutoSaveService = None

logger = logging.getLogger(__name__)


class BackupScheduler:
    """Scheduler for automated backups"""
    
    def __init__(self, config_path: str = "backup_system/backup_config.json"):
        """
        Initialize BackupScheduler
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self.storage_manager = StorageManager(self.config.get("storage", {}))
        self.backup_service = BackupService(self.storage_manager, config_path)
        self.monitoring = None
        if MonitoringService:
            self.monitoring = MonitoringService(self.config, self.backup_service, self.storage_manager)
        self.autosave = None
        if AutoSaveService:
            autosave_config = self.config.get("autosave", {"enabled": True, "interval_minutes": 15})
            if autosave_config.get("enabled", True):
                self.autosave = AutoSaveService(self.backup_service, self.config)
        self.running = False
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}
    
    def schedule_backups(self):
        """Schedule backup jobs based on configuration"""
        backup_config = self.config.get("backup", {})
        schedule_config = backup_config.get("schedule", {})
        
        # Schedule full backup
        full_schedule = schedule_config.get("full", "0 2 * * 0")  # Default: Sunday 2 AM
        if full_schedule:
            schedule.every().sunday.at("02:00").do(self._run_full_backup)
            logger.info(f"Scheduled full backup: {full_schedule}")
        
        # Schedule incremental backup
        incremental_schedule = schedule_config.get("incremental", "0 3 * * *")  # Default: Daily 3 AM
        if incremental_schedule:
            schedule.every().day.at("03:00").do(self._run_incremental_backup)
            logger.info(f"Scheduled incremental backup: {incremental_schedule}")
        
        # Schedule auto-save (every 15 minutes)
        if self.autosave:
            autosave_interval = self.config.get("autosave", {}).get("interval_minutes", 15)
            schedule.every(autosave_interval).minutes.do(self._run_autosave)
            logger.info(f"Scheduled auto-save: every {autosave_interval} minutes")
    
    def _run_full_backup(self):
        """Run full backup"""
        logger.info("Running scheduled full backup...")
        try:
            result = self.backup_service.create_full_backup()
            if result.success:
                logger.info(f"Full backup completed: {result.backup_id}")
                if self.monitoring:
                    self.monitoring.record_backup_status(result)
                self._apply_retention_policy()
            else:
                logger.error(f"Full backup failed: {result.error}")
                if self.monitoring:
                    self.monitoring.record_backup_status(result)
        except Exception as e:
            logger.error(f"Error running full backup: {e}", exc_info=True)
    
    def _run_incremental_backup(self):
        """Run incremental backup"""
        logger.info("Running scheduled incremental backup...")
        try:
            result = self.backup_service.create_incremental_backup()
            if result.success:
                logger.info(f"Incremental backup completed: {result.backup_id}")
                if self.monitoring:
                    self.monitoring.record_backup_status(result)
                self._apply_retention_policy()
            else:
                logger.error(f"Incremental backup failed: {result.error}")
                if self.monitoring:
                    self.monitoring.record_backup_status(result)
        except Exception as e:
            logger.error(f"Error running incremental backup: {e}", exc_info=True)
    
    def _run_autosave(self):
        """Run auto-save"""
        if not self.autosave:
            return
        
        logger.info("Running scheduled auto-save...")
        try:
            result = self.autosave.create_autosave()
            if result.get("success"):
                logger.info(f"Auto-save completed: {result.get('autosave_id')}")
            else:
                logger.warning(f"Auto-save completed with issues: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error running auto-save: {e}", exc_info=True)
    
    def _apply_retention_policy(self):
        """Apply retention policy to delete old backups"""
        retention_config = self.config.get("backup", {}).get("retention", {})
        full_retention = retention_config.get("full", 30)
        incremental_retention = retention_config.get("incremental", 7)
        
        # Get all backups
        backups = self.backup_service.list_backups()
        
        # Sort by timestamp
        backups.sort(key=lambda x: x.timestamp)
        
        # Delete old backups
        full_count = 0
        incremental_count = 0
        
        for backup in backups:
            if backup.type == "full":
                full_count += 1
                if full_count > full_retention:
                    logger.info(f"Deleting old full backup: {backup.backup_id}")
                    self.storage_manager.delete_backup(backup.backup_id)
            elif backup.type == "incremental":
                incremental_count += 1
                if incremental_count > incremental_retention:
                    logger.info(f"Deleting old incremental backup: {backup.backup_id}")
                    self.storage_manager.delete_backup(backup.backup_id)
    
    def run(self):
        """Run scheduler loop"""
        self.running = True
        self.schedule_backups()
        
        logger.info("Backup scheduler started")
        
        # Run initial health check
        if self.monitoring:
            self.monitoring.check_backup_health()
            self.monitoring.check_storage_usage()
        
        while self.running:
            schedule.run_pending()
            
            # Periodic health checks (every hour)
            if self.monitoring and int(time.time()) % 3600 == 0:
                self.monitoring.check_backup_health()
                self.monitoring.check_storage_usage()
            
            time.sleep(60)  # Check every minute
    
    def stop(self):
        """Stop scheduler"""
        self.running = False
        logger.info("Backup scheduler stopped")


def main():
    """Main entry point for scheduler"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Backup Scheduler')
    parser.add_argument('--config', default='backup_system/backup_config.json',
                       help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    scheduler = BackupScheduler(args.config)
    
    try:
        scheduler.run()
    except KeyboardInterrupt:
        scheduler.stop()


if __name__ == "__main__":
    main()


