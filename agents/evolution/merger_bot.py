#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merger Bot - Part of the Master Evolution Agent.
Executes the 'Golden Merge' plan, splicing files and recording the evolution.
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List
import datetime

class MergerBot:
    def __init__(self, workspace_path: str = "."):
        self.workspace = Path(workspace_path).resolve()
        self.backup_dir = self.workspace / "backups" / f"pre_merge_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def execute_merge_plan(self, plan: Dict) -> bool:
        """
        Executes a merge plan (JSON).
        Plan format:
        {
            "actions": [
                {"type": "keep", "path": "path/to/winner"},
                {"type": "discard", "path": "path/to/loser"},
                {"type": "overwrite", "source": "path/to/winner", "target": "path/to/target"}
            ]
        }
        """
        print(f"🤖 MergerBot: Executing plan...")
        
        # 1. Create Backup
        self._create_backup()
        
        # 2. Execute Actions
        success = True
        for action in plan.get("actions", []):
            try:
                self._execute_action(action)
            except Exception as e:
                print(f"❌ Error executing {action}: {e}")
                success = False
                
        return success

    def _create_backup(self):
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
            print(f"📦 Backup created at {self.backup_dir}")

    def _execute_action(self, action: Dict):
        action_type = action.get("type")
        
        if action_type == "keep":
            # No-op, just logging
            print(f"✅ KEEP: {action.get('path')}")
            
        elif action_type == "discard":
            target = self.workspace / action.get("path")
            if target.exists():
                # Move to backup instead of delete for safety
                shutil.move(str(target), str(self.backup_dir / target.name))
                print(f"🗑️ DISCARD: {target.name} (moved to backup)")
            else:
                # If the file to discard doesn't exist, it's already gone, so consider it discarded.
                print(f"🗑️ DISCARD: {target.name} (already absent)")
                
        elif action_type == "overwrite":
            src = self.workspace / action.get("source")
            dst = self.workspace / action.get("target")
            if src.exists():
                shutil.copy2(str(src), str(dst))
                print(f"🔄 OVERWRITE: {dst.name} with {src.name}")
            else:
                raise FileNotFoundError(f"Source {src} not found")
        
        elif action_type == "create":
            target = self.workspace / action.get("path")
            content = action.get("content", "")
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                with open(target, 'w') as f:
                    f.write(content)
                print(f"✨ CREATE: {target.name}")
            else:
                print(f"⚠️ CREATE: {target.name} already exists, skipping creation.")

        elif action_type == "combine":
            # applying a merge strategy (e.g., line-by-line, block-by-block, or using a diff/patch tool),
            # and writing the combined result to the target.
            # For now, we'll just log that a combine action was requested.
            sources = [self.workspace / s for s in action.get("sources", [])]
            target = self.workspace / action.get("target")
            print(f"🧩 COMBINE: Sources {sources} into {target} (combine logic not yet implemented)")
            # Example of a very basic combine (concatenation) - this would need more sophisticated logic
            # with open(target, 'w') as outfile:
            #     for fname in sources:
            #         with open(fname) as infile:
            #             outfile.write(infile.read())
            #         outfile.write("\n") # Add a newline between combined files for clarity

if __name__ == "__main__":
    # Test run
    bot = MergerBot()
    # Dummy plan
    bot.execute_merge_plan({"actions": [{"type": "keep", "path": "README.md"}]})
