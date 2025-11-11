#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification script to check if everything is set up correctly
"""

import os
import sys
import importlib.util

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_module(module_name, package_name=None):
    """Check if a module is installed"""
    if package_name is None:
        package_name = module_name
    
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        print(f"❌ {package_name} not installed")
        print(f"   Install with: pip install {package_name}")
        return False
    print(f"✅ {package_name} installed")
    return True

def check_file(filepath):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {filepath} exists")
        return True
    else:
        print(f"❌ {filepath} not found")
        return False

def check_env_file():
    """Check if .env file exists"""
    if os.path.exists('.env'):
        print("✅ .env file exists")
        return True
    else:
        print("⚠️  .env file not found")
        print("   Copy env.example to .env and configure it")
        return False

def check_api_server():
    """Check if API server can be imported"""
    try:
        sys.path.insert(0, os.getcwd())
        import api_server
        print("✅ api_server.py can be imported")
        return True
    except Exception as e:
        print(f"❌ Error importing api_server.py: {e}")
        return False

def check_ia_module():
    """Check if IA module can be imported"""
    try:
        sys.path.insert(0, os.getcwd())
        from ia_conversacional_integrada import IAConversacionalIntegrada
        print("✅ ia_conversacional_integrada.py can be imported")
        return True
    except Exception as e:
        print(f"❌ Error importing ia_conversacional_integrada.py: {e}")
        return False

def check_simulator_files():
    """Check simulator files"""
    files = [
        'simulate_chat.py',
        'simulate_chat_cli.py',
        'populate_kb.py'
    ]
    all_exist = True
    for file in files:
        if not check_file(file):
            all_exist = False
    return all_exist

def check_test_scenarios():
    """Check test scenarios directory"""
    if os.path.exists('test_scenarios'):
        files = os.listdir('test_scenarios')
        json_files = [f for f in files if f.endswith('.json')]
        if json_files:
            print(f"✅ test_scenarios/ directory exists with {len(json_files)} scenario files")
            return True
        else:
            print("⚠️  test_scenarios/ directory exists but no JSON files found")
            return False
    else:
        print("❌ test_scenarios/ directory not found")
        return False

def main():
    """Run all checks"""
    print("=" * 70)
    print("🔍 Verifying Setup")
    print("=" * 70)
    print()
    
    checks = []
    
    print("📋 Python Environment:")
    checks.append(check_python_version())
    print()
    
    print("📦 Required Packages:")
    required_modules = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('pydantic', 'pydantic'),
        ('requests', 'requests'),
        ('pymongo', 'pymongo'),
    ]
    
    # Check OpenAI (optional)
    openai_available = check_module('openai', 'openai')
    if not openai_available:
        print("   ⚠️  OpenAI not installed (optional, will use pattern matching)")
    print()
    
    for module, package in required_modules:
        checks.append(check_module(module, package))
    print()
    
    print("📁 Required Files:")
    checks.append(check_file('api_server.py'))
    checks.append(check_file('ia_conversacional_integrada.py'))
    checks.append(check_file('sistema_cotizaciones.py'))
    checks.append(check_simulator_files())
    print()
    
    print("📂 Test Scenarios:")
    checks.append(check_test_scenarios())
    print()
    
    print("⚙️  Configuration:")
    checks.append(check_env_file())
    print()
    
    print("🔧 Module Imports:")
    checks.append(check_api_server())
    checks.append(check_ia_module())
    print()
    
    # Summary
    print("=" * 70)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"✅ All checks passed ({passed}/{total})")
        print()
        print("🚀 You're ready to start!")
        print()
        print("Next steps:")
        print("  1. Start API server: python api_server.py")
        print("  2. In another terminal: python simulate_chat_cli.py")
        print("  3. Or use: ./start_simulator.sh")
        return 0
    else:
        print(f"⚠️  Some checks failed ({passed}/{total})")
        print()
        print("Please fix the issues above before proceeding")
        return 1

if __name__ == "__main__":
    sys.exit(main())

