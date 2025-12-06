#!/usr/bin/env python3
"""
Verify Package Installation
Checks that all components are properly installed and operational
"""

import sys
from pathlib import Path

# Add repository root to path
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

def check_imports():
    """Check that all imports work"""
    print("Checking imports...")
    try:
        from scripts.orchestrator.agent_interface import (
            AgentInterface, AgentCoordinator,
            RepositoryAgent, IntegrationAgent, QuotationAgent
        )
        print("  ✅ Agent Interface imports: PASS")
        
        from scripts.orchestrator.phase_executors.phase_0_executor import Phase0Executor
        print("  ✅ Phase 0 Executor import: PASS")
        
        from scripts.orchestrator.main_orchestrator import MainOrchestrator
        print("  ✅ Main Orchestrator import: PASS")
        
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_files():
    """Check that all required files exist"""
    print("\nChecking files...")
    files = [
        "scripts/orchestrator/agent_interface.py",
        "scripts/orchestrator/auto_start.py",
        "scripts/orchestrator/install_auto_start.sh",
        "scripts/orchestrator/phase_executors/phase_0_executor.py",
        "scripts/orchestrator/config/auto_start_config.json",
        "scripts/orchestrator/PACKAGE_README.md"
    ]
    
    all_exist = True
    for file_path in files:
        path = Path(file_path)
        if path.exists():
            print(f"  ✅ {file_path}: EXISTS")
        else:
            print(f"  ❌ {file_path}: MISSING")
            all_exist = False
    
    return all_exist

def check_agent_system():
    """Check that agent system works"""
    print("\nChecking agent system...")
    try:
        from scripts.orchestrator.agent_interface import AgentCoordinator
        
        coordinator = AgentCoordinator()
        
        # Check agents are registered
        if len(coordinator.agents) >= 3:
            print(f"  ✅ Agents registered: {len(coordinator.agents)}")
        else:
            print(f"  ❌ Not enough agents registered: {len(coordinator.agents)}")
            return False
        
        # Check agent types
        expected_agents = ["RepositoryAgent", "IntegrationAgent", "QuotationAgent"]
        for agent_type in expected_agents:
            if agent_type in coordinator.agents:
                print(f"  ✅ {agent_type}: REGISTERED")
            else:
                print(f"  ❌ {agent_type}: MISSING")
                return False
        
        # Test delegation
        test_task_id = "TEST_TASK"
        test_config = {"type": "analyze_repositories", "repositories": []}
        
        try:
            request_file = coordinator.delegate_task("RepositoryAgent", test_task_id, test_config)
            if Path(request_file).exists():
                print("  ✅ Task delegation: WORKS")
            else:
                print("  ❌ Task delegation: FAILED")
                return False
        except Exception as e:
            print(f"  ❌ Task delegation error: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Agent system check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_phase_executor():
    """Check that phase executor works"""
    print("\nChecking phase executor...")
    try:
        from scripts.orchestrator.phase_executors.phase_0_executor import Phase0Executor
        from scripts.orchestrator.state_manager import StateManager
        
        state_manager = StateManager()
        executor = Phase0Executor(0, state_manager)
        
        # Check coordinator is available
        if executor.coordinator:
            print("  ✅ Agent Coordinator: AVAILABLE")
        else:
            print("  ⚠️  Agent Coordinator: NOT AVAILABLE (will use fallback)")
        
        # Check methods exist
        methods = ["execute", "_delegate_task", "_execute_task_fallback"]
        for method in methods:
            if hasattr(executor, method):
                print(f"  ✅ Method {method}: EXISTS")
            else:
                print(f"  ❌ Method {method}: MISSING")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Phase executor check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_auto_start():
    """Check auto-start installation"""
    print("\nChecking auto-start...")
    try:
        import os
        
        # Check config file
        config_file = Path("scripts/orchestrator/config/auto_start_config.json")
        if config_file.exists():
            print("  ✅ Auto-start config: EXISTS")
            
            import json
            with open(config_file) as f:
                config = json.load(f)
                if config.get("enabled"):
                    print("  ✅ Auto-start: ENABLED")
                else:
                    print("  ⚠️  Auto-start: DISABLED")
        else:
            print("  ❌ Auto-start config: MISSING")
            return False
        
        # Check script is executable
        script_file = Path("scripts/orchestrator/auto_start.py")
        if script_file.exists():
            if os.access(script_file, os.X_OK):
                print("  ✅ Auto-start script: EXECUTABLE")
            else:
                print("  ⚠️  Auto-start script: NOT EXECUTABLE")
        else:
            print("  ❌ Auto-start script: MISSING")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Auto-start check failed: {e}")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("Package Verification")
    print("=" * 60)
    
    checks = [
        ("Imports", check_imports),
        ("Files", check_files),
        ("Agent System", check_agent_system),
        ("Phase Executor", check_phase_executor),
        ("Auto-Start", check_auto_start)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("✅ All checks passed! Package is ready to use.")
        return 0
    else:
        print("❌ Some checks failed. Please review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

