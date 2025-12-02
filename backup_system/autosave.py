#!/usr/bin/env python3
"""
Auto-Save Service
Automatically saves current work every 15 minutes
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backup_service import BackupService
from storage_manager import StorageManager

logger = logging.getLogger(__name__)


class AutoSaveService:
    """Service for automatic saving of current work"""
    
    def __init__(self, backup_service: BackupService, config: Dict):
        """
        Initialize AutoSaveService
        
        Args:
            backup_service: BackupService instance
            config: Configuration dictionary
        """
        self.backup_service = backup_service
        self.config = config
        self.autosave_config = config.get("autosave", {
            "enabled": True,
            "interval_minutes": 15,
            "scope": ["filesystem", "mongodb"],
            "lightweight": True
        })
        self.autosave_dir = "./autosaves"
        os.makedirs(self.autosave_dir, exist_ok=True)
    
    def create_autosave(self) -> Dict:
        """
        Create an auto-save snapshot
        
        Returns:
            Dictionary with autosave result
        """
        autosave_id = f"autosave_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        timestamp = datetime.now().isoformat()
        
        logger.info(f"Creating auto-save: {autosave_id}")
        
        scope = self.autosave_config.get("scope", ["filesystem", "mongodb"])
        lightweight = self.autosave_config.get("lightweight", True)
        
        try:
            autosave_data = {
                "autosave_id": autosave_id,
                "timestamp": timestamp,
                "type": "autosave",
                "scope": scope
            }
            
            # Quick MongoDB snapshot (only recent changes if lightweight)
            if "mongodb" in scope:
                if lightweight:
                    mongo_data = self._quick_mongodb_snapshot()
                else:
                    mongo_data = self.backup_service._backup_mongodb()
                autosave_data["mongodb"] = mongo_data
            
            # Quick filesystem snapshot (only modified files if lightweight)
            if "filesystem" in scope:
                if lightweight:
                    fs_data = self._quick_filesystem_snapshot()
                else:
                    fs_data = self.backup_service._backup_filesystem(scope)
                autosave_data["filesystem"] = fs_data
            
            # Save autosave
            autosave_file = os.path.join(self.autosave_dir, f"{autosave_id}.json")
            with open(autosave_file, 'w', encoding='utf-8') as f:
                json.dump(autosave_data, f, indent=2, default=str)
            
            # Compress if enabled
            if self.config.get("backup", {}).get("compression", {}).get("enabled", True):
                import gzip
                compressed_file = f"{autosave_file}.gz"
                with open(autosave_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        f_out.writelines(f_in)
                os.remove(autosave_file)
                autosave_file = compressed_file
            
            # Cleanup old autosaves (keep last 24 hours = 96 autosaves)
            self._cleanup_old_autosaves(keep_hours=24)
            
            logger.info(f"Auto-save created: {autosave_id}")
            
            return {
                "success": True,
                "autosave_id": autosave_id,
                "timestamp": timestamp,
                "file": autosave_file,
                "size": os.path.getsize(autosave_file) if os.path.exists(autosave_file) else 0
            }
        
        except Exception as e:
            logger.error(f"Auto-save failed: {e}", exc_info=True)
            return {
                "success": False,
                "autosave_id": autosave_id,
                "timestamp": timestamp,
                "error": str(e)
            }
    
    def _quick_mongodb_snapshot(self) -> Dict:
        """Quick MongoDB snapshot (only recent documents)"""
        try:
            from mongodb_service import ensure_mongodb_connected, get_mongodb_service
            
            if not ensure_mongodb_connected():
                return {"collections": {}, "error": "MongoDB not connected"}
            
            service = get_mongodb_service()
            if not service:
                return {"collections": {}, "error": "Could not get MongoDB service"}
            
            collections_data = {}
            collections_to_backup = self.config.get("mongodb", {}).get("collections", [])
            
            # Only get recent documents (last 100 per collection for speed)
            for collection_name in collections_to_backup:
                try:
                    collection = service.get_collection(collection_name)
                    # Get most recent 100 documents
                    documents = list(collection.find({}).sort("_id", -1).limit(100))
                    collections_data[collection_name] = {
                        "count": len(documents),
                        "total_count": collection.count_documents({}),
                        "documents": documents,
                        "snapshot_type": "recent_only"
                    }
                except Exception as e:
                    logger.warning(f"Error in quick MongoDB snapshot for {collection_name}: {e}")
                    collections_data[collection_name] = {
                        "count": 0,
                        "error": str(e)
                    }
            
            return {
                "collections": {k: v["count"] for k, v in collections_data.items()},
                "data": collections_data,
                "snapshot_type": "quick"
            }
        
        except Exception as e:
            logger.error(f"Quick MongoDB snapshot failed: {e}")
            return {"collections": {}, "error": str(e)}
    
    def _quick_filesystem_snapshot(self) -> Dict:
        """Quick filesystem snapshot (only recently modified files)"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        patterns = self.config.get("filesystem", {}).get("patterns", [])
        
        files_backed_up = []
        total_size = 0
        
        # Only get files modified in last 24 hours
        import time
        cutoff_time = time.time() - (24 * 3600)  # 24 hours ago
        
        import glob
        for pattern in patterns:
            if "*" in pattern:
                matches = glob.glob(os.path.join(base_dir, pattern))
                for match in matches:
                    if os.path.isfile(match):
                        # Check if recently modified
                        mtime = os.path.getmtime(match)
                        if mtime > cutoff_time:
                            rel_path = os.path.relpath(match, base_dir)
                            try:
                                with open(match, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                files_backed_up.append({
                                    "path": rel_path,
                                    "size": len(content),
                                    "content": content,
                                    "modified": datetime.fromtimestamp(mtime).isoformat()
                                })
                                total_size += len(content)
                            except Exception as e:
                                logger.debug(f"Could not read {match}: {e}")
            else:
                # Direct file
                file_path = os.path.join(base_dir, pattern)
                if os.path.exists(file_path):
                    mtime = os.path.getmtime(file_path)
                    if mtime > cutoff_time:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            files_backed_up.append({
                                "path": pattern,
                                "size": len(content),
                                "content": content,
                                "modified": datetime.fromtimestamp(mtime).isoformat()
                            })
                            total_size += len(content)
                        except Exception as e:
                            logger.debug(f"Could not read {file_path}: {e}")
        
        return {
            "count": len(files_backed_up),
            "total_size": total_size,
            "files": files_backed_up,
            "snapshot_type": "recent_only"
        }
    
    def _cleanup_old_autosaves(self, keep_hours: int = 24):
        """Cleanup old autosaves"""
        import time
        cutoff_time = time.time() - (keep_hours * 3600)
        
        if not os.path.exists(self.autosave_dir):
            return
        
        removed_count = 0
        for filename in os.listdir(self.autosave_dir):
            file_path = os.path.join(self.autosave_dir, filename)
            if os.path.isfile(file_path):
                mtime = os.path.getmtime(file_path)
                if mtime < cutoff_time:
                    try:
                        os.remove(file_path)
                        removed_count += 1
                    except Exception as e:
                        logger.warning(f"Error removing old autosave {filename}: {e}")
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old autosaves")
    
    def list_autosaves(self, limit: int = 10) -> List[Dict]:
        """List recent autosaves"""
        autosaves = []
        
        if not os.path.exists(self.autosave_dir):
            return autosaves
        
        for filename in sorted(os.listdir(self.autosave_dir), reverse=True):
            if filename.endswith('.json') or filename.endswith('.json.gz'):
                autosave_id = filename.replace('.json.gz', '').replace('.json', '')
                file_path = os.path.join(self.autosave_dir, filename)
                mtime = os.path.getmtime(file_path)
                size = os.path.getsize(file_path)
                
                autosaves.append({
                    "autosave_id": autosave_id,
                    "timestamp": datetime.fromtimestamp(mtime).isoformat(),
                    "size": size,
                    "file": filename
                })
                
                if len(autosaves) >= limit:
                    break
        
        return autosaves


def main():
    """Main entry point for autosave"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-Save Service')
    parser.add_argument('--config', default='backup_system/backup_config.json',
                       help='Path to configuration file')
    parser.add_argument('--create', action='store_true', help='Create autosave now')
    parser.add_argument('--list', action='store_true', help='List recent autosaves')
    
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
    autosave_service = AutoSaveService(backup_service, config)
    
    if args.create:
        result = autosave_service.create_autosave()
        print(json.dumps(result, indent=2, default=str))
    
    if args.list:
        autosaves = autosave_service.list_autosaves()
        print(f"\nRecent autosaves ({len(autosaves)}):\n")
        for autosave in autosaves:
            print(f"  {autosave['autosave_id']}: {autosave['timestamp']} ({autosave['size']:,} bytes)")


if __name__ == "__main__":
    main()

