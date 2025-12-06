#!/usr/bin/env python3
"""
Conversation Data Recovery Script
Scans MongoDB, backup files, and exports to recover lost conversation data
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


class ConversationRecovery:
    """Recovery system for lost conversation data"""

    def __init__(self, mongodb_uri: str | None = None):
        self.mongodb_uri = mongodb_uri or os.getenv(
            "MONGODB_URI", "mongodb://localhost:27017/bmc-cotizaciones"
        )
        self.client = None
        self.db = None
        self.recovery_report = {
            "timestamp": datetime.now().isoformat(),
            "mongodb": {
                "connected": False,
                "database": "",
                "collections": {},
                "total_found": 0,
            },
            "filesystem": {"backups": [], "exports": [], "total_found": 0},
            "summary": {
                "total_conversations": 0,
                "total_quotes": 0,
                "total_sessions": 0,
                "recovery_status": "failed",
                "recommendations": [],
            },
        }

    def connect_mongodb(self) -> bool:
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.mongodb_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command("ping")
            self.db = self.client.get_database()
            self.recovery_report["mongodb"]["connected"] = True
            self.recovery_report["mongodb"]["database"] = self.db.name
            print(f"✅ Connected to MongoDB: {self.db.name}")
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"❌ MongoDB connection failed: {e}")
            self.recovery_report["mongodb"]["collections"] = {"error": str(e)}
            self.recovery_report["summary"]["recommendations"].append(
                "MongoDB connection failed. Check MONGODB_URI environment variable."
            )
            return False
        except Exception as e:
            print(f"❌ Error connecting to MongoDB: {e}")
            return False

    def scan_mongodb(self) -> dict[str, Any]:
        """Scan MongoDB for conversation data"""
        if self.db is None:
            return {}

        collections_to_check = [
            "conversations",
            "conversaciones",
            "sessions",
            "context",
            "quotes",
            "cotizaciones",
            "quotes_history",
            "analytics",
        ]

        found_data = {}

        for collection_name in collections_to_check:
            try:
                collection = self.db[collection_name]
                count = collection.count_documents({})

                if count > 0:
                    # Get sample data
                    sample = list(collection.find().limit(10).sort("_id", -1))
                    found_data[collection_name] = {
                        "count": count,
                        "sample_size": len(sample),
                        "sample": sample,
                    }

                    self.recovery_report["mongodb"]["total_found"] += count
                    self.recovery_report["mongodb"]["collections"][collection_name] = count

                    # Update summary
                    if collection_name in ["conversations", "conversaciones"]:
                        self.recovery_report["summary"]["total_conversations"] += count
                    elif collection_name in ["quotes", "cotizaciones"]:
                        self.recovery_report["summary"]["total_quotes"] += count
                    elif collection_name in ["sessions", "context"]:
                        self.recovery_report["summary"]["total_sessions"] += count

                    print(f"  📊 {collection_name}: {count} documents")
            except Exception as e:
                print(f"  ⚠️  Error scanning {collection_name}: {e}")

        return found_data

    def scan_filesystem(self, root_dir: str | None = None) -> list[dict[str, Any]]:
        """Scan filesystem for backup and export files"""
        if not root_dir:
            root_dir = os.getcwd()

        root_path = Path(root_dir)
        backup_files = []

        # Patterns to match backup/export files
        patterns = [
            "**/conversation*.json",
            "**/backup*.json",
            "**/export*.json",
            "**/*_conversations.json",
            "**/*_export.json",
            "**/kb_populated*.json",
        ]

        # Directories to search
        search_dirs = [
            root_path,
            root_path / "backups",
            root_path / "exportaciones",
            root_path / "exports",
            root_path / "data",
        ]

        found_files = []

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for pattern in patterns:
                try:
                    for file_path in search_dir.glob(pattern):
                        if file_path.is_file():
                            try:
                                with open(file_path, encoding="utf-8") as f:
                                    data = json.load(f)

                                # Extract conversations from various formats
                                conversations = []
                                if isinstance(data, list):
                                    conversations = data
                                elif isinstance(data, dict):
                                    if "conversations" in data and isinstance(
                                        data["conversations"], list
                                    ):
                                        conversations = data["conversations"]
                                    elif "messages" in data and isinstance(data["messages"], list):
                                        conversations = [data]
                                    elif "data" in data and isinstance(data["data"], list):
                                        conversations = data["data"]
                                    elif "interacciones" in data and isinstance(
                                        data["interacciones"], list
                                    ):
                                        conversations = data["interacciones"]

                                if conversations:
                                    file_info = {
                                        "path": str(file_path),
                                        "name": file_path.name,
                                        "size": file_path.stat().st_size,
                                        "conversations_count": len(conversations),
                                        "sample": (
                                            conversations[:5]
                                            if len(conversations) > 5
                                            else conversations
                                        ),
                                    }
                                    found_files.append(file_info)
                                    self.recovery_report["filesystem"]["total_found"] += len(
                                        conversations
                                    )
                                    self.recovery_report["summary"]["total_conversations"] += len(
                                        conversations
                                    )
                                    print(
                                        f"  📁 Found: {file_path.name} ({len(conversations)} conversations)"
                                    )
                            except json.JSONDecodeError:
                                print(f"  ⚠️  Invalid JSON: {file_path.name}")
                            except Exception as e:
                                print(f"  ⚠️  Error reading {file_path.name}: {e}")
                except Exception as e:
                    print(f"  ⚠️  Error searching in {search_dir}: {e}")

        self.recovery_report["filesystem"]["backups"] = found_files
        return found_files

    def create_backup(self, output_dir: str | None = None) -> str:
        """Create backup of current MongoDB data"""
        if self.db is None:
            print("❌ MongoDB not connected. Cannot create backup.")
            return ""

        if not output_dir:
            output_dir = os.path.join(os.getcwd(), "backups")

        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(output_dir, f"backup_{timestamp}.json")

        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "database": self.db.name,
            "collections": {},
        }

        collections_to_backup = [
            "conversations",
            "conversaciones",
            "quotes",
            "sessions",
            "context",
        ]

        for collection_name in collections_to_backup:
            try:
                collection = self.db[collection_name]
                count = collection.count_documents({})
                if count > 0:
                    data = list(collection.find({}))
                    backup_data["collections"][collection_name] = data
                    print(f"  💾 Backed up {collection_name}: {count} documents")
            except Exception as e:
                print(f"  ⚠️  Error backing up {collection_name}: {e}")

        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)

        print(f"✅ Backup created: {backup_file}")
        return backup_file

    def restore_from_file(
        self, file_path: str, target_collection: str = "conversations"
    ) -> dict[str, Any]:
        """Restore conversations from a backup file"""
        if self.db is None:
            return {"success": False, "error": "MongoDB not connected"}

        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            # Extract conversations
            conversations = []
            if isinstance(data, list):
                conversations = data
            elif isinstance(data, dict):
                if "collections" in data and target_collection in data["collections"]:
                    conversations = data["collections"][target_collection]
                elif "conversations" in data:
                    conversations = data["conversations"]
                elif "data" in data:
                    conversations = data["data"]
                elif "messages" in data or "session_id" in data:
                    # Single conversation object with session_id and messages
                    conversations = [data]

            if not conversations:
                return {"success": False, "error": "No conversations found in file"}

            collection = self.db[target_collection]
            restored = 0
            failed = 0

            for conv in conversations:
                try:
                    # Remove _id to allow MongoDB to create new one
                    if "_id" in conv:
                        del conv["_id"]

                    # Ensure required fields
                    if "timestamp" not in conv and "createdAt" not in conv:
                        conv["timestamp"] = datetime.now()
                    if "createdAt" not in conv:
                        conv["createdAt"] = conv.get("timestamp", datetime.now())

                    collection.insert_one(conv)
                    restored += 1
                except Exception as e:
                    failed += 1
                    print(f"  ⚠️  Failed to restore conversation: {e}")

            return {
                "success": True,
                "restored": restored,
                "failed": failed,
                "total": len(conversations),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_report(self) -> dict[str, Any]:
        """Generate recovery report"""
        # Determine recovery status
        total_found = (
            self.recovery_report["mongodb"]["total_found"]
            + self.recovery_report["filesystem"]["total_found"]
        )

        if total_found > 0:
            self.recovery_report["summary"]["recovery_status"] = "success"
            if self.recovery_report["mongodb"]["total_found"] == 0:
                self.recovery_report["summary"]["recommendations"].append(
                    "Data found in backup files but not in MongoDB. Consider restoring from backups."
                )
        else:
            self.recovery_report["summary"]["recovery_status"] = "failed"
            self.recovery_report["summary"]["recommendations"].append(
                "No conversation data found. Check if MongoDB is properly configured."
            )

        return self.recovery_report

    def run_recovery(self, create_backup_first: bool = True) -> dict[str, Any]:
        """Run full recovery scan"""
        print("=" * 70)
        print("🔍 CONVERSATION DATA RECOVERY SYSTEM")
        print("=" * 70)
        print()

        # Create backup first if requested
        if create_backup_first and self.connect_mongodb():
            print("\n📦 Creating backup before recovery...")
            self.create_backup()

        # Scan MongoDB
        print("\n🔍 Scanning MongoDB...")
        if self.connect_mongodb():
            self.scan_mongodb()
        else:
            print("  ⚠️  Skipping MongoDB scan (not connected)")

        # Scan filesystem
        print("\n📁 Scanning filesystem for backup files...")
        self.scan_filesystem()

        # Generate report
        print("\n📊 Generating recovery report...")
        report = self.generate_report()

        # Print summary
        print("\n" + "=" * 70)
        print("📋 RECOVERY SUMMARY")
        print("=" * 70)
        print(f"  MongoDB: {report['mongodb']['total_found']} documents found")
        print(f"  Filesystem: {report['filesystem']['total_found']} conversations found")
        print(f"  Total Conversations: {report['summary']['total_conversations']}")
        print(f"  Total Quotes: {report['summary']['total_quotes']}")
        print(f"  Total Sessions: {report['summary']['total_sessions']}")
        print(f"  Status: {report['summary']['recovery_status'].upper()}")

        if report["summary"]["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in report["summary"]["recommendations"]:
                print(f"  - {rec}")

        print("=" * 70)

        return report

    def save_report(self, output_file: str | None = None) -> str:
        """Save recovery report to file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(os.getcwd(), f"recovery_report_{timestamp}.json")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.recovery_report, f, ensure_ascii=False, indent=2, default=str)

        print(f"💾 Recovery report saved: {output_file}")
        return output_file


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Recover lost conversation data")
    parser.add_argument("--mongodb-uri", help="MongoDB connection string")
    parser.add_argument(
        "--no-backup", action="store_true", help="Skip creating backup before recovery"
    )
    parser.add_argument("--restore", help="Restore from backup file")
    parser.add_argument(
        "--target-collection",
        default="conversations",
        help="Target collection for restore",
    )
    parser.add_argument("--output", help="Output file for recovery report")

    args = parser.parse_args()

    recovery = ConversationRecovery(mongodb_uri=args.mongodb_uri)

    if args.restore:
        # Restore mode
        if not recovery.connect_mongodb():
            print("❌ Cannot restore: MongoDB not connected")
            sys.exit(1)

        print(f"🔄 Restoring from: {args.restore}")
        result = recovery.restore_from_file(args.restore, args.target_collection)

        if result["success"]:
            print(f"✅ Restored {result['restored']} conversations")
            if result["failed"] > 0:
                print(f"⚠️  Failed to restore {result['failed']} conversations")
        else:
            print(f"❌ Restore failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    else:
        # Scan mode
        report = recovery.run_recovery(create_backup_first=not args.no_backup)

        # Save report
        recovery.save_report(args.output)

        # Exit with appropriate code
        if report["summary"]["recovery_status"] == "failed":
            sys.exit(1)
        elif report["summary"]["recovery_status"] == "partial":
            sys.exit(2)


if __name__ == "__main__":
    main()
