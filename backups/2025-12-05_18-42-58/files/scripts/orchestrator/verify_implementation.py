#!/usr/bin/env python3
"""
Verification Script
Verifies that all components of the orchestrator are properly implemented
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def verify_imports():
    """Verify all modules can be imported"""
    print("Verifying imports...")
    try:
        from scripts.orchestrator.state_manager import StateManager
        from scripts.orchestrator.dependency_resolver import DependencyResolver
        from scripts.orchestrator.triggers import TriggerManager
        from scripts.orchestrator.approval_engine import ApprovalEngine
        from scripts.orchestrator.success_criteria import SuccessCriteria
        from scripts.orchestrator.error_handler import ErrorHandler, ErrorType
        from scripts.orchestrator.retry_manager import RetryManager
        from scripts.orchestrator.github_integration import GitHubIntegration
        from scripts.orchestrator.status_reporter import StatusReporter
        from scripts.orchestrator.main_orchestrator import MainOrchestrator
        from scripts.orchestrator.phase_executors.base_executor import BaseExecutor
        from scripts.orchestrator.phase_executors.phase_0_executor import Phase0Executor
        from scripts.orchestrator.utils.file_validator import FileValidator
        from scripts.orchestrator.utils.json_validator import JSONValidator
        from scripts.orchestrator.utils.metric_validator import MetricValidator
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_files():
    """Verify all required files exist"""
    print("\nVerifying files...")
    base_dir = Path(__file__).parent
    required_files = [
        "state_manager.py",
        "dependency_resolver.py",
        "triggers.py",
        "approval_engine.py",
        "success_criteria.py",
        "error_handler.py",
        "retry_manager.py",
        "github_integration.py",
        "status_reporter.py",
        "main_orchestrator.py",
        "run_automated_execution.py",
        "setup_config.py",
        "requirements.txt",
        "README.md",
        "phase_executors/base_executor.py",
        "phase_executors/phase_0_executor.py",
        "utils/file_validator.py",
        "utils/json_validator.py",
        "utils/metric_validator.py",
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def verify_config_files():
    """Verify configuration files exist"""
    print("\nVerifying configuration files...")
    base_dir = Path(__file__).parent
    config_dir = base_dir / "config"
    required_configs = [
        "orchestrator_config.json",
        "phase_config.json",
        "success_criteria.json",
        "github_config.json"
    ]
    
    all_exist = True
    for config_file in required_configs:
        full_path = config_dir / config_file
        if full_path.exists():
            print(f"  ✅ config/{config_file}")
        else:
            print(f"  ❌ config/{config_file} - MISSING")
            all_exist = False
    
    return all_exist

def verify_classes():
    """Verify key classes can be instantiated"""
    print("\nVerifying class instantiation...")
    try:
        from scripts.orchestrator.state_manager import StateManager
        from scripts.orchestrator.dependency_resolver import DependencyResolver
        from scripts.orchestrator.error_handler import ErrorHandler
        
        # Test StateManager
        sm = StateManager()
        print("  ✅ StateManager instantiated")
        
        # Test DependencyResolver
        dr = DependencyResolver(state_manager=sm)
        print("  ✅ DependencyResolver instantiated")
        
        # Test ErrorHandler
        eh = ErrorHandler()
        print("  ✅ ErrorHandler instantiated")
        
        return True
    except Exception as e:
        print(f"  ❌ Class instantiation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all verification checks"""
    print("="*60)
    print("Orchestrator Implementation Verification")
    print("="*60)
    
    results = []
    
    results.append(("Imports", verify_imports()))
    results.append(("Files", verify_files()))
    results.append(("Config Files", verify_config_files()))
    results.append(("Classes", verify_classes()))
    
    print("\n" + "="*60)
    print("Verification Summary")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    if all_passed:
        print("✅ All verifications passed!")
        return 0
    else:
        print("❌ Some verifications failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

