#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for Training & Evaluation System
Validates all components of the training system
"""

import sys
import json
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from training_evaluation_system import (
    TrainingEvaluationSystem,
    BotMode,
    CorrectionTrigger
)
from benchmark_system import BenchmarkSystem
from training_integrated_bot import TrainingIntegratedBot


def test_training_system():
    """Test the training evaluation system"""
    print("\n" + "="*60)
    print("🧪 Testing Training Evaluation System")
    print("="*60)
    
    system = TrainingEvaluationSystem()
    
    # Test 1: Set training mode
    print("\n📝 Test 1: Activar modo entrenamiento...")
    result = system.set_session_mode("test_001", "agent_test", BotMode.TRAINING)
    assert result["success"] == True, "Failed to activate training mode"
    assert "instructions" in result, "Instructions not provided"
    print("   ✅ Modo entrenamiento activado correctamente")
    
    # Test 2: Detect correction
    print("\n📝 Test 2: Detectar corrección con emoji...")
    is_correction, text = system.detect_correction(
        f"{CorrectionTrigger.CORRECTION_EMOJI.value} Mejorar la respuesta",
        "test_001"
    )
    assert is_correction == True, "Failed to detect correction emoji"
    assert text == "Mejorar la respuesta", "Incorrect correction text extracted"
    print("   ✅ Corrección detectada correctamente")
    
    # Test 3: Create correction request
    print("\n📝 Test 3: Crear solicitud de corrección...")
    correction = system.create_correction_request(
        session_id="test_001",
        user_id="agent_test",
        original_query="¿Cuánto cuesta el Isodec?",
        original_response="El precio varía según el espesor",
        correction_text="Incluir precios específicos por espesor"
    )
    assert correction.id is not None, "Correction ID not generated"
    assert correction.session_id == "test_001", "Incorrect session ID"
    print(f"   ✅ Corrección creada con ID: {correction.id}")
    
    # Test 4: Get statistics
    print("\n📝 Test 4: Obtener estadísticas de sesión...")
    stats = system.get_session_statistics("test_001")
    assert stats["success"] == True, "Failed to get statistics"
    assert stats["corrections_made"] == 1, "Incorrect corrections count"
    print(f"   ✅ Estadísticas: {stats['corrections_made']} correcciones realizadas")
    
    # Test 5: End training session
    print("\n📝 Test 5: Finalizar sesión de entrenamiento...")
    result = system.end_training_session("test_001")
    assert result["success"] == True, "Failed to end session"
    print("   ✅ Sesión finalizada correctamente")
    
    print("\n" + "="*60)
    print("✅ Training System: Todos los tests pasaron!")
    print("="*60)
    return True


def test_benchmark_system():
    """Test the benchmark system"""
    print("\n" + "="*60)
    print("🧪 Testing Benchmark System")
    print("="*60)
    
    benchmark = BenchmarkSystem()
    
    # Mock response function
    def mock_response(query):
        query_lower = query.lower()
        if "isodec" in query_lower and "cotización" in query_lower:
            return "Para cotizar Isodec necesito: espesor, dimensiones (largo x ancho), y tus datos de contacto."
        elif "productos" in query_lower or "aislantes" in query_lower:
            return "Tenemos Isodec, Poliestireno y Lana de Roca con diferentes características."
        elif "precio" in query_lower:
            return "Los precios son competitivos y varían según especificaciones."
        else:
            return "Estoy aquí para ayudarte con nuestros productos de aislamiento."
    
    # Test 1: Run benchmark
    print("\n📝 Test 1: Ejecutar benchmark con suite 'default'...")
    result = benchmark.run_benchmark(
        suite_name="default",
        bot_response_func=mock_response,
        mode="test_mode"
    )
    assert result["success"] == True, "Benchmark failed"
    assert result["summary"]["total_tests"] > 0, "No tests executed"
    print(f"   ✅ Benchmark ejecutado: {result['summary']['total_tests']} tests")
    print(f"   📊 Score promedio: {result['summary']['average_score']:.1f}/100")
    
    # Test 2: Generate report
    print("\n📝 Test 2: Generar reporte de benchmark...")
    report = benchmark.generate_report(period_days=1)
    assert report.id is not None, "Report ID not generated"
    assert report.total_tests >= 0, "Invalid test count"
    print(f"   ✅ Reporte generado con ID: {report.id}")
    print(f"   📊 Tests: {report.total_tests}, Score: {report.average_score:.1f}")
    
    # Test 3: Add custom test
    print("\n📝 Test 3: Agregar test personalizado...")
    from benchmark_system import BenchmarkTest
    custom_test = BenchmarkTest(
        id="test_custom_001",
        name="Test personalizado",
        description="Test de prueba",
        input_query="¿Tienen descuentos?",
        expected_output="descuentos, promociones, oferta",
        category="pricing",
        difficulty=2,
        tags=["descuentos", "pricing"]
    )
    benchmark.add_test("custom", custom_test)
    print("   ✅ Test personalizado agregado")
    
    print("\n" + "="*60)
    print("✅ Benchmark System: Todos los tests pasaron!")
    print("="*60)
    return True


def test_integrated_bot():
    """Test the integrated bot"""
    print("\n" + "="*60)
    print("🧪 Testing Training Integrated Bot")
    print("="*60)
    
    bot = TrainingIntegratedBot()
    
    # Test 1: Process normal message
    print("\n📝 Test 1: Procesar mensaje normal...")
    response = bot.process_message("test_002", "agent_test", "Hola")
    assert len(response) > 0, "Empty response"
    print(f"   ✅ Respuesta generada: {response[:50]}...")
    
    # Test 2: Activate training mode
    print("\n📝 Test 2: Activar modo entrenamiento...")
    response = bot.process_message("test_002", "agent_test", "MODO ENTRENAMIENTO")
    assert "entrenamiento activado" in response.lower(), "Training mode not activated"
    print("   ✅ Modo entrenamiento activado")
    
    # Test 3: Make a correction
    print("\n📝 Test 3: Realizar corrección...")
    # First, get a normal response
    bot.process_message("test_002", "agent_test", "¿Qué productos tienen?")
    # Then correct it
    response = bot.process_message(
        "test_002",
        "agent_test",
        f"{CorrectionTrigger.CORRECTION_EMOJI.value} Incluir precios en la respuesta"
    )
    assert "reformulada" in response.lower(), "Correction not processed"
    print("   ✅ Corrección procesada y reformulación generada")
    
    # Test 4: Get statistics
    print("\n📝 Test 4: Obtener estadísticas...")
    response = bot.process_message("test_002", "agent_test", "ESTADÍSTICAS")
    assert "estadísticas" in response.lower(), "Statistics not returned"
    print("   ✅ Estadísticas mostradas")
    
    # Test 5: End session
    print("\n📝 Test 5: Finalizar sesión...")
    response = bot.process_message("test_002", "agent_test", "SALIR ENTRENAMIENTO")
    assert "finalizada" in response.lower() or "sesión" in response.lower(), "Session not ended"
    print("   ✅ Sesión finalizada")
    
    print("\n" + "="*60)
    print("✅ Integrated Bot: Todos los tests pasaron!")
    print("="*60)
    return True


def test_data_persistence():
    """Test data persistence"""
    print("\n" + "="*60)
    print("🧪 Testing Data Persistence")
    print("="*60)
    
    # Test 1: Create directories
    print("\n📝 Test 1: Verificar directorios de datos...")
    data_dir = Path("data")
    training_dir = data_dir / "training"
    benchmarks_dir = data_dir / "benchmarks"
    
    # These should be created by the systems
    if not training_dir.exists():
        print("   ℹ️  Directorio training no existe, creándolo...")
        training_dir.mkdir(parents=True, exist_ok=True)
    
    if not benchmarks_dir.exists():
        print("   ℹ️  Directorio benchmarks no existe, creándolo...")
        benchmarks_dir.mkdir(parents=True, exist_ok=True)
    
    assert training_dir.exists(), "Training directory not created"
    assert benchmarks_dir.exists(), "Benchmarks directory not created"
    print("   ✅ Directorios verificados/creados")
    
    # Test 2: Save and load training data
    print("\n📝 Test 2: Guardar y cargar datos de entrenamiento...")
    system = TrainingEvaluationSystem()
    system.set_session_mode("test_persist", "agent_test", BotMode.TRAINING)
    system.create_correction_request(
        session_id="test_persist",
        user_id="agent_test",
        original_query="Test query",
        original_response="Test response",
        correction_text="Test correction"
    )
    
    # Data should be saved automatically
    corrections_file = training_dir / "corrections.json"
    assert corrections_file.exists(), "Corrections file not created"
    print("   ✅ Datos de correcciones guardados")
    
    # Test 3: Save and load benchmark data
    print("\n📝 Test 3: Guardar y cargar datos de benchmark...")
    benchmark = BenchmarkSystem()
    
    test_suites_file = benchmarks_dir / "test_suites.json"
    test_results_file = benchmarks_dir / "test_results.json"
    
    # These should exist after system initialization
    assert test_suites_file.exists(), "Test suites file not created"
    print("   ✅ Datos de benchmark guardados")
    
    print("\n" + "="*60)
    print("✅ Data Persistence: Todos los tests pasaron!")
    print("="*60)
    return True


def main():
    """Run all tests"""
    print("\n" + "🚀"*30)
    print("     SUITE COMPLETA DE TESTS")
    print("     Sistema de Entrenamiento y Evaluación")
    print("🚀"*30)
    
    results = {
        "training_system": False,
        "benchmark_system": False,
        "integrated_bot": False,
        "data_persistence": False
    }
    
    try:
        results["training_system"] = test_training_system()
    except Exception as e:
        print(f"\n❌ Error en Training System: {e}")
    
    try:
        results["benchmark_system"] = test_benchmark_system()
    except Exception as e:
        print(f"\n❌ Error en Benchmark System: {e}")
    
    try:
        results["integrated_bot"] = test_integrated_bot()
    except Exception as e:
        print(f"\n❌ Error en Integrated Bot: {e}")
    
    try:
        results["data_persistence"] = test_data_persistence()
    except Exception as e:
        print(f"\n❌ Error en Data Persistence: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 RESUMEN DE TESTS")
    print("="*60)
    
    all_passed = all(results.values())
    passed_count = sum(results.values())
    total_count = len(results)
    
    for component, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {component}")
    
    print(f"\n🎯 Total: {passed_count}/{total_count} componentes pasaron")
    
    if all_passed:
        print("\n" + "🎉"*30)
        print("     ¡TODOS LOS TESTS PASARON!")
        print("     Sistema listo para usar")
        print("🎉"*30)
        return 0
    else:
        print("\n⚠️  Algunos tests fallaron. Revisar errores arriba.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
