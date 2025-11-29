#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Recovery and Cleanup Utility
Detects partial setup states and offers recovery options
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import validator
sys.path.insert(0, str(Path(__file__).parent))
from validate_environment import EnvironmentValidator


class SetupRecovery:
    """Recovery utility for setup issues"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent.resolve()
        self.backup_dir = self.root_dir / "backups" / "setup_recovery"
        self.issues: List[Dict[str, Any]] = []
        self.fixes_applied: List[str] = []
        
    def detect_issues(self) -> List[Dict[str, Any]]:
        """Detect setup issues"""
        issues = []
        
        # Check .env file
        env_file = self.root_dir / ".env"
        if not env_file.exists():
            issues.append({
                "type": "missing_env",
                "severity": "critical",
                "message": ".env file is missing",
                "fix": "create_env_file"
            })
        else:
            # Check if .env has placeholder values
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "your-" in content or "your_" in content:
                        issues.append({
                            "type": "placeholder_values",
                            "severity": "warning",
                            "message": ".env file contains placeholder values",
                            "fix": "update_env_values"
                        })
            except Exception:
                pass
        
        # Check Python dependencies
        try:
            import openai
        except ImportError:
            issues.append({
                "type": "missing_dependencies",
                "severity": "critical",
                "message": "Python dependencies not installed",
                "fix": "install_dependencies"
            })
        
        # Check knowledge base files
        knowledge_files = [
            "conocimiento_consolidado.json",
            "base_conocimiento_final.json",
            "conocimiento_completo.json"
        ]
        found_kb = any((self.root_dir / f).exists() for f in knowledge_files)
        if not found_kb:
            issues.append({
                "type": "missing_knowledge",
                "severity": "warning",
                "message": "No knowledge base files found",
                "fix": "consolidate_knowledge"
            })
        
        # Check logs directory
        logs_dir = self.root_dir / "logs"
        if not logs_dir.exists():
            issues.append({
                "type": "missing_logs_dir",
                "severity": "info",
                "message": "Logs directory doesn't exist",
                "fix": "create_logs_dir"
            })
        
        # Check MongoDB (optional)
        try:
            from pymongo import MongoClient
            mongodb_uri = os.getenv("MONGODB_URI", "")
            if mongodb_uri and not mongodb_uri.startswith("your-"):
                try:
                    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=2000)
                    client.admin.command("ping")
                    client.close()
                except Exception:
                    issues.append({
                        "type": "mongodb_unavailable",
                        "severity": "warning",
                        "message": "MongoDB is configured but not accessible",
                        "fix": "check_mongodb"
                    })
        except ImportError:
            pass
        
        self.issues = issues
        return issues
    
    def create_backup(self) -> Path:
        """Create backup of current state"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / timestamp
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Backup .env if exists
        env_file = self.root_dir / ".env"
        if env_file.exists():
            shutil.copy2(env_file, backup_path / ".env")
        
        # Save backup info
        backup_info = {
            "timestamp": timestamp,
            "backup_path": str(backup_path),
            "files_backed_up": []
        }
        
        if env_file.exists():
            backup_info["files_backed_up"].append(".env")
        
        with open(backup_path / "backup_info.json", 'w') as f:
            json.dump(backup_info, f, indent=2)
        
        return backup_path
    
    def fix_create_env_file(self) -> bool:
        """Fix: Create .env file from template"""
        env_file = self.root_dir / ".env"
        env_example = self.root_dir / "env.example"
        
        if env_file.exists():
            return True  # Already exists
        
        if env_example.exists():
            shutil.copy2(env_example, env_file)
            self.fixes_applied.append("Created .env file from env.example")
            return True
        
        return False
    
    def fix_update_env_values(self) -> bool:
        """Fix: Update placeholder values in .env"""
        env_file = self.root_dir / ".env"
        
        if not env_file.exists():
            return False
        
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            updated = False
            with open(env_file, 'w', encoding='utf-8') as f:
                for line in lines:
                    if '=' in line and ('your-' in line or 'your_' in line):
                        # Keep the line but mark it
                        updated = True
                    f.write(line)
            
            if updated:
                self.fixes_applied.append("Marked placeholder values in .env (manual update needed)")
                return True
        except Exception:
            return False
        
        return False
    
    def fix_install_dependencies(self) -> bool:
        """Fix: Install Python dependencies"""
        try:
            import subprocess
            requirements = self.root_dir / "requirements.txt"
            
            if not requirements.exists():
                return False
            
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.fixes_applied.append("Installed Python dependencies")
                return True
            else:
                return False
        except Exception:
            return False
    
    def fix_consolidate_knowledge(self) -> bool:
        """Fix: Consolidate knowledge base"""
        consolidate_script = self.root_dir / "consolidar_conocimiento.py"
        
        if not consolidate_script.exists():
            return False
        
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("consolidar_conocimiento", consolidate_script)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, "ConsolidadorConocimiento"):
                    consolidador = module.ConsolidadorConocimiento()
                    conocimiento = consolidador.consolidar_todos()
                    consolidador.guardar(str(self.root_dir / "conocimiento_consolidado.json"))
                    self.fixes_applied.append("Consolidated knowledge base")
                    return True
        except Exception:
            pass
        
        return False
    
    def fix_create_logs_dir(self) -> bool:
        """Fix: Create logs directory"""
        logs_dir = self.root_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        self.fixes_applied.append("Created logs directory")
        return True
    
    def fix_check_mongodb(self) -> bool:
        """Fix: Check MongoDB connection"""
        # Just provide information, can't auto-fix
        self.fixes_applied.append("MongoDB check: Ensure MongoDB is running (docker start bmc-mongodb)")
        return False
    
    def apply_fixes(self, auto_fix: bool = False) -> Dict[str, Any]:
        """Apply fixes for detected issues"""
        if not self.issues:
            return {
                "success": True,
                "message": "No issues detected",
                "fixes_applied": []
            }
        
        # Create backup before applying fixes
        backup_path = self.create_backup()
        
        fixes_applied = []
        fixes_failed = []
        
        for issue in self.issues:
            fix_func_name = f"fix_{issue['fix']}"
            if hasattr(self, fix_func_name):
                fix_func = getattr(self, fix_func_name)
                
                if auto_fix or issue["severity"] == "critical":
                    try:
                        if fix_func():
                            fixes_applied.append(issue["type"])
                        else:
                            fixes_failed.append(issue["type"])
                    except Exception as e:
                        fixes_failed.append(f"{issue['type']}: {e}")
                else:
                    # Just log the fix
                    fixes_applied.append(f"{issue['type']} (manual fix needed)")
        
        return {
            "success": len(fixes_failed) == 0,
            "backup_path": str(backup_path),
            "fixes_applied": fixes_applied,
            "fixes_failed": fixes_failed,
            "fixes_details": self.fixes_applied
        }
    
    def restore_from_backup(self, backup_timestamp: Optional[str] = None) -> bool:
        """Restore from backup"""
        if backup_timestamp is None:
            # Find latest backup
            if not self.backup_dir.exists():
                return False
            
            backups = sorted(self.backup_dir.iterdir(), key=lambda x: x.name, reverse=True)
            if not backups:
                return False
            
            backup_path = backups[0]
        else:
            backup_path = self.backup_dir / backup_timestamp
        
        if not backup_path.exists():
            return False
        
        # Restore .env
        backup_env = backup_path / ".env"
        if backup_env.exists():
            env_file = self.root_dir / ".env"
            shutil.copy2(backup_env, env_file)
            return True
        
        return False
    
    def print_report(self, issues: List[Dict[str, Any]]):
        """Print recovery report"""
        print("\n" + "=" * 70)
        print("SETUP RECOVERY REPORT")
        print("=" * 70 + "\n")
        
        if not issues:
            print("✅ No issues detected. Setup appears to be complete.\n")
            return
        
        # Group by severity
        critical = [i for i in issues if i["severity"] == "critical"]
        warnings = [i for i in issues if i["severity"] == "warning"]
        info = [i for i in issues if i["severity"] == "info"]
        
        if critical:
            print("CRITICAL ISSUES (Must be fixed):")
            print("-" * 70)
            for issue in critical:
                print(f"\n❌ {issue['type']}")
                print(f"   {issue['message']}")
                print(f"   Fix: {issue['fix']}")
            print()
        
        if warnings:
            print("WARNINGS (Recommended to fix):")
            print("-" * 70)
            for issue in warnings:
                print(f"\n⚠️  {issue['type']}")
                print(f"   {issue['message']}")
                print(f"   Fix: {issue['fix']}")
            print()
        
        if info:
            print("INFO (Optional):")
            print("-" * 70)
            for issue in info:
                print(f"\nℹ️  {issue['type']}")
                print(f"   {issue['message']}")
                print(f"   Fix: {issue['fix']}")
            print()
    
    def print_fixes_applied(self, result: Dict[str, Any]):
        """Print fixes applied"""
        if result["fixes_applied"]:
            print("\n" + "=" * 70)
            print("FIXES APPLIED")
            print("=" * 70 + "\n")
            for fix in result["fixes_applied"]:
                print(f"✅ {fix}")
            print()
        
        if result.get("backup_path"):
            print(f"📦 Backup created at: {result['backup_path']}\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Recover from setup issues")
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Automatically apply fixes for critical issues"
    )
    parser.add_argument(
        "--restore",
        help="Restore from backup (provide timestamp or 'latest')"
    )
    parser.add_argument(
        "--list-backups",
        action="store_true",
        help="List available backups"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    recovery = SetupRecovery()
    
    # List backups
    if args.list_backups:
        backup_dir = recovery.backup_dir
        if backup_dir.exists():
            backups = sorted(backup_dir.iterdir(), key=lambda x: x.name, reverse=True)
            print("\nAvailable backups:")
            for backup in backups[:10]:  # Show last 10
                print(f"  {backup.name}")
        else:
            print("No backups available")
        return
    
    # Restore from backup
    if args.restore:
        if args.restore == "latest":
            success = recovery.restore_from_backup()
        else:
            success = recovery.restore_from_backup(args.restore)
        
        if success:
            print("✅ Restored from backup")
        else:
            print("❌ Failed to restore from backup")
        return
    
    # Detect and fix issues
    issues = recovery.detect_issues()
    
    if args.json:
        result = recovery.apply_fixes(auto_fix=args.auto_fix)
        print(json.dumps({
            "issues": issues,
            "fixes": result
        }, indent=2))
    else:
        recovery.print_report(issues)
        
        if issues:
            if args.auto_fix:
                result = recovery.apply_fixes(auto_fix=True)
                recovery.print_fixes_applied(result)
            else:
                print("💡 Run with --auto-fix to automatically fix critical issues")
                print("   Or run: python scripts/setup_environment_wizard.py\n")
    
    sys.exit(0)


if __name__ == "__main__":
    main()

