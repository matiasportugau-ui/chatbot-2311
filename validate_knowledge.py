#!/usr/bin/env python3
"""
validate_knowledge.py

Validates the structure and syntax of knowledge base JSON files.
Used in CI/CD pipelines to prevent corrupt files from blocking deployment.
"""

import json
import sys
import os
from pathlib import Path

def validate_json_file(file_path):
    """
    Validates a JSON file for syntax errors.
    Returns (is_valid, error_message)
    """
    path = Path(file_path)
    if not path.exists():
        return False, f"File not found: {file_path}"
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"JSON Error: {e.msg} at line {e.lineno} column {e.colno}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_knowledge.py <file1> [file2 ...]")
        sys.exit(1)
        
    files = sys.argv[1:]
    has_errors = False
    
    print("🔍 Validating Knowledge Base Files...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    for file_path in files:
        is_valid, error = validate_json_file(file_path)
        if is_valid:
            print(f"✅ {file_path}: Valid")
        else:
            print(f"❌ {file_path}: Invalid")
            print(f"   Error: {error}")
            has_errors = True
            
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    if has_errors:
        print("⚠️  Validation failed for some files.")
        sys.exit(1)
    else:
        print("✅ All files verified successfully.")
        sys.exit(0)

if __name__ == "__main__":
    main()
