#!/usr/bin/env python3
"""
Agent 1: Chatbot Testing and Review Script
Tests chatbot functionality and reviews system progress
"""

import json
import sys
from datetime import datetime
from pathlib import Path

print("=" * 70)
print("AGENT 1: CHATBOT TESTING & REVIEW")
print("=" * 70)
print()

# Test 1: Import and initialize chatbot
print("📋 TEST 1: Module Import and Initialization")
print("-" * 70)
try:
    from chat_interactivo import AgenteInteractivo

    agente = AgenteInteractivo()
    print("✅ Chatbot module imported successfully")
    print("✅ AgenteInteractivo initialized")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 2: Test basic responses
print("\n📋 TEST 2: Basic Response Testing")
print("-" * 70)
test_cases = [
    ("Hola", "saludo"),
    ("Quiero cotizar", "cotizacion"),
    ("Información sobre Isodec", "informacion"),
    ("Gracias", "despedida"),
]

results = []
for message, expected_type in test_cases:
    try:
        response = agente.procesar_mensaje(message)
        results.append(
            {
                "input": message,
                "expected": expected_type,
                "response_length": len(response),
                "success": True,
                "response_preview": response[:100] + "..." if len(response) > 100 else response,
            }
        )
        print(f"✅ '{message}' → Response generated ({len(response)} chars)")
    except Exception as e:
        results.append(
            {"input": message, "expected": expected_type, "success": False, "error": str(e)}
        )
        print(f"❌ '{message}' → Error: {e}")

# Test 3: Test quote generation flow
print("\n📋 TEST 3: Quote Generation Flow")
print("-" * 70)
quote_flow = [
    "cotizar",
    "Juan Pérez",
    "099123456",
    "Montevideo",
    "isodec",
    "10 x 5",
    "100mm",
    "Blanco",
    "Gotero",
]

print("Testing complete quote flow...")
for step, message in enumerate(quote_flow, 1):
    try:
        response = agente.procesar_mensaje(message)
        print(f"  Step {step}: ✅ Response received")
        if "error" in response.lower() or "❌" in response:
            print(f"    ⚠️  Warning in response: {response[:80]}...")
    except Exception as e:
        print(f"  Step {step}: ❌ Error: {e}")

# Test 4: System components check
print("\n📋 TEST 4: System Components Check")
print("-" * 70)
components = {
    "SistemaCotizaciones": "sistema_cotizaciones",
    "IA Conversacional": "ia_conversacional_integrada",
    "Base Conocimiento": "base_conocimiento_dinamica",
}

component_status = {}
for name, module in components.items():
    try:
        __import__(module)
        print(f"✅ {name} module available")
        component_status[name] = True
    except ImportError as e:
        print(f"❌ {name} module not found: {e}")
        component_status[name] = False
    except Exception as e:
        print(f"⚠️  {name} module has issues: {e}")
        component_status[name] = False

# Check API server file exists
api_server_exists = Path("api_server.py").exists()
print(f"{'✅' if api_server_exists else '❌'} API Server file exists")
component_status["API Server"] = api_server_exists

# Test 5: Configuration check
print("\n📋 TEST 5: Configuration Check")
print("-" * 70)

config_items = {
    ".env file": Path(".env").exists(),
    "env.example": Path("env.example").exists(),
    "requirements.txt": Path("requirements.txt").exists(),
    "matriz_precios.json": Path("matriz_precios.json").exists(),
    "unified_launcher.py": Path("unified_launcher.py").exists(),
}

for item, exists in config_items.items():
    status = "✅" if exists else "❌"
    print(f"{status} {item}")

# Generate report
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

total_tests = len(results)
passed_tests = sum(1 for r in results if r.get("success", False))
failed_tests = total_tests - passed_tests

print(f"Total Tests: {total_tests}")
print(f"Passed: {passed_tests} ✅")
print(f"Failed: {failed_tests} {'❌' if failed_tests > 0 else ''}")
print(f"Success Rate: {(passed_tests / total_tests * 100):.1f}%")

# Save results
report = {
    "timestamp": datetime.now().isoformat(),
    "agent": "Agent 1",
    "test_results": results,
    "summary": {
        "total": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "success_rate": passed_tests / total_tests * 100 if total_tests > 0 else 0,
    },
    "components": {name: Path(f"{module}.py").exists() for name, module in components.items()},
    "configuration": config_items,
}

with open("agent1_test_report.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print("\n✅ Test report saved to: agent1_test_report.json")
print("=" * 70)
